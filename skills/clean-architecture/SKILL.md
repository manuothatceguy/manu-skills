---
name: clean-architecture
description: Use when deciding where code belongs, when business rules are tangled with frameworks, ORM or HTTP, when modules have dependency cycles, when modeling a complex domain, or when the user says "arquitectura", "capas", "hexagonal", "ports and adapters", "dependency rule", "DDD", "screaming architecture". Not for routine CRUD edits.
---

# Clean Architecture

Architecture is about managing dependencies so business rules don't depend on details. The database, the web, frameworks and devices are details, and details are plugins to the policy.

## The Dependency Rule
Source code dependencies point inward, toward higher-level policy. Inner code never names anything declared in outer code: no classes, functions, data formats or framework types.

```
Frameworks & drivers (web, DB, UI, devices)   ← outermost, most volatile
  Interface adapters (controllers, presenters, gateways)
    Use cases (application rules)
      Entities (enterprise rules)             ← innermost, most stable
```

- When control flow must go outward (a use case saving data), invert it. The inner layer declares the interface (port) and the outer layer implements it (adapter).
- Data crossing a boundary is simple structures shaped for the inner layer. Don't pass ORM rows, HTTP requests or framework objects inward.
- `main` (the composition root) is the dirtiest plugin. It creates the concretes and wires them.

## Placement guide
| Code | Goes in |
|---|---|
| Rule that exists without software (interest calculation, invariants) | Entity / domain |
| One application operation (PlaceOrder, ApproveExpense) | Use case (interactor), which owns the transaction boundary |
| HTTP/CLI/queue → use-case input translation | Controller (thin) |
| Use-case output → view model / JSON | Presenter |
| DB, external API, filesystem | Gateway/adapter implementing a port declared inward |
| DI container, config, wiring | Main |

## Boundaries without over-engineering
- Draw a full boundary only where volatility is likely. Otherwise use a partial boundary (a strategy or facade) and keep the option open.
- **Humble Object**: split hard-to-test code (UI, DB driver, device) into a thin humble part and a testable logic part. Maximize the testable part.
- IO-near adapters must not re-implement a domain question. Call the domain and translate the result.
- Services and microservices are not boundaries by themselves. A shared fat data model across services is a distributed monolith.
- Simple CRUD can stay simple. Team size or file count does not justify DDD layers.
- **Screaming architecture**: the top-level folders name the domain (`billing/`, `scheduling/`), not the framework (`controllers/`, `models/`).

## Components (packages, modules, deployables)
No cycles (ADP), depend toward stability (SDP), stable means abstract (SAP), group what changes together (CCP). For grouping decisions, cycle breaking or instability/abstractness metrics read [references/components.md](references/components.md).

## Enforce, don't hope
Write the allowed dependencies down and check them mechanically in CI: an allowed-dependencies map, import-linter rules, ArchUnit, dependency-cruiser, eslint boundaries, go `depguard`, or Uncle Bob's `dependency-checker` for Clojure. An architecture rule that only lives in a prompt or a wiki erodes, fast when agents write the code.

## Domain-heavy work
If the problem is modeling the business (aggregates, invariants, bounded contexts, events), read [references/ddd-hexagonal.md](references/ddd-hexagonal.md). Load it only for that decision.

## Review checklist
1. Can business rules run in a unit test with no DB, web server or framework?
2. Do all imports in domain and use cases point inward?
3. Could you swap the DB or delivery mechanism without touching use cases?
4. Is the component graph acyclic?
5. Does only `main` instantiate concretes?
6. Does the folder structure scream the domain?
