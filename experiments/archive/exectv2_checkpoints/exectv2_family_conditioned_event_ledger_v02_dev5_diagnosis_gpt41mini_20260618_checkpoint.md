# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_event_ledger_v02_dev5_diagnosis_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_event_ledger_v0.2`
- Pipeline family: `exectv2_hybrid_family_conditioned_event_ledger`
- Target family: `Diagnosis`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 11
- Mentions raw: 10
- Mentions scored: 10
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.444 | 0.545 | 0.375 | 6 | 5 | 10 |

- Ideal target F1: 0.800
- Current comparator F1: 0.658