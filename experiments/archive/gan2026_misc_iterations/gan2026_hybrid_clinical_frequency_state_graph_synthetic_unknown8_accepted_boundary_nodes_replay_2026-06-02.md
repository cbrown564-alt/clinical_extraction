# Gan 2026 Accepted Boundary Nodes Graph Replay

This is diagnostic graph replay only, not a benchmark result.

- Source artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.jsonl`
- Split: `synthetic_hard_cases`
- Split manifest: `gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01`
- Rows: 8
- JSONL artifact: `experiments/gan2026_hybrid_clinical_frequency_state_graph_synthetic_unknown8_accepted_boundary_nodes_replay_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_hybrid_clinical_frequency_state_graph_synthetic_unknown8_accepted_boundary_nodes_replay_2026-06-02.json`

## Coverage Replay

- Accepted boundary-builder rows: 8
- Accepted hosted nodes: 8
- Baseline representable rows: 0/8
- Replayed representable rows: 8/8
- Representability gains: 8

## Projection Replay

- Exact normalized label matches: 7/8
- Purist accuracy/F1: 0.8750 / 0.8750
- Pragmatic accuracy/F1: 0.8750 / 0.8750
- Projection changed after accepted-node merge: 7

## Rows

| Source row | Gold | Baseline representable | Replayed representable | Baseline projection | Replayed projection | Hosted nodes |
| ---: | --- | --- | --- | --- | --- | ---: |
| 900016 | unknown | False | True | no seizure frequency reference | unknown | 1 |
| 900017 | unknown | False | True | no seizure frequency reference | unknown | 1 |
| 900019 | unknown | False | True | no seizure frequency reference | unknown | 1 |
| 900021 | unknown | False | True | no seizure frequency reference | unknown | 1 |
| 900022 | unknown | False | True | no seizure frequency reference | unknown | 1 |
| 900028 | unknown | False | True | no seizure frequency reference | unknown | 1 |
| 900030 | unknown | False | True | 1 per multiple week | unknown | 1 |
| 900044 | unknown | False | True | 4 per day | 4 per day | 1 |
