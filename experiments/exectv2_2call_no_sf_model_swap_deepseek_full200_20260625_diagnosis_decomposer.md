# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_full200_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `full200`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Draft Diagnosis mentions: 492
- Diagnosis spans: 1074
- Mentions raw: 634
- Mentions scored: 630
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9937

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.738 | 0.736 | 0.741 | 326 | 117 | 114 |

## Source-Near Diagnostic

- Overlap F1=0.824 R=0.865
