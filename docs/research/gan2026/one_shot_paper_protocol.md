# One-call extraction evaluation protocol

Owner: Conor Brown. Reorganised 2026-09-14; study permissions and frozen results are unchanged.
This document owns the study question, datasets, comparisons, endpoints and readiness.
The [roadmap](../../plans/ACTIVE_ROADMAP.md) owns priorities and the
[paper outline](../../../publications/jamia-one-shot/README.md) owns the manuscript.

| Need | Document |
| --- | --- |
| Source annotation rules and output | [Annotation guide](seizure_finding_annotation_guide.md) |
| Gemini/Codex workflow, consistency checks and finding evaluation | [Annotation review](seizure_finding_annotation_review.md) |
| Prompt/schema versions and their rationale | [Schema decisions](one_shot_schema_decisions.md) |
| Authorised run settings, completed comparisons, costs and replay | [Execution record](one_shot_execution_record.md) |

## Main next research step: full seizure-finding annotation

The target is all dev750 letters, including row_ok=False, with a complete inventory
of task-relevant seizure findings read from each full source letter. Annotators must
not limit their inventory to r5 outputs or to the existing selected answer. The
existing Gan answer reference remains separate and retains its scoring semantics.

### Source-only test450 annotation

On 2026-09-15, Conor requested a separate ChatGPT 6 Pro task to annotate all
450 synthetic test letters after the dev750 review completes. This explicitly
authorises preparation of a source-only annotation export and subsequent annotation;
it does not authorise sealed prediction/failure inspection or extraction development
on test450. Preserve the existing native answers and evaluation restrictions.

The package is preserved locally at
`runs/seizure_finding_annotation_test450_6pro_2026-09-15/`. It includes all 450
sources, including 20 row_ok=False records, and excludes native labels, selected
references and predictions. The later simplified workflow authorised initial
annotation with frozen v0.6 rules while unresolved development conventions remained
explicit questions. The execution record owns package hashes and completion evidence.

A fresh conversation performed initial annotation with an immediate source check
under the lean workflow in the annotation review document. This replaced the
planned separately recorded full-source self-review and A/C check tables; those
stages must not be claimed as completed. All450 outputs are now locally received
and mechanically verified. Independent semantic review remains pending.
Keep new test-source policy ambiguities unresolved for domain adjudication; do not
use them to tune extraction prompts, schemas, scorers or semantic repairs. Record
annotation exposure in later reports; this work does not establish untouched-holdout
generalisation. The execution record owns the results and verification artifacts.

## Prove seizure annotation, then extend all four families

If the seizure annotation approach works well, extend the same process to the
four categories: seizure findings, medications (the existing Prescription family),
diagnoses and investigations. Define family-specific scope and matching rather
than reusing seizure quantity rules. Compare seizure-only rich extraction against
all-four-family extraction on the same permitted letters, holding the model,
runtime, original frequency-label rules and shared clinical content fixed. Retain
the original frequency answer as the common endpoint to test whether expanded
task scope harms that task. Score additional findings only against the reviewed
family references; freeze the concrete comparison and analysis before execution.

Conor plans to provide the reviewed dataset and guidelines to Yujian Gan and ask
whether the King's College London Hospital annotators are willing to use the full
annotation approach on real patient letters, ideally across all four categories.
This is planned collaborator outreach by Conor, not confirmed participation or
permission to send data. Real annotation and evaluation need an agreed scope,
source-use/sharing permissions, exposure history and clinical review procedure.
Existing aggregate-only holdout safeguards remain in force; any additional clinical
annotation access must be explicitly arranged with the custodian, never inferred
as permission to inspect sealed prediction failures for development.

## Question and scope

Can a locally deployable model preserve the established seizure-frequency answer
while returning a richer, inspectable evidence record in one clinical inference
call? The primary outcome uses the existing expert-selected current-frequency
label. The richer record is a model-produced inventory, not private reasoning and
not a newly gold-annotated clinical-fact benchmark.

The core study comprises the primary real-letter frequency result, controlled
synthetic rich/simple contrast, contract reliability, actual runtime and one compact
configuration example. The separately planned multi-family patient extension needs
its own prespecified fields and reference limits within this protocol. Hybrid/rule-heavy comparators, longitudinal evaluation,
optimizer search, authoring-effort and participant usability studies are out of
scope. Historical results remain context, not results of this method.

