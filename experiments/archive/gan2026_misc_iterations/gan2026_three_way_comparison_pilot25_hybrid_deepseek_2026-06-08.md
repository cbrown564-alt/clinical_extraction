# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_three_way_comparison_pilot25_hybrid_deepseek_2026-06-08.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 25/25
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 2
- `frequency_rate`: 20
- `unknown_frequency`: 3

## Aggregation Policies

- `cluster_axis`: 1
- `primary_with_context`: 1
- `single_fact`: 20
- `unknown_due_to_ambiguity`: 3

## Row Notes

- No parse or validation errors.
