---
name: "memory-vault-declutter"
description: "Use when Manu asks to clean up, declutter, prune, tidy or slim down his memory vault, when the daily-notes index or Current status sections have grown long, or on a routine pass (about monthly) so the vault stays light for the agents that read it."
---

# Memory Vault — Declutter

Companion to `memory-vault` and `memory-vault-setup`. A catch-up reads every master file, the newest daily notes and the inbox. Each extra line costs every future session. This skill keeps the vault small by folding old material into short digests and fixing drift, while keeping everything that answers *when / how / why*.

Git is the safety net. Nothing is lost for good, so removal is fine once the useful content lives somewhere shorter. Follow the sync and commit rules of `memory-vault`, section 02.

## 01. Rules

- Propose first, act after Manu says yes. This matches the token priority in the root master file: cosmetic cleanups get a one-line proposal and wait for approval.
- Never touch the content of a project's code, assets or `decisions/`. This skill only folds notes and repairs structure.
- Never drop a decision, an open question or a reason. Move it to the folder that owns it before removing its source.
- One logical cleanup per commit.

## 02. The pass

01. Sync with git (`memory-vault`, section 02). The tree must be clean, otherwise stop.
02. Run the read-only audit and read its report. It changes nothing.
    ```bash
    python3 <skills>/memory-vault-declutter/scripts/audit_vault.py <vault> --days 30
    ```
03. Write the plan as one short list: each candidate, the action, and what survives. Show it to Manu and wait.
04. Apply the approved items by category (section 03), one commit each.
05. Write one daily note for the pass (`memory-vault`, section 06) saying what was folded and what was kept, with the commit hashes.
06. Re-run the audit. It should show only what Manu declined.

## 03. Categories

**Daily notes older than 30 days.** Fold them into one digest per month.
01. Read each old note. Keep in the digest: the decision and its why, the commit hashes, links to code or assets, and any Next item still open.
02. Drop from the digest: step-by-step narration, intermediate attempts, anything a later note or the project master file already says.
03. Write `01-daily-notes/archive/YYYY-MM.md`, grouped by project, one bullet per kept fact with its original date and time. Create `archive/` with its own master file if it does not exist, and list it in `01-daily-notes.md`.
04. Retarget every link that pointed at a folded note (master files list them in Current status) to the digest, using the audit's broken-link section afterwards to catch misses.
05. Remove the folded notes and their rows from the index in the same commit. Name the removed range in the commit body so `git log` finds them.
06. Always keep the three newest notes of every project, however old.

**Open Next items.** The audit lists them from the old notes. For each one, decide with Manu: done (drop), still open (carry into the owning project's master file under Current status or its roadmap), or abandoned (drop with a one-line reason in the digest).

**Current status sections.** Cut each to what is true now plus a link to the newest note. History belongs in the digest.

**Inbox.** Triage stale items (`memory-vault`, section 07). Ask about the ones with no clear owner. Do not delete unsorted items on your own.

**Structure drift.** Fix broken links, folders with no master file, files no master file mentions, and index rows without a file. These are repairs, so they need no separate approval beyond the plan.

**Assets.** For versioned sets (`_v01`, `_v02`) propose keeping the latest and the one a job or listing actually uses, then remove the rest through `git rm` and drop their lines from `assets.md`. Ask before touching anything over 50 MB.

**Empty folders.** Remove them together with the step in the parent master file that pointed at them.

## 04. Done when

- The audit shows no broken links, mismatches or unsorted inbox items, other than ones Manu declined.
- `git status` is clean and the push went through.
- Reading the root master file and the newest notes still lets an agent explain every project's goal, status and open questions.
