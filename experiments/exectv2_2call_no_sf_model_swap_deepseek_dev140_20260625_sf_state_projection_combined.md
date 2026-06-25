# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_dev140_20260625_sf_state_projection_combined.jsonl`
- Projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Source prompt version: `structured_direct_no_sf_adjudicator_v01`
- Ablation: `combined`
- Split: `dev140`
- Letters: 140

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| state projection | seizure_frequency | Changes active-rate / seizure-free / unknown state from explicit evidence spans. |
| ownership projection | seizure_frequency | Changes generic-vs-named seizure ownership from named seizure evidence. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `state.drop_historical_active_rate` | 1 |
| `state.drop_historical_or_advice_seizure_free` | 5 |
| `state.drop_unlabelled_active_rate` | 8 |
| `state.last_event_active_to_seizure_free` | 2 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.695 | 0.670 | 0.721 | 124 | 61 | 48 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.755 | 0.698 | 0.822 | 60 | 26 | 13 |
| seizure-free | 0.701 | 0.644 | 0.770 | 47 | 26 | 14 |
| unknown | 0.531 | 0.654 | 0.447 | 17 | 9 | 21 |
