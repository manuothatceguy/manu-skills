#!/usr/bin/env python3
"""delegate-swarm: fire small, verifiable tasks at cheap coding agents, each in its own git worktree.

Every worker is a bullet, not a gun: one task, a minimal prompt, a fixed file scope and
an acceptance command. The orchestrator (Claude) plans, writes batches and reads summaries.

Subcommands: init, doctor, lint, run, status, ship, checks, capsule, clean.
Standard library only (Python >= 3.11).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        sys.exit("delegate-swarm needs Python 3.11+ (or `pip install tomli`).")

SKILL_DIR = Path(__file__).resolve().parent.parent
GLOBAL_DIR = Path(os.environ.get("SWARM_CONFIG_DIR", "~/.config/delegate-swarm")).expanduser()
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
PH_RE = re.compile(r"\{(\w+)\}")
GIT_LOCK = threading.Lock()


# ----------------------------------------------------------------------------- helpers

def die(msg: str, code: int = 2):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.exit(code)


def emit(obj):
    print(json.dumps(obj, indent=1, ensure_ascii=False))


def fill(template: str, values: dict) -> str:
    """Single-pass placeholder fill; inserted values are never re-scanned."""
    return PH_RE.sub(lambda m: str(values[m.group(1)]) if m.group(1) in values else m.group(0), template)


def fill_cmd(cmd: list, values: dict) -> list:
    return [fill(str(a), values) for a in cmd]


def sh(cmd, cwd=None, check=True, timeout=None, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(map(str, cmd))} failed ({r.returncode}): {(r.stderr or r.stdout).strip()[-800:]}")
    return r


def git(*args, cwd, check=True):
    return sh(["git", *args], cwd=cwd, check=check).stdout.strip()


def tail(text: str, chars: int) -> str:
    text = ANSI_RE.sub("", text or "").strip()
    return text if len(text) <= chars else "…" + text[-chars:]


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def expand(path: str, values: dict) -> Path:
    return Path(fill(path, values)).expanduser()


# ----------------------------------------------------------------------------- repo + config

def repo_root(start: Path) -> Path:
    r = sh(["git", "rev-parse", "--show-toplevel"], cwd=start, check=False)
    if r.returncode != 0:
        die(f"{start} is not inside a git repository. delegate-swarm needs git (worktrees).")
    return Path(r.stdout.strip())


def load_config(root: Path) -> dict:
    cfg = tomllib.loads((SKILL_DIR / "config.default.toml").read_text())
    for p in (GLOBAL_DIR / "config.toml", root / ".swarm" / "config.toml"):
        if p.exists():
            try:
                cfg = deep_merge(cfg, tomllib.loads(p.read_text()))
            except tomllib.TOMLDecodeError as e:
                die(f"invalid TOML in {p}: {e}")
    return cfg


def path_values(root: Path) -> dict:
    tag = hashlib.sha1(str(root).encode()).hexdigest()[:6]
    return {"skill": str(SKILL_DIR), "repo_root": str(root), "repo": f"{root.name}-{tag}"}


# ----------------------------------------------------------------------------- capsules

def parse_capsule(text: str):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    pre, sections, cur = [], {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+@([\w-]+)\s*$", line)
        if m:
            cur = m.group(1)
            sections[cur] = []
            continue
        (sections[cur] if cur else pre).append(line)
    return "\n".join(pre).strip(), {k: "\n".join(v).strip() for k, v in sections.items()}


def resolve_capsule(spec: str, root: Path, cfg: dict):
    name, _, wanted = spec.partition("#")
    vals = path_values(root)
    for d in cfg["capsules"]["paths"]:
        f = expand(d, vals) / f"{name}.md"
        if f.exists():
            pre, secs = parse_capsule(f.read_text())
            keys = [w.strip() for w in wanted.split(",") if w.strip()] or list(secs)
            missing = [k for k in keys if k not in secs]
            if missing:
                raise ValueError(f"capsule '{name}' has no section(s) {missing}; available: {list(secs)}")
            body = "\n\n".join([pre] + [secs[k] for k in keys]).strip()
            return f"## {name}\n{body}", str(f)
    raise ValueError(f"capsule '{name}' not found in {cfg['capsules']['paths']}")


# ----------------------------------------------------------------------------- batches

class Task:
    def __init__(self, raw: dict, batch: "Batch"):
        self.raw = raw
        self.id = str(raw.get("id", ""))
        self.title = str(raw.get("title", self.id))
        self.goal = str(raw.get("goal", "")).strip()
        self.context = str(raw.get("context", "")).strip()
        self.files = [str(f) for f in raw.get("files", [])]
        self.read = [str(f) for f in raw.get("read", [])]
        self.accept = str(raw.get("accept", "") or batch.cfg["verify"]["accept"]).strip()
        self.tier = str(raw.get("tier", batch.raw.get("tier", batch.cfg["models"]["default_tier"])))
        self.models = [str(m) for m in raw.get("models", [])]  # explicit override
        self.capsules = list(dict.fromkeys(batch.cfg["capsules"]["default"] + batch.raw.get("capsules", []) + raw.get("capsules", [])))
        self.depends_on = [str(d) for d in raw.get("depends_on", [])]
        self.commit = str(raw.get("commit", "") or f"swarm({self.id}): {self.title}")
        self.allow_empty = bool(raw.get("allow_empty", False))
        self.branch = f"{batch.cfg['run']['branch_prefix']}/{batch.name}/{self.id}"


class Batch:
    def __init__(self, path: Path, root: Path, cfg: dict):
        self.path, self.root, self.cfg = path, root, cfg
        try:
            self.raw = tomllib.loads(path.read_text())
        except FileNotFoundError:
            die(f"batch file not found: {path}")
        except tomllib.TOMLDecodeError as e:
            die(f"invalid TOML in batch {path}: {e}")
        self.name = str(self.raw.get("batch", path.stem))
        base = str(self.raw.get("base", cfg["run"]["base"]))
        self.base = git("rev-parse", "--abbrev-ref", "HEAD", cwd=root) if base in ("current", "HEAD") else base
        self.tasks = [Task(t, self) for t in self.raw.get("task", [])]
        self.by_id = {t.id: t for t in self.tasks}
        vals = path_values(root)
        self.wt_root = expand(cfg["run"]["worktree_root"], vals) / self.name

    def models_for(self, t: Task):
        if t.models:
            return t.models
        return [str(m) for m in self.cfg["models"].get(t.tier, [])]


def batch_path(arg: str, root: Path) -> Path:
    p = Path(arg)
    if p.exists():
        return p.resolve()
    cand = root / ".swarm" / "batches" / (arg if arg.endswith(".toml") else f"{arg}.toml")
    return cand if cand.exists() else p


def in_scope(path: str, patterns: list) -> bool:
    for pat in patterns:
        if pat.endswith("/") and path.startswith(pat):
            return True
        if path == pat or fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(Path(path).name, pat):
            return True
    return False


def render_prompt(b: Batch, t: Task, feedback: str = "") -> tuple[str, int]:
    cfg = b.cfg
    caps = []
    for spec in t.capsules:
        body, _ = resolve_capsule(spec, b.root, cfg)
        caps.append(body)
    cap_text = "\n\n".join(caps)
    tpl = expand(cfg["prompt"]["template"], path_values(b.root)).read_text()
    blocks = {
        "title": t.title,
        "goal": t.goal,
        "context_block": f"\n# Context (from the orchestrator; trust it)\n{t.context}\n" if t.context else "",
        "files_list": "\n".join(f"- {f}" for f in t.files),
        "read_block": ("You may READ these for reference:\n" + "\n".join(f"- {f}" for f in t.read) + "\n") if t.read else "",
        "accept": t.accept,
        "capsule_block": f"\n# Repo conventions (follow them)\n{cap_text}\n" if cap_text else "",
        "feedback_block": f"\n# Previous attempt failed (start over from a clean tree)\n{feedback}\n" if feedback else "",
    }
    return fill(tpl, blocks), len(cap_text)


def lint(b: Batch) -> dict:
    g, sc = b.cfg["granularity"], b.cfg["scope"]
    errors, warnings, tasks = [], [], []
    if not b.tasks:
        errors.append("batch has no [[task]] entries")
    seen = set()
    for t in b.tasks:
        tag = f"[{t.id or '?'}]"
        if not ID_RE.match(t.id):
            errors.append(f"{tag} id must be kebab-case, max 48 chars")
        if t.id in seen:
            errors.append(f"{tag} duplicate id")
        seen.add(t.id)
        if not t.goal:
            errors.append(f"{tag} no goal")
        if not t.files and not t.allow_empty:
            errors.append(f"{tag} no files: a bullet needs a target")
        if not t.accept:
            errors.append(f"{tag} no accept command (task or [verify].accept): a bullet needs a way to know it hit")
        elif t.accept.strip() in ("true", ":", "exit 0"):
            warnings.append(f"{tag} accept is a no-op; nothing verifies this task")
        if len(t.files) > g["max_files"]:
            errors.append(f"{tag} {len(t.files)} files > max_files={g['max_files']}: split the task")
        if any(c in f for f in t.files for c in "*?["):
            warnings.append(f"{tag} glob in files widens the scope; prefer exact paths")
        if len(t.goal) > g["max_goal_chars"]:
            errors.append(f"{tag} goal is {len(t.goal)} chars > {g['max_goal_chars']}: split the task")
        if len(t.context) > g["max_context_chars"]:
            errors.append(f"{tag} context is {len(t.context)} chars > {g['max_context_chars']}: pass less, more precise context")
        for block in re.findall(r"```.*?\n(.*?)```", t.context, flags=re.S):
            n = block.count("\n")
            if n > g["max_context_code_lines"]:
                errors.append(f"{tag} context has a {n}-line code block > {g['max_context_code_lines']}: "
                              "pass signatures and the few lines that matter, or put the file in `read`")
        if len(t.read) > 3:
            warnings.append(f"{tag} {len(t.read)} reference files; a bullet rarely needs more than 1-2")
        bad = [f for f in t.files + t.read if in_scope(f, sc["forbidden"])]
        if bad:
            errors.append(f"{tag} forbidden paths in scope: {bad}")
        for d in t.depends_on:
            if d not in b.by_id:
                errors.append(f"{tag} depends_on unknown task '{d}'")
        models = b.models_for(t)
        if not models:
            errors.append(f"{tag} tier '{t.tier}' has no models in [models]")
        total = 0
        for spec in t.capsules:
            try:
                body, _ = resolve_capsule(spec, b.root, b.cfg)
                total += len(body)
                if len(body) > g["max_capsule_chars"]:
                    errors.append(f"{tag} capsule '{spec}' is {len(body)} chars > {g['max_capsule_chars']}: select sections (name#a,b) or trim it")
            except ValueError as e:
                errors.append(f"{tag} {e}")
        if total > g["max_total_capsule_chars"]:
            errors.append(f"{tag} capsules total {total} chars > {g['max_total_capsule_chars']}")
        prompt_chars = None
        if not any(e.startswith(tag) for e in errors):
            prompt_chars = len(render_prompt(b, t)[0])
        tasks.append({"id": t.id, "tier": t.tier, "files": t.files, "deps": t.depends_on, "prompt_chars": prompt_chars})
    # cycles
    state = {}

    def visit(tid, stack):
        if state.get(tid) == 1:
            errors.append(f"dependency cycle: {' -> '.join(stack + [tid])}")
            return
        if state.get(tid) == 2 or tid not in b.by_id:
            return
        state[tid] = 1
        for d in b.by_id[tid].depends_on:
            visit(d, stack + [tid])
        state[tid] = 2

    for t in b.tasks:
        visit(t.id, [])
    # overlapping scopes between tasks that may run at the same time
    def ancestors(tid, acc=None):
        acc = set() if acc is None else acc
        for d in (b.by_id[tid].depends_on if tid in b.by_id else []):
            if d not in acc:
                acc.add(d)
                ancestors(d, acc)
        return acc

    for i, a in enumerate(b.tasks):
        for c in b.tasks[i + 1:]:
            if a.id in ancestors(c.id) or c.id in ancestors(a.id):
                continue
            shared = sorted(set(a.files) & set(c.files))
            if shared:
                errors.append(f"[{a.id}] and [{c.id}] both modify {shared} in parallel: add depends_on or merge them")
    if b.base:
        dirty = git("status", "--porcelain", "--untracked-files=no", cwd=b.root)
        if dirty:
            warnings.append("main worktree has uncommitted changes; workers only see committed code on " + b.base)
    ok = not errors or not g["enforce"]
    return {"ok": ok, "batch": b.name, "base": b.base, "errors": errors, "warnings": warnings, "tasks": tasks}


# ----------------------------------------------------------------------------- run

class Run:
    def __init__(self, b: Batch, args):
        self.b, self.args = b, args
        self.dir = b.root / ".swarm" / "runs" / b.name / now_stamp()
        self.dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.state = {"batch": b.name, "base": b.base, "run_dir": str(self.dir), "started": dt.datetime.now().isoformat(timespec="seconds"),
                      "finished": None, "tasks": {t.id: {"status": "pending"} for t in self.selected()}}
        self.save()

    def selected(self):
        only = set(self.args.only.split(",")) if self.args.only else None
        return [t for t in self.b.tasks if only is None or t.id in only]

    def save(self):
        with self.lock:
            (self.dir / "state.json").write_text(json.dumps(self.state, indent=1, ensure_ascii=False))

    def update(self, tid, **kw):
        with self.lock:
            self.state["tasks"][tid].update(kw)
        self.save()


def remove_worktree(root: Path, wt: Path):
    if wt.exists():
        sh(["git", "worktree", "remove", "--force", str(wt)], cwd=root, check=False)
        if wt.exists():
            shutil.rmtree(wt, ignore_errors=True)
    sh(["git", "worktree", "prune"], cwd=root, check=False)


def prepare_worktree(b: Batch, t: Task, dep_branches: list) -> Path:
    wt = b.wt_root / t.id
    with GIT_LOCK:
        remove_worktree(b.root, wt)
        wt.parent.mkdir(parents=True, exist_ok=True)
        start = dep_branches[0] if dep_branches else b.base
        git("worktree", "add", "-f", "-B", t.branch, str(wt), start, cwd=b.root)
    for extra in dep_branches[1:]:
        r = sh(["git", "merge", "--no-edit", extra], cwd=wt, check=False)
        if r.returncode != 0:
            sh(["git", "merge", "--abort"], cwd=wt, check=False)
            raise RuntimeError(f"dependencies conflict when combined ({extra}); merge them first")
    return wt


def changed_files(wt: Path, base_commit: str) -> list:
    git("add", "-A", cwd=wt)
    out = git("diff", "--cached", "--name-only", "--no-renames", base_commit, cwd=wt)
    return [l for l in out.splitlines() if l]


def run_cmd_logged(cmd, cwd: Path, log: Path, timeout: int, env=None, shell=False):
    with open(log, "w") as fh:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             env=env, shell=shell, start_new_session=True, text=True)
        try:
            rc, timed_out = p.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
            rc, timed_out = -9, True
    return rc, timed_out, log.read_text(errors="replace")


def parse_report(out: str) -> dict:
    clean = ANSI_RE.sub("", out)
    idx = clean.rfind("STATUS:")
    if idx < 0:
        return {"status": None, "changed": "", "notes": ""}
    lines = clean[idx:].splitlines()
    rep = {"status": lines[0].split(":", 1)[1].strip().split()[0].upper() if lines[0].split(":", 1)[1].strip() else None,
           "changed": "", "notes": ""}
    notes, in_notes = [], False
    for l in lines[1:]:
        if l.startswith("CHANGED:"):
            rep["changed"] = l.split(":", 1)[1].strip()
        elif l.startswith("NOTES:"):
            in_notes = True
            notes.append(l.split(":", 1)[1].strip())
        elif in_notes:
            if not l.strip() or len(notes) >= 3:
                break
            notes.append(l.strip())
    rep["notes"] = " | ".join(n for n in notes if n)[:400]
    return rep


def execute_task(run: Run, t: Task) -> dict:
    b, cfg = run.b, run.b.cfg
    tdir = run.dir / t.id
    tdir.mkdir(exist_ok=True)
    dep_branches = [b.by_id[d].branch for d in t.depends_on]
    res = {"id": t.id, "status": "error", "branch": t.branch, "model": None, "attempts": 0, "changed": [], "diffstat": "",
           "notes": "", "fail_reason": "", "logs": str(tdir)}
    try:
        run.update(t.id, status="preparing")
        wt = prepare_worktree(b, t, dep_branches)
        res["worktree"] = str(wt)
        env = {**os.environ, **{k: str(v) for k, v in cfg["backend"].get("env", {}).items()}}
        if cfg["verify"]["setup"]:
            rc, _, out = run_cmd_logged(cfg["verify"]["setup"], wt, tdir / "setup.log", cfg["verify"]["accept_timeout_sec"], env, shell=True)
            if rc != 0:
                raise RuntimeError("setup failed: " + tail(out, 600))
        base_commit = git("rev-parse", "HEAD", cwd=wt)
        models = b.models_for(t)
        feedback = ""
        allowed = t.files + cfg["scope"]["always_allowed"]
        for i in range(max(1, int(cfg["run"]["max_attempts"]))):
            model = models[i % len(models)]
            res.update(attempts=i + 1, model=model)
            run.update(t.id, status="firing", attempt=i + 1, model=model)
            if i:
                git("reset", "--hard", base_commit, cwd=wt)
                git("clean", "-fd", cwd=wt)
            prompt, _ = render_prompt(b, t, feedback)
            pf = tdir / f"prompt-{i + 1}.md"
            pf.write_text(prompt)
            vals = {"model": model, "worktree": str(wt), "prompt": prompt, "prompt_file": str(pf), "task": t.id, "batch": b.name}
            rc, timed_out, out = run_cmd_logged(fill_cmd(cfg["backend"]["cmd"], vals), wt, tdir / f"attempt-{i + 1}.log",
                                                int(cfg["run"]["timeout_sec"]), env)
            rep = parse_report(out)
            res["notes"] = rep["notes"]
            if timed_out:
                feedback = f"You ran out of time ({cfg['run']['timeout_sec']}s). Do less exploring; go straight to the change."
                res["fail_reason"] = "timeout"
                continue
            if rep["status"] == "BLOCKED":
                res.update(status="blocked", fail_reason="worker reported BLOCKED")
                return res
            changed = changed_files(wt, base_commit)
            if not changed and not t.allow_empty:
                feedback = "You finished without changing any file. The task requires changes to the scoped files."
                res["fail_reason"] = f"no changes (worker exit {rc})" + (": " + tail(out, 300) if rc else "")
                continue
            outside = [f for f in changed if not in_scope(f, allowed)]
            if outside:
                feedback = f"You modified files outside your scope: {outside}. All changes were discarded. Touch only: {t.files}."
                res["fail_reason"] = f"scope violation: {outside}"
                continue
            run.update(t.id, status="verifying")
            arc, atimed, aout = run_cmd_logged(t.accept, wt, tdir / f"accept-{i + 1}.log", int(cfg["verify"]["accept_timeout_sec"]), env, shell=True)
            if arc != 0:
                feedback = f"Acceptance command `{t.accept}` failed{' (timeout)' if atimed else ''}. Output tail:\n{tail(aout, 1500)}"
                res["fail_reason"] = f"accept failed (exit {arc}{', timeout' if atimed else ''})" + (f": {tail(aout, 300)}" if aout.strip() else ", no output")
                continue
            # success: squash everything into one commit on the task branch
            with GIT_LOCK:
                git("reset", "--soft", base_commit, cwd=wt)
                git("add", "-A", cwd=wt)
                if changed:
                    ident = [] if git("config", "user.email", cwd=wt, check=False) else \
                        ["-c", "user.name=delegate-swarm", "-c", "user.email=swarm@localhost"]
                    git(*ident, "commit", "-q", "--no-verify", "-m", t.commit, "-m", f"worker-model: {model}\nattempts: {i + 1}", cwd=wt)
            res.update(status="done", changed=changed, fail_reason="",
                       diffstat=git("diff", "--shortstat", base_commit, "HEAD", cwd=wt))
            return res
        res["status"] = "failed"
        return res
    except Exception as e:  # noqa: BLE001
        res.update(status="error", fail_reason=str(e)[:600])
        return res
    finally:
        run.update(t.id, **{k: res[k] for k in ("status", "model", "attempts", "fail_reason")})


def cmd_run(args, root, cfg):
    b = Batch(batch_path(args.batch, root), root, cfg)
    report = lint(b)
    if args.only:  # only errors that concern the tasks being fired (or the batch as a whole) block a partial run
        ids = set(args.only.split(","))
        report["errors"] = [e for e in report["errors"] if not e.startswith("[") or any(f"[{i}]" in e for i in ids)]
        report["ok"] = not report["errors"] or not cfg["granularity"]["enforce"]
    if not report["ok"]:
        emit({**report, "fired": False})
        sys.exit(1)
    run = Run(b, args)
    tasks = run.selected()
    if not tasks:
        die("--only matched no tasks")
    selected_ids = {t.id for t in tasks}
    done, results = {}, {}
    pending = list(tasks)
    par = args.parallel or int(cfg["run"]["max_parallel"])
    with cf.ThreadPoolExecutor(max_workers=par) as ex:
        futures = {}
        while pending or futures:
            for t in list(pending):
                deps = t.depends_on
                # deps outside --only must already exist as branches (from an earlier run)
                unmet = [d for d in deps if d in selected_ids and d not in done]
                failed = [d for d in deps if d in done and done[d] != "done"]
                missing = [d for d in deps if d not in selected_ids and
                           sh(["git", "rev-parse", "--verify", "-q", b.by_id[d].branch], cwd=root, check=False).returncode != 0]
                if failed or missing:
                    pending.remove(t)
                    why = f"dependency not done: {failed or missing}"
                    results[t.id] = {"id": t.id, "status": "skipped", "fail_reason": why}
                    done[t.id] = "skipped"
                    run.update(t.id, status="skipped", fail_reason=why)
                elif not unmet and len(futures) < par:
                    pending.remove(t)
                    futures[ex.submit(execute_task, run, t)] = t
            if not futures:
                continue
            fin, _ = cf.wait(futures, return_when=cf.FIRST_COMPLETED)
            for f in fin:
                t = futures.pop(f)
                results[t.id] = f.result()
                done[t.id] = results[t.id]["status"]
    ordered = [results[t.id] for t in tasks]
    counts = {}
    for r in ordered:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    summary = {"ok": all(r["status"] == "done" for r in ordered), "batch": b.name, "base": b.base, "run_dir": str(run.dir),
               "counts": counts, "warnings": report["warnings"], "tasks": ordered}
    (run.dir / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    run.state["finished"] = dt.datetime.now().isoformat(timespec="seconds")
    run.save()
    # compact view for the orchestrator: no paths it doesn't need
    compact = {**summary, "tasks": [{k: v for k, v in r.items() if k not in ("worktree",) and v not in ("", [], None)} for r in ordered]}
    emit(compact)


# ----------------------------------------------------------------------------- run lookup

def latest_run(root: Path, batch: str, which: str | None) -> Path:
    base = root / ".swarm" / "runs" / batch
    if which:
        p = base / which
        if not p.exists():
            die(f"run {which} not found in {base}")
        return p
    runs = sorted(p for p in base.glob("*") if p.is_dir()) if base.exists() else []
    if not runs:
        die(f"no runs for batch '{batch}'")
    return runs[-1]


def merged_results(root: Path, batch: str) -> dict:
    """Latest result per task across all runs of a batch (reruns with --only override older ones)."""
    base = root / ".swarm" / "runs" / batch
    out = {}
    for d in sorted(p for p in base.glob("*") if p.is_dir()) if base.exists() else []:
        s = d / "summary.json"
        if s.exists():
            for r in json.loads(s.read_text())["tasks"]:
                out[r["id"]] = r
    return out


def cmd_status(args, root, cfg):
    name = Path(args.batch).stem
    d = latest_run(root, name, args.run)
    st = json.loads((d / "state.json").read_text())
    emit({"batch": name, "run_dir": str(d), "finished": st.get("finished"), "tasks": st["tasks"],
          "latest_per_task": {k: v.get("status") for k, v in merged_results(root, name).items()}})


# ----------------------------------------------------------------------------- ship

def cmd_ship(args, root, cfg):
    b = Batch(batch_path(args.batch, root), root, cfg)
    results = merged_results(root, b.name)
    ready = [b.by_id[i] for i, r in results.items() if r["status"] == "done" and i in b.by_id]
    if args.only:
        keep = set(args.only.split(","))
        ready = [t for t in ready if t.id in keep]
    if not ready:
        die("nothing to ship: no task with status done")
    ship_file = root / ".swarm" / "runs" / b.name / "ship.json"
    shipped = json.loads(ship_file.read_text()) if ship_file.exists() else {}
    out = []
    if args.mode == "merge":
        integ = f"{cfg['run']['branch_prefix']}/{b.name}/integration"
        wt = b.wt_root / "_integration"
        with GIT_LOCK:
            remove_worktree(root, wt)
            git("worktree", "add", "-f", "-B", integ, str(wt), b.base, cwd=root)
        for t in ready:
            r = sh(["git", "merge", "--no-ff", "--no-edit", t.branch], cwd=wt, check=False)
            if r.returncode == 0:
                out.append({"id": t.id, "merged": True})
            else:
                conflicts = git("diff", "--name-only", "--diff-filter=U", cwd=wt, check=False).splitlines()
                sh(["git", "merge", "--abort"], cwd=wt, check=False)
                out.append({"id": t.id, "merged": False, "conflicts": conflicts})
        accept = cfg["verify"]["accept"]
        verdict = None
        if accept and not args.no_verify:
            if cfg["verify"]["setup"]:
                subprocess.run(cfg["verify"]["setup"], cwd=wt, shell=True, capture_output=True)
            r = subprocess.run(accept, cwd=wt, shell=True, capture_output=True, text=True, timeout=int(cfg["verify"]["accept_timeout_sec"]))
            verdict = {"command": accept, "exit": r.returncode, "tail": tail(r.stdout + r.stderr, 600) if r.returncode else ""}
        emit({"ok": all(o["merged"] for o in out) and (verdict is None or verdict["exit"] == 0), "mode": "merge",
              "integration_branch": integ, "worktree": str(wt), "repo_verify": verdict, "tasks": out,
              "next": f"review then: git checkout {b.base} && git merge --no-ff {integ}"})
        return
    fg = cfg["forge"]
    if fg["name"] == "none" or not fg.get("pr_create"):
        die("forge is 'none': use `ship --mode merge`")
    for t in ready:
        if t.id in shipped and not args.force:
            out.append({"id": t.id, "pr": shipped[t.id].get("pr"), "note": "already shipped (use --force to push again)"})
            continue
        r = results[t.id]
        body = root / ".swarm" / "runs" / b.name / f"pr-{t.id}.md"
        body.write_text(
            f"{t.goal}\n\n**Acceptance:** `{t.accept}` passed.\n\n"
            f"**Worker:** {r.get('model')} · attempts: {r.get('attempts')} · {r.get('diffstat', '')}\n\n"
            + (f"**Worker notes:** {r['notes']}\n\n" if r.get("notes") else "")
            + f"_Batch `{b.name}`, task `{t.id}`. Opened by delegate-swarm._\n")
        # a task chained on exactly one shipped dependency opens a stacked PR against that branch,
        # so its diff shows only its own change (GitHub retargets it when the parent merges)
        pr_base = b.by_id[t.depends_on[0]].branch if len(t.depends_on) == 1 and t.depends_on[0] in shipped else b.base
        vals = {"branch": t.branch, "base": pr_base, "title": t.title, "body_file": str(body), "task": t.id, "batch": b.name}
        p = sh(fill_cmd(fg["push"], vals), cwd=root, check=False)
        if p.returncode != 0:
            out.append({"id": t.id, "error": "push failed: " + tail(p.stderr or p.stdout, 400)})
            continue
        cmd = fill_cmd(fg["pr_create"], vals) + (["--draft"] if args.draft else [])
        c = sh(cmd, cwd=root, check=False)
        url = next((l for l in reversed((c.stdout or "").splitlines()) if l.startswith("http")), None)
        if c.returncode != 0:
            out.append({"id": t.id, "error": "PR failed: " + tail(c.stderr or c.stdout, 400)})
            continue
        shipped[t.id] = {"branch": t.branch, "pr": url, "base": pr_base}
        out.append({"id": t.id, "pr": url, **({"stacked_on": pr_base} if pr_base != b.base else {})})
    ship_file.write_text(json.dumps(shipped, indent=1))
    emit({"ok": all("error" not in o for o in out), "mode": "pr", "tasks": out})


def cmd_checks(args, root, cfg):
    name = Path(args.batch).stem
    ship_file = root / ".swarm" / "runs" / name / "ship.json"
    if not ship_file.exists():
        die("no PRs shipped for this batch yet")
    shipped = json.loads(ship_file.read_text())
    out = []
    for tid, s in shipped.items():
        r = sh(fill_cmd(cfg["forge"]["pr_checks"], {"branch": s["branch"], "pr": s.get("pr") or s["branch"]}), cwd=root, check=False)
        state = {0: "pass", 8: "pending"}.get(r.returncode, "fail")
        out.append({"id": tid, "pr": s.get("pr"), "checks": state, **({"tail": tail(r.stdout + r.stderr, 500)} if state == "fail" else {})})
    emit({"batch": name, "tasks": out})


# ----------------------------------------------------------------------------- misc commands

def cmd_lint(args, root, cfg):
    b = Batch(batch_path(args.batch, root), root, cfg)
    rep = lint(b)
    if args.show:
        t = b.by_id.get(args.show) or die(f"no task {args.show}")
        print(render_prompt(b, t)[0])
        return
    emit(rep)
    sys.exit(0 if rep["ok"] else 1)


def cmd_capsule(args, root, cfg):
    try:
        body, src = resolve_capsule(args.spec, root, cfg)
    except ValueError as e:
        die(str(e))
    if args.quiet:
        emit({"spec": args.spec, "source": src, "chars": len(body), "limit": cfg["granularity"]["max_capsule_chars"]})
    else:
        print(body)
        print(f"\n--- {len(body)} chars (limit {cfg['granularity']['max_capsule_chars']}) from {src}", file=sys.stderr)


def detect_commands(root: Path) -> dict:
    """Best guess of (setup, accept) for common stacks. Empty strings when unsure."""
    f = lambda n: (root / n).exists()  # noqa: E731
    if f("package.json"):
        try:
            scripts = json.loads((root / "package.json").read_text()).get("scripts", {})
        except json.JSONDecodeError:
            scripts = {}
        test = scripts.get("test", "")
        has_test = bool(test) and "no test specified" not in test
        if f("pnpm-lock.yaml"):
            pm, setup = "pnpm", "pnpm install --frozen-lockfile --silent"
        elif f("yarn.lock"):
            pm, setup = "yarn", "yarn install --frozen-lockfile --silent"
        elif f("bun.lockb") or f("bun.lock"):
            pm, setup = "bun", "bun install --frozen-lockfile"
        else:
            pm, setup = "npm", "npm ci --silent" if f("package-lock.json") else "npm install --silent"
        if has_test:
            return {"stack": "node", "setup": setup, "accept": f"{pm} test"}
        for alt in ("typecheck", "lint", "build"):
            if alt in scripts:
                return {"stack": "node", "setup": setup, "accept": f"{pm} run {alt}", "note": "no test script; using " + alt}
        return {"stack": "node", "setup": setup, "accept": ""}
    if f("pyproject.toml") or f("setup.py") or f("pytest.ini") or f("requirements.txt"):
        if f("uv.lock"):
            return {"stack": "python", "setup": "uv sync -q", "accept": "uv run pytest -q"}
        if f("poetry.lock"):
            return {"stack": "python", "setup": "poetry install -q", "accept": "poetry run pytest -q"}
        has_tests = f("tests") or f("test") or f("pytest.ini") or any(root.glob("test_*.py"))
        return {"stack": "python", "setup": "", "accept": "python3 -m pytest -q" if has_tests else ""}
    if f("Cargo.toml"):
        return {"stack": "rust", "setup": "", "accept": "cargo test -q"}
    if f("go.mod"):
        return {"stack": "go", "setup": "", "accept": "go test ./..."}
    if f("gradlew"):
        return {"stack": "gradle", "setup": "", "accept": "./gradlew test -q"}
    if f("pom.xml"):
        return {"stack": "maven", "setup": "", "accept": "mvn -q test"}
    if f("Makefile") and re.search(r"^test\s*:", (root / "Makefile").read_text(errors="ignore"), re.M):
        return {"stack": "make", "setup": "", "accept": "make test"}
    return {"stack": "unknown", "setup": "", "accept": ""}


def detect_skills(root: Path, cfg: dict) -> dict:
    """Skills this repo probably uses, and which of them still lack a capsule."""
    found = set()
    for d in (root / ".claude" / "skills").glob("*/SKILL.md"):
        found.add(d.parent.name)
    docs = " ".join((root / n).read_text(errors="ignore") for n in ("CLAUDE.md", "AGENTS.md", ".claude/CLAUDE.md") if (root / n).exists())
    known = [d.parent.name for d in Path("~/.claude/skills").expanduser().glob("*/SKILL.md")]
    found |= {k for k in known if k in docs}
    if (root / "00-inbox").is_dir() and (root / f"{root.name}.md").exists():
        found.add("memory-vault")  # vault layout: root master file + inbox
    vals = path_values(root)
    have = {p.stem for d in cfg["capsules"]["paths"] for p in expand(d, vals).glob("*.md") if not p.stem.startswith("_")}
    return {"used": sorted(found), "missing_capsules": sorted(found - have)}


def cmd_init(args, root, cfg):
    sw = root / ".swarm"
    (sw / "capsules").mkdir(parents=True, exist_ok=True)
    (sw / "batches").mkdir(exist_ok=True)
    created, detected = [], None
    skills = detect_skills(root, cfg)
    if not (sw / "config.toml").exists():
        text = (SKILL_DIR / "templates" / "repo-config.example.toml").read_text()
        if args.auto:
            detected = detect_commands(root)
            text = text.replace('accept = ""', f'accept = {json.dumps(detected["accept"])}', 1)
            text = text.replace('setup = ""', f'setup = {json.dumps(detected["setup"])}', 1)
            if "memory-vault" in skills["used"]:
                text = text.replace("default = []", 'default = ["memory-vault#structure,master-files"]', 1)
        (sw / "config.toml").write_text(text)
        created.append(".swarm/config.toml")
    common = Path(git("rev-parse", "--git-common-dir", cwd=root))
    common = common if common.is_absolute() else root / common
    excl = common / "info" / "exclude"
    excl.parent.mkdir(parents=True, exist_ok=True)
    cur = excl.read_text() if excl.exists() else ""
    add = [l for l in (".swarm/runs/", ".swarm/batches/") if l not in cur.splitlines()]
    if add:
        excl.write_text(cur + ("" if cur.endswith("\n") or not cur else "\n") + "\n".join(add) + "\n")
    todo = []
    if detected is not None and not detected["accept"]:
        todo.append("no test command detected: set [verify].accept in .swarm/config.toml (ask the user if the repo has no tests)")
    elif detected is None and created:
        todo.append("set [verify].accept and setup in .swarm/config.toml")
    for s in skills["missing_capsules"]:
        todo.append(f"distill a capsule for skill '{s}' into .swarm/capsules/{s}.md (SKILL.md section 05)")
    todo.append("verify the accept command passes on the base branch, then commit .swarm/config.toml and .swarm/capsules/")
    emit({"ok": True, "created": created, "detected": detected, "skills": skills, "ignored_locally": add, "todo": todo})


def fix_models(cfg: dict, avail: set, free: list) -> dict:
    """Drop vanished models from each tier, top up with still-available free ones, write the global config."""
    tiers = {k: v for k, v in cfg["models"].items() if isinstance(v, list)}
    new, changed = {}, {}
    for tier, models in tiers.items():
        keep = [m for m in models if m in avail]
        for m in free:
            if len(keep) >= max(3, len(models)):
                break
            if m not in keep:
                keep.append(m)
        new[tier] = keep
        if keep != models:
            changed[tier] = keep
    if changed:
        gp = GLOBAL_DIR / "config.toml"
        gp.parent.mkdir(parents=True, exist_ok=True)
        text = gp.read_text() if gp.exists() else ""
        text = re.sub(r"(?ms)^# >>> swarm doctor --fix.*?^# <<< swarm doctor --fix\n?", "", text)
        if re.search(r"(?m)^\[models\]", text):
            return {"warning": "[models] already set by hand in global config; update it manually", "suggested": changed}
        block = "# >>> swarm doctor --fix (managed; edit freely or delete)\n[models]\n" + \
            "".join(f"{t} = {json.dumps(v)}\n" for t, v in new.items()) + "# <<< swarm doctor --fix\n"
        gp.write_text(text.rstrip() + ("\n\n" if text.strip() else "") + block)
    return changed


def cmd_doctor(args, root, cfg):
    checks = []

    def add(name, ok, detail=""):
        checks.append({"check": name, "ok": ok, **({"detail": detail} if detail else {})})

    add("python>=3.11", sys.version_info >= (3, 11), sys.version.split()[0])
    add("git repo", True, str(root))
    bk = cfg["backend"]["cmd"][0]
    add(f"backend '{bk}' on PATH", shutil.which(bk) is not None)
    if cfg["backend"].get("list_models") and shutil.which(cfg["backend"]["list_models"][0]):
        r = sh(cfg["backend"]["list_models"], cwd=root, check=False, timeout=60)
        avail = set(ANSI_RE.sub("", r.stdout).split())
        for tier in [k for k, v in cfg["models"].items() if isinstance(v, list)]:
            gone = [m for m in cfg["models"][tier] if m not in avail]
            add(f"models in tier '{tier}' available", not gone, f"missing: {gone}" if gone else f"{len(cfg['models'][tier])} ok")
        free = sorted(m for m in avail if "free" in m or m.endswith("big-pickle"))
        add("free models listed by backend", bool(free), ", ".join(free[:15]))
        if getattr(args, "fix", False) and free:
            fixed = fix_models(cfg, avail, free)
            if fixed:
                add("models fixed in ~/.config/delegate-swarm/config.toml", True, json.dumps(fixed))
    fg = cfg["forge"]
    if fg["name"] != "none":
        fb = fg["pr_create"][0]
        add(f"forge '{fb}' on PATH", shutil.which(fb) is not None)
        if fg.get("auth_check") and shutil.which(fg["auth_check"][0]):
            r = sh(fg["auth_check"], cwd=root, check=False)
            add("forge auth", r.returncode == 0, tail(r.stderr or r.stdout, 200) if r.returncode else "")
        add("git remote 'origin'", sh(["git", "remote", "get-url", "origin"], cwd=root, check=False).returncode == 0)
    add("repo config", (root / ".swarm" / "config.toml").exists(), "run `swarm init`" if not (root / ".swarm" / "config.toml").exists() else "")
    add("[verify].accept set", bool(cfg["verify"]["accept"]), "tasks must then each set accept" if not cfg["verify"]["accept"] else cfg["verify"]["accept"])
    emit({"ok": all(c["ok"] for c in checks), "checks": checks})


def cmd_clean(args, root, cfg):
    vals = path_values(root)
    wt_base = expand(cfg["run"]["worktree_root"], vals)
    targets = [wt_base] if args.all else [wt_base / Path(args.batch).stem]
    removed = []
    for tgt in targets:
        if tgt.exists():
            for wt in sorted(p for p in tgt.rglob("*") if p.is_dir() and (p / ".git").exists()):
                remove_worktree(root, wt)
                removed.append(str(wt))
            shutil.rmtree(tgt, ignore_errors=True)
    sh(["git", "worktree", "prune"], cwd=root, check=False)
    branches = []
    if args.branches:
        prefix = cfg["run"]["branch_prefix"] + "/" + ("" if args.all else Path(args.batch).stem + "/")
        for br in git("for-each-ref", "--format=%(refname:short)", f"refs/heads/{prefix}", cwd=root).splitlines():
            if sh(["git", "branch", "-D", br], cwd=root, check=False).returncode == 0:
                branches.append(br)
    emit({"ok": True, "worktrees_removed": len(removed), "branches_deleted": branches})


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="swarm", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="path inside the target repo (default: cwd)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init", help="create .swarm/ in the repo")
    p.add_argument("--auto", action="store_true", help="detect setup/accept commands and the repo's skills")
    p = sp.add_parser("doctor", help="check backend, models, forge and config")
    p.add_argument("--fix", action="store_true", help="replace vanished models with available free ones (global config)")
    p = sp.add_parser("lint", help="check granularity and render prompts without firing")
    p.add_argument("batch")
    p.add_argument("--show", metavar="TASK_ID", help="print the full prompt one task would get")
    p = sp.add_parser("run", help="fire the batch")
    p.add_argument("batch")
    p.add_argument("--only", help="comma-separated task ids")
    p.add_argument("--parallel", type=int)
    p = sp.add_parser("status", help="progress of the latest (or a given) run")
    p.add_argument("batch")
    p.add_argument("--run")
    p = sp.add_parser("ship", help="open PRs (default) or merge done tasks into an integration branch")
    p.add_argument("batch")
    p.add_argument("--mode", choices=["pr", "merge"], default="pr")
    p.add_argument("--only")
    p.add_argument("--draft", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--no-verify", action="store_true", help="merge mode: skip the repo-wide accept run")
    p = sp.add_parser("checks", help="CI status of shipped PRs")
    p.add_argument("batch")
    p = sp.add_parser("capsule", help="print a resolved capsule, e.g. memory-vault#commit")
    p.add_argument("spec")
    p.add_argument("-q", "--quiet", action="store_true")
    p = sp.add_parser("clean", help="remove worktrees (and optionally branches)")
    p.add_argument("batch", nargs="?", default="")
    p.add_argument("--all", action="store_true")
    p.add_argument("--branches", action="store_true", help="also delete local task branches")
    args = ap.parse_args()
    if args.cmd == "clean" and not (args.batch or args.all):
        ap.error("clean needs a batch name or --all")
    root = repo_root(Path(args.repo).resolve())
    cfg = load_config(root)
    {"init": cmd_init, "doctor": cmd_doctor, "lint": cmd_lint, "run": cmd_run, "status": cmd_status, "ship": cmd_ship,
     "checks": cmd_checks, "capsule": cmd_capsule, "clean": cmd_clean}[args.cmd](args, root, cfg)


if __name__ == "__main__":
    main()
