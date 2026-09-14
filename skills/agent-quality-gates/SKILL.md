---
name: agent-quality-gates
description: Use when agents write most of the code and reviewing it line by line doesn't scale, when setting up CI, hooks or thresholds to keep agent output clean, when agents weaken tests or game metrics, when agent code turns into a big ball of mud, or when the user mentions "CRAP", "mutation testing", "cyclomatic complexity", "coverage gate", "property tests", "no leo el código del agente".
---

# Agent quality gates

**Core principle:** you can't tell an agent to be clean. Measure the cleanliness it produces and make it fix the failures (Robert C. Martin, 2026). Rule files bias agents but they break them anyway. Tests and tools are constraints they can't overturn. Set them up so doing the right thing is the path of least resistance, and cheating is harder than adding a test.

## Gates and the thresholds Martin used
| Gate | Catches | Bar |
|---|---|---|
| Unit + acceptance tests | Wrong behavior | All green before handoff |
| Coverage | Unexecuted code | Above 95%, and still only a floor |
| **CRAP** = `CC² × (1 − cov)³ + CC` | Complex and untested functions | ≤ 8, later ≤ 6 |
| Cyclomatic complexity | Tangled logic | ≤ 6 is fine for agent-maintained code |
| **Mutation testing** | Tests that don't assert | Cover uncovered sites, kill all survivors, differential |
| Module size via mutation-site count | Modules doing several jobs | Warning (he used 50). Split by job, not by number |
| Duplication (fuzzy, structural) | Copy-from-similar | Reduce the easy candidates |
| Dependency rules | Cycles, forbidden edges | Zero |
| Property tests | Edge cases examples miss | Agent classifies each function: property, example, mutation, or too simple |
| Jitter tests | Race conditions | Random delays plus many repeated runs |

Phrase the goal as tool plus threshold: "Run the CRAP tool and bring every function to 6 or below." "Run mutation, cover the uncovered, kill the survivors."

Martin's tools are at github.com/unclebob: crap4clj/go/java, clj-mutate, mutate4go/java, dry4clj/go/java, dependency-checker. He offers them as templates: point your agent at one and have it build the same for your stack. Off-the-shelf alternatives include PIT, Stryker, mutmut, cargo-mutants, jscpd, dependency-cruiser, import-linter and ArchUnit.

## Running them
- **Enforce mechanically** in hooks, CI or a single `verify` script. The agent reads failures only.
- **Mutation is differential** (changed functions only), runs one module at a time, with limited workers. Run heavy tools sequentially.
- **No proxies.** Don't let the agent write its own "complexity counter" in place of the real tool, and don't let it hand-edit tool manifests.
- **Distance prevents cheating.** The agent that writes the tests shouldn't be the one making them pass. Semantic distance (spec → parser → IR → generated tests) puts steps between the agent and a fake green.

## Costs and blind spots
- **Mutation over-stabilizes.** Heavily pinned behavior is hard to change later, and it eats CPU. Pick where you want that rigidity, and have an agent triage which surviving sites matter.
- **CRAP leaves scars.** In Martin's 8-build experiment, forcing CRAP very low raised coverage but hurt readability and didn't improve design.
- **Metrics can be gamed.** Agents invented phony abstractions and shredded code to hit an architecture metric, and CRAP, coverage and complexity all stayed green. Pair gates with a structure view (see agent-architecture-oversight).
- **Tests need their own checks.** CRAP and mutation don't clean test code. Look for vacuous tests (assertions inside conditionals), setup duplication, and assertions that were softened during a change.
- **Right-size.** Often unit tests plus CRAP is enough. Add mutation, acceptance mutation and property tests for code where being wrong is expensive.

Metrics don't see security, performance under load, missing requirements, or what shows on screen. Keep threat review, load tests, acceptance tests from real requirements, and human play-testing.
