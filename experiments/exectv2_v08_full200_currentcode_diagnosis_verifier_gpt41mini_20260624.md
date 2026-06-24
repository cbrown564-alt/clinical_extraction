# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_v08_full200_currentcode_diagnosis_verifier_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.6`
- Pipeline family: `exectv2_llm_diagnosis_verifier`
- Split: `full_200_authorized`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 489
- Mentions raw: 471
- Mentions scored: 465
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9873

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.710 | 0.748 | 0.675 | 297 | 100 | 143 |

## Source-Near Diagnostic

- Overlap F1=0.781 R=0.708 (TP=405 FP=60 FN=167)
- Attribute agreement: 0.891 (361/405)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.623 | 0.695 | 0.565 | 0.936 | 323 | 142 | 249 |
| semantic | 0.582 | 0.649 | 0.528 | 0.923 | 302 | 163 | 270 |
| benchmark | 0.536 | 0.598 | 0.486 | 0.917 | 278 | 187 | 294 |