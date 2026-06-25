# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_sf_state_projection_combined.jsonl`
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
| `state.drop_unlabelled_active_rate` | 15 |
| `state.last_event_active_to_seizure_free` | 3 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.568 | 0.578 | 0.558 | 96 | 70 | 76 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.671 | 0.624 | 0.726 | 53 | 32 | 20 |
| seizure-free | 0.552 | 0.582 | 0.525 | 32 | 23 | 29 |
| unknown | 0.344 | 0.423 | 0.289 | 11 | 15 | 27 |
