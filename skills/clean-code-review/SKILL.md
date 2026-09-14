---
name: clean-code-review
description: Use right after an agent or a person finishes a non-trivial code change and before presenting, committing or merging it, or when the user says "review this", "revisá este diff", "is this safe to merge", "audit this code", "this looks AI-generated". Not for conceptual questions, CI config or test-only diffs.
---

# Clean code review (guard pass)

Review the diff, not the whole repo. Prioritize behavior bugs and change-cost risks over style. Formatters and linters own formatting, so don't comment on it.

## 1. AI failure modes (check first, highest yield)
1. **Swallowed errors**: broad catch returning null, empty or "ok". Catch only what you can recover from.
2. **Fake success**: hardcoded return values, fixture data or stubs in production paths. Tests skipped, weakened or edited to pass.
3. **Hallucinated APIs**: calls to methods or packages that don't exist in the installed version. Verify against the lockfile or source.
4. **Copy-from-similar**: a duplicated function with small edits (off-by-one and wrong-null bugs hide here). Re-derive from the spec.
5. **Speculative generality**: flags, options, interfaces, factories, `*_v2`, `enable_*` with no current caller.
6. **Defensive noise**: null checks and type checks inside the trust boundary where the type already excludes the case. Keep validation at real boundaries (user input, network, deserialized data).
7. **Dead code**: unused imports, helpers, exports "for later".
8. **New dependency** for something a few local lines cover.
9. **Style drift**: a second pattern for logging, errors, HTTP or DB when the file already has one.
10. **Scope creep**: unrelated files touched, refactor bundled with a bug fix.

## 2. Code level
- Names reveal intent. Functions small, one job, ≤ 3-4 params, no flag args, command-query separated.
- Cyclomatic complexity ≤ 10, nesting ≤ 3-4.
- Comments explain why, never what. No commented-out code.

## 3. Design level (SOLID, named by the smell)
- **SRP**: a module answers to more than one actor (billing and reporting in one class).
- **OCP**: adding a variant means another `switch`/`if type ==` branch in existing code.
- **LSP**: an override throws "not supported" or ignores the parent's contract.
- **ISP**: clients forced to depend on methods they don't use.
- **DIP**: business logic imports concrete DB, HTTP or framework classes. Interfaces belong to the client that uses them.
- **Wrong abstraction**: a shared helper full of caller-specific branches. Inline it back first, then re-abstract.
- Design smells: rigidity, fragility, immobility, viscosity, needless complexity, needless repetition, opacity.

## 4. Never remove these while "simplifying"
Validation at trust boundaries, error handling that prevents data loss, security (authz, escaping, parameterized queries, secrets) and behavior the user asked for. Removing one is a behavior change, so flag it.

## Output
- Guard pass (you are the author): fix violations, then list `file:line: what changed` and close with `clean-code-review: N fixed, M flagged`.
- Review mode (someone else's code): don't edit. List findings by severity with `file:line`, the rule, a concrete failure scenario and the suggested fix.
- Never invent a quality score or percentage.

Prefer measuring over reading when tools exist: coverage, complexity, CRAP, mutation, duplication and dependency checks catch more than line-by-line review (see agent-quality-gates).
