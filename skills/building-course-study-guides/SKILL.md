---
name: building-course-study-guides
description: Use when a learner needs a complete study guide from course slides, textbooks, or lecture materials, especially for exam preparation. Triggers on “guía de estudio”, “resumen de materia”, “preparar examen final”, “course study guide”, and “exam prep”.
---

# Building Course Study Guides

Create a clear, source-grounded study guide in the format the learner requests. For a large course, a self-contained HTML file is a useful default. Match the learner’s language, preserve course terminology, and prioritize topics using the syllabus and available exams.

## Workflow

1. Inspect the syllabus, course materials, and available past exams. Recheck the file inventory if the learner adds materials during drafting. Extract searchable text, and inspect rendered PDF pages where diagrams, tables, or visual questions matter. Record the unit structure, source pages, notation, learner language, and exam language. See [course-content.md](references/course-content.md) for content and exam alignment.
2. Plan coverage and depth with the learner’s time and goal in mind. Draft one section at a time, using [constructor-prompt-template.md](constructor-prompt-template.md) as a flexible contract. Delegation is optional; use only tools and models available in the current runtime.
3. Assemble the requested deliverable. For HTML, see [html-design.md](references/html-design.md) and reuse `scripts/shell_snippets.html` as needed. Keep external dependencies out of offline deliverables; use static diagrams such as inline SVG or HTML/CSS.
4. For quantitative courses, follow [math-rendering.md](references/math-rendering.md). Run the MathML builder with the task workspace output path and fragments in document order.
5. Check the guide against its sources, including worked calculations, exercise coverage, terminology, and rendered diagrams. Use [verification.md](references/verification.md) and `scripts/verify_build.py` for relevant structural checks. Inspect the result on a narrow screen and in print when HTML is requested.
6. Deliver the requested files and a concise coverage note. Create a local HTML file by default; publish only when requested.

## Route related learning requests

At planning time and whenever the learner changes the deliverable, check which companion skills apply. Load each matching skill for its part of the work; this guide keeps responsibility for source selection, course coverage, and fact checking.

- **Guided practice:** If the learner wants tutoring, oral-exam rehearsal, step-by-step problem solving, or guided exercises within the guide, use `socratic-tutor` for the prompts, hints, and feedback. Anchor them in the course material.
- **Spaced review:** If the deliverable includes flashcards, an Anki deck, or a spaced-repetition practice set, use `active-recall-anki` for card design and TSV validation. Check every card against the source before delivery.
- **Separate quiz:** If the learner asks for a standalone quiz and `quiz-maker` is available, use it for question formats. Check its answer key and coverage against the course sources.

Include only deliverables that follow from the learner’s request and the agreed guide scope.

## Content choices

### Explain every subject-specific concept

Assume the learner is meeting the subject for the first time unless they explicitly state otherwise. Define every subject-specific term when it first appears in the teaching sequence, including basic prerequisite concepts. Do not start explaining only at the term the learner flagged: audit from the beginning of every included unit. For example, explain cost, production, quantity, total, average and marginal before asking the learner to interpret marginal cost.

For each concept, state what it means in plain language, what it measures or describes, and how it differs from nearby concepts. Use a concrete example when the definition alone does not make the meaning clear. Definitions must not depend on other undefined technical terms or merely repeat the term using synonyms.

Introduce the meaning before the formula. Explain every symbol, unit, denominator and assumption needed to interpret it. Show how to read the result in words. A formula, acronym expansion, topic heading, worked calculation or quiz explanation does not substitute for teaching the concept.

Make every formula panel readable on its own. Repeat each acronym's full name beside its equation even if introduced earlier. Include a nearby key for variables, subscripts, Greek letters, change symbols and derivatives, with units and a plain-language interpretation. Split collections of equations into individually labeled rows or cards rather than one horizontally scrolling chain. Verify the panel at reading size on desktop and mobile; an earlier paragraph or a distant glossary does not satisfy local clarity.

When adding links to shared definitions, provide a visible return link to the exact formula or passage that opened them. Track the originating anchor per visit, including when multiple formulas share a definition, and test the full outbound-and-return path with keyboard focus. Keep definitions usable without JavaScript through ordinary anchors and a section-level fallback return.

Keep the definitions in the main reading flow, before exercises and reading checks that use them. A glossary can support navigation and review, but must not be the only place that explains a concept. Define technical terms in graph labels, captions, tables, examples and answer feedback too, or explicitly link them to an earlier explanation.

Before delivery, audit the vocabulary of all included units for undefined concepts and circular definitions. Verify that a first-time reader can understand each explanation using concepts already introduced. Fix all gaps, rather than adding only the specific definition mentioned in user feedback. Completeness applies to the agreed scope; it does not justify adding excluded units.

Teach unfamiliar ideas clearly and match the actual exam format. Use worked examples, partially completed steps, diagnostic errors, retrieval questions, diagrams, or mixed practice when they fit the subject and the learner’s needs. These are options, not mandatory components of every unit. Do not add interactive behavior or a particular section merely to satisfy a template.

Preserve course-specific symbols and terminology when they affect interpretation or grading. Explain alternate terms when they help the learner connect course materials to other sources. A glossary, formula sheet, recipe bank, or theory-question bank can help when supported by the materials or requested; do not invent exam frequencies or claim exact exam wording without checking the papers.

## Relevant tools

Resolve the following script paths relative to this SKILL.md. The command examples assume the current directory is this skill directory; output and fragment paths can point into the task workspace.

- `scripts/build_mathml.py --output <built.html> <fragment>...`: assemble fragments in the given order and compile LaTeX to MathML.
- `scripts/verify_build.py <built.html>`: checks common math and HTML structure problems. Treat findings as leads to inspect, since structural checks cannot establish content correctness.
- `scripts/dump_section.py --file <built.html> [<id>] [--math]`: inspect a section or its formulas in a compact text view.
- `scripts/find_bad_formula.py <dir>`: help locate a formula when a MathML build reports a count mismatch.

Use only tools that exist in the current checkout. Keep generated guide files in the task workspace.
