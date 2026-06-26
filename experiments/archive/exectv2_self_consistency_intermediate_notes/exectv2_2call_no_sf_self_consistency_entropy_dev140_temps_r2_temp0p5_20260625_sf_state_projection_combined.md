# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_sf_state_projection_combined.jsonl`
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
| `state.drop_historical_active_rate` | 1 |
| `state.drop_historical_or_advice_seizure_free` | 5 |
| `state.drop_unlabelled_active_rate` | 7 |
| `state.last_event_active_to_seizure_free` | 4 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.624 | 0.626 | 0.622 | 107 | 64 | 65 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.688 | 0.654 | 0.726 | 53 | 28 | 20 |
| seizure-free | 0.677 | 0.652 | 0.705 | 43 | 23 | 18 |
| unknown | 0.355 | 0.458 | 0.289 | 11 | 13 | 27 |
