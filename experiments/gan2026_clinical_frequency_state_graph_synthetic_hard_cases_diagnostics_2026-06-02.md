# Gan 2026 Clinical Frequency State Graph Diagnostics

This is architecture and diagnostic work, not a benchmark result.

- Split: `synthetic_hard_cases`
- Split manifest: `gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01`
- Rows: 56
- JSONL artifact: `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.json`
- Surface policy: Reviewed synthetic hard-case development panel; not validation or holdout.

## Oracle Coverage

- Representable: 30/56 = 0.5357
- Missing gold representability: 26

| Gold kind | Rows | Representable | Rate |
| --- | ---: | ---: | ---: |
| frequency | 36 | 20 | 0.5556 |
| no_reference | 11 | 9 | 0.8182 |
| seizure_free | 1 | 1 | 1.0000 |
| unknown | 8 | 0 | 0.0000 |

## Projection Diagnostics

- Purist accuracy/F1: 0.6964 / 0.6964
- Pragmatic accuracy/F1: 0.7500 / 0.7500
- Exact normalized label matches: 26/56
- Rows with graph errors: 0
- Rows with competing hypotheses: 6

## Missing Representability by Gold Kind

| Gold kind | Missing rows |
| --- | ---: |
| frequency | 16 |
| no_reference | 2 |
| unknown | 8 |

## Top Projection Misses

| Source row | Gold | Projected | Gold kind | Node labels |
| ---: | --- | --- | --- | --- |
| 900001 | 1 per 2 week | 5 per week | frequency | 5 per week, 1 per 2 week |
| 900002 | seizure free for 6 month | 3 per week | seizure_free | 3 per week, seizure free for 6 month |
| 900005 | 6 per month | 20 per month | frequency | 20 per month, 6 per month |
| 900008 | 1 per week | 8 per week | frequency | 8 per week, 1 per 8 month |
| 900014 | 2 per 1 month | no seizure frequency reference | frequency | no seizure frequency reference |
| 900016 | unknown | no seizure frequency reference | unknown | no seizure frequency reference |
| 900017 | unknown | no seizure frequency reference | unknown | no seizure frequency reference |
| 900019 | unknown | no seizure frequency reference | unknown | no seizure frequency reference |
| 900021 | unknown | no seizure frequency reference | unknown | no seizure frequency reference |
| 900022 | unknown | no seizure frequency reference | unknown | no seizure frequency reference |
| 900024 | 1 cluster per 2 week, 3 per cluster | no seizure frequency reference | frequency | no seizure frequency reference |
| 900025 | 2 cluster per month, 5 per cluster | no seizure frequency reference | frequency | no seizure frequency reference |
