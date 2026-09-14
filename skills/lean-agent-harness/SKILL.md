---
name: lean-agent-harness
description: Use when deciding how to run coding agents on a task (one agent, planner plus implementer, subagents, pipelines, swarms, orchestration), when token usage or cost is too high, when agents drift, stall in loops, duplicate each other's work or pollute each other's context, or when the user mentions "harness", "orchestration", "multi-agent", "subagents", "consume muchos tokens".
---

# Lean agent harness

**Core principle:** use the least orchestration that gets the job done, and push everything deterministic into scripts. Every role, handoff and protocol costs tokens and adds failure modes.

Robert C. Martin's path through 2026 went like this. He started with one agent, then used a planner plus an implementer, then built 3-, 4- and 6-agent assembly lines (swarm-forge), then an elaborate squad he scrapped. In September he wrote that better models had "obviated" his harness, and that once he stopped using it his token consumption "has fallen by a huge factor". He kept unit tests, CRAP and mutation testing.

## Pick the smallest level that works
| Level | Setup | Use when |
|---|---|---|
| 1 | One agent, a significant task, a few guidelines, deterministic gates | Default. Features, debugging, UI tweaks, performance |
| 2 | Planner session (not allowed to edit source) plus implementer | You wait on the agent more than you plan |
| 3 | Short assembly line, for example coder → cleaner, or specifier → coder → refactorer → architect | A long batch of stories that need heavy testing and hardening |
| 4 | Leader plus many roles | Rarely pays. Martin's elaborate version "became unworkable" |

- **Match process to problem.** His six-agent line took 67 minutes and 1,558 lines to build hello world, 24 of them the app.
- **Oscillate.** Run a line for a batch of features, drop to one agent for tweaks and debugging, then do a hardening pass.
- **Assembly line, not a parallel crowd.** Six agents in a line worked. Six in parallel on independent stories went badly: collisions, merges, no shared design. If work must run in parallel, design the interfaces between the streams first.

## Token rules
- **Everything deterministic goes in a script**: queues, ordering, parsing, metrics, merges, commit ids, and a state machine that says what comes next. Agents do deterministic procedures and long loops badly.
- **Build a tool instead of grinding.** Don't burn tokens on what the agent is bad at, such as matching delimiters or re-translating specs each run.
- **Gate output shows failures only.** A passing tool prints one line.
- **Narrow, short-lived agents.** After repeated compactions, roles blur and agents forget handoffs. Tear down and restart with fresh context when behavior gets odd.
- **Pass artifacts, not narration.** Send commit ids through a helper (agents mangle long hashes), files and failing tests. If one agent tells another which tools it ran, the other starts running them too.
- **Rules bias behavior, they don't bind it.** The latest instruction dominates, so rules at the top of CLAUDE.md or AGENTS.md fade. Keep instruction files short and delete leftovers, because some agents read other tools' rule files.
- **Use a watchdog for loops, not willpower.** Detect inactivity and nudge with: "What should you be doing right now?"

## Measure before adding structure
1. Run the task at level 1 and record tokens, wall time and gate results.
2. Add one layer only for a failure you actually saw.
3. Compare tokens per finished task, and remove any layer that doesn't pay.

In June Martin estimated a six-pack "should not be vastly more" tokens than one agent. In September his usage said otherwise. Measure, don't estimate.

## Red flags
- Handoff messages longer than the diff.
- Several agents reading the same files for one task.
- A reviewer role re-running what CI already runs.
- Startup protocol docs over a few hundred lines.
- An agent reasoning out what a tool would compute.
- Orchestration built before one agent was tried on the task.
