# Gan 2026 CandidateSet Selector Schema Probe

- JSONL: `experiments\gan2026_validation250_selected_candidate_decision_v2_v2_high_recall.jsonl`
- Pipeline: `llm_candidate_set_selector_schema_probe`
- Prompt/schema version: `gan2026_candidate_set_selector_schema_probe_v2`
- CandidateSet JSONL: `experiments\gan2026_validation250_candidate_set_v2_high_recall.jsonl`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: selector schema-fit probe only; no scoring and no final labels.

## Summary

- Selected decision rows: 250/250
- Call failures: 0
- Parse/validation failure rows: 0
- Missing candidate-set rows: 0

## Selection Mode

- `no_reliable_candidate`: 3
- `related_candidate_group`: 21
- `single_candidate`: 226

## Row Notes

- No parse or validation errors.
