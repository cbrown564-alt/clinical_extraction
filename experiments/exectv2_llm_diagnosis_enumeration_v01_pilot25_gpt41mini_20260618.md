# ExECTv2 Diagnosis Enumeration Recall Pass

- JSONL: `experiments\exectv2_llm_diagnosis_enumeration_v01_pilot25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_enumeration_v0.1`
- Pipeline family: `exectv2_llm_diagnosis_enumeration`
- Component owner: `llm_first`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Diagnosis spans: 89
- Mentions raw: 63
- Mentions scored: 63
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.771 | 0.750 | 0.792 | 42 | 14 | 11 |

## Source-Near Diagnostic

- Overlap F1=0.824 R=0.875
