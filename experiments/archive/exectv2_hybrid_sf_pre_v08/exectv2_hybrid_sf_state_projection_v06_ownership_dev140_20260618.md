# ExECTv2 SeizureFrequency State/Ownership Projection v0.6

- JSONL: `experiments\exectv2_hybrid_sf_state_projection_v06_ownership_dev140_20260618.jsonl`
- Projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Source prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.5`
- Ablation: `ownership`
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

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.721 | 0.710 | 0.733 | 137 | 56 | 50 |

## State Slices

| State | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.762 | 0.720 | 0.809 | 72 | 28 | 17 |
| seizure-free | 0.781 | 0.794 | 0.769 | 50 | 13 | 15 |
| unknown | 0.476 | 0.500 | 0.455 | 15 | 15 | 18 |
