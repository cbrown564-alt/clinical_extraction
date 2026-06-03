# Gan 2026 LLM-Only Typed Operations Reasoner V0

- JSONL: `experiments/gan2026_llm_only_typed_operations_reasoner_validation250_gpt41mini_v0_contractfix_max10000_2026-06-03.jsonl`
- Architecture: `llm_only_typed_operations_reasoner`
- Prompt/program version: `gan2026_llm_only_typed_operations_reasoner_v0_contractfix`
- Typed output schema version: `typed_operations_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 3
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy typed-operation extraction; graph projection is over model-extracted operation nodes.

## Typed Target

- Required operands: event count, time window, denominator, cluster size, seizure-free duration, temporal anchor, semiology grouping, uncertainty type, and selected evidence ID.

## Smoke Summary

- Structured records: 3/3
- Parse/schema failures: 0
- Selected evidence valid: 1/3
- Operation graph nodes: 4
- Selected-operation trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 1, Purist 1/3 (0.3333), Pragmatic 1/3 (0.3333)
- `format_only`: scorable 1, Purist 1/3 (0.3333), Pragmatic 1/3 (0.3333)
- `selected_evidence_arithmetic`: scorable 3, Purist 2/3 (0.6667), Pragmatic 2/3 (0.6667)
- `typed_operation_graph_projection`: scorable 3, Purist 2/3 (0.6667), Pragmatic 2/3 (0.6667)

## Row Review

- 10: gold `4 per day`; raw `up to 4 seizures per day`; typed graph `4 per day`
- 40: gold `4 per week`; raw `up to 4 seizures per week`; typed graph `multiple per week`
