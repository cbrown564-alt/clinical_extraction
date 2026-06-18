# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_candidate_adjudicator_v01_dev25_diagnosis_passthrough_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_candidate_adjudicator_v0.1`
- Pipeline family: `exectv2_hybrid_family_conditioned_candidate_adjudicator`
- Target family: `Diagnosis`
- Split: `dev`
- Model: `candidate-passthrough`
- Mode: `candidate-passthrough`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 0
- Mentions raw: 64
- Mentions scored: 64
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.833 | 0.818 | 0.849 | 45 | 10 | 8 |

- Ideal target F1: 0.800
- Current comparator F1: 0.658