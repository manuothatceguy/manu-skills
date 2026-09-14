# Constructor prompt template

Dispatch one Agent per unit with `model: "haiku"` and `run_in_background: true` (cap 2–3 concurrent). Fill the [BRACKETS].

```
ROL: profesor escribiendo UNA sección de una guía de estudio completa de [MATERIA]
para un alumno que no sabe nada del tema: enseñar desde cero, definir cada término
la primera vez que aparece. Examen: [formato, duración, estilo de preguntas].

UNIDAD: [tema]. FUENTES (leé con Read, pages de a máx 20 páginas hasta cubrir todo):
[rutas de PDF]
Basate en las slides reales; si falta un concepto necesario del tema estándar, incluilo.

SALIDA: [ruta exacta .html]
- Si la ruta YA existe: leela y continuá desde donde quedó, NO reescribas de cero.
- Escribí el archivo apenas tengas la primera subsección; ampliá con Edit tras cada paso
  (si te cortan por límite de sesión, lo escrito queda).
- Fragmento HTML sin doctype/html/head/body. Raíz <section id="[id]">, título <h2>[N]. [Título]</h2>.
- Primero un <div class="recap"><strong>En una mirada:</strong> ...</div> (4-6 líneas + "al terminar
  tenés que poder...").
- Subsecciones <h3>. Cajas: <div class="formula">, <div class="tip"><strong>Examen:</strong>,
  <div class="bug"><strong>Error típico:</strong>. Código en <pre><code> con &lt; &gt; &amp; escapados.
- MATEMÁTICA en LaTeX, NUNCA texto Unicode (nada de λ^k escrito λk, ni fracciones con /):
  display dentro de <div class="formula"> con \[ ... \], inline en prosa/tablas/<details> con \( ... \).
  Sin $ ni $$. El controller compila \[ \] y \( \) a MathML en el build; vos solo escribís el LaTeX.
- Checkpoints tras las subsecciones densas: <details><summary>Checkpoint: [pregunta]</summary>[resp]</details>.
- Cerrá con autoevaluación de 3-5 preguntas: <details><summary>Respuesta</summary>[resp]</details>.
- Sin markdown, sin estilos inline, sin <style>, sin recursos externos.
- MINI-QUIZZES interactivos (si el examen es multiple-choice): al menos 2-3 INTERCALADOS en el medio, markup EXACTO (no lo cambies), data-c="1" correcta / "0" incorrecta, puede haber 0/1/varias correctas, distractores = errores reales:
  <div class="quiz" data-multi="true">
    <p class="qz-q">[pregunta, \( ... \) inline]</p>
    <ul class="qz-opts"><li data-c="1">[correcta]</li><li data-c="0">[distractor]</li></ul>
    <button class="qz-check">Corregir</button>
    <div class="qz-fb">[por qué, breve]</div>
  </div>
- Cuidado estructural: cerrá SIEMPRE el <p> antes de abrir un <div class="formula"> (un <div> no va dentro de un <p>). La matemática multi-línea va dentro de \[\begin{aligned}...\end{aligned}\] (con el \[ \], y "aligned", nunca "align" suelto).

CONTENIDO MÍNIMO: [lista concreta de conceptos, al menos un ejemplo de código CON bug para
detectar, y una tabla comparativa donde aplique].
- Si hay un ejemplo numérico que el examen toma (p. ej. backprop a mano), copiá el FORMATO de la solución oficial de un examen viejo, no solo el resultado: si el examen usa un grafo escalar con nodos nombrados y la chain rule escrita paso a paso, hacelo así y no en forma matricial (aunque la matriz dé el mismo número, esconde el método que corrige el profe). Ideal: reusar los números de un problema real para poder verificar contra el solucionario.

IDIOMA: [ej. español rioplatense (voseo), términos técnicos en inglés].
EXTENSIÓN: [rango de palabras] más código.
MENSAJE FINAL: solo la ruta escrita + 2 líneas de qué cubriste. NO pegues el contenido.
```

## Controller verification snippet (cheap, no re-read)

```python
import re
s = open('guia.html').read()
print('sections', len(re.findall(r'<section', s)), '/', len(re.findall(r'</section>', s)))
for t in ['div','pre','table','details','ul','ol','main','style']:
    o = len(re.findall(r'<'+t+r'[ >]', s)); c = len(re.findall(r'</'+t+r'>', s))
    print(t, o, '/', c, '' if o == c else '<<< DESBALANCE')
print('recaps', s.count('class="recap"'), 'checkpoints', s.count('summary>Checkpoint'))
```
