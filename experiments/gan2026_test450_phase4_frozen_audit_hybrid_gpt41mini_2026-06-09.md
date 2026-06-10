# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v5`
- CandidateSet JSONL: `live`
- Split: `test` / `gan2026_split_v1`
- Rows: 450
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 450/450
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 45
- `frequency_rate`: 269
- `no_reference`: 19
- `seizure_free`: 75
- `unknown_frequency`: 42

## Aggregation Policies

- `additive_same_window`: 3
- `cluster_axis`: 1
- `no_reference_boundary`: 5
- `primary_with_context`: 118
- `seizure_free_state`: 27
- `single_fact`: 294
- `unknown_due_to_absence`: 2

## Row Notes

- No parse or validation errors.
