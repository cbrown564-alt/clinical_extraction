# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_test450_gpt41mini_v3nested_v3_2026-06-07.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_test450_candidate_set_v3_nested_dedupe_context_v1_2026-06-07.jsonl`
- Split: `test` / `gan2026_split_v1`
- Rows: 450
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 449/450
- Call failures: 0
- Parse/validation failure rows: 1
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 44
- `frequency_rate`: 262
- `no_reference`: 18
- `seizure_free`: 83
- `unknown_frequency`: 42

## Aggregation Policies

- `additive_same_window`: 14
- `no_reference_boundary`: 11
- `primary_with_context`: 128
- `seizure_free_state`: 5
- `single_fact`: 285
- `unknown_due_to_absence`: 6

## Row Notes

- 13167: supporting_candidate_ids:unknown_candidate_id:llm:13167:6
