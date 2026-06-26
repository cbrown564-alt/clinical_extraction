# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_extracted_candidate_schema_probe_validation15_gpt41mini_v4_2026-06-05.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v4`
- Split: `validation` / `gan2026_split_v1`
- Rows: 15
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 15/15
- Total candidates: 22
- Call failures: 0
- Parse/validation failure rows: 1
- Detail failure rows: 0
- Evidence error rows: 1
- Source phrase error rows: 1
- Rows with no candidates: 0

## Candidate Kinds

- `cluster_frequency`: 3
- `frequency_rate`: 17
- `last_event_only`: 2

## Row Notes

- 79: candidate:llm:79:1: evidence_not_exact; candidate:llm:79:1: source_phrase_not_exact; candidate:llm:79:2: evidence_not_exact; candidate:llm:79:2: source_phrase_not_exact
