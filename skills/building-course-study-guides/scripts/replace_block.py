#!/usr/bin/env python3
"""Replace the Nth <div class="ex">...</div> block in a fragment with new HTML.

When auditing exercises you often need to rewrite one whole exercise (a wrong
Cournot equilibrium, a votes-count that contradicts itself) without disturbing
its neighbours. Edit's exact-string matching is painful across a multi-line
block full of LaTeX backslashes; this targets by position instead.

    from replace_block import replace
    replace("parts/06a-ej.html", 3, '''<div class="ex">... new exercise 3 ...</div>''')

Assumes each exercise is one <div class="ex"> ... </details></div> block.
"""
import re

def replace(path, n, new, cls="ex"):
    s = open(path).read()
    blocks = list(re.finditer(rf'<div class="{cls}">.*?</details>\s*</div>', s, re.S))
    if len(blocks) < n:
        raise SystemExit(f"{path}: only {len(blocks)} '{cls}' blocks, asked for #{n}")
    b = blocks[n - 1]
    open(path, "w").write(s[:b.start()] + new.strip() + s[b.end():])
    print(f"ok  {path} block #{n} replaced")
