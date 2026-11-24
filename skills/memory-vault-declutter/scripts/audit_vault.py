#!/usr/bin/env python3
"""Read-only audit of a memory vault. Lists declutter candidates, changes nothing."""
import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
NOTE_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d{4}|\d{4}_unknown-time)\.md$")
VERSIONED = re.compile(r"^(.*)_v(\d+)(\.[^.]+)$")
SKIP_DIRS = {".git", "node_modules", ".obsidian"}
BIG_FILE = 50 * 1024 * 1024


def walk(vault):
    for path in sorted(vault.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(vault).parts):
            continue
        yield path


def rel(vault, path):
    return path.relative_to(vault).as_posix()


def section(title, lines):
    print(f"\n## {title} ({len(lines)})")
    for line in lines:
        print(f"- {line}")
    if not lines:
        print("- none")


def inbox(vault):
    folder = vault / "00-inbox"
    if not folder.is_dir():
        return []
    return [p.name for p in sorted(folder.iterdir()) if p.name != "00-inbox.md"]


def old_notes(vault, days):
    folder = vault / "01-daily-notes"
    cutoff = datetime.now() - timedelta(days=days)
    found = []
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        match = NOTE_NAME.match(path.name)
        if match and datetime.strptime(match.group(1), "%Y-%m-%d") < cutoff:
            found.append(path)
    return found


def open_next(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    items = []
    for line in text.splitlines():
        match = re.match(r"^\s*-\s*\*\*Next:\*\*\s*(.+)$", line)
        if match and not re.match(r"^(none|nothing|n/a|-)\b", match.group(1), re.I):
            items.append(match.group(1).strip()[:100])
    return items


def broken_links(vault):
    found = []
    for path in walk(vault):
        if path.suffix != ".md":
            continue
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            if in_fence:
                continue
            for match in LINK.finditer(line):
                target = match.group(1).strip().split("#", 1)[0]
                if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
                    continue
                if not (path.parent / target).exists():
                    found.append(f"{rel(vault, path)}:{number} -> {target}")
    return found


def folders_without_master(vault):
    found = []
    for path in walk(vault):
        if path.is_dir() and not (path / f"{path.name}.md").exists():
            if any(child.is_file() for child in path.iterdir()):
                found.append(rel(vault, path))
    return found


def uncovered_files(vault):
    # a file counts as covered when its folder master file mentions its name
    found = []
    for path in walk(vault):
        if not path.is_dir():
            continue
        master = path / f"{path.name}.md"
        if not master.exists():
            continue
        text = master.read_text(encoding="utf-8", errors="replace")
        for child in sorted(path.iterdir()):
            if child.is_file() and child != master and child.suffix == ".md" and child.name not in text:
                if path.name == "01-daily-notes":
                    continue
                found.append(rel(vault, child))
    return found


def index_mismatch(vault):
    folder = vault / "01-daily-notes"
    index = folder / "01-daily-notes.md"
    if not index.exists():
        return []
    text = index.read_text(encoding="utf-8", errors="replace")
    listed = set(re.findall(r"\[(\d{4}-\d{2}-\d{2}_[0-9a-z_-]+)\]", text))
    on_disk = {p.stem for p in folder.glob("*.md") if NOTE_NAME.match(p.name)}
    lines = [f"note not in index: {name}" for name in sorted(on_disk - listed)]
    lines += [f"index entry without file: {name}" for name in sorted(listed - on_disk)]
    return lines


def asset_versions(vault):
    groups = {}
    for path in walk(vault):
        match = VERSIONED.match(path.name) if path.is_file() else None
        if match:
            groups.setdefault((path.parent, match.group(1), match.group(3)), []).append(path.name)
    return [f"{rel(vault, k[0])}: {', '.join(sorted(v))}" for k, v in sorted(groups.items()) if len(v) > 1]


def big_files(vault):
    return [f"{rel(vault, p)} ({p.stat().st_size // 1024 // 1024} MB)" for p in walk(vault) if p.is_file() and p.stat().st_size > BIG_FILE]


def empty_folders(vault):
    return [rel(vault, p) for p in walk(vault) if p.is_dir() and not any(p.iterdir())]


def git_dirty(vault):
    result = subprocess.run(["git", "-C", str(vault), "status", "--short"], capture_output=True, text=True)
    return result.stdout.strip().splitlines() if result.returncode == 0 else ["not a git repository"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", type=Path)
    parser.add_argument("--days", type=int, default=30, help="daily notes older than this are rollup candidates")
    args = parser.parse_args()
    vault = args.vault.expanduser().resolve()
    if not vault.is_dir():
        sys.exit(f"{vault} is not a directory")

    print(f"# Vault audit of {vault}")
    section("Uncommitted changes (commit or stop before decluttering)", git_dirty(vault))
    section("Inbox items still unsorted", inbox(vault))
    notes = old_notes(vault, args.days)
    section(f"Daily notes older than {args.days} days (rollup candidates)", [p.name for p in notes])
    carried = [f"{p.name}: {item}" for p in notes for item in open_next(p)]
    section("Open Next items inside those old notes (decide before rolling up)", carried)
    section("Daily note index mismatches", index_mismatch(vault))
    section("Broken relative links", broken_links(vault))
    section("Folders with files but no master file", folders_without_master(vault))
    section("Markdown files their master file never mentions", uncovered_files(vault))
    section("Asset version sets (keep the latest and the shipped one)", asset_versions(vault))
    section(f"Files over {BIG_FILE // 1024 // 1024} MB", big_files(vault))
    section("Empty folders", empty_folders(vault))


if __name__ == "__main__":
    main()
