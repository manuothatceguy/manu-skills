# Legacy code (Michael Feathers)

Legacy code is code without tests. To change it safely you need tests, and to add tests you often need to change it. Break that loop with the smallest, most mechanical edits possible.

## The legacy change algorithm
1. Identify change points: where the edit must go.
2. Find test points: where you can observe the effect (return value, output, a collaborator call).
3. Break dependencies that block getting the code into a test harness. Use only safe, mechanical edits and lean on the compiler or type checker.
4. Write characterization tests.
5. Make the change, test-first if you can, then refactor.

## Characterization tests
- They document what the code does now, not what it should do.
- Write an assertion you know is wrong, run it, and paste the real value into the expectation.
- For big outputs use a golden master (approval test): capture output for many inputs and diff later.
- Weird behavior you find stays pinned. Fixing it is a separate, explicit decision.

## Seams (places to change behavior without editing that line)
- **Object seam**: pass an interface or subclass instead of the concrete collaborator. This is the most common one.
- **Link/module seam**: swap the import, module or classpath entry in the test build.
- **Preprocessing/config seam**: environment or build-time substitution. Use it as a last resort.

## Adding behavior without tests on the old code
- **Sprout Method/Class**: write the new logic in a new, fully tested function or class and call it from the old code with a one-line change.
- **Wrap Method/Class**: rename the old method, create a new one with the old name that calls the old one plus the new behavior (decorator style).

## Dependency-breaking techniques (the frequent ones)
| Blocker | Technique |
|---|---|
| Constructor creates heavy objects | Parameterize Constructor, Extract and Override Factory Method |
| Static or global call | Introduce Instance Delegator, Replace Global Reference with Getter |
| Singleton | Introduce Static Setter (test-only), then inject |
| Concrete class parameter | Extract Interface, Adapt Parameter |
| Method too big to test | Break Out Method Object |
| Hidden side effect inside logic | Extract and Override Call, Subclass and Override Method |

## Understanding a monster method first
- Sketch effects: which variables and fields each section reads and writes.
- Scratch refactoring: refactor freely to learn the code, then `git restore` everything.
- Look for sensing variables and seams before extracting.

## Agent notes
- Characterization tests first, then refactor, then feature. Three commits, not one.
- Golden-master tests are cheap to generate and a good job to delegate. Review the input set, not the snapshot.
- Mutation testing on the touched file tells you if the characterization net actually catches changes.
