# Gan 2026 Month-Bucket Duration Selection Projection Ablation graph_gated_v2

Diagnostic only: this is validation-cycle projection replay over saved state-graph artifacts, not a benchmark result, scorer-normalization change, or production projection-policy promotion.

- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 250
- JSONL artifact: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.json`

## Surface Mix

| Surface | Rows | Changed labels | Changed-label rate |
| --- | ---: | ---: | ---: |
| `regression_validation_hard_slice` | 232 | 0 | 0.0000 |
| `target_duration_enriched` | 18 | 18 | 1.0000 |

## Target Duration Surface

- Exact duration corrections: 18
- Exact duration regressions: 0
- Selected-node evidence valid: 18/18

## Regression Panel

- Already-correct regressions: 0
- Non-duration seizure-free regressions: 0
- Unknown/no-reference/boundary changes: 0
- Frequency-with-seizure-free-node changes: 0
- Selected-node evidence valid: 232/232

## Regression Family Tags

| Family | Rows | Changed labels |
| --- | ---: | ---: |
| `candidate_absent_or_weak` | 4 | 0 |
| `cluster_or_diary` | 207 | 0 |
| `deterministic_miss` | 4 | 0 |
| `seizure_free_overreach` | 53 | 0 |
| `shorthand_interval_range` | 51 | 0 |
| `temporal_conflict` | 196 | 0 |
| `unknown_no_reference_boundary` | 72 | 0 |

## Graph Metadata Gate

- Blocked month-bucket replacements: 46

| Graph flag | Rows |
| --- | ---: |
| `active_boundary_state_node` | 6 |
| `selected_rule_not_duration_normalization_v0` | 46 |

## Regression Tags

| Tag | Rows | Changed labels |
| --- | ---: | ---: |
| `already_projection_correct` | 181 | 0 |
| `candidate_absent_or_weak` | 4 | 0 |
| `cluster_or_diary` | 207 | 0 |
| `deterministic_miss` | 4 | 0 |
| `frequency_with_seizure_free_node` | 19 | 0 |
| `numeric_seizure_free_duration` | 19 | 0 |
| `seizure_free_overreach` | 53 | 0 |
| `shorthand_interval_range` | 51 | 0 |
| `temporal_conflict` | 196 | 0 |
| `unknown_no_reference_boundary` | 72 | 0 |

## Changed Rows

| Source row | Surface | Gold | Baseline | Month-bucket | Tags |
| ---: | --- | --- | --- | --- | --- |
| 3118 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 3137 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 4839 | `target_duration_enriched` | seizure free for multiple month | seizure free for 4 month | seizure free for multiple month |  |
| 4842 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 4951 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5040 | `target_duration_enriched` | seizure free for 6 months | seizure free for multiple year | seizure free for 6 months | numeric_seizure_free_duration |
| 5082 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5092 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5110 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5121 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5136 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5141 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5197 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5210 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5221 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5345 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
| 5379 | `target_duration_enriched` | seizure free for multiple month | seizure free for 6 month | seizure free for multiple month |  |
| 5406 | `target_duration_enriched` | seizure free for multiple month | seizure free for multiple year | seizure free for multiple month |  |
