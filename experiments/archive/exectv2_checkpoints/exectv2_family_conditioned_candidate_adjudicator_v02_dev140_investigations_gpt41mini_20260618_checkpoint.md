# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_candidate_adjudicator_v02_dev140_investigations_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_candidate_adjudicator_v0.2`
- Pipeline family: `exectv2_hybrid_family_conditioned_candidate_adjudicator`
- Target family: `Investigations`
- Split: `dev`
- Model: `gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 128
- Mentions raw: 124
- Mentions scored: 123
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9919

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.892 | 0.935 | 0.853 | 116 | 8 | 20 |

- Ideal target F1: 0.800
- Current comparator F1: 0.872