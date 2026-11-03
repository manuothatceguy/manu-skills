# Verification

Compare each unit with the relevant syllabus and source pages. Check coverage, course terminology, diagrams, and worked answers. For graphical models, compare every plotted equilibrium marker and shaded area with the curve intersections and equations, then inspect the PDF export at reading size. Include retrieval questions that make the learner interpret a curve when graphical interpretation is part of the course. Text extraction helps search, but it may omit visual information or flatten superscripts and subscripts. Inspect rendered PDF pages for diagrams, figure-based questions, and exercise notation that looks ambiguous or inconsistent after extraction. Use automated checks to locate possible structural problems, then inspect each finding in context. Delegation is optional and depends on the current runtime.

Audit every distinct diagram in the browser and the exported PDF. Inspect curve labels as well as markers: a label can cross a line even when the marker is correct. Check that captions and headings use the same subscripts as the plotted old and new states. Keep short mathematical expressions in captions together when printing; compile them as inline math or use a no-break span. For rates, name both the quoted period and capitalization frequency. A nominal annual rate with monthly capitalization must not be called a monthly rate.

## Available scripts

Use only scripts present in the checkout. Keep generated files in the task workspace. The core scripts are:

- `build_mathml.py --output <built.html> <fragment>...` assembles fragments in the given order and compiles LaTeX in one pandoc call.
- `verify_build.py <built.html>` checks common math and HTML structure problems. It cannot verify content accuracy or coverage.
- `dump_section.py --file <built.html> [<id>] [--math]` displays a section or its formulas compactly.
- `find_bad_formula.py <dir>` helps locate a formula when the build’s formula count does not match.

Run relevant checks after meaningful edits. Independently verify worked calculations and quiz answers against the source. A passing structural check does not establish that the guide is complete or correct.

After math conversion, compare the source formula count with the MathML count and search for `merror`. Render the display formulas and representative inline formulas at reading size, then inspect print output for broken or split notation. Text extraction alone cannot prove that the compiled formula looks right.

## Print and PDF

When the learner needs a printable guide, inspect print preview. Use print styles to preserve formulas and headings, and decide whether hidden answers should print open. Verify the resulting pages in the browser print preview; layout varies by browser and printer settings. Check the rendered page text for nearly empty pages, especially when a source note spills past a forced section break. A compact print line height or smaller source-note spacing can keep citations with their section. For colored page backgrounds or diagonal shapes, inspect the rendered page itself for text contrast at every overlap; CSS colors alone do not establish readability.

## Lessons from content reviews

- Audit explanatory prose as well as formulas. A correct accounts formula can coexist with a sentence wrongly implying that financial-asset purchases are productive investment. Check definitions, exclusions, units, denominators and boundary cases such as indifference at the shutdown price.
- Do not attribute a learner-supplied correction to the teacher without evidence. Label it as a corrected point or an agreed assumption.
- Source slides can contradict their own graphs. Inspect the original page and explain an established erratum rather than reproduce the mistake.
- A topic name is not coverage: give the mechanism, conditions and a concrete example, especially for unemployment types, inflation versus disinflation, production stages and policy limits.
- When reading checks are requested, place them throughout every included unit. Check both answer logic and the interaction, including invalid short answers and stale feedback after edits.
- When using worked solutions, verify price and quantity separately against the demand and first-order condition. Swapping their labels leaves revenue unchanged and can hide an error. Keep exact values until the final rounding of areas and elasticities.
- Check that average, total and marginal cost functions are compatible: total cost equals quantity times average cost, and marginal cost is its derivative. If the source contradicts itself, identify which consistent subset solves the requested question and flag the contradiction.
- Distinguish short-run shutdown from long-run exit. State which costs remain payable, use the corresponding average-cost threshold, and explain indifference at equality. When aggregating a finite number of firms with positive startup quantities, do not connect discrete threshold quantities into a continuous supply segment.
- If an objective such as “maximize sales” is ambiguous, state whether it means revenue or physical quantity and explain how the alternative changes the result. Do not silently treat a handwritten interpretation as part of the enunciado.
- Aggregate segment demands only while their individual quantities are nonnegative. Check the active price interval before comparing uniform pricing and price discrimination; a formal sum may stop describing the same market at the computed optimum.
- Track units through surplus areas: a price in cents times a quantity in millions gives millions of cents. Producer surplus is revenue minus variable costs; it is not profit unless fixed costs are zero or deducted explicitly.
