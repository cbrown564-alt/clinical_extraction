# Gan 2026 ExtractedCandidate Schema Probe

- JSONL: `experiments\gan2026_validation250_llm_candidate_set_qwen36_35b_v6_2026-06-06.jsonl`
- Pipeline: `llm_extracted_candidate_schema_probe`
- Prompt/schema version: `gan2026_extracted_candidate_schema_probe_v6`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: schema-fit probe only; no scoring and no final labels.

## Summary

- Candidate sets: 205/250
- Total candidates: 473
- Call failures: 45
- Parse/validation failure rows: 49
- Detail failure rows: 0
- Evidence error rows: 3
- Source phrase error rows: 2
- Rows with no candidates: 45

## Candidate Kinds

- `cluster_frequency`: 24
- `frequency_rate`: 171
- `last_event_only`: 24
- `seizure_free`: 91
- `unknown_frequency`: 163

## Row Notes

- 40: not_run
- 180: not_run
- 212: not_run
- 466: not_run
- 659: not_run
- 1165: not_run
- 1223: not_run
- 1413: not_run
- 1573: not_run
- 1591: not_run
- 1773: not_run
- 1880: not_run
- 1922: candidate:llm:1922:3: evidence_not_exact; candidate:llm:1922:5: evidence_not_exact; candidate:llm:1922:7: evidence_not_exact; candidate:llm:1922:9: evidence_not_exact; candidate:llm:1922:11: evidence_not_exact; candidate:llm:1922:13: evidence_not_exact; candidate:llm:1922:15: evidence_not_exact; candidate:llm:1922:17: evidence_not_exact; candidate:llm:1922:19: evidence_not_exact
- 1979: not_run
- 2023: not_run
- 2149: not_run
- 2233: not_run
- 2369: not_run
- 2435: not_run
- 2459: not_run
- 2748: candidate:llm:2748:3: source_phrase_not_exact
- 2789: not_run
- 2887: candidate:llm:2887:2: evidence_not_exact
- 3262: not_run
- 3493: candidate:llm:3493:1: evidence_not_exact; candidate:llm:3493:2: evidence_not_exact; candidate:llm:3493:3: evidence_not_exact; candidate:llm:3493:4: evidence_not_exact; candidate:llm:3493:5: evidence_not_exact; candidate:llm:3493:5: source_phrase_not_exact
- 3532: not_run
- 3534: not_run
- 3682: not_run
- 3710: not_run
- 3753: not_run
- 3806: not_run
- 3827: not_run
- 3849: not_run
- 3889: not_run
- 3949: not_run
- 3999: not_run
- 4022: not_run
- 4026: not_run
- 4100: not_run
- 4173: not_run
- 4243: not_run
- 4345: not_run
- 4402: not_run
- 4562: not_run
- 4592: not_run
- 4694: not_run
- 4709: not_run
- 5110: not_run
- 5507: not_run
