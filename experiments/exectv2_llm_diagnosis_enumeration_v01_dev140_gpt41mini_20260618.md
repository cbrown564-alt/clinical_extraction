# ExECTv2 Diagnosis Enumeration Recall Pass

- JSONL: `experiments\exectv2_llm_diagnosis_enumeration_v01_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_diagnosis_enumeration_v0.1`
- Pipeline family: `exectv2_llm_diagnosis_enumeration`
- Component owner: `llm_first`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Diagnosis spans: 606
- Mentions raw: 426
- Mentions scored: 424
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9953

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.615 | 0.620 | 0.610 | 225 | 138 | 144 |

## Source-Near Diagnostic

- Overlap F1=0.748 R=0.765
