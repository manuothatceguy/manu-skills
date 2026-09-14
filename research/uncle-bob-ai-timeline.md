# Uncle Bob on AI and agents: dated timeline (2026)

Source for the agent skills. Every entry was checked against the tweet JSON (api.fxtwitter.com) or the repo. Quotes are short. Read the link for full context.

## January: one agent, then two, then three
- 2026-01-11 · Says he is not "vibe" coding, he is supervising a powerful tool like he has for 50 years. [2010358336437256455](https://x.com/unclebobmartin/status/2010358336437256455)
- 2026-01-22 · Asks Claude whether refactorings help it read code. It cites named intent, less working memory and fewer paths (cyclomatic complexity). [2014301148555935836](https://x.com/unclebobmartin/status/2014301148555935836)
- 2026-01-22 · Claude codes faster and holds more detail, but "cannot hold the big picture". It doesn't foresee the disaster it creates. [2014311028972994582](https://x.com/unclebobmartin/status/2014311028972994582)
- 2026-01-27 · Two Claude windows, one plans (rules forbid source changes) and one edits. Manual pull/push between them. [2016166910698696916](https://x.com/unclebobmartin/status/2016166910698696916)
- 2026-01-28 · With three agents "Claude is waiting for me". The bottleneck is planning. [2016544529826926618](https://x.com/unclebobmartin/status/2016544529826926618)
- 2026-01-30 · Claude "burned a gazillion tokens" recreating deleted files. [2017325684562039178](https://x.com/unclebobmartin/status/2017325684562039178)

## February to April: tools and a three-agent network
- 2026-02-24 · Publishes a Claude skill for the CRAP metric (crap4clj). [2026407185807245659](https://x.com/unclebobmartin/status/2026407185807245659)
- 2026-03-10 · "Vibe coding is not the same as disciplined agentic development." [2031396174490472638](https://x.com/unclebobmartin/status/2031396174490472638)
- 2026-03-30 · Tangled logic where fixing X broke Y and so on, even with unit and acceptance tests. Codex did marginally better. [2038712155835334920](https://x.com/unclebobmartin/status/2038712155835334920)
- 2026-04-14 · Doesn't review agent code. Measures coverage, dependency structure, cyclomatic complexity, module sizes, mutation. [2044114698451476492](https://x.com/unclebobmartin/status/2044114698451476492)
- 2026-04-18 · Architect (Claude) writes plans and acceptance tests, coder (Codex) does unit tests and implementation, reviewer (Codex) refactors using coverage, CRAP, mutation and dependency tools. [2045477573535142212](https://x.com/unclebobmartin/status/2045477573535142212)
- 2026-05-14 · Cancels his Claude account, using Codex. [2054970327592042661](https://x.com/unclebobmartin/status/2054970327592042661)

## June to August: the harness era
- 2026-06-05 · Doesn't use agents to interpret JSON/Gherkin or for static analysis ("token use would be embarrassingly high"). Uses purpose-built tools. Multiple agents are a way to manage context windows. Information hiding keeps agents in their lanes. [2062873889647054955](https://x.com/unclebobmartin/status/2062873889647054955), [2062875491082637512](https://x.com/unclebobmartin/status/2062875491082637512)
- 2026-07-23 · Doesn't read any agent code. "Extreme constraints": unit tests, gherkin, QA procedures, metrics, mutation, coverage. [2080257779395154409](https://x.com/unclebobmartin/status/2080257779395154409)
- 2026-07-29 · "You can't tell an agent to be clean. You have to measure the cleanliness." [2082497764223492161](https://x.com/unclebobmartin/status/2082497764223492161)
- 2026-08-04 · Squad leader plus many roles. The FSM, simulator and Monte Carlo testing were his idea, not the agents'. [2084638878548304046](https://x.com/unclebobmartin/status/2084638878548304046)
- 2026-08-05 · Agents are transient, born for one small task, then die. No role leakage seen. [2084975239369269462](https://x.com/unclebobmartin/status/2084975239369269462)
- 2026-08-08 · A complex harness on a simple problem produces overkill. [2086140127739342935](https://x.com/unclebobmartin/status/2086140127739342935)
- 2026-08-11 · Models don't follow rules well over time, so you need deterministic tools. Three threads of tests, and he spot-checks acceptance and QA. [2087181971390595298](https://x.com/unclebobmartin/status/2087181971390595298)
- 2026-08-19 · The highly elaborate squad scheme "became unworkable". Scrapping it for a simpler one. [2090068337489306092](https://x.com/unclebobmartin/status/2090068337489306092)
- 2026-08-23 · Some overhead. He wouldn't use it for simple work, only for large tasks. [2091659417213145157](https://x.com/unclebobmartin/status/2091659417213145157)

## September: the pivot
- 2026-09-02 · swarm-forge commits say to split modules that mix jobs, not to chase a mutation-site count, and that adapters call domain answers.
- 2026-09-07 · "I'm starting to think that I'm over constraining them. Perhaps vastly over constraining them." [2096994914185662851](https://x.com/unclebobmartin/status/2096994914185662851)
- 2026-09-11 · "Time to rethink this." Models got so good the harness was obviated. Debates with Grok and Codex like senior engineers. Keeps unit tests, CRAP, mutation ("they can leave scars"). Harnesses "should not treat agents as components within a software design." [2098432570887217520](https://x.com/unclebobmartin/status/2098432570887217520)
- 2026-09-12 · Video "Morning Bathrobe Rant: Rethinking Harnesses". [2098744156709441896](https://x.com/unclebobmartin/status/2098744156709441896)
- 2026-09-14 · "Since I stopped using my harness, my token consumption has fallen by a huge factor. That harness was massively inefficient." [2099530728455217475](https://x.com/unclebobmartin/status/2099530728455217475)

## Experiments and repos
- negative-test-experiment: 8 builds of Hunt the Wumpus. "CRAP raises coverage and wrecks cleanliness. It does not improve design."
- swarm-forge: tmux, git worktrees, constitution prompts, handoff scripts, packs (two-pack to six-pack), platoon brainstorm.
- Acceptance-Pipeline-Specification: Gherkin → JSON IR → generated tests, plus acceptance mutation.
- Tools: crap4clj, crap4go, clj-mutate, mutate4go, dry4go, dry4java, dependency-checker, speclj-structure-check.

## More from the full harvest (547 AI tweets, Jan to Sep 2026)
Full text of all of them is in `ai-tweets-2026.md`.
- 2026-02-03 · Fragility: the AI "fixes" unit tests. Fix: acceptance tests that describe visible behavior and that the AI can't edit. [2018706386058649843](https://x.com/unclebobmartin/status/2018706386058649843)
- 2026-02-05 · Claude fills GWT steps with implementation details. He fires up an agent to rewrite them into external observables. [2019429219617456389](https://x.com/unclebobmartin/status/2019429219617456389)
- 2026-02-12 · SDD risks big design up front. Just enough specs per sprint, with human approval "ferociously defended". [2021998958579794052](https://x.com/unclebobmartin/status/2021998958579794052)
- 2026-02-15 · TDD micro steps are inefficient for AIs. The principles stay, the techniques change. [2023158252700066287](https://x.com/unclebobmartin/status/2023158252700066287)
- 2026-02-24 · "Don't burn tokens on fixing things that the AI isn't good at fixing." Have it build a tool. [2026328052825772186](https://x.com/unclebobmartin/status/2026328052825772186)
- 2026-03-06 · Codex shredded the code chasing architecture conformance while tests stayed green. He built a viewer and proposed a simple 7-component layered design. [2030012233342750746](https://x.com/unclebobmartin/status/2030012233342750746)
- 2026-03-12 · Workflow: scenarios first, CRAP ≤ 8, differential mutation one module at a time with 3 workers. Module limit of 50 mutation sites. [2032145477786099912](https://x.com/unclebobmartin/status/2032145477786099912), [2032101258438283470](https://x.com/unclebobmartin/status/2032101258438283470)
- 2026-03-14 · Quicksilver: rules bias AIs but don't constrain them. Overconstrain with tests and partition into small units. [2032798591501078576](https://x.com/unclebobmartin/status/2032798591501078576)
- 2026-03-15 · The AI focuses on the last instruction. Rules high in CLAUDE.md or AGENTS.md get less attention. [2033246552651649097](https://x.com/unclebobmartin/status/2033246552651649097)
- 2026-03-21 · Container analogy. Coverage leaves holes, mutation plugs them but over-stabilizes the shape. [2035338639719227823](https://x.com/unclebobmartin/status/2035338639719227823)
- 2026-04-14 · "Distance": one AI writes tests and another passes them. Semantic distance via parser, IR and generator. [2044112087174267368](https://x.com/unclebobmartin/status/2044112087174267368)
- 2026-05-06 · "I don't trust Skill files any farther than I can throw them." [2052005431975752176](https://x.com/unclebobmartin/status/2052005431975752176)
- 2026-05-22 · Phases: swarm for features, single agent for tweaks, robustness run, tune swarm, architecture review. [2057809771361677498](https://x.com/unclebobmartin/status/2057809771361677498)
- 2026-05-25 · Put constraints in place so the right behavior is the path of least resistance. [2058970537846571155](https://x.com/unclebobmartin/status/2058970537846571155)
- 2026-05-29 · Agent architecture recommendations never end and lead to over-architecture. [2060373671596703931](https://x.com/unclebobmartin/status/2060373671596703931)
- 2026-06-02 · Agents can't see the screen, so QA has to go through the UI. [2061808243018547376](https://x.com/unclebobmartin/status/2061808243018547376)
- 2026-06-04 · Six-pack tokens "should not be vastly more" than one agent. Compare with Sep 14. [2062571106838446573](https://x.com/unclebobmartin/status/2062571106838446573)
- 2026-06-11 · Six-agent swarm on hello world: 67 min, 1,558 lines, 24 of them the app. [2065161022185316672](https://x.com/unclebobmartin/status/2065161022185316672)
- 2026-06-15 · Deterministic work (queues, sorting) goes in a script. [2066532597195284581](https://x.com/unclebobmartin/status/2066532597195284581)
- 2026-06-19 · Refactoring for agents: CC ≤ 6 and slightly more comments are fine. [2067935532580024741](https://x.com/unclebobmartin/status/2067935532580024741)
- 2026-06-21 · Ball of mud vs a well-factored system: measure clock time and tokens. The factored one wins. [2068772911406784926](https://x.com/unclebobmartin/status/2068772911406784926)
- 2026-07-02 · "Just because we can do them doesn't mean we actually should." Often unit tests plus CRAP. [2072736888478175413](https://x.com/unclebobmartin/status/2072736888478175413)
- 2026-07-10 · QA agent tested through APIs, so the UI was never connected. He added a checker that forbids API calls in QA scripts. [2075579428877349310](https://x.com/unclebobmartin/status/2075579428877349310)
- 2026-07-16 · Agents make haphazard local optimizations. Only the human thinks globally. [2077715525845561698](https://x.com/unclebobmartin/status/2077715525845561698)
- 2026-07-30 · TDD is a human discipline. Agents are held to it through coverage, CRAP and mutation. [2082850576832905657](https://x.com/unclebobmartin/status/2082850576832905657)
- 2026-08-05 · "Ensure that everything that can be deterministic, is done with a deterministic tool." [2085104553746190372](https://x.com/unclebobmartin/status/2085104553746190372)
- 2026-08-06 · Agents don't loop well. He uses an executable FSM and watchdog reminders. [2085348166669353181](https://x.com/unclebobmartin/status/2085348166669353181)
- 2026-08-17 · An agent copied experiment results instead of measuring them. [2089391548408439130](https://x.com/unclebobmartin/status/2089391548408439130)
- 2026-08-21 · Independent stories built by non-collaborating agents "does not end well". Six in a line works, six in parallel doesn't. [2090814740276642173](https://x.com/unclebobmartin/status/2090814740276642173), [2090845662698987654](https://x.com/unclebobmartin/status/2090845662698987654)
- 2026-08-24 · Audit and read the "NOT done" part. Leftover rule files confuse agents. Agents are weak at conceptual encapsulation. [2091869198980887007](https://x.com/unclebobmartin/status/2091869198980887007), [2091883431529447444](https://x.com/unclebobmartin/status/2091883431529447444), [2091876658898706474](https://x.com/unclebobmartin/status/2091876658898706474)
- 2026-09-01 · After AFK work, audit and put the gaps in issues.md. Ask for plain language when agents invent vocabulary. [2094770149500879092](https://x.com/unclebobmartin/status/2094770149500879092), [2094767806659154285](https://x.com/unclebobmartin/status/2094767806659154285)
- 2026-09-12 · Triage mutation sites and let an agent choose the critical ones. [2098745490007261251](https://x.com/unclebobmartin/status/2098745490007261251)
- 2026-09-14 · "What if we built tools that helped us interrogate them." [2099502349601456223](https://x.com/unclebobmartin/status/2099502349601456223)

## Secondary sources (not his words, used with care)
- blog.alexrusin.com/uncle-bob-ai-coding-agents: five-role gauntlet, long prompts "lost in the middle". Its claim that "specs are ephemeral" contradicts his tweets (2026-02-12, 2026-04-15: specs are committed and evolved), so the skills don't use it.
- explainx.ai blog (July 2026): test gauntlet instead of code review.
- cctest.ai: limits of metric gates (security, performance, architecture).
