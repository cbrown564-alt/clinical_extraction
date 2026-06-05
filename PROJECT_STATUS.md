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
- `boundary_benchmark_seed_panel_v0` is now the broadened H3/H7 contract surface
  for that posture: 36 synthetic rows, 18 minimal pairs, 18 clinical-state
  invariant pairs, 36 exact-evidence rows, 20 boundary rows, and 16 renderer
  rows. It is not final-label promotion evidence.
- `boundary_benchmark_contract_v0` now executes the typed boundary classifier
  and benchmark renderer over that broadened panel: 36/36 contract-matched rows,
  36/36 exact-evidence rows, 18/18 clinical-state invariant pairs, and
  final-label policy remains disconnected.
- `boundary_benchmark_validation_panel_v0` ports only the stable typed fields to
  validation hard slices: 30 validation rows, 19 boundary rows, 11 renderer rows,
  22 hard rows, 8 controls, 30/30 exact-evidence rows, no note text in
  artifacts, and final-label policy disconnected.
- `boundary_benchmark_validation_contract_v0` passed the validation mechanism
  smoke: 30/30 contract-matched rows, 30/30 exact-evidence rows, 0 note-text
  rows, 22 hard rows, 8 controls, and final-label policy disconnected. It
  remains validation-development mechanism evidence only.
- `boundary_benchmark_candidate_assembly_v0` resolves the architecture decision
  in favor of a shallow typed-candidate-contract layer over the current
  assembled candidate, but only as a diagnostic validation artifact: 30 selected
  rows, 6 W->C, 1 C->W, 30/30 exact-evidence rows, 0 note-text rows, and blocked
  by coverage plus W->C gates before any frozen audit.
- `h3_h7_full_boundary_benchmark_test_v0` fully tests the current
  boundary/benchmark H3/H7/H8 branch. H3 is rejected for the shallow typed
  layer: all-eligible validation exposure is clean but only 36 rows with
  6 W->C and 1 C->W, below coverage and W->C gates. H7 is supported on the
  synthetic minimal-pair panel: typed behavior is consistent on 18/18 pairs
  while the deterministic comparator flips on 4/18 pairs. H8 is partially
  supported as validation-development mechanism evidence: 11/11 benchmark
  convention rows have exact evidence and separated clinical/rendered fields,
  but no locked-test transfer audit was run.
- `h5_semantic_repair_gap_test_v0` partially supports and revises H5. Validation
  repair layers mask weak raw LLM behavior, but the original raw-layer-gap
  primary signal is wrong: raw/base validation-test gap is -0.0240, full-repair
  gap is 0.1747, and validation receives a 0.1987 larger repair gain than
  locked test. Treat this as deterministic semantic repair and contract-coverage
  overfitting validation, not LLM-owned transfer success.
- `h5_repair_policy_v1_manifest` freezes H5 policy v1 as the current bounded
  repair contract for the next validation diagnostic: frequency-bearing
  predictions may not become no-reference, per-hour rates render as
  `multiple per day`, vague frequency words remain unresolved-multiple labels,
  cluster context preserves frequency content, renderer effects remain
  separate from clinical selection, and holdout use is not authorized.
- `h9_action_policy_gap_v0` partially supports H9 as an action-policy shift,
  not as the primary gap explanation. Validation has 34/750 nonprediction or
  review rows, all safety-floor-owned, including 19 blocked deterministic-correct
  labels and 15 blocked deterministic-wrong labels. The aggregate locked-test
  selector readout has only 1/450 nonprediction row, and no locked-test row-level
  artifacts were written.
- `structured_event_projection_audit_v0` switches the rejected shallow
  boundary/renderer bridge into an explicit structured event/projection schema:
  30/30 rows have explicit projection ownership, 19 boundary-projection rows,
  11 benchmark-renderer rows, 6 W->C, 1 C->W carried as a no-regression case,
  and 1.0000 parse-ok plus exact-evidence. It is schema-ready but still blocked
  by coverage and W->C gates before any frozen audit.
- `structured_seed_projection_generator_v0` broadens the synthetic structured
  seed generator around that projection-owner schema: 180 synthetic rows,
  90/90 hard rows emitted, 90/90 controls suppressed, 180/180 exact-evidence
  rows, 180/180 explicit projection-owner rows, and 0 source-note-text rows.
  It promotes only to validation projection-owner panel design.
