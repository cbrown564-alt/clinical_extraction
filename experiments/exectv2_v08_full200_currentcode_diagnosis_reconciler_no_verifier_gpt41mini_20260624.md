# ExECTv2 Diagnosis Decomposition Reconciler

- JSONL: `experiments\exectv2_v08_full200_currentcode_diagnosis_reconciler_no_verifier_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_reconciler_v0.2`
- Pipeline family: `exectv2_hybrid_diagnosis_reconciler`
- Split: `full_200_authorized`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Verifier candidate mentions: 0
- Decomposer candidate mentions: 610
- Diagnosis spans: 1068
- Mentions raw: 625
- Mentions scored: 622
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.9952

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.706 | 0.726 | 0.686 | 302 | 114 | 138 |

## Source-Near Diagnostic

- Overlap F1=0.779 R=0.813
