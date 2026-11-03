---
name: memory-vault
source: memory-vault skill, distilled for single-task workers
---
This repo is a Markdown knowledge vault. Every folder has a master file named like the folder (`02-kdp-books/02-kdp-books.md`) that is a numbered guide to what the folder holds.

## @structure
- Numbered folders and steps use two digits: `00-inbox/`, `01-daily-notes/`, `02-<project>/`, `01-define-audience/`.
- New folder names are kebab-case and each gets its own master file `<folder>/<folder>.md`.
- Put material in the folder whose master file's Conventions cover it; never dump it in `assets/` or `jobs/` by default.

## @master-files
- When you add, rename, move or delete a file or folder, update its parent's master file in the same change: a numbered step with a relative link, what to extract from it and what to do with it.
- Keep numbering two-digit and consecutive; every link must resolve.

## @assets
- Asset names: `<project>_<type>_<short-description>[_vNN].<ext>` (e.g. `kdp-books_cover_sudoku-vol1_v02.png`).
- Each asset gets a line in its project's `assets/assets.md` saying which job or folder uses it and how.

## @daily-note
- File `01-daily-notes/YYYY-MM-DD_HHmm.md`. Take the time ONLY from `TZ=America/Argentina/Buenos_Aires date "+%Y-%m-%d_%H%M"`; never invent or round it.
- Title `# YYYY-MM-DD HH:mm -03 — <summary>`, an `## Index` listing every `##` topic, and per topic: Project, What changed, How, Why, Next.
- Add the note at the top of the index in `01-daily-notes/01-daily-notes.md`.
