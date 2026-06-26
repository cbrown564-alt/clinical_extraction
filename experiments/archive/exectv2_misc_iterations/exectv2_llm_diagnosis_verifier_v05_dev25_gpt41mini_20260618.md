# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_llm_diagnosis_verifier_v05_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.5`
- Pipeline family: `exectv2_llm_diagnosis_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 52
- Mentions raw: 44
- Mentions scored: 44
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.837 | 0.911 | 0.774 | 41 | 4 | 12 |

## Source-Near Diagnostic

- Overlap F1=0.840 R=0.750 (TP=42 FP=2 FN=14)
- Attribute agreement: 0.809 (34/42)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.740 | 0.841 | 0.661 | 0.977 | 37 | 7 | 19 |
| semantic | 0.620 | 0.705 | 0.554 | 0.952 | 31 | 13 | 25 |
| benchmark | 0.240 | 0.273 | 0.214 | 0.706 | 12 | 32 | 44 |