## Data and reference

| Source | Reference and intended role | Use conditions |
| --- | --- | --- |
| Real Gan 300 | Existing expert-selected current-frequency label; primary clinical-task evaluation, native Purist and Pragmatic companion. | Confirm authority, reference version, prior development/evaluation exposure and eligibility before access. Real(300) remains sealed. Do not substitute the synthetic split permissions. |
| Synthetic Gan | Existing single-label reference; controlled prompt/model comparison. Historical study union is 1,200 letters, dev750 + test450, including row_ok=False. | Develop on permitted dev750 only. Freeze reuse/evaluation policy before any test450 run; train300 is not implicitly available. Disclose prior use of every evaluated partition. |
| ExECT | Expert-annotated synthetic four-family inventory; one small descriptive configuration example. | Select from permitted dev140; retain native units and scoring. No new test60 run or model leaderboard is needed. |

The [dataset description](../shared/dataset_description_2026-08-26.md) owns the
historical corpus counts; counts for this study must come from its authorised
manifest. The [holdout policy](../../benchmarks/holdout-is-aggregate-only.md)
continues to apply. Never inspect sealed identifiers, notes, quotes, predictions
or errors during development. A custodian/execution process may produce permitted
aggregates under a separately approved frozen run procedure.

Use all eligible real letters, targeting the existing 300 rather than selecting
easy or successful cases. Record any exclusions with prespecified, prediction-free
reasons and the resulting denominator. Patient linkage and prior exposure require
metadata confirmation; if independence cannot be established, disclose it and do
not claim patient-level generalisation or unsupported precision. The existing
reference does not support full inventory recall, precision or completeness.

## Conditions and output

| Condition | One response contains | Interpretation |
| --- | --- | --- |
| Rich, primary | Zero or more scoped seizure-frequency findings with type/value, relevant seizure type, temporality, uncertainty/negation and exact quotations; one native task answer linked to relevant findings where applicable. | Tests the richer extraction contract. Any brief stated selection basis is visible output, not evidence of internal reasoning. |
| Simple, controlled | One native task answer and supporting quotation; no emitted finding inventory. | Primary paired comparator for the cost and task effect of the richer contract. |
| Holgate, contingent | Original supplied task and output form, parsed under its documented constraints. | External whole-prompt comparator; not an isolated feature ablation. |

Freeze the concrete schema and scope before calls. A valid zero-finding response
is allowed when appropriate; it is not permission to omit a required answer or
fabricate evidence for a no-reference state. Define required fields and the legal
representation of absent evidence for each sentinel in the no-call fixtures.

Match rich/simple note text, model and revision, decoding, runtime, label and
selection definitions, uncertainty convention, evidence obligation and examples'
clinical content. Record exact paired edits to scope instructions and schema-shaped
example outputs. Use the same development-chosen output cap and timeout, generous
enough for rich output; report truncation and realised costs. From 2026-09-16 the
default request timeout for new runners is 600 seconds; completed runs keep their
recorded timeouts, and each plan records the value used. Keep the constrained
decoding policy fixed while recording each condition's schema. This contrast
changes scope and output together; any selection-basis field must be recorded as
part of that intervention. Additional component ablations are not required.

Conor's supervisor is obtaining Holgate's full Llama 2 prompt. Record supplied
version, provenance, message roles, examples, output requirements and original
runtime/adaptation assumptions. Confirm use and quotation permissions. Do not
reconstruct or substitute it. Compare supplied and own prompts on the same chosen
model and notes where feasible; a Holgate/Llama 2 versus newer-model comparison
alone confounds prompt and model. Any adapted external prompt is separately named.
Missing comparator evidence fields remain unavailable, never manufactured.

## One-call and failure accounting

One-call means one clinical inference request per note, not zero demonstrations.
The model supplies both findings and final answer. Deterministic handling may
parse, check types, validate quotation locations and serialise values without
changing their meaning. It must not choose a different event, resolve ambiguity,
normalise a clinical value semantically or invent an answer. Audit the actual
prompt/parser/adapter path before adopting an existing runner.

