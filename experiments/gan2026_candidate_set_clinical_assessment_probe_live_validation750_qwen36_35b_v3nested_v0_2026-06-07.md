# Gan 2026 CandidateSet Clinical Assessment Probe

- JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_qwen36_35b_v3nested_v0_2026-06-07.jsonl`
- Pipeline: `llm_candidate_set_clinical_assessment_probe`
- Prompt/schema version: `gan2026_candidate_set_clinical_assessment_probe_v3`
- CandidateSet JSONL: `experiments\gan2026_validation750_candidate_set_v3_nested_dedupe_2026-06-06.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: clinical-assessment schema-fit probe only; no score calculation and no rendered answers.

## Summary

- Clinical assessment rows: 749/750
- Call failures: 0
- Parse/validation failure rows: 1
- Missing candidate-set rows: 0

## Assessment Kinds

- `cluster_frequency`: 77
- `frequency_rate`: 387
- `no_reference`: 17
- `seizure_free`: 140
- `unknown_frequency`: 128

## Aggregation Policies

- `additive_same_window`: 40
- `cluster_axis`: 1
- `no_reference_boundary`: 17
- `primary_with_context`: 126
- `seizure_free_state`: 1
- `single_fact`: 518
- `unknown_due_to_absence`: 17
- `unknown_due_to_ambiguity`: 29

## Row Notes

- 12438: supporting_candidate_ids:unknown_candidate_id:llm:1248:2
