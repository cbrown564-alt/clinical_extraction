# ExECTv2 Diagnosis Verifier

- JSONL: `experiments\exectv2_llm_diagnosis_verifier_v05_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_verifier_v0.5`
- Pipeline family: `exectv2_llm_diagnosis_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 325
- Mentions raw: 297
- Mentions scored: 292
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9832

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.616 | 0.680 | 0.564 | 208 | 98 | 161 |

## Source-Near Diagnostic

- Overlap F1=0.692 R=0.595 (TP=241 FP=51 FN=164)
- Attribute agreement: 0.643 (155/241)

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.551 | 0.657 | 0.474 | 0.948 | 192 | 100 | 213 |
| semantic | 0.361 | 0.431 | 0.311 | 0.852 | 126 | 166 | 279 |
| benchmark | 0.189 | 0.226 | 0.163 | 0.660 | 66 | 226 | 339 |