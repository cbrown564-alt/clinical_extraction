# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_2026-06-06.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v6`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 50/50
- Total candidates: 80
- Call failures: 0
- Parse/validation failure rows: 2
- Detail failure rows: 0
- Evidence error rows: 1
- Source phrase error rows: 1
- Rows with no candidates: 0

## Candidate Kinds

- `cluster_frequency`: 10
- `frequency_rate`: 51
- `last_event_only`: 7
- `seizure_free`: 2
- `unknown_frequency`: 10

## Row Notes

- 79: candidate:llm:79:2: evidence_not_exact
- 598: candidate:llm:598:1: source_phrase_not_exact
