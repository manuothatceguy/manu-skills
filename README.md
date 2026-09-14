# skill-factory

My agent skills in one place: Clean Code, Clean Architecture, working with AI agents the way Uncle Bob does it in 2026, plus my own skills for studying, citing and code comment style. They are grouped by the need you have at that moment.

Clean code and agent skill bodies are in English on purpose, because English costs fewer tokens. Descriptions include Spanish trigger words. Heavy material lives in `references/` or `scripts/` and loads only when needed.

## Catalog by need

### I'm writing code
| Skill | When |
|---|---|
| `clean-code-writing` | New functions, classes, endpoints. Names, size, args, errors, comments |
| `tdd-discipline` | Test-first, judging tests, coverage and mutation |
| `comment-style-tools` | Enforcing my comment style mechanically (rules in `config/CLAUDE.md`) |

### I finished a change
| Skill | When |
|---|---|
| `clean-code-review` | Guard pass before commit or merge, including LLM failure modes |

### I have to change existing code
| Skill | When |
|---|---|
| `changing-existing-code` | Refactoring (smell → refactoring) and legacy code without tests (seams, characterization tests) |

### I have to decide structure
| Skill | When |
|---|---|
| `clean-architecture` | Layers, Dependency Rule, boundaries, components, and DDD/hexagonal in its reference |

### I'm working with agents (Uncle Bob 2026)
| Skill | When |
|---|---|
| `lean-agent-harness` | How much orchestration to use, token cost, context pollution, loops |
| `agent-quality-gates` | Measure instead of reading agent code: CRAP, mutation, deps, thresholds |
| `acceptance-first-agents` | Gherkin, QA through the UI and acceptance mutation as the contract |
| `agent-architecture-oversight` | What design stays human, agents that thrash, recommendation overload |
| `auditing-agent-work` | The agent says "done", ran unattended, or went suspiciously fast |

### I'm writing a deliverable that cites sources
| Skill | When |
|---|---|
| `precise-citations` | Any report, PR or answer that cites a file, line, function, config value or CVE |

### I'm studying
| Skill | When |
|---|---|
| `building-course-study-guides` | A full study guide for a whole course from its slide PDFs and past exams |

A caveat Uncle Bob himself makes: he doesn't "trust Skill files any farther than I can throw them". Rules bias agents but don't bind them. Skills guide the agent, and what actually enforces is gates in hooks or CI. `agent-quality-gates` covers that.

## Install

Clone the repo and symlink every skill into Claude Code:

```bash
git clone https://github.com/manuothatceguy/skill-factory.git && cd skill-factory
for s in skills/*/; do ln -sfn "$PWD/$s" ~/.claude/skills/$(basename "$s"); done
```

Only the descriptions load until a skill triggers, so having all of them installed is cheap.

To also use the global comment rules, back up your own `~/.claude/CLAUDE.md` first, then:

```bash
ln -sfn "$PWD/config/CLAUDE.md" ~/.claude/CLAUDE.md
```

On my machine both are symlinks, so editing a file here updates the installed skill at once. After a change: commit and push.

## Third-party skills I use (not vendored)
| Skill | Source | Verdict |
|---|---|---|
| `find-skills` | `npx skills add vercel-labs/skills@find-skills -g -y` | Keep. Finds and installs skills from skills.sh |
| `quiz-maker` | `onewave-ai/claude-skills@quiz-maker` | Weak. A generic template with placeholders. `building-course-study-guides` already writes better exam-specific quizzes |
| `token-efficiency` | project skill in another repo | Not worth it. 8.7K words of always-on rules and dated model advice, which costs the tokens it promises to save. `lean-agent-harness` covers the useful part |
| React Native skills (`vercel-react-native-skills`, `react-native-best-practices`, …) | project skills in the app repo | Keep them in that project, they only matter there |

## Existing skills worth installing as they are

Found on skills.sh, Vercel's skills registry, with `npx skills find`. Install counts were current at the time of the search.

| Skill | Installs | Why |
|---|---|---|
| `mattpocock/skills@tdd` | 901K | Short, strong TDD loop with seams and vertical slices |
| `vercel-labs/agent-skills@vercel-composition-patterns` | 336K | Clean Code for React components (no boolean props, compound components) |
| `vercel-labs/agent-skills@vercel-react-best-practices` | 713K | React/Next performance rules |
| `wondelai/skills@clean-architecture` | 5.8K | Longer version with scoring and references |
| `wondelai/skills@working-with-legacy-code` | 2.2K | Full Feathers treatment |
| `amelnagdy/guard-skills@clean-code-guard` | 3.9K | Very complete AI-code guard, heavier in tokens |
| `ccheney/robust-skills@clean-ddd-hexagonal` | 4.4K | Compact DDD/hexagonal router with references |
| `ciembor/agent-rules-books@clean-code` | 40 | Minimal mini/nano rule files, good for tight budgets |

Don't stack several skills that cover the same need, because they compete for triggering and waste tokens.

## Research
- `research/uncle-bob-ai-timeline.md`: dated timeline of his AI and agent tweets, with short quotes and links. This is the evidence behind the agent skills.
- `research/harvest/harvest.py`: the script that harvested his timeline through api.fxtwitter.com.

Kept local and not published: the full text of the 547 harvested tweets and copies of his repos (see `.gitignore`). Rerun the harvester or clone github.com/unclebob to rebuild them.

## Sources and licenses
The clean code skills are written from scratch, synthesizing Martin (Clean Code, Clean Architecture), Fowler (Refactoring), Feathers (Legacy Code) and Evans/Vernon (DDD), cross-checked against these MIT-licensed skill repos: wondelai/skills, ciembor/agent-rules-books, amelnagdy/guard-skills, pproenca/dot-skills, ccheney/robust-skills, mattpocock/skills, sickn33/agentic-awesome-skills.

The agent skills come from Robert C. Martin's public tweets (Jan to Sep 2026) and his public repos.

## Known debts
- None of the skills were pressure-tested with subagents (the `writing-skills` method). Do it for the ones that misfire.
- `building-course-study-guides` has a 7K-word SKILL.md that loads whole on every trigger. Split the math pipeline, audit and gotcha sections into `references/`.
