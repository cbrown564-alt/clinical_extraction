# Paper-evidence exploration brief

Date: 2026-08-10
Revised: 2026-08-19 (proposed method named without Grok or hybrid shorthand)
Status: source library implemented and source-checked; final browser-render QA remains open for the 2026-08-10 HTML and SVG sources
Work order: [active roadmap](../plans/ACTIVE_ROADMAP.md)  
Claim authority: [paper claim status](../../canon/10_paper_provenance.md)

## Purpose

Build a purpose-made source library for the research paper that the user will
write. Each source must have one job and make an essential paper question easy
to answer. The library may use concise prose, charts, interactive or sortable
views, case collections, spreadsheets, slides, or dashboards when those forms
work better than Markdown.

The first deliverable is the claim-to-evidence audit below. It records what a
skeptical reader would need, what evidence already exists, its limit, and any
remaining gap. The audit selects and prioritizes source artifacts; it does not
feed a generated manuscript.

This brief scopes the exploration. It is not a new evidence register. The
2026-08-10 Prescription decomposition and aggregate-only `test59` confirmation
are now reflected in the paper-provenance owner; they strengthen one bounded
component claim without changing the primary C16/C17 score fills.

## Settled direction

- The final deliverable is a systems paper, not an evaluation-framework paper.
- The paper is motivated by a clinical-research need: make valuable information
  in epilepsy narrative letters usable for cohort identification,
  longitudinal and retrospective analysis, and future modelling without losing
  the meaning or source of the clinical statements. This is the paper's
  motivation, not a claim that the current system has been clinically deployed
  or validated for those uses.
- The paper must explain the extraction difficulty before presenting the
  architecture. Gan 2026 requires one current seizure-frequency state to be
  reconstructed from temporal, referential, and sometimes competing language.
  ExECTv2 requires a complete and coherent set of clinical facts to be
  collected from a short, dense letter without omissions, conflation,
  unsupported additions, or loss of multiplicity.
- The paper leads with the proposed method: translate clinic letters into
  structured facts in a designed form, with quoted source text and recorded
  rules. Inspectability, intermediate schemas, attribution, ablations, and
  error analysis show how that method behaves. They are not a separate paper
  about evaluation machinery.
- Its proposed core contribution is this method, evaluated on two public
  golds. The model collects a structured ledger with quoted letter text.
  Named rules then shape that ledger into the required form. Those mappings
  can be replayed without a new model call. Written rules and a model alone
  are baselines. The contribution is not that rules are inherently safer than
  models, that every method exposes the same intermediate detail, or that one
  extraction already serves multiple use cases.
- The paper may report matched performance gains where the retained evidence
  directly supports them. It must not claim state of the art, a universal
  hybrid advantage over every comparator, or readiness for clinical deployment.
- Reliability means evaluated research reliability: decisions can be traced
  and reproduced; component behaviour can be inspected and assessed for safer
  failure; and the architecture and evaluation discipline are examined across
  two tasks and multiple model settings. It does not mean broad clinical
  validation.
- Cross-task generalisation concerns the reusable architecture and evaluation
  discipline. Gan 2026 tests deep seizure-frequency reasoning; ExECTv2 tests
  broad phenotype extraction. Their schemas, clinical policies, and measures
  remain task-specific.
- The paper's narrative order is: clinical problem, how each gold defines
  its answer, the proposed method and what it records, then performance
  against the two baselines. Tables cite Grok so the story stays on the
  method. Gemini is in the same band where cells exist.
- The generated manuscript was retired. The user will write the final
  paper personally from the source library and canonical evidence owners.

These are planning decisions. They become paper claims only if the
[paper claim owner](../../canon/10_paper_provenance.md) supports them at the
required strength.

## Boundaries

This documentation work may proceed alongside the vLLM dev10 engineering
objective. It must not block, redirect, or change that objective. It does not
authorize:

- model calls, locked-row inspection, prompt or rule tuning, or new evidence;
- changes to research artifacts, scores, selected methods, or claim strength;
- a rewrite of all research reports or the manuscript;
- a generated replacement manuscript or another catch-all report;
- treating prepared but unreviewed clinical work as validation; or
- replacing the current project objective, roadmap, retained-evidence index,
  or paper provenance.

## First deliverable: claim-to-evidence audit

Start with a small set of tentative systems-paper claims. For each one, record:

1. the claim in ordinary language;
2. what a skeptical systems-paper reader would need to see;
3. the existing report, artifact, decision, test, or architecture view that
   answers that need;
