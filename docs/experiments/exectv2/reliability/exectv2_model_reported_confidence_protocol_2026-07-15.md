# ExECTv2 model-reported confidence protocol

Date: 2026-07-15

Status: frozen before the aggregate replay

## Question

Do the saved `low` / `medium` / `high` confidence labels rank family-cell
errors outside `dev140`, and do either of two fixed review rules catch enough
`test60` errors to justify their burden?

This closes the confidence item in `PROJECT_STATUS.md`. A negative result is a
complete answer.

## Data and inspection policy

- Dataset: ExECTv2.
- Development split: `dev140`; aggregate summaries and permitted row review.
- Evaluation split: `test60`; aggregate summaries only. The replay must not
  print or serialize letter identifiers, note text, gold facts, predictions,
  evidence, rationales, or row-level outcomes from `test60`.
- Saved outputs: the three historical model-led producer sets referenced by
  `configs/exectv2/model_led_audit/`, at their recorded Git revision.
- Models: GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6:35B repair v02.
  The DeepSeek thinking state is unrecorded, so its result remains audit-only.
- Call mode: Git-blob replay; no model calls.

## Fixed analysis

The unit is one letter-family cell for Diagnosis, Seizure Frequency,
Prescription, or Investigations. The named model's source producer supplies
the confidence labels. A cell's label is the least confident non-empty label
among its model-produced mentions (`low < medium < high`). A cell with no
usable label is `missing`; it is never silently converted to `low`.

The primary outcome is exact family-cell correctness of the final
decision-0040 output under `clinical_headline`. Source-model exact correctness
is secondary and distinguishes a confidence failure from a later deterministic
change. The scorer, gold, model outputs, projection, and repair policy are
fixed; this study changes none of them.

Primary readouts, separately for `dev140` and aggregate-only `test60`:

1. confidence-label coverage and distribution;
2. correctness and error count by label;
3. ordinal failure AUROC among cells with a usable label;
4. error catch rate and review burden for two predeclared rules:
   `low_or_medium` and `low_or_medium_or_missing`;
5. source-to-final changed-cell counts and correctness directions.

All three models are reported separately. A pooled result is descriptive only.
No threshold or rule may be selected after seeing `test60`.

## Artifact and reproducibility contract

The machine-readable artifact must record the source revision, configuration
paths, model identifiers, prompt/program metadata available in the saved
outputs, scorer, split sizes, row policy, confidence aggregation rule, repair
policy, per-model aggregate tables, parse/call events, and artifact hashes. It
must contain no row-level `test60` material.

Expected outputs:

- `experiments/exectv2_model_reported_confidence_out_of_sample_20260715.json`
- `docs/experiments/exectv2/reliability/exectv2_model_reported_confidence_out_of_sample_2026-07-15.md`

## Stop rule and claim boundary

A model's confidence is called informative on `test60` only if usable-label
coverage is at least 80%, failure AUROC is at least 0.65, and at least one
predeclared rule catches at least 50% of errors with review burden no greater
than 30%. Otherwise retain the negative result and do not adopt a confidence-
based review policy.

The strongest possible claim is an aggregate out-of-sample result for these
saved historical outputs on ExECTv2 `test60`. It is not deployment calibration,
independent clinical validation, a six-model conclusion, or evidence about a
thinking-enabled DeepSeek V4 Flash run.
