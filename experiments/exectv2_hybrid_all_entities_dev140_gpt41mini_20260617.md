# ExECTv2 Hybrid — All Entities (GPT candidates + deterministic projection)

- JSONL: `experiments\exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl`
- Prompt version: `exectv2_hybrid_all_entities_v0.1`
- Split: `dev`
- Model (candidate source): `openai/gpt-4.1-mini`
- Rule augmentation: `False`
- Letters: 140

## Gate & routing

- Candidates offered: 1337
- Mentions scored (post gate): 1326
- Routed (excluded): 11
- Routed taxonomy: {'no_frequency_attributes': 4, 'bare_nonzero_count': 2, 'duplicate_mention': 5}

## Overall scores

| Layer | Item P | Item R | Item F1 | Letter P | Letter R | Letter F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.348 | 0.311 | 0.329 | 0.655 | 0.599 | 0.626 |
| semantic | 0.232 | 0.208 | 0.220 | 0.565 | 0.410 | 0.475 |
| benchmark | 0.192 | 0.172 | 0.181 | 0.526 | 0.350 | 0.420 |

Published targets: overall per-item 0.87 / per-letter 0.90.

## Per-entity (semantic, CUI-dropped) + projection ablation

| Entity | Pub item F1 | Semantic item F1 | Benchmark item F1 | Δ (CUI projection) | SN recall | Routed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.281 | 0.246 | -0.035 | 0.806 | 0 |
| Diagnosis | 0.85 | 0.243 | 0.172 | -0.072 | 0.306 | 0 |
| EpilepsyCause | 0.90 | 0.175 | 0.175 | +0.000 | 0.809 | 0 |
| Investigations | 0.95 | 0.548 | 0.490 | -0.057 | 0.890 | 1 |
| Onset | 0.96 | 0.148 | 0.130 | -0.018 | 0.824 | 0 |
| PatientHistory | 0.78 | 0.161 | 0.106 | -0.054 | 0.360 | 1 |
| Prescription | 0.87 | 0.174 | 0.174 | +0.000 | 0.903 | 2 |
| SeizureFrequency | 0.66 | 0.131 | 0.131 | +0.000 | 0.620 | 7 |
| WhenDiagnosed | 0.91 | 0.073 | 0.073 | +0.000 | 1.000 | 0 |