4. the evidence boundary, including task, split, model, method, replay mode,
   scorer, and clinical-review status where relevant; and
5. the remaining gap, or `none` when the existing evidence is sufficient for
   the proposed wording.

Begin with the proposed architectural contribution, component attribution,
matched method comparisons, evaluated research reliability, and cross-task
reuse. Do not begin by rewriting an existing report. If a tentative claim is
unsupported, narrow it or mark the gap; do not manufacture a stronger story
from adjacent evidence.

## Two evidence lanes

The audit and source library use two equal but distinct evidence lanes. Neither
can substitute for the other.

| Evidence lane | What it can establish | What it cannot establish |
| --- | --- | --- |
| Literature and dataset evidence | The clinical problem; gaps in existing systems; why transparency, provenance, uncertainty handling, and human review matter; benchmark task definitions; and label or ambiguity limits | What this project implements or how its selected system performs |
| Project, system, and experimental evidence | What the architecture implements; named performance results; component roles and harms; reproducibility properties; and the limits observed in this system | A field-wide clinical need, a universal trustworthy-system requirement, or a gap across prior systems |

Every prospective claim or source artifact must name the lane or lanes it uses,
the existing evidence owner, and the relevant boundary. Project scores are not
the only admissible evidence. Literature may explain why a system property
matters; only project evidence may show whether this system has that property.
This is a routing rule, not a new evidence register or literature review.

## Claim-to-evidence audit

This is a paper-planning view of existing owners, not a new evidence register.
`Directly supported` means the current owners support the narrow wording below.
`Bounded support` means the claim is usable only with the stated limit.
`Planning hypothesis` means the proposed paper interpretation still needs a
paper-direction or novelty decision; it is not a canonical claim.

### 1. System problem and proposed contribution

**State:** paper direction settled; exact problem and novelty wording remain a
planning hypothesis built on directly supported implementation facts.

**Tentative claim:** the system combines model interpretation with explicit
deterministic constraints and verification so that epilepsy-letter extraction
can be inspected and reproduced rather than treated as one opaque model call.

**Settled motivation:** narrative letters contain information that could
support cohort identification, longitudinal and retrospective analysis, and
future modelling if it can be structured without losing clinical meaning or
provenance. Gan and ExECT show why this is not one generic extraction problem:
one requires reconstruction of a current temporal state, while the other
requires complete multi-fact recovery.

**What a skeptical reader needs:** a precise problem that existing extraction
approaches leave unresolved; a concise account of what the system adds; and a
clear distinction between an implemented architecture, an empirical result,
and a novelty claim.

**Evidence lanes:** literature and dataset evidence must support the clinical
need, prior-system gap, task definitions, and ambiguity limits. Project evidence
supports only the implemented architecture and retained results.

**Best existing owners:** [system architecture](../../canon/01_system_architecture.md),
[pipeline steps](../../canon/02_pipeline_steps.md),
[task-shape framework](../shared/task_shape_framework_2026-08-06.md), and
[paper claim status](../../canon/10_paper_provenance.md) statements S1, S2, and S6.

**Boundary:** the repository directly supports one modular package, three
method forms, explicit stages, and retained runs on Gan 2026 and ExECTv2. Paper
provenance still marks the one-package/two-task statement as partial. The
repository does not by itself establish novelty over prior systems or that this
is the paper's most important contribution.

**Gap or decision:** the clinical motivation and task-difficulty-first sequence
are settled. The proposed method uses a model plus recorded rules
that keep a source span and a change log. Written rules and a model alone are
baselines. The remaining decisions are the exact novelty claim and how strongly
the paper can connect the research system to the motivating downstream uses.
Writing sources now exist for the literature motivation, the two golds, and
prior approaches; they still refuse a novelty claim. Evidence of real-world
downstream use remains outside this audit.

### 2. Hybrid record and architecture

**State:** directly supported for the proposed method; safety interpretation is
bounded.

**Tentative claim:** the proposed method keeps a source span and a named change
log. Development replay makes recorded model and rule contributions
inspectable and reproducible on the same model output; it does not make a
collapsed direct-model decision internally visible.

**What a skeptical reader needs:** an end-to-end architecture, stable method
identities, concrete intermediate records, ownership of every clinical change,
executed examples, and checks that prevent the description drifting from code.

**Evidence lanes:** literature may establish why transparency, provenance,
uncertainty handling, and human review matter. Project evidence establishes the
stages, intermediate records, attribution, replay, and checks in this system.

