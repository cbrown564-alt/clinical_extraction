# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_sf_state_projection_combined.jsonl`
- Projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Source prompt version: `structured_direct_no_sf_adjudicator_v01`
- Ablation: `combined`
- Split: `full200`
- Letters: 200

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
| `state.drop_preceded_by_current_seizure_free` | 1 |
| `state.drop_unlabelled_active_rate` | 19 |
| `state.last_event_active_to_seizure_free` | 3 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.629 | 0.614 | 0.645 | 156 | 98 | 86 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.709 | 0.646 | 0.785 | 84 | 46 | 23 |
| seizure-free | 0.590 | 0.573 | 0.607 | 51 | 38 | 33 |
| unknown | 0.488 | 0.600 | 0.412 | 21 | 14 | 30 |
