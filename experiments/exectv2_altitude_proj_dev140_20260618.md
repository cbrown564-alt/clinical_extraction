# ExECTv2 Hybrid — All Entities (GPT candidates + deterministic projection)

- JSONL: `experiments\exectv2_altitude_proj_dev140_20260618.jsonl`
- Prompt version: `benchmark_altitude_v0.1`
- Split: `dev`
- Model (candidate source): `altitude_projection`
- Rule augmentation: `False`
- Letters: 140

## Gate & routing

- Candidates offered: 0
- Mentions scored (post gate): 0
- Routed (excluded): 0
- Routed taxonomy: {}

## Overall scores

| Layer | Item P | Item R | Item F1 | Letter P | Letter R | Letter F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.369 | 0.359 | 0.364 | 0.668 | 0.635 | 0.651 |
| semantic | 0.246 | 0.239 | 0.242 | 0.584 | 0.443 | 0.504 |
| benchmark | 0.183 | 0.178 | 0.181 | 0.530 | 0.357 | 0.426 |

Published targets: overall per-item 0.87 / per-letter 0.90.

## Per-entity (semantic, CUI-dropped) + projection ablation

| Entity | Pub item F1 | Semantic item F1 | Benchmark item F1 | Δ (CUI projection) | SN recall | Routed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.281 | 0.246 | -0.035 | 0.806 | 0 |
| Diagnosis | 0.85 | 0.318 | 0.147 | -0.171 | 0.486 | 0 |
| EpilepsyCause | 0.90 | 0.175 | 0.175 | +0.000 | 0.809 | 0 |
| Investigations | 0.95 | 0.548 | 0.490 | -0.057 | 0.890 | 0 |
| Onset | 0.96 | 0.148 | 0.130 | -0.018 | 0.824 | 0 |
| PatientHistory | 0.78 | 0.180 | 0.127 | -0.053 | 0.371 | 0 |
| Prescription | 0.87 | 0.174 | 0.174 | +0.000 | 0.903 | 0 |
| SeizureFrequency | 0.66 | 0.131 | 0.131 | +0.000 | 0.620 | 0 |
| WhenDiagnosed | 0.91 | 0.073 | 0.073 | +0.000 | 1.000 | 0 |