**Best existing owners:** the generated [architecture index](../../architecture/README.md),
[ownership matrix](../../architecture/diagrams/ownership_matrix.md),
[component-attribution design](../design/component_evidence_attribution_architecture.md),
[retained evidence index](../../experiments/retained_evidence_manifest.md), and
paper provenance S6 and C5.

**Boundary:** generated manifests, executed teaching cases, stage tests, and
no-call reference replay support inspectability and engineering reproducibility
for recorded boundaries on the selected paths. They do not expose model
reasoning, prove that the components are clinically safe, show that every path
has equally detailed intermediates, establish complete historical runtime
metadata, or show that a human reviewer finds the presentation easy to use.

**Gap or decision:** keep the proposed method as the cited path. Mark a baseline
step as collapsed or unavailable rather than implying the same record on every
method. Usability and clinical-safety language must remain out unless
separately supported.

### 3. Matched performance comparisons

**State:** directly supported for named comparisons; universal advantage is
unsupported.

**Tentative claim:** the hybrid method yields matched gains in named settings,
while the size and direction of the gain depend on the task, component, model,
split, and scorer.

**What a skeptical reader needs:** like-for-like methods, exact model and
pipeline identities, development and holdout kept separate, task-specific
metrics, uncertainty about route differences, and negative or mixed results
shown alongside gains.

**Evidence lanes:** project and experimental evidence supports the named
comparisons. Literature and dataset evidence supplies benchmark definitions,
comparator context, and metric or label limits; it cannot strengthen the
project's scores.

**Best existing owners:** [paper provenance](../../canon/10_paper_provenance.md)
C10, C11, and C15–C17; [Decision 0046](../../decisions/0046-exect-primary-method-comparison-boundary.md);
and the [six-model comparison](../shared/six_model_comparison_report_2026-07-18.md).

**Boundary:** the cleanest three-method comparison is living Grok on ExECT
rules, ExECT LLM only (raw F1), and ExECT LLM with rules (hybrid F1),
on `dev140` and aggregate-only `test60`. Full ledger is the named
control, not the headline. Clinical-fact F1 is an internal research
measure, not the published ExECT benchmark.
Gan has retained task-specific method and six-model comparisons, but prompt,
repair, replay, provider-route, and historical-versus-final ruleset identities
must remain visible. These results do not show state of the art or a universal
hybrid win over every comparator.

**Settled presentation:** present performance as two parallel task stories.
Keep each task's methods, identities, splits, measures, and limits distinct. Do
not merge them into one score or capability ranking.

### 4. Component contribution and harm

**State:** bounded development support.

**Tentative claim:** retained replays identify which deterministic stages first
change an answer, show where those stages rescue model output, and expose named
cases where a component also causes harm.

**What a skeptical reader needs:** before-and-after outputs from the same model
call, the component that made the first clinical change, rescue and regression
counts, representative cases, and an account of what the attribution method
cannot establish.

**Evidence lanes:** project and experimental evidence supports component
changes, rescues, and harms. Literature or dataset evidence may establish their
clinical significance only when a suitable source states it directly.

**Best existing owners:** paper provenance C18 and C19;
[hybrid mechanism synthesis](../shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md);
the linked Gan and ExECT stage ablations; and the
[component-attribution design](../design/component_evidence_attribution_architecture.md).

**Boundary:** ordered no-call replay supports first-change attribution on Gan
dev750 and ExECT dev140. It is not leave-one-stage-out necessity or a general
holdout mechanism result. One later predeclared ExECT confirmation is narrower:
removing two named v09 Prescription rules improved aggregate-only `test59`
results, while one model was marginally worse. That supports the named
simplification only; it does not authorize disabling a whole stage or revise
the primary score fills.

**Settled presentation:** harms and failure modes are supporting evidence. Use
the smallest defensible set of rescues, mixed effects, and harmful cases needed
to show how the architecture behaves and where its limits are visible. The
Prescription case should say that decomposition exposed dev-fitting and that
the selected two-rule simplification transferred to holdout; do not turn that
one result into a claim about deterministic correction as a class.

### 5. Evaluated research reliability

**State:** directly supported as an evaluation discipline; stronger reliability
language is a planning hypothesis.

**Tentative claim:** the project evaluates the same eight reliability questions
across both tasks while preserving task-specific measures, evidence states,
row-access limits, and known gaps.

**What a skeptical reader needs:** explicit definitions, reproducible evidence
sources, honest missing cells, separation of textual grounding from semantic
support, correction harms, runtime failures, and no pooled score that hides
incomparable measures.

