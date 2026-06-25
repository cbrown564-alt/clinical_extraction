# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_dev140_20260625_sf_union_arbitration.jsonl`
- Arbitration version: `exectv2_hybrid_sf_union_arbitration_v08`
- Split: `dev140`
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
| `drop_composite_and_anchor` | 1 |
| `drop_current_bare_named_event` | 1 |
| `drop_det_generic_short_rate` | 2 |
| `drop_det_short_generic_anchor` | 75 |
| `drop_diffuse_unknown` | 5 |
| `drop_generic_free_history_or_span` | 3 |
| `drop_historical_or_advice_state` | 8 |
| `drop_named_unknown_long_context` | 4 |
| `drop_non_target_event` | 1 |
| `drop_seizure_free_active_rate` | 2 |
| `rewrite_up_to_range_lower_zero` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.766 | 0.728 | 0.808 | 139 | 52 | 33 |
| active-rate | 0.798 | 0.722 | 0.890 | 65 | 25 | 8 |
| seizure-free | 0.761 | 0.699 | 0.836 | 51 | 22 | 10 |
| unknown | 0.697 | 0.821 | 0.605 | 23 | 5 | 15 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
