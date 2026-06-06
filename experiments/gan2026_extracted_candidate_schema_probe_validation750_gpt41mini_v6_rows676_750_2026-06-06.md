# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_rows676_750_2026-06-06.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v6`
- Split: `validation` / `gan2026_split_v1`
- Rows: 75
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 75/75
- Total candidates: 190
- Call failures: 0
- Parse/validation failure rows: 5
- Detail failure rows: 0
- Evidence error rows: 3
- Source phrase error rows: 2
- Rows with no candidates: 0

## Candidate Kinds

- `cluster_frequency`: 22
- `frequency_rate`: 112
- `last_event_only`: 28
- `seizure_free`: 9
- `unknown_frequency`: 19

## Row Notes

- 16408: candidate:llm:16408:3: evidence_not_exact
- 16757: candidate:llm:16757:3: source_phrase_not_exact
- 16758: candidate:llm:16758:2: evidence_not_exact
- 16824: candidate:llm:16824:2: source_phrase_not_exact
- 16867: candidate:llm:16867:2: evidence_not_exact
