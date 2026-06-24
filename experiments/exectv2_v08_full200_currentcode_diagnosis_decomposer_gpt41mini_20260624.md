# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_v08_full200_currentcode_diagnosis_decomposer_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `full_200_authorized`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 489
- Diagnosis spans: 1068
- Mentions raw: 610
- Mentions scored: 610
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.708 | 0.731 | 0.686 | 302 | 111 | 138 |

## Source-Near Diagnostic

- Overlap F1=0.782 R=0.808
