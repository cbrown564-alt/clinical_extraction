# Gan 2026 State Graph Family-Aware Validation Grouping

This grouping is validation-only and uses non-test-derived surface features.

- Source artifact: `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.jsonl`
- Rows: 250
- Summary JSON: `experiments/gan2026_clinical_frequency_state_graph_family_aware_validation_grouping_2026-06-02.json`

## Validation Hard Slices

| Group | Rows | Oracle coverage | Purist F1 | Pragmatic F1 | Exact labels | Competing hypotheses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| candidate_absent_or_weak | 4 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| cluster_or_diary | 219 | 0.8630 | 0.9224 | 0.9315 | 161 | 41 |
| deterministic_miss | 4 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| seizure_free_overreach | 71 | 0.5634 | 0.8873 | 0.8873 | 15 | 0 |
| shorthand_interval_range | 59 | 0.8983 | 0.9153 | 0.9322 | 40 | 10 |
| temporal_conflict | 209 | 0.8947 | 0.9234 | 0.9330 | 157 | 36 |
| unknown_no_reference_boundary | 27 | 0.0000 | 1.0000 | 1.0000 | 0 | 0 |

## Gold Semantic Kind

| Kind | Rows | Oracle coverage | Purist F1 | Pragmatic F1 |
| --- | ---: | ---: | ---: | ---: |
| frequency | 167 | 1.0000 | 0.9701 | 0.9820 |
| seizure_free | 38 | 1.0000 | 0.8947 | 0.8947 |
| unknown | 24 | 0.1667 | 0.7500 | 0.7500 |
| unresolved_multiple | 21 | 0.4762 | 0.7143 | 0.7143 |
