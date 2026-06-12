# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_three_way_comparison_validation750_hybrid_qwen3635b_2026-06-08.resume-part.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 500
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 500/500
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 55
- `frequency_rate`: 220
- `no_reference`: 24
- `seizure_free`: 100
- `unknown_frequency`: 101

## Aggregation Policies

- `additive_same_window`: 32
- `cluster_axis`: 3
- `no_reference_boundary`: 24
- `primary_with_context`: 105
- `seizure_free_state`: 1
- `single_fact`: 307
- `unknown_due_to_absence`: 7
- `unknown_due_to_ambiguity`: 21

## Row Notes

- No parse or validation errors.
