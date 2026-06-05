# Project Status

Last updated: 2026-06-05

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

The current goal-achieving path is not another narrow switch layer. The repo now
has `structured_candidate_contract_v0` as the typed candidate/event gate for the
next validation ablation before any new holdout use.

The immediate research-control path is the validation-test generalisation gap
program: instrument component attribution and test named hypotheses before
adding or promoting another prediction-bearing architecture.

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

Near-term work should run component-stress ablations on the selected H2/H4
panel with H6 as the transfer-control hypothesis. Broad validation F1 movement
is not an adequate learning goal.

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
- `structured_seed_validation_panel_v0` selected a conservative real validation
  hard/control surface for those seed families: 46 rows, 23 hard and 23 matched
  controls, with no note text written to artifacts.
- `structured_seed_validation_extractor_v0` passed that validation smoke but is
  blocked by undercoverage: 23/23 hard rows emitted with exact candidate
  evidence, 23/23 controls suppressed, 0 action mismatches, and only 23 hard
  opportunities versus the required 60 W->C and 150 prediction-bearing rows.
- `validation_test_gap_hypothesis_selection_v0` selects exactly three controlled
  hypotheses: H2 component ownership, H4 evidence versus projection/rendering,
  and H6 selective-action transfer control. The matrix used 0 locked-test
  row-level artifacts.
- `h2_h4_validation_component_stress_panel_v0` is ready for ablation: 106
  validation-only rows, 69 hard rows, 37 controls, 38 hard exact-evidence rows,
  31 hard nonprediction rows, and 0 locked-test row-level artifacts used.
- `h2_h4_validation_component_stress_ablation_v0` passed the H6 no-regression
  controls but found no W->C gains on the hard panel: staged final policy
  changed 31/106 rows, with 0 W->C, 0 C->W, 16 C->nonprediction, and
  15 W->nonprediction.
- `nonprediction_recovery_audit_v0` selected `untagged_nonprediction` as the
  only broad recovery lane worth testing: 19 releases, 19 C->nonprediction
  recoveries, and 0 wrong-baseline releases on validation750; releasing all
  nonpredictions would release 15 wrong baselines.
- `untagged_nonprediction_release_candidate_v0` passes the validation
  no-regression gate: 19 released rows, 19 release-correct, 0 release-wrong,
  735 prediction-bearing rows, 697 correct prediction rows, and 37/37 H6
  controls preserved.
- `untagged_nonprediction_release_candidate_v0` is frozen in a validation-only
  protocol addendum: release only staged nonpredictions with no hidden-family
  tags through deterministic-comparator fallback; no holdout use is authorized.
- `untagged_nonprediction_release_candidate_v0_assembled_candidate` is now the
  auditable validation-development assembly record: 750 rows, 19 release-eligible
  rows, 19 releases, 0 release-wrong rows, 735 prediction-bearing rows, 697
  correct prediction rows, 37/37 H6 controls preserved, and 0 locked-test
  row-level artifacts used. Holdout use remains unauthorized.
- H1 hidden-family mix is now tested as an aggregate-only slice readout over
  `selective_safety_floor_gate_v0`: validation proxy 0.9440 versus test proxy
  0.7800. The result is inconclusive rather than accepted because broad,
  overlapping families show gaps across much of the surface; use the sharper
  family gaps as strata for H3/H7, not as a primary explanation.
- Generalization-first design is now the active research posture for
  seizure-free duration and benchmark-format convention. A validation exact-label
  drop is acceptable only when a predeclared, source-grounded mechanism separates
  clinical boundary semantics from scorer-facing benchmark rendering and is
  tested on hard/control panels.
- `boundary_benchmark_seed_panel_v0` is the first H3/H7 contract surface for
  that posture: 12 synthetic rows, 6 minimal pairs, 6 clinical-state invariant
  pairs, 12 exact-evidence rows, 6 boundary rows, and 6 renderer rows. It is
  ready for mechanism contract tests and is not final-label promotion evidence.

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
- Structured seed validation panel:
  `experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.json`
- Structured seed validation extractor smoke:
  `experiments/gan2026_structured_seed_validation_extractor_v0_2026-06-05.json`
