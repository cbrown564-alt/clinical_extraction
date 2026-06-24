# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_v08_full200_currentcode_sf_structured_direct_union_arbitration_20260624.jsonl`
- Arbitration version: `exectv2_hybrid_sf_union_arbitration_v08`
- Split: `full_200_authorized`
- Letters: 200

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| suppression | seizure_frequency | Drops non-target, historical, anaphoric, and source-shortened SF states. |
| benchmark surface rewrites | benchmark_format | Rewrites residual source phrases to the benchmark type/state surface. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `drop_anaphoric_generic_state` | 6 |
| `drop_bare_seizure_free_context` | 2 |
| `drop_current_bare_named_event` | 18 |
| `drop_det_generic_short_rate` | 4 |
| `drop_det_short_generic_anchor` | 114 |
| `drop_diffuse_unknown` | 4 |
| `drop_generic_free_history_or_span` | 3 |
| `drop_historical_or_advice_state` | 12 |
| `drop_named_unknown_long_context` | 2 |
| `drop_non_target_event` | 7 |
| `drop_seizure_free_active_rate` | 2 |
| `rewrite_cluster_of_3_to_seizure_cluster` | 1 |
| `rewrite_up_to_range_lower_zero` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.767 | 0.746 | 0.789 | 191 | 65 | 51 |
| active-rate | 0.816 | 0.769 | 0.869 | 93 | 28 | 14 |
| seizure-free | 0.762 | 0.711 | 0.821 | 69 | 28 | 15 |
| unknown | 0.652 | 0.763 | 0.569 | 29 | 9 | 22 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
