# Gan 2026 Clinical Frequency State Graph Diagnostics

This is architecture and diagnostic work, not a benchmark result.

- Split: `validation_hard_slices`
- Split manifest: `gan2026_split_v1`
- Rows: 250
- JSONL artifact: `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.json`
- Surface policy: Projection-only ablation over validation hard-slice union from experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slices_2026-06-01.json; validation rows only.

## Oracle Coverage

- Representable: 219/250 = 0.8760
- Missing gold representability: 31

| Gold kind | Rows | Representable | Rate |
| --- | ---: | ---: | ---: |
| frequency | 167 | 167 | 1.0000 |
| seizure_free | 38 | 38 | 1.0000 |
| unknown | 24 | 4 | 0.1667 |
| unresolved_multiple | 21 | 10 | 0.4762 |

## Projection Diagnostics

- Purist accuracy/F1: 0.9160 / 0.9160
- Pragmatic accuracy/F1: 0.9240 / 0.9240
- Exact normalized label matches: 181/250
- Rows with graph errors: 0
- Rows with competing hypotheses: 44

## Missing Representability by Gold Kind

| Gold kind | Missing rows |
| --- | ---: |
| unknown | 20 |
| unresolved_multiple | 11 |

## Top Projection Misses

| Source row | Gold | Projected | Gold kind | Node labels |
| ---: | --- | --- | --- | --- |
| 278 | multiple per week | seizure free for multiple year | unresolved_multiple | multiple per week, seizure free for multiple year |
| 338 | multiple per month | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 743 | multiple per week | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 744 | multiple per week | 1 per 8 week | unresolved_multiple | multiple per week, 1 per 8 week |
| 869 | multiple per month | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 1317 | unknown, multiple per cluster | no seizure frequency reference | unknown | no seizure frequency reference |
| 1687 | multiple per week | 1 per 2 week | unresolved_multiple | 1 per 2 week, multiple per week |
| 1695 | multiple per month | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 1707 | multiple per week | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 2080 | multiple per month | no seizure frequency reference | unresolved_multiple | no seizure frequency reference |
| 2149 | unknown | no seizure frequency reference | unknown | no seizure frequency reference |
| 2166 | unknown | no seizure frequency reference | unknown | no seizure frequency reference |
