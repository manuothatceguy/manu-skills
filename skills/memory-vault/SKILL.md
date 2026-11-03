---
name: "memory-vault"
description: "Use whenever an agent works in Manu's memory vault: catching up on a project via master files, running jobs, keeping master files current, triaging the inbox, and writing daily notes."
---

# Memory Vault — Usage

The vault keeps every agent caught up across sessions. It works only if each agent (1) processes master files before acting, (2) keeps them accurate, (3) leaves daily notes, and (4) syncs every change with git. To create the vault or add projects, folders, assets, jobs or job steps, use the `memory-vault-setup` skill.

## 01. How the vault is organised

- Two-digit numbering: `00-inbox/`, `01-daily-notes/`, then projects from `02-<project>/` upward. Steps inside a job, and any other ordered folders, are `01-…`, `02-…`.
- A project usually has the standard folders `assets/` and `jobs/`, plus **any other folders it needs** (`research/`, `decisions/`, `code/` …), nested as deep as useful. Don't assume a project's layout — its master file tells you what's there.
- **`jobs/` holds one folder per recurring task** — e.g. `creating-campaigns/`, `drafting-emails/`, `facebook-ads/`. Each job's master file describes the whole process; each step of that process is a numbered subfolder (`facebook-ads/01-define-audience/`) with its own master file explaining how to do it.
- Every folder has a **master file** named like the folder (`02-kdp-books/02-kdp-books.md`, `jobs/facebook-ads/facebook-ads.md`). The vault root has one too (`<vault-name>/<vault-name>.md`) — that is the entry point.
- **A master file is a guide on how to read and process the folder.** Its numbered steps tell you which resource to open, what to extract from it, and what to do with it. Follow it in order; don't skim.
- The vault is a **git repository** on branch `main`, usually linked to a GitHub remote named `origin`.

## 02. Git sync rules

The repo is the source of truth shared by every agent and machine. Keep it in sync at all times.

**Pull before you read or change anything:**

```bash
git -C <vault> status --short          # must be clean before pulling
git -C <vault> pull --rebase origin main
```

Skip the pull only if `git remote` shows no `origin` yet. If the working tree has uncommitted changes you didn't make, don't discard them: commit them as `vault: commit pending changes found at session start` and mention them in the daily note.

**Commit after every change.** One logical change = one commit, made as soon as that change is complete — a new or edited file *together with* its master-file update, a new folder, a new job or step, a new project, an inbox triage, a daily note. Never batch a whole session into one commit, and never leave the tree dirty between tasks.

```bash
git -C <vault> add -A
git -C <vault> commit -m "<type>(<scope>): <what changed>"
git -C <vault> push origin main         # if origin exists
```

Commit message format:
- `<type>` is one of `add`, `update`, `move`, `remove`, `note`, `triage`, `vault` (structure or conventions).
- `<scope>` is the folder it touches, e.g. `02-kdp-books`, `02-kdp-books/jobs/facebook-ads`, `02-kdp-books/jobs/facebook-ads/02-write-copy`, `02-kdp-books/research`, `inbox`, `daily-notes`.
- Examples: `add(02-kdp-books/assets): sudoku vol1 cover v02` · `update(02-kdp-books/jobs/facebook-ads/02-write-copy): add hook templates` · `vault(02-kdp-books/jobs): add drafting-emails job` · `note(daily-notes): 2026-10-10_1430 ad budget decision` · `triage(inbox): 3 items to 02-kdp-books`.
- Add a body line with the *why* when it isn't obvious from the subject.

**Moving or renaming:** use `git mv` so history follows the file.

**Push failures:**
- Rejected because the remote moved ahead → `git pull --rebase origin main`, then push again.
- Rebase conflict → resolve it by keeping both sides' content (in master files and note indexes, merge the entries rather than picking one), `git add` the files, `git rebase --continue`, push. If the conflict is about real content where one side must win, stop and ask Manu.
- No network or auth error → keep committing locally and say in the daily note and in your reply that the push is pending.

**Never:** `git push --force`, `git reset --hard`, rewriting pushed history, deleting branches, or committing secrets (API keys, passwords, `.env`). Don't create the GitHub repo or change the remote — Manu manages that.

## 03. Starting a session — get caught up

01. Sync: pull as in section 02.
02. Open the root master file and follow its guide.
03. Open the master file of the project you will work on and execute its guide step by step. When a step points to a subfolder — standard or custom, at any depth — open that folder's master file and complete its guide before returning (depth-first).
04. For each step, actually do the processing it asks for — note the constraints, decisions, inputs and outputs it tells you to extract.
05. Read the newest daily notes for this project from the index in `01-daily-notes/01-daily-notes.md` — at least the last three, or all since the project's "Current status" was last updated. `git log --oneline -20 -- 02-<project>/` is a quick cross-check of what changed recently.
06. Check `00-inbox/` for items about this project.
07. If a master file is wrong — broken links, files or folders not covered by its guide, a folder with no master file, stale status — fix it and commit before starting the task.

You are caught up when you can explain the project's goal, its folders, assets, jobs and latest decisions without opening anything else. If you can't, a master file is missing something: improve it.

## 04. Running a job

When Manu asks for work that matches a job ("make a Facebook ad for vol. 2", "draft the launch emails"):

