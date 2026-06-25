# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_full200_20260625_sf_union_arbitration.jsonl`
- Arbitration version: `exectv2_hybrid_sf_union_arbitration_v08`
- Split: `full200`
- Letters: 200

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| suppression | seizure_frequency | Drops non-target, historical, anaphoric, and source-shortened SF states. |
| benchmark surface rewrites | benchmark_format | Rewrites residual source phrases to the benchmark type/state surface. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `drop_anaphoric_generic_state` | 2 |
| `drop_bare_seizure_free_context` | 1 |
| `drop_composite_and_anchor` | 1 |
| `drop_current_bare_named_event` | 1 |
| `drop_det_generic_short_rate` | 4 |
| `drop_det_short_generic_anchor` | 114 |
| `drop_diffuse_unknown` | 6 |
| `drop_generic_free_history_or_span` | 3 |
| `drop_historical_or_advice_state` | 11 |
| `drop_named_unknown_long_context` | 3 |
| `drop_non_target_event` | 6 |
| `drop_seizure_free_active_rate` | 2 |
| `rewrite_up_to_range_lower_zero` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.772 | 0.731 | 0.818 | 198 | 73 | 44 |
| active-rate | 0.784 | 0.696 | 0.897 | 96 | 42 | 11 |
| seizure-free | 0.793 | 0.747 | 0.845 | 71 | 24 | 13 |
| unknown | 0.697 | 0.816 | 0.608 | 31 | 7 | 20 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
