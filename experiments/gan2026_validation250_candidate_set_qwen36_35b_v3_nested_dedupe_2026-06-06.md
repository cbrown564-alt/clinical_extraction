# gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06

Validation250 extract-stage deterministic+LLM candidate-set union only. No selection, normalization, projection, scoring, or locked-test work.

## Artifacts

- JSONL: `experiments\gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation250_candidate_set_qwen36_35b_v3_nested_dedupe_2026-06-06.json`

## Summary

- Rows: 250
- Total candidates: 624
- Rows with no candidates: 5
- Mean candidates per row: 2.50
- Max candidates per row: 8
- Rows with union assembly issues: 186
- LLM missing candidate-set rows: 45
- LLM call-error rows: 45
- LLM parse/validation issue rows: 49
- Merged duplicate candidates: 60
- Merged nested duplicate candidates: 166

## Candidate Kinds

- `cluster_frequency`: 27
- `frequency_rate`: 291
- `last_event_only`: 24
- `seizure_free`: 119
- `unknown_frequency`: 163

## Source Types

- `deterministic_candidate`: 218
- `llm_candidate`: 406
