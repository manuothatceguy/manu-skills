# Code comment style (applies to every session)

When I ask you to write or rewrite code comments, follow these rules. I review pickily and reject anything that reads as AI-generated.

- First person singular ("I tried...", "I keep its token"). Narrate the process: what I tried first, why it failed, what worked.
- Plain, simple words and short sentences. Prefer the simpler word ("beautiful" over "gorgeous"). No filler ("really", "the whole point", "it is the X that...").
- Keep precise technical terms, do not dumb them down (rollback, max(current ids) + 1, JWT, chunked, etc.).
- No ALL-CAPS emphasis on words mid-sentence (write "not", not "NOT").
- No rhetorical AI scaffolding: no "X does not work / What works is Y" symmetry, no punchy one-line closers, no labels like "The goal:", "The catch:", "Bug 1:".
- Do not start a comment with a bare noun-phrase title (e.g. "the hidden request; ..."). Write a full sentence. Short pure label comments like "# progress counters" are fine.
- No semicolons joining clauses. No "label: explanation" colon patterns.
- No markdown, backticks forbidden.
- One idea per long line, let the editor word-wrap, do not hard-wrap mid-sentence.
- Lists: a lead-in line, then each item is one TAB after the `#`, arrows NOT aligned, no dash bullet. Inline comments start ONE space after the code, never align columns.
- No trailing period at the END of a comment, but keep periods BETWEEN sentences inside a comment.
- Do not over-comment, over-explaining every line is itself an AI tell.

The scripts I use to enforce this mechanically (trailing-period stripper, dash-bullet converter, review greps) live in the `comment-style-tools` skill.

# Memory vault

My memory vault lives at `/home/manu/manu-vault`. Start every vault session at `/home/manu/manu-vault/manu-vault.md` and follow the `memory-vault` skill (use `memory-vault-setup` to add projects, assets or job steps).
