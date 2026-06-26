# ExECTv2 Diagnosis Decomposition Reconciler

- JSONL: `experiments\exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_reconciler_v0.2`
- Pipeline family: `exectv2_hybrid_diagnosis_reconciler`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Verifier candidate mentions: 317
- Decomposer candidate mentions: 462
- Diagnosis spans: 812
- Mentions raw: 451
- Mentions scored: 449
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9956

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.647 | 0.636 | 0.658 | 243 | 139 | 126 |

## Source-Near Diagnostic

- Overlap F1=0.777 R=0.820
