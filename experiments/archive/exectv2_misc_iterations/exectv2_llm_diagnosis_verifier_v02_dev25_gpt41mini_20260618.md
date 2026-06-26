# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_llm_diagnosis_verifier_v02_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.2`
- Pipeline family: `exectv2_llm_diagnosis_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 52
- Mentions raw: 43
- Mentions scored: 43
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.619 | 0.682 | 0.566 | 30 | 14 | 23 |

## Source-Near Diagnostic

- Overlap F1=0.727 R=0.643 (TP=36 FP=7 FN=20)
- Attribute agreement: 0.722 (26/36)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.566 | 0.651 | 0.500 | 0.952 | 28 | 15 | 28 |
| semantic | 0.424 | 0.488 | 0.375 | 0.842 | 21 | 22 | 35 |
| benchmark | 0.202 | 0.233 | 0.179 | 0.625 | 10 | 33 | 46 |