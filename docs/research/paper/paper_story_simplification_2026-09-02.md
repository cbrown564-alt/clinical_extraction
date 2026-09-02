# Paper story: findings and a proposal to simplify it

Date: 2026-09-02
Status: proposal archive. Current decisions live in
[paper-story simplification](../../paper/decisions/paper-story-simplification.md).
Do not treat this file as the claim or results owner.
Draft under discussion: `paper/draft/FES.tex` (10 pages compiled: title,
declaration, 8-page body; 5,100 body words, 8 tables, 5 figures).
Companion: `paper/supporting materials/Supporting materials.tex`.

## 1. What was done today

- The paper's stages were renamed. The pipeline is now `extract`, then
  `decide`. The first call's answer is called the *provisional answer*.
  Title, abstract, intro, methods, tables, figures and conclusion were
  updated and recompiled. Figure 2 shows two pills (LLM, Rules) per stage.
- Reference b21 (Xu et al., JAMIA 2020) was added as the clinical
  precedent for a high-recall candidate stage followed by a precise
  choosing stage ("generate-and-rank").
- The supporting materials gained one sentence mapping the
  implementation names (`find`, `encode`, `select`) to the paper names.

Nothing below has been applied yet.

## 2. The problem with the current story

The paper says two things: a modular pipeline matches a fine-tuned LLM,
and `decide` adds +0.07. The thing that was actually built, a first call
that turns a one-label task into a validated record of every candidate
with exact evidence, is described in one sentence of Architecture and
one clause of the Discussion. No number in the paper measures it.

Three specific gaps:

1. Nothing measures the extraction record itself. Schema validity,
   evidence exactness and candidates per letter are in the supporting
   materials (Section "Finding Multiple Candidates with Exact Evidence")
   and absent from the paper.
2. Nothing shows that the record is what makes the LLM accurate. The
   experiment exists (Section 4 below) and is not in the paper.
3. The sentence "candidate recall is left to future work" (Results IV-B
   and Discussion) concedes a gap that is framed wrong. The gold standard
   has one label and one quote per letter, so multi-label recall does not
   apply. The stage-1 measure that does apply is whether the gold answer
   is among the extracted candidates. It has never been computed for the
   LLM cells.

The reader is also asked to hold about ten threads (fine-tuning
alternative, three configurations, two stages, evidence record, six
models, local hardware, temperature and thinking, ExECT transfer, hybrid
equals LLM-only, `unknown` errors). The story needs one thread and three
supports.

## 3. What the supervisor wants (from the brief and the June emails)

