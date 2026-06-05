# Project Status

Last updated: 2026-06-05

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

The current goal-achieving path is not another narrow switch layer. The repo now
has `structured_candidate_contract_v0` as the typed candidate/event gate for the
next validation ablation before any new holdout use.

## Current Strategy

Use saved artifacts as research instruments for component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators,
safety floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

The conservative staged assembly remains the active validation control:
716 prediction-bearing rows, 26 abstentions, and 8 human-review rows on
validation750. Trigger-context release is rejected, and last-event automatic
release remains blocked under `last_event_duration_policy_v0`.

Return to validation and synthetic hard panels for a new mechanism that can
beat the deterministic locked-test ceiling. Do not tune from test row-level
failures, and do not inspect locked-test row-level diagnostics.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning.
- Any holdout-facing use needs a frozen predeclared audit and explicit user
  authorization.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Final F1 is secondary to candidate recall, evidence exactness, projection
  consistency, metadata completeness, ambiguity preservation, and regression
  accounting.
- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.

## Current Evidence

RQ1-RQ10 now have bounded validation-development answers or explicit claim
boundaries. RQ3 remains positive but has unresolved projection-policy work.
Important standing numbers:

- `selective_safety_floor_gate_v0`: 21 validation750 changes with 11 W->C and
  0 C->W; 14 frozen local test450 changes with 8 W->C and 0 C->W.
- RQ9 v3: 716/750 validation rows covered, 26 abstained, 8 routed to human
  review; covered-row Purist accuracy 0.9469.
- RQ10: among 53 residual Purist misses, 23 `underdetermined_note`, 19
  `true_extraction_failure`, 11 `benchmark_convention_dominated`, and 0 strong
  likely gold defects.
- Conservative staged assembly component matrix: 750/750 unique validation
  rows, 716 prediction-bearing rows, 34 non-predictions, 0 verifier rows used,
  and 0 parse/evidence/schema issue rows.
- Trigger-context release promotion gate rejected the only release row: 0 W->C,
  0 C->W, and 1 category-correct-not-exact-label caveat.
- `last_event_duration_policy_v0`: 1 duration-auditable row, 0 automatic
  release-ready rows.
- `structured_candidate_contract_v0` direct-labeler validation750 panel:
  539 prediction-bearing rows, 26 W->C, 121 C->W on prediction-bearing rows,
  parse-ok plus exact-evidence rate 0.3469; blocked before holdout.
- Direct-labeler structured family audit found clean seed slices only:
  `seizure_free->unknown` has 7 W->C / 0 C->W and `yearly->daily` has
  5 W->C / 0 C->W; all clean slices are far below the 60 W->C gate.
- `structured_seed_expansion_panel_v0` now provides a synthetic hard/control
  mechanism surface: 180 rows, 90 hard and 90 matched controls across
  `seizure_free_to_unknown`, `yearly_to_daily`, and `cluster_completion`.
- `structured_seed_event_generator_v0` passed the synthetic smoke on that panel:
  90/90 hard rows emitted, 90/90 controls suppressed, 180/180 exact evidence.

Core plans and artifacts:

- End-to-end assembly plan:
  `docs/research/gan2026_multi_component_assembly_end_to_end_plan_2026-06-04.md`
- Component evidence matrix:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`
- Trigger release gate:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_trigger_release_promotion_2026-06-04.json`
- Assembly experiment log:
  `experiments/gan2026_multi_component_assembly_experiment_log_2026-06-05.md`
- Structured candidate direct-labeler panel:
  `experiments/gan2026_structured_candidate_event_contract_v0_direct_labeler_validation750_panel_2026-06-05.json`
- Structured candidate family audit:
  `experiments/gan2026_structured_candidate_event_contract_v0_direct_labeler_family_audit_2026-06-05.json`
- Structured seed expansion panel:
  `experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.json`
- Structured seed event generator smoke:
  `experiments/gan2026_structured_seed_event_generator_v0_synthetic_panel_2026-06-05.json`

## Work Board

### Now

- Design the next structured mechanism around high-precision candidate
  generation, not broad direct-labeler switching: target at least 60 W->C,
  <=5% C->W, and >=95% parse-ok plus exact-evidence on validation hard/control
  panels.
