# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_six_model_single_call_gpt56sol_dev140_20260715_sf_state_projection_combined.jsonl`
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
| `ownership.generic_active_to_named` | 1 |
| `state.drop_historical_active_rate` | 1 |
| `state.drop_preceded_by_current_seizure_free` | 2 |
| `state.last_event_active_to_seizure_free` | 3 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.801 | 0.811 | 0.792 | 133 | 31 | 35 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.812 | 0.779 | 0.848 | 67 | 19 | 12 |
| seizure-free | 0.865 | 0.889 | 0.842 | 48 | 6 | 9 |
| unknown | 0.643 | 0.750 | 0.562 | 18 | 6 | 14 |
