# Gan 2026 LLM-Only Typed Operations Reasoner V0

- JSONL: `experiments/gan2026_llm_only_typed_operations_reasoner_validation50_gpt41mini_v0_contractfix_max4800_2026-06-03.jsonl`
- Architecture: `llm_only_typed_operations_reasoner`
- Prompt/program version: `gan2026_llm_only_typed_operations_reasoner_v0_contractfix`
- Typed output schema version: `typed_operations_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy typed-operation extraction; graph projection is over model-extracted operation nodes.

## Typed Target

- Required operands: event count, time window, denominator, cluster size, seizure-free duration, temporal anchor, semiology grouping, uncertainty type, and selected evidence ID.

## Smoke Summary

- Structured records: 49/50
- Parse/schema failures: 1
- Selected evidence valid: 48/50
- Operation graph nodes: 81
- Selected-operation trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 24, Purist 23/50 (0.4600), Pragmatic 23/50 (0.4600)
- `format_only`: scorable 37, Purist 33/50 (0.6600), Pragmatic 34/50 (0.6800)
- `selected_evidence_arithmetic`: scorable 49, Purist 47/50 (0.9400), Pragmatic 47/50 (0.9400)
- `typed_operation_graph_projection`: scorable 50, Purist 47/50 (0.9400), Pragmatic 47/50 (0.9400)

## Row Review

- 10: gold `4 per day`; raw `up to 4 seizures per day`; typed graph `4 per day`
- 40: gold `4 per week`; raw `up to 4 seizures per week`; typed graph `multiple per week`
- 79: gold `6 to 7 per year`; raw `6#8804; 6 to 7 seizures per year`; typed graph `6 to 7 per year`
- 103: gold `2 to 4 per year`; raw `None`; typed graph `no seizure frequency reference`
- 187: gold `1 per 7 to 9 day`; raw `seizure clusters every 7 to 9 days`; typed graph `1 per 7 to 9 day`
- 190: gold `1 per 4 week`; raw `Clusters of absence seizures every 4 weeks; last tonic–clonic seizure May 2025; seizure free since then`; typed graph `1 per 4 week`
- 278: gold `multiple per week`; raw `multiple times per week, at least 2 episodes`; typed graph `multiple per week`
- 280: gold `multiple per day`; raw `multiple seizures per day`; typed graph `multiple per day`
- 338: gold `multiple per month`; raw `many convulsions in past month`; typed graph `no seizure frequency reference`
- 446: gold `2 per week`; raw `up to 2 per week`; typed graph `2 per week`
- 466: gold `21 to 28 per month`; raw `21 to 28 seizures per month`; typed graph `21 to 28 per month`
- 531: gold `12 to 30 per 3 month`; raw `12 to 30 seizures per quarter`; typed graph `12 to 30 per 3 month`
- 678: gold `2 per 4 month`; raw `multiple seizure frequency patterns: 2 per 4 months, clusters 3 to 6 per day, seizure free nearly 2 weeks`; typed graph `2 per 4 month`
- 704: gold `2 per month`; raw `2 per month with clustering around late luteal phase`; typed graph `2 per month`
- 731: gold `1 per day`; raw `daily brief seizures with recent cluster of three`; typed graph `1 per day`
- 743: gold `multiple per week`; raw `these episodes crop up most shifts`; typed graph `no seizure frequency reference`
- 744: gold `multiple per week`; raw `Brief absences on most weekdays; 1 generalised tonic–clonic seizure in last 8 weeks`; typed graph `1 per 8 week`
- 816: gold `1 per month`; raw `monthly seizures`; typed graph `1 per month`
- 869: gold `multiple per month`; raw `several per month with occasional clusters`; typed graph `multiple per day`
- 891: gold `1 per 2 day`; raw `3-4 seizures per 6 week period`; typed graph `1 per 2 day`
- 978: gold `1 per 2 month`; raw `about 1 seizure every 2 months`; typed graph `1 per 2 month`
- 987: gold `1 per 2 month`; raw `2 seizures per 2 months`; typed graph `1 per 2 month`
- 1030: gold `1 to 3 per month`; raw `1 to 3 seizures per month`; typed graph `1 to 3 per month`
- 1046: gold `3 to 5 per month`; raw `3 to 5 seizures per month`; typed graph `3 to 5 per month`
- 1070: gold `3 to 4 per week`; raw `3 to 4 seizures per week`; typed graph `3 to 4 per week`
- 1094: gold `3 to 5 per week`; raw `3 to 5 seizures per week`; typed graph `3 to 5 per week`
- 1165: gold `5 to 7 per 3 week`; raw `5 to 7 seizures per 3 weeks; seizure free for 6 weeks`; typed graph `7 per 3 week`
