# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_six_model_single_call_gemma4_26b_dev140_20260715_sf_state_projection_combined.jsonl`
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
| `state.drop_historical_active_rate` | 2 |
| `state.drop_historical_or_advice_seizure_free` | 3 |
| `state.drop_preceded_by_current_seizure_free` | 1 |
| `state.drop_unlabelled_active_rate` | 8 |
| `state.last_event_active_to_seizure_free` | 3 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.617 | 0.571 | 0.673 | 113 | 85 | 55 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.674 | 0.606 | 0.759 | 60 | 39 | 19 |
| seizure-free | 0.661 | 0.692 | 0.632 | 36 | 16 | 21 |
| unknown | 0.430 | 0.362 | 0.531 | 17 | 30 | 15 |
