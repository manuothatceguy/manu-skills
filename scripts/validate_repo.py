#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
ARTIFACT_DIRS = (
    ROOT / "skills" / "building-course-study-guides" / "artifacts",
    ROOT / "skills" / "active-recall-anki" / "decks",
)


def outside_fences(lines):
    fence = None
    for line in lines:
        match = FENCE.match(line)
        if match:
            fence = None if fence == match.group(1) else fence or match.group(1)
            continue
        if fence is None:
            yield line


def validate_skill(path, text=None, staged=False):
    errors = []
    if text is None:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            return [f"{path}: cannot read skill: {error}"]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [f"{path}: missing YAML frontmatter opening delimiter"]
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return [f"{path}: missing YAML frontmatter closing delimiter"]
    fields = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    for required in ("name", "description"):
        if not fields.get(required):
            errors.append(f"{path}: frontmatter requires a non-empty {required}")
    for match in SKILL_LINK.finditer("\n".join(outside_fences(lines[end + 1:]))):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
            continue
        destination = (path.parent / target).resolve()
        if staged:
            try:
                relative = destination.relative_to(ROOT).as_posix()
            except ValueError:
                errors.append(f"{path}: local reference {target} is outside the repository index")
                continue
            result = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f":{relative}"], capture_output=True)
            if result.returncode:
                errors.append(f"{path}: broken staged local reference {target} (missing from index)")
        elif not destination.exists():
            errors.append(f"{path}: broken local reference {target}")
    return errors


def validate_html(path, text=None):
    if text is None:
        text = path.read_text(encoding="utf-8")
    required_tags = (r"<html\b", r"</html\s*>", r"<body\b", r"</body\s*>")
    if any(not re.search(pattern, text, re.I) for pattern in required_tags):
        return [f"{path}: expected a complete HTML document with opening and closing html and body elements"]
    validator = ROOT / "skills" / "building-course-study-guides" / "scripts" / "verify_build.py"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".html") as staged_file:
        staged_file.write(text)
        staged_file.flush()
        result = subprocess.run([sys.executable, str(validator), staged_file.name], text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    return [] if result.returncode == 0 else [f"{path}: {output or 'HTML validation failed'}"]


def validate_tsv(path, text=None):
    from importlib.util import module_from_spec, spec_from_file_location

    validator_path = ROOT / "skills" / "active-recall-anki" / "scripts" / "validate_deck.py"
    spec = spec_from_file_location("anki_validator", validator_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    if text is None:
        errors, _ = module.validate_deck(path)
    else:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".tsv") as staged_file:
            staged_file.write(text)
            staged_file.flush()
            errors, _ = module.validate_deck(Path(staged_file.name))
    return [] if errors == 0 else [f"{path}: Anki TSV validation reported {errors} error(s)"]


def validate_path(path, content=None):
    try:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
    except UnicodeDecodeError:
        return [f"{path}: staged content is not valid UTF-8"]
    if path.name == "SKILL.md" and path.parent.parent.name == "skills":
        return validate_skill(path, text, staged=content is not None)
    if path.suffix.lower() == ".html":
        return validate_html(path, text)
    if path.suffix.lower() == ".tsv":
        return validate_tsv(path, text)
    return []


def is_artifact_path(path):
    return any(path.is_relative_to(directory) for directory in ARTIFACT_DIRS)


def all_targets():
    targets = list((ROOT / "skills").glob("*/SKILL.md"))
    for directory in ARTIFACT_DIRS:
        if directory.exists():
            targets.extend(path for path in directory.rglob("*") if path.suffix.lower() in {".html", ".tsv"})
    return sorted(set(targets))


def staged_targets():
    result = subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--diff-filter=ACMRT", "--name-only", "-z"], capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip() or "git diff failed")
    targets = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = raw_path.decode("utf-8", errors="surrogateescape")
        path = ROOT / relative
        is_skill = path.name == "SKILL.md" and path.parent.parent.name == "skills"
        if not is_skill and not (path.suffix.lower() in {".html", ".tsv"} and is_artifact_path(path)):
            continue
        staged = subprocess.run(["git", "-C", str(ROOT), "show", f":{relative}"], capture_output=True)
        if staged.returncode:
            raise RuntimeError(staged.stderr.decode("utf-8", errors="replace").strip() or f"cannot read staged file {relative}")
        targets.append((path, staged.stdout))
    return targets


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate skill metadata, local references, study-guide HTML, and Anki TSV files")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all", action="store_true", help="validate all skills and educational artifacts")
    mode.add_argument("--staged", action="store_true", help="validate staged skills and educational artifacts")
    parser.add_argument("paths", nargs="*", help="specific skill, HTML, or TSV paths")
    args = parser.parse_args(argv)
    if args.all:
        targets = all_targets()
    elif args.staged:
        try:
            targets = staged_targets()
        except RuntimeError as error:
            print(error, file=sys.stderr)
            return 2
    elif args.paths:
        targets = [Path(path).resolve() for path in args.paths]
    else:
        targets = all_targets()
    failures = []
    for target in targets:
        path, content = target if isinstance(target, tuple) else (target, None)
        failures.extend(validate_path(path, content))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Validated {len(targets)} skill or educational artifact file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
