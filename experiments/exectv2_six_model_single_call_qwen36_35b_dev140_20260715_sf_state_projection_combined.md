# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_six_model_single_call_qwen36_35b_dev140_20260715_sf_state_projection_combined.jsonl`
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
| `state.drop_historical_or_advice_seizure_free` | 1 |
| `state.drop_preceded_by_current_seizure_free` | 1 |
| `state.drop_unlabelled_active_rate` | 15 |
| `state.last_event_active_to_seizure_free` | 2 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.704 | 0.700 | 0.708 | 119 | 51 | 49 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.766 | 0.727 | 0.810 | 64 | 24 | 15 |
| seizure-free | 0.719 | 0.719 | 0.719 | 41 | 16 | 16 |
| unknown | 0.491 | 0.560 | 0.438 | 14 | 11 | 18 |
