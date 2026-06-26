# Gan 2026 Qwen v0.6 Validation750 Repair Replay Error Analysis

Date: 2026-06-21

Scope: no-call replay of existing Qwen v0.6 validation750 raw outputs. This is validation development work on `gan2026_split_v1`; no test450 row-level output was inspected.

## Summary

- Source artifact: `experiments\gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl`
- Replay JSONL: `experiments\gan2026_v06_validation750_hybrid_structured_events_qwen3635b_replay_repairfix_2026-06-21.jsonl`
- Replay report: `experiments\gan2026_v06_validation750_hybrid_structured_events_qwen3635b_replay_repairfix_2026-06-21.md`
- Baseline Purist validation accuracy/micro F1 proxy: 0.8507 (638 / 750)
- Replay Purist validation accuracy/micro F1 proxy: 0.8827 (662 / 750)
- Delta: +24 corrected rows, 0 regressions
- Parse/schema/label issues: 1 (baseline 4)

## Implemented Repair Themes

- Qwen schema aliases: tolerate `temporality=hypothetical` and `historical/current`, plus existing assertion alias repair.
- Selected-evidence count windows: derive clean `N per WINDOW` labels for episode/aura counts while ignoring incidental `including N episodes` examples.
- Sustained selected seizure-free: prevent elapsed-anchor repair from converting selected sustained seizure-free intervals into `1 per N month` when the selected event itself is seizure-free over a >=4 month interval.
- Multi-semiology highest burden: derive explicit high-burden rates such as `4 times per day`, `4 absences per day`, `daily drop attacks`, and `no more than twice weekly`, with guards for PRN medication limits and seizure-free medication-dose text.

## Corrected Rows

| Row | Final | Gold | Main repair notes |
| ---: | --- | --- | --- |
| 743 | multiple per day | multiple per week |  |
| 2992 | seizure free for multiple year | seizure free for 7 month | final_label_repaired: 'seizure free since 19-May-2024' -> 'seizure free for multiple year' |
| 3015 | seizure free for 1 year | seizure free for 12 month |  |
| 3988 | multiple per week | multiple per week | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 3999 | 1 per month | 1 per month |  |
| 4839 | seizure free for multiple year | seizure free for multiple month | final_label_repaired: 'seizure free for 4+ months' -> 'seizure free for multiple year' |
| 5866 | 4 per 6 week | 4 per 6 week | final_label_repaired: '4 in 6 weeks' -> '4 per 6 week' |
| 6358 | seizure free for 6 month | seizure free for 15 to 16 months |  |
| 8924 | seizure free for multiple year | seizure free for multiple month | final_label_repaired: 'seizure free since May 2025' -> 'seizure free for multiple year' |
| 12314 | 3 per week | 3 per week | final_label_repaired: 'multiple per week' -> '3 per week' |
| 12366 | 4 per day | 4 per day | final_label_repaired: 'multiple seizure types with high frequency (4/day, clusters, 2/month)' -> '4 per day' |
| 12378 | 4 per day | 4 per day | final_label_repaired: 'multiple per day' -> '4 per day' |
| 12383 | 4 per day | 4 per day | final_label_repaired: 'multiple seizure types with high frequency (focal: 4/day; drop attacks: clusters; tonic-clonic: 2/month)' -> '4 per day' |
| 12403 | 2 to 3 per day | 2 to 3 per day | final_label_repaired: 'multiple per day' -> '2 to 3 per day' |
| 12412 | 2 per day | 2 per day | final_label_repaired: 'multiple seizure types with varying frequencies (2/day, clusters, 2/month)' -> '2 per day' |
| 12506 | 4 per day | 4 per day | final_label_repaired: 'multiple per day' -> '4 per day' |
| 12562 | 1 per day | 1 per day | final_label_repaired: 'multiple per day/week' -> '1 per day' |
| 12573 | 1 per day | 1 per day | final_label_repaired: 'multiple seizure types: GTCs up to 2/month, daily drop attacks, FIAS every 4-6 weeks' -> '1 per day' |
| 12679 | 1 per day | 1 per day | final_label_repaired: 'multiple seizure types: 1-2 GTCS/month, daily absences, focal non-motor every 3-4 weeks, drop attacks' -> '1 per day' |
| 12749 | 3 to 4 per day | 3 to 4 per day | final_label_repaired: 'multiple per day' -> '3 to 4 per day' |
| 12751 | 4 per day | 4 per day | final_label_repaired: 'multiple per day' -> '4 per day' |
| 16938 | 2 per week | 2 per week | final_label_repaired: '2 per 2 months (GTC), up to 2 per week (Absence)' -> '2 per week' |
| 16947 | 2 per week | 2 per week | final_label_repaired: '4 per 2 months (GTC), up to 2 per week (absence)' -> '2 per week' |
| 16961 | 2 per week | 2 per week | final_label_repaired: 'multiple per week' -> '2 per week' |

## Regressions

None in this replay.

## Remaining Miss Clusters

Top gold labels among remaining Purist misses:

- `unknown`: 21
- `seizure free for multiple month`: 4
- `2 per month`: 2
- `1 cluster per month, multiple per cluster`: 2
- `3 cluster per month, multiple per cluster`: 2
- `4 per 6 month`: 2
- `8 per 2 month`: 1
- `3 to 5 per month`: 1
- `7 to 9 per 2 week`: 1
- `2 to 3 per 3 month`: 1
- `seizure free for 9 month`: 1
- `7 per 7 month`: 1

Top remaining gold -> predicted Purist-category transitions:

- `unknown` -> `currently_no_seizure`: 10
- `unknown` -> `seizure_freq_more1mon_less1week`: 4
- `unknown` -> `seizure_freq_more1per6mon_less1mon`: 2
- `unknown` -> `seizure_freq_1_per_mon`: 2
- `seizure free for multiple month` -> `seizure_freq_unknown`: 2
- `1 cluster per month, multiple per cluster` -> `seizure_freq_unknown`: 2
- `8 per 2 month` -> `seizure_freq_unknown`: 1
- `3 to 5 per month` -> `seizure_freq_more1week_less1day`: 1
- `7 to 9 per 2 week` -> `seizure_freq_1_per_mon`: 1
- `2 to 3 per 3 month` -> `seizure_freq_more1mon_less1week`: 1
- `seizure free for 9 month` -> `seizure_freq_more1week_less1day`: 1
- `7 per 7 month` -> `seizure_freq_more1mon_less1week`: 1

## Next Validation Targets

- Unknown-boundary rows where Qwen selects seizure-free or a concrete rate from uncertain/provoked/recent-only wording remain the largest cluster.
- Cluster labels with imprecise per-cluster burden are still under-repaired; examples remain in monthly and multi-week cluster gold labels.
- Some seizure-free multiple-month rows still become unknown because the model omits a normalizable raw interval or selects evidence too vaguely.
