#!/usr/bin/env python3
"""Controller-side audits. Constructors' self-audits are worthless (they all
reported "no errors" while shipping wrong math). Run these against the FRAGMENTS
before building, and against the built HTML after.

Usage: python3 audit_math.py <dir-with-html-fragments-or-the-built-file>

It prints, for each fragment:
  1) plain-text math Unicode that escaped LaTeX-ification (subscripts/exponents
     vanish here: 'd t^2' -> 'dt2'), the #1 place leftover math hides is inside
     <details> checkpoints and <th>/<td> cells the conversion pass skipped;
  2) <div class="formula"> boxes that contain PROSE (constructors dump an
     explanation + equation in one box; split them: equation in .formula, prose
     in <p>);
  3) every display formula on one compact line, so you can re-derive the worked
     examples by hand (that is the only audit that finds a wrong sign or a
     dropped term).
"""
import re, sys, glob, os, html

target = sys.argv[1] if len(sys.argv) > 1 else "."
files = sorted(glob.glob(os.path.join(target, "*.html"))) if os.path.isdir(target) else [target]

UNI = re.compile(r"[λμρσαβγδΔπθεωΩ∇∂∫Σ√≤≥≠≈²³⁴ᵏⁿ₀₁₂₃ᵢⱼ]")

def strip_math(s):
    # remove already-rendered <math> and LaTeX-delimited spans
    s = re.sub(r"<math\b.*?</math>", "", s, flags=re.S)
    s = re.sub(r"\\\[.*?\\\]|\\\(.*?\\\)", "", s, flags=re.S)
    return s

for f in files:
    s = open(f).read()
    name = os.path.basename(f)

    # 1) plain-text math outside any math span (ignore benign prose · ± → and the brand)
    stripped = strip_math(s)
    for m in UNI.finditer(stripped):
        ctx = re.sub(r"<[^>]+>", "", stripped[max(0, m.start()-45):m.start()+18]).replace("\n", " ")
        print(f"[unicode] {name}: {m.group(0)!r}  …{ctx}…")

    # 2) prose stuck inside formula boxes
    for m in re.finditer(r'<div class="formula">(.*?)</div>', s, re.S):
        # el <span class="fcap"> es el título de la caja y sí va acá, no lo cuento como prosa
        body = re.sub(r'<span class="fcap">.*?</span>', "", m.group(1), flags=re.S)
        rest = re.sub(r"<[^>]+>", "", re.sub(r"<math\b.*?</math>|\\\[.*?\\\]|\\\(.*?\\\)", "", body, flags=re.S))
        rest = html.unescape(rest).strip()
        if len(rest) > 25:
            print(f"[prose-in-formula] {name}: …{rest[:90]}…")

    # 2b) restos de LaTeX en prosa, donde nunca hubo delimitador que los envolviera.
    # El que se me escapó a producción fue 0{,}25, el truco de la coma decimal en modo
    # matemático escrito derecho adentro de una oración, que muestra las llaves literales
    for label, pat in (("llaves",   r"\{[,.]\}"),
                       ("subínd",   r"[A-Za-z]'*_[A-Za-z0-9{(]"),
                       ("superínd", r"[A-Za-z0-9}]\^[A-Za-z0-9{(]"),
                       ("comando",  r"\\[a-zA-Z]{2,}")):
        clean = re.sub(r"<style\b.*?</style>|<script\b.*?</script>", "", stripped, flags=re.S)
        for m in re.finditer(pat, clean):
            ctx = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", clean[max(0, m.start()-50):m.end()+25]))
            print(f"[latex-en-prosa/{label}] {name}: {m.group(0)!r}  …{ctx}…")

    # 2c) un \text{...} de título adentro de un aligned cae en la columna 1, que es
    # angosta porque la dimensiona un s'_A, y el texto se corta a la mitad. Va como
    # caption HTML arriba del <math>, no como fila del mtable
    for m in re.finditer(r'<mtr><mtd columnalign="right"[^>]*><mtext[^>]*>([^<]*)</mtext></mtd></mtr>', s):
        print(f"[titulo-en-mtable] {name}: {m.group(1)!r} -> sacalo a un <span class=\"fcap\">")

    # 2d) derivación encadenada con flechas en un solo renglón. El display math no corta línea,
    # así que esa línea fija el ancho de la caja y le cuelga una barra horizontal abajo.
    # Va como aligned, un paso por fila, repitiendo el lado izquierdo en vez de encadenar
    for m in re.finditer(r'<math display="block".*?</math>', s, re.S):
        blk = m.group(0)
        if "<mtable" in blk:
            continue
        t = re.sub(r"<[^>]+>", "", blk)
        # el acento de \vec{x} se aplana a "x→", así que una flecha pegada a una letra
        # es un vector y no un paso de la derivación
        pasos = len(re.findall(r"(?<![A-Za-z])→", t)) + t.count("⟹") + t.count("⇒")
        igs = t.count("=")
        # el largo del texto pelado es el filtro que importa: una cadena corta como q=1-q => q=1/2
        # entra igual en el renglón, la que desborda es la de ~50 caracteres para arriba
        if len(t) > 45 and ((pasos >= 1 and igs >= 2) or igs >= 4 or t.count(";") >= 3):
            print(f"[cadena-larga] {name}: flechas={pasos} '='={igs}  {t[:100]}")

    # 2e) punto huérfano: el <p> termina con la fórmula y le queda el punto de la oración
    # después del </math>, que cae solo en un renglón abajo de la caja
    # el (?:(?!</math>).)*? es obligatorio. Con un .*? pelado, cuando el primer </math> no viene
    # seguido de puntuación el motor estira el match hasta el siguiente y reporta falsos positivos
    # de cientos de miles de caracteres, saltándose de paso las fórmulas del medio
    for m in re.finditer(r'<math display="block"(?:(?!</math>).)*?</math>\s*([.,;])\s*</p>', s, re.S):
        print(f"[puntuacion-huerfana] {name}: {m.group(1)!r} suelto después de un display block")

    # 3) dump display formulas for hand-checking
    for i, tex in enumerate(re.findall(r"\\\[(.+?)\\\]", s, re.S), 1):
        print(f"[formula] {name} #{i}: {' '.join(tex.split())[:200]}")
