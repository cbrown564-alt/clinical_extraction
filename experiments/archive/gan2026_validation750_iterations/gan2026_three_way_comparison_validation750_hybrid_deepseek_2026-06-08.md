# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 750/750
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 64
- `frequency_rate`: 412
- `no_reference`: 26
- `seizure_free`: 145
- `unknown_frequency`: 101
- `unresolved_multiple`: 2

## Aggregation Policies

- `additive_same_window`: 31
- `cluster_axis`: 10
- `no_reference_boundary`: 26
- `primary_with_context`: 82
- `seizure_free_state`: 143
- `single_fact`: 355
- `unknown_due_to_absence`: 5
- `unknown_due_to_ambiguity`: 98

## Row Notes

- No parse or validation errors.