- `structured_validation_projection_panel_v0` ports the projection-owner schema
  to validation hard/control expansion: 47 rows, 23 hard rows, 23 matched
  controls, 1 boundary no-regression case, 24 prediction-bearing rows, 23 W->C,
  1 C->W, 1.0000 parse-ok plus exact-evidence, 47/47 explicit
  projection-owner rows, and 0 source-note-text rows. Frozen test remains
  blocked by coverage and W->C gates.
- `structured_validation_projection_extractor_v0` passes the validation
  projection-owner extractor smoke under the inherited control-evidence policy:
  47 rows, 23/23 hard rows emitted, 23/23 controls suppressed, the boundary
  no-regression row suppressed, 23 selected prediction-bearing W->C rows, 0 C->W
  releases, 23/23 hard exact-evidence rows, 21/23 control references retrievable,
  and 0 source-note-text rows. It remains undercovered before any frozen audit.
- `structured_projection_expansion_source_audit_v0` rejects broadening from the
  saved direct-labeler structured source: among 187 clean prediction-bearing
  rows it has only 6 W->C, 40 C->W, and just 1 novel clean W->C beyond the
  current projection extractor. It is not a safe source for validation expansion.
- `structured_validation_hard_opportunity_miner_v0` shows the current
  validation assembly cannot satisfy the 60 W->C gate on its fixed
  prediction-bearing residual surface: it finds 38 hard W->C opportunities,
  40 matched controls, 1 no-regression row, 0 C->W rows, and only 0.6053
  parse-ok plus exact-evidence because many broad gold references are not exact
  extractor spans. The remaining incorrect validation rows include 38 predicts,
  9 abstentions, and 6 human-review rows.
- `structured_synthetic_hard_opportunity_panel_v0` adds synthetic development
  data for undercovered projection-owner mechanisms: 240 rows, 120 hard and
  120 matched controls across `unknown_frequency`, `cluster_frequency`,
  `daily_frequency`, and `other_frequency`; 240/240 exact-evidence rows and
  explicit projection ownership. It is not validation, holdout, or benchmark
  evidence.

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
- H5 semantic repair gap test v0:
  `experiments/gan2026_h5_semantic_repair_gap_test_v0_2026-06-05.json`,
  `experiments/gan2026_h5_semantic_repair_gap_test_v0_2026-06-05.md`
- H5 semantic repair inventory and family ablation v0:
  `experiments/gan2026_h5_repair_inventory_v0_2026-06-05.json`,
  `experiments/gan2026_h5_repair_inventory_v0_2026-06-05.md`,
  `experiments/gan2026_h5_repair_family_ablation_v0_2026-06-05.json`,
  `experiments/gan2026_h5_repair_family_ablation_v0_2026-06-05.md`
- H5 repair policy v1 no-call reparse:
  `experiments/gan2026_h5_repair_policy_v1_reparse_validation250_2026-06-05.json`,
  `experiments/gan2026_h5_repair_policy_v1_reparse_validation250_2026-06-05.md`,
  `experiments/gan2026_h5_semantic_kind_transformations_policy_v1_validation250_2026-06-05.csv`,
  `experiments/gan2026_h5_semantic_kind_transformations_policy_v1_validation250_2026-06-05.md`
- H5 repair policy v1 manifest:
  `experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.json`,
  `experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.md`
- H9 action-policy gap v0:
  `experiments/gan2026_h9_action_policy_gap_v0_2026-06-05.json`,
  `experiments/gan2026_h9_action_policy_gap_v0_2026-06-05.md`
- Generalization-first boundary/convention solution design:
  `docs/research/gan2026_generalization_first_boundary_and_benchmark_solution_design_2026-06-05.md`
- Boundary/benchmark H3/H7 seed panel v0:
  `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`,
  `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.md`
- Boundary/benchmark H3/H7 contract smoke v0:
  `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json`,
  `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.md`
- Boundary/benchmark validation hard-slice panel v0:
  `experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.json`,
  `experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.md`
- Boundary/benchmark validation contract smoke v0:
  `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.json`,
  `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.md`
