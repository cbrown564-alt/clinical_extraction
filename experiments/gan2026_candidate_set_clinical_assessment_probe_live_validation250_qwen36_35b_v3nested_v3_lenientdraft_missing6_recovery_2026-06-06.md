# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_missing6_recovery_2026-06-06.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 6
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 6/6
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `frequency_rate`: 1
- `seizure_free`: 5

## Aggregation Policies

- `seizure_free_state`: 5
- `single_fact`: 1

## Row Notes

- No parse or validation errors.
