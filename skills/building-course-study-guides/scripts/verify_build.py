#!/usr/bin/env python3
"""La verificación que corro después de CADA edición de la guía ya construida.

  python3 verify_build.py guia.html

Son seis chequeos y los seis tienen que dar cero. Ninguno es caro, así que no
hay excusa para saltearlos: los seis juntos tardan menos de un segundo sobre un
archivo de 900 KB, y cada uno corresponde a un bug que se me escapó a producción
al menos una vez.

  1) LaTeX sin compilar en la prosa. Si quedó un \\frac o un \\[ suelto es que
     un delimitador no cerró y pandoc no llegó a ver esa fórmula.
  2) Subíndices y superíndices crudos (s''_i, u_j^{(l)}, y_{k+1}) y llaves de
     LaTeX ({,} para la coma decimal). Son costumbres de LaTeX escritas derecho
     adentro de una oración, donde nunca hubo delimitador que las envolviera.
  3) <mi>&</mi>, la marca de un \\begin{aligned} que no se convirtió en tabla.
  4) LaTeX crudo envuelto en tags <math> (escribiste <math>\\lambda</math> en vez
     de \\(\\lambda\\)). El chequeo 1 no lo ve porque borra <math>...</math> primero.
  5) Balance de tags. Cuento aperturas menos cierres por elemento.
  6) <div> adentro de <p>, que es HTML inválido y hace que el navegador cierre
     el párrafo antes de tiempo y te huerfane el texto que seguía.

Salida vacía quiere decir que está limpio.
"""
import re, sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "guia.html"
s = open(path).read()

# saco el MathML, el CSS, el JS y los bloques de código: lo que queda es prosa, y ahí no
# debería haber LaTeX. Los <pre> son código, no prosa: un nombre como simulate_simple_post
# tiene guiones bajos legítimos que el chequeo de subíndices confundiría con LaTeX
body = re.sub(r"<math.*?</math>", "§M§", s, flags=re.S)
body = re.sub(r"<style.*?</style>|<script.*?</script>|<pre.*?</pre>", "", body, flags=re.S)
body = re.sub(r"<[^>]+>", " ", body)

fallas = 0
CRUDO = {
    "comando LaTeX":      r"\\[a-zA-Z]{2,}",
    "delimitador suelto": r"\\\(|\\\)|\\\[|\\\]",
    "subíndice crudo":    r"[A-Za-z]'*_[A-Za-z0-9{(]",
    "superíndice crudo":  r"[A-Za-z0-9}]\^[A-Za-z0-9{(]",
    "llaves LaTeX":       r"\{[,.]\}",
    "token sin sustituir": r"@@MATH",
}
for nombre, pat in CRUDO.items():
    for m in re.finditer(pat, body):
        ctx = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body[max(0, m.start()-50):m.end()+25]))
        print(f"[{nombre}] {m.group(0)!r}  …{ctx}…")
        fallas += 1

for m in re.finditer(r"<mi>&(amp;)?</mi>", s):
    print("[aligned roto] un <mi>&</mi> literal: esa fórmula no se convirtió en <mtable>")
    fallas += 1

# Un <math> con una barra invertida adentro es LaTeX crudo envuelto en tags <math>, no MathML.
# El chequeo de arriba no lo agarra porque lo primero que hago es borrar <math>...</math> entero,
# dando por hecho que ahí adentro ya hay MathML. Pasa cuando escribís <math>\lambda_i</math> en
# vez de \(\lambda_i\): compilar() no encuentra ningún token \[ \] / \( \), devuelve la fuente sin
# tocar, y el LaTeX viaja hasta el archivo final sin que nadie se queje. El MathML real nunca lleva
# una barra invertida, así que basta con buscarla adentro de cada <math>
for m in re.finditer(r"<math\b[^>]*>(.*?)</math>", s, flags=re.S):
    if "\\" in m.group(1):
        cuerpo = re.sub(r"\s+", " ", m.group(1))[:60]
        print(f"[math sin compilar] un <math> con LaTeX crudo adentro: …{cuerpo}… (escribiste <math> en vez de \\( \\))")
        fallas += 1

# Sólo cuento los elementos cuyo cierre es obligatorio. En HTML5, li/td/th/tr
# pueden omitir el </>, el navegador los cierra solo, así que un desbalance ahí
# no es un bug y sólo genera ruido
c = Counter()
for m in re.finditer(r"</?(div|p|section|details|table|span|math|summary|pre|ul|ol)\b[^>]*?(/?)>", s):
    t = m.group(1)
    c[t] += -1 if m.group(0).startswith("</") else (0 if m.group(2) else 1)
for t, v in c.items():
    if v:
        print(f"[tags] <{t}> desbalanceado: {v:+d}")
        fallas += 1

# el (?:(?!</p>).)*? encierra el match en UN párrafo. Con un .*? pelado el motor
# estira el match a través de párrafos enteros y reporta cualquier cosa
for m in re.finditer(r"<p>(?:(?!</p>).)*?<div", s, re.S):
    print("[html inválido] un <div> adentro de un <p>")
    fallas += 1

sys.exit(1 if fallas else 0)
