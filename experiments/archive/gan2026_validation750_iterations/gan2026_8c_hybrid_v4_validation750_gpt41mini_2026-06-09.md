# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_8c_hybrid_v4_validation750_gpt41mini_2026-06-09.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v4`
- CandidateSet JSONL: `live`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 748/750
- Call failures: 0
- Parse/validation failure rows: 2
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 82
- `frequency_rate`: 420
- `no_reference`: 32
- `seizure_free`: 146
- `unknown_frequency`: 68

## Aggregation Policies

- `additive_same_window`: 26
- `cluster_axis`: 5
- `no_reference_boundary`: 21
- `primary_with_context`: 215
- `seizure_free_state`: 60
- `single_fact`: 415
- `unknown_due_to_absence`: 6

## Row Notes

- 12484: supporting_candidate_ids:unknown_candidate_id:llm:12484:6
- 12665: supporting_candidate_ids:unknown_candidate_id:llm:12665:6
