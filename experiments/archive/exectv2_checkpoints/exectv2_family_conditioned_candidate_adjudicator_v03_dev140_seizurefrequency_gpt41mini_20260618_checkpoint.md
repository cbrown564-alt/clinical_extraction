# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_candidate_adjudicator_v03_dev140_seizurefrequency_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_candidate_adjudicator_v0.3`
- Pipeline family: `exectv2_hybrid_family_conditioned_candidate_adjudicator`
- Target family: `SeizureFrequency`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 206
- Mentions raw: 206
- Mentions scored: 206
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.697 | 0.665 | 0.733 | 137 | 69 | 50 |

- Ideal target F1: 0.800
- Current comparator F1: 0.782