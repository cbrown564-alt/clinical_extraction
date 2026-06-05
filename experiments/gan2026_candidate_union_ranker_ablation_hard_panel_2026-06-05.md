# Gan 2026 Candidate-Union Ranker Ablation

Validation hard-panel ranker ablation over selected-state union candidates. Ranker selection uses non-gold candidate features; gold labels are used only after selection for W->C/C->W accounting. This does not change production predictions, scorer policy, split policy, or locked-test behavior.

## Summary

Base hard-panel Purist proxy: 0.4933 (37 / 75).
Oracle recoverable miss rows: 16; oracle upper bound 0.7067.

| Ranker | Selected | W->C | C->W | Projected proxy | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `diary_log_only_v0` | 3 | 3 | 0 | 0.5333 | `promote_candidate` |
| `comparator_absent_quality_rank_v0` | 37 | 13 | 5 | 0.6000 | `diagnostic_positive_but_not_promotable` |
| `comparator_absent_structural_guard_rank_v0` | 24 | 10 | 0 | 0.6267 | `promote_candidate` |
| `unknown_or_cluster_frequency_rank_v0` | 17 | 3 | 7 | 0.4400 | `reject` |

## Interpretation

`comparator_absent_structural_guard_rank_v0` is a clean validation hard-panel signal with 10 W->C and 0 C->W. Expand this family with negative tests before any full-validation or holdout use.

## Artifacts

- Ranker CSV: `experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.csv`
- Ranker JSON: `experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.json`
