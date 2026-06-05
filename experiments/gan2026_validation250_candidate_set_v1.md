# Gan 2026 Validation250 CandidateSet Union V1

Validation250 extract-stage deterministic+LLM candidate-set union only. No selection, normalization, projection, scoring, or locked-test work.

## Artifacts

- JSONL: `experiments\gan2026_validation250_candidate_set_v1.jsonl`
- Summary JSON: `experiments\gan2026_validation250_candidate_set_v1.json`

## Summary

- Rows: 250
- Total candidates: 703
- Rows with no candidates: 4
- Mean candidates per row: 2.81
- Max candidates per row: 10
- Rows with union assembly issues: 84
- LLM missing candidate-set rows: 2
- LLM call-error rows: 2
- LLM parse/validation issue rows: 18
- Merged duplicate candidates: 25

## Candidate Kinds

- `cluster_frequency`: 49
- `frequency_rate`: 502
- `last_event_only`: 22
- `no_reference`: 2
- `seizure_free`: 119
- `unknown_frequency`: 9

## Source Types

- `deterministic_candidate`: 370
- `llm_candidate`: 333