01. Find it in `jobs/jobs.md` and open the job's master file (`jobs/facebook-ads/facebook-ads.md`). Gather the inputs it lists.
02. Execute each step folder in order (`01-…`, `02-…`), following that step's master file and checking its verification criteria before moving on.
03. Save what the job produces where the job says (usually `assets/`, named per the convention) and link it.
04. If reality differs from what a step says — a tool changed, a better approach worked, a step was missing — update that step's master file (or add/renumber steps) so the next run is better. Commit each update.
05. If the work is a recurring task with no job yet, do it, then propose creating the job from what you just did (procedure in `memory-vault-setup`, Jobs).

## 05. While working

01. **Keep master files in sync, in the same commit.** Whenever you add, rename, move or delete a file or folder, update its parent's master file guide: add or edit the numbered step, its link, and what to extract and do with it.
02. **Put things where they belong.** Use the folder whose Conventions section covers the material. If nothing fits, create a new folder rather than forcing it into `assets/` or `jobs/`: kebab-case name, its own master file, and a step in the parent guide (procedure in `memory-vault-setup`, section 08). Check first that no existing folder already covers it.
03. **Assets** go in the project's `assets/` folder, named `<project>_<type>_<short-description>[_vNN].<ext>`, and get a line in `assets.md` saying which job or folder uses them and how. Files over ~50 MB: ask before committing (see `memory-vault-setup`, Assets).
04. **Breakthrough or breaking change?** Write a daily note right away (section 06), don't wait for the end of the session.
05. **After each change:** commit and push (section 02).

## 06. Daily notes

Write one:
- at the end of every session,
- at the end of the day,
- mid-session after a breakthrough or breaking change.

Each note must answer at least one of: *"I don't remember **when** / **how** / **why** something was done."*

### 06.1 Timestamps must be real — never invent them

The whole point of a daily note is to answer *when*, so a made-up time is worse than no note. **Never guess, estimate, round or reuse a date or time.** Don't take it from your own sense of "now", from the conversation, from an earlier note or from the last commit. Read it from the system clock at the moment you write the note:

```bash
TZ=America/Argentina/Buenos_Aires date "+%Y-%m-%d_%H%M"     # file name  → 2026-10-11_1432
TZ=America/Argentina/Buenos_Aires date "+%Y-%m-%d %H:%M %Z" # note title → 2026-10-11 14:32 -03
```

- **Timezone:** Manu's local time, `America/Argentina/Buenos_Aires`, unless the root master file's Conventions name another one. Always pass `TZ=` explicitly — cloud machines usually run in UTC, and a bare `date` would log the wrong hour or even the wrong day.
- On Windows PowerShell use `[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date), 'Argentina Standard Time').ToString('yyyy-MM-dd_HHmm')`. If a dedicated current-time tool is available, it is equally valid.
- Run the command fresh for every note. A session that spans hours gets each note's own real time.
- Times *inside* a note (when something happened earlier) must come from evidence — commit times via `git log --format="%h %ad %s" --date=iso-local` (with the same `TZ=`), file timestamps, or what Manu said. If you don't know when something happened, write "time unknown" instead of filling one in.
- If you can't read the clock at all (no shell, no time tool), say so to Manu and ask for the time. If no one is there to ask, name the file with the date from `git log -1` plus `_unknown-time` and state in the note that the time could not be verified.

### 06.2 File and template

File: `01-daily-notes/YYYY-MM-DD_HHmm.md`, using the clock output from 06.1. Several per day are fine.

```markdown
# YYYY-MM-DD HH:mm ±TZ — <one-line summary>

## Index
01. [<Topic A>](#topic-a)
02. [<Topic B>](#topic-b)

## Topic A
- **Project:** [02-project](../02-project/02-project.md)
- **Job / folder:** [facebook-ads](../02-project/jobs/facebook-ads/facebook-ads.md) (if any)
- **What changed:** …
- **How:** … (files touched, commands, links)
- **Why:** … (reasoning, alternatives rejected)
- **Commits:** `abc1234`, `def5678` (short hashes from `git log --oneline`)
- **Next:** … (open questions, follow-ups)

## Topic B
…
```

Then:
01. Make sure every `##` subtitle is an entry in the note's index.
02. Add the note at the top of the index in `01-daily-notes/01-daily-notes.md`.
03. Update the "Current status" of each affected master file and link the note there.
04. Commit as `note(daily-notes): <file name> <summary>` and push.

## 07. Triaging the inbox

For each item in `00-inbox/`:
01. Decide which project and which folder it belongs to (or ask the user if unclear). Any folder is a valid destination — an asset, a job's step, a custom folder; create a new one if nothing fits.
02. Move it there with `git mv`; rename it if it is an asset.
03. Add it to the destination master file's guide.
04. Remove it from `00-inbox/00-inbox.md`.
05. Commit as `triage(inbox): <item> to <project>/<folder>` and push.
06. Mention the triage in the session's daily note.

## 08. Before ending a session

- [ ] Every new, moved or renamed file is covered by its parent master file's guide, with a working link.
- [ ] Every new folder, at any depth, has its master file and a step in its parent's guide.
- [ ] Jobs you ran reflect what actually worked.
- [ ] Numbering is two-digit throughout.
- [ ] A daily note exists for this session, with a full index, and is listed in `01-daily-notes.md`.
- [ ] Every daily-note date and time came from the system clock (06.1), not from a guess.
- [ ] Affected master files show the current status.
- [ ] `git status` is clean and, if `origin` exists, `git log origin/main..main` is empty (everything pushed). If a push is pending, it's stated in the daily note.