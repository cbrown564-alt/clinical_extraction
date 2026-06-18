# ExECTv2 Diagnosis Candidate Acceptance Gate

- JSONL: `experiments\exectv2_hybrid_diagnosis_acceptance_gate_v01_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_acceptance_gate_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_acceptance_gate`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Candidate mentions: 87
- Accepted candidates: 42
- Mentions scored: 42
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.625 | 0.698 | 0.566 | 30 | 13 | 23 |

## Source-Near Diagnostic

- Overlap F1=0.653 R=0.571
