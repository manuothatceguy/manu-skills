# Unit drafting prompt

Use this prompt when asking a worker or drafting a course unit in a separate file. Adapt it to the available tools and the requested output; it is a guide, not a required structure.

> Draft the section for **[unit/topic]** from the supplied course materials. Save it to **[path]** in the learner’s language, using the course’s terminology and notation. Cover the examinable ideas at the depth supported by the sources. Cite source page numbers in a compact way where useful. Match the examples and question formats to the actual exams. Clearly label any explanation that goes beyond the supplied material.
>
> If an output file already exists, inspect it and continue without discarding useful work. Save progress in manageable increments. Check formulas and worked answers against the sources. Use only the HTML components that serve this unit; do not force a recap, diagram, quiz, scaffold, or callout if it adds no value.

For an HTML fragment, use the surrounding guide’s conventions. Omit document-level wrappers such as `<!doctype>`, `<html>`, `<head>`, and `<body>`. Put diagrams in self-contained HTML, CSS, or inline SVG; do not rely on a remote renderer. Use `\( ... \)` and `\[ ... \]` for math when the guide will pass through the MathML build. Keep prose outside `.formula` blocks. Close paragraphs before block elements and balance tags.

A section may include a short recap, worked example, practice question with a revealed answer, misconception check, or self-evaluation when appropriate. Keep answers and explanations accurate and grounded in the course sources.
