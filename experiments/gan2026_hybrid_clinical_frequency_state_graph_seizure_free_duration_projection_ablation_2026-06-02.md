# Gan 2026 State-Graph Seizure-Free Duration Projection Ablation

Diagnostic only: this is validation-cycle replay over saved graph artifacts, not a benchmark result and not a projection-policy promotion.

All seizure-free labels have monthly frequency `0.0` under the Gan scorer, so this report focuses on exact duration-label behavior rather than Purist or Pragmatic F1.

- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 25
- JSONL artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.json`

## Row Sources

| Source | Rows |
| --- | ---: |
| validation_hard_slice_representable_projection_miss | 25 |

## Projection Variants

| Variant | Exact duration matches | Corrections vs baseline | Regressions vs baseline | Selected seizure-free rows |
| --- | ---: | ---: | ---: | ---: |
| `baseline_v0` | 0/25 | 0 | 0 | 21 |
| `seizure_free_priority` | 6/25 | 6 | 0 | 25 |
| `longest_seizure_free_duration` | 3/25 | 3 | 0 | 25 |
| `shortest_seizure_free_duration` | 7/25 | 7 | 0 | 25 |
| `numeric_duration_priority` | 7/25 | 7 | 0 | 25 |
| `oracle_exact_seizure_free_node` | 7/25 | 7 | 0 | 25 |

## Failure Modes

| Mode | Rows |
| --- | ---: |
| exact_seizure_free_node_not_selected | 3 |
| non_seizure_free_selected | 4 |
| numeric_duration_present_but_gold_absent | 2 |
| only_broad_duration_nodes | 16 |

## Scorer-Equivalent Duration Labels

| Source row | Gold | Baseline | Exact node present | Best non-oracle labels |
| ---: | --- | --- | --- | --- |
| 2907 | seizure free for 6 month | seizure free for multiple year | True | seizure_free_priority: seizure free for 6 month, shortest_seizure_free_duration: seizure free for 6 month, numeric_duration_priority: seizure free for 6 month |
| 2932 | seizure free for 9 month | seizure free for multiple year | True | seizure_free_priority: seizure free for 9 month, shortest_seizure_free_duration: seizure free for 9 month, numeric_duration_priority: seizure free for 9 month |
| 2938 | seizure free for 8 month | seizure free for multiple year | True | seizure_free_priority: seizure free for 8 month, shortest_seizure_free_duration: seizure free for 8 month, numeric_duration_priority: seizure free for 8 month |
| 2965 | seizure free for 16 month | 4 to 5 per week | True | shortest_seizure_free_duration: seizure free for 16 month, numeric_duration_priority: seizure free for 16 month |
| 3082 | seizure free for 10 month | 6 to 7 per 3 month | True | seizure_free_priority: seizure free for 10 month, longest_seizure_free_duration: seizure free for 10 month, shortest_seizure_free_duration: seizure free for 10 month, numeric_duration_priority: seizure free for 10 month |
| 3118 | seizure free for multiple month | seizure free for multiple year | False |  |
| 3137 | seizure free for multiple month | seizure free for multiple year | False |  |
| 4839 | seizure free for multiple month | seizure free for 4 month | False | seizure_free_priority: seizure free for multiple year, longest_seizure_free_duration: seizure free for multiple year |
| 4842 | seizure free for multiple month | seizure free for multiple year | False |  |
| 4951 | seizure free for multiple month | seizure free for multiple year | False |  |
| 4992 | seizure free for 11 month | 1 per 8 day | True | seizure_free_priority: seizure free for 11 month, longest_seizure_free_duration: seizure free for 11 month, shortest_seizure_free_duration: seizure free for 11 month, numeric_duration_priority: seizure free for 11 month |
| 5040 | seizure free for 6 months | seizure free for multiple year | False |  |
| 5082 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5092 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5110 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5121 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5136 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5141 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5197 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5210 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5221 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5345 | seizure free for multiple month | seizure free for multiple year | False |  |
| 5351 | seizure free for 18 month | 1 per day | True | seizure_free_priority: seizure free for 18 month, longest_seizure_free_duration: seizure free for 18 month, shortest_seizure_free_duration: seizure free for 18 month, numeric_duration_priority: seizure free for 18 month |
| 5379 | seizure free for multiple month | seizure free for 6 month | False |  |
| 5406 | seizure free for multiple month | seizure free for multiple year | False |  |
