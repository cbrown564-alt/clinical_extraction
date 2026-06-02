# Gan 2026 Clinical Frequency State Graph Diagnostics

This is architecture and diagnostic work, not a benchmark result.

- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Rows: 50
- JSONL artifact: `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.json`
- Surface policy: Validation prefix of 50 rows for state-graph coverage diagnostics.

## Oracle Coverage

- Representable: 47/50 = 0.9400
- Missing gold representability: 3

| Gold kind | Rows | Representable | Rate |
| --- | ---: | ---: | ---: |
| frequency | 44 | 44 | 1.0000 |
| unresolved_multiple | 6 | 3 | 0.5000 |

## Projection Diagnostics

- Purist accuracy/F1: 0.9600 / 0.9600
- Pragmatic accuracy/F1: 0.9600 / 0.9600
- Exact normalized label matches: 45/50
- Rows with graph errors: 0
- Rows with competing hypotheses: 5

## Missing Representability by Gold Kind

| Gold kind | Missing rows |
| --- | ---: |
| unresolved_multiple | 3 |

## Top Projection Misses

| Source row | Gold | Projected | Gold kind | Node labels |
| ---: | --- | --- | --- | --- |
| 278 | multiple per week | seizure free for multiple year | unresolved_multiple | multiple per week, seizure free for multiple year |
| 338 | multiple per month | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 743 | multiple per week | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 744 | multiple per week | 1 per 8 week | unresolved_multiple | multiple per week, 1 per 8 week |
| 869 | multiple per month | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
