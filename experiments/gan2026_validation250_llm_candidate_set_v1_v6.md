# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_validation250_llm_candidate_set_v1_v6.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v6`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 249/250
- Total candidates: 383
- Call failures: 1
- Parse/validation failure rows: 12
- Detail failure rows: 0
- Evidence error rows: 9
- Source phrase error rows: 10
- Rows with no candidates: 4

## Candidate Kinds

- `cluster_frequency`: 37
- `frequency_rate`: 202
- `last_event_only`: 22
- `seizure_free`: 55
- `unknown_frequency`: 67

## Row Notes

- 1591: candidate:llm:1591:1: source_phrase_not_exact
- 1880: candidate:llm:1880:2: evidence_not_exact; candidate:llm:1880:2: source_phrase_not_exact
- 1923: candidate:llm:1923:1: source_phrase_not_exact
- 2628: candidate:llm:2628:2: evidence_not_exact
- 3532: not_run
- 3534: candidate:llm:3534:1: evidence_not_exact; candidate:llm:3534:1: source_phrase_not_exact
- 3791: candidate:llm:3791:1: evidence_not_exact; candidate:llm:3791:1: source_phrase_not_exact
- 3801: candidate:llm:3801:1: evidence_not_exact; candidate:llm:3801:1: source_phrase_not_exact
- 4562: candidate:llm:4562:1: evidence_not_exact; candidate:llm:4562:1: source_phrase_not_exact
- 4574: candidate:llm:4574:1: evidence_not_exact; candidate:llm:4574:1: source_phrase_not_exact
- 4592: candidate:llm:4592:1: evidence_not_exact; candidate:llm:4592:1: source_phrase_not_exact
- 4597: candidate:llm:4597:1: evidence_not_exact; candidate:llm:4597:1: source_phrase_not_exact; candidate:llm:4597:2: evidence_not_exact; candidate:llm:4597:2: source_phrase_not_exact
