# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08.resume-part.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 190
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 190/190
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 15
- `frequency_rate`: 105
- `seizure_free`: 43
- `unknown_frequency`: 26
- `unresolved_multiple`: 1

## Aggregation Policies

- `additive_same_window`: 3
- `primary_with_context`: 14
- `seizure_free_state`: 43
- `single_fact`: 103
- `unknown_due_to_absence`: 2
- `unknown_due_to_ambiguity`: 25

## Row Notes

- No parse or validation errors.
