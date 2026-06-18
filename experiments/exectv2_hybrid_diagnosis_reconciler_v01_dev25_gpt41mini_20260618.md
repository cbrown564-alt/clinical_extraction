# ExECTv2 Diagnosis Decomposition Reconciler

- JSONL: `experiments\exectv2_hybrid_diagnosis_reconciler_v01_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_reconciler_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_reconciler`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Verifier candidate mentions: 51
- Decomposer candidate mentions: 69
- Diagnosis spans: 120
- Mentions raw: 64
- Mentions scored: 64
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.833 | 0.818 | 0.849 | 45 | 10 | 8 |

## Source-Near Diagnostic

- Overlap F1=0.867 R=0.929
