# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_llm_diagnosis_verifier_v01_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.1`
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
| 0.80 | 0.592 | 0.644 | 0.547 | 29 | 16 | 24 |

## Source-Near Diagnostic

- Overlap F1=0.694 R=0.607 (TP=34 FP=8 FN=22)
- Attribute agreement: 0.706 (24/34)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.653 | 0.762 | 0.571 | 0.905 | 32 | 10 | 24 |
| semantic | 0.449 | 0.524 | 0.393 | 0.757 | 22 | 20 | 34 |
| benchmark | 0.163 | 0.191 | 0.143 | 0.516 | 8 | 34 | 48 |