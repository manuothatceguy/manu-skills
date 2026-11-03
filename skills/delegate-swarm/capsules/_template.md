---
name: <skill-or-repo-name>
source: <which skill or doc this was distilled from>
---
One or two sentences a worker always needs: what this repo is, the one convention everything depends on.

## @section-name
- Imperative rules only, each one changes how a worker edits files in its scope.
- Formats with one concrete example (`<type>(<scope>): <what>` → `add(api): login endpoint`).
- Forbidden things specific to this repo.

## @another-section
- Keep each section under ~500 characters; select sections per task with `name#a,b`.

<!--
Leave OUT of a capsule:
- Session procedures: pulling, catching up, reading indexes, writing session notes, pushing. The orchestrator does those.
- Git workflow and commit rules: workers never run git; the orchestrator sets the commit message per task.
- Background, history, rationale. A worker needs the rule, not why it exists.
- Anything a task's own `context` already says.
Check size with: swarm capsule <name>#<sections>
-->
