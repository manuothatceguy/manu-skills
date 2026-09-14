# Component principles and metrics

A component is the unit of release or deployment: a jar, gem, npm package, Go module, DLL, or a top-level namespace that you treat as one.

## Cohesion (what goes inside)
- **REP, Reuse/Release Equivalence**: what you reuse you release together, with one version number.
- **CCP, Common Closure**: gather classes that change for the same reasons at the same times. Separate those that change for different reasons. Most apps should favor CCP early.
- **CRP, Common Reuse**: don't make users depend on classes they don't need. Separating them avoids needless redeploys.

The three pull against each other. Early in a project lean on CCP (developability). As the project matures and others reuse it, shift toward REP and CRP.

## Coupling (between components)
- **ADP, Acyclic Dependencies**: no cycles in the component graph. Break a cycle by applying DIP (an interface in the depended-on side, implemented by the other) or by extracting a new component both depend on.
- **SDP, Stable Dependencies**: depend in the direction of stability. A volatile component must not be depended on by a stable one.
- **SAP, Stable Abstractions**: a component should be as abstract as it is stable. Stable components hold interfaces and policy. Unstable ones hold concrete details.

## Metrics
- Fan-in `Ca`: classes outside that depend on classes inside.
- Fan-out `Ce`: classes inside that depend on classes outside.
- Instability `I = Ce / (Ca + Ce)`. 0 is maximally stable, 1 is maximally unstable.
- Abstractness `A = Na / Nc` (abstract classes and interfaces over total classes). In dynamic languages count real indirection only (protocols, multimethods, interfaces), not config.
- Distance from the main sequence `D = |A + I − 1|`.
	- Zone of pain (A≈0, I≈0) means concrete and heavily depended on, hard to change. A DB schema or a stable util lib may be acceptable there.
	- Zone of uselessness (A≈1, I≈1) means abstractions nobody depends on, dead abstractions.
	- A healthy threshold is around D ≤ 0.3.

## Practical checks
- Generate the component graph and fail CI on cycles and on edges not listed in an allowed-dependencies map.
- Review edges when a new component is added, not after the graph is a hairball.
- A cycle discovered late means you should first extract the shared concept, and only then move code.

Tools: dependency-cruiser (JS/TS), import-linter (Python), ArchUnit / jdepend (Java), NDepend (.NET), go-arch-lint / depguard (Go), unclebob/dependency-checker (Clojure, reports I, A, D and zones).
