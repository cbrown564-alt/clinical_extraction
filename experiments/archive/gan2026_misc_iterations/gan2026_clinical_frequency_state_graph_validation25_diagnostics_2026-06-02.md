# Gan 2026 Clinical Frequency State Graph Diagnostics

This is architecture and diagnostic work, not a benchmark result.

- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Rows: 25
- JSONL artifact: `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.json`
- Surface policy: Validation prefix of 25 rows for state-graph coverage diagnostics.

## Oracle Coverage

- Representable: 24/25 = 0.9600
- Missing gold representability: 1

| Gold kind | Rows | Representable | Rate |
| --- | ---: | ---: | ---: |
| frequency | 22 | 22 | 1.0000 |
| unresolved_multiple | 3 | 2 | 0.6667 |

## Projection Diagnostics

- Purist accuracy/F1: 0.9600 / 0.9600
- Pragmatic accuracy/F1: 0.9600 / 0.9600
- Exact normalized label matches: 23/25
- Rows with graph errors: 0
- Rows with competing hypotheses: 2

## Missing Representability by Gold Kind

| Gold kind | Missing rows |
| --- | ---: |
| unresolved_multiple | 1 |

## Top Projection Misses

| Source row | Gold | Projected | Gold kind | Node labels |
| ---: | --- | --- | --- | --- |
| 278 | multiple per week | seizure free for multiple year | unresolved_multiple | multiple per week, seizure free for multiple year |
| 338 | multiple per month | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
