# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_hybrid_sf_state_projection_v06_combined_dev140_20260618.jsonl`
- Projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Source prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.5`
- Ablation: `combined`
- Split: `dev`
- Letters: 140

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| state projection | seizure_frequency | Changes active-rate / seizure-free / unknown state from explicit evidence spans. |
| ownership projection | seizure_frequency | Changes generic-vs-named seizure ownership from named seizure evidence. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `state.change_recovery` | 17 |
| `state.drop_historical_active_rate` | 1 |
| `state.drop_historical_or_advice_seizure_free` | 2 |
| `state.drop_preceded_by_current_seizure_free` | 1 |
| `state.drop_unlabelled_active_rate` | 6 |
| `state.last_event_active_to_seizure_free` | 1 |
| `state.seizure_free_last_event_date` | 4 |
| `state.seizure_free_last_event_duration` | 1 |
| `state.seizure_free_point_anchor` | 4 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.763 | 0.722 | 0.807 | 151 | 58 | 36 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.800 | 0.791 | 0.809 | 72 | 19 | 17 |
| seizure-free | 0.794 | 0.761 | 0.831 | 54 | 17 | 11 |
| unknown | 0.625 | 0.532 | 0.758 | 25 | 22 | 8 |
