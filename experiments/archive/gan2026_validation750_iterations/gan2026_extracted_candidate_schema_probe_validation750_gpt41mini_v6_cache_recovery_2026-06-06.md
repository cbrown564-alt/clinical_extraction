# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_extracted_candidate_schema_probe_validation750_gpt41mini_v6_cache_recovery_2026-06-06.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v6`
- Split: `validation` / `gan2026_split_v1`
- Rows: 582
- Model: `openai/gpt-4.1-mini`
- Mode: `cache-recovery`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 582/582
- Total candidates: 1092
- Call failures: 0
- Parse/validation failure rows: 24
- Detail failure rows: 0
- Evidence error rows: 12
- Source phrase error rows: 17
- Rows with no candidates: 9

## Candidate Kinds

- `cluster_frequency`: 120
- `frequency_rate`: 431
- `last_event_only`: 137
- `no_reference`: 13
- `seizure_free`: 185
- `unknown_frequency`: 206

## Row Notes

- 1486: candidate:llm:1486:1: source_phrase_not_exact
- 1591: candidate:llm:1591:1: source_phrase_not_exact
- 1794: candidate:llm:1794:1: source_phrase_not_exact
- 1880: candidate:llm:1880:2: source_phrase_not_exact
- 1923: candidate:llm:1923:1: source_phrase_not_exact
- 1980: candidate:llm:1980:1: source_phrase_not_exact
- 2628: candidate:llm:2628:2: evidence_not_exact
- 2759: candidate:llm:2759:1: source_phrase_not_exact
- 3534: candidate:llm:3534:1: evidence_not_exact; candidate:llm:3534:1: source_phrase_not_exact
- 5791: candidate:llm:5791:2: source_phrase_not_exact
- 6153: candidate:llm:6153:3: source_phrase_not_exact; candidate:llm:6153:4: evidence_not_exact; candidate:llm:6153:4: source_phrase_not_exact
- 6571: candidate:llm:6571:3: evidence_not_exact; candidate:llm:6571:3: source_phrase_not_exact
- 9397: candidate:llm:9397:2: evidence_not_exact
- 11562: candidate:llm:11562:1: source_phrase_not_exact
- 12584: candidate:llm:12584:4: source_phrase_not_exact
- 12676: candidate:llm:12676:6: source_phrase_not_exact
- 12679: candidate:llm:12679:4: evidence_not_exact
- 12949: candidate:llm:12949:2: evidence_not_exact; candidate:llm:12949:2: source_phrase_not_exact
- 13267: candidate:llm:13267:2: source_phrase_not_exact
- 13598: candidate:llm:13598:2: evidence_not_exact
- 13608: candidate:llm:13608:2: evidence_not_exact
- 14611: candidate:llm:14611:2: evidence_not_exact; candidate:llm:14611:2: source_phrase_not_exact
- 15168: candidate:llm:15168:2: evidence_not_exact
- 15479: candidate:llm:15479:1: evidence_not_exact
