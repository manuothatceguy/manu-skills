---
name: active-recall-anki
description: Use when generating spaced-repetition flashcards or Anki decks from course notes, slide decks, textbooks, documentation, or codebases. Triggers on "flashcards", "anki", "spaced repetition", "repetición espaciada", "tarjetas de memoria", "active recall", "memorizar", "generar mazo anki".
---

# Active Recall Cards for Anki

Turn supplied learning material into useful prompts for spaced review. Check answers against the source and keep its terms. Keep each card focused enough that the learner can tell what they need to retrieve and judge their answer.

Avoid prompts that require reciting long passages. Split a card when it asks for several independent facts, while keeping related steps together when splitting would remove useful context.

## Card design

Use basic question/answer or cloze formats as appropriate. A cloze should remain understandable with its surrounding text. Add context when a prompt would otherwise be ambiguous. Create reverse or comparison cards when they test a useful distinction, rather than automatically for every fact.

## Examples

### Basic
```
Front: [Probability] What distribution models the waiting time between arrivals in a Poisson process?
Back: Exponential distribution.
Tags: probability
```

### Cloze
```
Text: [Probability] In a Poisson process, the waiting time between arrivals is {{c1::exponentially distributed}}.
Extra: The rate parameter matches the process rate.
Tags: probability
```

## TSV output

Choose the Anki note type that matches the card format. Basic notes use Front and Back fields; cloze notes use Text and Extra fields. During import, map the first two columns to the fields for the selected note type and map the third column to Tags. Turn on "Allow HTML in fields" when the cards contain HTML. Keep Basic and Cloze notes in separate imports unless you explicitly configure a mixed-note import.

Use a tab-separated (`.tsv`) file with three columns:

- **Column 1**: Front (or Text for Cloze decks). HTML markup allowed (`<strong>`, `<code>`, `<pre>`, `\(` inline LaTeX).
- **Column 2**: Back (or Extra field for Cloze decks).
- **Column 3**: Tags, separated by spaces.

Rules for TSV generation:
- No literal tabs (`\t`) inside card fields (replace with spaces).
- Quoted fields may contain newlines; otherwise use `<br>` for line breaks.
- LaTeX uses MathJax delimiters recognized by modern Anki: `\(` and `\)` for inline, `\[` and `\]` for display.

Anki supports quoted fields containing newlines. Use `<br>` instead when a cloze deletion itself spans lines.
To show one deletion on several cards, Anki also accepts `{{c1,2::text}}`; the validator checks each index.

## Validation

Resolve the script path relative to this SKILL.md and run the deck validator before delivering. This example assumes the current directory is this skill directory:

```bash
python3 scripts/validate_deck.py my_deck.tsv
```

The validator checks three-column TSV structure, non-empty fronts, basic cloze syntax, HTML tag balance, and warns when a front exceeds 350 characters. With `--strict`, length warnings also fail validation. Review long cards for clarity; length alone does not establish that a card is poor.
