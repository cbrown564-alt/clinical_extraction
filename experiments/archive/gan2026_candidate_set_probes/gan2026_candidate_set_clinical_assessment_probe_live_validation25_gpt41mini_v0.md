# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v0.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v0`
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
- `frequency_rate`: 21
- `unknown_frequency`: 2

## Aggregation Policies

- `primary_with_context`: 10
- `single_fact`: 15

## Row Notes

- No parse or validation errors.
