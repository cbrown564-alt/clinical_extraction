# Gan 2026 State Graph Counterfactual Invariance

This is a validation-derived diagnostic panel. It is not final-label accuracy and not a benchmark result.

- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Rows: 50
- Order invariance: 50/50 = 1.0000
- Lexical paraphrase invariance: 49/50 = 0.9800
- JSONL artifact: `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.json`

## First Invariance Misses

| Source row | Gold kind | Original nodes | Reordered nodes | Paraphrase nodes | Order ok | Paraphrase ok |
| ---: | --- | ---: | ---: | ---: | --- | --- |
| 891 | frequency | 2 | 2 | 1 | True | False |
