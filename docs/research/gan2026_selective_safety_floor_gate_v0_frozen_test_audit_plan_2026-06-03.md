# Gan 2026 Selective Safety-Floor Gate v0 Frozen-Test Audit Plan

- Date: 2026-06-03
- Candidate: `selective_safety_floor_gate_v0`
- Candidate seed: `combined_selective_gate_v0`
- Split manifest: `gan2026_split_v1`
- Test surface: locked `test` split, 450 rows
- Current planning commit: `153c580`
- Validation basis:
  `experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.md`
- Validation-cycle manifest:
  `experiments/gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.md`

## Decision

Write a separate frozen-test audit plan before any locked-test use of
`selective_safety_floor_gate_v0`.

The validation-cycle manifest explicitly excludes locked test. It freezes a
validation-only no-call replay over saved artifacts; it must not be stretched
into a holdout protocol. A locked-test run is justified only as a frozen
generalization audit because the validation surface is already saturated and
the candidate changes are narrow, high-precision, and separately attributable.

This plan does not run locked test. It only defines the conditions under which a
future locked-test audit would be valid.

## Frozen Claim Language

Any future result under this plan must be described as:

- a final holdout generalization audit only if every frozen-input and
  inspection rule below was followed;
- a hybrid deterministic-safety-floor result, not an LLM-first result;
- a selective-action audit of two sidecars under a deterministic safety floor,
  not a production-policy promotion;
- not a benchmark-comparable claim unless a separate benchmark-replication
  policy is written.

If any code, scorer, prompt, model, repair, graph, schema, threshold, or gate
policy changes after this plan, cancel this audit and return to validation.

## Frozen Inputs

Before any locked-test command, record these exact values in the test run
artifact:

- repo commit hash and dirty-worktree status;
- `data/Gan (2026)/splits/gan2026_split_v1.json` path and hash;
- source validation artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`;
- validation-cycle manifest:
  `experiments/gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json`;
- validation replay report and JSON/JSONL artifacts;
- scorer module/version and Purist/Pragmatic category policy;
- candidate implementation entry point and all gate names;
- model id, temperature, max tokens, DSPy cache setting, API base, and no-call
  or live-call mode;
- artifact output paths for locked-test JSONL, summary JSON, Markdown report,
  and any call log before execution.

## Frozen Candidate Policy

The prediction-bearing layer is `selective_safety_floor_gate_v0`.

The layer order is fixed:

1. Start from `baseline_safety_floor_v2`.
2. Apply `projection_boundary_state_priority_gate_v0`.
3. Apply `llm_candidate_sidecar_rescue_gate_v0` only if the projection gate did
   not change the row.
4. Preserve the original baseline label and component-layer labels for every
   row.

The gate definitions, evidence exactness checks, selected-source-id checks,
changed-row accounting, scorer mapping, repair policy, graph policy, and
fallback behavior must match the validation-cycle manifest. Do not introduce a
new normalization path for locked test.

## Pre-Run Checks

Required before any locked-test execution:

- run the targeted tests for the selective replay implementation;
- record `git status --short`;
- record the split manifest hash;
- confirm the locked-test row text, labels, and row-level failures have not
  been inspected for tuning this candidate;
- confirm the output artifact paths are fixed;
- confirm no run command points at the validation-cycle manifest as if it
  authorized locked test.

If any check fails, stop. Do not run locked test.

## Allowed First Readout

The first locked-test readout may include only:

- aggregate Purist and Pragmatic counts for `selective_safety_floor_gate_v0`,
  `baseline_safety_floor_v2`, and each component diagnostic layer;
- changed rows, wrong-to-correct, correct-to-wrong, changed-label precision, and
  deterministic-correct regressions versus baseline;
- exact-evidence and valid-source-id counts for changed rows;
- fallback or abstention counts by component layer;
- call, parse, schema, and scorer-invalid counts;
- predeclared slice aggregates listed below.

Do not list locked-test row ids, note text, evidence snippets, predicted labels,
gold labels, or row-level failure examples in the first readout.

## Predeclared Slices

Locked-test slices may be computed only from predeclared metadata, candidate
diagnostics, or text-pattern indicators fixed before row-level inspection.

Report each slice with row count, Purist, Pragmatic, changed rows,
wrong-to-correct, correct-to-wrong, deterministic-correct regressions,
changed-row evidence exactness, and changed-row source-id validity.

- gold label kind: frequency, seizure-free, unknown, unresolved-multiple, and
  cluster labels;
- numeric rate labels versus vague or `multiple` labels;
- seizure-free durations shorter than one year versus one year or longer;
- unknown/no-reference boundary rows by gold label kind only;
- rows where the projection gate fires versus rows where it abstains;
- rows where the LLM sidecar rescue gate fires versus rows where it abstains;
- rows where both sidecars abstain and baseline remains final;
- rows with current-state markers: `current`, `currently`, `now`,
  `at present`, `ongoing`;
- rows with historical or negated distractor markers: `previously`,
  `history of`, `denies`, `no`, `last`, `free of`;
- rows with cluster-language markers: `cluster`, `clusters`, `clustered`,
  `per cluster`;
- rows with ambiguity markers: `uncertain`, `unclear`, `not clear`,
  `difficult to quantify`, `variable`.

## Post-Hoc Analysis Boundary

Row-level locked-test inspection is allowed only after the first readout has
been written and frozen. Any such inspection is post-hoc final-evaluation
analysis, not development tuning.

If row-level review identifies a defect, record it as a holdout finding. Any
fix starts a new validation-cycle candidate and cannot be patched into this
test result.

## Stop Rules

Accept as a valid frozen holdout audit only if:

- all frozen inputs and pre-run checks were recorded before execution;
- no locked-test row-level inspection occurred before the first readout;
- no code, prompt, model, scorer, repair, graph, schema, threshold, or gate
  change was made to complete or interpret the audit;
- changed rows keep exact evidence and valid source ids;
- deterministic-correct regressions remain zero, or any nonzero count is
  recorded as a failure of the candidate rather than tuned away;
- claim language preserves hybrid deterministic-safety-floor attribution.

Mark revise-only or reject if:

- the run requires any policy or implementation change;
- evidence or source-id validity breaks systemically;
- the improvement depends mainly on benchmark-format conventions;
- the LLM sidecar cannot be separately attributed from the projection gate;
- the result needs row-level locked-test tuning to be understandable or useful.

## Immediate Next Action

Do not run locked test from the validation-cycle manifest. If the user chooses
to proceed with holdout later, create or verify the runnable command against
this audit plan, record the frozen inputs, run the pre-run checks, and only then
execute the locked-test audit.
