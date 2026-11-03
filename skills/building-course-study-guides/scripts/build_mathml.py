#!/usr/bin/env python3
"""Assemble ordered HTML fragments and compile their LaTeX to MathML."""

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path


MATH_TOKEN = re.compile(r"\\\[(.+?)\\\]|\\\((.+?)\\\)", re.S)
PROTECTED_BLOCK = re.compile(r"<!--.*?-->|<(pre|code|script|style)\b[^>]*>.*?</\1\s*>", re.S | re.I)
RAW_LATEX = re.compile(r"\\(?:\[|\]|\(|\)|[A-Za-z]{2,})")


def compile_math(source):
    protected = []
    tokens = []

    def hide(match):
        protected.append(match.group(0))
        return f"@@PROTECTED{len(protected) - 1}@@"

    def extract(match):
        kind = "block" if match.group(1) is not None else "inline"
        tokens.append((kind, match.group(1) or match.group(2)))
        return f"@@MATH{len(tokens) - 1}@@"

    staged = PROTECTED_BLOCK.sub(hide, source)
    staged = MATH_TOKEN.sub(extract, staged)
    if not tokens:
        if RAW_LATEX.search(staged):
            raise ValueError("uncompiled LaTeX remains in the assembled HTML")
        return source, 0, 0

    markdown = "\n\n<!--SEP-->\n\n".join(
        f"$${html.unescape(value).strip()}$$" if kind == "block" else f"${html.unescape(value).strip()}$"
        for kind, value in tokens
    )
    result = subprocess.run(
        ["pandoc", "--mathml", "-f", "markdown", "-t", "html"],
        input=markdown,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"pandoc failed: {result.stderr.strip()}")

    converted = re.findall(r"<math\b.*?</math>", result.stdout, flags=re.S)
    if len(converted) != len(tokens):
        raise ValueError(
            f"{len(tokens)} formulas in, {len(converted)} out. "
            "Run find_bad_formula.py on the fragments to locate unsupported LaTeX"
        )

    for index, ((kind, _), mathml) in enumerate(zip(tokens, converted)):
        mathml = re.sub(r"<annotation\b.*?</annotation>", "", mathml, flags=re.S)
        mathml = mathml.replace("<semantics>", "").replace("</semantics>", "")
        if kind == "block" and 'display="block"' not in mathml:
            mathml = mathml.replace("<math ", '<math display="block" ', 1)
        staged = staged.replace(f"@@MATH{index}@@", mathml, 1)

    if "@@MATH" in staged or RAW_LATEX.search(staged):
        raise ValueError("uncompiled LaTeX remains in the assembled HTML")
    if re.search(r"<mi>&(?:amp;)?</mi>", staged):
        raise ValueError("an aligned formula contains a literal ampersand")

    multiline = sum(1 for _, value in tokens if r"\begin{aligned}" in value or r"\\" in value)
    if multiline > staged.count("<mtable"):
        raise ValueError(f"{multiline} multiline formulas but only {staged.count('<mtable')} MathML tables")

    for index, block in enumerate(protected):
        staged = staged.replace(f"@@PROTECTED{index}@@", block, 1)

    block_count = sum(kind == "block" for kind, _ in tokens)
    return staged, block_count, len(tokens) - block_count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", required=True, type=Path)
    parser.add_argument("fragments", nargs="+", type=Path, help="HTML fragments in document order")
    args = parser.parse_args(argv)

    try:
        source = "\n".join(path.read_text(encoding="utf-8") for path in args.fragments)
        built, blocks, inline = compile_math(source)
        args.output.write_text(built, encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1

    print(f"Wrote {args.output}: {blocks} display and {inline} inline formulas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
