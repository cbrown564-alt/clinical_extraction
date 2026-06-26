# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_candidate_adjudicator_v02_dev25_diagnosis_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_candidate_adjudicator_v0.2`
- Pipeline family: `exectv2_hybrid_family_conditioned_candidate_adjudicator`
- Target family: `Diagnosis`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 3
- Clinical events raw: 45
- Mentions raw: 45
- Mentions scored: 45
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.688 | 0.800 | 0.604 | 32 | 8 | 21 |

- Ideal target F1: 0.800
- Current comparator F1: 0.658