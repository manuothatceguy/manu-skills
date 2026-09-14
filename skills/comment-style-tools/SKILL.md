---
name: comment-style-tools
description: Helper scripts for enforcing Manu's code comment style — strip trailing periods from comments and docstrings, convert dash bullets to tab bullets, and grep for style violations. Use when cleaning up comments in a file after writing or rewriting them, or when the user asks to enforce the comment style rules.
---

# Comment style helper scripts

The style rules themselves live in `~/.claude/CLAUDE.md` and are always loaded. This file holds the tooling to apply them mechanically.

## Strip the trailing period from every comment

Keeps periods between sentences, handles `#` comments and triple-quoted docstrings. Pass file paths as arguments:

```python
# usage: python3 strip_comment_period.py file1.py file2.py
import re, sys

def strip_period(text):
    s = text.rstrip()
    if s.endswith('.') and not s.endswith('..'):
        s = s[:-1]
    return s

for path in sys.argv[1:]:
    out, in_doc = [], False
    for line in open(path).read().split("\n"):
        stripped = line.strip()
        if stripped == '"""':
            in_doc = not in_doc; out.append(line); continue
        if in_doc:
            out.append(strip_period(line)); continue
        if stripped.startswith('"""') and stripped.endswith('"""') and stripped.count('"""') >= 2:
            m = re.match(r'^(.*)\.("""\s*)$', line)
            out.append(m.group(1) + '"""' if m else line); continue
        if '#' in line:
            i = line.index('#')
            out.append(line[:i] + strip_period(line[i:])); continue
        out.append(line)
    open(path, "w").write("\n".join(out))
```

## Convert dash bullets into one-tab bullets

Turns `# - item` into `#\titem`:

```bash
sed -i 's/^\( *\)# - /\1#\t/' FILE.py
```

## Review passes

Find style violations to fix by hand:

```bash
grep -nE '#[^"]*;' FILE.py          # semicolons inside comments
grep -nE "\bwe\b|\bus\b|\bour\b" FILE.py   # leftover "we/us/our" when the voice should be first person singular
```
