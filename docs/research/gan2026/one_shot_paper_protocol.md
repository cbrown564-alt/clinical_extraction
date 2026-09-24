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

The frozen v0.7 reference and saved R8 comparisons retain that full-inventory
meaning. On 2026-09-23 Conor selected a narrower **candidate primary finding
score** for future development: current activity, an explicit last event, and a
source-stated prior measurement that explains a change. The
[candidate annotation rule](seizure_finding_annotation_v08.md#candidate-compact-primary-finding-policy-23-september-2026)
defines its scope. It must receive its own source-first reference and frozen
scorer before any score is reported. It does not replace the established native
selected-frequency primary outcome, make the old inventory scores comparable to
new ones, or permit a changed prompt to be judged against a moving reference.

### Compact primary finding score

The owner-reviewed compact v0.3 dev750 reference and `finding_compact_v03_v2`
scorer are now versioned. The scorer uses all 750 synthetic development letters,
including `row_ok=False`, and the 1,219 selected claims in the source-backed
v0.3 candidate. Independent annotation agreement is not a prerequisite for
this development comparison. The source review and owner adjudications establish
its provenance; they do not establish clinical validation.

Report **whole-claim precision, recall and F1** alongside **source-aligned
precision and recall** and separate component precision and recall for event
population, counted unit, seizure status, measurement kind, measurement value,
phase, source window and meaning-changing restriction. The native selected
frequency answer remains a separate primary endpoint under the existing Gan
scorer. One whole-claim match cannot conceal an otherwise correct measurement
with a wrong event label.

A whole-claim prediction matches one reference claim when its declared event population
(scope plus a small explicit spelling-alias list), counted unit, seizure status,
phase, measurement, source time window, and meaning-changing restriction agree,
and at least one exact source quotation overlaps. Numeric values, bounds and
denominators match component by component. A seizure-free duration scores in
place of a co-stated since anchor; anchor-only claims require the anchor. The
scorer uses maximum one-to-one matching, so duplicate predictions receive no
second credit. After retaining whole-claim pairs, it aligns remaining claims
one-to-one by overlapping exact source evidence, maximising pair count and then
component agreement. Each aligned pair earns independent component credit;
unaligned predictions and references count as errors for every component.
Component scores use all usable predicted claims and all reference claims as
denominators, including unusable-response misses. Agreement among aligned pairs
is also reported to distinguish extraction coverage from field correctness.
No native frequency-band collapse, inferred subtype, format repair or semantic
repair is applied.

The [scorer manifest](../../../results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/scorer_v03_manifest.json)
records the reference, schema, prompt and local snapshot hashes. Rebuild with
`.venv/bin/python scripts/benchmarks/score_compact_findings_v03.py`. To score
saved parsed R9 responses, provide `--predictions INPUT.jsonl --output OUTPUT_DIR`.
The input must cover every source row with matching source ID, row index and
source hash. Also provide `--run-metadata RUN.json` declaring nonempty
`model`, `prompt_version`, `prompt_revision`, `replay_mode` and
`repair_policy`; the prompt identifiers must match this frozen R9 revision.
Each input line contains a `response` object or null. Invalid responses
contribute all reference claims as misses and no predicted claims; invalid
reasons and per-letter pairs stay in the requested local output directory.
This command makes no model calls and does not inspect test450.

The saved R9 development mismatch audit found a source-window prefix mismatch
in the original scorer. Version `finding_compact_v03_v3` accepts optional
leading articles and `in`/`over` on a stated `past`, `last` or `current`
relative window while retaining the interval word and quantity. The original
score is preserved. The [versioned audit and replay](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/window_audit_v03_v3/README.md)
record the source examples, scorer change, remaining event/restriction
questions and both scores. No event-population or restriction equivalence is
added without a source-backed policy decision. This is development rescore
evidence, not a second model result.

The later [scored-term v2 development audit](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/concepts_v02_source_audit/README.md)
proposes a finite set of explicit event and population codes and keeps literal
labels/evidence in a separate projection. It remains provisional while
conditional qualitative findings, combined broad populations and observation
scope are adjudicated. Its score is a diagnostic replay of the same saved R9
responses, not a replacement endpoint or evidence of prompt improvement.
The [v3 policy continuation](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate/README.md)
keeps the same development whole-claim count after clarifying explicit
qualitative conditions, incomplete combined labels, and observation-limited
absence. Source 6077 remains a flagged provisional claim under its earlier
owner adjudication. The literal v0.3 score remains the frozen comparison.

An [eight-case diary arithmetic check](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate/README.md#diary-arithmetic-correction)
found a prompt/reference mismatch: the reference includes owner-approved sums
of disjoint diary components, while R9 explicitly forbids arithmetic. The
earlier source-15992 model-error attribution is withdrawn. The score remains
unchanged, but these misses cannot be assigned solely to model capability.
The check is selected, so it does not quantify the full effect.

### R10/R11 development pilot

The fixed [R10/R11 development pilot](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r11/dev750_pilot16/README.md)
tested prompt alignment on 16 selected dev750 letters. Its selected result
does not estimate population performance. The calendar-window v04 scorer
changes only month spelling and range punctuation equivalences; a saved-R9
dev750 replay remains at 445 whole-claim matches (F1 35.21%). R11 was then
prepared for a full dev750 first-response run with the same v0.3 reference,
one-call output and no repair. The execution record owns completed results.

The [full R11 synthetic dev750 result](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r11/dev750/README.md)
is mixed under the same v04 scorer: F1 rises from 35.21% to 36.19% as extras
fall, but exact matches and recall fall and the native Pragmatic answer loses
nine correct letters. Its paired development F1 interval crosses zero.
Keep R11 as a development comparison; do not substitute its selected pilot
or full development score for a frozen test450 or clinical claim.

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

## Jev fictional comparison

Status: offline supplementary prototype, approved 2026-09-21. No model performance
result and no change to the primary study. The experiment asks whether Jev and a
generative model can select and classify the same source-derived candidates using
identical bounded questions, without task-specific training.

The [fixture pack](../../../examples/jev_comparison/README.md) owns runnable commands
and limitations. The builder reads only fictional source text, never gold, and
uses newline-delimited source sentences as candidates without clinical filtering.
Each candidate has exact offsets. Every candidate receives the same role,
measurement-structure, outer-quantity, inner-quantity and denominator questions.
A separate whole-letter question selects the current burden or an explicit
no-current, unsupported or ambiguous answer. Field questions identify their own
candidate in their instructions; they do not depend on another parallel answer.
Literal numeric options come only from that candidate. No arithmetic, semantic
repair, native Gan mapping or R7/R8 record conversion is performed.

Both providers receive exactly the same state and question definitions. The LLM
has only an additional output-format instruction. Jev uses Choice; Score is not
literal numeric extraction. See the official [Choice documentation](https://docs.typesafe.ai/primitives/choice),
[Score documentation](https://docs.typesafe.ai/primitives/score) and
[source-value extraction pattern](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook),
checked 2026-09-21. Default Jev request version is `jev-1.13.0`; a future live run
must verify availability and record the actual returned model version.

The first pack has six invented letters and a seventh condition omitting the
correct candidate while retaining the entire letter. Provisional author-written
keys cover 48 decisions: primary selection, every available candidate's role and
four attributes of the expected selected candidate. Other candidate attributes
remain unscored. Missing/invalid answers count as wrong with a fixed denominator;
report selection, component errors and exact selection-plus-attributes separately.
These are fixture agreement measures, not native Purist/Pragmatic scores or clinical
validation. The omission condition tests abstention when a candidate is unavailable;
it does not establish candidate recall on real notes.

Before live comparison, freeze model/runtime, fixtures, source segmentation,
questions, keys, scorer and a call/cost budget. Preserve submitted requests and raw
responses, returned model, time, usage, failures and attempts separately for each
provider. The offline scorer accepts saved responses but does not execute calls or
measure latency. Review the fictional keys independently before making substantive
accuracy claims. A later dev750 study requires a reviewed reference and prospective
native-answer mapping; locked test450 remains outside development.

The current pack covers one principal finding per letter. Multi-event selection,
quantity ranges in scored examples, cross-sentence binding, evidence precision,
calibration, candidate-order sensitivity and native answer agreement remain future
work. A verifier study must separately measure false acceptance of deliberately
incorrect extractions. An LLM-plus-Jev pipeline adds a clinical model call and is
not the primary one-call method.

### Frozen live pilot v2 (2026-09-21)

Conor authorised completion of the reference review, paired live comparison,
robustness checks and a decision about dev750. The [v2 freeze](../../../results/letter-benchmarks/gan/jev_fictional_v2/freeze.json)
is authoritative for exact inputs, hashes and execution settings. V1 remains an
unchanged offline preparation artifact. V2 has 22 conditions and 157 scored
decisions: seven base conditions, three quantity substitutions, four paraphrases,
one complementary-current-findings case and seven order reversals. The order
condition reverses candidate, question and option order together; it cannot isolate
which of those orderings causes any difference. Cases are related fixtures, not
22 independent clinical examples, and no inferential significance claim is planned.

DeepSeek V4 Pro reviewed the 14 distinct letters in a fresh source-only context,
without author keys or evaluation predictions. Its reference decisions agreed
with the author's keys. Omission and order keys derive mechanically from these
reviewed cases. Codex reviewed the rationales: the sister's seizures are excluded
because they concern another person; the review's loose phrase "non-epileptic/other"
is not evidence that those events are non-epileptic. This is independent model
review plus author adjudication, not independent human clinical validation.

Before evaluation, v2 clarified that the denominator sentinel `not_established`
applies to qualitative frequency, whereas `not_applicable` covers observed counts,
seizure freedom and non-frequency statements. No evaluation output informed this
change. Questions retain per-candidate binding and source-only numerical candidates.

Models: Jev `jev-1.13.0` and DeepSeek `deepseek-flash` (documented as V4.1 Flash).
The DeepSeek alias is not an immutable checkpoint; preserve the returned model
identifier without claiming stronger version pinning. DeepSeek uses thinking
on/low, temperature 0, 24,000 maximum output tokens and JSON-object output.
Each provider has one sequential request per condition, a 600-second timeout,
no automatic retry, and no syntax or semantic repair. Raw response text, usage,
returned model, HTTP failures and wall-clock latency are retained locally.

The pilot ceiling is US$2 including the review. Conservative full-run reservation
is US$0.86298273 using UTF-8 input-byte bounds plus framing allowance, maximum
DeepSeek output tokens and published peak rates. Report measured-token peak-price
upper estimates separately from provider invoices; missing usage retains its
full reservation. This pilot has a separate ledger and does not erase earlier
study charges. Credentials are loaded at runtime and never saved in artifacts.

Report primary selection, role and attribute accuracy, exact selection-plus-four-
attributes, and error mechanisms by condition group. One all-case denominator
includes provider, truncation, syntax and missing-answer failures. No test450 or
patient-data access, native-score substitution, or complete-inventory claim is
permitted. Do not automatically execute dev750: recurrent binding, abstention or
robustness failures require more fictional development; even a clean pilot needs
candidate-coverage assessment, a reviewed reference and frozen native mapping.

### V3 narrower classification and verification pilot (2026-09-21)

Conor authorised the next bounded experiment. The
[v3 freeze](../../../results/letter-benchmarks/gan/jev_fictional_v3/freeze.json)
records eight development and eight reserved fictional letters, assigned before
question implementation. Reserved comparator predictions are not inspected during
development; all questions, keys and scoring are frozen before either split runs.
These author-written fictional cases are not an untouched clinical holdout.

The common task is classification of source-derived candidate sentences, not open
finding discovery or numerical extraction. Both standalone models classify role,
measurement kind, outer-field applicability and inner-field applicability, plus
whether the candidate list covers all current confirmed findings. Full-letter
context supports cross-sentence references. Source-derived literal numeric spans
are stored separately without semantic binding, normalization or performance claims.
V3 covers multiple seizure types, ranges, uncertain epileptic status, unresolved
contradictions, missing candidates, cluster applicability and absent current data.
Definitions belong to this experiment and do not modify the v0.7 reference rules.

The three conditions are DeepSeek alone, Jev alone on the same candidates, and
DeepSeek followed by Jev verification of its unchanged classification tuples.
The hybrid has two clinical calls. An accept releases a tuple unchanged; reject,
uncertain or a missing verdict defers it to review. It neither repairs an answer
nor silently suppresses a field. Candidate coverage remains a separate warning:
accepting all supplied tuples does not establish inventory completeness.

An independent source-only DeepSeek V4 Pro review labels all 48 sentences without
proposed keys or comparator outputs. One of 192 labels differed: inner applicability
for a future cluster-day threshold with no size. Codex retained yes under the already
written rule that cluster structure makes the field applicable even if its value is
unstated. The disagreement and reason are preserved in the freeze. This is model
review and author adjudication, not independent clinical validation.

Each split has 100 scored standalone decisions and 23 candidate tuples. Missing
source candidates remain in current-finding recall denominators even when the
coverage warning is correct. A separate verifier challenge contains one correct
and three deliberately wrong tuples per letter: changed role, kind or inner-field
applicability. Correctness labels and mutation names are never sent to Jev. Report
false acceptance on these 48 seeded wrong claims separately from false acceptance
on actual DeepSeek errors; if the latter denominator is zero it is not evidence
of error-detection sensitivity. Also report correct-proposal deferrals, retained
current-finding recall, complete candidate classifications, cost and latency.

Keep the v2 model settings, 600-second timeout and one-attempt/no-repair policy.
V3 has its own US$2 cap, with US$0.797638866 reserved for all calls including review
and a full-context allowance for hybrid verification. Calls within this pilot must
be run serially: its append-only accounting files are not a concurrent transaction
store. No broad benchmark or patient-data call is authorised by this pilot.

After development, execute the unchanged frozen reserved comparison once, without
prompt tuning. Recurrent classification/applicability errors, false acceptance of
seeded wrong claims or rejection of correct inventory prevent expansion of this
candidate. Even a clean result would still need native-answer mapping, reviewed
references and a candidate-coverage assessment before a dev750 experiment.
