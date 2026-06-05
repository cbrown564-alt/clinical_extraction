# Project Status

Last updated: 2026-06-05

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

The active path is the validation-test generalisation gap program. Use saved
artifacts as research instruments for component questions, not as whole-pipeline
F1 trophies. The current mechanism track is boundary/benchmark typed events with
final-label policy disconnected.

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

- Conservative staged assembly on validation750: 716 prediction-bearing rows,
  26 abstentions, 8 human-review rows, covered-row Purist accuracy 0.9469.
- `selective_safety_floor_gate_v0`: validation750 21 changes with 11 W->C and
  0 C->W; frozen local test450 14 changes with 8 W->C and 0 C->W.
- `h2_h4_validation_component_stress_ablation_v0`: H6 controls preserved
  37/37, but hard-panel staged policy produced 0 W->C and 31 nonpredictions.
- `untagged_nonprediction_release_candidate_v0_assembled_candidate`: 19
  validation releases, 0 release-wrong rows, 735 prediction-bearing rows,
  697 correct prediction rows, and 37/37 H6 controls preserved.
- H5 policy v1 is frozen as bounded repair: no frequency-bearing predictions may
  become no-reference, per-hour rates render as `multiple per day`, vague
  frequency words remain unresolved multiple labels, and renderer effects stay
  separate from clinical selection.
- `structured_projection_port_promoted_v0` was explicitly authorized despite
  failed validation gates and then rejected on frozen aggregate-only test450:
  base 342/450 Purist proxy 0.7600 fell to 337/450 proxy 0.7489, with 7 W->C,
  12 C->W, and changed-label precision 0.3684. No locked-test row-level artifact
  was written.
- `h10_raw_identity_sidecar_v1`: paired validation750 raw outputs are
  byte-identical for `raw_output`, `llm_candidate_raw_output`, and
  `adjudicator_raw_output` on 750/750 matched rows. It made 0 model calls,
  changed 0 predictions, and wrote no row-level output artifact.
- `boundary_event_contract_v1`: synthetic typed-event contract passed with
  36/36 contract-matched rows, 18/18 invariant pairs, 36/36 exact-evidence rows,
  complete typed-event/projection-policy metadata on 36/36 rows, and final-label
  policy disconnected.
- `boundary_event_validation_panel_v1`: validation panel scanned 750 records
  and emitted 30 supported exact-evidence typed-event rows, with 19 boundary
  rows, 11 renderer rows, 22 hard rows, 8 controls, 0 unsupported candidate
  rows, 0 source-note-text rows, complete metadata on 30/30 rows, and final
  policy disconnected.

## Core Artifacts

- Assembly plan: `docs/research/gan2026_multi_component_assembly_end_to_end_plan_2026-06-04.md`
- Gap staged action plan: `docs/research/gan2026_validation_test_gap_staged_action_plan_2026-06-05.md`
- Current validation assembly control: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.json`
- H5 repair policy v1: `experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.json`
- Rejected structured projection audit: `experiments/gan2026_structured_projection_port_test450_aggregate_audit_2026-06-05.json`
- H10 raw identity sidecar: `experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.json`
- Boundary event contract v1: `experiments/gan2026_boundary_event_contract_v1_2026-06-05.json`
- Boundary event validation panel v1: `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.json`

## Work Board

### Now

- Run `h7_minimal_pair_panel_v1` to test whether the typed mechanism preserves
  clinical state across wording, order, section, distractor, semiology, and time
  anchor perturbations.
- Add `benchmark_renderer_fixture_v1` with clinical state frozen and renderer
  effects explicit.
- Treat `structured_projection_port_promoted_v0` as rejected/revise-only. Any
  follow-up must start a new validation-only cycle with stricter selector
  precision, especially around `unknown_frequency`.

### Next

- After contract and robustness gates pass, run
  `boundary_renderer_component_ablation_v1` as validation diagnostics.
- Attach H6 action summaries and the H10 raw-identity sidecar to any new
  candidate before interpreting deltas.

### Blocked

- Whole-pipeline promotion remains blocked until a holdout-facing frozen
  protocol is authorized.
- Trigger-context release is rejected as a behavior change.
- Last-event automatic release remains blocked under
  `last_event_duration_policy_v0`.
- Few-shot train-exemplar, direct-labeler targeted switch, and broad structured
  projection port branches are closed as goal-achieving paths.

### Done Recently

- 2026-06-05: Added `boundary_event_contract_v1`; synthetic typed-event
  contract passed and the next staged task is complete.
- 2026-06-05: Added `boundary_event_validation_panel_v1`; validation hard/control
  typed-event panel is ready with no unsupported candidate rows or note text.
- 2026-06-05: Added `h10_raw_identity_sidecar_v1`; paired validation raw
  outputs are byte-identical on 750/750 matched rows.
- 2026-06-05: Ran the authorized frozen aggregate-only structured projection
  port audit; the promoted policy was rejected.
- 2026-06-05: Froze H5 repair policy v1 and moved boundary/benchmark work to a
  generalization-first typed-event posture.
