#!/usr/bin/env python3
"""Assemble HTML fragments and compile their LaTeX to MathML with pandoc.

This is the controller's build step. Constructors write fragments with math as
LaTeX (\\[ ... \\] display, \\( ... \\) inline); this concatenates them in ORDER
and turns every formula into native MathML that renders with no JS and no CDN
(the Artifact CSP blocks both).

Why pandoc and not latex2mathml: latex2mathml silently breaks \\begin{aligned}
(literal & , no row stacking), so multi-line derivations overflow on one line.
pandoc emits a real <mtable>. See SKILL.md "Math" section.

Edit PARTS, OUT, ORDER for your guide, then: python3 build_mathml.py
It self-verifies and exits non-zero on any problem.
"""
import re, sys, html, subprocess

PARTS = "CHANGE_ME/parts"
OUT   = "CHANGE_ME/guia.html"
ORDER = ["00-header", "02-unit", "..."]   # fragment basenames, in document order

src = "\n".join(open(f"{PARTS}/{p}.html").read() for p in ORDER)

# Pull every math token out in document order, leaving a placeholder.
tokens = []
def grab(m):
    tokens.append(("block" if m.group(0).startswith(r"\[") else "inline", m.group(1)))
    return f"@@MATH{len(tokens)-1}@@"
staged = re.sub(r"\\\[(.+?)\\\]", grab, src, flags=re.S)     # \[ \] first (may contain parens)
staged = re.sub(r"\\\((.+?)\\\)", grab, staged, flags=re.S)

# One pandoc call for ALL formulas (spawning per-formula is far too slow at ~1500).
# .strip() the token: pandoc does NOT treat "$ x $" (a space right after the opening $)
# as inline math, so an inline \( x \) a constructor wrote with spaces silently drops and
# the stray $ then mis-pairs with a later one, cascading and losing ~half the formulas.
md = "\n\n<!--SEP-->\n\n".join(
    (f"$${html.unescape(t).strip()}$$" if k == "block" else f"${html.unescape(t).strip()}$") for k, t in tokens)
proc = subprocess.run(["pandoc", "--mathml", "-f", "markdown", "-t", "html"],
                      input=md, capture_output=True, text=True)
if proc.returncode != 0:
    sys.exit("pandoc failed:\n" + proc.stderr)

maths = re.findall(r"<math\b.*?</math>", proc.stdout, flags=re.S)
if len(maths) != len(tokens):
    # A dropped formula = an unsupported command (e.g. \xleftrightarrow / mathtools arrows).
    # Find it with find_bad_formula.py, then rewrite with \overset/\underset/\rightleftharpoons.
    sys.exit(f"MISMATCH: {len(tokens)} formulas in, {len(maths)} out. Run find_bad_formula.py.")

def clean(mathml, kind):
    mathml = re.sub(r"<annotation\b.*?</annotation>", "", mathml, flags=re.S)  # drop the x-tex source
    mathml = mathml.replace("<semantics>", "").replace("</semantics>", "")
    if kind == "block" and 'display="block"' not in mathml:
        mathml = mathml.replace("<math ", '<math display="block" ', 1)
    return mathml

out = staged
for i, ((kind, _), mathml) in enumerate(zip(tokens, maths)):
    out = out.replace(f"@@MATH{i}@@", clean(mathml, kind), 1)
open(OUT, "w").write(out)

# --- self-verification: these caught every real bug in practice ---
problems = []
if "@@MATH" in out:
    problems.append("unsubstituted @@MATH placeholders")
if re.search(r"\\\[|\\\(|\\frac|\\begin\{|\\lambda|\\cdot", out):
    problems.append("raw LaTeX left outside <math> (missing delimiter?)")
if re.search(r"<mi>&(?:amp;)?</mi>", out):
    problems.append("literal <mi>&</mi>: an aligned block did not become an <mtable>")
aligned_in = sum(1 for _, t in tokens if r"\begin{aligned}" in t or r"\\" in t)
if aligned_in > out.count("<mtable"):
    problems.append(f"{aligned_in} multi-line formulas but only {out.count('<mtable')} <mtable>")
for tag in ["div", "table", "details", "summary", "tr", "td", "th", "section", "math", "p"]:
    o = len(re.findall(f"<{tag}[ >]", out)); c = out.count(f"</{tag}>")
    # note: one <div> stays open on purpose if your shell .wrap spans header->footer
    if o != c and not (tag == "div" and o - c == 1):
        problems.append(f"tag imbalance <{tag}>: {o} open / {c} close")

block = sum(1 for k, _ in tokens if k == "block")
print(f"wrote {OUT}  ({len(out)} bytes)  MathML: {block} display, {len(tokens)-block} inline, {out.count('<mtable')} mtable")
if problems:
    print("\n!! PROBLEMS:")
    for p in problems: print("  -", p)
    sys.exit(1)
print("all formulas compiled, structure balanced.")
