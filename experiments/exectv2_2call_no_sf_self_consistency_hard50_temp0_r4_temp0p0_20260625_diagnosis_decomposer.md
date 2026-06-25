# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r4_temp0p0_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `hard50_temp0`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 115
- Diagnosis spans: 267
- Mentions raw: 158
- Mentions scored: 158
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.806 | 0.794 | 0.818 | 81 | 21 | 18 |

## Source-Near Diagnostic

- Overlap F1=0.826 R=0.879
