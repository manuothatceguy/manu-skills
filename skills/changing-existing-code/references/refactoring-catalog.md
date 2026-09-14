# Refactoring catalog (Martin Fowler, 2nd ed.), condensed

Each entry says when to use it and how to do it safely. Run tests after every step.

## Composing functions
- **Extract Function**: a fragment needs a comment to explain it, or it's reused. Move it into a function named by intent. Pass what it reads and return what it changes.
- **Inline Function**: the body is as clear as the name, or the indirection is useless. Replace calls with the body.
- **Extract Variable / Inline Variable**: name a complex expression, or remove a name that adds nothing.
- **Replace Temp with Query**: a temp is computed once and read many times. Turn it into a function so extraction gets easier.
- **Split Variable**: one variable is assigned for two purposes. Use two variables.
- **Replace Function with Command**: a function is huge with many locals. Turn it into an object with fields, then extract methods.

## Moving features
- **Move Function / Move Field**: it uses another module's data more than its own (feature envy).
- **Extract Class**: a class has two clusters of data and behavior that change separately.
- **Inline Class**: a class does too little.
- **Hide Delegate**: clients navigate `a.b().c()`. Add a method on `a`.
- **Remove Middle Man**: a class only forwards calls.
- **Split Phase**: code does two different things in sequence (parse then compute). Separate them with an intermediate data structure.

## Organizing data
- **Replace Primitive with Object**: a string or number carries rules (money, email, range).
- **Encapsulate Variable / Encapsulate Collection**: shared mutable data. Route access through functions and return copies.
- **Change Reference to Value**: an object is small and immutable in spirit.
- **Replace Derived Variable with Query**: a stored value can be computed.

## Simplifying conditionals
- **Decompose Conditional**: extract condition, then-branch and else-branch into named functions.
- **Consolidate Conditional Expression**: several checks give the same result. Combine them into one named predicate.
- **Replace Nested Conditional with Guard Clauses**: handle special cases first and return early.
- **Replace Conditional with Polymorphism**: the same switch on type appears in several places.
- **Introduce Special Case (Null Object)**: many callers check for the same special value.
- **Introduce Assertion**: code assumes a condition. Make it explicit.

## APIs
- **Separate Query from Modifier**: a function returns a value and has side effects.
- **Parameterize Function**: several functions differ only by a literal.
- **Remove Flag Argument**: a boolean selects behavior. Create one explicit function per case.
- **Preserve Whole Object / Introduce Parameter Object**: callers unpack an object, or the same params travel together.
- **Replace Constructor with Factory Function**: construction needs a name or returns subtypes.
- **Replace Error Code with Exception**, or the reverse for expected conditions.

## Inheritance
- **Pull Up / Push Down Method or Field**: behavior belongs to the parent or only one child.
- **Replace Subclass with Delegate** / **Replace Superclass with Delegate**: inheritance is used for reuse, not for substitutability. Prefer composition.
- **Collapse Hierarchy**: parent and child are no longer different.

## Safe sequence for a big function
1. Characterize or verify tests.
2. Slide Statements to group related lines.
3. Extract Function for each group, one at a time.
4. Replace Temp with Query where temps block extraction.
5. Decompose Conditional and add guard clauses.
6. Move the extracted functions to the data they envy.
