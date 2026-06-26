# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_state_projection_combined.jsonl`
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
| `state.drop_unlabelled_active_rate` | 16 |
| `state.last_event_active_to_seizure_free` | 1 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.618 | 0.615 | 0.622 | 107 | 67 | 65 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.675 | 0.631 | 0.726 | 53 | 31 | 20 |
| seizure-free | 0.609 | 0.582 | 0.639 | 39 | 28 | 22 |
| unknown | 0.492 | 0.652 | 0.395 | 15 | 8 | 23 |
