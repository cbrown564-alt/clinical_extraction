# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r4_temp1p0_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `entropy_dev140_temps`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 348
- Diagnosis spans: 774
- Mentions raw: 422
- Mentions scored: 422
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.703 | 0.718 | 0.688 | 209 | 82 | 95 |

## Source-Near Diagnostic

- Overlap F1=0.759 R=0.775
