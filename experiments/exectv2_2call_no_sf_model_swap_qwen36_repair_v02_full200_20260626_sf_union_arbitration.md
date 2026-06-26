# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_sf_union_arbitration.jsonl`
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
| `drop_anaphoric_generic_state` | 5 |
| `drop_bare_seizure_free_context` | 3 |
| `drop_composite_and_anchor` | 3 |
| `drop_current_bare_named_event` | 4 |
| `drop_det_generic_short_rate` | 4 |
| `drop_det_short_generic_anchor` | 114 |
| `drop_diffuse_unknown` | 6 |
| `drop_historical_or_advice_state` | 8 |
| `drop_non_target_event` | 8 |
| `drop_seizure_free_active_rate` | 2 |
| `rewrite_up_to_range_lower_zero` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.716 | 0.680 | 0.756 | 183 | 86 | 59 |
| active-rate | 0.761 | 0.671 | 0.879 | 94 | 46 | 13 |
| seizure-free | 0.689 | 0.656 | 0.726 | 61 | 32 | 23 |
| unknown | 0.644 | 0.778 | 0.549 | 28 | 8 | 23 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
