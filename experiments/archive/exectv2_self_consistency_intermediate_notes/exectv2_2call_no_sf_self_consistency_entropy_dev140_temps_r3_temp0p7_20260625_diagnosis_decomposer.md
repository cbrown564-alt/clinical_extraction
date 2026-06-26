# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r3_temp0p7_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `entropy_dev140_temps`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 334
- Diagnosis spans: 762
- Mentions raw: 417
- Mentions scored: 416
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9976

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.708 | 0.727 | 0.691 | 210 | 79 | 94 |

## Source-Near Diagnostic

- Overlap F1=0.779 R=0.790
