# gan2026_validation250_candidate_set_v3_nested_dedupe

Validation250 extract-stage deterministic+LLM candidate-set union only. No selection, normalization, projection, scoring, or locked-test work.

## Artifacts

- JSONL: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl`
- Summary JSON: `experiments\gan2026_validation250_candidate_set_v3_nested_dedupe.json`

## Summary

- Rows: 250
- Total candidates: 514
- Rows with no candidates: 3
- Mean candidates per row: 2.06
- Max candidates per row: 9
- Rows with union assembly issues: 195
- LLM missing candidate-set rows: 1
- LLM call-error rows: 1
- LLM parse/validation issue rows: 12
- Merged duplicate candidates: 25
- Merged nested duplicate candidates: 221

## Candidate Kinds

- `cluster_frequency`: 40
- `frequency_rate`: 285
- `last_event_only`: 22
- `seizure_free`: 92
- `unknown_frequency`: 75

## Source Types

- `deterministic_candidate`: 159
- `llm_candidate`: 355
