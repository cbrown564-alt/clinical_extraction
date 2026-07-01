# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_section_timeline_ablation_dev140_sf_union_with_timeline.jsonl`
- Arbitration version: `exectv2_hybrid_sf_union_arbitration_v08`
- Split: `dev`
- Letters: 140

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| suppression | seizure_frequency | Drops non-target, historical, anaphoric, and source-shortened SF states. |
| benchmark surface rewrites | benchmark_format | Rewrites residual source phrases to the benchmark type/state surface. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `drop_anaphoric_generic_state` | 5 |
| `drop_bare_seizure_free_context` | 5 |
| `drop_current_bare_named_event` | 2 |
| `drop_det_generic_short_rate` | 3 |
| `drop_det_short_generic_anchor` | 84 |
| `drop_diffuse_unknown` | 3 |
| `drop_generic_free_history_or_span` | 2 |
| `drop_historical_or_advice_state` | 8 |
| `drop_named_unknown_long_context` | 4 |
| `drop_non_target_event` | 9 |
| `drop_seizure_free_active_rate` | 1 |
| `rewrite_absences_to_typical_absences` | 1 |
| `rewrite_anaphoric_named_to_generic_seizures` | 2 |
| `rewrite_cluster_of_3_to_seizure_cluster` | 1 |
| `rewrite_up_to_range_lower_zero` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.915 | 0.897 | 0.935 | 157 | 18 | 11 |
| active-rate | 0.920 | 0.882 | 0.962 | 75 | 10 | 3 |
| seizure-free | 0.931 | 0.931 | 0.931 | 54 | 4 | 4 |
| unknown | 0.875 | 0.875 | 0.875 | 28 | 4 | 4 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
