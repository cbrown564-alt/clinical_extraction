# ExECTv2 Hybrid — All Entities (GPT candidates + deterministic projection)

- JSONL: `experiments\exectv2_hybrid_all_entities_dev140_gpt41mini_20260617_ruleaug.jsonl`
- Prompt version: `exectv2_hybrid_all_entities_v0.1`
- Split: `dev`
- Model (candidate source): `openai/gpt-4.1-mini`
- Rule augmentation: `True`
- Letters: 140

## Gate & routing

- Candidates offered: 2347
- Mentions scored (post gate): 2083
- Routed (excluded): 264
- Routed taxonomy: {'duplicate_mention': 258, 'no_frequency_attributes': 4, 'bare_nonzero_count': 2}

## Overall scores

| Layer | Item P | Item R | Item F1 | Letter P | Letter R | Letter F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.356 | 0.501 | 0.416 | 0.711 | 0.788 | 0.748 |
| semantic | 0.294 | 0.414 | 0.344 | 0.685 | 0.697 | 0.691 |
| benchmark | 0.267 | 0.376 | 0.312 | 0.669 | 0.648 | 0.658 |

Published targets: overall per-item 0.87 / per-letter 0.90.

## Per-entity (semantic, CUI-dropped) + projection ablation

| Entity | Pub item F1 | Semantic item F1 | Benchmark item F1 | Δ (CUI projection) | SN recall | Routed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.538 | 0.462 | -0.077 | 0.968 | 9 |
| Diagnosis | 0.85 | 0.347 | 0.284 | -0.063 | 0.459 | 52 |
| EpilepsyCause | 0.90 | 0.274 | 0.274 | +0.000 | 0.905 | 9 |
| Investigations | 0.95 | 0.444 | 0.399 | -0.045 | 0.971 | 101 |
| Onset | 0.96 | 0.142 | 0.124 | -0.018 | 0.882 | 13 |
| PatientHistory | 0.78 | 0.244 | 0.197 | -0.047 | 0.524 | 39 |
| Prescription | 0.87 | 0.307 | 0.307 | +0.000 | 0.952 | 4 |
| SeizureFrequency | 0.66 | 0.524 | 0.524 | +0.000 | 0.930 | 37 |
| WhenDiagnosed | 0.91 | 0.333 | 0.333 | +0.000 | 1.000 | 0 |
