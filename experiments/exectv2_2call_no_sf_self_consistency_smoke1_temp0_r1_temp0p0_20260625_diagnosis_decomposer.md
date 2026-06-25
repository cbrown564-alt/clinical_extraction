# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_smoke1_temp0_r1_temp0p0_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `smoke1_temp0`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 2
- Diagnosis spans: 5
- Mentions raw: 3
- Mentions scored: 3
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.400 | 0.500 | 0.333 | 1 | 1 | 2 |

## Source-Near Diagnostic

- Overlap F1=0.857 R=0.750
