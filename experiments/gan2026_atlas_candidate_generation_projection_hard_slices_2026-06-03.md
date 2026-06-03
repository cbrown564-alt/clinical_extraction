# Gan 2026 Atlas Candidate-Generation And Projection Hard-Slice Predeclaration

This is a validation-development predeclaration derived from the hidden-family and first-failure atlas. It fixes slice membership before any candidate-generation rescue or projection-arbitration change is run.

- Date: `2026-06-03`
- Split manifest: `gan2026_split_v1`
- Source atlas CSV: `experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv`
- Candidate context: `hybrid_parallel_state_candidate_reasoner deterministic safety floor`
- Claim language: Diagnostic validation-cycle hard-slice manifest, not a benchmark or holdout claim.

## Hypothesis

The remaining validation misses are dominated by two separable mechanisms: absent or weak candidate generation, and projection/arbitration over already representable clinical states. A useful next experiment should improve one named mechanism on fixed validation hard slices while keeping the deterministic safety-floor final policy.

## Slice Manifest

| Slice | Focus | Rows | Primary metric |
| --- | --- | ---: | --- |
| `candidate_generation_rescue` | candidate generation | 44 | Candidate-recall rescue rate before final-label promotion; final policy keeps the deterministic safety floor unless a rescue is predeclared and ablated. |
| `candidate_generation_unknown_seizure_free_boundary` | candidate generation | 26 | Boundary-state recall without converting uncertain seizure-free language into a prediction-bearing deterministic repair. |
| `projection_arbitration` | graph/final projection | 11 | Projection-variant correction precision, mechanical-correct to projected-wrong regressions, and selected-evidence/source trace validity. |
| `projection_unknown_seizure_free_arbitration` | graph/final projection | 6 | Unknown/seizure-free/current-vs-historical arbitration precision with no broad validation retuning. |

## Experiment Unit

- Minimal change: add only candidate-generation rescue or projection-arbitration variants, not a broad prompt/schema/scorer rewrite.
- Surface: fixed validation hard slices in this manifest; no train or locked-test inspection.
- Comparator: current `hybrid_parallel_state_candidate_reasoner` deterministic safety-floor replay.
- Required ablations: deterministic top, candidate-generation rescue sidecar, baseline graph projection, projection-arbitration variant, and final safety-floor policy.
- Required counts: slice-level Purist/Pragmatic, wrong-to-correct, correct-to-wrong, deterministic-correct regressions, evidence exactness, source-id validity, fallback rate, and changed-label precision.

## Stop Rule

Promote only if candidate-generation rescues or projection-arbitration changes are high precision on these fixed slices, preserve evidence/source traces, and introduce no deterministic-correct regressions under the safety-floor final policy.

## Slice Definitions

### candidate_generation_rescue

- Rows: 44
- Membership: Atlas row is Purist-wrong and first_failure_owner is candidate_generation.
- Component focus: candidate generation
- Primary metric: Candidate-recall rescue rate before final-label promotion; final policy keeps the deterministic safety floor unless a rescue is predeclared and ablated.

### candidate_generation_unknown_seizure_free_boundary

- Rows: 26
- Membership: Atlas row is Purist-wrong, first_failure_owner is candidate_generation, and hidden_families includes unknown_boundary or seizure_free_duration.
- Component focus: candidate generation
- Primary metric: Boundary-state recall without converting uncertain seizure-free language into a prediction-bearing deterministic repair.

### projection_arbitration

- Rows: 11
- Membership: Atlas row is Purist-wrong and first_failure_owner is projection or final_projection.
- Component focus: graph/final projection
- Primary metric: Projection-variant correction precision, mechanical-correct to projected-wrong regressions, and selected-evidence/source trace validity.

### projection_unknown_seizure_free_arbitration

- Rows: 6
- Membership: Atlas row is Purist-wrong, first_failure_owner is projection or final_projection, and hidden_families includes unknown_boundary, seizure_free_duration, or current_vs_historical.
- Component focus: graph/final projection
- Primary metric: Unknown/seizure-free/current-vs-historical arbitration precision with no broad validation retuning.
