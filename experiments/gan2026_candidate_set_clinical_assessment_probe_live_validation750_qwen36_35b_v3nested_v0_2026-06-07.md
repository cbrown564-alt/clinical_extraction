# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_qwen36_35b_v3nested_v0_2026-06-07.resume-part.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 380
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 380/380
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 19
- `frequency_rate`: 206
- `seizure_free`: 89
- `unknown_frequency`: 66

## Aggregation Policies

- `additive_same_window`: 9
- `primary_with_context`: 59
- `seizure_free_state`: 1
- `single_fact`: 294
- `unknown_due_to_absence`: 3
- `unknown_due_to_ambiguity`: 14

## Row Notes

- No parse or validation errors.
