# Gan 2026 H3/H7/H8 Full Boundary/Benchmark Test v0

Development H3/H7/H8 readout over synthetic minimal pairs and all eligible validation boundary/benchmark rows. It tests candidate exposure, exact evidence, metadata completeness, transition safety, and pair consistency without using locked-test row-level artifacts.

## Decision

h3_rejected_current_layer_h7_supported_h8_partial

## Hypothesis Outcomes

| Hypothesis | Status |
| --- | --- |
| H3 candidate-generation recall | `tested_rejected_for_current_typed_layer` |
| H7 template brittleness | `tested_supported_for_deterministic_template_brittleness` |
| H8 benchmark-format convention | `tested_partial_validation_support_for_benchmark_convention_subset` |

## Summary

| Metric | Value |
| --- | ---: |
| synthetic rows | 36 |
| synthetic pairs | 18 |
| typed pair-consistent pairs | 18 |
| deterministic pair-consistent pairs | 14 |
| deterministic flip pairs | 4 |
| synthetic typed-correct rows | 36 |
| synthetic deterministic-correct rows | 21 |
| validation contract rows | 36 |
| validation candidate-present rows | 36 |
| validation exact-evidence rows | 36 |
| validation selected prediction-bearing rows | 36 |
| validation C->W rate | 0.0278 |
| H8 validation rows | 11 |
| H8 selected prediction-bearing rows | 11 |
| H8 clinical/rendering separated rows | 11 |

## Validation Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 29 |
| `C_to_W` | 1 |
| `W_to_C` | 6 |

## H8 Benchmark Convention Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 11 |

## H8 Benchmark Rules

| Rule | Rows |
| --- | ---: |
| `gan_cluster_multiple_per_cluster` | 3 |
| `gan_unknown_sentinel` | 1 |
| `gan_vague_multiple_frequency` | 7 |

## H3 Gate Failures

- `validation_candidate_exposure_below_150`
- `validation_w_to_c_below_60`

## H7 Gate Failures

- none

## H8 Gate Failures

- none

## Interpretation

H3 is rejected for the current shallow typed layer because all eligible validation rows have exact supported candidate exposure but the surface is too small and produces too few W->C transitions for promotion. H7 is supported on the synthetic pair panel: the typed mechanism is pair consistent while the deterministic comparator flips on superficial wording/order variants. H8 has partial validation-development support: benchmark-convention rows are explicitly separated into clinical state and Gan-rendered label fields with exact evidence, but the readout is not a locked-test transfer audit.

## Artifacts

- Rows JSONL: `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.json`
- Source current candidate JSONL: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.jsonl`
