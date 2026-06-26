# ExECTv2 Family-Conditioned Event Ledger

- JSONL: `experiments\exectv2_family_conditioned_candidate_adjudicator_v05_dev140_prescription_qwen36_35b_strict_actions_20260623.jsonl`
- Prompt version: `exectv2_hybrid_family_conditioned_candidate_adjudicator_v0.4`
- Pipeline family: `exectv2_hybrid_family_conditioned_candidate_adjudicator`
- Target family: `Prescription`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live-actions-strict`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 0
- Mentions raw: 196
- Mentions scored: 196
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Clinical Recovery

| Metric | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target headline | 0.922 | 0.927 | 0.917 | 177 | 14 | 16 |

- Ideal target F1: 0.800
- Current comparator F1: 0.817