- Validation-test gap implementation plan:
  `docs/research/gan2026_validation_test_generalisation_gap_implementation_plan_2026-06-05.md`
- Validation-test gap hypothesis synthesis report:
  `docs/research/gan2026_validation_test_gap_hypothesis_synthesis_report_2026-06-05.md`
- Validation-test gap Phase 0 protocol and inventory:
  `docs/research/gan2026_validation_test_gap_protocol_2026-06-05.md`,
  `experiments/gan2026_validation_test_gap_artifact_inventory_2026-06-05.json`
- Validation-test surface map v0:
  `experiments/gan2026_validation_test_surface_map_v0_2026-06-05.json`
- Validation-test gap matrix v0:
  `experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl`,
  `experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.md`
- Validation-test gap hypothesis selection v0:
  `experiments/gan2026_validation_test_gap_hypothesis_selection_v0_2026-06-05.json`,
  `experiments/gan2026_validation_test_gap_hypothesis_selection_v0_2026-06-05.md`
- H2/H4 validation component-stress panel v0:
  `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.json`,
  `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.md`
- H2/H4 validation component-stress ablation v0:
  `experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.json`,
  `experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.md`
- Nonprediction recovery audit v0:
  `experiments/gan2026_nonprediction_recovery_audit_v0_2026-06-05.json`,
  `experiments/gan2026_nonprediction_recovery_audit_v0_2026-06-05.md`
- Untagged nonprediction release candidate v0:
  `experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.json`,
  `experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.md`
- Untagged nonprediction release candidate protocol addendum:
  `docs/research/gan2026_untagged_nonprediction_release_candidate_protocol_addendum_2026-06-05.md`
- Untagged nonprediction assembled-candidate artifact:
  `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.json`,
  `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.md`
- H1 hidden-family slice aggregates v0:
  `experiments/gan2026_h1_hidden_family_slice_aggregates_v0_2026-06-05.json`,
  `experiments/gan2026_h1_hidden_family_slice_aggregates_v0_2026-06-05.md`
- Generalization-first boundary/convention solution design:
  `docs/research/gan2026_generalization_first_boundary_and_benchmark_solution_design_2026-06-05.md`
- Boundary/benchmark H3/H7 seed panel v0:
  `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`,
  `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.md`

## Work Board

### Now

- Implement typed `seizure_free_boundary_event_v0` and
  `benchmark_convention_renderer_v0` contract tests against
  `boundary_benchmark_seed_panel_v0`; keep clinical state and Gan-rendered label
  separate, and do not connect the mechanisms to final-label policy yet.
- Extend the gap-matrix adapters only when a saved artifact has an explicit
  row-source contract. The current matrix intentionally uses only the staged
  assembly component seed and skips locked-test row-level artifacts.
- Design the next structured mechanism around high-precision candidate
  generation, not broad direct-labeler switching: target at least 60 W->C,
  <=5% C->W, and >=95% parse-ok plus exact-evidence on validation hard/control
  panels.

### Next

- Decide whether the next architecture should be a typed candidate contract
  layered over current components or a richer structured event representation
  with explicit projection ownership.
- Expand from the clean seed slices (`seizure_free->unknown`, `yearly->daily`,
  and cluster completion) through typed event generation plus matched controls;
  do not promote family-slice rules directly.
- Broaden `structured_seed_validation_extractor_v0` beyond its undercovered
  23-hard-row validation smoke before any frozen test audit.
- Build synthetic hard/control panels that stress prediction-bearing failures,
  not only nonprediction repair opportunities.
- Write a frozen test450 protocol addendum only after the structured
  candidate/event validation gates pass.
- If cost/latency/token efficiency is needed, run a telemetry-only pass over
  surviving primitives before strengthening RQ8 claims.

### Blocked

- Whole-pipeline promotion remains blocked until any holdout-facing use has a
  frozen protocol and explicit user authorization.
- Trigger-context release is rejected as a behavior change because it failed
  the predeclared promotion gate.
- Last-event automatic release remains blocked under
  `last_event_duration_policy_v0`.
- Few-shot train-exemplar and direct-labeler targeted switch branches are
  blocked as goal-achieving paths: both were validation-clean enough to study
  but far too low-coverage on frozen aggregate-only test450 audits.

