# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_hybrid_v5_validation750_gpt41mini_2026-06-09.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v5`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 749/750
- Call failures: 0
- Parse/validation failure rows: 1
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 77
- `frequency_rate`: 431
- `no_reference`: 29
- `seizure_free`: 131
- `unknown_frequency`: 81

## Aggregation Policies

- `additive_same_window`: 3
- `cluster_axis`: 6
- `no_reference_boundary`: 11
- `primary_with_context`: 218
- `seizure_free_state`: 35
- `single_fact`: 470
- `unknown_due_to_absence`: 6

## Row Notes

- 12502: supporting_candidate_ids:unknown_candidate_id:llm:12502:4
