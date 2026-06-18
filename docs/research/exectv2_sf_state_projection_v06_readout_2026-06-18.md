# ExECTv2 SeizureFrequency State Projection v0.6 Readout

Date: 2026-06-18
Scope: deterministic replay over SF state adjudicator v0.5 dev140 output.
Status: partial gain; does not clear the `0.8` gate.

## Why this run exists

The residual convention decomposition estimated an oracle path from SF v0.5
`0.721` to `0.805` if state and generic-vs-named ownership conventions could be
resolved perfectly. v0.6 tests the legitimate version of that idea: finite
deterministic projection over saved v0.5 predictions and candidate spans, with
no model calls and no gold labels available to projection rules.

Rules are classified as `seizure_frequency` deterministic rules because they
change prediction-bearing state or seizure-type ownership. They are not hidden
normalization.

## Ablation Results

| Ablation | F1 | P | R | TP | FP | FN | Read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| none / v0.5 replay | 0.721 | 0.710 | 0.733 | 137 | 56 | 50 | baseline reproduced |
| ownership only | 0.721 | 0.710 | 0.733 | 137 | 56 | 50 | no measurable movement |
| state only | 0.763 | 0.722 | 0.807 | 151 | 58 | 36 | useful partial gain |
| combined | 0.763 | 0.722 | 0.807 | 151 | 58 | 36 | same as state-only |

State slices for the promoted v0.6 combined replay:

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.800 | 0.791 | 0.809 | 72 | 19 | 17 |
| seizure-free | 0.794 | 0.761 | 0.831 | 54 | 17 | 11 |
| unknown | 0.625 | 0.532 | 0.758 | 25 | 22 | 8 |

Rule action counts for the combined replay:

| Rule | Count |
| --- | ---: |
| `state.change_recovery` | 17 |
| `state.drop_historical_active_rate` | 1 |
| `state.drop_historical_or_advice_seizure_free` | 2 |
| `state.drop_preceded_by_current_seizure_free` | 1 |
| `state.drop_unlabelled_active_rate` | 6 |
| `state.last_event_active_to_seizure_free` | 1 |
| `state.seizure_free_last_event_date` | 4 |
| `state.seizure_free_last_event_duration` | 1 |
| `state.seizure_free_point_anchor` | 4 |

## Interpretation

v0.6 validates part of the convention-decomposition thesis: explicit state
projection can recover real headroom, moving SF from `0.721` to `0.763` with
only a small FP increase. The active-rate and seizure-free slices are now near
the `0.8` boundary.

It also falsifies the optimistic operational read of the oracle. The oracle
ceiling `0.805` assumes perfect state/ownership decisions. The finite rules that
can be predeclared without gold leakage recover only part of that ceiling, and
the unknown slice remains weak (`0.625`, precision `0.532`). Ownership-only
projection contributes no measurable gain on this artifact.

The result should be reported as:

> Deterministic SF state projection over adjudicator candidates improves dev140
> clinical-recovery F1 from `0.721` to `0.763`, but does not clear the `0.8`
> target. The convention oracle remains an upper bound, not an achieved or
> safely reachable score.

Not supported:

> SeizureFrequency clears `0.8` after deterministic convention projection.

## Hard-Slice Diagnostic

The follow-up hard-slice diagnostic isolates the remaining v0.6 residual rather
than proposing another broad rule pass:
`experiments/exectv2_sf_v06_hard_slice_diagnostic_dev140_20260618.md`.

| State | FN | FP |
| --- | ---: | ---: |
| active-rate | 17 | 19 |
| seizure-free | 11 | 17 |
| unknown | 8 | 22 |

The remaining SF blocker is now the unknown-state precision slice. v0.6 recovers
many unknown misses, leaving only 8 unknown FNs, but it still over-emits 22
unknown states. The largest unknown buckets are state swaps against active-rate
gold, generic/named ownership gaps, and grounded scope over-emissions. This
argues against another broad unknown/change recovery rule: a further loop would
need a predeclared high-precision suppression test for unknown over-emission,
with a stop rule if active-rate or seizure-free recall regresses.

## Four-Family Readout With v0.6 SF

The combined key-family ledger now uses Prescription verifier v0.1,
Investigations verifier v0.1, Diagnosis reconciler v0.1, and SF v0.6 combined
projection.

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.817 | 0.773 | 0.865 | 167 | 49 | 26 |
| Diagnosis | 0.658 | 0.658 | 0.658 | 243 | 126 | 126 |
| SeizureFrequency | 0.763 | 0.723 | 0.807 | 151 | 58 | 36 |
| Investigations | 0.872 | 0.869 | 0.875 | 119 | 18 | 17 |

This remains a two-family clear plus two-family characterization result, not a
benchmark-complete key-entity architecture.

## Artifacts

- Implementation:
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/llm_sf_state_projection.py`
- Runner:
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/runners/run_sf_state_projection.py`
- Ablation reports:
  `experiments/exectv2_hybrid_sf_state_projection_v06_none_dev140_20260618.md`,
  `experiments/exectv2_hybrid_sf_state_projection_v06_state_dev140_20260618.md`,
  `experiments/exectv2_hybrid_sf_state_projection_v06_ownership_dev140_20260618.md`,
  `experiments/exectv2_hybrid_sf_state_projection_v06_combined_dev140_20260618.md`
- Combined key-family ledger:
  `experiments/exectv2_key_entities_clinical_error_ledger_v06sf_dev140_20260618.md`
