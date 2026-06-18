# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_event_ledger_v01_dev5_prescription_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_event_ledger_v0.1`
- Pipeline family: `exectv2_hybrid_family_conditioned_event_ledger`
- Target family: `Prescription`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 8
- Mentions raw: 9
- Mentions scored: 8
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.8889

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.875 | 1.000 | 0.778 | 7 | 0 | 2 |

- Ideal target F1: 0.800
- Current comparator F1: 0.817