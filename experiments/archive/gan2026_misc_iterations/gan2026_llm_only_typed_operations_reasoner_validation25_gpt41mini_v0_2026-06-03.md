# Gan 2026 LLM-Only Typed Operations Reasoner V0

- JSONL: `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v0_2026-06-03.jsonl`
- Architecture: `llm_only_typed_operations_reasoner`
- Prompt/program version: `gan2026_llm_only_typed_operations_reasoner_v0`
- Typed output schema version: `typed_operations_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy typed-operation extraction; graph projection is over model-extracted operation nodes.

## Typed Target

- Required operands: event count, time window, denominator, cluster size, seizure-free duration, temporal anchor, semiology grouping, uncertainty type, and selected evidence ID.

## Smoke Summary

- Structured records: 22/25
- Parse/schema failures: 3
- Selected evidence valid: 16/25
- Operation graph nodes: 22
- Selected-operation trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 14, Purist 14/25 (0.5600), Pragmatic 14/25 (0.5600)
- `format_only`: scorable 20, Purist 20/25 (0.8000), Pragmatic 20/25 (0.8000)
- `selected_evidence_arithmetic`: scorable 22, Purist 20/25 (0.8000), Pragmatic 20/25 (0.8000)
- `typed_operation_graph_projection`: scorable 25, Purist 19/25 (0.7600), Pragmatic 19/25 (0.7600)

## Row Review

- 10: gold `4 per day`; raw `up to 4 seizures per day`; typed graph `no seizure frequency reference`
- 40: gold `4 per week`; raw `up to 4 seizures per week`; typed graph `no seizure frequency reference`
- 187: gold `1 per 7 to 9 day`; raw `None`; typed graph `no seizure frequency reference`
- 190: gold `1 per 4 week`; raw `None`; typed graph `no seizure frequency reference`
- 218: gold `1 per 3 week`; raw `1 per 3 week`; typed graph `no seizure frequency reference`
- 278: gold `multiple per week`; raw `multiple seizures per week`; typed graph `multiple per week`
- 280: gold `multiple per day`; raw `multiple seizures per day`; typed graph `multiple per day`
- 409: gold `1 per month`; raw `None`; typed graph `no seizure frequency reference`
- 419: gold `2 per year`; raw `approximately twice per year`; typed graph `2 per year`
- 446: gold `2 per week`; raw `up to 2 per week`; typed graph `2 per week`
- 466: gold `21 to 28 per month`; raw `21 to 28 seizures per month`; typed graph `21 to 28 per month`
- 531: gold `12 to 30 per 3 month`; raw `12 to 30 seizures per quarter`; typed graph `12 to 30 per 3 month`
