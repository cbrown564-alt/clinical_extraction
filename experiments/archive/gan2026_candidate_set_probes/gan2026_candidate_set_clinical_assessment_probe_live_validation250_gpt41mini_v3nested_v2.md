# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v2`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 247/250
- Call failures: 0
- Parse/validation failure rows: 3
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 22
- `frequency_rate`: 167
- `seizure_free`: 41
- `unknown_frequency`: 17

## Aggregation Policies

- `additive_same_window`: 3
- `cluster_axis`: 2
- `no_reference_boundary`: 1
- `primary_with_context`: 41
- `seizure_free_state`: 14
- `single_fact`: 185
- `unknown_due_to_absence`: 1

## Row Notes

- 1363: Value error, supporting_candidate_ids and rejected_candidate_ids overlap
- 3532: Value error, frequency_rate requires primary_candidate_ids
- 5567: rejected_candidate_ids:unknown_candidate_id:llm:5567:5
