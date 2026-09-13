# One-call extraction evaluation protocol

Draft for execution decisions, 2026-09-13. Owner: Conor Brown.
Aligned with the [paper outline](../../../publications/jamia-one-shot/README.md)
and [roadmap](../../plans/ACTIVE_ROADMAP.md). No model calls, spending or new
sealed-data use are authorised by this document. Longitudinal work is postponed.

## Question and scope

Can a locally deployable model preserve the established seizure-frequency answer
while returning a richer, inspectable evidence record in one clinical inference
call? The primary outcome uses the existing expert-selected current-frequency
label. The richer record is a model-produced inventory, not private reasoning and
not a newly gold-annotated clinical-fact benchmark.

The primary real-letter result, controlled synthetic rich/simple contrast,
contract reliability, actual runtime and one compact configuration example are
the complete study. Hybrid/rule-heavy comparators, longitudinal evaluation,
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
enough for rich output; report truncation and realised costs. Keep the constrained
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

A matching quote proves location only. No full assertion annotation or independent
clinical inventory review is required for this paper, and no unsupported-assertion
rate, clinical finding precision/recall or inventory completeness claim follows
from these measures. Show only fictional or permitted development examples.
Classified failures on sealed data are mechanical aggregate categories, not a
request for clinical row review. A future entailment study needs a separate design.

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
before runs. Numerical adequacy thresholds remain unset: without prespecified
thresholds report measured performance, not that the system is clinically good
enough. This preserves the roadmap's capability question without requiring a new
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

## Readiness and reproducibility

| Decision still required | Owner | Evidence needed before dependent execution |
| --- | --- | --- |
| Real-set authority, prior use, reference version, linkage and eligibility | Conor with custodian | Recorded metadata/access decision; no sealed-row inspection to resolve it. |
| Concrete rich/simple schemas, answer adapter and no-call fixtures | Implementation contributor, reviewed by Conor | Rendered diff, semantic audit and failure accounting matching this protocol. |
| Model/runtime panel and budget | Conor with implementation contributor | Feasible pinned configurations and authorised cost envelope. |
| Synthetic evaluation/reuse and real aggregate-only procedure | Conor with evaluation owner | Frozen manifests, permitted outputs and prior-exposure disclosure. |
| Interval implementation; any adequacy threshold or non-inferiority claim | Conor with analysis contributor | Prespecified method; justified numerical boundaries only if that claim is pursued. |
| Holgate prompt and permitted use | Conor's supervisor | Original supplied material and conditions; blocks this comparator only. |

Every run records dataset/version, split, source hashes, selection and row policy,
reference and scorer versions, model/runtime, rendered request and component hashes,
raw attempts, first-pass failures, repair policy, replay mode, exclusions,
denominators and costs. Keep extraction, format handling and scoring separable.
The outline's Figure 1 shows that path; Table 1 shows data/reference roles; Figure 2
shows the configuration change. Fill tables only from reviewed run artifacts.
