import argparse
import ast
import io
from pathlib import Path
import re
import tokenize


def clean_comments(source):
    ast.parse(source)
    lines = source.splitlines(keepends=True)
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    for token in reversed(tokens):
        if token.type != tokenize.COMMENT:
            continue
        comment = re.sub(r"^# - ", "#\t", token.string)
        trimmed = comment.rstrip()
        if trimmed.endswith(".") and not trimmed.endswith(".."):
            comment = trimmed[:-1] + comment[len(trimmed):]
        row, start = token.start
        end = token.end[1]
        lines[row - 1] = lines[row - 1][:start] + comment + lines[row - 1][end:]
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check Python comment punctuation and bullets")
    parser.add_argument("--write", action="store_true", help="Apply changes to comments")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    pending = []
    for path in args.files:
        raw = path.read_bytes()
        encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
        source = raw.decode(encoding)
        cleaned = clean_comments(source)
        if cleaned != source:
            pending.append((path, cleaned.encode(encoding)))
    for path, content in pending:
        if args.write:
            path.write_bytes(content)
        print(f"{path}: {'updated' if args.write else 'comment changes needed'}")
    return int(bool(pending) and not args.write)


if __name__ == "__main__":
    raise SystemExit(main())
