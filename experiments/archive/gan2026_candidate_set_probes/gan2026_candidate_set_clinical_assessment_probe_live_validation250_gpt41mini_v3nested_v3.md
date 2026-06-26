# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v3.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 250/250
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 19
- `frequency_rate`: 171
- `seizure_free`: 41
- `unknown_frequency`: 19

## Aggregation Policies

- `additive_same_window`: 3
- `cluster_axis`: 2
- `primary_with_context`: 59
- `seizure_free_state`: 15
- `single_fact`: 167
- `unknown_due_to_absence`: 4

## Row Notes

- No parse or validation errors.