### Done Recently

- 2026-06-05: Added a validation-test generalisation gap implementation plan,
  frozen Phase 0 protocol, machine-readable H1-H10 hypothesis registry,
  saved-artifact inventory, and aggregate-only surface-map generator. The first
  surface map reproduces roughly 17-point validation-test gaps for the closed
  targeted-switch, few-shot, and structural-guard branches without inspecting
  locked-test row-level failures.
- 2026-06-05: Added `validation_test_gap_matrix_v0` as the first Phase 2
  artifact: 1,534 validation-only layer rows from the staged assembly component
  seed, covering 750 deterministic comparator rows, 750 final-policy rows, and
  34 abstain/review monitor rows with 0 locked-test row-level artifacts used.
- 2026-06-05: Added `validation_test_gap_hypothesis_selection_v0`. It selects
  H2 component ownership, H4 evidence-versus-projection/rendering, and H6
  selective-action transfer control as the next controlled experiments.
- 2026-06-05: Added `h2_h4_validation_component_stress_panel_v0`, a
  validation-only component-stress design panel with 69 hard rows and 37
  deterministic-correct controls. It uses 0 locked-test row-level artifacts and
  is ready for component ablations, not architecture promotion.
- 2026-06-05: Added `h2_h4_validation_component_stress_ablation_v0`, a no-call
  validation ablation over the panel. Decision:
  `diagnostic_ablation_passed_h6_controls_but_nonprediction_pressure_remains`;
  H6 controls preserved 37/37, but staged final policy had 0 W->C, 0 C->W,
  16 C->nonprediction, and 15 W->nonprediction.
- 2026-06-05: Added `nonprediction_recovery_audit_v0` and
  `untagged_nonprediction_release_candidate_v0`. The selected release lane
  recovers 19 validation nonpredictions through deterministic-comparator
  fallback with 0 release-wrong rows and 37/37 H6 controls preserved; broader
  assembly still requires an auditable assembled-candidate artifact.
- 2026-06-05: Froze
  `untagged_nonprediction_release_candidate_v0` in a validation-only protocol
  addendum. The release rule is limited to staged nonpredictions with no
  hidden-family tags through deterministic-comparator fallback and still blocks
  holdout-facing use.
- 2026-06-05: Materialized
  `untagged_nonprediction_release_candidate_v0_assembled_candidate` as the
  auditable validation-development assembly record with row-level eligibility,
  original action, fallback label, candidate action, component ownership, H6
  membership, and aggregate accounting.
- 2026-06-05: Created a living validation-test gap hypothesis synthesis report.
  It records tested H2/H4/H6 evidence, interprets the untagged nonprediction
  patch as deterministic fallback action-policy recovery, and predeclares H1
  hidden-family slice aggregation as the next setup-heavy hypothesis.
- 2026-06-05: Added `h1_hidden_family_slice_aggregates_v0` and updated the
  synthesis report. H1 is inconclusive as a primary explanation: validation
  0.9440 versus test 0.7800, with gaps spread across overlapping families rather
  than concentrated cleanly in a small family set.
- 2026-06-05: Added a generalization-first solution design for seizure-free
  duration and benchmark-format convention. The next mechanism should use typed
  boundary events and explicit benchmark rendering, and may accept validation
  score loss if it improves principled transfer evidence.
- 2026-06-05: Added `boundary_benchmark_seed_panel_v0`, a 12-row synthetic H3/H7
  seed panel with exact evidence and pair-invariant clinical states for
  seizure-free boundary and benchmark-renderer contract tests.
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
- 2026-06-05: Added `structured_seed_validation_panel_v0` and
  `structured_seed_validation_extractor_v0`. The validation smoke passed on the
  seed panel, but the decision is `validation_smoke_passed_undercoverage`
  because it covers only 23 hard opportunities and cannot authorize holdout use.
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
- 2026-06-04: Completed Observatory Phase 5 scaffold: `/review` page with
  paper-ready report builder, run-comparison table, per-label performance table,
  error-taxonomy summary, evidence-audit table, and full-report Markdown/CSV
  export. Updated design doc and navbar.
