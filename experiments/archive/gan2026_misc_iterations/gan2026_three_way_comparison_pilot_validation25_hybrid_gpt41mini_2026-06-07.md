# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_three_way_comparison_pilot_validation25_hybrid_gpt41mini_2026-06-07.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v2_high_recall.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 25/25
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 2
- `frequency_rate`: 22
- `unknown_frequency`: 1

## Aggregation Policies

- `primary_with_context`: 8
- `single_fact`: 17

## Row Notes

- No parse or validation errors.
