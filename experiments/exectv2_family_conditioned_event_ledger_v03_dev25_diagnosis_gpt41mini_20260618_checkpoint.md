# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_event_ledger_v03_dev25_diagnosis_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_event_ledger_v0.3`
- Pipeline family: `exectv2_hybrid_family_conditioned_event_ledger`
- Target family: `Diagnosis`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 34
- Mentions raw: 37
- Mentions scored: 36
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9730

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.405 | 0.500 | 0.340 | 18 | 18 | 35 |

- Ideal target F1: 0.800
- Current comparator F1: 0.658