The primary condition uses first-attempt output with no repair call. Preserve raw
responses and failure categories: no response/timeout, truncation, invalid syntax,
invalid schema, invalid target label and absent required evidence. Apply a fixed
precedence for mutually exclusive unusable-response counts; diagnostic flags may
overlap. Schema-invalid or otherwise unusable responses count as incorrect in the
all-note task denominator, even if a plausible label can be salvaged from text.
A correct native unknown/no-reference label is not a system refusal; preserve those
states in scoring and coverage. Exact quotation checks are separately reported; they do not adjudicate entailment.

Any deterministic format-only recovery is a separately reported secondary view,
with original validity, recovered count and remaining failures. An extra model
repair request is outside the primary one-call condition and must show total calls
and cost. Operational retries cannot replace failed first attempts invisibly.
Clinical repair or deterministic clinical selection constitutes another method,
not a format fix in this study.

## Outcomes and analysis

| Outcome | Denominator and report | Outline exhibit |
| --- | --- | --- |
| Primary real-letter task agreement | Native Purist correct / all eligible scheduled real notes, unusable output incorrect. Pragmatic companion; no pooled cross-corpus score. | Table 2 |
| Usable-answer coverage | Usable responses / all eligible scheduled notes. Conditional agreement is secondary and never replaces all-note agreement. | Table 2 |
| Controlled task difference | Rich minus simple all-note Purist on the same authorised synthetic notes; Pragmatic companion, paired wins/losses/ties and uncertainty. | Table 3 |
| First-pass contract validity | Schema-valid responses / all scheduled notes; distinguish responses received from absent responses. | Table 4 |
| Exact-source quotations | Exact matches / all schema-required quotation slots in received outputs, counting missing required quotes as failures; also notes with every required quote exact / all scheduled notes. Report no-evidence states separately, never as vacuous successes. | Table 4 |
| Rich record description | Finding counts and declared types/qualifiers among schema-valid outputs, with usable counts and exclusions. | Table 4 |
| Execution | Failure categories, truncation, any secondary recovery, call counts, latency and tokens; actual model revision, quantisation, engine, hardware and concurrency. | Table 4 |

