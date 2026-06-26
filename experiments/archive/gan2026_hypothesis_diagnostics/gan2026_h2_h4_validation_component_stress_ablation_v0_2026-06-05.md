# Gan 2026 H2/H4 Validation Component-Stress Ablation v0

Validation-development no-call component-stress ablation over the H2/H4 panel. It reuses saved validation panel labels and component metadata only; locked-test row-level failures remain uninspected.

## Decision

diagnostic_ablation_passed_h6_controls_but_nonprediction_pressure_remains

## Conditions

| Condition | Rows | Scorable | Correct | Nonprediction | Exact evidence | Valid source ids |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `deterministic_comparator` | 106 | 106 | 53 | 0 | 75 | 75 |
| `staged_final_policy` | 106 | 75 | 37 | 31 | 75 | 75 |
| `staged_prediction_bearing_only` | 75 | 75 | 37 | 0 | 75 | 75 |

## Comparisons

| Candidate | Overlap | Changed | W->C | C->W | C->nonprediction | W->nonprediction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `staged_final_policy` | 106 | 31 | 0 | 0 | 16 | 15 |
| `staged_prediction_bearing_only` | 75 | 0 | 0 | 0 | 0 | 0 |

## H6 Control Arm

| Controls | Preserved | Regressed | Nonprediction regressions |
| ---: | ---: | ---: | ---: |
| 37 | 37 | 0 | 0 |

## Staged Final Policy By Stratum

| Role | Owner | Family | Rows | Correct | Nonprediction | W->C | C->W | C->nonprediction |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `control` | `deterministic_adapter` | `competing_semiologies` | 1 | 1 | 0 | 0 | 0 | 0 |
| `control` | `deterministic_adapter` | `none` | 29 | 29 | 0 | 0 | 0 | 0 |
| `control` | `safety_floor` | `none` | 7 | 7 | 0 | 0 | 0 | 0 |
| `hard` | `deterministic_adapter` | `benchmark_format_convention` | 7 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `deterministic_adapter` | `cluster_burden` | 5 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `deterministic_adapter` | `competing_semiologies` | 12 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `deterministic_adapter` | `current_vs_historical` | 3 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `deterministic_adapter` | `rate_bucket_or_denominator` | 1 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `deterministic_adapter` | `seizure_free_duration` | 1 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `deterministic_adapter` | `unclassified` | 1 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `benchmark_format_convention` | 3 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `cluster_burden` | 1 | 0 | 0 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `competing_semiologies` | 9 | 0 | 7 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `current_vs_historical` | 2 | 0 | 1 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `none` | 16 | 0 | 16 | 0 | 0 | 16 |
| `hard` | `safety_floor` | `rate_bucket_or_denominator` | 2 | 0 | 2 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `seizure_free_duration` | 4 | 0 | 3 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `uncertainty_or_ambiguity` | 1 | 0 | 1 | 0 | 0 | 0 |
| `hard` | `safety_floor` | `unclassified` | 1 | 0 | 1 | 0 | 0 | 0 |

## Next Step

Investigate action-policy nonpredictions before promoting a new architecture: the staged policy avoids C->W label regressions but routes deterministic-correct hard rows to nonprediction. Candidate changes must recover those rows without damaging H6 controls.

## Artifacts

- Ablation JSONL: `experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.json`
- Source panel: `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl`
