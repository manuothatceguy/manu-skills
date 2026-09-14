---
name: tdd-discipline
description: Use when implementing a feature or bug fix test-first, writing or judging unit tests, when tests break on every refactor or pass without catching bugs, or when the user says "TDD", "test first", "red green refactor", "tests primero", "mutation testing", "coverage".
---

# TDD discipline

## The three laws
1. Write no production code except to pass a failing test.
2. Write only enough of a test to fail (not compiling counts as failing).
3. Write only enough production code to pass the one failing test.

Cycle: **red → green → refactor**, measured in minutes. Refactor only on green, both production code and tests.

## Vertical slices, not horizontal
- One behavior → one test → minimal code → repeat. Each test is a tracer bullet that answers what the last cycle taught you.
- Don't write all tests first and then all code. Bulk tests check imagined behavior and lock in structure too early.
- Order tests from degenerate to general: empty, one, many, then edge cases. Let the design emerge. Each new test should force a more generic implementation ("as tests get more specific, code gets more generic").

## What a good test is
- It verifies behavior through a public interface (a seam), not private methods or internals. Refactoring must not break it.
- It reads like a spec: `rejects_checkout_when_cart_empty`, not `test3`.
- **F.I.R.S.T.**: Fast, Independent, Repeatable, Self-validating, Timely.
- One concept per test. Arrange-Act-Assert (Given-When-Then) with a visible structure.
- Expected values come from an independent source (a worked example, the spec, a known literal), never recomputed the way the code does it.
- Test code is production code. Keep it clean, DRY in helpers but explicit in assertions.

## Anti-patterns
- **Implementation-coupled**: mocking internal collaborators or asserting through a side channel (querying the DB instead of the API).
- **Tautological**: `expect(add(a,b)).toBe(a+b)`, or snapshots nobody checked.
- **Mock everything**: mock only at architectural boundaries (network, clock, randomness, filesystem, third-party APIs). Prefer fakes and in-memory adapters.
- **Fragile timing**: sleeps, real clocks, order-dependent tests.
- **Weakening a test to go green**: changing expectations, adding `skip`, loosening assertions. Never do this without the user's explicit OK.

## Is the suite strong enough?
- Coverage is a floor, not a goal. Uncovered code is untested for sure, and covered code may still be unasserted.
- **Mutation testing** answers "would the tests notice if the code were wrong?" A surviving mutant is a missing assertion. Tools: PIT (Java), Stryker (JS/TS, C#, Scala), mutmut or cosmic-ray (Python), cargo-mutants (Rust), go-mutesting or unclebob/mutate4go (Go), clj-mutate (Clojure).
	- Run it on changed files or differentially, not on the whole repo every time.
	- Kill survivors by adding the assertion the mutant exposes. Mark true equivalents and move on.
- **CRAP** = `CC² × (1 − coverage)³ + CC` flags complex, poorly tested functions. Fix them with tests first and splitting second. Pushing CRAP very low by shattering functions buys coverage but can wreck readability (Uncle Bob's own 2026 experiment). Treat a 30+ score as a must-fix and single digits as good enough.

## With agents
- Ask the agent to show the failing test output before the implementation. That is proof the red step happened.
- Agree on the seams under test before writing tests on anything non-trivial.
- Unit tests alone don't prove the feature. Pair them with acceptance tests (see acceptance-first-agents).
