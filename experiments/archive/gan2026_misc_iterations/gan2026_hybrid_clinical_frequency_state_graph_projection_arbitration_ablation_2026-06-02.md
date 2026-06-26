# Gan 2026 State-Graph Projection/Arbitration Ablation

Diagnostic only: this is validation-cycle replay over saved graph artifacts, not a benchmark result and not a projection-policy promotion.

- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 42
- JSONL artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.json`

## Row Sources

| Source | Rows |
| --- | ---: |
| accepted_boundary_node_replay_projection_miss | 4 |
| validation_hard_slice_representable_projection_miss | 38 |

## Projection Variants

| Variant | Exact matches | Purist F1 | Pragmatic F1 | Corrections vs baseline | Regressions vs baseline |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline_v0` | 0/42 | 0.5714 | 0.6190 | 0 | 0 |
| `competing_frequency_uncertainty` | 1/42 | 0.5000 | 0.5000 | 1 | 0 |
| `boundary_state_priority` | 17/42 | 0.8571 | 0.8810 | 17 | 0 |
| `seizure_free_priority` | 8/42 | 0.6667 | 0.6905 | 8 | 0 |
| `lowest_current_frequency` | 3/42 | 0.6667 | 0.6905 | 3 | 0 |
| `oracle_gold_node` | 23/42 | 1.0000 | 1.0000 | 23 | 0 |

## Failure Families

| Family | Rows | Baseline exact | Best non-oracle variant | Best exact | Oracle exact |
| --- | ---: | ---: | --- | ---: | ---: |
| frequency_arbitration | 5 | 0 | `lowest_current_frequency` | 3 | 5 |
| seizure_free_arbitration | 25 | 0 | `seizure_free_priority` | 6 | 7 |
| unknown_arbitration | 6 | 0 | `boundary_state_priority` | 5 | 5 |
| unresolved_multiple_arbitration | 6 | 0 | `boundary_state_priority` | 6 | 6 |

## Remaining Baseline Misses

| Source row | Source | Gold | Baseline | Best non-oracle labels | Oracle |
| ---: | --- | --- | --- | --- | --- |
| 338 | accepted_boundary_node_replay_projection_miss | multiple per month | no seizure frequency reference | boundary_state_priority: multiple per month, seizure_free_priority: multiple per month | multiple per month |
| 1317 | accepted_boundary_node_replay_projection_miss | unknown, multiple per cluster | unknown |  | unknown |
| 3528 | accepted_boundary_node_replay_projection_miss | unknown | seizure free for multiple year | boundary_state_priority: unknown | unknown |
| 4694 | accepted_boundary_node_replay_projection_miss | multiple per day | no seizure frequency reference | boundary_state_priority: multiple per day, seizure_free_priority: multiple per day | multiple per day |
| 278 | validation_hard_slice_representable_projection_miss | multiple per week | seizure free for multiple year | boundary_state_priority: multiple per week | multiple per week |
| 744 | validation_hard_slice_representable_projection_miss | multiple per week | 1 per 8 week | boundary_state_priority: multiple per week | multiple per week |
| 1687 | validation_hard_slice_representable_projection_miss | multiple per week | 1 per 2 week | boundary_state_priority: multiple per week | multiple per week |
| 2907 | validation_hard_slice_representable_projection_miss | seizure free for 6 month | seizure free for multiple year | boundary_state_priority: seizure free for 6 month, seizure_free_priority: seizure free for 6 month | seizure free for 6 month |
| 2932 | validation_hard_slice_representable_projection_miss | seizure free for 9 month | seizure free for multiple year | boundary_state_priority: seizure free for 9 month, seizure_free_priority: seizure free for 9 month | seizure free for 9 month |
| 2938 | validation_hard_slice_representable_projection_miss | seizure free for 8 month | seizure free for multiple year | boundary_state_priority: seizure free for 8 month, seizure_free_priority: seizure free for 8 month | seizure free for 8 month |
| 2965 | validation_hard_slice_representable_projection_miss | seizure free for 16 month | 4 to 5 per week | boundary_state_priority: unknown, seizure_free_priority: seizure free for multiple year | seizure free for 16 month |
| 3082 | validation_hard_slice_representable_projection_miss | seizure free for 10 month | 6 to 7 per 3 month | boundary_state_priority: seizure free for 10 month, seizure_free_priority: seizure free for 10 month | seizure free for 10 month |
| 3118 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 3137 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 3281 | validation_hard_slice_representable_projection_miss | 8 per month | 1 per day | lowest_current_frequency: 8 per month | 8 per month |
| 3371 | validation_hard_slice_representable_projection_miss | unknown | 1 per month | boundary_state_priority: unknown | unknown |
| 3469 | validation_hard_slice_representable_projection_miss | unknown | seizure free for multiple year | competing_frequency_uncertainty: unknown, boundary_state_priority: unknown | unknown |
| 3482 | validation_hard_slice_representable_projection_miss | unknown | 1 per 12 week | boundary_state_priority: unknown | unknown |
| 3534 | validation_hard_slice_representable_projection_miss | unknown | 1 per year | boundary_state_priority: unknown | unknown |
| 3995 | validation_hard_slice_representable_projection_miss | 1 per month | 3 per day | lowest_current_frequency: 1 per month | 1 per month |
| 4026 | validation_hard_slice_representable_projection_miss | 1 per month | 6 to 7 per month | competing_frequency_uncertainty: unknown, lowest_current_frequency: 1 per 8 week | 1 per month |
| 4116 | validation_hard_slice_representable_projection_miss | 1 per 1 to 2 day | 1 per day | competing_frequency_uncertainty: unknown, lowest_current_frequency: 3 per 10 day | 1 per 1 to 2 day |
| 4592 | validation_hard_slice_representable_projection_miss | 1 per 2 month | 1 per week | lowest_current_frequency: 1 per 2 month | 1 per 2 month |
| 4839 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for 4 month | competing_frequency_uncertainty: unknown, boundary_state_priority: seizure free for multiple year, seizure_free_priority: seizure free for multiple year | seizure free for multiple year |
| 4842 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 4951 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 4992 | validation_hard_slice_representable_projection_miss | seizure free for 11 month | 1 per 8 day | boundary_state_priority: seizure free for 11 month, seizure_free_priority: seizure free for 11 month | seizure free for 11 month |
| 5040 | validation_hard_slice_representable_projection_miss | seizure free for 6 months | seizure free for multiple year |  | seizure free for multiple year |
| 5082 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5092 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5110 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5121 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5136 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5141 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5197 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5210 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5221 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5345 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5351 | validation_hard_slice_representable_projection_miss | seizure free for 18 month | 1 per day | boundary_state_priority: seizure free for 18 month, seizure_free_priority: seizure free for 18 month | seizure free for 18 month |
| 5379 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for 6 month |  | seizure free for 6 month |
| 5406 | validation_hard_slice_representable_projection_miss | seizure free for multiple month | seizure free for multiple year |  | seizure free for multiple year |
| 5567 | validation_hard_slice_representable_projection_miss | multiple per week | 2 per 6 month | boundary_state_priority: multiple per week | multiple per week |
