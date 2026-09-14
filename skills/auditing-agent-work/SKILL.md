---
name: auditing-agent-work
description: Use when an agent reports a task as done, after an agent ran unattended (AFK, overnight, long swarm run), when an agent finished suspiciously fast, when tests or assertions were changed during a task, when inputs were missing, or when you can't tell what an agent actually did.
---

# Auditing agent work

**Core principle:** agents declare success early, skip steps, and take the path of least resistance. Robert C. Martin caught agents skipping QA tests, inventing missing data and copying results instead of measuring. Agents also find many of their own mistakes when made to look. Auditing is cheap, so always do it before accepting work.

## The audit loop
1. Ask the agent to **audit its recent work** against the task or plan.
2. Read the answer carefully, **especially the gaps and what was NOT done**.
3. Have it **write the gaps to `issues.md`** before working on them. Context compaction loses lists that only live in chat.
4. Go through the gaps one by one and turn each into a real issue, or discard it.
5. Have it fix the issues.
6. Audit the fixes, then repeat.

Feed the same file from your own runs of the app: see a problem, have an agent diagnose it and add it to `issues.md`.

## Prompts that work
- "Read the plan and check it against the code."
- "What did you just do?"
- "What should you be doing right now?"
- "Did you run every test and QA procedure? List the ones you skipped."
- "List every assertion you changed. Classify each as improperly softened, broadened but valid, or required by the change, and justify it."
- "Explain this in plain language and define any names you introduced."
- Before a compaction: "Write down notes on what you just did."

## Suspicion triggers
| Signal | Check |
|---|---|
| Finished faster than expected | Did the gates actually run? Read their output, not the summary |
| Tests green after edits to tests | Diff the test changes. Look for loosened asserts and skips |
| Missing input files or data | Did it stop and ask, or invent values? |
| Results or reports produced | Were they measured this run, or copied from an earlier run? |
| QA passed | Did it drive the real UI, or call APIs? |
| "Flaky, rerunning" or a long run cut short | Real flakiness, or impatience? |
| Files recreated after a bad revert | Content from memory, not guaranteed. Diff against git |
| "You allowed this yesterday" | Big contexts remember old exceptions. Restate the bar |

## Cross-checks
- **A second agent or model**: one writes bug reports and another fixes them, or one prosecutes and another defends.
- **Review session transcripts** with another agent to find where the first one got confused, then fix the prompt or tool that caused it.
- **Skim diffs as they scroll** to steer early. Spot-check code, Gherkin and QA procedures in proportion to how critical they are.
- **Play-test yourself.** Agents don't understand obvious user expectations.

## When you find a violation
An apology or a promise is not a fix, because rules bias agents but don't bind them. Turn the violation into a constraint: a test, a checker script, or a gate that fails. Then rerun the audit.