A matching quote proves location only. The current annotation plan above adds a
source-first dev750 inventory reference and review of emitted findings so that
finding correctness and completeness can be measured separately. Until that
reference and its matching rules are reviewed, schema validity, quotation occurrence
and finding counts remain technical/descriptive measures, not clinical finding
precision or recall. The dev750 reference and frozen exact matcher now support that
development score; the [execution record](one_shot_execution_record.md#r7-finding-correctness-and-completeness-2026-09-22)
owns the saved R7 result and the [R8 run](one_shot_execution_record.md#r8-rich-dev750-finding-score-2026-09-22).
Exact field agreement is not the inventory endpoint. Finding Purist,
defined in the [finding-match note](finding_purist_match.md) and scored in the
[execution record](one_shot_execution_record.md#finding-purist-dev750-rescore-2026-09-22),
is that endpoint. It is not clinical validation or a holdout result.
Real finding measures still depend on the clinical annotations actually obtained. Sealed failure reporting remains mechanical and aggregate-only;
the development annotation plan does not permit inspection of sealed failures.

The primary real endpoint and primary controlled contrast above are fixed. Report
absolute scores and paired differences with 95% intervals under a prespecified
analysis implementation. Use patient clusters where known; otherwise use the
established sampling unit with the independence limitation explicit. Respect known
synthetic source families. Freeze the interval method, random seed if resampling,
and handling of small strata before evaluation. Do not choose an analysis after
seeing which makes a difference persuasive. Other slices are descriptive.

The real cohort target is 300 eligible existing letters, subject to authority and
eligibility; it is not a newly powered sample-size claim. Report attainable
precision rather than inventing a larger recruitment target. Absence of a
statistically clear rich/simple difference does not establish equivalence or
non-inferiority. Such a claim requires a justified margin and analysis agreed
before runs. Conor selected descriptive performance reporting without numerical adequacy
thresholds or a non-inferiority claim. Report measured performance, not that the
system is clinically good enough. This preserves the roadmap's capability question without requiring a new
clinical validation study for the planned descriptive paper.

## Model panel and execution order

1. Complete no-call rich/simple rendering, schema and native-adapter fixtures,
   including numeric, uncertain/no-reference, multiple-statement and unusable cases.
   Inspect exact prompts; do not reopen sealed notes.
2. Confirm feasible local runtime candidates and budget, then prespecify a compact
   panel with the same contract. An older model may provide capability context if
   it is feasible and matched; no historical model list is mandatory. Pin revision,
   quantisation, engine, context and decoding. Do not infer hospital deployment.
3. Use permitted synthetic development to settle prompts and output limits. Record
   selection and all attempts; development comparisons are not held-out results.
4. Freeze conditions, scorer/adapter, row policy, panel and analysis before the
   authorised synthetic evaluation. Report runtime changes as distinct conditions.
5. Freeze the selected real-evaluation condition before any authorised real run.
   Do not revise it from sealed errors. Report prior exposure and permitted
   aggregate outcomes, whether favourable or not.
6. Complete one compact ExECT specification-to-component change on development
   examples with the same model/decoding. Show edited fields, scope, evidence rules
   and examples, native descriptive checks and visible regressions. It demonstrates
   configurability, not clinician usability, reduced expertise or generalisation.

## Proposed multi-family patient extension (not frozen)

After proving the expanded seizure annotation on dev750, extend annotation and
extraction to the four families below. This staged development plan replaces the
earlier descriptive-only extension proposal. Reuse the existing ExECT family names. Conor/collaborator still need to confirm the scope and
available reference metadata without inspecting sealed rows.

| Family | Proposed returned fields | Reference boundary |
| --- | --- | --- |
| Diagnosis | Named diagnosis, certainty, negation, timeframe and exact quotation | Score only against an authorised diagnosis reference if available. |
| Seizure frequency | Measurement-specific findings with event scope, timeframe, bounds/approximation and quotations; one declared current-frequency answer | Existing Gan single-label scoring applies only to the declared answer. |
| Prescription | Medication name, dose/unit, schedule, current/planned/stopped status and quotation | Do not infer administration or adherence from a prescription. |
| Investigations | Named investigation, performed/planned status, reported result, timeframe and quotation | Do not infer a normal result from missing documentation. |

Absent findings are empty family lists, not assertions that the patient has no
condition. Preserve uncertainty and family-specific meaning: diagnosis negation
may be relevant to that separate family; the frequency record has no generic negation
field. Distinguish these clinical states from execution failure. Do not derive additional-family accuracy, inventory recall or clinical
completeness from the Gan frequency label. Until additional references are confirmed,
report schema, quote and output counts descriptively; do not invent family
accuracy. Development annotation is now planned under the amendment above.
Patient annotation and data sharing still require explicit arrangements. Freeze exact
schemas, examples, scope, runtime and analysis before either patient run; neither
run may be tuned from the other's sealed outputs.

## Readiness and reproducibility

| Decision still required | Owner | Evidence needed before dependent execution |
| --- | --- | --- |
| Real-set authority, prior use, reference version, linkage and eligibility | Conor with custodian | Recorded metadata/access decision; no sealed-row inspection to resolve it. |
| Rich/simple contract and synthetic analysis | Implemented and verified | Rendered artifacts, four new safeguard tests, frozen configuration and completed aggregates linked in the execution record. |
| Supplementary local runtime | Conor with implementation contributor | API configuration and comparison complete; Dell access/runtime details pending. Collaborator owns real-data cluster runtime. |
| Real aggregate-only procedure | Conor with evaluation owner | Synthetic manifest/freeze and prior-exposure disclosure recorded; written real-data authority and execution metadata remain pending. |
| Interval implementation and selection rule | Implemented and verified | Prespecified Wilson/paired bootstrap analysis complete; rich frequency condition selected before test results. No adequacy or non-inferiority claim. |
| Seizure-finding annotation | Gemini through AGY; Codex orchestration and secondary review | Reviewed source-first dev750 inventories, matching rules, guide versions and unresolved judgements. |
| Four-family extension and clinical annotation | Conor with Yujian Gan/custodian and implementation contributor | Successful seizure annotation pilot, reviewed development references, agreed clinical annotation participation/permissions, and frozen comparison before real runs. |
| Holgate prompt and permitted use | Conor's supervisor | Original supplied material and conditions; blocks this comparator only. |

Every run records dataset/version, split, source hashes, selection and row policy,
reference and scorer versions, model/runtime, rendered request and component hashes,
raw attempts, first-pass failures, repair policy, replay mode, exclusions,
denominators and costs. Keep extraction, format handling and scoring separable.
The outline's Figure 1 shows that path; Table 1 shows data/reference roles; Figure 2
shows the configuration change. Fill tables only from reviewed run artifacts.
