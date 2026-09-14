---
name: clean-code-writing
description: Use when writing new functions, classes, modules or endpoints and names, function size, arguments, error handling or comments need to stay readable, or when the user asks for "clean code", "código limpio", "better names", "smaller functions". Not for reviewing a finished diff, restructuring existing code or deciding layers.
---

# Clean Code while writing

Working code is not automatically clean code. Write for a reader who reasons locally: they should understand a function without reconstructing hidden state.

Before writing, read the file you will edit and one neighbor. Match its naming, error handling, logging and imports. Project conventions beat these rules.

## Names
- A name says why it exists and what it does. Reject `data`, `info`, `temp`, `result2`, `manager`, `utils`, `handle*`/`process*` without a qualifier.
- One word per concept across the codebase. Don't mix `fetch`/`get`/`retrieve` for the same idea.
- Length follows scope: short for tiny scopes, descriptive for wide ones.
- Commands are verbs, queries are nouns or predicates (`isValid`, `total`).

## Functions
- Small, one level of abstraction, one job. If you can extract a piece with a name that doesn't restate the body, the function did more than one thing.
- Read top-down: intent first, details in helpers below (stepdown rule).
- Few arguments. More than 3-4 means a missing concept, so introduce a parameter object. No boolean flag arguments; split into two functions.
- Command-query separation: a function either changes state or answers, not both. No hidden side effects, no output parameters.
- Keep cyclomatic complexity low (aim ≤ 5, hard ceiling 10) and nesting shallow. Prefer guard clauses and polymorphism over nested conditionals.

## Errors
- Keep the happy path readable. Isolate error handling from the logic.
- Throw or return typed errors with context. Never swallow errors with a catch-all that returns null/empty success.
- Don't return or pass null when the language offers optional/result types or a special-case object.

## Objects and data
- Objects hide data and expose behavior. Data structures expose data and have no behavior. Don't build hybrids.
- Law of Demeter: avoid `a.getB().getC().doD()` train wrecks. Tell, don't ask.
- Keep framework, persistence, vendor and construction details out of business logic.

## Comments
- A comment is a failure to express intent in code. First rename or extract.
- Keep only why-comments: rationale, constraints, warnings, legal, public API contracts.
- Delete commented-out code, changelog comments and comments that paraphrase the line below.
- Agents read comments and trust them. A stale comment leads them to write bugs, so fix it or delete it in the same change.

## Simple design (Kent Beck, in priority order)
1. Passes all tests.
2. Reveals intent.
3. No duplicated knowledge (same rule in two places). Similar-looking code that encodes different rules is not duplication.
4. Fewest elements. No speculative flags, interfaces, factories or config without a present caller.

## Before you say "done"
- Can each changed function be understood without scrolling?
- Did any name need a comment to explain it? Rename instead.
- Is there a test that protects the new behavior, and did you run it?
- Boy Scout rule: leave touched code a bit cleaner, but do not widen the task beyond what makes the change safe.
