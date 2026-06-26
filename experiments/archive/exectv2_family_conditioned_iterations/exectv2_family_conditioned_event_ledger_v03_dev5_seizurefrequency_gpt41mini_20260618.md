# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_event_ledger_v03_dev5_seizurefrequency_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_event_ledger_v0.3`
- Pipeline family: `exectv2_hybrid_family_conditioned_event_ledger`
- Target family: `SeizureFrequency`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 11
- Mentions raw: 11
- Mentions scored: 8
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.7273

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.737 | 0.875 | 0.636 | 7 | 1 | 4 |

- Ideal target F1: 0.800
- Current comparator F1: 0.782