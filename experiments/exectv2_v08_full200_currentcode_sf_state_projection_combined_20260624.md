# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_v08_full200_currentcode_sf_state_projection_combined_20260624.jsonl`
- Projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Source prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.5`
- Ablation: `combined`
- Split: `full_200_authorized`
- Letters: 200

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| state projection | seizure_frequency | Changes active-rate / seizure-free / unknown state from explicit evidence spans. |
| ownership projection | seizure_frequency | Changes generic-vs-named seizure ownership from named seizure evidence. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `state.change_recovery` | 16 |
| `state.drop_historical_active_rate` | 1 |
| `state.drop_historical_or_advice_seizure_free` | 6 |
| `state.drop_preceded_by_current_seizure_free` | 1 |
| `state.drop_unlabelled_active_rate` | 6 |
| `state.last_event_active_to_seizure_free` | 5 |
| `state.seizure_free_last_event_date` | 1 |
| `state.seizure_free_point_anchor` | 2 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.697 | 0.650 | 0.752 | 182 | 98 | 60 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.733 | 0.680 | 0.794 | 85 | 40 | 22 |
| seizure-free | 0.685 | 0.630 | 0.750 | 63 | 37 | 21 |
| unknown | 0.642 | 0.618 | 0.667 | 34 | 21 | 17 |
