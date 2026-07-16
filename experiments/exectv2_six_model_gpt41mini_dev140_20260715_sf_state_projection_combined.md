# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_six_model_gpt41mini_dev140_20260715_sf_state_projection_combined.jsonl`
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
| `ownership.generic_active_to_named` | 2 |
| `state.drop_historical_active_rate` | 2 |
| `state.drop_historical_or_advice_seizure_free` | 5 |
| `state.drop_unlabelled_active_rate` | 8 |
| `state.last_event_active_to_seizure_free` | 3 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.640 | 0.634 | 0.645 | 111 | 64 | 61 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.654 | 0.612 | 0.703 | 52 | 33 | 22 |
| seizure-free | 0.746 | 0.712 | 0.783 | 47 | 19 | 13 |
| unknown | 0.387 | 0.500 | 0.316 | 12 | 12 | 26 |
