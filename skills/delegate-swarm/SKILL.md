---
name: delegate-swarm
description: Orchestrate cheap/free coding agents (OpenCode by default) as single-task workers in parallel git worktrees, then ship each result as a PR. Use when building features, tests, refactors or boilerplate that can be split into small verifiable tasks, or when the user asks to delegate, use OpenCode, use free models, fan out, run agents in parallel, or save Claude usage.
---

# delegate-swarm — Claude aims, workers fire

You are the orchestrator. You think: decompose, brief, triage, decide. Workers are cheap agents running free models through `scripts/swarm.py`. **Each worker is a bullet, not a gun:** one small task, a fixed set of files, one command that proves it hit, and only the information it needs. Your tokens go into planning and judging; the workers' tokens go into typing code.

Run the CLI as `swarm` if it is on PATH, otherwise `python3 <this skill's dir>/scripts/swarm.py`; if neither works, run this skill's `install.sh` once. Every command prints compact JSON. Run it from inside the target repo (or pass `--repo PATH`).

## 01. Decide whether to delegate

Delegate when the work splits into tasks that are **mechanical and verifiable**: endpoints or components following an existing pattern, tests, CRUD, migrations, renames, docs, scripts, data transforms, config wiring.

Do it yourself when:
- the acceptance criterion can't be expressed as a command (design, UX judgment, prose quality);
- it is architecture, security, concurrency, memory management, or a subtle bug you haven't located yet;
- explaining it would take longer than writing it (a 3-line fix);
- the files contain secrets or client code that must not leave the machine. Free models may use the data for training.

## 02. Setup is your job, not the user's

Before the first batch in a repo, prepare it yourself, silently, without asking the user to run anything. If `.swarm/config.toml` already exists, only run step 1.

1. `swarm doctor --fix` — checks the backend, the forge and its login, and replaces free models that no longer exist with ones that do (writes `~/.config/delegate-swarm/config.toml`). If the backend binary is missing or the forge isn't logged in, tell the user the one command that fixes it (`gh auth login`, OpenCode's `/connect`) and stop; those need them.
2. `swarm init --auto` — creates `.swarm/`, detects the stack's `setup` and `accept` commands, and detects the skills the repo uses (repo `.claude/skills/`, skills named in CLAUDE.md/AGENTS.md, vault layout). Read its `todo` list and do every item:
   - **No accept detected:** look for the test command yourself (README, CI workflow files, Makefile). If the repo truly has no automated check, ask the user once what proves a change is correct; meanwhile, tasks can still set their own `accept` (a focused test, a type check, a `grep`).
   - **Missing capsules:** distill each one from its skill (section 05) into `.swarm/capsules/`.
   - **Verify:** run the `setup` and `accept` commands once on the base branch. If `accept` already fails there, every bullet will "miss": tell the user and don't fire until it passes or you pick a narrower command.
3. Commit `.swarm/config.toml` and `.swarm/capsules/` (on the current branch, normal commit message for the repo).

Then report setup in one line to the user (stack, accept command, capsules) and continue with the actual work.

Workers only see **committed** code on the base branch. Commit (or stash) your own work before firing.

## 03. Decompose — granularity is the whole game

