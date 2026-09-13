# Clinical extraction: research programme and reconstruction plan

Updated: 2026-09-13. Owner: Conor Brown.
Programme direction revised by Conor on 2026-09-11. The three strands below
supersede longitudinal-only prioritisation and earlier hybrid-centred manuscript
plans for future work. They do not rewrite the completed dissertation or its
results. This is the sole programme and reorganisation plan; the numbered
longitudinal phases and completed migration records below retain their scope.

Sequencing decision (2026-09-13): Conor prioritises completion of code
reconstruction and repository migration before resuming programme research.
R5 is research-paper tables. Its full implementation is deferred; reconstruction
must leave room for table evidence and study-owned records. Conor approved
L1–L7, L9 and L10 from the
[compatibility investigation](../research/maintenance/repository_migration_2026-09-08.md#7-legacy-support-investigation-2026-09-13).
L8 is retained: `run.py`, `requirements.txt` and the no-install HPC/vLLM workflow
remain supported. Move required code out of `paper/` and `trace_explorer/` to its
functional owners, migrate consumers, then delete obsolete implementations and
old import paths. Saved-result replay, source/output bytes and the existing demo,
workbench and longitudinal experiences remain supported. These are approved
dispositions; the moves and removals are not yet implemented.

Longitudinal status: Phases 2–4 are complete for their synthetic development scopes. Phase 4
adds the twelve-patient local viewer, both histories, five evidence-traced cohort
queries and saved-extraction component comparison. All 44 declared query gaps
are resolved with reference facts. Predicted-input errors and link limitations
remain explicit in the [prototype record](../../results/longitudinal/prototype_v0.1/README.md).
No expert validation, dataset freeze or deployment is claimed. Phase 5 is next.


[Project status](../../PROJECT_STATUS.md) owns task progress and current checks.
This document owns scope, task order, dependencies, completion criteria, and the
repository restructuring map. [Navigation](../NAVIGATION.md) names the current
locations. Target paths below do not imply that those directories exist yet.

## Programme direction

| Strand | Agreed purpose | Existing evidence | Proposed work and boundary |
| --- | --- | --- | --- |
| A. Primary JAMIA-oriented paper | Tightly ablated one-shot, schema-driven, evidence-grounded extraction, emphasising capable locally deployable models on hospital-controlled infrastructure | Completed dissertation; retained Gan/ExECT outputs, prompt-component studies, model comparisons and local endpoint work | Establish a new paper protocol and capability claim. Hybrid/rule-heavy approaches are not the central method or a main comparator; a later paper may address them. No acceptance, deployment or new model result is implied. |
| B. Epilepsy applications | Bounded cohort identification and longitudinal reconstruction with inspectable evidence | Three-use-case Applications simulation; a separate working twelve-patient longitudinal prototype and saved-output comparisons | Review remaining semantics, test named trial/pathway questions and burden-history analysis, then seek independent validation. Prediction remains an illustrative demo and is outside the first longitudinal release. |
| C. Generalisation beyond epilepsy letters | Test whether reusable software supports a materially different source/task | Shared evidence and run utilities; an advisory architecture review | Research-paper tables selected on 2026-09-13. Prepare source/evidence foundations during reconstruction; defer the full table workflow and source/reference selection. No different-domain capability is established. |

The production/evaluation lifecycle supports all three strands: versioned task
profiles, reproducible run manifests, task-specific metrics within a common
evaluation interface, regression checks, review/error capture and, only when an
application needs it, serving. It is not a fourth product strand. The immediate
priority is to complete the agreed code reconstruction and repository migration,
preserving existing evidence, before defining Strand A's experiment. Full R5
implementation and the remaining longitudinal research phases are deferred.

The completed MSc dissertation remains under `publications/dissertation/`.
`docs/paper/` and its linked evidence owners retain the submitted work's methods
and claims. A future JAMIA manuscript will have its own publication directory
when actual manuscript work starts. The new narrative must be supported by its
own comparison protocol; relabelling old hybrid results as one-shot extraction
is not permitted. Gan 2026 and ExECTv2 keep their separate populations, reference
semantics, scorers and split permissions.

### Strand A: define the capability threshold before choosing a winner

Planning continued at Conor's request (2026-09-13): the
[working manuscript outline](../../publications/jamia-one-shot/README.md) owns the
new paper's argument and exhibits; the
[draft evaluation protocol](../research/gan2026/one_shot_paper_protocol.md) owns
prospective comparisons and unresolved reference/threshold decisions. The premise
combines accuracy, inspectable evidence, natural-language configuration and local
execution. Configurability and reduced authoring expertise need bounded exploration;
they are not established claims. Paper planning can proceed while reconstruction
remains the prerequisite to new experiments. Neither document authorises calls or
locked-data use.

Agreed paper framing (2026-09-13, refined during paper planning): one primary
seizure-frequency evaluation with real-patient evidence carrying the clinical
claim, followed by a compact ExECT configurability demonstration. Gan synthetic evidence supports the
main task's controlled experiments; the real-data reference, sample size and
permitted evaluation use still require protocol confirmation. ExECT provides a
small synthetic, expert-annotated schema-adaptation demonstration covering
diagnoses, medications, investigations and frequencies associated with distinct
seizure types. Include a compact descriptive reference check, not a substantial
comparative model study. Longitudinal evaluation belongs primarily in a separate
paper; draft Strand A without longitudinal results. An optional fictional example
may illustrate downstream use in discussion or supplement. ExECT shows task and
representation breadth within epilepsy, not established generalisation beyond it.

The agreed prompt comparisons are the full Ben Holgate Llama 2 prompt (to be
obtained by Conor's supervisor) and a controlled own-prompt contrast: extract and
represent all seizure-frequency facts, then select one label with a rationale,
versus a single label with evidence. Both own-prompt conditions use one call.
The [protocol](../research/gan2026/one_shot_paper_protocol.md) owns matched settings,
provenance and interpretation: whole-prompt comparison and joint task/output
ablation answer different questions. No comparator text has yet been received.

Keep the main task's scoring explanation central. Preserve each benchmark's own
scorer and avoid a pooled cross-dataset score. Detailed ExECT dataset/scoring
material can sit in supporting material. The manuscript outline can proceed now;
prove the bounded modular extraction path before rewriting methods and running
new experiments. This agreement does not authorise new model calls or holdout use.

The research question is whether current locally deployable models can perform
useful evidence-grounded structured extraction in one inference pass under a
declared task, without a fine-tuning or rule-heavy clinical-repair requirement.
This is a hypothesis, not a conclusion from existing mixed-method tables.
Hospital-controlled execution is an intended operating condition; open weights
or a successful laptop/workstation run alone do not establish it.

Before selecting the model panel, specify the extraction families, reference
data, permitted development split, error costs and minimum acceptable evidence,
coverage and reliability. Include earlier models such as Llama 3.1 and Qwen 2.5
where source and runtime evidence support a fair comparison. Pin exact model
revisions, sizes, quantisation, context, hardware, inference engine and settings.
The present review did not establish a matched old-versus-new local panel.
Published older-model results can provide context, but must not be treated as
controlled baselines when their task, data or adaptation differs.

Hold the dataset, schema, permitted inputs and scoring fixed for each comparison.
Ablate the declared contributions separately: schema/field descriptions,
evidence obligation, scope instructions and examples, then model capability and
runtime settings where warranted. Define whether “one-shot” also means zero
demonstrations; one model call and zero-shot prompting are different claims.
Report raw one-call success and failures. Any format-only retry must have a
separate denominator and call cost; clinically meaningful repair creates another
method. Syntax checks and value-preserving serialization are also recorded.
Do not make a second clinical model call or deterministic clinical selection
invisible inside the one-shot condition.

Measure extraction correctness, unsupported assertions, evidence support,
missing/uncertain states, parse/schema failures and clinically relevant slices,
alongside latency, tokens and hardware requirements. Quote matching establishes
source location, not clinical support. Existing Gan label scores cannot alone
measure the correctness of an entire extracted history. Freeze the evaluation
before any new locked test use; prior access history still governs reuse of
existing holdouts. No new calls or spending are authorised by this plan update.

### Strand B: preserve the distinction between the two prototypes

The `/demo` Applications views use 72 fictional patients and 360 notes whose
records were co-generated, not extracted. Cohort filters, five-visit timelines
and two fitted emergency-risk logistic regressions are executable teaching
workflows. Medication count and age do not constitute a medication-response or
demographic study. The risk simulation intentionally makes note features useful;
its performance is not evidence of predictive utility.

The separate `/longitudinal` implementation uses twelve authored patients, saved
model facts or explicitly selected provisional references, inferred links, both
temporal accounts and five evidence-traced cohort questions. The
[prototype record](../../results/longitudinal/prototype_v0.1/README.md) owns its
results: reference facts plus inferred links agree on 480/480 provisional queries
across authored/generated packs; saved predicted facts agree on 190/240, including
20 failed requests and one unsupported definitive answer. These are inspected
synthetic-development results. Limited link alignment prevents treating query
agreement as complete history reconstruction.

The next application decisions are clinical identity and uncertainty, support
for complete negative histories, and which named cohort or progression question
the retained fields can answer. A trial or surgery-pathway predicate needs its
own definition; the current word “eligible” means the supported query predicate,
not clinical intervention eligibility. Disease-burden rates, ranges and clusters
need an additional evaluation endpoint if progression is an intended outcome.
Medication timing can support descriptive association; it does not identify a
treatment effect. Keep expert reference and real-record transfer separate from
prototype completion. The existing longitudinal phases below govern this strand.

### Strand C: research-paper tables

Selected by Conor on 2026-09-13. Tables provide a different source structure
for the shared extraction foundations. The first source collection, exact
extraction question, reference and reviewer remain to be chosen when this strand
starts. FHIR and guideline workflows are no longer competing R5 choices.

For reconstruction, preserve original document identity and a versioned extracted
view; allow evidence references to distinguish table cells, headers and footnotes
from prose offsets. Study/report identity, populations, outcomes, units,
denominators and time points belong to the research-paper task. Multiple evidence
locations may support one assertion. A later consumer must report insufficient
capture scope rather than silently inventing fields. The architecture owner
specifies this extension boundary; current implemented evidence remains text-only.
No PDF/table parser, OCR, corpus acquisition or full table extraction workflow is
required to close the present reconstruction.

The earlier candidate comparison considered a named user question, source
availability, reference quality, distinct input structure, reviewer access and
a small observable output.
Public FHIR data could test structured resource identity, time and interoperability,
but may test mapping rather than narrative extraction. Research papers could test
table-aware evidence, study/report identity, denominators and outcome time points.
Guideline work first needs a concrete remit: extracting study evidence, answering
questions about a guideline and checking care against recommendations are different
tasks. Do not pick one because its format resembles current JSON records.

The first implementation should show a different domain using the same source,
evidence and provenance interfaces without importing epilepsy enums or Gan
labels. Reuse two downstream policies on a retained extraction only where its
capture scope supports both. Missing fields must yield insufficient coverage or
an explicit new extraction request. Generalise shared code after this test, not
before it.

## DSPy and GEPA: evidence review and bounded role

Review scope: current code and local aggregate artifacts at `b005d6d0` plus the
existing uncommitted longitudinal work, selected Git history, configurations,
saved instructions and study reports. No new model calls, optimizer runs,
locked row inspection or result regeneration were performed. The
[11 September architecture review](../design/architecture_review_2026-09-11.md)
is advisory and reviewed the earlier `fa8917f2` snapshot. Its statement that no
longitudinal package exists is superseded by the local prototype, while its
coupling findings remain useful questions for reconstruction.

### What DSPy actually supplied

DSPy remains a runtime dependency (`pyproject.toml`). Gan, ExECT and paper runners
use `dspy.LM`, `Signature`, `Predict` and `Module`; the shared model factory in
`tasks/seizure_frequency/gan2026/llm_config.py` routes hosted, Ollama and vLLM
conditions. `core/local_structured_output.py` has a distinct format-only retry
module. ExECT's `signatures.py` exposes no-call rendering through `ChatAdapter`.
The historical optimizer used `Example.with_inputs`, `Parallel`, compile,
feedback and saved candidate instructions. These are concrete execution and
experiment capabilities, not demonstrated accuracy gains caused by DSPy itself.

Its more ambitious modular-program role was used less. Current main predictors
mostly accept `prompt_input_json: str` and return JSON strings; clinical scope,
schema, examples and selection instructions live inside task-specific payload
builders. A DSPy signature around that payload does not separate those concerns.
The selected Gan v0.5 prompt was manually authored, not GEPA-optimised; see the
[prompt lineage](../research/gan2026/structured_prompt_lineage_2026-08-15.md).
Gan GEPA was removed in `9c80030b`; ExECT GEPA in `d6c6ecab`, during retirement of
closed experimental lanes. Continued DSPy use therefore principally reflects
useful execution interfaces and accumulated runner dependencies. There is no
controlled evidence that switching frameworks would improve extraction.

### What the optimizer evidence supports

| Evidence | Finding | Limit |
| --- | --- | --- |
| Retained H2 [run summary](../../experiments/exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.json), [launcher](../../experiments/gepa_h2_minibatch_exectv2.py) and [instruction](../../experiments/exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.instruction.txt) | GPT-4.1-mini task model, DeepSeek Reasoner reflection, 90 training/50 selection letters within dev140, minibatch 8, 1,400 metric-call cap, task temperature 0. Instruction grew from approximately 121 to 490 tokens, below the 600-token soft budget. Saved full-dev F1 is 0.7194, with no unscorable letters. | Full dev contains optimizer/selection examples. The 0.710 manual comparator in the run record is historical, not a matched fresh manual-versus-GEPA experiment. The stored elapsed 2,441.6 seconds times compile in the driver, not the entire final evaluation. |
| Historical ExECT `gepa/{program,metric,run_gepa,data}.py`, recoverable at `d6c6ecab^` | Optimised instruction text over a fixed four-family schema, evidence adapter and scorer; per-letter F1 minus length costs. Concrete missed/spurious feedback, recall-weighted objectives and stage-local feedback were implemented later. | It was not merely a scalar-feedback experiment, and did not search freely over schemas, annotation policy or parser semantics. Average per-letter fitness and pooled final micro-F1 weight records differently. |
| `71879c72`, `e075f5c8`, `bf38c85c` | Diagnostics revised early failure explanations: an adapter oracle failure arose from nonmatching quotes; a different SF state metric changed the apparent gap; later code corrected feedback that called a scored true positive over-emission. | These are different issues: representational capacity, metric meaning and feedback consistency. The commit records do not establish their individual contribution to overall search performance. |
| `3174881c`, `bf38c85c`, `6bc1b958` | Recall-additive verification, per-stage models/demos, restricted component mutation and stage-specific credit feedback were built. | More stages did not by themselves establish better extraction. Several run/checkpoint records and contemporary reports are no longer present; surviving code is not evidence that every planned run completed. |
| Historical Gan `gepa/metric.py` at `6bc1b958` | Fitness rewards final Purist correctness (1.0), Pragmatic correctness (0.4), parseable wrong output (0.1), otherwise zero, minus instruction/demo/output length penalties. Parsing uses the existing repair configuration. | This rewards a chosen label, not comprehensive event/evidence extraction. A correct answer can hide omitted or incorrect intermediate facts. A complete comparable Gan GEPA run series was not recovered in this review. |

There is an unresolved provenance discrepancy: the retained H2 JSON/Markdown say
0.7194/0.719, [historical canon](../history/canon/08_gepa.md) says 0.7393, and the
retained-evidence manifest contains 0.741 in the relevant historical package.
Some referenced implementation/closure paths were subsequently deleted. Preserve
the originals and trace scorer versions, aggregation and replays before citing a
single consolidated GEPA score. The archive's claim that its entry point is ready
for replay is not true of the current tree: the launcher imports removed modules.
Historical commit messages about a universal “plateau” also cannot override later
corrections or stand in for recoverable run artifacts.

### Why manual changes could outperform search

The strongest supported explanation is a combination of task formulation and
evaluation alignment, with bounded search and model capability still unresolved.
The saved evolved instruction asks for current states only, omits unknown states,
ignores ranges and excludes requested investigations. Its schema starts with a
deduplicated, benchmark-shaped fact inventory. That is a different target from
retaining history and uncertainty for multiple questions. No instruction search
can recover information the selected representation and policy deliberately discard.

The scoring path combines evidence matching, representation conversion and clinical
unit matching. An identical scalar error can mean a missing fact, wrong evidence
offset, different concept granularity or disagreement with annotation policy.
Early diagnostics confused these. Later explicit feedback improved visibility,
but the SF coherence correction demonstrates that even detailed feedback can tell
the model to optimise against its score. A type-agnostic state metric also cannot
prove correct assignment of states to individual seizure types. Length penalties
and minority-class weighting add further objectives; the selected H2 instruction
staying below budget does not prove that the penalty caused or did not cause the
search outcome.

The H2 launcher reports a noisy three-example acceptance comparison and increased
the minibatch to eight. That is evidence of a search limitation being investigated,
not proof that a larger search would succeed. Full proposal/acceptance logs and
repeated-seed comparisons are missing from the retained local package. The fixed
task model and changing evaluator versions further limit causal attribution.

Manual work could change capture scope, field meaning, examples and task
decomposition after inspecting mechanisms; automated instruction search had a
narrower action space. Specific manual changes have measured gains: the
[Luna study](../research/gan2026/luna_prompt_variants_report_2026-07-30.md) improved
raw development Purist from 411/750 to 422/750 for rate guidance, while a different
variant led the repaired score. The
[ExECT leave-one-out study](../research/exectv2/v0924_prompt_ablation_luna_dev20_2026-08-16.md)
found scope removal most damaging on its small development sample, and cumulative
removal exposed component interactions. These studies support targeted hypotheses,
not general manual superiority: models, budgets, representation and scoring differ
from the GEPA study. The retained H2 score is slightly above its recorded manual
mini baseline. Successful manual iterations also benefited from repeated developer
inspection; a fair comparison must account for that selection advantage.

### Appropriate DSPy boundary

Keep DSPy as an optional implementation of model execution and bounded optimisation,
behind ordinary typed Python interfaces. Use signatures to expose meaningful task
inputs/outputs, small modules where a real stage has a distinct responsibility,
and adapters to render and validate a declared request. Preserve the rendered
messages, schema and component hashes alongside every run. Keep domain records,
evidence validation, temporal linking and scorers callable without DSPy or a live
model. Do not split a one-shot study into extra calls merely to create modules.
The [DSPy documentation](https://dspy.ai/) describes signatures, Python composition
and optimisers as separate capabilities; the historical wrappers use only part
of that interface.

Do not restore GEPA as a default execution dependency. If later justified, compare
a frozen manual baseline against one bounded optimiser on a named module, with a
stable evaluator, matched model/data/budget and separate selection/evaluation data.
Inspect feedback on deliberately correct, missing, unsupported and mislinked
development predictions before spending calls. Retain candidate lineage and raw
outputs; report query/task correctness independently of optimisation fitness.
Current [GEPA documentation](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/diving-deeper/gepa-in-depth.md)
supports feedback and bounded search, but does not identify the historical installed
version or establish that today's defaults reproduce the old run. Pin both DSPy
and GEPA versions for any future comparison.

## Staged codebase reconstruction

This is a proposed strategy, not implementation authorisation for broad changes.
Keep one package initially. Prove a behaviour-preserving slice, record what can be
reused, then extend it. A changed directory name or DSPy base class is not a
modularity result.

The [software specification](../design/architecture.md) owns the component design
and acceptance criteria. The agreed sequence is Gan prompt composition and replay
parity, ExECT schema reuse, then longitudinal consumers. The earlier ExECT-first
artifact proposal remains a bounded second-slice design. Preserve existing raw
responses, identifiers and scoring throughout. Complete the agreed reconstruction
before paper work; decide which compatibility adapters to retain from the audit.

| Stage | Work and owner | Completion evidence |
| --- | --- | --- |
| R1. Establish the baseline | Conor settles Strand A's task/claim; implementation contributor inventories current callers, dirty files, active writers, local-only data and supported commands. Recover historical optimizer dependencies only in an isolated inspection/replay environment if needed. | Existing evidence owners and migration record identify preserved bytes, versions, score discrepancies and known test failures. No old queue is resumed. |
| R2. Prove Gan prompt composition | On the single-label Gan task, introduce a source-document input and typed assertion output alongside one current one-shot path; keep legacy adapters. Separate task definition, prompt assembly, model execution, format handling and task projection without changing the model request. Make instructions, examples, allowed-label presentation, evidence requirements and schema presentation independently inspectable and versioned. | A permitted development replay has the same rendered request and outputs; ordinary-note execution needs no dummy gold fields; raw/repair provenance and errors survive. |
| R3. Test ExECT reuse and the common lifecycle | Apply task-specific schemas and prompt components to diagnoses, medications, investigations and seizure-type-specific frequencies without ExECT branches in the shared runner. Reuse current registry/resume/comparison code where compatible; add versioned task profiles and a manifest adapter for this path. Keep benchmark scorers independent. | One run can be inspected, replayed, scored and reviewed without source-path guesses; failures remain in denominators; a model change needs configuration rather than clinical code edits. |
| R4. Apply to a second epilepsy consumer | Connect the retained assertion representation to one cohort/history policy only if its capture scope suffices. Preserve availability cutoffs before inference and both historical accounts. | Same stored facts serve two declared policies; unavailable fields are explicit; new policy execution cannot change prior assertions. |
| R5. Prepare for research-paper tables; full task deferred | Preserve the extension boundary for document/table identity, structured evidence locations and study-owned result types during reconstruction. Select concrete sources and implement the workflow later. | Foundations do not require epilepsy labels or prose-only evidence for every task. Current text-only support and deferred table parsing/extraction remain explicit; this is not a different-domain result. |
| R6. Consolidate demonstrated overlap | Move only utilities used correctly by both slices; update callers, compatibility, documentation and tests together. Add serving only for a named application need. | Required replay, package, UI and public-checkout checks pass; unused abstractions are removed; rollback and provenance remain possible. |

Implementation progress on 2026-09-13:

- R1 retains the migration record's byte, path and local-only inventory. The
  implementation started at `b005d6d0` with existing user work preserved; a new
  active-writer check found no matching local model, generation or pytest process.
- R2 is implemented for the explicitly selected `gan_llm_extract` profile. Prompt
  components compose the byte-identical legacy payload and rendered messages;
  ordinary-source execution needs no benchmark gold, and replay has no live-call
  fallback. A permitted validation/development saved response retains its selected
  compatibility output.
- The bounded R3 path is implemented as an additive ExECT library and operational
  path. Its explicit
  profiles do not mutate the legacy default; raw event positions and unknown fields
  precede the named Compact adapter; scoring stays task-owned; lifecycle manifests
  bind recorded runtime metadata when present and account for parse/schema failure.
  The older row-key resume helper is not used as request identity because it can
  overwrite duplicate keys; persisted artifact loading and registry integration
  remain future work if a named run needs them.
- R4 is implemented for the existing synthetic longitudinal facts. One immutable,
  query-independent artifact serves visit and retrospective policies; source dates
  and text are identity-bound, cutoff-limited captures exclude later sources, and
  query-conditioned saved outputs are refused as reusable evidence.
- R5 is selected as research-paper tables. The study-report example remains
  fictional; source/reference selection and full implementation are deferred.
  The present decision records foundation requirements, not implemented table support.
- R6 moves only the demonstrated source/artifact/lifecycle records and DSPy provider
  construction into `core/`. Gan keeps its historical provider import, old runners
  and outputs through compatibility paths. No serving layer was added because no
  application need was named.

These are software implementation claims, not a new model result, clinical
validation, completed paper protocol, different-domain result or deployment.

### Package boundaries to preserve or correct

The approved support reduction supersedes earlier blanket import/CLI compatibility
requirements in this document. Preserve required behavior and evidence through
the replacement interfaces; old aliases and package paths need not remain.
The [architecture destination map](../design/architecture.md#reconstruction-destinations-after-the-legacy-support-decision)
owns the code boundaries. The migration record will record exact file moves and
verification. Do not treat a directory rename as completion of that separation.

| Current boundary | Disposition and reason |
| --- | --- |
| `tasks/.../gan2026` and `tasks/.../exectv2` | Preserve dataset IDs, parsing/normalisation, split policies and scoring as benchmark adapters. Separate reusable domain facts from benchmark label/mention semantics gradually. |
| `core/` | Retain genuinely shared evidence, validation, IO/path and arithmetic utilities. `FinalExtraction` is answer-centred and `EvidenceSpan` lacks document/version identity; add an adjacent assertion/source representation before replacing callers. Task-specific reliability and roster helpers do not become universal merely by living here. |
| Gan `llm_config.py`, `paper/lm.py`, `operational/runtime.py` | Map overlapping provider concerns, then extract a shared execution configuration. ExECT currently imports the Gan model factory: correct that dependency with compatibility wrappers after parity is shown. Preserve actual provider payloads and route-specific settings. |
| `operational/gan.py` | Remove the need to construct a benchmark record with dummy gold fields for a new runtime path. This is interface coupling, not evidence that gold is sent to the model. Keep old CLI behaviour through an adapter. |
| ExECT `assembly/` and scoring views | Reuse lessons from provenance and findings; do not relocate benchmark-specific dictionaries, mention conversions or gold-dependent scoring into a supposedly generic core. Separate pure projection from evaluation. |
| `longitudinal/` | Preserve evidence, source accounts, linking, temporal and query ownership. Its dictionary/schema representation and source-specific semantic rules need review; do not silently repair prediction errors while adding types. |
| `paper/` | Move retained task-specific replay and evaluation to benchmark-owned evaluation modules, shared comparison mechanics to `evaluation/`, and publication builders to their script owner. Retire the historical live dispatcher and remove the old namespace after consumers move. Preserve dissertation result semantics. |
| `core/registry.py`, resume and comparison records | Adapt existing manifests before inventing another registry. Old phase/architecture enums are legacy metadata, not universal task-profile concepts. Unified evaluation means a shared report interface, not one clinical score. |
| `trace_explorer/`, frontend, generated architecture docs | Move API, inspection and review storage to `inspection/`; put benchmark hydration in benchmark-owned evaluation modules. Preserve review/error capture and distinct demonstration sources. Rebind frontend consumers; generated diagrams must describe implemented paths. |

The lifecycle manifest should identify task/schema/prompt/program/scorer versions,
dataset and permitted split, source and output hashes, runtime/model revision,
hardware/quantisation, call/latency/cost and failure accounting, replay mode,
format and semantic changes, reviewer decisions and artifact visibility. A task
profile declares required fields and policy compatibility. Neither a profile nor
a registry entry grants access to locked data or authorises a model run.

### Decisions required before a major refactor

1. What exact extraction unit, families and evidence-backed outputs define the
   primary one-shot paper, and which existing references can score them fairly?
2. What measured threshold would support the hospital-controlled local-model
   claim, and what constitutes a matched Llama 3.1/Qwen 2.5 comparison?
3. What counts as one-shot, a permitted format repair, unsupported evidence and
   an abstention? Which metric is primary and which errors must be reported apart?
4. Which retained interfaces/commands need compatibility, and which old outputs
   cannot be losslessly mapped to the proposed assertion representation?
5. Which policy/scorer revisions explain the GEPA score discrepancy, and which
   missing logs must be recovered before attributing the search outcome?
6. Can feedback distinguish extraction, evidence, annotation and selection errors
   consistently, and does optimisation fitness rank candidates as the intended
   evaluation does? If not, improve the evaluator before tuning prompts.
7. Research-paper tables are selected for R5. Exact sources, reference and review
   ownership remain later research decisions; preserve the table-evidence extension
   boundary now without implementing the full task.
8. What immediate application needs serving, if any? Until there is one, keep
   reproducible batch execution and review sufficient for the research workflow.

Implementation contributor owns dependency mapping and verification; Conor owns
research scope and sequencing. Independent domain reviewers are required for
validation claims, not for reversible architecture exploration. No partner,
hospital deployment, external publication or paid run is assumed.

Verification of this programme update: documentation hygiene, whitespace checks
and local links in the new programme sections pass. No Python/source, prompt,
schema or saved-result changes were made. Full pytest, Ruff, mypy, frontend tests
and model experiments were not rerun for this documentation-only update; earlier
prototype verification remains separately attributed to its existing record.

## Strand B detail: longitudinal outcome and research question

Build a synthetic, patient-linked epilepsy clinic-letter dataset and a working
extraction pipeline that support cohort identification and longitudinal analysis.
Preserve what was documented at each visit and how later evidence changes the
retrospective interpretation. Demonstrate one complete path from letters to
supported facts, patient history, and a cohort answer before generating the full
corpus. Later expert annotation and real-record evaluation establish separate,
stronger forms of evidence.

Primary question: does explicit linking of evidence across clinic letters improve
time-dependent cohort answers and reconstruction of patient histories compared
with independent letter extraction and simple aggregation?

The dataset and its annotation policy are research contributions to investigate.
Neither schema superiority nor clinical usefulness has been established. Existing
Gan and ExECT results remain evidence for their original tasks only.

## Decisions and working assumptions

**Agreed direction for the first longitudinal release**

- Keep both views: the account supported by letters available at a selected date,
  and the retrospective account using later evidence. Preserve earlier assertions
  rather than silently replacing them.
- Focus on cohort identification and longitudinal analysis. Predictive modelling,
  treatment recommendation, and clinical deployment are outside the first release.
- Start with synthetic letters and AI-generated provisional annotations. Seek
  expert annotation after a working demonstration; do not claim AI agreement is
  expert agreement.
- Preserve concurrent seizure patterns and frequency qualifiers. Separate epilepsy
  diagnoses from seizure types. Record past, current, planned, and conditional
  medication information without treating a plan as confirmed use.
- Restructure the repository first, including code callers, results, publications,
  examples, media, documentation, and local research material.

**Planning assumptions to test in the pilot**

- Target 300 synthetic patients, each with 2–5 letters (600–1,500 letters).
  Phase 1 replaces the infeasible 150/150 distinct-seed allocation with a
  provisional ceiling of 140 ExECT development records and 160 Gan development
  records, subject to source terms and lineage checks. Fewer eligible records
  mean a smaller corpus or disclosed seed-free authoring, not locked-data reuse.
  These are coverage targets, not prevalence estimates or a powered sample size.
- Use four clinical families: epilepsy diagnosis, seizure events/patterns,
  medications, and investigations. Avoid an unrestricted patient-history family;
  add context only where a named research question needs it.
- Start with one authored three-letter patient, then a 12-patient/36-letter pilot.
  Pilot patients stay in development, even if the annotation scheme later changes.
- Conor owns scope and research decisions. An implementation contributor executes
  engineering tasks. Clinical reviewers are prospective collaborators, not assigned
  or confirmed participants. King's and Swansea are possible partners.
- No new model calls, outreach, corpus generation, or publication is part of this
  planning change. Model budgets, providers, and release destinations are selected
  in the phases that need them.

## First phase: repository restructuring

### Observed structure

Inspection on 2026-09-08 at Git base `8da94df5`, with an already dirty working tree.
Counts exclude dependency/build caches, Python caches, and `.DS_Store`. Sizes are
approximate file bytes, not disk allocation. This was a path/metadata inventory
and selected caller review; locked row contents were not inspected.

| Area | Files / tracked | Approx. MiB | Finding |
| --- | ---: | ---: | --- |
| `src/` | 417 / 417 | 3.5 | Existing package, task implementations, operational CLI, paper runners, APIs |
| `tests/` | 107 / 107 | 0.7 | Replay, paths, scoring, generated-doc and safety dependencies |
| `frontend/` | 216 / 197 | 5.1 | Workbench plus active user edits to viva/application demos |
| `docs/` | 617 / 535 | 85.4 | Current owners mixed with superseded canon, decisions, reports and generated assets |
| `paper/` | 55 / 55 | 24.0 | Manuscripts, supporting materials, templates, handbook/rubric and existing archives |
| `paper_experiments/` | 283 / 283 | 58.6 | Tracked machine evidence also read by runners, tests and frontend panels |
| `experiments/` | 2,276 / 1 | 1,342.9 | Mostly local run outputs; one tracked exception requires explicit handling |
| `scratch/` | 1,098 / 0 | 695.2 | Local working material; includes holdout-related paths, not automatically disposable |
| `data/` | 624 / 0 | 9.0 | Local input corpora and split material |
| `literature/` | 41 / 0 | 83.1 | Local source library and publishing templates |
| `media/` | 29 / 0 | 66.7 | Local clinical-letter story assets, source material and audio |
| `scripts/` | 61 / 60 | 0.6 | Checks, study runners, builders, shell/PowerShell helpers |
| `configs/` | 4 / 4 | <0.1 | Gan and ExECT study configurations |
| `examples/` | 1 / 1 | <0.1 | Three-letter Gan/vLLM walkthrough input |

Other roots: `.github/` contains CI; `logs/` is empty; `tmp/` and `.tmp/` are
local temporary output; `.trace_explorer/` is local app state. `.venv/`, tool
caches, `.skills/`, and `.worktrees/` are environment state. Keep credentials in
`.env` local; never include their values in the migration inventory.

`PROJECT_STATUS.md` and `CONTEXT.md` are ignored local files. Contrary to the old
README, much of `docs/` and all observed `paper/` files are tracked. Gitignore
patterns do not untrack existing files. A move must preserve the intended
visibility, not merely copy the old ignore rules.

### Proposed target structure

Keep one Python package and one frontend. Organise publications by output,
results by evaluation, and studies by question. Avoid a new package architecture
until the longitudinal pilot demonstrates what can actually be shared.

```text
README.md                         project entry and runnable examples
AGENTS.md                         cross-track working and evidence rules
PROJECT_STATUS.md                 local current task state
CONTEXT.md                        local glossary, narrowed during migration
pyproject.toml / uv.lock          package and pinned development environment
run.py / requirements.txt        retained external Gan runner compatibility
src/clinical_extraction/
  core/                          demonstrated shared functionality
  tasks/                         existing Gan/ExECT implementations retained
  longitudinal/                  new implementation, added with the pilot
  operational/                   supported operational entry points
  paper/                         existing benchmark replay API, initially retained
  architecture/                  existing generators and manifests
  trace_explorer/ / observatory/  retain until their consumers are classified
frontend/                         shared UI; benchmark views and new patient views
configs/{gan2026,exectv2,longitudinal}/
tests/                            current checks plus new behavior checks
scripts/{checks,benchmarks,longitudinal,publications}/
examples/{gan2026,exectv2,longitudinal}/
publications/
  dissertation/                  current paper sources, supporting materials, notes
  exect-comparison/               only when an actual manuscript is created
  longitudinal-benchmark/         only when an actual manuscript is created
results/
  letter-benchmarks/              existing paper_experiments subtree, intact initially
  longitudinal/<version>/<study>/ reviewed results and reproducibility metadata
runs/                             ignored execution outputs, organised by study
  archive/                       local historical runs required for provenance
scratch/                          ignored transient and quarantined working material
data/                             local-only; versioned release exports are separate
  sources/{gan2026,exectv2}/       source copies + preserved IDs and split provenance
  longitudinal/<version>/         generated letters, annotations, splits, QC
media/<purpose>/                  local production assets; served exports in frontend
literature/                       local reading copies; no automatic redistribution
docs/
  README.md / NAVIGATION.md       brief entry and ownership map
  plans/ACTIVE_ROADMAP.md         this plan, the sole roadmap
  longitudinal/                  annotation, generation, evaluation and task definition
  benchmarks/{gan2026,exectv2}/   retained dataset-specific policies and limitations
  design/                        shared software/evidence design
  research/{gan2026,exectv2,longitudinal,shared}/  protocols and result interpretation
  architecture/                  generated implementation reference until recategorised
  reference/                     terminology and literature synthesis
  runbooks/                      repeatable operations
  history/                       superseded guidance, scoped and dated
```

Create a directory when its first owned artifact exists. Dataset release packaging
and storage are decided after volume and sharing review; the target tree does not
authorise committing full raw runs, private source material, or hidden test gold.

### Disposition and dependency map

| Current location | Proposed disposition | Dependencies and completion evidence |
| --- | --- | --- |
| Root `README.md`, `AGENTS.md`, status and glossary | Retain names; make new direction primary and old task terms explicitly scoped | One active plan; public README does not require ignored files to explain the project |
| `paper/` | Move to `publications/dissertation/`; classify draft, final, reference/template and historical material within it | TeX image/bibliography paths, supporting-material links and figure builders; build and visually inspect affected PDFs; preserve earlier output provenance |
| `paper_experiments/` | Move as one unit to `results/letter-benchmarks/` before attempting any internal split | Inventory/roster pointers, replay commands, tests, panel APIs, figure builders and stored path strings; retain schema and method IDs |
| `src/clinical_extraction/paper/` | Keep import/CLI compatibility initially; scope it as existing benchmark runners | `python -m clinical_extraction.paper`, imports and external users must keep working; no cosmetic global rename |
| `src/.../tasks/`, `core/`, `operational/` | Retain; add longitudinal implementation separately after the first example | Reuse evidence/provider/IO code only where semantics match; Gan/ExECT scoring rules cannot become universal clinical rules |
| `src/.../trace_explorer/`, `observatory/`, `architecture/` | Keep working consumers; classify overlaps before consolidation | API routes, generators, caches, demo fixtures and manifest callables; do not rewrite these systems merely to match folder labels |
| `tests/` | Retain existing checks; regroup only alongside the code they exercise | Pytest paths, fixture locations, local-corpus skips and capped deep allowlist; no mass test deletion |
| `configs/` | Retain dataset namespaces; add longitudinal configurations when executable | Embedded protocol/output paths and old full200 study configs; existence never grants permission to run locked data |
| `scripts/` | Group checks, benchmark runners, longitudinal tools and publication builders | CI, pre-commit hooks, PowerShell/shell relative roots, `scripts.*` imports and documentation commands must migrate together |
| `examples/vllm_gan_three_letters.jsonl` | Move to `examples/gan2026/`; keep pinned contents; add separately labelled longitudinal example later | `VLLM.md`, operational walkthrough, commands and tests; preserve external command compatibility during transition |
| `frontend/` | Retain application; separate benchmark results, authored simulations and extracted patient histories in the UI | Existing dirty/untracked user files are preserved; browser QA of old workbench and new patient loop; no reclassification of authored simulation as benchmark output |
| `data/` | Group source corpora and new dataset versions after loader/split references are mapped | Exact source IDs, split manifests, loaders, ignore rules; old locked rows remain sealed and are excluded from seed selection |
| `experiments/` | Sort into study run folders under ignored `runs/`; preserve referenced old runs in `runs/archive/` | Embedded artifact paths, registry entries, retained-evidence hashes and the tracked exception; scan metadata/callers, not locked row failures |
| `scratch/`, `logs/`, `tmp/`, `.tmp/`, `.trace_explorer/` | Keep local operational roles; retire only confirmed regenerable residue | Some scratch paths are holdout storage or sole saved outputs; do not delete by age/name alone; restore app indexes when paths change |
| `media/` and `docs/audio/` | Keep local source assets by purpose; archive obsolete story productions locally | Source-letter provenance, audio project dependencies, app imports/served exports; preserve local-only visibility |
| `literature/`, `docs/literature/` | Retain local reading copies; put authored synthesis under `docs/reference/` | Separate copyrighted copies, authored reviews and publication templates; do not turn ignored PDFs into tracked files during consolidation |
| `docs/paper/`, `docs/research/paper/` | Put manuscript-specific prose under publication notes; shared benchmark policies under `docs/benchmarks/`; keep research evidence under `docs/research/` | Classify file by purpose; existing Gan manuscript and wider ExECT tables have different claim owners; repair incoming links before removal |
| `docs/history/canon/`, `docs/history/decisions/` | Retain historical guidance only for a named use; migrate still-applicable safeguards into active owners | The old canon is already superseded; preserve rationale and code/test callers; avoid a second live claim register |
| `docs/design/`, `reference/`, `runbooks/` | Keep shared content; relocate dataset-only policy to its benchmark home | Some procedures contain old model/split permissions; make scope explicit before reusing |
| `docs/research/`, `docs/experiments/` | Consolidate study prose into `docs/research/<track>/`; retain required evidence; remove superseded narrative when Git suffices | 271 research Markdown files and 73 experiment Markdown files need file-level classification; no wholesale deletion based on directory |
| `docs/architecture/` | Keep generated reference in the first migration; re-scope only through generator changes | `scripts/build_architecture_docs.py` and `tests/test_architecture_stage_manifests.py` enforce generated content |
| `docs/plans/` | This roadmap remains active; remove superseded plans unless a continuing use requires them | Supersede old paper-only pruning instructions; no renewed authorisation for old experiment queues |
| `.github/`, `.pre-commit-config.yaml`, `.gitignore`, package manifests | Retain; update with each affected move | Clean public-checkout CI, tracked/local boundaries, packaging and path discovery |
| `.env`, `.venv/`, caches, `.skills/`, `.worktrees/` | Keep as environment state outside content reorganisation | No credential inspection, virtualenv move, worktree deletion or dependency churn |

Known hard callers include `src/clinical_extraction/paper/{gan,exect,gan_panel,exect_panel}.py`,
`gan_cell_replay.py`, `exect_cell_replay.py`, `gan_result_figures.py`, the operational
CLI, `scripts/build_*`, `tests/test_paper_*`, panel tests, and CI's documentation
hygiene paths. Use these as starting points; Phase 0 still requires a complete
per-move caller search, including JSON metadata, TeX, TypeScript and ignored local
configuration. Do not enumerate or print locked row content to find path strings.

### Documentation reduction decision (2026-09-13)

Conor approved substantial documentation reduction as a migration outcome.
Moving prose into an archive does not count as reducing it. Keep concise current
owners, necessary reproducibility evidence and references with a named use;
consolidate duplicate explanations and remove superseded tracked narrative when
Git history is sufficient. The documentation lifecycle owns the retention rules.

Complete the remaining research/experiment file classification in bounded groups.
For each group, record keep, consolidate or remove and the reason in the existing
migration record, check consumers and provenance, then apply the disposition.
Retain an on-disk archive only for a specific continuing use. Protect original
protocols and result interpretation needed by retained evidence, generated
references with consumers, and sole local copies. Do not impose an arbitrary
percentage or delete a directory merely because it is old.

Completion requires applied dispositions for the remaining study documents,
resolved competing guidance, and before/after file and line counts for each cut.
The migration record owns those counts and recovery references. The first cut is
implemented there; broader classification remains open.

### Migration procedure and acceptance

1. **P0.1 Baseline and ownership.** Record dirty files, active writers, tracked and
   ignored paths, selected output hashes, replay commands and baseline check
   results. Verify the state of the previously reported September 5 hosted runs
   before moving any directory they might write to. Do not infer completion from
   the old status log. Preserve current frontend work and the user's deleted
   `FES.out`/`FES.pdf`; do not restore them to make the tree clean.
2. **P0.2 File-level disposition.** Expand the table into a migration mapping for
   each moved file: source, destination, purpose, callers, visibility, byte hash,
   and rollback location. This is a migration artifact, not a new evidence/claim
   register. Audit reference and licensing boundaries before any public export.
3. **P0.3 Representative move.** Move the pinned Gan example with its callers;
   verify the walkthrough without a paid model call. Prove the mapping/check
   approach on this bounded slice before spreading it.
4. **P0.4 Documentation and publications.** Rehome manuscript assets and obsolete
   guidance. Update TeX, builders and links in the same slice. Keep already-issued
   manuscript outputs identifiable. Do not rewrite scientific results while moving.
5. **P0.5 Results and run paths.** Introduce explicit artifact-root resolution,
   then migrate `paper_experiments/` and referenced local runs. Support one
   canonical writable location; temporary read compatibility must have a removal
   condition. Preserve raw-output bytes and version IDs; record old-to-new paths
   separately rather than silently rewriting provenance inside immutable records.
6. **P0.6 Helpers and data.** Group scripts and configs, repair CI/imports, then
   move source data only when loader and split references are covered. Keep
   public-safe manifests separate from private files. Verify ignore rules before
   adding anything to Git. Shared package and frontend roots remain in place.
7. **P0.7 Verify and close.** Compare hashes and aggregate replay outputs; verify
   supported CLI/API paths, public-checkout behavior, affected PDF builds and UI
   flows, link integrity, generated-doc consistency and package checks. Inspect
   only permitted development examples; holdout remains aggregate-only. Record
   any pre-existing failures separately and resolve migration-induced failures.

Rollback each slice using the recorded move mapping and preserved bytes; never
use a hard reset or a clean command against the user's working tree. Keep the
prior path readable until its dependent readers are migrated, then remove the
compatibility path. Hash equality proves bytes survived; it does not prove
runtime behavior, so both checks are required.

Phase 0 ends when the selected layout is implemented, required checks pass, old
results remain reproducible, the documentation has one current owner per concern,
and a new longitudinal example has an unambiguous destination. Planning this map
alone does not complete Phase 0. If a move proves disproportionately disruptive,
record a bounded retained-path exception and its reason here instead of inventing
another migration project or blocking the pilot on cosmetic package renaming.

### Migration progress

- **Slice 1 (P0.1–P0.3)** executed on 2026-09-08: baseline captured (with PID 26725
  identified as a live runner targeting `experiments/paper/gan_llm_extract_encode_select/`),
  partial file-level mapping created (covering P0.3 exact move and group proposals; full
  mapping remains in progress), and `examples/vllm_gan_three_letters.jsonl` relocated
  to `examples/gan2026/vllm_gan_three_letters.jsonl` with callers and walkthroughs updated.
  See the tracked migration record at
  [`docs/research/maintenance/repository_migration_2026-09-08.md`](../research/maintenance/repository_migration_2026-09-08.md).
- **Slice 2 (P0.4 publication materials move)** executed on 2026-09-08: all 55 tracked
  manuscript and supporting files moved intact from `paper/` to `publications/dissertation/`
  with byte parity verified, filesystem callers updated (`FIGURE_DIR` in `gan_result_figures.py`,
  template path in `test_gan_extract_label_forms_prompt.py`), active Markdown links updated,
  and PDF compilation behavior verified before/after the move.
- **Slice 3 (P0.4 plan archive)** executed on 2026-09-08: four obsolete historical plans
  (`assembly_line_one_fact_2026-08-18.md`, `exect_llm_representation_and_hybrid_revaluation_2026-08-16.md`,
  `exect_prompt_fundamentals_2026-08-16.md`, `paper_final_repo_scope_2026-08-17.md`) moved
  from `docs/plans/` to `docs/history/plans/` with historical prose preserved, top archival notices
  added, relative links rebased, incoming links updated, and `ACTIVE_ROADMAP.md` preserved as the
  sole active plan.
- **Slice 4 (P0.4 guidance archive)** executed on 2026-09-09: all 13 files in `docs/canon/`
  moved to `docs/history/canon/` and all 42 files in `docs/decisions/` moved to `docs/history/decisions/`
  with archival headers, rebased links, and updated manifest/code references.
- **Slice 5 (P0.4 research notes & sections)** executed on 2026-09-09: all 35 files in `docs/research/paper/`
  rehomed to `docs/research/gan2026/`, `docs/research/exectv2/`, and `docs/research/shared/`;
  draft manuscript sections relocated to `publications/dissertation/notes/sections/`;
  `docs/benchmarks/gan2026/` and `docs/benchmarks/exectv2/` established for retained benchmark policies.
- **Slice 6 (P0.5 results & run paths)** executed on 2026-09-09: all 283 files in `paper_experiments/`
  relocated to `results/letter-benchmarks/` with git history preserved; explicit artifact-root
  resolution helper `resolve_letter_benchmarks_root()` introduced in `src/clinical_extraction/core/paths.py`;
  read-compatibility symlink `paper_experiments -> results/letter-benchmarks` maintained.
- **Slice 7 (P0.6 helpers, configs, data, runs)** executed on 2026-09-09: target directories created
  and documented (`configs/longitudinal/`, `examples/{exectv2,longitudinal}/`,
  `scripts/{checks,benchmarks,longitudinal,publications}/`, `data/sources/{gan2026,exectv2}/`,
  `data/longitudinal/`, and ignored `runs/archive/`); `/runs/` added to `.gitignore`.
- **Phase 0 review correction (2026-09-09)**: The directory scaffolding above does
  not mean every proposed move was executed. Current callers now use
  `results/letter-benchmarks/`; saved provenance strings remain unchanged.
  Verification and retained-path exceptions are recorded below and in the
  migration record. Phase 1 planning can proceed; broad Phase 0 closure is not claimed.

### Retained paths and compatibility removal

- Keep existing scripts in `scripts/` and executable configurations in their
  current dataset namespaces. The new script directories are destinations for
  future tools, not a completed regrouping. Moving the existing helpers would
  require coordinated CI, shell/PowerShell, import and command changes without
  changing the longitudinal pilot outcome. Revisit each helper when it changes.
- Keep source corpora under their existing `data/` paths until a separate move
  verifies loader references, source IDs and split manifests. New source/data
  directories are scaffolding only; no corpus relocation is claimed.
- Keep historical runs in `experiments/` and protected scratch paths. Their
  references and writer ownership have not been fully mapped; the baseline
  identified a live writer. `runs/archive/` is a destination, not an executed
  archive. Recheck writers and record a per-file mapping before any later move.
- Keep the tracked `paper_experiments` symlink solely for historical saved paths
  and external consumers. Current source, API and script path literals use the
  canonical results directory. The symlink is not a filesystem permission barrier.
  Remove it only after a separate old-to-new path mapping resolves saved artifact
  references without changing their bytes, external supported commands are
  accounted for, and replay/API checks pass in a checkout without the symlink.
- Broader study-document classification remains unfinished. The executed archives
  and research-note moves do not establish one current owner for every historical
  concern. Resolve remaining conflicting active guidance before claiming full
  documentation consolidation.


## Longitudinal timeline and dependencies

Indicative elapsed working weeks from the start of execution, assuming one primary
researcher with implementation assistance. Re-estimate after Phase 0 and the pilot.
These are planning allowances, not committed dates. Partner review, annotation
capacity, real-data access and publication introduce external calendar time.
No deadline or model budget has been supplied.

| Phase | Window / effort allowance | Depends on | Required outcome | Accountable owner |
| --- | --- | --- | --- | --- |
| 0. Restructure repository | W1–2 / 5–10 working days | Current plan | Verified migration with replay and visibility preserved | Conor + implementation contributor |
| 1. Define research tasks | W3 / 3–5 days | P0 | Bounded questions, prior-work comparison, success criteria | Conor |
| 2. Design annotation through cases | W4–5 / 7–10 days | P1 | One worked patient, then 12-patient annotated development pilot | Conor; clinical input if available |
| 3. Build generation and QC | W6 / 4–5 days | P2 | Reproducible small generation batch, checked against final text | Implementation contributor; Conor reviews |
| 4. Complete functional prototype | W7–8 / 7–10 days | P2–3 | Letters → evidence → both patient views → cohort answer | Implementation contributor |
| 5. Review and revise pilot | W9 / 3–5 internal days plus reviewer time | P4 | Internal review and, when available, clinician feedback with decisions | Conor; prospective clinical reviewers |
| 6. Freeze and generate corpus | W10–11 / 7–10 days | P3–5 internal decisions | Versioned ~300-patient provisional corpus and sealed test partition | Conor + implementation contributor |
| 7. Compare pipelines | W12–13 / 7–10 days | P6 and frozen evaluation protocol | Reproducible component and downstream results | Conor + implementation contributor |
| 8. Obtain expert reference | W14 onward / capacity-dependent | P5 collaboration; P6 materials | Independent annotation, adjudication and reference-quality report | Clinical annotation lead, once agreed |
| 9. Release and paper | After P7; claims depend on P8 | Release checks and chosen claim level | Versioned research release and bounded manuscript | Conor; coauthors if agreed |
| 10. Evaluate real-record transfer | Separately scheduled | Partner/access arrangements; frozen candidate | Independently evaluated real longitudinal cohort | Clinical/data partner + Conor |

Phases 1–4 can proceed without a clinical partner. If external feedback is late,
internal pilot findings can support continued synthetic development; record that
clinical design review is missing. Expert-reference claims require Phase 8.
Real-record transfer claims require Phase 10. Scale-up can be delayed if the pilot
shows fundamental ambiguity or unacceptable annotation effort.

## Phase tasks and evidence of completion

### Phase 1 — Define the questions and scope

- P1.1 Compare the attached Xie, ExECT/ExECTv2, Gan, Chang and temporal-reasoning
  work with available longitudinal benchmarks. Verify bibliography and current
  publication versions. Distinguish existing longitudinal applications from
  explicit cross-letter annotation/evaluation. Do not claim first or better yet.
- P1.2 Define cohort questions, their index dates, follow-up windows, eligibility,
  missing-data policy and allowed evidence. Choose a primary downstream endpoint
  before comparing models; retain extraction/linking metrics as explanatory tests.
- P1.3 Specify the two views precisely: only information available by the cutoff
  for the visit account; later evidence permitted and attributed retrospectively.
  Clarify clinic date versus document availability date, delayed letters, and
  missing/partial dates. Known patient IDs are supplied; patient matching is out.
- P1.4 Resolve seed eligibility: existing ExECT `dev140` cannot supply 150 distinct
  seeds. Choose additional permitted source material, fewer unique seeds with
  disclosed reuse, or a revised allocation. Never use `test60`/`test450` to fill
  the gap. Audit source terms and duplicate lineage before generation or sharing.
- P1.5 Set the coverage matrix, model budget, sampling rationale and evidence
  thresholds for scaling. Record the 300-patient target as provisional.

Completion: one task definition and literature rationale under `docs/longitudinal/`
and `docs/reference/`; every proposed annotation field has a downstream purpose.

Phase 1 work on 2026-09-09 produced the
[task definition](../longitudinal/task_definition.md) and
[literature rationale](../reference/longitudinal_epilepsy_rationale.md).
P1.2–P1.3 are specified for the worked example. P1.4 adopts a revised candidate
allocation; actual source matching and duplicate-lineage auditing remain required
before source-conditioned generation. P1.5 defines coverage, scaling conditions
and a £0 paid-call default pending a later pilot budget. P1.1 now includes the
supplied Chang et al. preprint (22 February 2026), including its majority-phenotype
aggregation and diagnostic-transition analysis. The working documents are ready
for P2.1. No model comparison, new corpus or expert validation is claimed;
source-use/lineage checks and any paid budget remain prerequisites for generation.

### Phase 2 — Design annotation through patient examples

- P2.1 Author one three-letter patient and expected answers in both views. Include
  concurrent patterns, a medication plan not enacted, and later reinterpretation.
- P2.2 Draft the minimal annotation guide. Specify patient/letter/mention IDs,
  source spans, assertion source/certainty/negation, event time versus documentation
  time, and links for repetition, updates, corrections and unresolved conflict.
- P2.3 Define family-specific meanings: seizure identity separate from diagnosis;
  bounds/ranges/count intervals separate from point rates; clusters separate from
  events per cluster; type-specific absence separate from global seizure freedom;
  drug prescription/plan/use separate; investigation request/performance/result
  separate. Missing information is not absence or cessation.
- P2.4 Define conservative linkage and conflict rules. Different time windows or
  seizure types are not contradictions. An apparent correction needs evidence;
  uncertain identity may remain unresolved. Repeated text is not independent
  corroboration. Preserve author/reporter disagreement rather than voting it away.
- P2.5 Expand to 12 patients and 36 letters covering ordinary unchanged follow-up,
  copied history, change of terminology, sparse dates, contradictory reports,
  no-reference letters, irregular follow-up and missing outcomes. Do not put every
  difficulty in every letter. Separate text-supported reference from hidden
  generation truth and record multiple acceptable answers where justified.
- P2.6 Dry-run annotation and scoring with a second independent pass. Measure
  time and disagreement by family, time field and relationship; identify costly
  fields that do not change any query. Revise before implementing the full schema.
  Audit model-facing schemas/instructions with the plain-language prompt skill.

Phase 2 completion (2026-09-10, v0.8): the inspectable 12-patient/36-letter pack,
240 fixed query answers, paired provisional guide/schema v0.3 and internal coverage
acceptance are verified. All 144 flagged temporal pairs and all 89 formerly
unaligned link instances have review dispositions. Explicit alternatives and
unsupported observed inferences remain visible; no clinical agreement is inferred.

The original independent pass retains 44 outputs and four failures. A new
18-call agy probe measures wall time and disagreement across four families and
focused temporal/relationship tasks for patients 002, 006 and 011. All calls
returned JSON; 17 outputs satisfy the schema, 16 pass grounded structure checks
and nine pass exact-offset checks. Total call wall time is 23.6 minutes; human
annotation time is unmeasured. The user confirmed no per-call charge for agy;
no paid API fallback ran. Source-attribution alternatives and new probe differences
remain explicit development limits.

Nine-variant query replay matches 229/240 authored answers; Q5 matches 48/48,
including all four requests for patients 001 and 011. A supported complete-prior-
history field resolves four Q3 gaps without inventing dates. The 11 remaining
conservative indeterminate answers are named Phase 4 implementation cases. A full
query evaluator and expert reference are later-phase work, rather than implicit
conditions for this provisional-schema phase. Earlier status text overstated them
as Phase 2 blockers.

The [pilot review](../longitudinal/pilot_disagreement_report.md) owns the completion
decision, timing/quality results, unresolved cases and verification. The
[v0.8 evidence package](../../results/longitudinal/pilot_v0.8/README.md) supplies
replay commands and source hashes. Focused checks pass (23 tests); the full suite
reports 803 passes and the same two unrelated benchmark documentation/inventory
failures. Ruff and mypy pass. Historical dated notes below retain earlier states.

Completion: inspectable case pack, annotation guide, provisional schema and query
answers with explicit unresolved cases. The pilot is development evidence, not
expert gold. Guide and schema have one owner each and version together.

P2.1 on 2026-09-09: [authored patient 001](../../examples/longitudinal/authored_patient_001/README.md)
contains three seed-free fictional letters, 20 provisional answers and four
physically filtered input sets. Checks cover evidence spans, source hashes, date
arithmetic and cutoff eligibility. Task definition v0.2 records the query
clarifications exposed by the example.

P2.2–P2.4 on 2026-09-09: [annotation guide v0.1](../longitudinal/annotation_guide.md)
and its paired provisional schema cover the four families, temporal uncertainty,
source evidence and conservative relationships. The worked example has 35
assertions and 10 links checked for structure, spans, bounds and references.
Clinical entailment and complete executable query coverage remain unverified.

P2.5–P2.6 correction on 2026-09-09: the [12-case pack](../longitudinal/pilot_coverage_matrix.md)
retains 36 original fictional letters and now uses the fixed task-v0.2 schedule,
exact filtered inputs, corrected query references and annotations across all letters.
The [pilot review](../longitudinal/pilot_disagreement_report.md) records 202 assertions,
44 relationships, outstanding coverage and a reproducible reference summary with
constant-answer baselines. Earlier agreement, timing and sensitivity numbers were
hard-coded and have been withdrawn. Coverage acceptance, an independent annotation
pass, measured disagreement/effort and a field-utility comparison remain open.
Phase 2 is not complete; schema v0.1 remains provisional.

P2.5 coverage revision v0.3 on 2026-09-09: five cases intentionally revised with
prior files retained. The coverage matrix maps every task minimum to authored
content; every query has at least two of each status. Forty-eight reference-free
jobs are prepared for the independent pass. None has been run; P2.6 remains open.


### Phase 3 — Generate and check synthetic records

Complete (2026-09-11): the [generation record](../../results/longitudinal/generation_v0.1/README.md)
contains twelve accepted seed-free patient records, 36 letters, 114 assertions,
39 relationships and 240 query references. The [generation protocol v0.3](../longitudinal/generation_protocol.md)
and [execution configuration](../../configs/longitudinal/generation_v0.1.json)
govern the completed 1 → 5 → 12 stages. Raw attempts, rejected drafts, revisions
and internal reviews remain local; reviewed fictional cases and hashes are saved
with the result. Every accepted case regenerated byte-for-byte.

Four scenario types are crossed with three writing styles, with one conservative
shared development family. All 426 assertion/link/answer/diagnostic review items
have dispositions. A one-day evidence gap changed three unsupported negative
answers to indeterminate without changing the letters. Final status counts are
54 eligible, 39 ineligible and 147 indeterminate. The incomplete evaluator matches
207/240; all 33 differences remain named development cases, including three harmful
positives after a documented diagnosis withdrawal. Agreement did not filter cases.

P3.1–P3.5 are implemented and verified for same-assistant seed-free authoring and
saved-output replay. No separate provider calls occurred. Generation/resume code
enforces disabled providers, unchanged inputs and recorded review before expansion.
Source-conditioned generation remains disabled; release matching, upstream ancestry
and unresolved Gan terms must be addressed before any seeded batch. Human effort,
independent clinical annotation and fresh stochastic reproducibility are not claimed.
The focused suite passes 26 tests; Ruff, mypy, documentation hygiene and Phase 2
preservation checks pass. The full suite has 806 passes and the same two pre-existing
benchmark documentation/inventory failures. This is scoped Phase 3 completion,
not a claim that all repository checks pass.

- P3.1 Specify generation as patient history → consultation documentation →
  seed-informed letter → reference checked against the finished letter. Model
  names, prompts, randomness, source lineage and revision history are recorded.
- P3.2 Separate clinical scenario from writing style. Vary length, shorthand,
  uncertainty, omissions, repeated text and consultation gaps. Do not create
  deterministic links between seed source/style and clinical outcome.
- P3.3 Implement IDs, versioning, validation, resumable generation and cost limits.
  Run one patient, five patients, then the small pilot batch; inspect each stage
  before increasing volume. Retry failures without silently dropping hard cases.
- P3.4 Check evidence spans and semantic support, temporal plausibility, bounds,
  duplicate text/seed families, contradiction provenance and query answerability.
  An independent model may flag issues but cannot establish clinical correctness.
- P3.5 Preserve raw generations, edits, rejected outputs and rejection reasons in
  local run records. Accept uncertainty where it is intended; avoid filtering the
  corpus to only cases a teacher/extractor can agree on.

Completion: regenerate a small batch from saved configuration, trace every
accepted reference to final letter evidence, and explain failed or revised cases.

### Phase 4 — Build one full user loop

Complete for the local saved-output prototype (2026-09-11). The
[Phase 4 record](../../results/longitudinal/prototype_v0.1/README.md) owns the
implementation evidence, component comparison and verification. P4.1 reuses 44
actual model extractions with input hashes and retains four failed captures;
changed/unseen inputs are rejected. P4.2–P4.4 implement the separate stages and
`/longitudinal` viewer, including explicit reference/prediction modes. Reference
facts with inferred links reproduce 480/480 provisional answers across both packs;
removing links gives 440/480. Predicted facts give 190/240, including 20 failed
requests and one unsupported definitive answer. Link precision/recall and alignment
coverage remain separate from query agreement. P4.5–P4.6 include component artifacts,
regression checks and browser verification of both views, keyboard evidence
navigation, mobile layout, empty cohorts, capture failure and retry/recovery.

The new evaluator resolves the eleven v0.8 gaps and 33 Phase 3 mismatches while
preserving the frozen diagnostics and references. This is a development fit, not
clinical validation. A fresh extraction provider and deployment are outside the
saved-output prototype. Phase 5 reviews the remaining semantic and identity limits
before any larger generation or scoring freeze.

- P4.1 Load letters and extract evidence-supported facts with versioned outputs.
- P4.2 Link patient-specific events and assemble both histories. Keep extraction,
  normalisation, linking, semantic repair and downstream query policy separable.
- P4.3 Implement cohort queries, including the 11 explicit v0.8 mechanism cases
  in the pilot review and the 33 Phase 3 diagnostic mismatches, with cutoff dates, observation windows,
  unknown/indeterminate results and supporting evidence. Do not infer treatment
  causality from before/after frequency changes.
- P4.4 Extend the existing frontend with a patient selector, ordered letters,
  visit/retrospective switch, evidence navigation, and a cohort query view. Show
  ambiguity, empty results, loading/failure and retry paths. Clearly identify
  authored examples, generated annotations and actual pipeline predictions.
- P4.5 Evaluate linking with reference letter annotations as input as well as
  predicted input, isolating extraction errors from history reconstruction errors.
- P4.6 Run automated checks and browser QA with keyboard navigation and readable
  evidence displays. Demonstrate a later correction changes the retrospective
  answer while leaving the earlier as-known answer reproducible.

Completion: a reproducible 12-patient demonstration with one complete cohort task
and both temporal views. No clinical validation or deployment claim.

### Phase 5 — Review before large-scale generation

- P5.1 Prepare a short collaborator pack: research question, worked cases, guide,
  functioning demo, known ambiguities, annotation-time estimate and concrete ask.
- P5.2 Conor chooses contacts and authorises outreach to prospective King's or
  Swansea collaborators. No partner commitment is assumed by this plan.
- P5.3 Obtain feedback on clinical distinctions, longitudinal usefulness,
  annotation burden, plausible letters, and missing cases. Record reviewer role
  and scope; internal review remains separately labelled if experts are unavailable.
- P5.4 Revise the schema, query definitions and pilot together. Decide proceed,
  revise or reduce scope using the Phase 1 criteria. Keep disagreements visible.

Completion: recorded design decisions and remaining limitations. Unavailable
reviewers delay expert validation, not reversible prototype work.

### Phase 6 — Freeze the provisional dataset and scale

- P6.1 Freeze annotation/generation/QC versions and split policy. Split at patient
  and seed-family level; keep duplicates, paraphrases and reused seed descendants
  together. Audit pre-existing source duplication before assigning partitions.
- P6.2 Set train/development/test counts based on the final eligible patient count,
  coverage and required precision. Keep pilot cases in development. Seal test
  letters and labels from pipeline developers; route test QC through an independent
  reviewer or controlled process. Cases inspected for development cannot be test.
- P6.3 Generate in bounded batches to the agreed target; monitor cost, time, rejection
  rate, clinical scenario coverage and style balance. Record every exclusion.
- P6.4 Produce the dataset card, machine-readable manifest, checksums, generation
  provenance, data dictionary and query reference. Clearly label provisional AI
  annotations; keep hidden generation truth separate from public task inputs.
- P6.5 Review what can be shared, what stays local, and what is withheld for test
  evaluation. Do not inherit source-corpus publication permission by assumption.

Completion: a versioned, reproducible synthetic corpus with known counts,
provenance, coverage and protected splits. Expert annotation is still separate.

### Phase 7 — Compare approaches and attribute differences

- P7.1 Predeclare the primary endpoint, baseline configurations, model versions,
  prompts, scorer, failure/abstention handling and frozen test-use policy.
- P7.2 Compare latest-letter-only, independent letter extraction with simple
  aggregation, one model reading all available letters, and the linked-history
  pipeline. Give each approach the same permitted time cutoff. Where possible,
  share extraction outputs and hold models/budgets fixed to isolate linking.
- P7.3 Report extraction, qualifiers/time, linking, evidence support and downstream
  answers separately. Score both temporal views, including unresolved cases and
  unjustified certainty. Do not report only a single micro-F1 over all attributes.
- P7.4 Run ablations for cross-letter links, repeated-text handling and later
  corrections. Inspect rescues and harms on development cases only. Include style
  transfer and simpler/ordinary histories as well as difficult slices.
- P7.5 Estimate uncertainty with patient/seed-family dependence respected. Report
  subset denominators, coverage, cost, latency, parse failures and annotation source.
- P7.6 Freeze candidates before locked evaluation; report permitted aggregates.
  A discovered holdout defect starts a new development candidate/dataset version;
  it does not permit silent repair and retesting of the same claim.

Completion: machine-readable results, reproducible report, bounded interpretation
and a decision on what improved. AI-reference results measure performance against
that provisional reference; they do not establish clinical accuracy.

### Phase 8 — Establish an expert reference

- P8.1 Agree clinical reviewer roles, compensation/capacity, annotation scope,
  training examples, adjudication procedure and data handling arrangements.
- P8.2 Independently double-annotate a prespecified sample without exposing AI
  suggestions in the primary agreement measurement; use development cases for
  training. If assisted annotation is studied, report it as a separate condition.
- P8.3 Measure agreement and effort by fact family, temporal relation, patient
  linking and query answer; adjudicate disagreements and audit guideline changes.
- P8.4 Release a new reference version with provenance and rerun frozen systems.
  If only a subset receives expert annotation, report that subset explicitly;
  do not label all 300 patients expert-annotated.

Completion: expert-reviewed synthetic reference with measured agreement and
limitations. This does not establish transfer to real clinic records.

### Phase 9 — Publish a reproducible research package

- P9.1 Decide the release scope and destination: provisional synthetic resource or
  expert-annotated benchmark. Freeze claim wording to the evidence actually obtained.
- P9.2 Package allowed letters/annotations, splits, scorer, baselines, documentation,
  limitations and provenance; define access to held-out labels and contamination
  implications. Verify installation and examples in a clean environment.
- P9.3 Write the longitudinal paper in its own publication directory. Link claims
  to versioned results; preserve the prior dissertation and ExECT comparisons.
- P9.4 Review artifacts, source terms, identifiers, accessibility of the demo,
  reference quality and reproducibility. Conor confirms audience/destination and
  external publication before release; record version/DOI only after issued.

Completion: a released resource and manuscript with explicit synthetic/expert/real
claim boundaries. Publishing a resource is distinct from acceptance of a paper.

### Phase 10 — Evaluate transfer to real longitudinal records

- P10.1 Agree access, governance, patient-level sampling, independent annotation
  and evaluation responsibilities with a clinical partner. Raw records can remain
  at the institution with only approved aggregate outputs returned.
- P10.2 Freeze the pipeline, schema and evaluation before evaluation access. Define
  how clinical differences, missing follow-up and unavailable information are scored.
- P10.3 Report external cohort results, distribution differences and limitations.
  Keep changes motivated by real test failures in a new development protocol.

Completion: evidence on a named real cohort. Clinical workflow validation and
production deployment remain separately scoped future work.

## Owners, verification and risk controls

During migration, active pointers use existing paths. After migration, update this
map rather than leaving competing owners:

| Concern | Current or planned owner |
| --- | --- |
| Scope, timeline, migration | This document |
| Current task state and check results | `PROJECT_STATUS.md` (local-only) |
| Navigation and document roles | `docs/NAVIGATION.md`, `docs/runbooks/documentation_lifecycle.md` |
| Longitudinal task, annotation, generation, evaluation | `docs/longitudinal/` files created in Phases 1–3 |
| Existing paper argument | `docs/paper/README.md`, then publication-specific notes |
| Existing machine evidence | `paper_experiments/inventory.json`, then preserved results inventory |
| New study protocol and report | `docs/research/longitudinal/<study>/` when a study starts |
| New run records and reviewed results | local `runs/`; reviewed `results/longitudinal/` after migration |

Before broad engineering completion, activate `.venv` and run `python -m pytest`,
`python -m ruff check src tests`, `python -m mypy src`, and the documentation hygiene
check. Use the documented frontend checks and browser QA when it changes. Run only
focused checks during iteration; deep pytest is the capped allowlist, not routine.
No expensive model call, broad artifact regeneration or locked-row inspection is
needed merely to plan or document this work.

### Review-oriented explanation after major changes

After a major architecture change, repository reconstruction, dataset/evaluation
redesign or multi-stage pipeline change reaches a reviewable state, produce a
visual PDF that helps collaborators understand the core logic at a deliberate
pace. The staged-reconstruction PDF is the first example of this practice. A useful
review PDF should:

- explain the motivating problem and the before/after system shape;
- diagram the important data, evidence, replay and decision flows;
- include short excerpts from the actual code, schema or configuration at the
  boundaries where behaviour is determined;
- distinguish implemented, verified, validated and still-open work; and
- be readable on a tablet, with every page rendered and visually inspected before
  handoff.

This PDF is a derived communication artifact, not a new source of requirements,
results or claims. Update the canonical plan, status, decision and evidence owners
first; generate the explanation from those owners and the implemented code. Do not
let the PDF replace tests, run manifests, method documentation or a required
decision record.

Main risks and responses:

- **Migration breaks reproducibility:** baseline hashes plus no-call replay; move
  callers and assets together; retain existing CLI and schema identities.
- **Local data becomes public:** inspect tracked status and ignore behavior before
  every move; export from an explicit reviewed allowlist, not the working tree.
- **New schema recreates annotation burden:** use one patient, then the pilot;
  measure effort/disagreement and remove fields without a question they support.
- **Generator teaches the benchmark its own assumptions:** separate hidden history,
  documented evidence, independent review, scenario/style factors and scoring.
- **Leakage through patient relatives, time or development review:** group seed
  descendants; enforce cutoff inputs; independently review sealed test material.
- **Overstated usefulness:** test cohort answers directly; distinguish synthetic
  reference agreement, expert-reviewed synthetic accuracy and real-record transfer.
- **Scope expansion:** keep prediction, broad patient-history mining, new diagnoses
  inferred from investigations, and clinical deployment outside the first release.

Pre-change tracked plans remain recoverable at `8da94df5`. The old ignored status
and glossary were preserved locally in
`scratch/project-history/2026-09-08-before-longitudinal-plan/`. Neither historical
plan text nor an old queue entry authorises resuming experiments under this plan.
