# Math rendering

For quantitative material, write equations in LaTeX and compile them to native MathML with `pandoc --mathml`. This avoids raw LaTeX in the finished HTML and does not require a browser math library or external assets.

Use `\( … \)` for inline math and `\[ … \]` for display math. Put only the equation in a `.formula` block. Use `aligned` inside a single display delimiter pair for multi-line derivations:

```html
<div class="formula">
  <span class="fcap">Stationary distribution</span>
  \[\begin{aligned}
    \pi_A + \pi_B &= 1 \\
    \pi_A &= \frac{3}{7}
  \end{aligned}\]
</div>
```

From the skill directory, run `python3 scripts/build_mathml.py --output /task/guide.html /task/parts/00-header.html /task/parts/01-unit.html /task/parts/99-footer.html` with fragments in document order. Replace `/task` with the task workspace path. The script sends formulas to pandoc in one batch and checks their count before writing the output. It leaves code blocks, scripts, styles, and HTML comments untouched so examples stay literal. It strips spaces inside delimiters. Use `aligned` rather than `align` or `align*` inside display delimiters.

Pandoc may reject some LaTeX commands, including extensible arrows such as `\xrightarrow`. If the output count differs from the input count, inspect the expressions and replace unsupported notation with supported primitives, such as `\overset{a}{\longrightarrow}`. Verify the generated `<mtable>` for multi-line equations and check that no raw delimiters or LaTeX commands remain in the finished HTML.

Do not put LaTeX inside a literal `<math>` element. The build only processes expressions wrapped in the delimiters above. A literal `<math>\lambda_i</math>` is not compiled and will show its source as text.

Keep derivations readable. Split long chains into aligned rows, repeat the left-hand side when it helps, and put explanatory captions in HTML rather than `\text{…}` rows that may stretch a narrow equation column. Allow wide equations to scroll on small screens, and inspect a real rendered example before delivery.

After building, check more than whether `<math>` elements exist. Confirm formula counts, multi-line tables, literal ampersands, and surviving LaTeX. Then verify the calculations against course sources; a successful conversion does not establish mathematical correctness.
