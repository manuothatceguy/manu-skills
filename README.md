# manu-skills

My personal agent skills in one place: delegating to cheap coding agents, designing and linting skills, my memory vault, studying, precise citations, and my code comment style. They are grouped by the need you have at that moment.

Heavy material lives in `references/` or `scripts/` and loads only when needed.

## Catalog by need

### I'm writing code
| Skill | When |
|---|---|
| `comment-style-tools` | Enforcing my comment style mechanically (rules in `config/CLAUDE.md`) |

### I'm delegating work to cheap agents
| Skill | When |
|---|---|
| `delegate-swarm` | Split work into small verifiable tasks and fire them at free OpenCode workers in parallel worktrees, one PR per task (`swarm` CLI in `scripts/`) |

### I'm writing or reviewing a skill
| Skill | When |
|---|---|
| `designing-skills` | Designing a new skill or auditing one an agent generated: dated prompting, leaked context, trivialities and agentic antipatterns, with a `lint_skill.py` that flags the mechanical ones |

### I'm working in my memory vault
| Skill | When |
|---|---|
| `memory-vault` | Catching up on a project through master files, running jobs, triaging the inbox, writing daily notes, syncing with git |
| `memory-vault-setup` | Scaffolding the vault, or adding a project, folder, asset, job or job step with its master file |

### I'm writing a deliverable that cites sources
| Skill | When |
|---|---|
| `precise-citations` | Any report, PR or answer that cites a file, line, function, config value or CVE |

### I'm studying
| Skill | When |
|---|---|
| `building-course-study-guides` | A source-grounded guide from course materials and past exams; routes Anki decks to `active-recall-anki` |
| `active-recall-anki` | Focused Basic or Cloze cards from study material, with a TSV syntax validator |

## Install

Keep this checkout as the source of truth. Codex discovers user skills in `~/.agents/skills`; Claude Code uses `~/.claude/skills`. Both can use symbolic links to the same skill folders.

From the repository root, install missing links for Codex without replacing existing entries:

```bash
mkdir -p "$HOME/.agents/skills"
for skill in "$PWD"/skills/*; do
  target="$HOME/.agents/skills/${skill##*/}"
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    ln -s "$skill" "$target"
  fi
done
```

For Claude Code, use the same procedure with `~/.claude/skills`. Inspect existing entries instead of overwriting name collisions. Codex normally detects skill updates automatically; start a new session if the catalog is stale.

`delegate-swarm` also ships the `swarm` CLI. Link it onto your PATH with `ln -sfn "$PWD/skills/delegate-swarm/scripts/swarm.py" "$HOME/.local/bin/swarm"`. Its `install.sh` copies the skill instead of linking it, so skip it when installing from this checkout; if an older copy already sits in `~/.claude/skills/delegate-swarm`, remove it and link this folder.

`config/CLAUDE.md` holds the shared comment rules. Back up existing global instructions before linking it as `~/.codex/AGENTS.md` or `~/.claude/CLAUDE.md`. The filename is historical; the rules apply to both runtimes. Project-specific guidance belongs in the project's own `AGENTS.md`.

The course-guide skill uses available runtime tools and models. Its detailed guidance lives in `references/`; the MathML builder takes fragment paths and an output path on the command line. Comment cleanup uses Python tokens and leaves docstrings for manual review.

The repository includes an opt-in Git pre-commit hook for skill metadata, local references, and staged study artifacts. Enable it in this checkout with `git config --local core.hooksPath .githooks`. Run `python3 scripts/validate_repo.py --all` for a manual repository check, or pass a guide HTML or deck TSV path directly. The hook checks mechanical errors; source accuracy and card quality still need review. Git hooks do not run inside Codex or Claude tool calls.

## Third-party skills I use (not vendored)
| Skill | Source | Verdict |
|---|---|---|
| `find-skills` | `npx skills add vercel-labs/skills@find-skills -g -y` | Keep. Finds and installs skills from skills.sh |
| `quiz-maker` | `onewave-ai/claude-skills@quiz-maker` | Optional. The local study skills cover cards and course-specific practice; compare output quality for the task |
| `token-efficiency` | project skill in another repo | Not worth it. 8.7K words of always-on rules and dated model advice, which costs the tokens it promises to save |
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
- `research/uncle-bob-ai-timeline.md`: dated timeline of Robert C. Martin's AI and agent tweets, with short quotes and links.
- `research/harvest/harvest.py`: the script that harvested his timeline through api.fxtwitter.com.

Kept local and not published: the full text of the 547 harvested tweets and copies of his repos (see `.gitignore`). Rerun the harvester or clone github.com/unclebob to rebuild them.

## Known debts
- Most skills have not been behavior-tested in Codex. The migration checks cover portability and the Python comment helper, not every workflow.
- The MathML builder requires pandoc; verifying exam coverage and worked answers still requires checking the course sources.
