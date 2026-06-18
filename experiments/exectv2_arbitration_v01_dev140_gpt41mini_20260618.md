# ExECTv2 Hybrid — All Entities (GPT candidates + deterministic projection)

- JSONL: `experiments\exectv2_arbitration_v01_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_arbitration_v0.1`
- Split: `dev`
- Model (candidate source): `openai/gpt-4.1-mini`
- Rule augmentation: `False`
- Letters: 140

## Gate & routing

- Candidates offered: 1337
- Mentions scored (post gate): 875
- Routed (excluded): 0
- Routed taxonomy: {}

## Overall scores

| Layer | Item P | Item R | Item F1 | Letter P | Letter R | Letter F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.393 | 0.232 | 0.292 | 0.688 | 0.446 | 0.541 |
| semantic | 0.262 | 0.155 | 0.195 | 0.599 | 0.301 | 0.401 |
| benchmark | 0.206 | 0.122 | 0.153 | 0.552 | 0.249 | 0.343 |

Published targets: overall per-item 0.87 / per-letter 0.90.

## Per-entity (semantic, CUI-dropped) + projection ablation

| Entity | Pub item F1 | Semantic item F1 | Benchmark item F1 | Δ (CUI projection) | SN recall | Routed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.191 | 0.191 | +0.000 | 0.355 | 0 |
| Diagnosis | 0.85 | 0.227 | 0.141 | -0.086 | 0.254 | 0 |
| EpilepsyCause | 0.90 | 0.172 | 0.172 | +0.000 | 0.619 | 0 |
| Investigations | 0.95 | 0.472 | 0.412 | -0.060 | 0.669 | 0 |
| Onset | 0.96 | 0.182 | 0.182 | +0.000 | 0.647 | 0 |
| PatientHistory | 0.78 | 0.144 | 0.090 | -0.054 | 0.223 | 0 |
| Prescription | 0.87 | 0.149 | 0.149 | +0.000 | 0.709 | 0 |
| SeizureFrequency | 0.66 | 0.086 | 0.086 | +0.000 | 0.455 | 0 |
| WhenDiagnosed | 0.91 | 0.050 | 0.050 | +0.000 | 0.636 | 0 |
