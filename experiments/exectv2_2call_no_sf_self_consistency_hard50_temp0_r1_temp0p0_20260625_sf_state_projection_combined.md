# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r1_temp0p0_20260625_sf_state_projection_combined.jsonl`
- Projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Source prompt version: `structured_direct_no_sf_adjudicator_v01`
- Ablation: `combined`
- Split: `hard50_temp0`
- Letters: 50

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| state projection | seizure_frequency | Changes active-rate / seizure-free / unknown state from explicit evidence spans. |
| ownership projection | seizure_frequency | Changes generic-vs-named seizure ownership from named seizure evidence. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `ownership.generic_active_to_named` | 2 |
| `state.drop_unlabelled_active_rate` | 3 |
| `state.last_event_active_to_seizure_free` | 1 |

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.585 | 0.574 | 0.596 | 31 | 23 | 21 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.642 | 0.630 | 0.654 | 17 | 10 | 9 |
| seizure-free | 0.588 | 0.500 | 0.714 | 10 | 10 | 4 |
| unknown | 0.421 | 0.571 | 0.333 | 4 | 3 | 8 |
