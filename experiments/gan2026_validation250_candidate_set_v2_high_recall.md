# Gan 2026 Validation250 CandidateSet Union V1

Validation250 extract-stage deterministic+LLM candidate-set union only. No selection, normalization, projection, scoring, or locked-test work.

## Artifacts

- JSONL: `experiments\gan2026_validation250_candidate_set_v2_high_recall.jsonl`
- Summary JSON: `experiments\gan2026_validation250_candidate_set_v2_high_recall.json`

## Summary

- Rows: 250
- Total candidates: 735
- Rows with no candidates: 3
- Mean candidates per row: 2.94
- Max candidates per row: 10
- Rows with union assembly issues: 68
- LLM missing candidate-set rows: 1
- LLM call-error rows: 1
- LLM parse/validation issue rows: 12
- Merged duplicate candidates: 25

## Candidate Kinds

- `cluster_frequency`: 50
- `frequency_rate`: 457
- `last_event_only`: 22
- `seizure_free`: 128
- `unknown_frequency`: 78

## Source Types

- `deterministic_candidate`: 377
- `llm_candidate`: 358
