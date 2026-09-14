# DDD and hexagonal architecture (load only for domain-modeling decisions)

## Which pattern answers which question
| Question | Pattern |
|---|---|
| What language and consistency rules describe the business? | DDD: ubiquitous language, bounded contexts, aggregates |
| Which way do source dependencies point? | Clean / Onion architecture |
| How does the app talk to many interfaces and infrastructures? | Hexagonal: ports and adapters |
| Do reads and writes need different models? | CQRS |
| Must state be rebuilt from history? | Event sourcing |

Use each only when the task needs it. They are tools, not a folder layout to impose.

## Strategic DDD
- **Ubiquitous language**: code names match the words domain experts use inside one context. If they say "policy holder", don't write `Customer`.
- **Bounded context**: a boundary where a model and its language are consistent. The same word (Order) can mean different things in Sales and Shipping, and that is fine.
- **Context map**: how contexts relate (shared kernel, customer/supplier, conformist, anti-corruption layer, open host service, published language).
- Put an **anti-corruption layer** in front of legacy or external models so their concepts don't leak in.

## Tactical DDD
- **Entity**: identity that persists over time. Equality by id.
- **Value object**: immutable, equality by value, validates itself (Money, Email, DateRange). Prefer value objects over primitives.
- **Aggregate**: a consistency boundary with one root. External code references the root only, by id. One transaction changes one aggregate. Keep aggregates small and pick boundaries from real invariants and contention.
- **Domain event**: something that happened, in past tense (`OrderPlaced`). Use it to coordinate aggregates or contexts.
- **Repository**: a collection-like port per aggregate root, declared in the domain or application layer and implemented in infrastructure.
- **Domain service**: an operation that doesn't belong to one entity. Keep it stateless.
- Avoid the anemic model, where getters and setters hold the data and services hold the rules. Put invariants inside the entities and aggregates.

## Hexagonal (ports and adapters)
- **Driving (primary) ports**: what the app offers (use-case interfaces). Driving adapters call them: REST controller, CLI, test.
- **Driven (secondary) ports**: what the app needs (repositories, notifier, clock). Driven adapters implement them: Postgres, SMTP, fake clock.
- Tests are just another driving adapter. In-memory adapters make use cases testable at full speed.

## Consistency across aggregates
- Default to eventual consistency across aggregates through domain events.
- When a requirement truly needs cross-aggregate atomicity, make that tradeoff explicit instead of silently splitting it.
- Use the **outbox pattern** when a DB commit and an external message must succeed or fail together.
- Sagas / process managers coordinate long-running multi-step workflows with compensations.

## Don'ts
- Don't invent business rules to fill a model. Name the missing invariant and ask.
- Don't create a repository per table or a generic `Repository<T>` that exposes query-anything.
- Don't let ORM annotations define the domain model when the model is non-trivial. Map at the adapter.
