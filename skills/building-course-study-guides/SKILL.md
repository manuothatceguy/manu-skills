---
name: building-course-study-guides
description: Use when a learner needs a complete from-scratch study guide or summary of an entire course or subject, built from its slide PDFs or lecture materials, to prepare for a final exam under time pressure. Covers multi-unit courses where one person cannot read everything in time.
---

# Building Course Study Guides

## Overview

Turn a folder of lecture slides (PDFs) plus any practice exam into one readable HTML study guide that teaches the whole course from zero, aimed squarely at the exam. The work is parallelized: a controller (you, the expensive model) orchestrates and assembles, while cheap constructor subagents each read one unit's slides and write that section.

**Core principle:** the controller is the most expensive model and does only orchestration; constructors are the cheapest model (Haiku) and do the bulk reading and drafting. Never invert this.

**Document every problem you solve, the moment you solve it — this is a hard rule, not a nicety.** The instant you fix something the skill did not already cover — a converter that breaks on `aligned`, a pandoc command it rejects, a constructor failure mode, a verification grep that caught a real bug, a reusable script — write it back into this SKILL.md (or `scripts/`) *before moving on*. Thinking budget is the scarce resource here: a documented fix costs the next run one cheap read; an undocumented one costs it the entire re-derivation you just paid for, plus the wrong turns before it. Every hour of this project's history went into finding these gotchas — spend the reader's budget on the exam content that matters, never on rediscovering a wheel already built. If you catch yourself thinking "I figured X out," that is the signal to stop and record X.

**Use the slides' own notation and terminology. Always. No exceptions, no "standard" alternative, no silent translation.** The student is graded by the people who wrote those slides, and the exam is phrased in their symbols. If the course calls the number in the system `E(F)` ("filling"), the time in the system `E(Y)` ("dwelling time"), and the utilization `r`, then the guide writes `E(F)`, `E(Y)`, `r` — never the textbook-standard `L`, `W`, `ρ`, and never `𝔼[N]`, `𝔼[T]`. This costs nothing while writing and is expensive to retrofit: it lives inside compiled MathML, so fixing it later means recompiling every affected formula instead of a find-and-replace.

The failure is silent and constructors do it constantly, because the standard notation is what they have seen most in training. So make it explicit in every constructor prompt, and verify it yourself afterward:

