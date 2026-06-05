# Project Status

Last updated: 2026-06-05

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

The active path is the validation-test generalisation gap program. Use saved
artifacts as research instruments for component questions, not as whole-pipeline
F1 trophies. The fully assembled
`hybrid_multi_component_staged_assembly_v1` saved-replay validation pipeline is
materialized, and its frozen holdout protocol addendum is written. The next
decision is whether the validation freeze gate is clean enough to request
explicit aggregate-only test450 authorization for one primary model variant or
a predeclared symmetric model-swap comparison.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning; any holdout-facing use needs a
  frozen protocol and explicit user authorization.
- `rules_only_v1` remains the frozen transparent comparator; the current
  validation control is `untagged_nonprediction_release_candidate_v0_assembled_candidate`.
- `h5_repair_policy_v1_manifest` is the bounded repair contract; do not mix
  repair-policy changes with boundary/renderer or action-policy changes.
- `structured_projection_port_promoted_v0`, trigger-context release, last-event
  automatic release, few-shot train-exemplar, direct-labeler targeted switch,
  and broad action-policy widening are rejected or revise-only.
- Final F1 is secondary to candidate recall, exact evidence, projection
  consistency, metadata completeness, ambiguity preservation, and regression
  accounting.

## Current Evidence

- Conservative staged assembly on validation750: 735 prediction-bearing rows,
  697 correct prediction rows, 37/37 H6 controls preserved, and 0 release-wrong
  rows after untagged nonprediction releases.
- 2026-06-05: User authorized an aggregate-only test450 audit under
  `docs/research/gan2026_hybrid_multi_component_staged_assembly_v1_frozen_holdout_protocol_2026-06-05.md`
  after validation freeze-gate review. Authorization applies to the saved-replay
  frozen protocol only; no row-level test failure review, live model variant
  winner selection, or benchmark-comparable claim is authorized.
- `selective_safety_floor_gate_v0`: validation750 21 changes with 11 W->C and
  0 C->W; frozen local test450 14 changes with 8 W->C and 0 C->W.
- H5 policy v1 is frozen as bounded repair; renderer effects stay separate from
  clinical selection.
- `structured_projection_port_promoted_v0` was rejected on frozen aggregate-only
  test450: base 342/450 Purist proxy 0.7600 fell to 337/450 proxy 0.7489, with
  7 W->C, 12 C->W, and changed-label precision 0.3684.
- Boundary/renderer typed-event is promoted only as a bounded rare-family
  component: validation typed panel after selector revision had 6 W->C, 0 C->W,
  0 H6 regressions, and 0 source-note-text rows.
- Stage 4 H6/H9 sidecars are complete: 735/750 prediction-bearing rows, 9
  abstain, 6 review, 19 deterministic-comparator fallback releases, 0
  release-lane C->W, and 0 H6 regressions.
- `hybrid_multi_component_staged_assembly_v1` validation750 saved replay emits
  750/750 unique rows, 735 prediction-bearing rows, 15 abstain/review rows, 28
  selected boundary/renderer overlays, 2 suppressed overlays, 0 H6 regressions,
  and no final-row, sidecar, or component-matrix contract issues.

## Core Artifacts

- Assembly/holdout docs: final findings, frozen base protocol, protocol review,
  GPT-4.1 mini variant, Qwen 3.6:35b/Ollama variant, and staged gap plan live
  under `docs/research/gan2026_*_2026-06-05.md`.
- Current v1 assembly artifacts: validation750 summary JSON, row JSONL, and
  component matrix CSV under
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v1_*_2026-06-05.*`.
- Control/policy artifacts: untagged nonprediction release control, H5 repair
  manifest, H10 raw identity sidecar, boundary/renderer ADR 0011, and H9/H6
  sidecars in `experiments/gan2026_*_2026-06-05.*`.

## Work Board

### Now

- Review the validation freeze gate from the v1 saved-replay artifacts before
  requesting any test450 authorization.
- Choose either one primary authorized model variant or a symmetric model-swap
  comparison; do not use locked test as a winner-selection surface.
- Keep `structured_projection_port_promoted_v0` and broad action-policy widening
  rejected/revise-only.

### Next

- Request explicit user authorization only after the validation freeze gate and
  model-variant policy are reviewed.
- If authorized, run the test450 audit once under the frozen protocol and report
  only aggregate/predeclared-slice readouts.

### Blocked

- Whole-pipeline promotion remains blocked until a holdout-facing frozen
  protocol is authorized.
- Stage 5 downstream provenance expansion is deferred unless live/replay drift
  becomes relevant.
- Locked-test row-level inspection remains prohibited for development.

### Done Recently

- 2026-06-05: Wrote and reviewed the frozen holdout protocol addendum for
  `hybrid_multi_component_staged_assembly_v1`; added GPT-4.1 mini and Qwen
  3.6:35b/Ollama variants. The review records that current v1 assembly code is
  saved-replay validation-only and that multiple model variants must not become
  locked-test winner selection.
- 2026-06-05: Implemented and materialized v1 saved-replay validation assembly:
  750/750 unique validation rows, 0 H6 regressions, eligible boundary/renderer
  attribution, suppressed rows unpromoted, and clean final-row, sidecar, and
  component-matrix contracts.
- 2026-06-05: Completed Stage 4 action-policy sidecars and promoted the
  boundary/renderer typed-event layer as a bounded rare-family component; no
  whole-pipeline promotion, holdout use, or benchmark-comparable language is
  authorized.
