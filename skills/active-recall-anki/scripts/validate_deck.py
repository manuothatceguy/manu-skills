#!/usr/bin/env python3
"""Validate the structure and basic syntax of Anki TSV decks.

Usage:
  python3 validate_deck.py deck.tsv [--strict]

Checks:
  1. Tab-delimited structure (exactly 3 columns: Front, Back, Tags).
  2. Balanced Cloze deletions with positive indices, including {{c1,2::...}}.
  3. Warns when fronts exceed 350 characters.
  4. HTML tag balance inside card fields.
"""

import argparse
import csv
import re
import sys
from pathlib import Path


def check_cloze_syntax(text: str) -> list[str]:
    errors = []
    open_count = text.count("{{")
    close_count = text.count("}}")
    if open_count != close_count:
        errors.append(f"Unbalanced cloze brackets: {open_count} open '{{{{' vs {close_count} close '}}}}'")

    cloze_matches = re.findall(r"\{\{([^}]+)\}\}", text)
    for c in cloze_matches:
        match = re.fullmatch(r"c((?:\d+,)*\d+)::(\S(?:.*\S)?)", c, flags=re.S)
        if not match or any(int(index) == 0 for index in match.group(1).split(",")):
            errors.append(f"Malformed cloze deletion '{{{{{c}}}}}' (expected format: '{{{{c1::content}}}}' or '{{{{c1,2::content}}}}')")
    return errors


def check_html_tags(text: str) -> list[str]:
    errors = []
    text_clean = re.sub(r"<(?:area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)\b[^>]*>", "", text, flags=re.I)
    tags = re.findall(r"<(/?[a-zA-Z0-9]+)\b[^>]*>", text_clean)
    stack = []
    for tag in tags:
        if tag.startswith("/"):
            close_tag = tag[1:].lower()
            if not stack:
                errors.append(f"Stray closing tag </{close_tag}> without opener")
            elif stack[-1] != close_tag:
                errors.append(f"Mismatched HTML tag: opened <{stack[-1]}>, closed </{close_tag}>")
                stack.pop()
            else:
                stack.pop()
        else:
            stack.append(tag.lower())
    if stack:
        errors.append(f"Unclosed HTML tags: {', '.join(f'<{t}>' for t in stack)}")
    return errors



def validate_deck(file_path: Path, strict: bool = False) -> tuple[int, int]:
    fatal_errors = 0
    warnings = 0

    if not file_path.exists():
        print(f"Error: file '{file_path}' does not exist", file=sys.stderr)
        return 1, 0

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for line_num, row in enumerate(reader, start=1):
            if not row or (len(row) == 1 and not row[0].strip()):
                continue

            if len(row) != 3:
                print(f"[Line {line_num}] Error: Expected 3 columns (Front, Back, Tags), found {len(row)}")
                fatal_errors += 1
                continue

            front, back, tags = row

            if not front.strip():
                print(f"[Line {line_num}] Error: Front field is empty")
                fatal_errors += 1

            if "{{" in front or "}}" in front:
                for err in check_cloze_syntax(front):
                    print(f"[Line {line_num}] Cloze Error: {err}")
                    fatal_errors += 1

            raw_front = re.sub(r"<[^>]+>", "", front).strip()
            if len(raw_front) > 350:
                print(f"[Line {line_num}] Warning: Front length {len(raw_front)} chars exceeds recommended 350")
                warnings += 1

            for field_name, content in [("Front", front), ("Back", back)]:
                for err in check_html_tags(content):
                    print(f"[Line {line_num}] HTML Error in {field_name}: {err}")
                    fatal_errors += 1

    return fatal_errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate Anki TSV flashcard decks")
    parser.add_argument("deck", help="Path to .tsv deck file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as fatal errors")
    args = parser.parse_args()

    deck_path = Path(args.deck)
    errors, warnings = validate_deck(deck_path, strict=args.strict)

    print(f"\nValidation complete: {errors} errors, {warnings} warnings.")
    if errors > 0 or (args.strict and warnings > 0):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
