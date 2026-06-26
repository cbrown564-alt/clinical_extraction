# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_validation250_llm_candidate_set_v0.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v5`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 248/250
- Total candidates: 358
- Call failures: 2
- Parse/validation failure rows: 18
- Detail failure rows: 0
- Evidence error rows: 8
- Source phrase error rows: 15
- Rows with no candidates: 6

## Candidate Kinds

- `cluster_frequency`: 36
- `frequency_rate`: 252
- `last_event_only`: 22
- `no_reference`: 2
- `seizure_free`: 44
- `unknown_frequency`: 2

## Row Notes

- 598: candidate:llm:598:1: source_phrase_not_exact
- 1486: candidate:llm:1486:1: source_phrase_not_exact
- 1591: candidate:llm:1591:1: source_phrase_not_exact
- 1794: candidate:llm:1794:1: source_phrase_not_exact
- 1880: candidate:llm:1880:1: evidence_not_exact; candidate:llm:1880:2: source_phrase_not_exact
- 1923: candidate:llm:1923:1: source_phrase_not_exact
- 1980: candidate:llm:1980:1: source_phrase_not_exact
- 2628: candidate:llm:2628:2: evidence_not_exact
- 2759: candidate:llm:2759:1: source_phrase_not_exact
- 3532: not_run
- 3534: candidate:llm:3534:1: source_phrase_not_exact
- 3791: candidate:llm:3791:1: evidence_not_exact; candidate:llm:3791:1: source_phrase_not_exact
- 3801: candidate:llm:3801:1: evidence_not_exact; candidate:llm:3801:1: source_phrase_not_exact
- 4562: candidate:llm:4562:1: evidence_not_exact; candidate:llm:4562:1: source_phrase_not_exact
- 4574: candidate:llm:4574:1: evidence_not_exact; candidate:llm:4574:1: source_phrase_not_exact
- 4592: candidate:llm:4592:1: evidence_not_exact; candidate:llm:4592:1: source_phrase_not_exact
- 4597: candidate:llm:4597:1: evidence_not_exact; candidate:llm:4597:1: source_phrase_not_exact
- 5551: not_run
