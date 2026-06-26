# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r3_temp0p7_20260625_sf_union_arbitration.jsonl`
- Arbitration version: `exectv2_hybrid_sf_union_arbitration_v08`
- Split: `entropy_dev140_temps`
- Letters: 140

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| suppression | seizure_frequency | Drops non-target, historical, anaphoric, and source-shortened SF states. |
| benchmark surface rewrites | benchmark_format | Rewrites residual source phrases to the benchmark type/state surface. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `drop_anaphoric_generic_state` | 1 |
| `drop_bare_seizure_free_context` | 1 |
| `drop_current_bare_named_event` | 10 |
| `drop_det_generic_short_rate` | 2 |
| `drop_det_short_generic_anchor` | 75 |
| `drop_diffuse_unknown` | 2 |
| `drop_generic_free_history_or_span` | 3 |
| `drop_historical_or_advice_state` | 9 |
| `drop_named_unknown_long_context` | 1 |
| `drop_non_target_event` | 3 |
| `drop_seizure_free_active_rate` | 2 |
| `rewrite_cluster_of_3_to_seizure_cluster` | 1 |
| `rewrite_up_to_range_lower_zero` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.780 | 0.749 | 0.814 | 140 | 47 | 32 |
| active-rate | 0.815 | 0.742 | 0.904 | 66 | 23 | 7 |
| seizure-free | 0.785 | 0.739 | 0.836 | 51 | 18 | 10 |
| unknown | 0.687 | 0.793 | 0.605 | 23 | 6 | 15 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
