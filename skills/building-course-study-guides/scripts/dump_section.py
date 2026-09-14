#!/usr/bin/env python3
"""Vuelca una <section> de la guía como texto legible, con el MathML pasado a texto plano.
Sirve para leer la guía sin ahogarse en las 1500 fórmulas compiladas.

  python3 dump_section.py --file guia.html              -> lista los ids de sección
  python3 dump_section.py --file guia.html u4           -> vuelca esa sección
  python3 dump_section.py --file guia.html u4 --math    -> sólo las fórmulas
"""
import re, sys

GUIA = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "guia.html"
s = open(GUIA).read()
secs = re.findall(r'<section id="([^"]+)".*?</section>', s, re.S)
if not [a for a in sys.argv[1:] if not a.startswith("--") and a != GUIA]:
    for m in re.finditer(r'<section id="([^"]+)"', s):
        print(m.group(1))
    sys.exit()

sid = [a for a in sys.argv[1:] if not a.startswith("--") and a != GUIA][0]
m = re.search(r'<section id="%s".*?</section>' % re.escape(sid), s, re.S)
if not m:
    sys.exit("no existe la sección " + sid)
seg = m.group(0)

def mathtext(mm):
    # el MathML a texto plano: alcanza para juzgar notación, no para juzgar layout
    return " " + re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", mm.group(0))) + " "

if "--math" in sys.argv:
    for i, mm in enumerate(re.finditer(r"<math.*?</math>", seg, re.S), 1):
        print(f"{i}: {re.sub(r'<[^>]+>', '', mm.group(0))}")
    sys.exit()

seg = re.sub(r"<math.*?</math>", mathtext, seg, flags=re.S)
seg = re.sub(r"<(h2|h3|h4|tr|div|p|li)\b[^>]*>", "\n", seg)
seg = re.sub(r"</(td|th)>", " | ", seg)
seg = re.sub(r"<[^>]+>", "", seg)
seg = re.sub(r"\n{3,}", "\n\n", seg)
print(re.sub(r"[ \t]{2,}", " ", seg))
