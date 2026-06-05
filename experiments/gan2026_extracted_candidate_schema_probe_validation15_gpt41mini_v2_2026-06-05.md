# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_extracted_candidate_schema_probe_validation15_gpt41mini_v2_2026-06-05.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v2`
- Split: `validation` / `gan2026_split_v1`
- Rows: 15
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 15/15
- Total candidates: 21
- Call failures: 0
- Parse/validation failure rows: 2
- Detail failure rows: 0
- Evidence error rows: 2
- Source phrase error rows: 1
- Rows with no candidates: 0

## Candidate Kinds

- `cluster_frequency`: 2
- `frequency_rate`: 17
- `last_event_only`: 2

## Row Notes

- 10: candidate:llm:10:1: evidence_not_exact
- 79: candidate:llm:79:2: evidence_not_exact; candidate:llm:79:2: source_phrase_not_exact

## Manual Inspection Notes

- Deterministic assembly worked: model output was limited to clinical draft fields, while ids, source artifact, row index, spans, source ids, owner, and policy bookkeeping were filled by code.
- The stricter cluster instruction helped: rows 40 and 128 no longer emitted trigger/context phrases as cluster candidates.
- True cluster candidates still worked: row 187 captured "events tend to cluster every seven to nine days"; row 190 captured clusters every 4 weeks over 1-2 days.
- Duplicate extraction improved but did not disappear: row 79 still emitted the same "less than or equal to 6 to 7 per year" value twice from repeated note wording.
- Exact evidence copying remains brittle around special characters and casing: row 10 corrupted the less-than-or-equal symbol; row 79 lowercased the initial "He".
- Frequency-detail parsing remains inconsistent: row 103 represented "every 1 or 2 weeks" as `count_range` plus `time_period` rather than the instructed `time_period_range`.
- The model correctly used uncertainty on row 278: "multiple times in past week" became `certainty=uncertain` with `certainty_reason=vague_count`.

## Current Interpretation

The simplified draft schema is viable for asking the LLM to find clinical candidate statements and choose broad candidate kinds. It is less reliable as the source of parsed frequency detail fields. The next design question is whether to keep the LLM detail object as source-near text only, then let deterministic normalization expand counts, ranges, intervals, and special symbols.
