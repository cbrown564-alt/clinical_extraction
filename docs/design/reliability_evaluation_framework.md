# Reliability evaluation framework

Last updated: 2026-07-18

This document defines the paper-facing reliability framework shared by Gan
2026 and ExECTv2. It asks the same eight questions of both tasks while keeping
their measures, denominators, score stages, and evidence limits explicit.

The framework reports evidence by criterion. It does not establish one shared
metric or clinical validity.

## Criteria

| ID | Criterion | Shared question |
| --- | --- | --- |
| `clinical_correctness_generalization` | Clinical correctness and generalization | Does the final system recover the intended clinical result, and what changes outside development? |
| `clinical_selection_unsupported_inference` | Clinical selection and unsupported inference | Does the system select a warranted current fact rather than an unsupported, historical, planned, or ambiguous one? |
| `evidence_support_faithfulness` | Evidence support and faithfulness | Is cited text present, and does it semantically support the selected conclusion? |
| `uncertainty_selective_action` | Uncertainty and selective action | Do uncertainty signals identify failures, and can they support abstention or review at acceptable burden? |
| `robustness_stability` | Robustness and stability | Does the decision persist across relevant data, sampling, wording, prompt, parser, or runtime changes? |
| `component_attribution_correction_safety` | Component attribution and correction safety | Which component changes the answer, and does deterministic correction help without damaging correct model output? |
| `coverage_clinical_slice_behavior` | Coverage and clinical-slice behavior | Which clinical families and hard cases are covered, missing, or materially weaker? |
| `operational_reliability` | Operational reliability | Does the named runtime complete predictably, with failures, repairs, retries, latency, and usage reported at their measured scope? |

Changing this set requires an amendment to
[decision 0044](../decisions/0044-shared-reliability-criteria-use-task-specific-measures.md).

## Assurance gates

Assurance gates are required metadata and governance checks. They are not
scored criteria and are never averaged into a reliability result.

Every measured result must name:

- dataset, split manifest, row policy, and inspection permission;
- exact model, route, runtime, temperature, token limit, and cache or replay
  mode, using `not_recorded` when historical evidence lacks a value;
- prompt or program, scorer, score stage, and repair policy;
- source artifacts, retained hashes, and a reproducibility command;
- split barriers, locked-row controls, canaries, and failure handling;
- independent clinical-review status; and
- a claim boundary.

A task may have a measurement for a criterion while the criterion remains
incomplete. `result_state` records whether a result exists;
`completion_status` records whether the required evidence and gates are
complete. A missing gate must remain visible and must not be described as
completed evidence.

## Result states

Each task has exactly one state for each criterion:

- `measured`: at least one valid retained measurement answers part or all of
  the criterion;
- `not_measured`: no selected measurement has been made;
- `not_applicable`: the criterion or named submeasure does not apply, with a
  reason;
- `not_measurable_current_data`: the current annotation or retained data has
  no valid denominator or measurement substrate.

The state is not a quality grade. A measured cell can still be partial,
diagnostic, or blocked from a stronger claim.

## Evidence states and row scopes

Evidence state and row-inspection scope are separate fields.

Allowed evidence states are:

- `not_measured`;
- `diagnostic`;
- `development_answer`;
- `aggregate_holdout_evidence`; and
- `externally_validated`.

Allowed row scopes are:

- `synthetic_fixture`;
- `development_rows_permitted`;
- `aggregate_only_rows_sealed`; and
- `independent_review_rows`.

Internal annotation review is not `externally_validated`. A holdout aggregate
does not become row evidence.

## Comparability

Every cross-task cell uses one of three states:

- `direct`: the measurement object, transform, score stage, and unit are the
  same;
- `construct_only`: the measures answer the same criterion, but their values
  must not be compared numerically; or
- `not_comparable`: the measures answer different questions or one task lacks
  a valid denominator.

Only `direct` measurements may produce a cross-task numerical delta. Current
task-level reliability results are generally `construct_only`; clinical
selection and unsupported inference is currently `not_comparable` because the
ExECT unknown-only denominator is zero.

## No composite score

No artifact or report may calculate an overall reliability number, average
criterion coverage, or weighted reliability ranking. Missing or diagnostic
evidence must remain visible rather than being diluted by unrelated results.

## Task measures

