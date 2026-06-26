# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v3nested_v1.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v1`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`
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
- `frequency_rate`: 23

## Aggregation Policies

- `cluster_axis`: 1
- `primary_with_context`: 6
- `single_fact`: 18

## Row Notes

- No parse or validation errors.
