---
name: "memory-vault-setup"
description: "Use to create or extend Manu's memory vault: scaffold the folder structure, add a project, any folder inside it, assets, jobs or job steps, and write their master files."
---

# Memory Vault — Setup

This skill builds the vault and adds new pieces to it. For working inside an existing vault (catching up, logging sessions, syncing with git), use the `memory-vault` skill.

## 01. Core rules the structure must satisfy

1. **Two-digit numbering everywhere:** `00`, `01`, `02` … `99`. Applies to top-level folders, job steps, any other ordered sequence of folders, and entries in master files.
2. **Every folder has a master file** named exactly like the folder, plus `.md` (e.g. `02-kdp-books/02-kdp-books.md`, `jobs/facebook-ads/facebook-ads.md`).
3. **A master file is a guide on how to read and process the folder's resources.** It is a numbered procedure, not an inventory. Each step names a resource, links to it, and says what to get out of it and what to do with it.
4. **Projects can contain any folders they need.** `assets/` and `jobs/` are the two standard folders, but a project can add others (`research/`, `decisions/`, `code/`, `clients/` …) and nest folders inside them. Every one of them follows rules 2 and 3.
5. Folder and file names are lowercase kebab-case.
6. **The vault is a git repository.** Every change is committed and, when a remote exists, pushed (rules in the `memory-vault` skill, section 02). Manu creates the GitHub repository and links the remote himself — never create one or add a remote unless he asks.

## 02. Target layout

```
<vault-name>/
├── .git/
├── .gitignore
├── .gitattributes
├── <vault-name>.md                 ← root master file (entry point for every agent)
├── 00-inbox/
│   └── 00-inbox.md
├── 01-daily-notes/
│   └── 01-daily-notes.md
├── 02-<project>/
│   ├── 02-<project>.md
│   ├── assets/                     ← standard
│   │   └── assets.md
│   ├── jobs/                       ← standard: one folder per recurring task
│   │   ├── jobs.md
│   │   ├── creating-campaigns/
│   │   │   ├── creating-campaigns.md
│   │   │   ├── 01-define-audience/
│   │   │   │   └── 01-define-audience.md
│   │   │   └── 02-write-brief/
│   │   │       └── 02-write-brief.md
│   │   ├── drafting-emails/
│   │   │   └── …
│   │   └── facebook-ads/
│   │       └── …
│   └── <any-folder>/               ← custom, as many as the project needs
│       ├── <any-folder>.md
│       └── <nested-folder>/
│           └── <nested-folder>.md
└── 03-<project>/ …
```

- `00` is always the Inbox, `01` is always Daily notes, projects take `02` upward in creation order.
- Folders inside a project, including each job, are unnumbered; the parent master file's guide sets the reading order. Number sibling folders (`01-`, `02-` …) only when they form a sequence — above all, the steps inside a job.

## 03. Master file template

Use this for every master file. Adapt the wording to the folder, but keep the numbered guide.

```markdown
# <Folder name>

## Purpose
What this folder is for and how it fits into its parent.

## Current status
Where things stand now. Link the latest relevant daily note.

## How to read and process this folder
01. **Read [<resource>](./<resource>.md).** Extract: <what to learn from it>. Then: <what to do with it — e.g. keep in mind as constraints, use as input for step 03, check it against X>.
02. **Go through [<subfolder>/](./<subfolder>/<subfolder>.md)** and follow its own guide. Come back with: <what you should know after it>.
03. …

## Outcome
What an agent should know or be able to do after completing the guide.

## Conventions
Rules specific to this folder (naming, formats, what goes where).
```

Every file and subfolder in the folder must appear in the guide with a direct relative link; subfolders link to their own master file. Order the steps the way a newcomer should process them.

The root master file also gets a `## Git` section stating: the vault is a git repo, the default branch is `main`, every change is committed with the message format from the `memory-vault` skill, and whether a remote is linked yet.

## 04. Creating a new vault

01. Ask for the vault name and location if not given. Default: `<name>-vault/` in the current working folder.
02. Create the root folder and its root master file. Its guide should be: 01 read this file's conventions, 02 sync with git (`memory-vault` section 02), 03 check `00-inbox`, 04 read the latest notes in `01-daily-notes`, 05 pick the project and follow its master file. List every project with a one-line description and link.
03. Create `00-inbox/00-inbox.md`: purpose (landing zone for unsorted material), and a guide for triaging each item into a project.
04. Create `01-daily-notes/01-daily-notes.md`: purpose, the daily-note naming and template (see the `memory-vault` skill), and an index of notes, newest first (empty at start).
05. For each project the user names, follow section 05.
06. If the user has existing material, put it in `00-inbox/` or straight into the matching project — in `assets/`, the right job, or whatever folder fits it (section 08) — and wire it into the master files.
07. Tell agents the vault exists: add a short line to the user's agent instructions (e.g. `CLAUDE.md`, project instructions) pointing to the root master file and the `memory-vault` skill.
08. Initialise git (section 09).
09. Write the first daily note in `01-daily-notes/` recording the vault's creation, add it to the index, and commit.
10. Run the checklist in section 10.

Quick scaffold (adapt names):

```bash
V=manu-vault
mkdir -p "$V/00-inbox" "$V/01-daily-notes"
touch "$V/$V.md" "$V/00-inbox/00-inbox.md" "$V/01-daily-notes/01-daily-notes.md"
```

Never leave a master file empty — fill each from the template before finishing.

## 05. Adding a project

