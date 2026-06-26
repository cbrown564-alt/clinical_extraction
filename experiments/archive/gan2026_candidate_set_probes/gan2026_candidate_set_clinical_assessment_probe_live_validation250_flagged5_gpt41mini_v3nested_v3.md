# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_gpt41mini_v3nested_v3.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 5
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 5/5
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 2
- `frequency_rate`: 1
- `unknown_frequency`: 2

## Aggregation Policies

- `primary_with_context`: 4
- `unknown_due_to_absence`: 1

## Row Notes

- No parse or validation errors.
