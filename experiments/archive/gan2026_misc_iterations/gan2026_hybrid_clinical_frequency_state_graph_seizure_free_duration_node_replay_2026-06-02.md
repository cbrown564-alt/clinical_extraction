# Gan 2026 State-Graph Seizure-Free Duration Node Replay

Diagnostic only: this is validation-cycle graph-node construction replay, not a benchmark result, scorer change, or production projection-policy promotion.

- Source artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.jsonl`
- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 18
- JSONL artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.json`

## Node Coverage

- New duration nodes: 21
- Rows with new duration nodes: 18/18
- Baseline exact gold duration nodes: 0/18
- Replayed exact gold duration nodes: 17/18
- Month-scale representability: 18/18
- Month-scale representability gains: 16
- Rows still only over-broad year: 0

## Evidence Validity

- Exact-evidence-valid nodes: 21/21
- Rows with any evidence error: 0

## Unchanged Projection Replay

- Exact duration matches after replay with unchanged projection: 0/18
- Projection changed from baseline: 0

## Rule Families

| Rule | Nodes | Taxonomy |
| --- | ---: | --- |
| `seizure_free_duration_node_normalization_v0.dated_diary_interval` | 1 | general |
| `seizure_free_duration_node_normalization_v0.dated_month_boundary` | 1 | gan2026_specific |
| `seizure_free_duration_node_normalization_v0.dated_since_interval` | 1 | general |
| `seizure_free_duration_node_normalization_v0.month_vague_from_evidence` | 5 | seizure_frequency |
| `seizure_free_duration_node_normalization_v0.numeric_month_from_evidence` | 1 | general |
| `seizure_free_duration_node_normalization_v0.numeric_to_broad_month_projection_surface` | 4 | benchmark_format |
| `seizure_free_duration_node_normalization_v0.since_without_date_boundary` | 8 | gan2026_specific |

## Rows

| Source row | Gold | Failure mode | New nodes | Exact gold node | Month-scale gain | Baseline projection | Replayed projection |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 3118 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 3137 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 4839 | seizure free for multiple month | seizure_free_arbitration | 1 | True | False | seizure free for 4 month | seizure free for 4 month |
| 4842 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 4951 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5040 | seizure free for 6 months | seizure_free_arbitration | 1 | False | True | seizure free for multiple year | seizure free for multiple year |
| 5082 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5092 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5110 | seizure free for multiple month | seizure_free_arbitration | 2 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5121 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5136 | seizure free for multiple month | seizure_free_arbitration | 2 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5141 | seizure free for multiple month | seizure_free_arbitration | 2 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5197 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5210 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5221 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5345 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
| 5379 | seizure free for multiple month | seizure_free_arbitration | 1 | True | False | seizure free for 6 month | seizure free for 6 month |
| 5406 | seizure free for multiple month | seizure_free_arbitration | 1 | True | True | seizure free for multiple year | seizure free for multiple year |