**Evidence lanes:** literature supports why selected reliability requirements
matter. Project evidence supports only the reliability properties measured or
demonstrated for this system, together with their gaps.

**Best existing owners:** [cross-task reliability](../../canon/09_cross_task_reliability.md),
[reliability framework](../design/reliability_evaluation_framework.md),
paper provenance S8 and C13, and the shared reliability package in the
[retained evidence index](../../experiments/retained_evidence_manifest.md).

**Boundary:** all sixteen task-by-question cells have explicit states and
sources, but evidence strength is uneven. Most cross-task comparisons are
construct-only; unsupported inference is not comparable. The ExECT semantic-
support sample is unreviewed, operational telemetry is unmatched, and there is
no independent clinical validation, deployment evidence, shared reliability
metric, or composite score.

**Settled emphasis:** foreground three properties of the proposed method:

1. gold agreement as a measured proxy rather than absolute clinical truth;
2. a recorded object that keeps the selected letter span and the named rule
   that changed it; and
3. inspectable uncertainty and failure modes, including competing readings,
   incomplete inventories, and abstention.

These are paper directions, not new evidence claims. Semantic faithfulness and
operational reliability remain incomplete where the owners say so. The locked
totals are results of this method. They do not make every rule safe or the
system clinically validated.

### 6. Cross-task reuse

**State:** bounded support for reuse of architecture and evaluation discipline;
performance transfer is unsupported.

**Tentative claim:** the same package, three method forms, stage-ownership
discipline, and reliability questions are applied to a deep single-label
seizure-frequency task and a broad multi-mention phenotype task, while each
task retains its own schema, clinical policies, and measures.

**What a skeptical reader needs:** the shared interfaces and controls, the
task-specific extensions, evidence that all six paths run, and a clear account
of what is reused versus what remains task-specific.

**Evidence lanes:** literature and dataset evidence defines the two task shapes,
labels, and ambiguity limits. Project evidence shows the shared architecture
applied to both tasks. Neither lane currently supports performance transfer.

**Best existing owners:** [system architecture](../../canon/01_system_architecture.md),
the generated [six-path architecture](../../architecture/README.md),
[task-shape framework](../shared/task_shape_framework_2026-08-06.md),
[cross-task reliability](../../canon/09_cross_task_reliability.md), and paper
provenance S1, S6, and C13.

**Boundary:** the evidence supports two task-specific implementations inside
one package and a shared discipline for stage ownership, evidence, replay, and
reliability questions. It does not show one shared scorer, numerically
comparable reliability, zero-shot transfer, performance generalisation from one
task to the other, or universal applicability to clinical extraction.

**Settled presentation:** task flexibility is a distinct cross-task
contribution. The architecture is applied to two task-specific implementations;
it is not transferred unchanged. Avoid wording that implies empirical
performance transfer or one shared task policy.

## Audit conclusion

The first claim-to-evidence audit is complete for the six tentative core
claims. The paper direction is now settled: after the clinical problem and
the two golds, lead with proposed method named without Grok or hybrid shorthand. The source span,
named rule changes, and locked totals against the two baselines are the
organising evidence. Current evidence cannot yet support a novelty claim,
broad clinical or deployment reliability, universal hybrid superiority, or
performance transfer across tasks.

The four prior direction gates are settled: use two parallel task stories;
treat harms and failure modes as supporting evidence; foreground clinically
meaningful correctness, evidence-grounded reviewability, and governable
uncertainty and failure modes; and describe task flexibility as one architecture
applied to two task-specific implementations rather than transferred unchanged.

The first source prototypes are built. The hybrid-rationale brief passed its
author test, and the paired-case format experiment supplied the first positive
HTML finding. These prototypes answer narrow questions. They do not complete
the planned review of the research corpus or provide the full set of sources
needed to write the paper.

## Representative prototypes

1. [Why the proposed method is a model plus recorded rules](why_hybrid_architecture_2026-08-09.md)
   is a self-contained explanatory brief. Its later test asks whether the user
   can explain why the proposed method keeps a source span and a change log
   without reopening a large report.
2. [Two reviewable evidence-to-output cases](reviewable_case_pair_2026-08-09.md)
   is a paired Gan and ExECT development case collection. Its later test asks
   whether the user can support clinically meaningful reviewability with a
   precise, traceable, appropriately qualified example from each task.

