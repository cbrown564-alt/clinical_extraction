# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 749/750
- Call failures: 0
- Parse/validation failure rows: 1
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 81
- `frequency_rate`: 429
- `no_reference`: 30
- `seizure_free`: 141
- `unknown_frequency`: 68

## Aggregation Policies

- `additive_same_window`: 35
- `cluster_axis`: 3
- `no_reference_boundary`: 19
- `primary_with_context`: 223
- `seizure_free_state`: 11
- `single_fact`: 451
- `unknown_due_to_absence`: 6
- `unknown_due_to_ambiguity`: 1

## Row Notes

- 6607: Value error, frequency_rate requires primary_candidate_ids