- **During calibration, build the glossary first.** Grep the slides for the definition slides ("some definitions", "notation", "Bezeichnungen") and write down every symbol with the course's own words for it. That glossary goes verbatim into each constructor's prompt.
- **A term the course defines is a term the guide must use.** Not just symbols — if the slides say "dwelling time", the guide says "dwelling time", even where "sojourn time" or "response time" would be more common elsewhere. Give the translation once, in a callout, then use the course's word everywhere.
- **Watch for one word meaning two things.** Courses reuse terms across chapters (in one, "dwelling time" was both a job's time in a queue *and* the holding time in a Markov state). Flag the collision explicitly rather than silently picking one.
- **After the build, audit for drift.** Strip the MathML back to text and grep for the standard-notation symbols the course does *not* use. Any hit is a bug, including in exercises and the formula sheet, which is where it hides longest.

## Match the exam's language, not just the guide's

The guide is written in the learner's language (Spanish, in the run this skill grew from), but **the slides and the exam may be in another language** (English here). That gap is invisible while you write and expensive on exam day: the student studies "clientes en el sistema" and then the exam says *filling* and they stall. Two moves close it, and the learner asked for both explicitly once they hit it:

- **A bilingual keyword glossary, mined from the real exam text, not invented.** `pdftotext` every past exam, then count the technical nouns and the question-stem verbs (`Compute`, `Determine`, `Sketch`, `Classify`, `Give a reason`, `Show that`) by frequency. Build one glossary section — exam-language term → the guide's word — organized by unit, placed next to the "how the exam works" section. Real frequencies also correct your assumptions: here the exams used *node*, *spiral*, *nullcline* heavily even though one auditor claimed the slides avoided them, so the guide's table was already right. Mining beats guessing.
- **The formula sheet goes in the exam's language.** It is the one artifact the student physically copies to the allowed cheat sheet and reads *during* the exam, so its labels and short operational text must match the exam so there is zero translation cost mid-problem. The teaching body of the guide stays in the learner's language (it is for studying); the sheet flips. Formulas are language-neutral, so only headings, labels, table headers, and glue text change. Leave the section's study framing (the "at a glance", the cheat-sheet rules) in the learner's language — it is guidance, not something written on the A4.

Terminology-from-the-slides (the section above) and language-of-the-exam are different axes: the first is *which word*, the second is *which language*. Both are silent failures, both are caught by the same discipline — read the source, don't translate on autopilot.

## Two high-value sections the learner will ask for late: a recipe bank and a theory-question bank

Once the guide teaches the material, the most-requested follow-ups are both *exam-facing indexes into what already exists*, not new teaching. Build them from the past exams, ranked by frequency, and they pay off per line:

- **A recipe bank ("recetario"): one numbered method per exercise type, ordered by how often that type appears.** For each recurring problem type (queue, Markov, game theory, directional field, fuzzy, numerical, scheduling, …) write the first three-to-five steps the student does *without thinking*, the one or two traps, and a one-line "appeared in 2017, 2019, 2024…". This is the complement of the formula sheet: the sheet holds the *formulas*, the recipe holds the *method* (what to write first, in what order, what to check). Reuse the `.sheet`/`.card`/tier-chip layout the formula sheet already has. **Give each card an exam-language trigger line** — the literal prompts that pose this type, quoted near-verbatim from the past papers (`"Model the system as a M|M|1 queue"`, `"Sketch the nullclines"`, `"Determine an explicit formula for yk"`) — so the student maps the *English task* to the method. The recipe steps themselves stay in the study language; only the trigger line flips, same split as the theory bank below.
- **A theory-question bank ("banco de teóricas"): the non-compute questions, with a frequency tag and a short model answer in `<details>`.** These are the `Explain / Describe / Why / Is it true that…` prompts that grade the *reasoning*, not the arithmetic, and students skip them in practice. Each one doubles as a self-test: question in the `<summary>`, model answer hidden. Pull the model answers from the `*_solutions.txt`, not from memory — the grader wants the course's phrasing (e.g. "the Hessian is symmetric only if the function is C²", "E[FRT]=E[BRT]"). **The exam-language rule applies to the question *stems* here, and it is easy to forget:** the student meets these questions phrased in the exam's language on exam day, so the `<summary>` should read in the exam's language (near-verbatim from the past paper — `Describe the Pareto condition in your own words`, `Is the Hessian matrix of a scalar field always symmetric?`), while the model answer below stays in the learner's study language. I first wrote the stems in the study language and the learner immediately caught it ("no usaste el idioma de las slides para el banco"). Same split as the formula sheet: the thing the student reads *during* the exam is in the exam's language; the thing they read *while studying* is in theirs.

Both are frequency-mined the same cheap way. `pdftotext -layout` every exam, then two grep passes over the non-solution files: the compute-type tally comes from topic keywords (`M|M|1|birth.death|queue`, `saddle|mixed strateg|Cournot`, `nullcline|stationary point`, …) counted `n/13`; the theory bank comes from the question-stem verbs (`explain|describe|give a reason|justify|why (is|does)|is it (true|correct)`) counted the same way. Two traps in the mining itself: (1) the subpart labels are not at line start — the margin credit-boxes (`0 1 2`) print before the `a)`/`b)`, so grep the verb anywhere in the line, not anchored; (2) older exams (here pre-2021) use a different header format and language (German scaffolding, `(ca. … Punkte)` instead of `(… credits)`), so a header regex tuned to the recent format silently returns nothing for them — eyeball one old exam before trusting a per-exam count.

**`pdftotext` is enough to mine frequencies and prose, but it flattens every diagram — read the PDF pages as images before you trust that you've seen an exam.** Whole task types live only in the figure: a Markov/queue **state graph** (the balance-equation problems, where a branchy graph needs per-node "rate in = rate out", not the birth-death cut that only holds on a straight chain), a **direction field** to classify from a picture, a **precedence graph** and its `s'/c'/s''/c''` critical-path table, **fuzzy membership plots** (and the exam's own step names — Aggregation → Implication → Accumulation → Defuzzification — which it makes you fill in), a **feed-forward NN** to forward/backprop through. The text dump gives none of these; the learner will (rightly) call it out — "hay diagramas, no podés leer un pdf con txt". Use the Read tool on the PDF pages (it renders them), skip the blank solution-space pages, and read a few content pages per call. Doing this across all 13 here surfaced a whole cluster of missing recipes the txt pass never hinted at: solving the linear system `ẏ=Ay+b` analytically (steady state `−A⁻¹b` + eigen-homogeneous + IVP — the single most repeated ODE problem), Jacobi/Gauss-Seidel as an `Ax=b` solver (splitting `A=L+D+U`, iteration matrix `N`, residual, `ρ(N)<1`), per-node balance equations, the fuzzy step-name terminology, predictor-corrector, and linearizing a nonlinear ODE around a fixed point. None of those were guessable from keyword counts.

## When to Use

- A learner asks you to "learn me the whole subject" / "armá un resumen de toda la materia" from slides.
- The material is many lecture PDFs and there is not enough time to read them all linearly.
- The deliverable should be readable and re-readable, not a chat dump.

Not for: a single article, one lecture, or a topic you can cover inline without reading source files.

## Workflow