01. Find the highest existing number and take the next one, e.g. `04`.
02. Create `04-<project>/` with `04-<project>.md`, plus `assets/assets.md` and `jobs/jobs.md` (skip either if Manu says the project won't need it).
03. Ask which recurring tasks the business runs (e.g. creating campaigns, drafting emails, Facebook ads) and add each as a job (section 07).
04. Ask what else the project involves and add a folder for each distinct area (section 08) — e.g. `research/`, `decisions/`, `code/`. Don't invent folders or jobs the project has no material for yet.
05. Fill the project master file: purpose, status, and a guide that walks through the project's resources and every folder in the order a newcomer should process them.
06. Add the project to the root master file.
07. Log it in a daily note.
08. Commit and push: `vault(04-<project>): create project`.

## 06. Assets (standard folder)

`assets/` holds the files the project uses or produces (images, documents, data, exports). Name files so they are findable without broad searches:
`<project>_<type>_<short-description>[_vNN].<ext>` — e.g. `kdp_cover_sudoku-vol1_v02.png`.

`assets.md` is a guide, not just a list: group assets by what they are used for and say, for each group, which job or folder consumes them and how. If a group grows large, give it its own subfolder (e.g. `assets/covers/`) with its own master file.

Large binaries (videos, big PSDs, datasets over ~50 MB) bloat the repo and GitHub rejects files over 100 MB. For those, ask Manu whether to use Git LFS (`git lfs track "*.psd"`, commit `.gitattributes`) or keep the file outside the vault and link to it from `assets.md`.

## 07. Jobs (standard folder)

`jobs/` holds the recurring tasks the business performs. **Each job is one kind of task** that gets done repeatedly — e.g. `creating-campaigns/`, `drafting-emails/`, `facebook-ads/`, `publishing-a-book/`, `customer-support/`. A job is not a single to-do item; it's the reusable know-how for doing that kind of work.

01. **`jobs/jobs.md`** is the guide to all jobs: for each one, a numbered entry with a link, a one-line description of what it produces, and when to run it. Note how jobs relate (e.g. `facebook-ads` uses the brief produced by `creating-campaigns`).
02. **One folder per job**, named after the task in kebab-case (`jobs/facebook-ads/`), unnumbered. Its master file (`facebook-ads.md`) describes the entire process to get that job done: goal and outcome, inputs (with links to assets or other jobs), tools and accounts involved, and the numbered list of steps with links to each step's folder.
03. **One folder per step** inside the job, numbered in execution order: `jobs/facebook-ads/01-define-audience/`, `02-write-copy/`, `03-create-creatives/`, `04-launch-and-monitor/`. Each step's master file (`01-define-audience.md`) explains how to achieve that specific task: inputs, tools, the procedure as numbered actions, outputs, and how to verify it succeeded. A step may hold its own files (templates, prompts, checklists, scripts); its master file guides through them.
04. **Adding a job:** create the folder and master file, at least the steps known so far, and add it to `jobs.md`. Commit as `vault(<project>/jobs): add <job> job`.
05. **Adding a step in the middle:** renumber the following step folders with `git mv` (so history follows the files), rename their master files, then fix every link to them. Commit the renumbering as one change.

## 08. Adding any other folder

Use this whenever material isn't an asset and isn't a job — at project level or nested inside any folder.

01. Pick a short kebab-case name that says what's inside (`research`, `decisions`, `meeting-notes`, `code`, `legal`). Number it only if it belongs to an ordered sequence of siblings.
02. Before creating it, check that no existing folder already covers the same thing; if one does, use it instead.
03. Create the folder and its master file `<folder>/<folder>.md` from the template in section 03. Its Conventions section states what belongs there and how files in it are named.
04. Add a numbered step for it to the parent master file's guide, in the place a newcomer should reach it, saying what to extract from it and how it relates to the other folders.
05. Commit and push: `vault(<path>): add <folder> folder`.

## 09. Git setup

01. If the folder is not a repo yet, from the vault root:

```bash
git init -b main
```

02. Create `.gitignore`:

```gitignore
# OS / editor
.DS_Store
Thumbs.db
*.swp
.obsidian/workspace*
.vscode/
.idea/
# secrets — never commit
.env
*.key
*.pem
```

03. Create `.gitattributes` so line endings don't create noise between machines:

```gitattributes
* text=auto eol=lf
*.png binary
*.jpg binary
*.pdf binary
```

04. Check that `git config user.name` and `user.email` are set; if not, ask Manu what to use rather than inventing values.
05. Make the first commit: `git add -A && git commit -m "vault: initial structure"`.
06. Don't create the GitHub repo or add a remote — Manu does that. Tell him the commands he'll need once the repo exists:

```bash
git remote add origin git@github.com:<user>/<vault-name>.git
git push -u origin main
```

07. Record in the root master file's `## Git` section that the remote is pending. When a later agent sees `origin` exists, it updates that line.

## 10. Checklist before finishing

- [ ] All numbering is two-digit.
- [ ] Every folder — root, standard or custom, at any depth — has a master file named after it.
- [ ] Every master file has a numbered read-and-process guide linking every file and subfolder in it.
- [ ] Root master file lists all projects and has its `## Git` section.
- [ ] Every job has its own folder with a process master file and numbered step folders, and is listed in `jobs.md`.
- [ ] Asset names follow the convention and are covered in `assets.md`.
- [ ] A daily note records what was set up and is indexed in `01-daily-notes.md`.
- [ ] `git status` is clean; if a remote exists, `main` is pushed.