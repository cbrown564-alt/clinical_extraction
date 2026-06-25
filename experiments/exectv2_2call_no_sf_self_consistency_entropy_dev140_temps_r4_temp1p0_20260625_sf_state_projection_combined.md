# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r4_temp1p0_20260625_sf_state_projection_combined.jsonl`
- Projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Source prompt version: `structured_direct_no_sf_adjudicator_v01`
- Ablation: `combined`
- Split: `entropy_dev140_temps`
- Letters: 140

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| state projection | seizure_frequency | Changes active-rate / seizure-free / unknown state from explicit evidence spans. |
| ownership projection | seizure_frequency | Changes generic-vs-named seizure ownership from named seizure evidence. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `ownership.generic_active_to_named` | 3 |
| `state.drop_historical_active_rate` | 2 |
| `state.drop_historical_or_advice_seizure_free` | 4 |
| `state.drop_unlabelled_active_rate` | 5 |
| `state.last_event_active_to_seizure_free` | 4 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.632 | 0.635 | 0.628 | 108 | 62 | 64 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.662 | 0.630 | 0.699 | 51 | 30 | 22 |
| seizure-free | 0.688 | 0.672 | 0.705 | 43 | 21 | 18 |
| unknown | 0.444 | 0.560 | 0.368 | 14 | 11 | 24 |
