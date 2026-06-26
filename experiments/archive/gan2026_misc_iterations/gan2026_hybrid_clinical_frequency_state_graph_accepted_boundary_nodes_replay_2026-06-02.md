# Gan 2026 Accepted Boundary Nodes Graph Replay

This is diagnostic graph replay only, not a benchmark result.

- Source artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.jsonl`
- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 10
- JSONL artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.json`

## Coverage Replay

- Accepted boundary-builder rows: 10
- Accepted hosted nodes: 18
- Baseline representable rows: 0/10
- Replayed representable rows: 10/10
- Representability gains: 10

## Projection Replay

- Exact normalized label matches: 6/10
- Purist accuracy/F1: 0.9000 / 0.9000
- Pragmatic accuracy/F1: 0.9000 / 0.9000
- Projection changed after accepted-node merge: 7

## Rows

| Source row | Gold | Baseline representable | Replayed representable | Baseline projection | Replayed projection | Hosted nodes |
| ---: | --- | --- | --- | --- | --- | ---: |
| 338 | multiple per month | False | True | no seizure frequency reference | no seizure frequency reference | 1 |
| 1317 | unknown, multiple per cluster | False | True | no seizure frequency reference | unknown | 1 |
| 3507 | unknown | False | True | no seizure frequency reference | unknown | 1 |
| 3512 | unknown | False | True | no seizure frequency reference | unknown | 2 |
| 3528 | unknown | False | True | seizure free for multiple year | seizure free for multiple year | 2 |
| 3532 | unknown | False | True | no seizure frequency reference | unknown | 2 |
| 3600 | unknown | False | True | no seizure frequency reference | unknown | 2 |
| 4694 | multiple per day | False | True | no seizure frequency reference | no seizure frequency reference | 1 |
| 5476 | unknown | False | True | no seizure frequency reference | unknown | 2 |
| 5490 | unknown | False | True | no seizure frequency reference | unknown | 4 |
