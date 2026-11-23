# manu-skills

A curated collection of agent skills for Codex, Claude Code, and any agent compatible with the [Agent Skills](https://skills.sh) format. Each skill follows progressive disclosure: concise instructions in `SKILL.md`, with heavy references and deterministic validators in `references/` and `scripts/`.

## Install

### Via `skills.sh` (recommended)

Install all skills or pick specific ones interactively:

```bash
npx skills add manuothatceguy/manu-skills
```

Install a single skill:

```bash
npx skills add manuothatceguy/manu-skills --skill designing-skills
```

List all discoverable skills without installing:

```bash
npx skills add manuothatceguy/manu-skills --list
```

### From a local checkout (symlinks)

To develop locally and keep this repository as the source of truth, symlink each skill into `~/.agents/skills` (Codex) or `~/.claude/skills` (Claude Code):

```bash
mkdir -p "$HOME/.agents/skills"
for skill in "$PWD"/skills/*; do
  target="$HOME/.agents/skills/${skill##*/}"
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    ln -s "$skill" "$target"
  fi
done
```

Repeat with `$HOME/.claude/skills` for Claude Code.

**Optional extras:**
- **`swarm` CLI (`delegate-swarm`):** link onto your `PATH` with:
  ```bash
  ln -sfn "$PWD/skills/delegate-swarm/scripts/swarm.py" "$HOME/.local/bin/swarm"
  ```
- **Shared global instructions (`config/CLAUDE.md`):** contains the comment-style rules used alongside `comment-style-tools`. Back up your existing global instructions before linking it to `~/.codex/AGENTS.md` or `~/.claude/CLAUDE.md`.

## Skills

### Engineering & Agent Workflows

| Skill | Description | Tools / Scripts |
|---|---|---|
| [`delegate-swarm`](skills/delegate-swarm/SKILL.md) | Orchestrate cheap/free coding agents (OpenCode by default) as single-task workers in parallel git worktrees, shipping one PR per task. | `scripts/swarm.py`, `templates/`, `capsules/` |
| [`designing-skills`](skills/designing-skills/SKILL.md) | Design new skills or audit existing ones against a smell catalog (dated prompting, leaked context, trivialities, agentic antipatterns). | `scripts/lint_skill.py` |
| [`precise-citations`](skills/precise-citations/SKILL.md) | Enforce source verification before citing file paths, line numbers, quoted code, config values, or CVEs in deliverables. | — |
| [`comment-style-tools`](skills/comment-style-tools/SKILL.md) | Enforce personal code comment rules mechanically on Python files while leaving docstrings untouched. | `scripts/clean_comments.py` |

### Knowledge & Memory Vault

| Skill | Description | Tools / Scripts |
|---|---|---|
| [`memory-vault`](skills/memory-vault/SKILL.md) | Operate a git-backed personal memory vault: catch up via master files, run jobs, triage inbox, and write timestamped daily notes. | — |
| [`memory-vault-setup`](skills/memory-vault-setup/SKILL.md) | Scaffold a memory vault and add projects, folders, assets, jobs, or job steps with their master files. | — |

### Study & Active Recall

| Skill | Description | Tools / Scripts |
|---|---|---|
| [`building-course-study-guides`](skills/building-course-study-guides/SKILL.md) | Build source-grounded offline HTML study guides from course slides, textbooks, and past exams; routes Anki decks to `active-recall-anki`. | `scripts/build_mathml.py`, `scripts/verify_build.py`, `scripts/dump_section.py`, `scripts/find_bad_formula.py` |
| [`active-recall-anki`](skills/active-recall-anki/SKILL.md) | Generate focused Basic and Cloze spaced-repetition flashcards as 3-column Anki TSV files. | `scripts/validate_deck.py` |

## Companion Skill Suites

General engineering, architecture, TDD, code review, refactoring, and UI workflows are intentionally not duplicated here — they are covered by these upstream suites via [`skills.sh`](https://skills.sh):

| Suite | Covers | Install |
|---|---|---|
| **Matt Pocock** (`mattpocock/skills`) | Engineering workflows, TDD, codebase design, domain modeling, code review, bug diagnosis, PRs | `npx skills add mattpocock/skills` |
| **pstack by poteto / Lauren Tan** (`cursor/plugins` → `pstack`) | Architecture, adversarial review, verification skills, refactoring principles, multi-agent playbooks | `npx skills add https://github.com/cursor/plugins/tree/main/pstack` |
| **CaldoAI** (`caldoai/skills`) | Whole-codebase untangling and test pruning | `npx skills add caldoai/skills` |
| **UIZZE** (`uizze/uizze`) | Real-screen-grounded UI design, anti-UI-slop, image-to-UI | `npx skills add uizze/uizze` |
| **Vercel Skills** (`vercel-labs/skills`) | Discovering and installing skills from `skills.sh` (`find-skills`) | `npx skills add vercel-labs/skills --skill find-skills` |
| **UI Polish** (`make-interfaces-feel-better`, `unslop-ui`) | Micro-interactions, visual details, and interface copy cleanup | `npx skills add jakubkrehel/make-interfaces-feel-better` · `npx skills add felipebasurto/unslop-ui` |

## Repository Structure

```text
.
├── config/          # Shared global agent instructions (CLAUDE.md)
├── scripts/         # Repository validator (validate_repo.py)
├── skills/          # Discoverable skills (skills/<name>/SKILL.md)
├── tests/           # Repository-level test suite
└── .githooks/       # Opt-in pre-commit hook
```

## Validation & Testing

Validate all skill frontmatter and local references:

```bash
python3 scripts/validate_repo.py --all
```

Run the skill-level unit tests:

```bash
python3 -m unittest discover -s skills/active-recall-anki/tests
python3 -m unittest discover -s skills/comment-style-tools/tests
python3 -m unittest discover -s skills/designing-skills/tests
```

Run the skill smell linter on any skill directory:

```bash
python3 skills/designing-skills/scripts/lint_skill.py skills/<skill-name>
```

Enable the opt-in pre-commit hook to validate staged skills and study artifacts automatically:

```bash
git config --local core.hooksPath .githooks
```
