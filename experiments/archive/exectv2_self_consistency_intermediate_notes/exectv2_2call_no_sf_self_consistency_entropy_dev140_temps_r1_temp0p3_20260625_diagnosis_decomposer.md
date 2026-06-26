# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `entropy_dev140_temps`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 332
- Diagnosis spans: 773
- Mentions raw: 419
- Mentions scored: 418
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9976

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.716 | 0.755 | 0.681 | 207 | 67 | 97 |

## Source-Near Diagnostic

- Overlap F1=0.763 R=0.775
