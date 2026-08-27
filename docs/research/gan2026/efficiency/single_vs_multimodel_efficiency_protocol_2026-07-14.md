# Gan single-pass versus multi-model efficiency protocol

Date: 2026-07-14

## Question

What efficiency conclusion can the retained Gan `test450` evidence support for
the single structured-event pass and the V12 multi-model comparison?

This study matters because the paper records a 15-row Purist difference but the
two saved evaluations were not instrumented as a matched runtime experiment.

## Fixed study design

- **Dataset and split:** Gan 2026 synthetic seizure-frequency subset,
  `test450`, split manifest `gan2026_split_v1`.
- **Row policy:** aggregate-only. Do not open, inspect, or reconstruct holdout
  row content, failures, selected evidence, or transitions.
- **Candidate:** the saved V12 test condition, two upstream structured-event
  passes (GPT and Qwen-3.6-35B), one GPT-4.1 fresh-evidence reasoner pass, and
  deterministic guards. DeepSeek input was unavailable on all 450 test rows.
- **Comparator:** one GPT-4.1-mini structured-event pass followed by the fixed
  deterministic normalization and scoring path.
- **Scorer:** the saved aggregate Gan Purist score; Pragmatic is secondary.
- **Primary efficiency units:** Purist-correct rows and required model passes
  per note under a cold execution.
- **Secondary units:** recorded calls, prompt tokens, completion tokens, cost,
  wall time, hardware, retries, and cache use, each with an explicit evidence
  status.
- **Mode:** no-call retrospective audit of selected aggregate reports. No
  prompt, rule, scorer, split, model, or repair changes.

## Sources

The four artifacts selected by the retained-evidence manifest supply the
paper-facing facts:

1. `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.json`
2. `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`
3. `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md`
4. `docs/research/gan2026/architecture/simplest_near_ceiling_architecture_results_2026-06-16.md`

`experiments/registry.jsonl` supplies the saved aggregate changed-row counts as
run-lineage diagnostics. Those counts do not strengthen the paper claim.

Git history may be used only for an aggregate schema audit confirming model
input availability and that missing telemetry was never retained. Historical
row values must not be restored, displayed, or read into the result.

## Artifact schema

The JSON result stores one record per method and one record per comparison
dimension. Every dimension is labelled `observed`, `derived`, `partial`, or
`unavailable`. It also records the split, scorer, model roles, replay/cache
condition, repair policy, component-attribution limit, source files, and claim
boundary.

## Component and regression checks

The study reports the saved aggregate wrong-to-correct and correct-to-wrong
counts for V12 versus the single-pass answer. It does not inspect rows or assign
first-failure ownership on `test450`. Changed-row exact-evidence coverage and
clinical-subproblem breakdowns are unavailable, so V12 cannot be promoted from
this audit.

## Stop rule

The question is answered when the artifact does one of the following:

- supports a matched comparison for a dimension from retained telemetry; or
- records that the dimension is unavailable and removes the unsupported claim
  from the paper.

Do not rerun either system merely to recreate telemetry. V12 source has been
removed, the retained evaluation used cached upstream traces, and a new run
would be a different runtime condition rather than a matched replay.

## Claim boundary

A positive result may state only the saved `test450` quality difference and the
architecture's required model-pass count. It may not claim measured token,
dollar, energy, hardware, or latency efficiency. The holdout quality numbers
remain frozen aggregate evidence; the operational interpretation is a
retrospective diagnostic.
