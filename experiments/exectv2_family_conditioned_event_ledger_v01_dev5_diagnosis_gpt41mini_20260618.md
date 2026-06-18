# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_event_ledger_v01_dev5_diagnosis_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_event_ledger_v0.1`
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
- Mentions raw: 8
- Mentions scored: 8
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.222 | 0.273 | 0.188 | 3 | 8 | 13 |

- Ideal target F1: 0.800
- Current comparator F1: 0.658