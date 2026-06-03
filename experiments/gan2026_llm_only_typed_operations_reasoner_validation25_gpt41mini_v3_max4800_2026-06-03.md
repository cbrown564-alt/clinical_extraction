# Gan 2026 LLM-Only Typed Operations Reasoner V0

- JSONL: `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.jsonl`
- Architecture: `llm_only_typed_operations_reasoner`
- Prompt/program version: `gan2026_llm_only_typed_operations_reasoner_v0_contractfix`
- Typed output schema version: `typed_operations_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy typed-operation extraction; graph projection is over model-extracted operation nodes.

## Typed Target

- Required operands: event count, time window, denominator, cluster size, seizure-free duration, temporal anchor, semiology grouping, uncertainty type, and selected evidence ID.

## Smoke Summary

- Structured records: 25/25
- Parse/schema failures: 0
- Selected evidence valid: 22/25
- Operation graph nodes: 37
- Selected-operation trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 15, Purist 15/25 (0.6000), Pragmatic 15/25 (0.6000)
- `format_only`: scorable 21, Purist 20/25 (0.8000), Pragmatic 20/25 (0.8000)
- `selected_evidence_arithmetic`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `typed_operation_graph_projection`: scorable 25, Purist 23/25 (0.9200), Pragmatic 23/25 (0.9200)

## Row Review

- 10: gold `4 per day`; raw `up to 4 seizures per day`; typed graph `4 per day`
- 40: gold `4 per week`; raw `up to 4 seizures per week`; typed graph `4 per week`
- 103: gold `2 to 4 per year`; raw `2 to 4 seizures per year`; typed graph `2 to 4 per year`
- 156: gold `1 per 6 day`; raw `1 seizure per 6 days`; typed graph `1 per 6 day`
- 187: gold `1 per 7 to 9 day`; raw `seizure clusters every 7 to 9 days`; typed graph `1 per 7 to 9 day`
- 190: gold `1 per 4 week`; raw `Clusters of absence episodes every 4 weeks; last tonic–clonic seizure in May 2025; seizure free since then`; typed graph `1 per 4 week`
- 338: gold `multiple per month`; raw `many convulsions in past month`; typed graph `no seizure frequency reference`
- 446: gold `2 per week`; raw `up to twice per week`; typed graph `multiple per week`
- 466: gold `21 to 28 per month`; raw `21 to 28 seizures per month`; typed graph `21 to 28 per month`
- 467: gold `9 per month`; raw `9 per month`; typed graph `no seizure frequency reference`
- 531: gold `12 to 30 per 3 month`; raw `12 to 30 seizures per quarter`; typed graph `12 to 30 per 3 month`
