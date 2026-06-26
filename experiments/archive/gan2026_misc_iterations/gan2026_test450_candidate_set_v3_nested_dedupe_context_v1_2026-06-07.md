# gan2026_test450_candidate_set_v3_nested_dedupe_context_v1

validation450 extract-stage deterministic+LLM candidate-set union only. No selection, normalization, projection, scoring, or locked-test work.

## Artifacts

- JSONL: `experiments\gan2026_test450_candidate_set_v3_nested_dedupe_context_v1_2026-06-07.jsonl`
- Summary JSON: `experiments\gan2026_test450_candidate_set_v3_nested_dedupe_context_v1_2026-06-07.json`

## Summary

- Rows: 450
- Total candidates: 1061
- Rows with no candidates: 6
- Mean candidates per row: 2.36
- Max candidates per row: 7
- Rows with union assembly issues: 287
- LLM missing candidate-set rows: 0
- LLM call-error rows: 0
- LLM parse/validation issue rows: 27
- Merged duplicate candidates: 20
- Merged nested duplicate candidates: 359

## Candidate Kinds

- `cluster_frequency`: 108
- `frequency_rate`: 496
- `last_event_only`: 99
- `no_reference`: 15
- `seizure_free`: 189
- `unknown_frequency`: 154

## Source Types

- `deterministic_candidate`: 288
- `llm_candidate`: 773
