# ExECTv2 Hybrid — All Entities (GPT candidates + deterministic projection)

- JSONL: `experiments\exectv2_arbitration_v02_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_arbitration_v0.2`
- Split: `dev`
- Model (candidate source): `openai/gpt-4.1-mini`
- Rule augmentation: `False`
- Letters: 140

## Gate & routing

- Candidates offered: 1337
- Mentions scored (post gate): 765
- Routed (excluded): 0
- Routed taxonomy: {}

## Overall scores

| Layer | Item P | Item R | Item F1 | Letter P | Letter R | Letter F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.418 | 0.216 | 0.285 | 0.696 | 0.384 | 0.495 |
| semantic | 0.278 | 0.144 | 0.190 | 0.608 | 0.261 | 0.365 |
| benchmark | 0.201 | 0.104 | 0.137 | 0.550 | 0.205 | 0.299 |

Published targets: overall per-item 0.87 / per-letter 0.90.

## Per-entity (semantic, CUI-dropped) + projection ablation

| Entity | Pub item F1 | Semantic item F1 | Benchmark item F1 | Δ (CUI projection) | SN recall | Routed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.158 | 0.158 | +0.000 | 0.226 | 0 |
| Diagnosis | 0.85 | 0.270 | 0.125 | -0.145 | 0.314 | 0 |
| EpilepsyCause | 0.90 | 0.163 | 0.163 | +0.000 | 0.429 | 0 |
| Investigations | 0.95 | 0.408 | 0.366 | -0.043 | 0.515 | 0 |
| Onset | 0.96 | 0.138 | 0.138 | +0.000 | 0.529 | 0 |
| PatientHistory | 0.78 | 0.117 | 0.078 | -0.039 | 0.170 | 0 |
| Prescription | 0.87 | 0.159 | 0.159 | +0.000 | 0.612 | 0 |
| SeizureFrequency | 0.66 | 0.076 | 0.076 | +0.000 | 0.390 | 0 |
| WhenDiagnosed | 0.91 | 0.067 | 0.067 | +0.000 | 0.182 | 0 |
