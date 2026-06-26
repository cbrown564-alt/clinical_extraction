# Gan 2026 CandidateSet Selector Schema Probe

- JSONL: `experiments\gan2026_validation250_selected_fact_v0_v2_high_recall.jsonl`
- Pipeline: `llm_candidate_set_selector_schema_probe`
- Prompt/schema version: `gan2026_candidate_set_selector_schema_probe_v0`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v2_high_recall.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: selector schema-fit probe only; no scoring and no final labels.

## Summary

- Selected fact rows: 248/250
- Call failures: 0
- Parse/validation failure rows: 2
- Missing candidate-set rows: 0

## Selection Status

- `no_reliable_candidate`: 8
- `selected`: 240

## Selection Basis

- `absence_of_evidence`: 8
- `candidate_combination`: 1
- `direct_candidate_selection`: 239

## Row Notes

- 2427: Value error, ambiguous must not select candidate ids
- 3528: Value error, selected unknown_frequency facts require an explicit unknown_basis
