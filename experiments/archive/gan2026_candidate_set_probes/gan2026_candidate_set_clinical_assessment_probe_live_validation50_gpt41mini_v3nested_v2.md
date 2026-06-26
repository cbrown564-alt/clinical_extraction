# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation50_gpt41mini_v3nested_v2.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v2`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 50/50
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 5
- `frequency_rate`: 43
- `unknown_frequency`: 2

## Aggregation Policies

- `cluster_axis`: 1
- `primary_with_context`: 9
- `single_fact`: 40

## Row Notes

- No parse or validation errors.