| Criterion | Gan 2026 | ExECTv2 | Current cross-task use |
| --- | --- | --- | --- |
| Clinical correctness and generalization | Purist accuracy primary; Pragmatic secondary; validation and locked test separate | 4-family micro F1 (`clinical_inventory_unit_keys`) for the four fixed families; dev140 and aggregate-only test60 separate | Construct only |
| Clinical selection and unsupported inference | Unknown-gold active-rate over-read; current-versus-historical and faithful-but-wrong counts | Preserve the six-model SF zero-denominator result; a rate requires independently governed exhaustive review | Not comparable |
| Evidence support and faithfulness | Textual grounding at the named stage; semantic support separately | Six-model final exact evidence; independent semantic-support review separately | Construct only until stage and review match |
| Uncertainty and selective action | Confidence coverage, calibration, failure detection, risk-coverage, and review burden at their recorded scope | Internal scoring-rule calibration and the bounded historical three-model routing result | Construct only |
| Robustness and stability | Development-to-holdout change, prompt-version index, and the one-model repeated-temperature study | Six-model dev-to-test change plus recorded parser and runtime behavior | Construct only |
| Component attribution and correction safety | Raw selection, format repair, selected-evidence repair, clinical repair, final label, and scoring remain separate | Decision-0040 family ownership, score stages, deterministic regressions, and six-model SF transitions | Construct only |
| Coverage and clinical-slice behavior | Seizure bands, seizure-free duration, unknown, cluster or diary language, and named hard families | Four fixed families, temporal selection, seizure state, medication regimen, investigation completion, annotation-sensitive cases, and parse or schema status | Construct only |
| Operational reliability | Observed calls, failures, repairs, and bounded offline cost; unmatched latency and retries remain unavailable | Six-model call and parse or schema behavior with hosted and local routes separate | Construct only |

Demographic fairness is `not_measured` for both tasks unless suitable
attributes, sample sizes, and a clinically meaningful fairness question are
established. Entity-family or seizure-band variation must not be relabelled as
demographic fairness.

## Measurement record

The machine scorecard contains one record per task, criterion, model scope,
split, and measurement. Each record contains at least:

```json
{
  "task": "gan2026 | exectv2",
  "criterion_id": "clinical_correctness_generalization",
  "measurement_id": "task-owned stable name",
  "model_scope": ["exact runtime identifiers"],
  "dataset": "named dataset",
  "split": "named split",
  "split_manifest": "repository path",
  "row_scope": "development_rows_permitted",
  "denominator": 0,
  "score_stage": "raw | evidence_valid | projected | final",
  "scorer": "named scorer or transform",
  "repair_policy": "named policy",
  "value": null,
  "evidence_state": "diagnostic",
  "comparability": "construct_only",
  "source_artifacts": ["repository paths"],
  "claim_boundary": "bounded statement",
  "not_measured_reason": null
}
```

The generated artifact also records route and runtime scope, prompt or program,
temperature, token limit, cache or replay mode, inspection rule, retained
source hashes, reproducibility command, independent-review status, pooling
unit, and unique-row count.

Rules:

- `value` may be null only for a `not_measured` result or an invalid or zero
  denominator.
- Zero denominators are recorded as zero.
- Repeated letters across models use `model_letter` as the pooling unit and
  record both unique letters and model-letter rows.
- `construct_only` and `not_comparable` measurements never emit a cross-task
  numerical delta.
- Locked artifacts contribute aggregates only and cannot emit row fields.
- Textual grounding and semantic support use different measurement IDs.
- No record contains a composite reliability field.

## Gap decisions

Every open gap records its class, owner, unblock condition, and effect on
claims. The default decisions for this implementation are:

- the ExECT unknown-only rate remains a closed diagnostic result until an
  independently governed reviewed substrate exists;
- the ExECT semantic-support sample is prepared but remains unreviewed and
  cannot certify semantic faithfulness;
- the historical ExECT uncertainty result remains a three-model negative
  result unless a separate protocol adopts a six-model routing claim;
- repeated-temperature or perturbation calls are optional new studies tied to
  a named claim, not framework completion work; and
- unmatched cost or latency telemetry is not reconstructed.

No model call, scorer change, deterministic clinical rule change, or locked-row
inspection is authorized by this framework.