- Expand from the clean seed slices (`seizure_free->unknown`, `yearly->daily`,
  and cluster completion) through typed event generation plus matched controls;
  do not promote family-slice rules directly.
- Translate `structured_seed_event_generator_v0` into validation hard/control
  row selection and typed event extraction for the same three seed families.
  Do not use locked test rows.
- Keep the structured surface validation-only until those gates pass and a
  frozen test450 protocol addendum is written.

### Next

- Decide whether the next architecture should be a typed candidate contract
  layered over current components or a richer structured event representation
  with explicit projection ownership.
- Build synthetic hard/control panels that stress prediction-bearing failures,
  not only nonprediction repair opportunities.
- Write a frozen test450 protocol addendum only after the structured
  candidate/event validation gates pass.
- If cost/latency/token efficiency is needed, run a telemetry-only pass over
  surviving primitives before strengthening RQ8 claims.

### Blocked

- Whole-pipeline promotion is blocked until a family-indexed matrix exists as
  an auditable assembled candidate and any holdout-facing use has a frozen
  protocol.
- Trigger-context release is rejected as a behavior change because it failed
  the predeclared promotion gate.
- Last-event automatic release remains blocked under
  `last_event_duration_policy_v0`.
- Few-shot train-exemplar and direct-labeler targeted switch branches are
  blocked as goal-achieving paths: both were validation-clean enough to study
  but far too low-coverage on frozen aggregate-only test450 audits.

### Done Recently

- 2026-06-05: Closed the direct-labeler targeted switch branch as safe but
  low-coverage. Validation750 targeted switching projected 717/750 with 9 W->C
  and 0 C->W, but frozen aggregate-only test450 selected only 4 rows with
  1 W->C and 0 C->W, leaving the final proxy at 354/450 (0.7867). No test
  row-level inspection was performed or authorized.
- 2026-06-05: Added `structured_candidate_contract_v0` with typed candidate
  event rows and validation gate accounting for >=150 coverage, >=60 W->C,
  <=5% C->W, and >=95% parse-ok plus exact-evidence before any frozen test
  audit.
- 2026-06-05: Materialized the first structured candidate/event panel from the
  saved direct-labeler full-validation surface. It covers 539 prediction-bearing
  rows but fails promotion gates: 26 W->C, 121 C->W, and 0.3469 parse-ok plus
  exact-evidence rate.
- 2026-06-05: Added a structured family audit over that panel. It found clean
  seed slices (`seizure_free->unknown` 7 W->C / 0 C->W; `yearly->daily`
  5 W->C / 0 C->W), but the decision is `seed_slices_only_undercoverage`.
- 2026-06-05: Added `structured_seed_expansion_panel_v0`, a 180-row synthetic
  hard/control mechanism panel with exact evidence strings and no holdout use.
- 2026-06-05: Added `structured_seed_event_generator_v0` and ran the synthetic
  smoke: 90/90 hard rows emitted, 90/90 controls suppressed, 180/180 exact
  evidence. This only promotes to validation hard/control design.
- 2026-06-05: Closed the train-exemplar few-shot branch as non-goal-achieving.
  The few-shot-specific contract was clean on validation750 (708/750 ->
  726/750; 18 W->C, 0 C->W), but frozen aggregate-only test450 reached only
  357/450 (0.7933), with 4 W->C and 0 C->W.
- 2026-06-05: Implemented `last_event_duration_policy_v0`, added focused
  policy tests, and rebuilt the validation750 staged assembly chain. The policy
  found 1 duration-auditable last-event row and 0 automatic release-ready rows.
- 2026-06-05: Materialized `component_evidence_matrix_v0` for the conservative
  candidate validation750 assembly: 716 predict / 26 abstain / 8 human review,
  0 verifier rows used, 0 parse/evidence/schema issue rows.
- 2026-06-05: Rejected `trigger_release_promotion_analysis_v0`; the proposed
  release failed the predeclared trigger promotion gate.
- 2026-06-05: Rechecked candidate-union, structural-guard, combined switch,
  direct-labeler, and few-shot branches. They show validation headroom but do
  not provide enough holdout-like coverage to reach the >=0.9 locked-test
  target without a new typed candidate/event mechanism.
- 2026-06-04: Added ADR 0010 for component homes before pipeline assembly and
  materialized the no-call staged-hybrid assembly surface.
