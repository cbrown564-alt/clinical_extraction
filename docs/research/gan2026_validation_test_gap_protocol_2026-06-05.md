# Gan 2026 Validation-Test Gap Protocol

Date: 2026-06-05

Status: frozen Phase 0 protocol for validation-test generalisation-gap
analysis. This protocol authorizes saved-artifact inventory, validation
row-level attribution, synthetic/adversarial mechanism panels, and aggregate or
predeclared-slice locked-test summaries only. It does not authorize locked-test
row-level tuning.

## Research Question

Why does the current Gan 2026 seizure-frequency system perform materially worse
on locked test450 than on validation750 when both splits come from the same
synthetic, template-generated dataset?

The working target is explanation, not another broad metric improvement. The
next candidate change must be justified by a named mechanism hypothesis and a
component-specific experiment.

## Split And Inspection Policy

Use `gan2026_split_v1`.

Validation750:

- allowed for row-level development diagnostics;
- allowed for first-failure ownership;
- allowed for hard-slice construction and examples;
- allowed for component ablations and same-raw-output replays.

Locked test450:

- allowed only for aggregate summaries and predeclared-slice summaries;
- allowed only when the slice definition and score layers were frozen before
  the readout;
- not allowed for row-level failure inspection during development;
- not allowed for prompt, rule, model, threshold, projection, repair, or
  normalization tuning.

Do not inspect locked-test row-level failures. If later post-hoc locked-test row
review becomes necessary, document it as final-evaluation analysis and start any
subsequent fix as a new validation-cycle candidate.

Synthetic and adversarial panels:

- allowed for mechanism testing and regression checks;
- not allowed as benchmark-comparable evidence;
- must include matched controls and explicit gold facts before candidate runs.

## Candidate And Comparator Set

First-wave analyses should use saved artifacts where possible:

- `rules_only_v1` deterministic comparator;
- conservative staged assembly;
- staged assembly component matrix;
- selective safety-floor gate;
- direct-labeler targeted switch and structured candidate surfaces;
- few-shot train-exemplar surfaces only as closed diagnostic branches;
- structural guard and combined switch surfaces only as transfer diagnostics;
- LLM structured/raw/repair ladders only where same-raw-output provenance is
  recoverable.

No first-wave analysis should introduce a new prediction-bearing architecture.

## Score Layers

The gap matrix should preserve separate rows for:

- deterministic comparator;
- raw model output;
- parsed raw model clinical label;
- format-only repair;
- deterministic adapter;
- graph projection;
- safety floor;
- abstain/review/monitor policy;
- final policy.

If a score layer is missing in an artifact, record it as an instrumentation gap
instead of inferring ownership from the final label.

## Component Ownership

Assign ownership by decision effect:

- `llm_clinical_selection`: the model selected the prediction-bearing clinical
  fact and evidence.
- `deterministic_rule`: deterministic code selected or changed the clinical
  fact, temporal state, event, or benchmark label.
- `deterministic_adapter`: deterministic code rendered from already selected
  model operands without changing fact identity.
- `graph_projection`: deterministic graph logic selected among states or nodes.
- `safety_floor`: deterministic fallback preserved or restored a comparator
  answer.
- `schema_repair`: format/schema repair without semantic change.
- `benchmark_format`: scorer-facing convention only.

If deterministic code selects among competing facts after an LLM call, classify
the row as hybrid for that subproblem.

## Hypothesis Contract

Every gap experiment must declare:

- hypothesis ids from
  `experiments/gan2026_validation_test_gap_hypothesis_registry_2026-06-05.json`;
- candidate and comparator;
- split manifest;
- scorer policy;
- distribution;
- score layers;
- inspection policy;
- expected mechanism;
- stop rule.

Experiments without hypothesis ids or inspection policy are diagnostic only and
cannot justify candidate changes.

## Required Outputs

Phase 0 outputs:

- this protocol;
- artifact inventory;
- machine-readable hypothesis registry;
- tests enforcing protocol metadata.

Phase 1 outputs:

- validation-test surface map;
- label-kind and hidden-family gap tables;
- action-rate summaries.

Phase 2 outputs:

- `validation_test_gap_matrix_v0`;
- component-owner, clinical-subproblem, score-layer, and first-failure tables.

Later phases:

- component-specific validation hard-slice reports;
- synthetic/adversarial component-stress panels;
- frozen aggregate-only test audit only after explicit authorization.

## Stop Rules

Pause architecture iteration until:

- the validation gap matrix exists;
- component-owner attribution is available for validation;
- test usage remains aggregate-only or predeclared-slice-only;
- at least three named hypotheses have controlled evidence;
- any proposed component change states which hypothesis it addresses.

Reject a mechanism if:

- it improves aggregate validation F1 without improving its target hard slice;
- it cannot identify prediction-bearing ownership;
- it credits the LLM for a deterministic semantic repair;
- changed rows lack exact evidence;
- deterministic-correct regressions are introduced;
- the only improvement is benchmark-format convention handling.

