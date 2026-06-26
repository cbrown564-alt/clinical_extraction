# Gan 2026 Trigger-Context Release Promotion Analysis

Validation-development trigger-context release promotion analysis. It uses validation accounting and component-matrix fields only; it does not inspect locked-test rows, change scorer policy, change gold labels, or create a benchmark-comparable claim.

## Decision

Decision: `reject`.

| Metric | Value |
| --- | ---: |
| release rows | 1 |
| analyzed rows | 1 |
| W->C rows | 0 |
| C->W rows | 0 |
| category-correct not exact-label rows | 1 |
| issues | `promotion_gate_expected_all_releases_w_to_c_and_zero_c_to_w` |

## Rows

| Row | Label | Matrix action | Transition | Caveat | Issues |
| ---: | --- | --- | --- | --- | --- |
| 5977 | `multiple per 6 week` | `abstain` | `C_to_C` | `category_correct_not_exact_label` | `none` |

## Artifact

- Summary JSON: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_trigger_release_promotion_2026-06-04.json`
