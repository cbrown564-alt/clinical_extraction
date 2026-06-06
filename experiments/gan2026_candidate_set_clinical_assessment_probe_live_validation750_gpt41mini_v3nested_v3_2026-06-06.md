# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 100
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 100/100
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 7
- `frequency_rate`: 85
- `seizure_free`: 1
- `unknown_frequency`: 7

## Aggregation Policies

- `additive_same_window`: 4
- `primary_with_context`: 25
- `single_fact`: 71

## Row Notes

- No parse or validation errors.
