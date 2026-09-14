---
name: changing-existing-code
description: Use when restructuring or modifying existing code that must keep its behavior, including code with no tests, or when the user says "refactor", "refactorizá", "code smell", "technical debt", "legacy code", "no tests", "afraid to touch this", "monster method", "can't get this class under test". Not for greenfield code.
---

# Changing existing code

Refactoring is a change to internal structure that keeps observable behavior: same outputs, same errors, same side effects, same ordering. A bug fix and a refactor are two separate changes, never one commit.

## Step 0: pick the path
- **Tests cover the area** → refactoring loop below.
- **No tests, or tests too weak** → legacy path first, then refactor. Read [references/legacy-seams.md](references/legacy-seams.md).
- Unsure how strong the tests are? Run coverage, and mutation testing if it is available, on the files you will touch. Surviving mutants mean the net has holes.

## Refactoring loop
1. Tests green. Commit.
2. Name the smell you are removing. A refactor without a named smell is churn.
3. Apply one small named refactoring. Run tests. Commit.
4. Repeat. Stop when the requested change becomes easy ("make the change easy, then make the easy change").

Keep each step small enough to revert with no regret. If tests go red, revert instead of debugging a big step.

## Smell → refactoring (most common)
| Smell | Refactorings |
|---|---|
| Long function | Extract Function, Replace Temp with Query, Decompose Conditional |
| Long parameter list / data clumps | Introduce Parameter Object, Preserve Whole Object |
| Duplicated knowledge | Extract Function, Pull Up Method, Slide Statements then extract |
| Feature envy | Move Function to the data it uses |
| Divergent change (one module, many reasons) | Split Phase, Extract Class |
| Shotgun surgery (one reason, many modules) | Move Function/Field, Combine into Class |
| Switch on type repeated | Replace Conditional with Polymorphism, Special Case object |
| Primitive obsession | Replace Primitive with Object (value object) |
| Flag argument | Remove Flag Argument (explicit functions) |
| Message chains | Hide Delegate |
| Mutable shared data | Encapsulate Variable, Separate Query from Modifier |
| Speculative generality | Collapse Hierarchy, Inline Function/Class, remove unused params |
| Comments explaining a block | Extract Function with the comment as its name |

More detail: [references/refactoring-catalog.md](references/refactoring-catalog.md).

## Rules for agents
- Use IDE or language-server rename/extract tools when available. They are cheaper and safer than rewriting text.
- Don't widen scope. If cleanup spreads to unrelated modules, stop at the smallest refactor that makes the requested change safe and list the rest as follow-ups.
- Never change a test's expected values during a refactor. If a test must change, behavior changed.
- Found a bug while refactoring? Note it, finish or revert the refactor, then ask before fixing.
