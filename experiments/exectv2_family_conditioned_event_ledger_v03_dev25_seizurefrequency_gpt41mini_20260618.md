# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_event_ledger_v03_dev25_seizurefrequency_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_event_ledger_v0.3`
- Pipeline family: `exectv2_hybrid_family_conditioned_event_ledger`
- Target family: `SeizureFrequency`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 33
- Mentions raw: 32
- Mentions scored: 25
- Evidence-invalid dropped: 7
- Evidence validity rate: 0.7812

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.429 | 0.480 | 0.387 | 12 | 13 | 19 |

- Ideal target F1: 0.800
- Current comparator F1: 0.782