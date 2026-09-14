#!/usr/bin/env python3
"""When build_mathml.py reports a formula-count MISMATCH, one formula used a
command pandoc's MathML writer does not support and got dropped. This tests each
formula individually and prints the culprit(s) — the ones that yield != 1 <math>.

Usage: python3 find_bad_formula.py <dir-with-fragments>   (edit ORDER to match)

Known offenders: mathtools extensible arrows \\xleftrightarrow{...},
\\xrightarrow{...}. Rewrite with primitives pandoc knows:
    labelled arrow      \\overset{a}{\\longleftrightarrow}
    birth-death chain   \\underset{\\mu_n}{\\overset{\\lambda}{\\rightleftharpoons}}
"""
import re, sys, html, subprocess, glob, os

target = sys.argv[1] if len(sys.argv) > 1 else "parts"
src = "\n".join(open(f).read() for f in sorted(glob.glob(os.path.join(target, "*.html"))))

tokens = []
def grab(m):
    tokens.append(("block" if m.group(0).startswith(r"\[") else "inline", m.group(1)))
    return "@@"
staged = re.sub(r"\\\[(.+?)\\\]", grab, src, flags=re.S)
staged = re.sub(r"\\\((.+?)\\\)", grab, staged, flags=re.S)

def nmath(md):
    p = subprocess.run(["pandoc", "--mathml", "-f", "markdown", "-t", "html"],
                       input=md, capture_output=True, text=True)
    return len(re.findall(r"<math\b.*?</math>", p.stdout, flags=re.S))

found = False
for i, (kind, tex) in enumerate(tokens):
    t = html.unescape(tex).strip()
    md = f"$${t}$$" if kind == "block" else f"${t}$"
    if nmath(md) != 1:
        found = True
        print(f"token {i} [{kind}] -> BAD:  {t[:110]!r}")
if not found:
    print("every formula converts to exactly one <math>. No offender found.")