The explanatory-brief test passed on 2026-08-09: the author approved it as a
succinct, clear rationale and as a writing-quality reference for later sources.
The first case-format test is recorded below. The prototypes are source
material, not manuscript sections, new evidence owners, or promoted claims.

### Paired-case format experiment

The Markdown [paired case collection](reviewable_case_pair_2026-08-09.md)
remains the traceable reference source. Two deliberately different views now
test whether another form makes the same evidence easier to understand and use:

- the paired visual case map (PowerPoint + deck source) was a format
  experiment; recover from git history if needed;
- the [interactive case explorer](../artifacts/paired_case_explorer_2026-08-09.html)
  supports quick case switching and an optional provenance reveal in one
  self-contained local file.

**Comparison question:** which form makes the two evidence-to-output journeys
clear enough for writing while preserving useful inspection depth?

**Writing and retrieval question:** can the user support an assertion about
clinically meaningful reviewability with one precise, qualified example from
each task without reopening the larger reports?

Evaluate both forms on:

1. speed of understanding;
2. ability to inspect the evidence, consequential decision, output, and caveat;
3. ability to retrieve the row-level source; and
4. ability to qualify benchmark agreement and uncertainty correctly.

**First user-test finding:** for the narrow job of making one reviewable
evidence-to-output journey easy to inspect, the standalone HTML explorer is the
best current form. The user reports that it makes writing easier. The deck
remains a comparison condition.

This finding supports the HTML form for that question. It does not validate the
selected cases, the evidence set, or the broader reviewability claim. The two
cases and their intermediate evidence are too light to demonstrate that concept
on their own. Treat the explorer as one focused exhibit, not as proof or a
complete report.

The wider source set provides distinct perspectives that this explorer cannot:

- task difficulty and the rationale for the architecture;
- aggregate and matched performance for each parallel task story;
- component and ablation contribution;
- error, failure, and harm boundaries; and
- literature-grounded clinical requirements.

The corpus disposition below records where each subject now lives.

## Source-library roles

Each retained or proposed artifact has one role:

| Role | Job | Default form |
| --- | --- | --- |
| Explanatory brief | Answer one framing, task, architecture, or interpretation question in ordinary language | Short, self-contained Markdown modelled on the [task-shape framework](../shared/task_shape_framework_2026-08-06.md) |
| Evidence view | Make a comparison, pattern, or trade-off easier to see than in prose | Chart, sortable view, spreadsheet, dashboard, or slide when materially clearer |
| Case collection | Show a small set of representative successes, failures, rescues, or harms with their limits | Focused cases linked to the owning artifacts; not a row ledger |
| Trace record | Preserve exact methods, protocols, machine-readable results, row records, and aggregate analyses | Existing protocol, report, JSON, JSONL, or retained evidence owner |
| Historical reference | Preserve prior framing or drafting work without controlling current direction | Superseded reports, clearly labelled; recover the retired manuscript from git history if needed |

Deep tables, row-level records, and exhaustive aggregate analyses stay with
their trace owners. A narrative brief links to them and states the useful
answer; it does not copy them into a long Markdown report.

## Format-selection policy

The source library is a purpose-built portfolio, not a Markdown default and not
one large HTML report. Choose the smallest form that fits the communication
job.

- **HTML is the working default candidate** for small, self-contained artifacts
  that combine concise prose, visual explanation, charts or diagrams, optional
  interaction, or a path from summary to deeper evidence. This is a default to
  test, not a requirement.
- **Markdown** suits concise pure writing and reference material.
- **PDF** suits a deliberately designed fixed reading artifact.
- **Slides** suit a genuinely sequenced visual argument or presentation. They
  are not the default for case evidence.
- **Spreadsheets** suit raw or row-level numeric inspection when sorting,
  filtering, or other tabular manipulation matters.

Every proposed artifact must state its reader or writing question, required
depth, whether interaction helps, evidence owner and source boundary, and why
the chosen form is better than the alternatives. Do not call any form ideal
before testing it.

## Historical manuscript status

The generated manuscript was retired on 2026-08-17. Two writing sources
were extracted from it:

- [how the two tasks are scored](score_definitions_2026-08-17.md)
- [starting related-work reading list](related_work_seed_2026-08-17.md)

It is not a drafting target or the organizing owner for the source
library. Recover the retired file from git history if a historical
comparison is needed.

The source library must make it easy for the user to write about:

1. the clinical-research value locked in narrative letters;
2. the distinct Gan and ExECT extraction difficulties;
3. how the proposed method keeps a source span and shapes facts into a designed form;
4. why a model-plus-rules method is the proposed system, with rules and a
   model alone as baselines; and
