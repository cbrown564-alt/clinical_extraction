# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_sf_union_arbitration.jsonl`
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
| `drop_bare_seizure_free_context` | 1 |
| `drop_composite_and_anchor` | 2 |
| `drop_current_bare_named_event` | 1 |
| `drop_det_generic_short_rate` | 2 |
| `drop_det_short_generic_anchor` | 75 |
| `drop_diffuse_unknown` | 1 |
| `drop_historical_or_advice_state` | 6 |
| `drop_non_target_event` | 2 |
| `drop_seizure_free_active_rate` | 2 |
| `rewrite_up_to_range_lower_zero` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.692 | 0.646 | 0.744 | 128 | 70 | 44 |
| active-rate | 0.753 | 0.660 | 0.877 | 64 | 33 | 9 |
| seizure-free | 0.661 | 0.636 | 0.689 | 42 | 24 | 19 |
| unknown | 0.603 | 0.629 | 0.579 | 22 | 13 | 16 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
