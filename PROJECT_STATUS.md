# Project Status

Last updated: 2026-06-05

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

The active path is the validation-test generalisation gap program. Use saved
artifacts as research instruments for component questions, not as whole-pipeline
F1 trophies. The boundary/benchmark typed-event layer is promoted as a bounded
rare-family component for eligible boundary and benchmark-rendering cases, not
as a broad aggregate-gap fix. Stage 4 action-policy sidecars and H6/H9 controls
are complete for the current cycle; the next candidate cycle must attach these
sidecars and H10 provenance before interpreting deltas.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning; any holdout-facing use needs a
  frozen protocol and explicit user authorization.
- `rules_only_v1` remains the frozen transparent comparator.
- `untagged_nonprediction_release_candidate_v0_assembled_candidate` is the
  current auditable validation assembly control.
- `h5_repair_policy_v1_manifest` is the bounded repair contract for new
  diagnostics; do not mix repair-policy changes with boundary/renderer changes.
- Final F1 is secondary to candidate recall, exact evidence, projection
  consistency, metadata completeness, ambiguity preservation, and regression
  accounting.

## Current Evidence

- Conservative staged assembly on validation750: 735 prediction-bearing rows
  after untagged nonprediction releases, 697 correct prediction rows, 37/37 H6
  controls preserved, and 0 release-wrong rows.
- `selective_safety_floor_gate_v0`: validation750 21 changes with 11 W->C and
  0 C->W; frozen local test450 14 changes with 8 W->C and 0 C->W.
- H5 policy v1 is frozen as bounded repair; renderer effects stay separate from
  clinical selection.
- `structured_projection_port_promoted_v0` was explicitly authorized despite
  failed validation gates and then rejected on frozen aggregate-only test450:
  base 342/450 Purist proxy 0.7600 fell to 337/450 proxy 0.7489, with 7 W->C,
  12 C->W, and changed-label precision 0.3684. No locked-test row-level artifact
  was written.
- `h10_raw_identity_sidecar_v1`: paired validation750 raw outputs are
  byte-identical on 750/750 matched rows, with 0 calls and 0 prediction changes.
- Boundary typed-event cycle is complete and promoted as a bounded
  rare-family component. It passed contract, validation-panel, H7, and
  renderer-fixture gates; after selector precision revision, the eligible
  validation typed panel has 6 W->C, 0 C->W, 0 H6 regressions, 0 source-note-text
  rows, and no final-label policy connection in the diagnostic artifacts.
  Coverage is accepted as intrinsically bounded because boundary/benchmark
  cases are rare; the claim is component-level support, not aggregate
  validation-test gap closure.
- Stage 4 H6/H9 sidecars are complete for the current validation control:
  action summary coverage is 735/750 prediction-bearing rows with 9 abstain and
  6 review rows after 19 deterministic-comparator fallback releases;
  release-lane ablation passes guardrails with 17 abstain-lane W->C, 2
  human-review-lane W->C, 0 C->W, and 0 H6 regressions; H6 replay passes across
  the current assembled control, boundary selector precision revision, and the
  release-lane sidecar.

## Core Artifacts

- Assembly plan: `docs/research/gan2026_multi_component_assembly_end_to_end_plan_2026-06-04.md`
- Gap staged action plan: `docs/research/gan2026_validation_test_gap_staged_action_plan_2026-06-05.md`
- Current validation assembly control: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.json`
- H5 repair policy v1: `experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.json`
- Rejected structured projection audit: `experiments/gan2026_structured_projection_port_test450_aggregate_audit_2026-06-05.json`
- H10 raw identity sidecar: `experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.json`
- Boundary event contract v1: `experiments/gan2026_boundary_event_contract_v1_2026-06-05.json`
- Boundary event validation panel v1: `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.json`
- H7 minimal pair panel v1: `experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.json`
- Benchmark renderer fixture v1: `experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.json`
- Boundary renderer component ablation v1: `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.json`
- Boundary selector precision revision v1: `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json`
- H9 action summary sidecar v1: `experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.json`
- H9 release lane ablation v1: `experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.json`
- H6 control replay v1: `experiments/gan2026_h6_control_replay_v1_2026-06-05.json`
- Boundary/renderer promotion decision:
  `docs/decisions/0011-promote-boundary-renderer-rare-family-component.md`

## Work Board

### Now

- Start any new mechanism work as a validation-only cycle with H6/H9 action
  sidecars and H10 provenance attached before interpreting deltas.
- Include the promoted boundary/renderer typed-event component only on eligible
  boundary and benchmark-rendering cases, with selector suppression and
  component-owner attribution intact.
- Keep `structured_projection_port_promoted_v0` and broad action-policy widening
  as rejected/revise-only; do not promote either as the lead path.

### Next

- If a new prediction-bearing candidate is assembled, attach H6 action summaries
  and the H10 raw-identity sidecar before interpreting deltas.

### Blocked

- Whole-pipeline promotion remains blocked until a holdout-facing frozen
  protocol is authorized.
- Trigger-context release is rejected as a behavior change.
- Last-event automatic release remains blocked under
  `last_event_duration_policy_v0`.
- Few-shot train-exemplar, direct-labeler targeted switch, and broad structured
  projection port branches are closed as goal-achieving paths.

### Done Recently

- 2026-06-05: Completed Stage 4 action-policy sidecars:
  `h9_action_summary_sidecar_v1`, `h9_release_lane_ablation_v1`, and
  `h6_control_replay_v1`. The current control has 735/750 prediction-bearing
  rows, 15 remaining nonprediction rows, 19 fallback releases, 0 release C->W,
  and 0 H6 regressions across replayed candidates.
- 2026-06-05: Promoted the boundary/renderer typed-event layer as a bounded
  rare-family component for eligible boundary and benchmark-rendering cases.
  The promotion accepts low coverage as intrinsic to the target family and does
  not authorize whole-pipeline promotion, holdout use, or benchmark-comparable
  language.
- 2026-06-05: Added `boundary_selector_precision_revision_v1`; suppressed the
  unsafe last-event override and unknown/no-reference churn, producing 6 W->C,
  0 C->W, and 0 H6 regressions on the 30-row validation typed panel. Corrected
  the reusable W->C gate from impossible 60+ to 25.
- 2026-06-05: Marked the Stage 2/3 boundary-renderer bundle complete in the
  staged action plan and moved the active board to Stage 4 action-policy
  sidecars.
- 2026-06-05: Ran `boundary_renderer_component_ablation_v1`; benchmark-only rows
  were 11/11 C->C, but clinical boundary projection caused 1 H6 C->W regression
  before selector precision revision, so the initial ablation was rejected.
- 2026-06-05: Added `benchmark_renderer_fixture_v1`; 16/16 renderer rows
  preserved clinical state with renderer rule ids and scorer-sentinel use
  explicit.
- 2026-06-05: Added `h7_minimal_pair_panel_v1`; typed state was invariant for
  18/18 synthetic pairs.
- 2026-06-05: Added `boundary_event_contract_v1` and
  `boundary_event_validation_panel_v1`; synthetic and validation typed-event
  gates passed with final-label policy disconnected.
- 2026-06-05: Added `h10_raw_identity_sidecar_v1`; paired validation raw
  outputs are byte-identical on 750/750 matched rows.
- 2026-06-05: Ran the authorized frozen aggregate-only structured projection
  port audit; the promoted policy was rejected.
- 2026-06-05: Froze H5 repair policy v1 and moved boundary/benchmark work to a
  generalization-first typed-event posture.
