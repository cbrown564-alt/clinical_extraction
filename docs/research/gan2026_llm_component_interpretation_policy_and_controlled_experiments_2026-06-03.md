# Gan 2026 LLM Component Interpretation Policy And Controlled Experiments

Date: 2026-06-03

Related artifacts:

- `docs/research/gan2026_llm_component_mechanics_error_analysis_2026-06-03.md`
- `experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`
- `docs/research/gan2026_llm_component_mechanics_protocol_2026-06-03.md`

## Purpose

This report turns recurring interpretation problems into fixed policy and lays
out the next controlled experiments. The goal is not to maximize validation F1.
The goal is to answer which LLM components can perform candidate generation,
evidence selection, and projection when those tasks are isolated, richly
specified, and evaluated without confounding downstream consequences.

## Fixed Interpretation Policy

These points should be treated as stable interpretation policy for RQ1/RQ2/RQ4
until explicitly superseded by a later decision record.

### 1. Projection-Compatible Clinical Phrases Are Correct Representations

Do not penalize an LLM for emitting a clinically equivalent phrase that is
trivially projectable into the Gan label surface.

Examples:

- `multiple times per week` is a correct clinical representation of
  `multiple per week`.
- `several focal seizures per week` is projection-compatible with
  `multiple per week` when the evidence supports an active current burden.
- `twice every two weeks` is a valid clinical phrase; whether it renders as
  `2 per 2 week` is a projection/rendering responsibility.

Interpretation: if a phrase preserves the clinical fact and only needs a stable
surface projection, the LLM component should receive credit for representation.
Any remaining error belongs to projection/rendering policy, not candidate
generation.

### 2. Ambiguous But Faithful Clinical Facts Are Valuable

Do not penalize the LLM for faithfully representing an inherently ambiguous
clinical fact.

Example:

- `multiple per shift` is an acceptable clinical fact. It is ambiguous because
  the shift frequency is not the same as a calendar denominator, but that is the
  clinical reality expressed by the source.

Required handling:

- classify the fact as uncertain or denominator-ambiguous;
- preserve the evidence and original phrase;
- apply a transparent projection policy when a Gan label is required;
- record the projection as policy-mediated rather than pretending the LLM
  should have emitted the benchmark label directly.

For `multiple per shift`, a conservative projection to `multiple per week` is
reasonable when the note context supports recurring shifts. The important
scientific question is whether the system exposes that ambiguity and applies
the same policy consistently.

### 3. Multiple Candidates Per Row Are Not A Defect By Default

Multiple candidates can be a feature, not a burden. A broad candidate generator
may improve generalisation by preserving maximum evidence and competing states
for a downstream selector.

Do not call candidate multiplicity a failure unless a controlled experiment
shows one of the following:

- the downstream selector cannot reliably choose among the candidates;
- candidate count causes systematic regressions under a fixed selection policy;
- extra candidates are unsupported, non-evidential, or duplicate noise rather
  than clinically plausible alternatives.

The correct question is not "did the LLM produce too many candidates?" The
correct question is "does broad candidate preservation improve the whole
candidate-to-selection system when paired with an excellent downstream
selector?"

### 4. Do Not Tune The LLM Away From Faithful Clinical Representations

The LLM should not be prompted to hide ambiguity, suppress plausible candidate
states, or pre-render every fact into Gan-specific syntax merely to improve a
local score. Those adaptations belong in explicit projection and rendering
components unless the experiment is specifically testing direct final-label
prediction.

RQ1/RQ2/RQ4 should preserve a sharp distinction:

- clinical representation quality;
- evidence exactness and support;
- state completeness;
- projection policy;
- benchmark rendering.

### 5. Score-Layer Labels Need First-Failure Ownership

When a row is wrong against Gan labels, the artifact must identify the first
failure owner:

- candidate generation;
- evidence selection;
- typed-state representation;
- projection policy;
- rendering/normalization;
- scorer/gold ambiguity.

Without first-failure ownership, a benchmark mismatch must not be used as an
LLM component failure claim.

## Revised Reading Of The Current Evidence

The current row-level artifact is useful, but it is not sufficient to settle the
core scientific questions.

What it does show:

- LLMs often preserve boundary, uncertainty, cluster, and competing-state
  evidence that deterministic rules may collapse.
- Evidence is frequently exact/source-near.
- Broad graph projection and mixed evidence-selection/projection prompts can
  regress rows when they choose among stale, current, seizure-free, cluster, and
  uncertain states without enough explicit policy.
- Some schema outputs expose interpretable projection problems, especially
  cluster axes, seizure-free duration, denominator ambiguity, and
  current-versus-historical selection.

What it does not yet prove:

- whether broad multiple-candidate generation improves end-to-end selection
  when paired with a strong selector;
- whether the LLM can perform projection well when projection is the only task;
- whether claim-table, selected-fact, candidate-list, and graph schemas differ
  in predictable ways under the same row panel;
- whether observed cluster and seizure-free failures come from prompt
  instructions, schema shape, projection policy, or mixed-task overload.

## Controlled Experiment Program

The next phase should remove confounding variables. Each experiment should use
saved validation rows and predeclared panels; no locked-test row-level
inspection is allowed.

