# Gan 2026 LLM-Only Typed Operations Reasoner V0

- JSONL: `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v0_contractfix_2026-06-03.jsonl`
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

- Structured records: 24/25
- Parse/schema failures: 1
- Selected evidence valid: 17/25
- Operation graph nodes: 20
- Selected-operation trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 13, Purist 13/25 (0.5200), Pragmatic 13/25 (0.5200)
- `format_only`: scorable 19, Purist 18/25 (0.7200), Pragmatic 18/25 (0.7200)
- `selected_evidence_arithmetic`: scorable 24, Purist 22/25 (0.8800), Pragmatic 22/25 (0.8800)
- `typed_operation_graph_projection`: scorable 25, Purist 18/25 (0.7200), Pragmatic 18/25 (0.7200)

## Row Review

- 10: gold `4 per day`; raw `up to 4 seizures per day`; typed graph `no seizure frequency reference`
- 40: gold `4 per week`; raw `up to 4 seizures per week`; typed graph `no seizure frequency reference`
- 79: gold `6 to 7 per year`; raw `6 to 7 seizures per year`; typed graph `6 to 7 per year`
- 103: gold `2 to 4 per year`; raw `None`; typed graph `no seizure frequency reference`
- 187: gold `1 per 7 to 9 day`; raw `seizure clusters every 7 to 9 days with 2 recent nocturnal generalized tonic-clonic seizures`; typed graph `no seizure frequency reference`
- 190: gold `1 per 4 week`; raw `Clusters of absence episodes every 4 weeks; last GTC seizure May 2025; seizure free since then`; typed graph `seizure free for multiple year`
- 218: gold `1 per 3 week`; raw `seizures every 3 weeks`; typed graph `no seizure frequency reference`
- 280: gold `multiple per day`; raw `multiple seizures in past day; several near-miss episodes over preceding week`; typed graph `multiple per day`
- 338: gold `multiple per month`; raw `many convulsions in past month`; typed graph `no seizure frequency reference`
- 446: gold `2 per week`; raw `up to twice per week`; typed graph `no seizure frequency reference`
- 466: gold `21 to 28 per month`; raw `21 to 28 seizures per month`; typed graph `21 to 28 per month`
- 531: gold `12 to 30 per 3 month`; raw `12 to 30 per quarter`; typed graph `12 to 30 per 3 month`