### 1. Calibrate (controller, cheap reads)
- Read the **practice exam first** if one exists — it tells you the real question style (find-the-bug, draw-the-diagram, compute), which drives the whole guide. Do not guess the exam from slide titles.
- Read the **syllabus/schedule slide** and one sample lecture to learn the unit breakdown, professor conventions (e.g. a symbol's meaning), and depth.
- Decide the unit list and their exam weight. Heavy units get more depth and go first.

### 2. Fan out (2–3 constructors, model: haiku)
- One constructor per unit (or per group of related lectures). **Cap at 2–3 in parallel** — a shared session credit limit can kill agents mid-run; if it does, only cheap work is lost.
- **Always pass `model: "haiku"`** to the Agent tool. Omitting it inherits the controller's expensive model.
- Give each constructor: its source PDFs, the exact output contract (fragment format, CSS class names, file path), the minimum content to cover, and the learner's language/tone.
- Use the constructor prompt in `constructor-prompt-template.md`.

### 3. Work while they run (controller)
- Write the transversal pieces yourself: the HTML shell + inlined CSS (load `artifact-design` first), the table of contents, the exam-strategy section, and any unit already in your context from calibration. Don't spend a constructor on what you already read.

### 4. Assemble and verify (controller, cheap ops)
- Concatenate `header + sections + footer` with `cat`. A strict fragment contract means no reformatting pass.
- Verify with **grep/tail/python**, never by re-reading full fragments: section tags balanced, one recap per unit, tag-balance per element (`div`, `pre`, `table`, `details`, `ul`, `ol`), no stray `<style>`/`<script>` inside fragments, escaped `<`/`>` in code blocks.
- Publish as an Artifact. Redeploy to the **same file path** to keep one URL across versions.

### 5. Enrich pass (optional, 2 constructors, model: haiku)
- For the heaviest units, dispatch constructors to contrast the draft against the real slides and Edit-in anything missing. This is where "don't omit relevant or seemingly-irrelevant content" gets satisfied.

## Suggest `/goal` to the user before starting

A guide build runs for many turns, spans several context windows, and ends with an audit that either passes or does not. That is exactly the shape `/goal` is for: **the user sets a completion condition and Claude keeps working across turns until it is met**, with elapsed time, turns, and tokens shown in an overlay panel. It works interactive, under `-p`, and in Remote Control.

You cannot invoke it — it is a CLI command the user types. So recommend it in your first reply, with a condition already written out, rather than describing the feature and leaving them to phrase it.

The condition has to be **machine-checkable**, because a vague one ("the guide is good") gives the evaluator nothing to decide on and it will either stop early or never stop. What works here:

```
/goal guia-modsim.html publicada como Artifact, con una <section> por cada unidad del temario,
audit_math.py sin hallazgos, y cero LaTeX crudo / desbalances de tags en la verificación final
```

Two operational facts worth knowing before you suggest it:

- **The evaluator waits for background shells and delegated subagents to finish** before it fires. This skill dispatches constructors in parallel, so the goal will sit idle while they run — that is correct behaviour, not a hang.
- **It needs hooks enabled.** With `disableAllHooks` or `allowManagedHooksOnly` set, `/goal` reports that it cannot run. If the user has either in `settings.json`, say so up front instead of letting them set a goal that never resolves.

## Token Economy Rules (the point of this skill)

| Rule | Why |
|---|---|
| Constructors run `model: "haiku"` | Bulk PDF reading + drafting is cheap work; the controller stays expensive only for judgment. |
| Cap parallel constructors at 2–3 | Shared credit limit; a mid-run kill wastes only cheap tokens. |
| Constructors write the file early, extend with Edit | If a run dies, partial work survives on disk and is resumable. |
| Prompts are resumable: "if the output file exists, continue, don't rewrite" | Survives session-limit kills. |
| Output only to file; final message = path + 2 lines | Pasting content into the reply doubles every token. |
| Controller verifies with grep/tail/python | Re-reading fragments can cost more than writing them. |

**Parallelism does not change usage — constructor count and controller involvement do.** A learner will ask "can't you run more than 3 at once?" The honest answer: concurrency is free. Running 12 constructors 3-at-a-time or all-at-once is the *same* twelve Haiku reads; usage is identical. What actually costs is (a) how many constructors you spawn — each cold-start re-pays the contract/instructions overhead, so grouping two small units into one agent is cheaper than two agents — and (b) how much the expensive controller reads and re-reads. So "cheapest usage" ≠ "fewer parallel"; it means *fewest spawns that still fit one unit's context, Haiku for all of them, and a lean controller that verifies with grep not re-reads.* The 2–3 concurrency cap is purely a reliability guardrail (a shared credit limit can kill mid-run agents); raise it when the user wants speed, because dead agents only lose cheap resumable work. Say this plainly when asked — don't let the user think more parallelism burns more budget.

### Code parallelism: batch first, thread only the subprocesses

A learner will also ask about parallelism *in the scripts* (threading), which is a different axis from agent concurrency. Measured on a 455 KB guide with 807 formulas and 25 exam PDFs:

| Step | Time | Worth threading? |
|---|---|---|
| `verify_build.py` (regex over the built HTML) | 0.10 s | No |
| Full `build_mathml.py` | 1.22 s | No |
| The single `pandoc` call for all 807 formulas | 0.32 s | No — already batched |
| `pdftotext` over 25 exam PDFs | 2.71 s → **0.42 s** with `ThreadPool(8)` | **Yes, 6.5×** |

Two rules fall out, and they generalise past this skill:

- **Threading only helps where Python is waiting on something outside itself.** `pdftotext` is a separate process, so the GIL is released and 8 workers really do run at once. The verification regexes are pure Python: the GIL serialises them, and 0.10 s has no headroom to recover anyway.
- **Batching beats parallelising whenever the tool takes batch input.** Spawning 807 pandoc processes across 8 threads is far slower than one pandoc call with 807 formulas, because process startup dominates the actual work. This is the same reason the Math section says never to spawn one pandoc per formula — the fix there is batching, and *parallelising the wrong design would have hidden the win.*

So: leave the build and the verifiers serial, and parallelise only the bulk PDF extraction in step 1 (already done in `calibrate.sh` via `xargs -P 8`). Do not add threading anywhere else — it buys nothing and makes failures harder to read.

## Deliverable Design (per unit)

Load `artifact-design` for the visual system. Every unit section must have:
- A **recap box** at the top ("En una mirada" / "At a glance") ending with "by the end you should be able to…".
- **Teaching from zero**: define every term the first time it appears.
- **Checkpoints** (`<details><summary>Checkpoint: …</summary>`) after the densest subsections.
- A **self-evaluation** of 3–5 questions with hidden answers at the end.
- **Exam-tip** and **bug/gotcha** callout boxes tied to the real exam style.
- Section numbering that follows the real syllabus order (numbering is meaningful, not decoration).
- **Interactive mini-quizzes on the hard concepts.** Every unit that has a genuinely tricky, error-prone topic (the ones students get wrong on the real exam) gets 2–3 clickable quizzes so the concept sticks through self-testing, not just reading. Put them near the end of the unit and match the real exam's question types: multiple-choice (0/1/several correct, distractors = real mistakes), **value-of-variables tracing** ("what does this print?", answer can be `?` for undefined), and **fill-in-the-blank** rendered as "which directive/clause completes this?". Use the exact `<div class="quiz">` markup from `constructor-prompt-template.md`; the controller supplies the CSS + one wiring script (header/style + footer/`<script>`) once, globally. **Audit every answer key yourself** — a wrong key teaches the wrong thing.

Match the guide's language and register to the learner (they wrote in Spanish rioplatense → the whole guide is voseo, technical terms kept in English).

### Interactive multiple-choice mini-quizzes (intercalated, not just end-of-unit)

When the real exam is multiple-choice heavy (I2DL: "zero, one, or several boxes correct, all-or-nothing scoring"), a clickable MC quiz beats a static hidden-answer `<details>`. The learner asked for these "in the middle" of sections, modelled on a prior guide — so put 2–3 per unit *between* dense subsections, plus the end-of-unit self-eval. The CSS + JS + print rules are in `scripts/shell_snippets.html` (search "interactive multiple-choice"); one shared script wires every `.quiz`, no per-quiz JS. The constructor markup contract (put it verbatim in each prompt, and say "don't change this markup"):

```
<div class="quiz" data-multi="true">
  <p class="qz-q">question, may hold inline \( ... \)</p>
  <ul class="qz-opts">
    <li data-c="1">correct option</li>       <!-- data-c="1" correct, "0" wrong; 0/1/many may be right -->
    <li data-c="0">plausible distractor</li>
  </ul>
  <button class="qz-check">Corregir</button>
  <div class="qz-fb">why, short</div>
</div>
```

Distractors must be the *real* common mistakes (mirror the wrong options in past exams), not filler. First click on the button grades (correct→green, your wrong picks→red, feedback reveals with a verdict); second click resets. Verify after building: `.quiz`, `qz-check`, `qz-fb`, and `qz-opts` counts must all be equal (one of each per quiz). The `@media print` rules reveal the correct options and feedback on paper.

## Math: write LaTeX, precompile to MathML with pandoc

For any quantitative course, **never let constructors write math as plain text with Unicode symbols** (`λk e−λ / k!`). Superscripts and subscripts silently vanish, and the result is both ugly and wrong — `λ^k` degrades to `λk`.

The Artifact CSP blocks every external host, so MathJax and KaTeX from a CDN will not load. The fix is to compile the LaTeX to **MathML** at assembly time: browsers render it natively, with no JS, no CDN, and no font files.

**Use `pandoc --mathml`, not `latex2mathml`.** This bit me hard: `latex2mathml` does *not* support `\begin{aligned}` — it emits the `&` as a literal `<mi>&</mi>` and turns `\\` into an `<mspace linebreak="newline">` that browsers ignore, so every multi-line derivation renders on one line, overflowing with a horizontal scrollbar. It looked fine in a shallow "does it start with `<math>`" test and shipped broken. `pandoc` produces a real `<mtable>` with one `<mtr>` per row. `pip install latex2mathml` is a trap for anything past a one-liner.

Contract for constructors: display math inside `<div class="formula">` goes in `\[ … \]`, inline math in prose/tables/`<details>` goes in `\( … \)`, multi-line derivations use one `\[ \]` wrapping `\begin{aligned}…\end{aligned}`. **Only the equation goes inside `.formula`** — see the box gotchas below.

Build step: don't spawn one pandoc per formula (a guide has ~1500). Extract every `\[…\]`/`\(…\)` into a list in document order, wrap each as `$$…$$`/`$…$`, join with a separator, run pandoc **once**, then substitute the `<math>` elements back by order. pandoc wraps each in `<semantics>` and appends the source LaTeX in `<annotation>` — strip both to keep the file lean.

```python
import re, html, subprocess
tokens = []
def grab(m):
    tokens.append(("block" if m.group(0).startswith(r"\[") else "inline", m.group(1)))
    return f"@@MATH{len(tokens)-1}@@"
staged = re.sub(r"\\\[(.+?)\\\]", grab, src, flags=re.S)   # \[ \] first (may contain parens)
staged = re.sub(r"\\\((.+?)\\\)", grab, staged, flags=re.S)
md = "\n\n<!--SEP-->\n\n".join((f"$${html.unescape(t)}$$" if k=="block" else f"${html.unescape(t)}$") for k,t in tokens)
out = subprocess.run(["pandoc","--mathml","-f","markdown","-t","html"], input=md, capture_output=True, text=True).stdout
maths = re.findall(r"<math\b.*?</math>", out, flags=re.S)
assert len(maths) == len(tokens), f"{len(tokens)} in, {len(maths)} out"   # a dropped one means an unsupported command
```

**Strip each token before wrapping — `$ x $` is not inline math to pandoc.** Constructors write inline as `\( x \)` and often leave spaces inside, so the captured group is `" x "`. Wrapped naively as `$ x $`, pandoc's rule (no space right after the opening `$`) means it is *not* recognized as math: it stays literal text and its stray `$` then mis-pairs with a later formula's `$`, cascading and silently dropping roughly half the formulas. The count assertion catches it, but the fix is upstream — `.strip()` the token before wrapping (already baked into `build_mathml.py`). A tell that this is the bug and not an unsupported command: every part file compiles when tested alone (block `$$…$$` is space-tolerant) yet the concatenated build drops ~50%.

**pandoc rejects `mathtools` extensible arrows** (`\xleftrightarrow{…}`, `\xrightarrow{…}`) and drops the whole formula, so the count assertion fires. That is the signal to hunt the culprit (test each token individually until one yields 0 `<math>`). Rewrite with primitives pandoc knows: a labelled arrow is `\overset{a}{\longleftrightarrow}`, a birth-death chain is `\underset{\mu_n}{\overset{\lambda}{\rightleftharpoons}}`.

Style `math[display="block"]` centered with `overflow-x:auto`; a `.mathfail` class makes failures visible. After building, assert: zero `\[`/`\frac`/`\begin{` survive (a leftover means a missing delimiter), zero `<mi>&</mi>` (a literal `&` = an `aligned` that didn't become a table), and `count("<mtable")` ≥ the number of input formulas containing `\\` or `&`.

Cheapest path: let constructors write plain text first, then dispatch a second **mechanical LaTeX-ification pass** per file (one Haiku agent each, `\[ \]`/`\( \)` contract + a Unicode→LaTeX substitution table). Converting is much cheaper than authoring, and it survives a mid-run kill. But re-scan afterward — the pass misses math buried in `<details>` checkpoints and `<th>`/`<td>` cells, which is exactly where leftover Unicode (`δt²`, `Δ = s'' − s'`, `b² − 4ac`, `R³`) hides. Grep for math Unicode *outside* `<math>…</math>` and fix each.

### A greedy `re.S` replace ate a whole section — anchor the match, and recover from the published artifact

To swap the 14 recipe examples in place I wrote `re.compile(r'<div class="ej">.*?</div>\n(' + anchor + ')', re.S)` and `pat.search(s)`. It looked safe because `.*?` is non-greedy — but `search` finds the *earliest* `<div class="ej">` in the whole document (the formula sheet §8 is full of them), and with `re.S` the `.*?` then expands across every card in between to reach the anchor. The `sub` replaced that entire span with one example, deleting §8 content and half of §9. `verify_build.py` passed on the wreckage because what remained was still well-formed. I only caught it because a later grep for `newestEvent` and `<mtable` came back empty in a section that should have had them.

Two lessons:

- **When replacing per-item in a document that repeats a class, forbid the match from crossing another instance.** The compiled examples were each a single line (compilar returns one-line HTML), so dropping `re.S` and matching `<div class="ej">[^\n]*</div>\n(anchor)` pins the match to the one `.ej` immediately before its anchor. If the block can span lines, use a guard like `(?:(?!<div class="ej">).)*?` instead so `.*?` can't jump over the next instance. Also assert `len(pat.findall(s)) == 1` before substituting.
- **The published artifact is your backup.** The corruption was local-only — I had not republished — so the live version was still the last good state. `WebFetch` the artifact URL (it saves the full HTML to a tool-results path), slice from `<title>…` to the end, strip the frame runtime's trailing `</body></html>`, and write that back over the local file. Faster and safer than reconstructing by hand. Keep a copy of the corrupted file in the scratchpad first in case the fetch is stale.

### `verify_build.py` must strip `<pre>` too — code identifiers are not LaTeX subscripts

The raw-subscript check `[A-Za-z]'*_[A-Za-z0-9{(]` fires on legitimate code identifiers: `simulate_simple_post` (a real 2024 exam function header) reads as `e_s` and `e_p` "raw subscripts". Same class as the `INT_LOW`/`INT_HIGH` false positive in prose. Code blocks are not prose, so `verify_build.py` now strips `<pre.*?</pre>` along with `<math>`/`<style>`/`<script>` before the prose checks. If a false positive still shows up in real prose (a linguistic term like `INT_LOW`), reword rather than loosen the check — but a whole `<pre>` of code should never have been scanned.

### Patching one formula after the build needs `+tex_math_single_backslash`

The build pipeline above rewraps every token as `$…$`/`$$…$$`, which plain `-f markdown` understands. But when you later fix a single formula in the built HTML and reach for pandoc with the `\(…\)` form the fragments use, **default markdown does not recognise `\(…\)` as math at all**. It emits the LaTeX as literal text — and worse, smart quotes fire on the way through, so `\(s''_i\)` comes out as `(s’’_i)`, which looks like a rendering bug rather than a compile failure. Fix: `-f markdown+tex_math_single_backslash`, or convert to `$…$` yourself.

Assert the *result*, not the exit code. pandoc returns 0 here — it happily produced a paragraph. The check that catches it is `re.search(r"<math.*?</math>", out)` plus a `"<mi>" in x or "<mo>" in x` sanity test on the match. Note this path also emits `<semantics>`/`<annotation>` wrappers that the main build strips, so strip them too or the patched formula won't match the rest of the file.

### Writing `<math>…LaTeX…</math>` instead of `\(…\)` ships raw LaTeX, silently

When you author a new section fragment by hand (not through a constructor), it is easy to type the math as `<math>\lambda_i</math>` out of habit — a `<math>` tag with LaTeX inside. `compilar()` (and the main build) only extract `\[…\]` and `\(…\)` tokens; they never look inside literal `<math>` tags. So `compilar` finds zero tokens, hits its `if not tokens: return puesto` early-out, and hands the fragment back **untouched** — the raw LaTeX rides straight into the published file, rendering as `λ_i` literal text. The tell is a `<math> count` that matches your literal-tag count but a source with zero `\(`; I once saw "166 `<math>`" and assumed success when all 166 were raw-LaTeX tags. Grep the fragment for `\\(` before compiling: if it is zero but you wrote math, you used the wrong delimiter. Fix in bulk with `re.sub(r"<math>(.*?)</math>", lambda m: "\\("+m.group(1)+"\\)", frag, flags=re.S)`, then recompile.

`verify_build.py` used to miss this because check 1 deletes `<math>…</math>` wholesale before hunting for raw LaTeX, treating anything inside `<math>` as already-compiled MathML. It now has a dedicated check: real MathML never contains a backslash, so any `<math>` whose body holds a `\` is flagged. Run `verify_build.py` after every hand-authored insert and it will catch this in under a second.

### A `\text{…}` header inside `aligned` gets clipped

Constructors like to caption a derivation from inside the math: `\begin{aligned} \text{Forward pass (earliest times):} \\ s'_A &= 0 \\ …\end{aligned}`. That header row has no `&`, so it lands in column 1 — and column 1 is narrow, because the other rows size it with a bare `s'_A`. The long text overflows its cell, gets clipped mid-word ("Forward pass (earliest"), and pushes a horizontal scrollbar onto the box.

Find them with `<mtr><mtd columnalign="right"[^>]*>(<mtext[^>]*>([^<]*)</mtext>)</mtd></mtr>` at the head of an `<mtable>`, delete the row, and re-emit the text as an HTML caption above the `<math>` (a `.fcap` span inside the `.formula` div). Captions are prose — they belong in HTML, not in the equation.

### A derivation chained with `→` on one line is the main source of horizontal scroll

Constructors compress a whole derivation into a single line: `\[\pi_A+\pi_B=1 \to \pi_A+(4/3)\pi_A=1 \to (7/3)\pi_A=1 \to \pi_A=3/7\approx 0.43, \pi_B=4/7\approx 0.57\]`. Display math does not wrap, so that one line sets the box width and drags a scrollbar under it. Rewrite as `aligned`, one step per row, **repeating the left-hand side** rather than chaining — the reader gets a column of `=` to scan down, and the box fits.

Find them mechanically: for each `<math display="block">` with no `<mtable>`, strip the tags and count `→`/`⟹`/`⇒` and `=`. Anything with an arrow plus 2+ equals signs, or 4+ equals signs, is a chain worth splitting. On one guide that surfaced 9 real cases out of 211 display formulas. Also worth the same treatment: a multi-stage definition packed with semicolons (the four RK4 stages on one line).

While you are there: a `<p>` that ends with a display formula usually still carries the sentence's trailing `.` after `</math>`, which renders as a lone period on its own line under the box. `re.sub(r'(<math display="block".*?</math>)\s*([.,;])\s*</p>', r'\1</p>', s)` — 44 of them in one guide.

### LaTeX habits leak into prose

Even after every `\command` is gone, LaTeX-flavoured fragments survive in plain text where no delimiter ever wrapped them. The one that shipped visible: **`0{,}25`** — the standard trick for a decimal comma in math mode, written straight into a sentence, rendering the braces literally. 13 of them across one guide. Others in the same family: `u^{(0)}`, `u_j^{(l+1)}`, `s''_i`, `y_{k+1}`, and bare equations like `Au = b`.

Sweep for these by stripping `<math>…</math>`, `<style>`, and `<script>` from the built file and grepping what remains for `\{[,.]\}`, `[A-Za-z]'*_[A-Za-z0-9{(]`, `[A-Za-z0-9}]\^[A-Za-z0-9{(]`, and `\\[a-zA-Z]{2,}`. All four must return zero. This runs in a second and is the last gate before publishing.

## Constructors misuse `.formula` boxes — split them

Haiku constructors treat `<div class="formula">` as a generic "important stuff" box and stuff prose, definitions, even ASCII-art tables inside it. On screen the equation and the paragraph share one bordered card and it reads as broken. After the build, find every `.formula` whose body, minus the `<math>` tags, still has >25 chars of prose, and split it: **only the equation stays in `.formula`; the explanation moves to a `<p>` after it.** Two real cases from one guide: a "Caution/maximin" equation with the interpretation paragraph crammed under it, and the whole stationary-point **classification table drawn with box-drawing characters** (`│ ─ ┼`) and `&nbsp;` padding inside a formula box — that one must become a real `<table>`.

## "You can now do exercise N" callouts must come *after* what they need

The practice callouts that point at the course's exercise sheets are the guide's most useful feature and its most fragile: a constructor drops one at the end of whatever it just wrote, without checking that the guide has actually taught what the exercise requires. In one guide, "with this you can now build the fuzzy rule base for the inverted pendulum" sat immediately after the explanation of a **PID controller** — before a single word about fuzzy logic. The reader follows it, hits the sheet, and finds a task the guide never covered.

The check is mechanical and takes one pass: for each `<div class="practice">`, find the offset of the concept it names and assert that offset is *smaller* than the callout's. Anything that fails either moves down, or is a signal that the guide is missing a section — which is what it usually means. In that same guide, the callout for "a second post office" landed 160 characters before the subsection that finally taught state-dependent birth-death rates.

Two follow-ups worth doing at the same time:

- **A callout with no enabling section is a content gap, not a placement bug.** The fuzzy one exposed that the guide taught how to *evaluate* a rule base and never how to *build* one, which is what the exercise asked for. Write the missing section; don't just move the box.
- **Do not trust the nearest preceding `<h3>`/`<h4>` to tell you where a callout sits.** Heading regions span subtopics, so a callout can be attributed to a heading it has nothing to do with. Compare raw offsets of the concept and the callout instead — that is what caught the false alarm on a voting callout that was actually fine.

## The callout label selector needs a child combinator

Callouts get their uppercase title from the first `<strong>`: `.bug strong:first-child { display:block; text-transform:uppercase; … }`. That descendant selector matches **any** `<strong>` that happens to be the first child of its own parent — so the moment a callout grows a table or numbered paragraphs, a `<strong>` inside a `<td>` or a `<p>` renders as a second block-level uppercase title, splitting the line in half. Write it as `.bug > strong:first-child` from the start. Same for `.recap` and `.tip`.

## Auditing a finished guide with subagents

The notation sweep above is the one job worth delegating after the build: it is wide, mechanical, and splits cleanly by slide chapter. Brief each agent with one chapter PDF plus the guide sections that came from it, hand it `dump_section.py`, and demand a report of *anchors* — guide symbol, slides symbol with the PDF page it was verified on, and 5-10 literal words for grep — rather than a prose summary. Tell it explicitly not to edit: MathML surgery is the controller's job.

Three things learned the hard way:

- **Two agents at a time, not five.** Five parallel agents over a 900 KB guide and four chapter PDFs exhausted the session's usage limit and all five died mid-read, having produced nothing. The blocks are independent, so serialising costs only wall-clock.
- **Hold your own edits while they run.** Their findings are addressed by literal quotes; if you rewrite the same region first, every anchor they hand back is stale. Work on a section no agent is assigned to instead.
- **Verify before applying — the audit is a lead, not a verdict.** One agent reported a framework as "entirely absent" when the guide had it in a callout, and called a whole neural-network section "a different model" when the slides did cover perceptrons, just with different symbols. Both reports were *directionally* right and factually overstated. A grep against the PDF settles each claim in seconds.

Ask the learner what the guide is *for* before acting on the list. When one said "the only thing that matters is not losing marks for notation", roughly half the findings became non-issues — a dummy index letter or a prose synonym costs nothing, while a missing criterion (classifying PDEs by the discriminant, which only exists in 2D, instead of by the eigenvalues of the coefficient matrix) costs an entire question. Sort by that, not by how many occurrences each has.

## Reusable scripts (don't re-derive these)

`scripts/` holds the tooling this skill's runs converged on, so the next build starts warm:

- **`build_mathml.py`** — assemble fragments + compile all LaTeX to MathML in one pandoc call, with the self-verification asserts baked in. Edit `PARTS`/`OUT`/`ORDER`, run it.
- **`audit_math.py <dir>`** — the controller audit: leftover plain-text math Unicode, prose stuck in `.formula` boxes, and a compact dump of every display formula for hand-checking. Run before and after building.
- **`find_bad_formula.py <dir>`** — when the build reports a formula-count mismatch, this pinpoints the formula with the pandoc-unsupported command.
- **`replace_block.py`** — rewrite the Nth `<div class="ex">` exercise by position (Edit's exact-match is painful across LaTeX-heavy blocks).
- **`calibrate.sh <course> <txt>`** — step-1 calibration: page counts, section→page map, and the exam-topic frequency table that decides depth and order.
- **`shell_snippets.html`** — the reusable HTML shell bits: math CSS, callout/exercise classes, `@media print` rules, and the scrollspy + open-details-before-print JS.
- **`verify_build.py <built.html>`** — run after **every** edit to the built guide. Six checks, all must be zero: raw LaTeX commands, stray delimiters, raw sub/superscripts and `{,}` in prose, unsubstituted `@@MATH` tokens, literal `<mi>&</mi>`, tag balance, and `<div>` inside `<p>`. Takes under a second on 900 KB; exits non-zero on any finding.
- **`dump_section.py --file <built.html> [<id>] [--math]`** — print one `<section>` as readable text with the MathML flattened to plain characters. This is how you (or an audit subagent) read a finished guide without drowning in compiled MathML. No args lists the section ids; `--math` prints just the formulas, one per line.
- **`check_practice_order.py <built.html>`** — flags "you can now do exercise N" callouts that appear *before* the guide teaches what the exercise needs. For each callout it extracts the technical terms and reports any whose first occurrence in the document comes later. Two filters keep it usable: parenthesised sheet titles are stripped (they exist only inside the callout), and a term appearing just once in the whole document is ignored for the same reason. Those two took one guide from 16 hits to 4, and the survivors were verbs, not concepts. Read the output by eye; it is a lead generator, not a gate.
- **`patch_math.py`** — importable helpers to edit a guide *after* the build, when `parts/` no longer exists: `compilar(html_con_latex)` runs the one-pass pandoc pipeline with the count assertion and strips pandoc's `<semantics>`/`<annotation>` wrappers so the patch matches the rest of the file; `insertar_antes(archivo, ancla, html)` splices a new block; `reemplazar_bloque(archivo, firma, latex)` swaps one display formula, addressed by the first characters of its flattened text.

None of these is clever, and that is the point: each one exists because a run re-derived it from scratch at least twice. Reach for them before writing a throwaway one-liner.

## Audit the math yourself — constructors will not

Constructors asked to "verify your formulas against the slides" **all reported "no errors found", and all were wrong.** The model that wrote the error is the worst possible auditor of it. Budget a controller pass:

1. Dump every display formula into one compact list (`grep -o '\\\[.*\\\]'`) — 80 formulas is a cheap read and it is where the errors concentrate.
2. Re-derive the worked examples by hand. Check that numeric examples *close*: does the stationary distribution sum to 1, does the critical path's slack match, does the defuzzified value follow from the stated areas?
3. Suspect above all: a derivative that skips a term (a cost function that also depends on the variable), a model term with one variable too many, an example whose numbers are "rounded" into place, a quantity silently swapped for a related one (queue vs system), and a planted "find the bug" exercise whose bug is not actually a bug.

## Print / PDF export

Learners want it on paper. Add a `@media print` block (hide the nav rail, drop the background, `break-before:page` per unit, `break-inside:avoid` on formulas/tables/callouts) plus a `beforeprint` listener that opens every `<details>` — the hidden answers must be visible on paper — and an `afterprint` that closes the ones that were closed. Then Ctrl+P → "Save as PDF" just works.

## Common Mistakes

- **Constructors on the expensive model.** The single most costly error — always set `model: "haiku"`.
- **Five constructors at once.** Exceeds shared credits; some die before writing. Three max.
- **Generic content.** Ground every section in the actual slides; a second enrichment pass catches omissions.
- **Re-reading fragments to verify.** Use structural greps.
- **Guessing the exam.** Read the practice exam; it reshapes priorities.
- **Math as Unicode text.** Exponents and subscripts silently disappear. Write LaTeX, compile to MathML.
- **`latex2mathml` for multi-line math.** It breaks `\begin{aligned}` silently (literal `&`, one overflowing line). Use `pandoc --mathml`.
- **`\xleftrightarrow` / mathtools arrows.** pandoc drops the whole formula. Use `\overset`/`\underset` over a primitive arrow.
- **Prose inside `.formula` boxes.** Constructors dump explanation and ASCII tables in there. Keep only the equation; split the rest out.
- **Shallow "does it compile" checks.** `<math>` present ≠ rendered right. Assert `<mtable>` count and no literal `<mi>&</mi>`; eyeball a real screenshot of a multi-line formula.
- **Trusting a constructor's self-audit.** They will tell you the math is correct. Check it yourself.
- **Inline math with spaces → `$ x $` drops ~half the formulas.** `.strip()` tokens in the build; see the Math section. A per-file-passes-but-combined-fails count mismatch is the signature.
- **Constructors write `\begin{align}` bare (no `\[ \]` wrapper) or use `align`/`align*` instead of `aligned`.** Bare means the regex never extracts it and raw LaTeX ships; `align` is not valid inside pandoc's math mode. Grep the built file for surviving `\begin{`/`\frac`/`\cdot` and rewrite as `\[\begin{aligned}…\end{aligned}\]`.
- **`<p>` wrapping a `<div class="formula">`.** Constructors write `<p><strong>Sigmoid:</strong> \(…\)` then a `<div class="formula">` on the next line without closing the `<p>`. Browsers auto-close it so it renders fine, but the tag-balance check flags it; close the `<p>` before the `<div>`. Find with a per-file `<p>` open/close count.
- **A planted index-swap in a worked example.** In the I2DL backprop example the weight update used `W2[0,1]=0.6` when the matrix had `0.4` there (0.6 was `W2[1,0]`) — off-diagonal values swapped. The forward/backward arithmetic was all correct, only the final update line was wrong. Re-derive every worked example by hand; the error hides in the last step nobody re-checks.
- **A worked example that is correct but in the wrong format.** The constructor's I2DL backprop example was matrix-form (`W^T@x`, outer products) — right numbers, but the exam poses backprop as a scalar computational graph: named nodes, each weight `w_ij` a scalar, forward done component-by-component, the chain rule written out as an explicit product of local partials, the multiple paths of a hidden-layer weight summed, and ONE named weight updated. Matrix form even hides the multipath sum, which is the exam's actual trap. Open the past exam's *solution* and copy its shape, not just its answer — a right answer in a format the exam never uses loses the method points the grader is looking for. Best move: reuse a real past-exam problem's numbers so the worked example is verifiable against the official solution.
- **One giant `Write` per section.** On a flaky connection the response is cut and the whole file is lost. Cap every `Write`/`Edit` at ~50 lines and make the prompt resumable; partial work then survives on disk.

## Optional: practice quizzes

For a final mock-exam day, a quiz-generator skill (e.g. `quiz-maker`) can turn the guide plus past exercises into a timed simulacro. Hand-written checkpoints beat generic quiz output for exam-specific traps; use the generator for volume, not for the core guide.
