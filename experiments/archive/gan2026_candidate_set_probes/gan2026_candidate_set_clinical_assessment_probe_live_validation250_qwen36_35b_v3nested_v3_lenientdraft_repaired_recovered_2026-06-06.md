# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_2026-06-06.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 250/250
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 8
- `frequency_rate`: 158
- `seizure_free`: 43
- `unknown_frequency`: 41

## Aggregation Policies

- `additive_same_window`: 7
- `cluster_axis`: 1
- `primary_with_context`: 56
- `seizure_free_state`: 27
- `single_fact`: 126
- `unknown_due_to_absence`: 14
- `unknown_due_to_ambiguity`: 19

## Row Notes

- No parse or validation errors.
