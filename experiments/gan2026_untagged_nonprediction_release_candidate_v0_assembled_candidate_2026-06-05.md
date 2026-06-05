# Gan 2026 Untagged Nonprediction Assembled Candidate v0

Auditable validation-development assembled candidate for untagged_nonprediction_release_candidate_v0. It records row-level release eligibility, original staged action, deterministic fallback label, candidate action, component ownership, and H6 membership. It does not authorize holdout use or benchmark-comparable claims.

## Decision

candidate_patch_passes_validation_no_regression_gate

## Aggregate Accounting

| Metric | Value |
| --- | ---: |
| rows | 750 |
| original nonpredictions | 34 |
| release-eligible rows | 19 |
| release-applied rows | 19 |
| candidate prediction-bearing rows | 735 |
| candidate correct prediction rows | 697 |
| release correct rows | 19 |
| release wrong rows | 0 |
| H6 member rows | 37 |
| H6 controls | 37 |
| H6 regressions | 0 |
| locked-test row-level artifacts used | 0 |

## Component Ownership

| Component owner | Rows |
| --- | ---: |
| `deterministic_adapter` | 701 |
| `deterministic_comparator_fallback` | 19 |
| `safety_floor` | 30 |

## Release Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_abstain` | 17 |
| `C_to_review` | 2 |

## Next Step

Use this artifact as the family-indexed assembly record before any separate frozen holdout protocol; do not run or tune on locked-test row-level failures from this artifact.

## Artifacts

- Assembled candidate JSONL: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.json`
- Component matrix: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`
- H2/H4 panel: `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl`