Split until every task passes all of these:
- **One behavior change.** If the title needs "and", split it.
- **At most 3 files modified** (`max_files`). The implementation plus its test is the typical pair.
- **One acceptance command** that targets the change: a single test file, a type check of one module, a `grep` for a doc section. Prefer focused commands over the whole test suite; they are faster and their failure output is about this task.
- **Disjoint files between tasks that run in parallel.** If two tasks must touch the same file, chain them with `depends_on` (the dependent task starts from its dependency's branch) or merge them into one task.
- **No exploration needed.** If the worker would have to search the repo to find where things go, the task is under-specified, not too hard.

Too small is cheap (workers are free); too big is expensive (failed attempts, scope violations, your time triaging). When unsure, split.

Shared setup first: if several tasks need a new type, interface or helper, make that a task of its own and have the others `depends_on` it, or do it yourself and commit it before the batch.

## 04. Brief each worker — need-to-know only

You hold far more context than any worker needs. Do **not** forward it. A worker gets exactly what a competent stranger needs to do this one task without asking anything, and nothing else. For each task write:

- `goal` — what must be true when it's done, in 2-6 lines. Behavior, inputs, outputs, edge cases to cover. Not the history of the project, not why the feature exists.
- `files` — exact paths it may modify.
- `read` — at most 1-2 files to imitate (the sibling endpoint, the existing test). Prefer this over pasting code.
- `context` — the facts it would otherwise have to dig for: function **signatures** it must call, the import path, the name of the helper, the shape of a type, the one convention that isn't visible in the `read` file. Paste signatures and the few relevant lines, never whole files.
- `accept` — the command (section 03).
- `commit` — the commit message, in the repo's format (workers never run git).

Litmus test for every line of `goal` and `context`: *would the task fail or come out wrong without this line?* If not, cut it. In particular, leave out: other tasks in the batch, the overall plan, the conversation with the user, decisions that don't affect these files, repo-wide background.

The linter enforces the ceiling (`max_goal_chars`, `max_context_chars`, no code block longer than `max_context_code_lines`, `max_files`), but the ceiling is not the target. Most good briefs are well under it.

## 05. Capsules — the skill knowledge a worker needs, distilled

Repos often have their own skills (e.g. `memory-vault`, `vault-tickets`). A worker never gets a whole skill. It gets a **capsule**: a short Markdown file with only the rules that change how files in its scope must be written, split into sections you select per task.

- Capsules live in `.swarm/capsules/<name>.md` (repo, commit it), `~/.config/delegate-swarm/capsules/` (yours, all repos) or this skill's `capsules/` (bundled: `memory-vault`). First match wins.
- Sections are `## @name`. Select them per task: `capsules = ["memory-vault#master-files,assets"]`. Text before the first section is always included, so keep it to one or two sentences.
- Repo-wide default capsules go in `.swarm/config.toml` `[capsules].default`; keep that list minimal.
- Check one with `swarm capsule memory-vault#assets` (prints it and its size).

**Making a capsule from a skill** (do this the first time you delegate in a repo whose skill has no capsule yet): read the skill, start from `capsules/_template.md`, and keep only imperative rules about how files are named, structured and formatted, with one concrete example per format. Drop everything about sessions and orchestration — pulling, catching up, reading indexes, pushing, daily logs the orchestrator writes, git and commit rules (workers don't run git; you put the right message in `commit`). Aim for under ~500 characters per section and under 1500 per selection. Save it in the repo's `.swarm/capsules/` and commit it.

Pick capsule sections the same way as context: a task that edits one asset file gets `#assets`, not the whole vault manual.

## 06. Fire

Write the batch to `.swarm/batches/<name>.toml` (format: `templates/batch.example.toml`), then:

```bash
swarm lint <name>                 # granularity, scopes, capsules, parallel overlaps
swarm lint <name> --show <task>   # the exact prompt one worker will receive
swarm run <name>                  # fire
```

Fix every lint error by splitting or tightening tasks, not by raising limits. Read `--show` for at least one task per batch: if anything in it is not need-to-know, cut it.

`run` can exceed a tool timeout: launch it in the background (e.g. Bash with `run_in_background`) and poll `swarm status <name>`. Each task gets its own worktree outside the repo and branch `swarm/<batch>/<task>`. Up to `max_parallel` workers fire at once; dependent tasks wait for their dependencies.

Per task, the script: runs `setup`, fires the worker with the tier's first model, rejects the attempt if the worker changed nothing or touched files outside `files`, runs `accept`, and on failure resets the worktree and retries with the next model in the tier, passing the failure output as feedback. On success it squashes everything into one commit with your `commit` message.

## 07. Triage the summary — read results, not code

The `run` output is all you read. Per task: `status`, `model`, `attempts`, `changed`, `diffstat`, `notes`, `fail_reason`.

- `done` — acceptance passed. Don't read the diff unless the change touches something risky (auth, data deletion, money, concurrency) or `notes` mention a caveat. Then read only the diff: `git diff <base>...<branch>`.
- `blocked` — the worker asked a question (`notes`). Answer it in `context`, then `swarm run <name> --only <id>`.
- `failed` — read only the last `accept-N.log` tail in the task's log dir. Then pick one: tighten `goal`/`context` (usually missing a signature or path), split the task, move it to `tier = "strong"`, or do it yourself. Don't retry an unchanged task.
- `error` — infrastructure (setup, worktree, dependency conflict). Fix the cause; it isn't the worker's fault.
- `skipped` — a dependency didn't finish.

Rerunning with `--only` keeps other tasks' results; `ship` uses the latest result per task.

## 08. Ship

```bash
swarm ship <name>                 # push each done branch and open one PR per task
swarm ship <name> --draft
swarm checks <name>               # CI per PR: pass / pending / fail (+ tail on fail)
swarm ship <name> --mode merge    # no forge: merge done branches into swarm/<name>/integration and run [verify].accept there
swarm clean <name> [--branches]   # remove worktrees (and local task branches)
```

With CI, the PR checks are the referee: read `checks`, open only the PRs that fail. Tasks chained with `depends_on` produce PRs that contain their dependency's commits; merge them in order. Never merge into the base branch or push to it without the user's go-ahead.

## 09. Swapping platforms

Nothing is tied to OpenCode or GitHub; it's all in config (`config.default.toml` documents every key). Override in `~/.config/delegate-swarm/config.toml` or a repo's `.swarm/config.toml`:

```toml
# another agent CLI: any command that edits files in {worktree} given {prompt} (or {prompt_file})
[backend]
cmd = ["aider", "--yes-always", "--model", "{model}", "--message-file", "{prompt_file}"]
list_models = []

# reuse one warm OpenCode server instead of a cold start per worker
# cmd = ["opencode", "run", "--auto", "--attach", "http://localhost:4096", "-m", "{model}", "--dir", "{worktree}", "{prompt}"]

# GitLab
[forge]
name = "gitlab"
pr_create = ["glab", "mr", "create", "--source-branch", "{branch}", "--target-branch", "{base}", "--title", "{title}", "--description", "{body_file}", "--yes"]
pr_checks = ["glab", "ci", "status", "--branch", "{branch}"]
auth_check = ["glab", "auth", "status"]

# no forge at all: use `ship --mode merge`
# [forge]
# name = "none"
```

The worker prompt itself is `templates/worker-prompt.md`; point `[prompt].template` elsewhere to change it. Its final-reply contract (`STATUS / CHANGED / NOTES`) is what the script parses.

## 10. Safety

- Workers run with auto-approved tools inside a worktree. A worktree isolates files and branches, not the machine: don't delegate in repos where running arbitrary commands is unacceptable.
- `[scope].forbidden` (`.env`, keys, `secrets/`) can't be put in a task's scope, and the worker is told never to read secrets. Still, don't delegate repos whose tracked files hold secrets or confidential client code.
- The script never pushes to the base branch, never force-pushes, and only deletes branches under `swarm/` when you pass `clean --branches`.
