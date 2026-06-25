# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r4_temp0p0_20260625_sf_union_arbitration.jsonl`
- Arbitration version: `exectv2_hybrid_sf_union_arbitration_v08`
- Split: `hard50_temp0`
- Letters: 50

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
| `drop_current_bare_named_event` | 3 |
| `drop_det_generic_short_rate` | 1 |
| `drop_det_short_generic_anchor` | 23 |
| `drop_diffuse_unknown` | 1 |
| `drop_generic_free_history_or_span` | 1 |
| `drop_historical_or_advice_state` | 6 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.822 | 0.800 | 0.846 | 44 | 11 | 8 |
| active-rate | 0.857 | 0.800 | 0.923 | 24 | 6 | 2 |
| seizure-free | 0.828 | 0.800 | 0.857 | 12 | 3 | 2 |
| unknown | 0.727 | 0.800 | 0.667 | 8 | 2 | 4 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
