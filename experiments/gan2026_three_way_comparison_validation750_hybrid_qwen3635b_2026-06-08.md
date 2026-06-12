# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_three_way_comparison_validation750_hybrid_qwen3635b_2026-06-08.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 750/750
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 68
- `frequency_rate`: 378
- `no_reference`: 24
- `seizure_free`: 139
- `unknown_frequency`: 141

## Aggregation Policies

- `additive_same_window`: 36
- `cluster_axis`: 3
- `no_reference_boundary`: 24
- `primary_with_context`: 140
- `seizure_free_state`: 2
- `single_fact`: 509
- `unknown_due_to_absence`: 10
- `unknown_due_to_ambiguity`: 26

## Row Notes

- No parse or validation errors.
