# Gan 2026 H2/H4 Validation Component-Stress Panel v0

Validation-development H2/H4 component-stress design panel. It uses validation row-level gap-matrix rows only, uses H6 selective-action as a no-regression transfer-control context, and does not inspect locked-test row-level failures.

## Decision

ready_for_component_stress_ablation

## Summary

| Metric | Value |
| --- | ---: |
| rows | 106 |
| hard rows | 69 |
| control rows | 37 |
| hard exact-evidence rows | 38 |
| hard valid-source-id rows | 38 |
| hard nonprediction rows | 31 |
| locked-test row-level artifacts used | 0 |

## Component Owners

| Owner | Rows |
| --- | ---: |
| `deterministic_adapter` | 60 |
| `safety_floor` | 46 |

## Clinical Subproblems

| Subproblem | Rows |
| --- | ---: |
| `adapter_rendering` | 64 |
| `final_policy` | 42 |

## Hidden Families

| Family | Rows |
| --- | ---: |
| `none` | 52 |
| `competing_semiologies` | 22 |
| `benchmark_format_convention` | 10 |
| `cluster_burden` | 6 |
| `current_vs_historical` | 5 |
| `seizure_free_duration` | 5 |
| `rate_bucket_or_denominator` | 3 |
| `unclassified` | 2 |
| `uncertainty_or_ambiguity` | 1 |

## Control Match Quality

| Match quality | Rows |
| --- | ---: |
| `owner_subproblem_untagged` | 31 |
| `owner_only` | 5 |
| `owner_subproblem_family` | 1 |

## Next Step

Run component-stress ablations on this panel before designing another prediction-bearing architecture: preserve exact evidence/source-id rates, report W->C and C->W within owner/family strata, and treat deterministic-correct controls as the H6 no-regression arm.

## Artifacts

- Panel JSONL: `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.json`
- Source matrix: `experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl`
- Hypothesis selection: `experiments/gan2026_validation_test_gap_hypothesis_selection_v0_2026-06-05.json`