- Boundary/benchmark candidate assembly v0:
  `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.json`,
  `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.md`
- H3/H7/H8 full boundary/benchmark test v0:
  `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.json`,
  `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.md`
- Validation-test gap staged action plan:
  `docs/research/gan2026_validation_test_gap_staged_action_plan_2026-06-05.md`
- Structured event/projection audit v0:
  `experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.json`,
  `experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.md`
- Structured seed projection generator v0:
  `experiments/gan2026_structured_seed_projection_generator_v0_2026-06-05.json`,
  `experiments/gan2026_structured_seed_projection_generator_v0_2026-06-05.md`
- Structured validation projection panel v0:
  `experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.json`,
  `experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.md`
- Structured validation projection extractor v0:
  `experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.json`,
  `experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.md`
- Structured projection expansion-source audit v0:
  `experiments/gan2026_structured_projection_expansion_source_audit_v0_2026-06-05.json`,
  `experiments/gan2026_structured_projection_expansion_source_audit_v0_2026-06-05.md`
- Structured validation hard-opportunity miner v0:
  `experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.json`,
  `experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.md`
- Structured synthetic hard-opportunity panel v0:
  `experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.json`,
  `experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.md`

## Work Board

### Now

- Run a synthetic projection generator smoke over
  `structured_synthetic_hard_opportunity_panel_v0`; require hard emits, matched
  control suppression, exact evidence, and explicit projection ownership before
  porting any new mechanism back to validation.
- Use `h5_repair_policy_v1_manifest` as the current bounded repair contract for
  the next validation diagnostic; do not restore broad frequency-to-sentinel
  repair or mix repair-policy changes with boundary/renderer mechanism changes.
- Extend the gap-matrix adapters only when a saved artifact has an explicit
  row-source contract. The current matrix intentionally uses only the staged
  assembly component seed and skips locked-test row-level artifacts.
- Design the next structured mechanism around high-precision candidate
  generation, not broad direct-labeler switching: target at least 60 W->C,
  <=5% C->W, and >=95% parse-ok plus exact-evidence on validation hard/control
  panels.

### Next

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

- 2026-06-05: Added `structured_synthetic_hard_opportunity_panel_v0`, a
  240-row synthetic development panel with 120 hard opportunities and 120
  matched controls across four undercovered projection-owner mechanism families.
  It is ready for a synthetic generator smoke and carries no validation,
  holdout, or benchmark claim.
- 2026-06-05: Added `structured_validation_hard_opportunity_miner_v0`, the
  aggressive validation opportunity miner requested for option 1. It shows the
  current validation assembly cannot reach the 60 W->C gate on prediction-bearing
  residual misses: only 38 hard W->C opportunities remain, with 15 more wrong
  rows sitting in abstain/human-review actions.
- 2026-06-05: Added `structured_projection_expansion_source_audit_v0`, rejecting
  the saved direct-labeler structured source as a broadening path. It offers
  only 1 novel clean W->C beyond the current extractor and carries 40 clean C->W
  rows, so the next expansion must come from explicit mechanism panel design.
- 2026-06-05: Added `structured_validation_projection_extractor_v0`, which
  passes the validation projection-owner extractor smoke while still blocking
  frozen-test use. It emits 23/23 hard opportunities, suppresses 23/23 matched
  controls plus the boundary no-regression case, releases 0 C->W rows, and keeps
  source note text out of artifacts.
- 2026-06-05: Added `structured_validation_projection_panel_v0`, a 47-row
  validation-development projection-owner panel with 23 hard rows, 23 matched
  controls, and 1 boundary no-regression case. It preserves explicit projection
  ownership and exact evidence for all rows but remains below coverage and W->C
  gates.
- 2026-06-05: Added `structured_seed_projection_generator_v0`, a synthetic
  projection-owner-aware generator smoke over 180 rows. It emitted 90/90 hard
  cases, suppressed 90/90 controls, preserved exact evidence and explicit
  projection ownership for all rows, and promotes only to validation panel
  design.
- 2026-06-05: Added `structured_event_projection_audit_v0`, replacing the
  shallow boundary/renderer bridge as the active representation path. The schema
  is ready for validation expansion with 30/30 explicit projection-owner rows
  and 0 source-note-text rows, but frozen-test use remains blocked by coverage
  and W->C gates.
