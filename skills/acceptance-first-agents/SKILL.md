---
name: acceptance-first-agents
description: Use when an agent will implement features or stories and you need proof they do what was asked without reading the code, when writing Gherkin/Given-When-Then scenarios or QA procedures for agent work, when a new feature keeps breaking old ones (fragility), or when agent tests pass but the feature is wrong or not wired to the UI.
---

# Acceptance-first work with agents

**Core principle:** the human owns *what* the system must do, through tests a human can read. The agent owns *how*. Agents "fix" unit tests freely, and thousands of deep unit tests are unreadable for a person. Acceptance tests describe visible behavior, and the agent may not edit them without approval (Robert C. Martin, Feb 2026, after fighting fragility).

## Three threads of tests
| Thread | Written by | Human role |
|---|---|---|
| **Acceptance** (Gherkin, Examples tables) | Specifier agent, from the story | Review or spot-check before code |
| **QA procedures** (outside-in, as a human would run them, then scripted to drive the real UI) | Specifier agent | Spot-check by criticality |
| **Unit tests** | Coder agent | Measured, not read (coverage, CRAP, mutation) |

For the agent to deviate from the desired behavior, it would have to change several of these files at once. Plus true manual play-testing: when Martin play-tested one swarm-built game he found 10 bugs, half of them his own spec errors.

## Workflow
1. Write an informal spec by hand. Add a **statics** document (wireframes, formulas, intent), because Gherkin covers dynamics only.
2. An agent turns it into smaller tasks. Review them.
3. For each task, write Gherkin and prune duplicate steps. Spot-check.
4. Run the scenarios and **confirm they fail**.
5. Write unit tests and code until the scenarios pass, then run the gates (see agent-quality-gates).
6. Run the QA procedure through the UI, then play-test.

## Rules
- The agent doesn't change a scenario without explicit OK. When a new feature legitimately changes a rule, old scenarios are updated under supervision.
- **Steps state external observables only.** Agents push implementation details into steps to make them easier to wire. When that happens, have an agent rewrite the steps in domain language.
- Prefer Scenario Outlines with Examples tables. They read well and are easy to mutate.
- Make randomness controllable in tests, **and** check that the real app is wired to real randomness.
- **Build the translator once.** Having the agent translate scenarios into tests by hand every run cost enormous tokens. A parser → JSON IR → generator is a tool.
- **Verify the translator.** It can generate tests that pass while testing nothing. Acceptance mutation catches that: mutate the Examples values in the IR and expect failures (github.com/unclebob/Acceptance-Pipeline-Specification).

## QA through the UI
Agents can't see the screen. A QA agent allowed to call the model's API will pass while the feature isn't connected to buttons or keys. Force QA scripts to use real UI events and add a checker that rejects API calls in them. UI tests are fragile, but agents don't mind rewriting them.

## Just enough spec
Spec-driven development risks big design up front. Write only enough scenarios for the stories in this iteration, co-author them with the agent, and keep final approval with the human. Commit them to source control and evolve them with the product.

## Right-size it
For small changes, unit tests plus CRAP are often enough. Use the three threads for larger projects and features where being wrong is expensive (see lean-agent-harness).
