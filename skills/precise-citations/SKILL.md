---
name: precise-citations
description: Use whenever a deliverable (report, PR, commit message, answer, security writeup) cites a file path, line number, function name, config value, CVE, or quotes code/library behavior. Enforces that every citation is verified against the actual source right before writing it — never fabricated, never approximate.
---

# Precise citations

A citation that is wrong is worse than no citation: it destroys trust in the whole
document and the reader cannot tell which other claims are also invented. This skill
is a hard rule, not a preference.

## The rule

Before writing any `file:line`, function name, quoted code, config value, CVE id, or
"the code does X" claim into a deliverable, I must have looked at the actual source
in this session and confirmed it says exactly that. If I have not just verified it,
I do not write it as a fact.

## What counts as a citation that must be verified

- A file path or `path:line` reference.
- A line number (these shift after edits — re-verify after any edit to the file).
- A quoted snippet of code, a docstring, an error message, a regex.
- A function/class/variable name presented as existing in the code.
- A config/setting default value, a constant, a version pin (read it from the lockfile/source, not memory).
- A CVE number or "fixed in version X" claim.
- "The library does Y" when the library source is not in front of me.

## Procedure (do this every time)

1. Open the file and read the exact lines, in this session, immediately before writing the citation.
2. Quote verbatim. Do not paraphrase inside quotation marks. Copy the bytes.
3. Pin line numbers only after reading them; re-check them if the file was edited since.
4. If I cannot open the source (e.g. a pip dependency whose code is not on the machine),
   I do NOT assert its internals. I downgrade the claim to what I can verify (the version
   pin from the lockfile) and say explicitly that I did not read the code.
5. Separate verified from inferred. Verified = "I read it". Inferred = "I expect, did not confirm".
   Label the second kind plainly; never let it look like the first.

## Red flags that mean STOP and verify

- "It's probably around line N" → open the file.
- "The X helper blocks/validates Y" without having read X → read X (this is exactly how the
  `outgoing_http.py` "blocks internal addresses" error happened: it only routes to a proxy).
- Quoting a docstring or message from memory → re-open and copy it.
- Citing a CVE or "maintained version hardened this" without the changelog/source → say it is
  from memory and unverified, or go verify.
- Reusing a line number from earlier in the conversation after the file changed → re-grep.

## Cheap verification commands

- `grep -n "exact_string" path` to pin a line number.
- Read the specific line range, not the whole file, then copy the text.
- For versions: read `uv.lock` / `package.json` / lockfile, not memory.
- After editing a `.tex`/`.md` that contains `path:line` citations, re-grep those lines to confirm they still point where the prose says.
