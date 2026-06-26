# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_event_ledger_v03_dev5_investigations_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_event_ledger_v0.3`
- Pipeline family: `exectv2_hybrid_family_conditioned_event_ledger`
- Target family: `Investigations`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 7
- Mentions raw: 7
- Mentions scored: 7
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.933 | 1.000 | 0.875 | 7 | 0 | 1 |

- Ideal target F1: 0.800
- Current comparator F1: 0.872