### Experiment A. Isolated Candidate Generation

Question: how well can the model generate all clinically plausible
seizure-frequency candidate facts when it is not asked to select or project?

Prompt goal:

- maximize faithful candidate recall;
- preserve exact evidence;
- preserve ambiguity and competing states;
- avoid benchmark rendering pressure.

Outputs:

- candidate fact list;
- evidence span;
- candidate type: ordinary rate, cluster cadence, per-cluster burden,
  seizure-free duration, unknown/ambiguous, proxy/non-seizure, historical;
- uncertainty and currentness;
- optional projection hint, clearly marked as non-decisive.

Primary metrics:

- gold-relevant candidate coverage;
- evidence exactness;
- unsupported-candidate rate;
- candidate diversity by hidden family;
- downstream selector lift when paired with a fixed selector.

Key policy test:

- whether multiple candidates improve or harm selection under a fixed
  downstream mechanism.

### Experiment B. Isolated Evidence Selection

Question: given candidate facts or a gold-relevant query, can the model select
the decisive evidence without projecting the final label?

Prompt goal:

- identify the evidence needed to answer the current seizure-frequency query;
- classify whether the evidence is decisive, ambiguous, incomplete, historical,
  proxy, or conflicting;
- avoid final Gan label rendering.

Outputs:

- selected evidence spans;
- evidence role;
- exact/source-id validity;
- conflict notes;
- missing operand notes.

Primary metrics:

- exact evidence;
- decisive-evidence precision;
- ambiguity classification accuracy;
- evidence support for gold hidden family;
- first-failure owner separation from projection.

Key policy test:

- whether rows currently marked exact-evidence-but-wrong are truly evidence
  failures or projection/state failures.

### Experiment C. Isolated Projection

Question: given fixed structured facts and evidence, can the model or a graph
policy choose the correct benchmark-relevant state and render it consistently?

Prompt/input goal:

- hold candidate facts fixed;
- hold evidence fixed;
- vary only projection instructions and schema;
- evaluate projection as its own task.

Projection panels:

- projection-compatible phrases: `multiple times per week`,
  `several per week`, `multiple per shift`;
- cluster cadence plus per-cluster burden;
- seizure-free duration;
- current-versus-historical conflict;
- competing semiologies and additive same-window counts;
- diary/log aggregation;
- unknown boundary and denominator ambiguity.

Primary metrics:

- projection correctness;
- policy consistency;
- W->C and C->W by hidden family;
- abstention/uncertainty rate;
- rendering-only error rate.

Key policy test:

- whether ambiguous faithful facts can be projected transparently without
  forcing the candidate/evidence component to emit benchmark syntax.

### Experiment D. Schema Representation Comparison

Question: which representation best supports downstream projection without
destroying useful ambiguity?

Compare on the same row panels:

- raw candidate list;
- selected-fact schema;
- claim table plus final query;
- state graph;
- minimal evidence tuple;
- richer typed state with explicit ambiguity/currentness/cluster axes.

Primary metrics:

- retained gold-relevant state;
- hidden-family coverage;
- state completeness;
- projection success when paired with the same projection policy;
- failure interpretability.

Key policy test:

- whether cluster and seizure-free failures are caused by schema shape rather
  than model incapability.

### Experiment E. Combined-Task Ablations

Question: what is lost when the prompt is asked to do more than one component
task at once?

Compare:

- candidate only;
- evidence only;
- projection only;
- candidate plus evidence;
- evidence plus projection;
- candidate plus evidence plus projection.

All runs should use the same predeclared panels and model family where possible.

Primary metrics:

- task-specific performance delta relative to isolated-task upper bound;
- ambiguity preservation;
- projection consistency;
- unsupported fact rate;
- final label correctness as a secondary readout only.

Key policy test:

- whether mixed-task prompting causes the model to prematurely collapse
  ambiguous clinical facts into benchmark labels.

## Frozen Component-Projection Panel

The already proposed frozen component-projection panel remains the immediate
next step, but with a sharper purpose: it should either answer the component
mechanics questions or demonstrate exactly which controlled experiment is
needed next.

Minimum panel requirements:

- predeclared validation row ids and hidden-family tags;
- first-failure owner labels;
- fixed candidate/evidence inputs for projection tests;
- separate regression panels for every gated projection policy;
- explicit treatment of projection-compatible phrasing and ambiguous clinical
  facts;
- no prompt tuning against aggregate F1.

Exit criteria:

- If the panel isolates component behavior clearly, write the RQ1/RQ2/RQ4
  answer from that evidence.
- If the panel remains confounded, run Experiments A-E before moving to RQ5 or
  architecture promotion.

## Research Policy Consequence

The project should stop treating the Gan label as the only valid representation
of a clinical fact. The Gan label is a benchmark-facing projection target. LLM
components may be doing scientifically valuable work when they preserve richer,
messier, clinically faithful facts that require transparent downstream policy.

The next research phase is therefore controlled component science:

- isolate tasks;
- preserve ambiguity;
- assign first-failure ownership;
- compare schema representations;
- test whether broad candidate preservation plus strong selection improves
  generalisation.

Only after these questions are answered should the project return to compiler,
rendering, end-to-end assembly, or validation-score optimization.
