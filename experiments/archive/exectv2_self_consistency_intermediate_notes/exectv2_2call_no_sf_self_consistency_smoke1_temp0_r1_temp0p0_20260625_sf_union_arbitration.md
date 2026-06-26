# ExECTv2 SeizureFrequency Union Arbitration v0.8

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_smoke1_temp0_r1_temp0p0_20260625_sf_union_arbitration.jsonl`
- Arbitration version: `exectv2_hybrid_sf_union_arbitration_v08`
- Split: `smoke1_temp0`
- Letters: 1

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| suppression | seizure_frequency | Drops non-target, historical, anaphoric, and source-shortened SF states. |
| benchmark surface rewrites | benchmark_format | Rewrites residual source phrases to the benchmark type/state surface. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `drop_det_short_generic_anchor` | 1 |

## Clinical Headline

| Slice | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.667 | 0.500 | 1.000 | 1 | 1 | 0 |
| active-rate | 0.667 | 0.500 | 1.000 | 1 | 1 | 0 |
| seizure-free | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| unknown | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |

This is a no-call replay over saved GPT-4.1-mini and deterministic candidate sources. The arbitration rules are prediction-bearing and must be reported as deterministic post-processing.
