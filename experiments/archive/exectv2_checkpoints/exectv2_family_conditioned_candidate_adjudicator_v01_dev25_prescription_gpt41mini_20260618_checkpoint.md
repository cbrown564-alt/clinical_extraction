# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_candidate_adjudicator_v01_dev25_prescription_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_candidate_adjudicator_v0.1`
- Pipeline family: `exectv2_hybrid_family_conditioned_candidate_adjudicator`
- Target family: `Prescription`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 33
- Mentions raw: 39
- Mentions scored: 39
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.961 | 0.949 | 0.974 | 37 | 2 | 1 |

- Ideal target F1: 0.800
- Current comparator F1: 0.817