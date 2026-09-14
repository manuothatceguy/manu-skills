---
name: agent-architecture-oversight
description: Use when agents build or change a system with several modules, when an agent keeps breaking one thing while fixing another (thrashing, myopia loop), when module boundaries or dependencies drift as agents add code, when an agent's architecture recommendations keep piling up, or when deciding what design work a human keeps while agents write the code.
---

# Architecture oversight with agents

**Core principle:** left alone, agents build large numbers of haphazardly connected local optimizations. They are weak at the big picture and at conceptual encapsulation (Robert C. Martin, 2026). The human thinks globally, without reading line by line, by making structure visible and checkable. Models improved fast during 2026 and by September Martin was debating structure with them like senior engineers. Use them as sparring partners, but keep the final call.

## What the human keeps
- **Partitioning and dependency direction.** When agents over-engineer, propose the simple shape yourself. Martin's example was a 7-component layered design, after an agent shredded the code chasing a metric.
- **Interfaces between parallel streams of work.** Independent stories built by non-collaborating agents don't assemble into a whole.
- **Domain concepts.** Agents miss what a concept means to a human. In one case they signaled "done" with a multi-recipient message instead of "last link in the chain".
- **Testing strategy for risky parts**, such as simulating a workflow state machine with jitter and Monte Carlo runs.
- **New approaches.** Agents rarely have the sideways idea that changes the algorithm.

## See structure without reading code
1. Generate a dependency graph or architecture viewer (an agent can build one) and look at it after each batch.
2. Keep allowed dependencies in a config and fail the build on violations and cycles.
3. For a specific rule ("AI code never reads the omniscient map"), build a small checker script and march through violations with tests green.
4. Ask a **fresh** agent, not the one doing local work, for a global review.
5. Ask for explanations in plain language. Agents coin names from their own code and can conflate two issues under one word.

## Using agent recommendations
Their list never ends. Following all of it gives an over-architected result that is "more like a bunch of dust in the wind". Pick a consistent subset, have the agent write a plan, execute it, then stop.

## Refactor for the agent as reader
- Named intent and shallow nesting help agents as much as humans. A ball of mud costs more time and tokens for the same change.
- For agent-maintained code, functions up to CC 6 and more comments are fine, because agents read and maintain comments. A wrong comment makes them write bugs, so keep comments true or delete them.
- Ask the agent which refactorings would make the code easier for it to work with.

## When the agent thrashes (fix X breaks Y breaks Z breaks X)
1. Stop and revert to the last green commit.
2. Get a new plan, not one from the confused session.
3. Cut the job into pieces, which usually means refactoring first.
4. For long cause-and-effect chains, walk step by step with probes and logs. Reasoning breaks down past some chain length.
5. For big restructurings, work in phases with acceptance tests frozen, and run the full suite plus a manual check after each phase.

## Checklist per batch
- New component edges allowed? Any cycle?
- Business logic in an adapter, controller or UI?
- A module picked up a second job?
- Can you explain the component graph in two minutes?
