# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_llm_diagnosis_verifier_v04_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.4`
- Pipeline family: `exectv2_llm_diagnosis_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 52
- Mentions raw: 45
- Mentions scored: 45
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.768 | 0.826 | 0.717 | 38 | 8 | 15 |

## Source-Near Diagnostic

- Overlap F1=0.792 R=0.714 (TP=40 FP=5 FN=16)
- Attribute agreement: 0.800 (32/40)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.673 | 0.756 | 0.607 | 0.977 | 34 | 11 | 22 |
| semantic | 0.554 | 0.622 | 0.500 | 0.952 | 28 | 17 | 28 |
| benchmark | 0.238 | 0.267 | 0.214 | 0.706 | 12 | 33 | 44 |