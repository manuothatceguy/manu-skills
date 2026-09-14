#!/usr/bin/env python3
"""Compilar LaTeX a MathML y meterlo en una guía YA CONSTRUIDA.

Esto es para el después: cuando los fragmentos de parts/ ya no existen y hay que
corregir una fórmula, agregar una sección, o reemplazar una derivación adentro
del HTML final. Impórtalo:

    from patch_math import compilar, insertar_antes, reemplazar_bloque

    html = compilar(open("seccion_nueva.html").read())   # LaTeX \\[ \\] y \\( \\) adentro
    insertar_antes("guia.html", "<h4>Autómatas celulares", html)

Dos trampas que ya me costaron caro y que están resueltas acá adentro:

1) pandoc con -f markdown a secas NO reconoce \\( \\) como matemática. Devuelve
   exit code 0 y un párrafo de texto plano, con las comillas tipográficas
   aplicadas encima, así que \\(s''_i\\) sale como (s''_i) y parece un bug de
   renderizado en vez de un fallo de compilación. Por eso acá cada fórmula se
   reenvuelve como $...$ / $$...$$, que sí es markdown estándar. La alternativa
   es -f markdown+tex_math_single_backslash.

2) Hay que hacer .strip() de cada token antes de envolverlo. Los constructores
   escriben \\( x \\) con espacios, y $ x $ no es matemática inline para pandoc
   (la regla es que no puede haber espacio después del $ de apertura). El $
   huérfano después se aparea con el de otra fórmula y se cae la mitad del
   documento en cascada. El assert de conteo lo agarra.

Y una diferencia de estilo: por este camino pandoc envuelve todo en <semantics>
con el LaTeX original en <annotation>. El build principal los saca, así que acá
también, para que la fórmula parchada sea idéntica al resto del archivo.
"""
import re, html, subprocess


def compilar(fuente):
    """Toma HTML con LaTeX en \\[ \\] y \\( \\), devuelve el mismo HTML con MathML."""
    tokens = []

    def agarrar(m):
        tokens.append(("block" if m.group(0).startswith("\\[") else "inline", m.group(1)))
        return f"@@MATH{len(tokens)-1}@@"

    # \\[ \\] primero: un bloque puede contener paréntesis adentro
    puesto = re.sub(r"\\\[(.+?)\\\]", agarrar, fuente, flags=re.S)
    puesto = re.sub(r"\\\((.+?)\\\)", agarrar, puesto, flags=re.S)
    if not tokens:
        return puesto

    md = "\n\n<!--SEP-->\n\n".join(
        (f"$${html.unescape(t).strip()}$$" if k == "block" else f"${html.unescape(t).strip()}$")
        for k, t in tokens)
    o = subprocess.run(["pandoc", "--mathml", "-f", "markdown", "-t", "html"],
                       input=md, capture_output=True, text=True)
    assert o.returncode == 0, o.stderr
    maths = re.findall(r"<math\b.*?</math>", o.stdout, flags=re.S)
    # un faltante = un comando que pandoc no soporta (los \\x... de mathtools, por ejemplo).
    # Para encontrar cuál, compilá los tokens de a uno hasta que uno devuelva cero <math>
    assert len(maths) == len(tokens), f"entraron {len(tokens)}, salieron {len(maths)}"

    for n, mm in enumerate(maths):
        mm = re.sub(r'<annotation encoding="application/x-tex">.*?</annotation>', "", mm, flags=re.S)
        mm = mm.replace("<semantics>", "").replace("</semantics>", "")
        # sin el > de cierre: los operadores nombrados salen como <mi mathvariant="normal">min</mi>,
        # y buscar "<mi>" exacto daba un falso "compiló vacía" en cualquier fórmula con \min o \max
        assert re.search(r"<(mi|mo|mn|mtext)\b", mm), f"fórmula {n} compiló vacía"
        esperado = 'display="block"' if tokens[n][0] == "block" else 'display="inline"'
        assert esperado in mm, f"fórmula {n} salió con el display equivocado"
        puesto = puesto.replace(f"@@MATH{n}@@", mm)

    assert "@@MATH" not in puesto
    assert "<mi>&</mi>" not in puesto and "<mi>&amp;</mi>" not in puesto
    return puesto


def insertar_antes(archivo, ancla, html_nuevo):
    s = open(archivo).read()
    i = s.find(ancla)
    assert i != -1, f"no encontré el ancla: {ancla!r}"
    open(archivo, "w").write(s[:i] + html_nuevo + "\n" + s[i:])


def reemplazar_bloque(archivo, firma, latex_nuevo):
    """Reemplaza el <math display="block"> cuyo texto pelado empieza con `firma`.

    La firma se compara contra el MathML sin tags, que es como se ve la fórmula
    leída de corrido: 'πA+πB=1→πA+(4/3)πA=1'. Es la forma más cómoda de apuntar
    a una fórmula concreta sin tener el LaTeX original.
    """
    s = open(archivo).read()
    hits = [m for m in re.finditer(r'<math display="block".*?</math>', s, re.S)
            if re.sub(r"<[^>]+>", "", m.group(0)).startswith(firma)]
    assert len(hits) == 1, f"la firma {firma!r} matcheó {len(hits)} fórmulas, tiene que matchear una"
    nuevo = compilar(f"\\[{latex_nuevo}\\]")
    h = hits[0]
    open(archivo, "w").write(s[:h.start()] + nuevo + s[h.end():])
