# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 732/750
- Call failures: 0
- Parse/validation failure rows: 18
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 82
- `frequency_rate`: 412
- `no_reference`: 25
- `seizure_free`: 141
- `unknown_frequency`: 71
- `unresolved_multiple`: 1

## Aggregation Policies

- `additive_same_window`: 33
- `cluster_axis`: 2
- `no_reference_boundary`: 22
- `primary_with_context`: 196
- `seizure_free_state`: 45
- `single_fact`: 425
- `unknown_due_to_absence`: 9

## Row Notes

- 7196: Value error, supporting_candidate_ids and rejected_candidate_ids overlap
- 8079: Value error, primary_candidate_ids and supporting_candidate_ids overlap
- 8355: Value error, candidate ids must be unique within each role
- 9496: Value error, candidate ids must be unique within each role
- 11118: Value error, candidate ids must be unique within each role
- 11350: Value error, candidate ids must be unique within each role
- 12412: Value error, candidate ids must be unique within each role
- 12502: Value error, candidate ids must be unique within each role
- 12548: Value error, supporting_candidate_ids and rejected_candidate_ids overlap
- 12665: Value error, candidate ids must be unique within each role
- 12667: Value error, candidate ids must be unique within each role
- 12679: Value error, primary_candidate_ids and supporting_candidate_ids overlap
- 12749: Value error, candidate ids must be unique within each role
- 12751: Value error, candidate ids must be unique within each role
- 15021: Value error, candidate ids must be unique within each role
- 15513: Value error, candidate ids must be unique within each role
- 15802: Value error, candidate ids must be unique within each role
- 16757: Value error, primary_candidate_ids and supporting_candidate_ids overlap