- 2026-06-05: Added `h5_repair_policy_v1_manifest`, freezing H5 policy v1 as
  the bounded repair contract for the next validation diagnostic. It confirms
  0 `frequency->no_reference` transitions, requires renderer effects to remain
  separate from clinical selection, and keeps holdout use unauthorized.
- 2026-06-05: Added a staged action plan for the validation-test gap program.
  The next sequence is deliberately non-confounded: freeze the control state,
  review/ablate semantic repair families, then test richer boundary/benchmark
  typed-event mechanisms with H6 controls and H10 provenance sidecars before
  any frozen aggregate test audit.
- 2026-06-05: Added H5 semantic repair inventory and same-output family
  ablation artifacts. Format-only repair remains allowed; selected-evidence
  arithmetic is `revise_or_bound` because it has 32 W->C and 1 C->W; benchmark
  convention rendering remains `review_required` despite 16 W->C and 0 C->W
  because it owns semantic-kind and category transitions.
- 2026-06-05: Added H5 repair policy v1 and a validation250 no-call reparse.
  The policy removes broad frequency-to-no-reference demotion, maps per-hour
  rates to `multiple per day`, preserves cluster frequency content, and renders
  vague frequency words as unresolved multiple. Benchmark-aligned validation250
  replay improves from 204 to 213 Purist-correct rows with 25 W->C, 0 C->W, and
  no `frequency->no_reference` transitions.
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
- 2026-06-05: Implemented `boundary_benchmark_contract_v0`. The no-call
  mechanism smoke passed all seed-panel rows, preserving exact evidence and
  separate clinical-state versus Gan-rendered-label fields without connecting to
  final-label policy.
- 2026-06-05: Broadened `boundary_benchmark_seed_panel_v0` and
  `boundary_benchmark_contract_v0` with generated hard/control cases. The
  synthetic mechanism surface now has 36 rows, 18 invariant pairs, 36/36 exact
  evidence rows, 36/36 contract matches, and still no final-label policy
  connection.
- 2026-06-05: Added `boundary_benchmark_validation_panel_v0`, a validation-only
  hard-slice port of stable boundary/renderer typed fields. It selected 30 rows
  with 30/30 exact evidence, omitted note text from artifacts, and kept
  final-label policy disconnected.
- 2026-06-05: Added `boundary_benchmark_validation_contract_v0`, a validation
  typed-field smoke over that panel. It passed 30/30 contract matches with
  30/30 exact evidence rows, 0 note-text rows, and no final-label policy
  connection.
- 2026-06-05: Added `boundary_benchmark_candidate_assembly_v0`, choosing the
  typed-candidate-contract layer as the next validation-only architecture
  bridge. It remains diagnostic only: 30 selected rows, 6 W->C, 1 C->W, 100%
  parse-ok plus exact-evidence, and blocked by coverage plus W->C gates.
- 2026-06-05: Added `h3_h7_full_boundary_benchmark_test_v0`. H3 is rejected for
  the shallow typed layer because all-eligible validation exposure is clean but
  only 36 rows with 6 W->C, below coverage and W->C gates. H7 is supported:
  typed behavior is pair-consistent on 18/18 synthetic pairs while the
  deterministic comparator flips on 4/18 pairs. H8 is partially supported as
  validation-development mechanism evidence: 11/11 benchmark convention rows
  have exact evidence and separated clinical/rendered fields. No locked-test
  row-level artifacts were used.
- 2026-06-05: Added `h5_semantic_repair_gap_test_v0` using the saved
  same-output validation ladder plus aggregate-only few-shot validation/test
  readouts. H5 is partially supported and revised: validation repair gain is
  0.2320 versus 0.0333 on locked test, while raw/base validation-test gap is not
  larger than full repair. No locked-test row-level artifacts were used.
- 2026-06-05: Added `h9_action_policy_gap_v0` from the validation gap matrix
  plus aggregate-only locked-test nonprediction selector readout. H9 is
  partially supported as an action-policy split shift, but not as the main gap
  explanation: validation has 34/750 nonprediction/review rows, while the
  aggregate locked-test selector readout has 1/450. No locked-test row-level
  artifacts were written.
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
