# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_dev140_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `dev140`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Draft Diagnosis mentions: 337
- Diagnosis spans: 770
- Mentions raw: 440
- Mentions scored: 437
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.9932

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.745 | 0.740 | 0.750 | 228 | 80 | 76 |

## Source-Near Diagnostic

- Overlap F1=0.815 R=0.847
