# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_llm_diagnosis_verifier_v06_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.6`
- Pipeline family: `exectv2_llm_diagnosis_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 325
- Mentions raw: 320
- Mentions scored: 317
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.9906

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.651 | 0.706 | 0.604 | 223 | 93 | 146 |

## Source-Near Diagnostic

- Overlap F1=0.737 R=0.657 (TP=266 FP=51 FN=139)
- Attribute agreement: 0.669 (178/266)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.601 | 0.684 | 0.536 | 0.952 | 217 | 100 | 188 |
| semantic | 0.413 | 0.470 | 0.368 | 0.881 | 149 | 168 | 256 |
| benchmark | 0.216 | 0.246 | 0.193 | 0.700 | 78 | 239 | 327 |