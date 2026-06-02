# Gan 2026 State-Graph Seizure-Free Duration Enriched Projection Replay

Diagnostic only: this is validation-cycle replay over saved graph artifacts, not a benchmark result and not a projection-policy promotion.

All seizure-free labels have monthly frequency `0.0` under the Gan scorer, so this report focuses on exact duration-label behavior rather than Purist or Pragmatic F1.

- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 18
- Graph field: `replayed_graph`
- JSONL artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.json`

## Row Sources

| Source | Rows |
| --- | ---: |
| validation_hard_slices | 18 |

## Projection Variants

| Variant | Exact duration matches | Corrections vs baseline | Regressions vs baseline | Selected seizure-free rows |
| --- | ---: | ---: | ---: | ---: |
| `baseline_v0` | 0/18 | 0 | 0 | 18 |
| `seizure_free_priority` | 0/18 | 0 | 0 | 18 |
| `longest_seizure_free_duration` | 0/18 | 0 | 0 | 18 |
| `shortest_seizure_free_duration` | 14/18 | 14 | 0 | 18 |
| `numeric_duration_priority` | 0/18 | 0 | 0 | 18 |
| `month_bucket_duration_selection` | 18/18 | 18 | 0 | 18 |
| `oracle_exact_seizure_free_node` | 17/18 | 17 | 0 | 18 |

`month_bucket_duration_selection` is a diagnostic output-surface variant. It prefers broad month-bucket nodes over numeric-month or broad-year conflicts and preserves plural numeric-month labels; it does not change scorer normalization or production projection.

## Failure Modes

| Mode | Rows |
| --- | ---: |
| exact_seizure_free_node_not_selected | 17 |
| numeric_duration_present_but_gold_absent | 1 |

## Scorer-Equivalent Duration Labels

| Source row | Gold | Baseline | Exact node present | Best non-oracle labels |
| ---: | --- | --- | --- | --- |
| 3118 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 3137 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 4839 | seizure free for multiple month | seizure free for 4 month | True | month_bucket_duration_selection: seizure free for multiple month |
| 4842 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 4951 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5040 | seizure free for 6 months | seizure free for multiple year | False | month_bucket_duration_selection: seizure free for 6 months |
| 5082 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5092 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5110 | seizure free for multiple month | seizure free for multiple year | True | month_bucket_duration_selection: seizure free for multiple month |
| 5121 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5136 | seizure free for multiple month | seizure free for multiple year | True | month_bucket_duration_selection: seizure free for multiple month |
| 5141 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5197 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5210 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5221 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5345 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5379 | seizure free for multiple month | seizure free for 6 month | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
| 5406 | seizure free for multiple month | seizure free for multiple year | True | shortest_seizure_free_duration: seizure free for multiple month, month_bucket_duration_selection: seizure free for multiple month |
