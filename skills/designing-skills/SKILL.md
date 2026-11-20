---
name: designing-skills
description: Use when creating a new skill, reviewing or rewriting an existing one, auditing a skill or prompt set that an agent generated, or when a skill triggers at the wrong time or gets ignored. Triggers include "diseñar una skill", "revisar esta skill", "skill generada por un agente", "prompt viejo".
---

# Designing skills

**Core principle:** a skill is context the agent pays for on every load, so each line has to change what the agent does compared with its default. A skill an agent wrote is a draft. It carries residue from the session that produced it, and it is ready only after one review pass and one real run.

Pick the branch: a new skill starts at step 1, an existing or generated skill starts at step 5.

## Design

1. **Name the gap.** Write down what the agent got wrong or did not know without the skill, from a run you observed. Collect two or three prompts that should trigger the skill and one near-miss that should not. Done when each planned section traces to an observed failure. If the agent already does the task well without help, stop here, because the skill would be all cost.
2. **Choose invocation.** Keep the description model-facing when the agent has to reach the skill on its own. Make the skill user-invoked when a person will always call it by name, which frees the always-loaded description.
3. **Write the description as a trigger.** State the situations that should load the skill, in the words the user actually types and in every language they prompt in. One trigger per distinct situation. Leave the workflow to the body, because an agent that reads a workflow summary in the description acts on the summary and skips the body.
4. **Write the body for a capable reader with zero context.** Give ordered steps when order matters and flat reference when it does not. End each step on a condition the agent can check. Attach the reason to each rule so the agent can handle the case the rule did not foresee. State the behavior you want rather than the one you fear. Keep one short, generic example per pattern. Move material that only some paths need into a sibling file behind a one-line pointer that says when to read it, and move anything deterministic into a script.

## Review

5. **Lint.** Run `scripts/lint_skill.py <skill-dir>` from this skill's directory. It prints `file:line` candidates for the mechanical smells below. Each one is a question to answer, and the answer may be that the line stays.
6. **Read every line against the catalog.** For each sentence, ask what the agent would do if the sentence were gone. Delete the whole sentence when the answer is "the same thing". Done when every remaining line has survived that question and every catalog row has been checked.
7. **Run it.** Give a fresh agent the prompts from step 1 with only the skill loaded. Check that it triggers on the hits, stays quiet on the near-miss, and that the output beats the run without the skill. Fix what you observed and rerun. Done when the gap from step 1 is closed in a run you watched.

Report a review as a list of findings, each with the line, the smell and the proposed rewrite, then apply the rewrites the user accepts.

## Smell catalog

<!-- skill-lint: off -->

### Dated prompting
These habits compensated for weaker models. Current models follow plain instructions, and the old emphasis now causes overreaction or adds nothing.

| Smell | Signal | Fix |
|---|---|---|
| Persona opener | "You are an expert…", "Act as a senior…", "sos un experto en…" | Delete it and give the knowledge the expert would have |
| Shouting | CRITICAL, MUST, NEVER, "IMPORTANT:" on ordinary rules | Lowercase plus the reason. Keep emphasis for the one rule that failed in testing |
| Incantations | "think step by step", "take a deep breath", tips, threats, "do not hallucinate" | Delete, or replace with a concrete check such as "quote the line you rely on" |
| Rigid template for a judgment task | A mandatory output skeleton with no stated consumer | Describe what the reader of the output needs |
| Example as mold | One long, specific example the agent will copy | Short generic example, or several that differ |

### Leaked context
Residue from the session, machine or project where the skill was generated. It misfires everywhere else.

| Smell | Signal | Fix |
|---|---|---|
| Hardcoded location | Absolute paths, home directories, usernames, hostnames, ports | Path relative to the skill directory, or tell the agent how to find it |
| Session narrative | "as discussed", "the user asked", "in this session", "the bug we fixed" | Rewrite as a standing instruction or delete |
| One case promoted to a rule | A rule naming one file, ticket, customer or error message | State the general condition, keep the case as a short example at most |
| Stale pins | Dates, version numbers, model names, counts, "the new API" | Tell the agent where to look up the current value |
| External reference | URLs, "see the docs", files outside the skill, tools assumed to be installed | Inline the fact that matters, bundle the file, or state the requirement and the fallback |
| Foreign project knowledge | Stack, team or naming conventions of one repo in a general skill | Move it to that project's instructions file |

### Trivialities
Lines the agent obeys with or without the skill.

| Smell | Signal | Fix |
|---|---|---|
| Default behavior | "write clean code", "be thorough", "handle errors", "follow best practices" | Delete, or replace with the specific non-obvious standard |
| Explaining the known | What git, REST or a unit test is | Delete |
| Restating the environment | Lists of scripts, commands or folders the agent can read itself | Keep only the convention no file reveals |
| Human-facing sections | Installation, changelog, author, license, a "when to use" section that repeats the description | Move to a README or delete |
| Duplication | The same rule in two sections or two files | One home, a pointer from the other |

### Agentic antipatterns
Shapes that make agent runs unpredictable.

| Smell | Signal | Fix |
|---|---|---|
| Workflow in the description | The description summarizes steps | Triggers only |
| No finish line | "until satisfied", "as needed", steps with no check | A checkable, exhaustive condition per step |
| Trust without verification | The skill ends at "done" with no test, diff or run | Add the step that proves the result |
| Steering by prohibition | Long "don't" lists | Name the target behavior. Keep a prohibition only for a hard guardrail, next to its positive |
| Rule without a reason | Bare imperatives | Add the reason in a clause |
| Flat wall | Dozens of equal-weight bullets | Order by when they apply, push the rare ones behind a pointer |
| Wrong freedom | A script-like recipe for a judgment task, or loose prose for a fragile operation | Match strictness to how costly a mistake is |
| Several jobs | One skill covering unrelated triggers | Split by trigger |
| Unbounded action | Loops with no stop condition, destructive or outward-facing actions with no confirmation | Add the bound and the confirmation |
| Deep nesting | A reference file that points to more reference files | Every file reachable in one hop from the main file |
| Sprawl | A body so long that attention thins | Disclose and split until each path carries only what it needs |

<!-- skill-lint: on -->
