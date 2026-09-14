#!/usr/bin/env python3
"""Busca callouts de práctica que mandan al alumno a un ejercicio que la guía
todavía no le enseñó a hacer.

  python3 check_practice_order.py guia.html

Los constructores cierran cada bloque con un "con lo visto acá ya podés hacer el
ejercicio N", sin fijarse en si la guía cubrió lo que ese ejercicio pide. El caso
que me encontré: "ya podés armar la base de reglas fuzzy" puesto justo después de
explicar un controlador PID, o sea antes de la primera palabra sobre fuzzy.

La heurística: de cada callout saco los términos técnicos y me fijo dónde aparece
por primera vez cada uno en el documento. Si la primera aparición está DESPUÉS del
callout, el lector no puede tener ese concepto todavía.

Da falsos positivos con palabras comunes, así que la salida es para leer a ojo, no
para aplicar a ciegas. Y ojo con una trampa: no uses el <h3>/<h4> anterior para
ubicar un callout, porque las regiones de encabezado abarcan varios subtemas y te
atribuyen el callout a un título que no tiene nada que ver. Comparar offsets crudos
es lo que distingue un problema real de una falsa alarma.
"""
import re, sys

PARAR = set("""con lo visto acá ya podés hacer el la los las de del que un una y o en es
para este esta ejercicio ejercicios sheet warm up toda cualquier también más como sus
te pide usando desde entre sobre son ser todo cada por al se su lo le pero si no
calcular calculá analizá implementá derivá armá modificá observá comparas hacés
viejos exámenes primero segundo tercero""".split())


def texto(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip()


def main(path):
    s = open(path).read()
    plano = texto(s).lower()
    # mapa de posición: recorto el HTML igual que el texto para poder comparar offsets
    problemas = 0
    for m in re.finditer(r'<div class="practice">(.*?)</div>', s, re.S):
        cuerpo = texto(m.group(1))
        # el título en inglés de la hoja va entre paréntesis y sólo existe acá adentro,
        # así que daba un falso positivo en casi todos los callouts
        cuerpo_util = re.sub(r"\([^)]*\)", " ", cuerpo)
        # dónde cae este callout medido en el texto plano
        ancla = texto(s[:m.start()]).lower()
        pos = len(ancla)
        terminos = {w for w in re.findall(r"[a-záéíóúñü\-]{5,}", cuerpo_util.lower())
                    if w not in PARAR}
        tarde = []
        for w in terminos:
            # si el término aparece una sola vez en todo el documento, esa vez es el
            # propio callout: no dice nada sobre el orden
            if plano.count(w) < 2:
                continue
            i = plano.find(w)
            if i > pos:
                tarde.append(w)
        if tarde:
            problemas += 1
            print(f"[callout] {cuerpo[:80]}")
            print(f"          términos que recién aparecen DESPUÉS: {sorted(tarde)}")
    print(f"\n{problemas} callout(s) para revisar a ojo")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "guia.html"))
