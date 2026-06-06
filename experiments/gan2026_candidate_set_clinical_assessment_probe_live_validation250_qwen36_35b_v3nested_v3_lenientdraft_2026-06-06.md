# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_2026-06-06.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 150
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 146/150
- Call failures: 4
- Parse/validation failure rows: 4
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 8
- `frequency_rate`: 110
- `seizure_free`: 12
- `unknown_frequency`: 16

## Aggregation Policies

- `additive_same_window`: 10
- `cluster_axis`: 7
- `primary_with_context`: 32
- `seizure_free_state`: 8
- `single_fact`: 76
- `unknown_due_to_absence`: 1
- `unknown_due_to_ambiguity`: 12

## Row Notes

- 531: not_run; assessment_draft_missing
- 1695: not_run; assessment_draft_missing
- 2932: not_run; assessment_draft_missing
- 2938: not_run; assessment_draft_missing
