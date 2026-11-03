---
name: comment-style-tools
description: Use when writing or cleaning up Manu's code comments, checking comment punctuation and bullet style, or enforcing the comment rules in the active agent instructions.
---

# Comment style tools

Follow the comment rules in the active instructions. Codex uses `~/.codex/AGENTS.md`; Claude Code uses `~/.claude/CLAUDE.md`. The shared source is `../../config/CLAUDE.md` relative to this skill directory. User and project instructions take precedence.

## Python comments

Resolve `scripts/clean_comments.py` relative to this skill directory. Check first:

```bash
python3 scripts/clean_comments.py path/to/file.py
```

Exit 1 means comments need changes. Apply them with `--write`, then inspect the diff. The script strips one final period, preserves ellipses and internal periods, and converts comment dash bullets into one-tab bullets. It parses Python before writing and changes only COMMENT tokens, preserving strings, encoding, and line endings. All input files are checked before any writes.

Docstrings are deliberately left untouched. Review them manually because they can contain doctests and meaningful string data. Use language-aware tools for other languages. Do not apply Python tokenization to JavaScript, shell, or mixed-language files.

## Review by hand

Check first-person singular, plain language, precise technical terms, one idea per line, no rhetorical labels or Markdown, and one space before inline comments. The helper checks punctuation and bullets only; it does not enforce those semantic rules.

## Validation

```bash
python3 -m unittest discover -s tests
```

Run from this skill directory. Tests cover literal strings, docstrings, inline comments, bullets, ellipses, CRLF, and incomplete Python.