5. outcome evidence, with replay, attribution, ablations, and error analysis
   showing where a material result arose.

This planning note does not authorize a replacement manuscript, new
clinical claims, or changes to paper provenance.

## Initial source prototypes

The following four prototypes have one communication job and a form chosen for
that job:

1. **Evidence-constellation map.** The initial standalone
   [HTML explorer](../artifacts/evidence_constellation_map_2026-08-09.html)
   maps the six audited core claims to their skeptic question, evidence lane,
   concrete exhibits, canonical owners, boundary, and gap. It is a navigation
   aid, not an evidence register or proof. **Author test: passed.** Starting
   from `component contribution`, the author can reach the cross-task mechanism
   synthesis and see the development-only, non-causal boundary without reopening
   the long audit. The shortcut now closes the default claim before opening the
   requested one.
2. **Parallel two-task performance view.** The initial standalone
   [HTML evidence view](../artifacts/parallel_two_task_performance_view_2026-08-09.html)
   presents the living Grok holdout method comparisons as two separate task
   stories, with each metric, split, shown method, evidence owner, and
   limit visible. Gan shows Grok LLM-only against cleaned hybrid;
   ExECT shows rules, Grok LLM only, and Grok LLM with rules.
   (Update, 2026-08-19: tables cite Grok 4.6. Gan `test450` is 327/450
   LLM-only and 375/450 cleaned hybrid; rules-only remains 329/450.
   ExECT `test60` is 0.7726 raw / 0.805 hybrid against rules 0.7937.)
   The view keeps the tasks' scorers and method sets separate.
3. **Component-role and failure-boundary source.** The four-slide
   [component roles and limits deck](../artifacts/paper_source_component_roles_and_limits_2026-08-09.pptx)
   uses a sequenced visual argument: the overall claim, the Gan mechanism, the
   ExECT family effects, then the causal boundary. Slides are appropriate
   because the claim accumulates across two task-specific charts and ends in a
   fixed qualification; interaction would add no value. **Author test: passed.**
   The author can retrieve one mechanism sentence for each task and the limit:
   first-changer development replay exposes rescue, harm, and no-op behaviour,
   but it is not leave-one-stage-out necessity or authorization for a rewrite.
4. **Literature-grounded clinical-requirements source.** The concise Markdown
   brief [why evidence, uncertainty, and human review belong together](why_evidence_uncertainty_and_human_review_belong_together_2026-08-09.md)
   uses WHO guidance, DECIDE-AI, FUTURE-AI, and the joint FDA–Health Canada–MHRA
   transparency principles. Markdown is appropriate because this is one
   qualified explanatory argument with no interaction or row-level data.
   **Author test: passed.** The author can explain why source evidence,
   actionable uncertainty, and human responsibility form one review process
   while preserving the difference between an external requirement, a project
   implementation fact, and clinical validation.

A 2026-08-09 rendered audit retains standalone HTML for items 1 and 2. The
constellation needs filtering, progressive disclosure, and direct source
navigation; the performance view needs paired visual comparison, exact lookup,
and optional method boundaries. Both were inspected at `1440×900` and
`390×844`; no horizontal overflow or undersized primary action was found. The
constellation resolved all local links after the new sources were added, and
the performance view resolved all eight. The slide source rendered all four
slides for individual inspection; chart values, source notes, text fit, and
slide bounds were checked. A later paper figure should still use an exportable
vector or fixed-reading form rather than treat a working HTML view as manuscript
artwork.

