# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_llm_diagnosis_verifier_v03_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.3`
- Pipeline family: `exectv2_llm_diagnosis_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 52
- Mentions raw: 42
- Mentions scored: 42
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.701 | 0.773 | 0.641 | 34 | 10 | 19 |

## Source-Near Diagnostic

- Overlap F1=0.755 R=0.661 (TP=37 FP=5 FN=19)
- Attribute agreement: 0.757 (28/37)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.592 | 0.691 | 0.518 | 0.927 | 29 | 13 | 27 |
| semantic | 0.490 | 0.571 | 0.429 | 0.872 | 24 | 18 | 32 |
| benchmark | 0.204 | 0.238 | 0.179 | 0.625 | 10 | 32 | 46 |