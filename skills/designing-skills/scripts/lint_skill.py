#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

MAX_BODY_WORDS = 2000
MAX_DESCRIPTION_CHARS = 1024
LINT_OFF = re.compile(r"<!--\s*skill-lint:\s*off\s*-->")
LINT_ON = re.compile(r"<!--\s*skill-lint:\s*on\s*-->")
FENCE = re.compile(r"^\s*(```|~~~)")
LOCAL_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SHOUT_WORDS = r"MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT|MANDATORY|REQUIRED|DO NOT|DON'T|SIEMPRE|NUNCA|CRÍTICO|IMPORTANTE|OBLIGATORIO"

LINE_RULES = [
    (
        "persona-opener",
        re.compile(
            r"\b(you are|you're) (an?|the) [\w\s,-]{0,40}?(expert|specialist|engineer|developer|assistant|architect|analyst|writer|reviewer)\b"
            r"|\bact as (an?|the)\b|\b(sos|eres) un[a]? [\w\s-]{0,30}?(expert[oa]|especialista|ingenier[oa]|desarrollador[a]?|asistente)\b"
            r"|\bactu[aá] como\b",
            re.I,
        ),
        "give the knowledge the expert would have instead of the role",
    ),
    ("shouting", re.compile(rf"(?<![\w`])({SHOUT_WORDS})(?![\w`])"), "lowercase it and add the reason"),
    (
        "incantation",
        re.compile(
            r"think step[- ]by[- ]step|take a deep breath|i('ll| will) tip|\$\d+ tip|you will be (penali[sz]ed|fired|punished)"
            r"|do(n't| not) hallucinate|no alucines|pens[aá] paso a paso|my (job|career) depends",
            re.I,
        ),
        "delete it or replace it with a concrete check",
    ),
    (
        "hardcoded-location",
        re.compile(r"(?<![\w.])(/home/|/Users/|/root/|/mnt/c/|[A-Z]:\\Users\\)[\w.-]+|\blocalhost:\d+|\b\d{1,3}(\.\d{1,3}){3}\b"),
        "use a path relative to the skill, or tell the agent how to find it",
    ),
    (
        "session-narrative",
        re.compile(
            r"\bas (we )?(discussed|mentioned|agreed)\b|\bin this (session|conversation|chat)\b|\bthe user (asked|said|wanted|requested)\b"
            r"|\b(earlier|previously) (we|you|i)\b|\bcomo (hablamos|vimos|dijimos)\b|\ben esta (sesi[oó]n|conversaci[oó]n)\b",
            re.I,
        ),
        "rewrite as a standing instruction or delete",
    ),
    ("external-reference", re.compile(r"https?://[^\s)>\]]+"), "inline the fact that matters or bundle the file"),
    (
        "stale-pin",
        re.compile(
            r"\b(as of|since|until) (\w+ )?20\d\d\b|\b20\d\d-\d\d-\d\d\b|\b(gpt-[\w.]+|claude[- ][\w.-]*\d[\w.-]*|gemini[- ][\w.]+)\b"
            r"|\b(the )?(latest|newest|current) (version|model|release)\b",
            re.I,
        ),
        "tell the agent where to look up the current value",
    ),
    (
        "triviality",
        re.compile(
            r"\b(follow|use|apply) (industry )?best practices\b|\bwrite (clean|good|high[- ]quality|maintainable) code\b"
            r"|\bbe (thorough|careful|concise|helpful|professional)\b|\bhandle errors (properly|gracefully|appropriately)\b"
            r"|\bmake sure (the code|it) works\b|\bensure (high )?quality\b|\bbuenas pr[aá]cticas\b|\bc[oó]digo limpio y\b",
            re.I,
        ),
        "delete it or name the specific non-obvious standard",
    ),
    (
        "no-finish-line",
        re.compile(r"\buntil (you are |you're )?(satisfied|happy|confident|done)\b|\bas (needed|appropriate|necessary)\b|\bhasta (estar|quedar) (conforme|satisfecho)\b", re.I),
        "state a condition the agent can check",
    ),
    (
        "human-facing-section",
        re.compile(r"^#{1,6}\s*(installation|install|changelog|change log|license|author|credits|contributing|version history|when to use( this skill)?)\s*$", re.I),
        "move it to a README, or fold triggers into the description",
    ),
]


def split_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return {}, 0
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            fields = {}
            for raw in lines[1:index]:
                match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", raw)
                if match:
                    fields[match.group(1)] = match.group(2).strip().strip("\"'")
            return fields, index + 1
    return {}, 0


def lint_description(path, fields):
    findings = []
    description = fields.get("description", "")
    if not description:
        return [(path, 1, "description", "missing description", "write the situations that should load the skill")]
    if len(description) > MAX_DESCRIPTION_CHARS:
        findings.append((path, 1, "description", f"{len(description)} characters", "one trigger per distinct situation"))
    if re.search(r"\b(first|then|next|finally|step \d|after that)\b.*\b(then|next|finally)\b", description, re.I):
        findings.append((path, 1, "workflow-in-description", "the description reads like a sequence of steps", "keep triggers, move the workflow to the body"))
    if re.search(r"\b(I|we|my|our) \b|\byou can\b", description):
        findings.append((path, 1, "description", "first or second person", "third person, starting from the triggering situation"))
    return findings


def lint_file(path, is_main=False):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        return [(path, 0, "unreadable", str(error), "fix the file")]
    findings = []
    start = 0
    if is_main:
        fields, start = split_frontmatter(lines)
        if start == 0:
            findings.append((path, 1, "frontmatter", "missing or unterminated frontmatter", "add name and description"))
        else:
            findings.extend(lint_description(path, fields))
    muted = False
    fenced = False
    words = 0
    for number, line in enumerate(lines[start:], start + 1):
        if LINT_OFF.search(line):
            muted = True
            continue
        if LINT_ON.search(line):
            muted = False
            continue
        words += len(line.split())
        if muted:
            continue
        for rule, pattern, fix in LINE_RULES:
            match = pattern.search(line)
            if match:
                findings.append((path, number, rule, match.group(0).strip(), fix))
        if FENCE.match(line):
            fenced = not fenced
        if fenced:
            continue
        for match in LOCAL_LINK.finditer(line):
            target = match.group(1).strip().split("#", 1)[0]
            if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            destination = (path.parent / target).resolve()
            if not destination.exists():
                findings.append((path, number, "broken-pointer", target, "bundle the file or drop the pointer"))
            elif not is_main and destination.suffix == ".md":
                findings.append((path, number, "deep-nesting", target, "point to it from the main file instead"))
    if words > MAX_BODY_WORDS:
        findings.append((path, 0, "sprawl", f"{words} words", "disclose rare branches behind pointers or split the skill"))
    return findings


def lint_skill(target):
    target = Path(target)
    main = target / "SKILL.md" if target.is_dir() else target
    if not main.is_file():
        return [(main, 0, "missing", "no SKILL.md found", "pass a skill directory or a SKILL.md path")]
    findings = lint_file(main, is_main=True)
    if target.is_dir():
        for extra in sorted(target.rglob("*.md")):
            if extra != main:
                findings.extend(lint_file(extra))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print candidate smells in a skill. Every finding is a question for the reviewer, some lines legitimately stay.")
    parser.add_argument("targets", nargs="+", help="skill directories or SKILL.md files")
    args = parser.parse_args(argv)
    findings = [finding for target in args.targets for finding in lint_skill(target)]
    for path, number, rule, evidence, fix in findings:
        print(f"{path}:{number}: [{rule}] {evidence} -> {fix}")
    print(f"{len(findings)} candidate(s).", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
