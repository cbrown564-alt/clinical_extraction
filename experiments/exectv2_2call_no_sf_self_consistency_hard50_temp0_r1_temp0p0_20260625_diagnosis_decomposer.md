# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r1_temp0p0_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `hard50_temp0`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 117
- Diagnosis spans: 267
- Mentions raw: 157
- Mentions scored: 157
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.784 | 0.762 | 0.808 | 80 | 25 | 19 |

## Source-Near Diagnostic

- Overlap F1=0.822 R=0.871