Sources: brief quoted in `Supporting materials.tex` lines 185–211; email
thread of 3 June 2026 (not in the repo; summarised from the user's paste).

- **He is a comparativist, not a multi-agent partisan.** The brief's
  research goal is a list of controlled comparisons: single-prompt vs
  decomposed under equal budget; self-consistency; evidence requirements
  ("answer only if supported by quote"); structured output validation;
  robustness tests. His review said "the exact architecture is your
  design choice" and called Table VIII (1/2/3-call comparison) useful. In
  June he accepted every negative result and asked for more variations to
  test.
- **He proposed the design that won.** Conor's June email: "the current
  best architecture I have is the first one you mentioned: extract the
  relevant candidates in step 1, then choose the correct candidate in
  step 2." Extract-then-decide is his suggestion (1).
- **He already holds the diagnosis the paper needs.** His words: "the
  model is already identifying the correct clinical facts most of the
  time, and the remaining errors are often due to differences in
  labelling conventions rather than failures in reasoning." That is the
  case for a separate `decide` stage: extraction is about facts,
  deciding is about applying the annotation convention, which he wrote.
- **His three June suggestions already have answers in the artifacts**
  (Section 4): (1) extract content then convert to label = the encode
  split, tested; (2) extract a label then have a judge verify it from
  evidence = verify-then-correct, negative in development; (3) sample at
  several temperatures and let an LLM choose = self-consistency, null and
  negative.
- **What he will not accept:** a flat "multi-agent does not help" stated
  as a prior. He watched that prior argued for three months. He will
  credit tests, not assertion. The repo's own July agentic redo
  (Section 4.6) shows the flat statement is not supportable anyway.
- **On the word "agent":** his comment asked for a definition. The draft
  says the term is not used. With this brief, that reads as refusal.
  Define it once (each LLM call has a fixed role, input and schema; the
  brief calls these agents) and map the final design to his four roles.

## 4. Evidence already in hand

All Gemini 3.7 Flash unless stated. `test450` numbers are aggregate-only
holdout replays whose repo claim boundaries say "ablation, not a results
column". They can be reported in the paper as ablations, clearly
labelled. The headline number stays 0.86 vs 0.81.

### 4.1 The record is reliable

- `test450` cell 3: 0 call failures, 0 parse failures
  (`docs/research/gan2026/gan_extract_prompt_component_ablation_round2_2026-08-30.md`;
  `docs/research/gan2026/gan_encode_then_select_living_prompt_test450_2026-09-02.md`).
- Per-model exact-evidence rates (99%+ for Gemini, Grok, Luna, DeepSeek;
  97% Qwen; 93% Gemma) and schema-valid rates (100% Gemini, Grok, Luna;
  99% DeepSeek, Qwen; 97% Gemma) are stated in
  `Supporting materials.tex` lines 671–677 **without a split or source
  artifact**. Confirm the source before the paper cites them.
- Candidates per letter: `test450` find totals from `comparison.json`,
  Gemini 985/450 = 2.19; six-model range 2.19–2.82
  (`docs/research/gan2026/gan_cell3_candidate_volume_dev750_2026-08-29.md`,
  Section 5). `dev750`: mean 2.16, median 2, range 1–6; selected set
  median 1.
- Gold standard for contrast: one label and one quote per letter
  (`data/Gan (2026)/synthetic_data_subset_1500.json`; each row's
  `check__Seizure Frequency Number.reference` is `[label, quote]`).

### 4.2 The record is the mechanism (brief: "structured output validation")

`docs/research/gan2026/gan_extract_prompt_component_ablation_round2_2026-08-30.md`,
`test450`, Purist micro-F1, find stop:

- Holgate one-label ask, one-label parser: 0.44 (198/450 with dialect
  parser; 139 with living parser). Report as a note, not the comparator.
- Holgate ask wrapped in the event/selection schema: 0.62 (277). This is
  the fair comparator.
- Full event record (cited prompt): 0.79 (355); after decide 0.86 (387).

The document's own summary: "the event/selection object is load-bearing
even when the clinical ask is Holgate's three steps."

### 4.3 The quote obligation matters (brief: "evidence requirements")

Same source. Prompt without the exact-quote requirement: find 0.767
(345), decide 0.822 (370). Cited: 355 → 387. Cost of dropping quotes: 17
letters at decide. Dropping the closed form list: decide 364, cost 23.

### 4.4 Decomposition (brief: "single-prompt vs multi-agent, same budget")

Already in the paper as Table VIII: one call 0.79; extract / decide in
two calls 0.85; three calls (extract split in two, or extract / rewrite
labels / decide) 0.79. Hybrid (one call + rules) 0.86. Source:
`paper_experiments/gan/rungs/gemini37flash/test450/comparison.json` and
the prompt-decomposition artifacts cited in the previous session.

### 4.5 Self-consistency (brief item; supervisor suggestion 3)

- Temperature 0 vs 1: 0.86 vs 0.84, paired difference +0.02, 95% CI
  −0.01 to 0.04, p = 0.20 (paper, Model Configuration). Thinking low vs
  high: 0.86 vs 0.84, p = 0.31.
- July agentic redo (gpt-4.1-mini, hard50 development panel): sampling at
  temperature 0.7 with majority vote scored 15/50 vs greedy 19/50
  (`docs/research/gan2026/gan2026_agentic_redo_results_2026-07-01.md`).
- Reading: the greedy answer is already the modal answer; sampling adds
  noise. Currently reported in the paper as a null "Model Configuration"
  result. Reframe as the self-consistency answer.

### 4.6 Verification stage, section agent, multi-agent (supervisor suggestion 2)

- Verify-then-correct: development finding only, no clean `test450`
  artifact. Conor's June email: it removes true positives because the
  label is a convention, not a quote ("multiple per week" vs "many events
  in the last week"). A related recorded negative: the generate-then-verify
  GEPA program did not beat the 0.731 ceiling
  (`docs/research/shared/exploratory_research_directions_multiagent_review_2026-07-01.md`,
  item 1).
- Section/Timeline agent: development finding, no artifact with numbers
  (`Supporting materials.tex` lines 398–404).
- July agentic redo, hard50 development panel, gpt-4.1-mini: multi-agent
  variants beat single-greedy (29–32/50 vs 19/50) but with 4–8 losses and
  failed the predeclared gate (wins ≥ 5 and losses ≤ 1). Older model,
  50 rows, gate designed for a different sample size. **Consequence:**
  the paper may say "on the living stack, more calls did not help
  (Table VIII); verification and aggregation are more reliable as code;
  section splitting hurt in development; dynamic orchestration was not
  tested at scale." It may not say "multi-agent does not help."

### 4.7 Not yet computed

Candidate-set recall: is the gold label among the extract candidates,
under the same Purist mapping? Computable for Gemini on `dev750` from
saved outputs with zero model calls; then a predeclared aggregate-only
replay on `test450`. Rules-only has a pool oracle already (`dev750`
0.908, `gan_rules_only_three_stage_phase_a_2026-08-29.md`); the LLM cells
do not. This replaces the "future work" sentence with the stage-1 metric
the supervisor asked for and quantifies how much headroom `decide` has
left.

## 5. Where the words are (body, 5,100 words)

Introduction 830. Literature Review 468. Methods 1,330 (Data 258,
Architecture 283, Prompt Design 161, Rule Design 254, Optimisation 129,
Evaluation 240). Results 1,280 (Benchmark 234, By Stage 289, Models 170,
Configuration 138, Errors 121, Generalisability 105, Environment 218).
Discussion 565. Ethics 240. Conclusion 233.

Duplication: the dataset is introduced three times; Literature Review
paragraphs 1–2 restate Introduction paragraphs 2 and 4; the Conclusion
reopens with epilepsy epidemiology.

## 6. Proposal: a ladder of cuts, straightforward to radical

### Level 0. Housekeeping. No story change. Frees ~450 words.

- Delete "the rest of the paper is organised as follows".
- Introduce the dataset once, in Data.
- Development Environment to ~90 words; the rest to supporting materials.
- Model Configuration to two sentences (or reframe as Section 4.5).
- Conclusion: drop the first paragraph.

### Level 1. Remove side quests. Frees ~400 words and one table.

- Method Generalisability (ExECT) to one sentence in future work.
- Table V (historical comparison): drop the Holgate rows, which the
  footnote already says are not comparable; the Gan line becomes prose.
- Deduplicate Literature Review against Introduction.
- Discussion applications paragraph to two sentences.

Cost: the "hospital hardware" thread becomes one sentence (Qwen on a
laptop reached Pragmatic 0.80).

### Level 2. One pipeline, not three configurations. Frees ~500 words, one to two tables.

Present one pipeline (LLM extract, then decide), with the decision stage
performed by rules by default and by a second LLM call as a variant
(same result, 0.85 vs 0.86). `Rules-only` becomes a baseline row (0.72).
Table II goes. Rule Design keeps only the decision rules. The secondary
objective becomes: does an explicit decision stage add value, and does it
matter who performs it? Answer: +0.07 either way.

Cost: the symmetric "rules or LLM at every stage" grid leaves the paper
and stays in the supporting materials. The two facts that matter from it
stay: rules cannot extract (0.63); rules can decide (+0.07). The
supervisor's Table VIII comment concerns mechanism comparisons, not this
grid.

### Level 3. Change the question. This is the recommended stopping point.

Current primary question: is a modular pipeline a viable alternative to
fine-tuning? Proposed primary question, in the brief's own terms:
**which mechanisms make training-free LLM extraction reliable?**

Answer, in the order the supervisor would recognise:

1. Two mechanisms the brief named and nobody in the seizure-frequency
   literature had tested are load-bearing: structured output validation
   (one-label ask 0.62 → event record 0.79; schema-valid 100%) and
   evidence requirements (drop quotes: −17 letters; exact evidence 99%).
2. An explicit decision stage that applies the labelling convention adds
   +0.07, by rules or by a second call (0.86 vs benchmark 0.81, without
   training).
3. Self-consistency, a verification stage, a section agent and extra
   extractor calls did not help on this task (with the scope stated in
   Section 4.6).
4. The gain replicates on six models; errors concentrate in cautious
   `unknown` answers and are inspectable because the alternatives are
   kept.

Structural consequences:

- Introduction ~450 words: problem; the argument ("a one-label task
  should not be asked as a one-label question"); what was done and found.
- Literature Review ~300 words: one-label formulation in prior LLM work
  (Holgate, Gan); generate-and-rank precedent (b21); clinicians' need for
  evidence (b14–b16).
- Architecture: define "agent" once; map the brief's four roles to the
  final design (Field Extractor kept as one call with a rich schema;
  Verification and Aggregation moved to code; Section/Timeline removed
  because splitting hurt). One paragraph contrasting the gold record
  (one label, one quote) with the extraction record (~2 events, each
  with quoted span, category, timing, status, canonical label; a
  provisional answer). Replace Table IV (categories) with a six-line
  record listing from a development letter.
- Results in the brief's order: Benchmark; Decomposition (Table VIII);
  Evidence requirement; Structured output (one-label vs record; record
  reliability across six models); Self-consistency and sampling (renamed
  Model Configuration); Verification stage (development finding, scoped);
  Robustness (six models); Error analysis tied to the record.
- Candidate-set recall (Section 4.7) replaces "left to future work".
- Discussion: three sentences on the brief's four roles, tested and
  resolved; keep the "richer record, more trustworthy system" paragraph,
  now backed by numbers.
- Fine-tuning comparison stays as the headline number and as the
  brief's premise ("instead of training models").

Honesty constraints: label every `test450` ablation as an ablation;
report the Holgate comparator as 0.62 with 0.44 as a note; confirm the
source of the per-model evidence and schema rates before citing them;
state the scope of every development-only negative.

### Level 4. Single model, single pipeline. Not recommended.

Six-model figure to one sentence; LLM-only to one sentence; buy a
worked-example figure. Costs the robustness breadth and the local-model
deployment point for ~350 words. Take the worked-example idea (record
listing) at Level 3 instead.

### Level 5. Rules only as the decision policy; drop the rules baseline. Not recommended.

Loses the baseline that shows rules cannot extract, which is why the LLM
is at extract. One table row is cheap for that.

## 7. What Level 3 does to the open supervisor comments

- Comment 1 (agents, architecture): answered structurally. One call plus
  rules; the four roles tested and mapped; Table VIII justifies the
  two-call design.
- Comment 2 (encode): done.
- Comment 4 (benchmark caution): done; the benchmark is demoted from the
  question to the headline result.
- Comment 5 (stage metrics): answered by candidate-set recall (stage 1)
  and record reliability, which are true stage metrics, instead of the
  "future work" concession.
- Comment 6 (length): Levels 0–2 free ~1,350 words; Level 3 spends
  ~600–700 of them.

## 8. Order of work for the next session

1. Compute `dev750` candidate-set recall for Gemini cell 3 from saved
   extract outputs (no model calls, development split). Write a short
   protocol first; then a predeclared aggregate-only `test450` replay.
2. Confirm the artifact and split behind the per-model evidence and
   schema rates quoted in the supporting materials.
3. Apply Levels 0–2 to `FES.tex`.
4. Rewrite front to back in the Level 3 order. Draft the abstract and
   introduction first and check the voice before the rest.
5. Fill the supporting materials' empty subsections (Multi-Agent Pipeline
   Variants, LLM Prompt Variants, Hybrid Pipeline Variants) with the
   mechanism ledger from Section 4, including the July redo with its
   scope; replace "This design meets all of these requirements" with a
   requirement → mechanism → evidence list.
6. Recompile; check the 8-page body limit.

Guardrails: no model calls needed for any of this; no `test450` row
inspection; the only holdout work is a predeclared aggregate replay for
candidate-set recall.