Before building each item, define one real user writing or retrieval question,
choose the form deliberately under the [format-selection policy](#format-selection-policy),
name the required depth and whether interaction helps, and record the evidence
owner and claim boundary. Test usefulness before expanding that form.

The first user finding remains narrow: it supports the HTML case explorer's
form for inspecting one journey. The tests above establish writing usefulness,
not clinical usability or a broader paper claim. Preserve protocols and
machine-readable evidence as trace records, and return any proposed claim
promotion to
[paper provenance](../../canon/10_paper_provenance.md) for a separate decision.

## Corpus disposition

The paper-source library covers the research documents from the
[six-model comparison](../shared/six_model_comparison_report_2026-07-18.md) through the
[ExECT category examples](../exectv2/category_cut_representative_examples_2026-08-08.md).
Each document has one role. Paper sources explain one point. Evidence records
preserve exact methods and results. Protocols preserve predeclared methods.
Historical records remain traceable but do not guide the paper. Active
development work stays outside the library.

### Retain as active evidence or reference

| Document | Role in the finished library |
| --- | --- |
| `six_model_comparison_report_2026-07-18.md` | Main technical comparison record; concise Gan and ExECT sources will replace it in the writing path. |
| `reliability_scorecard_2026-07-18.md` | Detailed reliability record; a visual source will present the paper-relevant findings. |
| `dev750_exact_evidence_and_repair_report_2026-07-27.md` | Pruned 2026-08-16; recover from Git history. Machine artifact may remain under `experiments/`. |
| `clinical_selection_policy_catalog_2026-07-31.md` | Internal policy reference; selected decisions will appear in task sources and cases. |
| `why_the_error_floor_persists_2026-07-31.md` | Broad technical synthesis; a shorter failure source will replace it in the writing path. |
| `six_model_open_mechanism_questions_abc_protocol_2026-08-03.md` | Protocol and route to the retained A-C artifact. |
| `task_shape_framework_2026-08-06.md` | Active task-difficulty source; rewrite for direct paper use. |
| `gold_task_taxonomy_2026-08-06.md` | Detailed Gan task record. |
| `gold_task_taxonomy_2026-08-06.md` | Detailed ExECT task record. |
| `six_model_category_cut_performance_2026-08-06.md` | Technical category-performance record; charts and task sources carry the main findings. |
| `six_model_holdout_category_aggregates_2026-08-06.md` | Aggregate-only holdout record. |
| `category_error_catalog_2026-08-06.md` | Complete Gan error record. |
| `family_error_catalog_2026-08-06.md` | Complete ExECT error record. |
| `six_model_hard_slice_error_modes_2026-08-06.md` | Cross-model hard-slice record. |
| `six_model_hard_slice_error_mode_examples_2026-08-06.md` | Detailed example record; selected rows move to the case workbook. |
| `hybrid_stage_ablation_2026-08-06.md` | Gan ordered-replay record. |
| `hybrid_stage_ablation_2026-08-06.md` | ExECT ordered-replay record. |
| `cross_task_hybrid_mechanism_synthesis_2026-08-06.md` | Technical cross-task mechanism synthesis. |
| `unknown_sentinel_clinical_harm_2026-08-06.md` | Gan harm record. |
| `unknown_breakthrough_loo_2026-08-06.md` | Gan counterfactual record. |
| `prescription_lens_counterfactual_2026-08-06.md` | ExECT counterfactual record. |
| `family_lens_rule_decomposition_2026-08-10.md` | Pruned 2026-08-16; recover from Git history. Prescription lens owners remain. |
| `prescription_lens_v10_holdout_confirmation_2026-08-10.md` | Aggregate-only holdout confirmation of the selected Prescription simplification. |
| `category_cut_representative_examples_2026-08-08.md` | Gan case source; selected rows move to the case workbook. |
| `category_cut_representative_examples_2026-08-08.md` | ExECT case source; selected rows move to the case workbook. |

### Preserve as protocols

The following files remain study records and are not part of the paper-writing
path:

- `deepseek_v4_flash_0731_matched_comparison_protocol_2026-08-03.md`
- `six_model_category_cut_protocol_2026-08-06.md`
- `six_model_hard_slice_error_modes_protocol_2026-08-06.md`
- `six_model_hard_slice_error_mode_examples_protocol_2026-08-06.md`
- `six_model_holdout_category_aggregates_protocol_2026-08-06.md`
- `six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md`
- `category_error_catalog_protocol_2026-08-06.md`
- `family_error_catalog_protocol_2026-08-06.md`
- `hybrid_stage_ablation_protocol_2026-08-06.md`
- `hybrid_stage_ablation_protocol_2026-08-06.md`
- `cross_task_hybrid_mechanism_synthesis_protocol_2026-08-06.md`
- `unknown_sentinel_clinical_harm_2026-08-06.md`
- `unknown_breakthrough_loo_2026-08-06.md`
- `prescription_lens_counterfactual_2026-08-06.md`
- `category_cut_representative_examples_protocol_2026-08-08.md`

### Keep as historical records

These reports describe superseded prompts, rules, routes, or paper packaging.
They remain available for audit but must not appear in the active paper-source
path:

- `qwen_sol_architecture_interaction_report_2026-07-27.md` (pruned 2026-08-16)
- `luna_prompt_variants_report_2026-07-30.md`
- `luna_dated_count_competing_rate_report_2026-07-31.md` (pruned 2026-08-16)
- `luna_prompt_variants_residual_analysis_2026-07-31.md` (pruned 2026-08-16)
- `deepseek_v4_flash_0731_matched_comparison_report_2026-08-03.md`
- `paper_claim_boundary_hybrid_mechanism_c16_0046_2026-08-06.md`
- `paper_claim_boundary_hybrid_mechanism_c16_0046_protocol_2026-08-06.md`

### Exclude from the paper library

`deepseek_unknown_competence_thread_2026-07-31.md` remains active
development work. It is neither a paper source nor a historical record.

## Finished source library

The library now answers each writing question in a form suited to the evidence:

| Writing question | Primary source | Form |
| --- | --- | --- |
| Why are narrative letters a research problem? | [Letters brief](why_narrative_letters_are_a_research_problem_2026-08-17.md) | Literature motivation; not a use claim |
| What did the two golds already decide? | [Golds brief](what_the_two_golds_already_decided_2026-08-17.md) | Writing brief; diagnostic owner stays in `shared/` |
| What did prior extractors already do? | [Prior-approaches brief](what_prior_extraction_approaches_already_did_2026-08-17.md) | Related work by shape and method; not novelty |
| What makes Gan and ExECT different? | [Task-shape source](../shared/task_shape_framework_2026-08-06.md) | Concise explanation and diagram |
| How does the proposed method keep a source span and shape facts into a designed form? | [Method rationale](why_hybrid_architecture_2026-08-09.md) and [architecture view](../artifacts/hybrid_architecture_2026-08-10.html) | Brief plus visual system map |
| What did Gan achieve, how, and within what limits? | [Gan story](gan_story_2026-08-10.md) | Self-contained task account |
| What did ExECT achieve, how, and within what limits? | [ExECT story](exect_story_2026-08-12.md) | Self-contained task account |
| Where do components help, harm, or do nothing? | [Component deck](../artifacts/paper_source_component_roles_and_limits_2026-08-09.pptx) and [failure source](failures_and_limits_2026-08-10.md) | Sequenced visual argument plus concise reference |
| Which cases make reviewability concrete? | [Paired cases](reviewable_case_pair_2026-08-09.md) and [case explorer](../artifacts/paired_case_explorer_2026-08-09.html) | Two guided journeys |
| Which letters show the task difficulties? | [Flagship 3-letter suite](flagship_3_letter_suite_2026-08-11.md) | Six development letters; not a holdout sample |
| Which rows can be filtered? | [Row-evidence workbook](../artifacts/paper_source_row_evidence_2026-08-10.xlsx) | Sortable selected examples |
| Which reliability properties were measured? | [Reliability view](../artifacts/reliability_view_2026-08-10.html) | Visual status matrix |
| How are the two tasks scored? | [Score definitions](score_definitions_2026-08-17.md) | Writing glossary; not a scoring authority |
| Where is the local PDF? | [Source map](related_work_seed_2026-08-17.md) | Citation lookup; not a literature review |

The ordered route is in [documentation navigation](../../NAVIGATION.md#paper-source-library).
Every older document in scope is classified above as active evidence, a
protocol, a historical record, or excluded development work. Technical records
remain where they are for traceability; historical status labels keep them out
of the writing path without breaking their links.

The sources and local links have been checked against their existing owners.
The workbook has been inspected for formula errors, row counts, filters, frozen
headers, and readable sheet renders. Browser-render QA for the three new HTML
views and the SVG failure map remains open because local browser access was not
available in this session. This is a presentation check, not an evidence gap.

No model calls, locked-row inspection, evidence changes, manuscript generation,
or claim promotion were part of this work.

## Governing sources

- [Project status](../../PROJECT_STATUS.md)
- [Active roadmap](../plans/ACTIVE_ROADMAP.md)
- [Paper claims and supporting evidence](../../canon/10_paper_provenance.md)
- [Retained evidence index](../../experiments/retained_evidence_manifest.md)
- [System architecture](../../canon/01_system_architecture.md)
- [Pipeline steps and ownership](../../canon/02_pipeline_steps.md)
- [Cross-task reliability](../../canon/09_cross_task_reliability.md)
- [Task-shape framework](../shared/task_shape_framework_2026-08-06.md)
- [Six-model comparison](../shared/six_model_comparison_report_2026-07-18.md)
- [Hybrid mechanism synthesis](../shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md)
- [Component-attribution design](../design/component_evidence_attribution_architecture.md)
