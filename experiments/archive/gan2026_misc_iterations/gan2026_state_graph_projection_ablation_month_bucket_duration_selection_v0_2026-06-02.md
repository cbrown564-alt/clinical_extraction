# Gan 2026 Month-Bucket Duration Selection Projection Ablation v0

Diagnostic only: this is validation-cycle projection replay over saved state-graph artifacts, not a benchmark result, scorer-normalization change, or production projection-policy promotion.

- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 250
- JSONL artifact: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.json`

## Surface Mix

| Surface | Rows | Changed labels | Changed-label rate |
| --- | ---: | ---: | ---: |
| `regression_validation_hard_slice` | 232 | 37 | 0.1595 |
| `target_duration_enriched` | 18 | 18 | 1.0000 |

## Target Duration Surface

- Exact duration corrections: 18
- Exact duration regressions: 0
- Selected-node evidence valid: 18/18

## Regression Panel

- Already-correct regressions: 27
- Non-duration seizure-free regressions: 0
- Unknown/no-reference/boundary changes: 2
- Frequency-with-seizure-free-node changes: 19
- Selected-node evidence valid: 232/232

## Regression Tags

| Tag | Rows | Changed labels |
| --- | ---: | ---: |
| `already_projection_correct` | 181 | 27 |
| `frequency_with_seizure_free_node` | 19 | 19 |
| `numeric_seizure_free_duration` | 19 | 16 |
| `unknown_no_reference_boundary` | 45 | 2 |

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
| 466 | `regression_validation_hard_slice` | 21 to 28 per month | 21 to 28 per month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 891 | `regression_validation_hard_slice` | 1 per 2 day | 1 per 2 day | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 899 | `regression_validation_hard_slice` | 1 per 2 week | 1 per 2 week | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 1171 | `regression_validation_hard_slice` | 7 to 9 per 3 week | 7 to 9 per 3 week | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 1591 | `regression_validation_hard_slice` | 11 per month | 11 per month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 2366 | `regression_validation_hard_slice` | 2 to 4 per year | 2 to 4 per year | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 2541 | `regression_validation_hard_slice` | 8 to 9 per 2 week | 8 to 9 per 2 week | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 2681 | `regression_validation_hard_slice` | 1 per day | 1 per day | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 2731 | `regression_validation_hard_slice` | 1 per 2 week | 1 per 2 week | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 2740 | `regression_validation_hard_slice` | 1 per month | 1 per month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 2907 | `regression_validation_hard_slice` | seizure free for 6 month | seizure free for multiple year | seizure free for 6 months | numeric_seizure_free_duration |
| 2932 | `regression_validation_hard_slice` | seizure free for 9 month | seizure free for multiple year | seizure free for 9 months | numeric_seizure_free_duration |
| 2938 | `regression_validation_hard_slice` | seizure free for 8 month | seizure free for multiple year | seizure free for 8 months | numeric_seizure_free_duration |
| 2965 | `regression_validation_hard_slice` | seizure free for 16 month | 4 to 5 per week | seizure free for 16 months | numeric_seizure_free_duration |
| 2992 | `regression_validation_hard_slice` | seizure free for 7 month | seizure free for 7 month | seizure free for 7 months | already_projection_correct, numeric_seizure_free_duration |
| 3015 | `regression_validation_hard_slice` | seizure free for 12 month | seizure free for 12 month | seizure free for 12 months | already_projection_correct, numeric_seizure_free_duration |
| 3048 | `regression_validation_hard_slice` | seizure free for 16 month | seizure free for 16 month | seizure free for 16 months | already_projection_correct, numeric_seizure_free_duration |
| 3058 | `regression_validation_hard_slice` | seizure free for 12 month | seizure free for 12 month | seizure free for 12 months | already_projection_correct, numeric_seizure_free_duration |
| 3082 | `regression_validation_hard_slice` | seizure free for 10 month | 6 to 7 per 3 month | seizure free for 10 months | numeric_seizure_free_duration |
| 3095 | `regression_validation_hard_slice` | seizure free for 12 month | seizure free for 12 month | seizure free for 12 months | already_projection_correct, numeric_seizure_free_duration |
| 3113 | `regression_validation_hard_slice` | seizure free for 14 month | seizure free for 14 month | seizure free for 14 months | already_projection_correct, numeric_seizure_free_duration |
| 3281 | `regression_validation_hard_slice` | 8 per month | 1 per day | seizure free for multiple year | frequency_with_seizure_free_node |
| 3371 | `regression_validation_hard_slice` | unknown | 1 per month | seizure free for multiple year | unknown_no_reference_boundary |
| 3469 | `regression_validation_hard_slice` | unknown | seizure free for multiple year | seizure free for 6 months | unknown_no_reference_boundary |
| 3791 | `regression_validation_hard_slice` | 10 per year | 10 per year | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 3801 | `regression_validation_hard_slice` | 9 per month | 9 per month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 4022 | `regression_validation_hard_slice` | 8 per month | 8 per month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 4337 | `regression_validation_hard_slice` | 3 per 3 month | 3 per 3 month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 4345 | `regression_validation_hard_slice` | 4 per month | 4 per month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 4368 | `regression_validation_hard_slice` | 5 per 2 month | 5 per 2 month | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 4562 | `regression_validation_hard_slice` | 1 per 6 week | 1 per 6 week | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 4597 | `regression_validation_hard_slice` | 1 per 3 week | 1 per 3 week | seizure free for multiple year | already_projection_correct, frequency_with_seizure_free_node |
| 4956 | `regression_validation_hard_slice` | seizure free for 7 month | seizure free for 7 month | seizure free for 7 months | already_projection_correct, numeric_seizure_free_duration |
| 4992 | `regression_validation_hard_slice` | seizure free for 11 month | 1 per 8 day | seizure free for 11 months | numeric_seizure_free_duration |
| 4994 | `regression_validation_hard_slice` | seizure free for 6 month | seizure free for 6 month | seizure free for 6 months | already_projection_correct, numeric_seizure_free_duration |
| 5331 | `regression_validation_hard_slice` | seizure free for 12 month | seizure free for 12 month | seizure free for 12 months | already_projection_correct, numeric_seizure_free_duration |
| 5351 | `regression_validation_hard_slice` | seizure free for 18 month | 1 per day | seizure free for 18 months | numeric_seizure_free_duration |
