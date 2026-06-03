# Gan 2026 LLM-Only Simplified Selected State Reasoner V0

- JSONL: `experiments/gan2026_llm_only_simplified_selected_state_reasoner_validation25_gpt41mini_v0_2026-06-03.jsonl`
- Architecture: `llm_only_simplified_selected_state_reasoner`
- Prompt/program version: `gan2026_llm_only_simplified_selected_state_reasoner_v0`
- Typed output schema version: `simplified_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-only selection-only validation development result; format-only and selected-evidence arithmetic are deterministic adapter layers.

## A1 Target

- one selected clinical state.
- Exact selected evidence.
- No graph projection.

## Smoke Summary

- Structured records: 25/25
- Parse/schema failures: 0
- Selected evidence valid: 25/25
- Selected-state trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 5, Purist 5/25 (0.2000), Pragmatic 5/25 (0.2000)
- `format_only`: scorable 18, Purist 18/25 (0.7200), Pragmatic 18/25 (0.7200)
- `selected_evidence_arithmetic`: scorable 25, Purist 23/25 (0.9200), Pragmatic 23/25 (0.9200)

## Adapter Delta

- Selected-evidence arithmetic raw-wrong to correct: 18
- Selected-evidence arithmetic raw-correct to wrong: 0

## Row Review

- 10: gold `4 per day`; raw `≤ four per day`; selected-evidence `4 per day`
- 40: gold `4 per week`; raw `≤ four seizures per week`; selected-evidence `4 per week`
- 79: gold `6 to 7 per year`; raw `≤ 6 to 7 per year`; selected-evidence `6 to 7 per year`
- 103: gold `2 to 4 per year`; raw `≤ two or four per year`; selected-evidence `2 to 4 per year`
- 156: gold `1 per 6 day`; raw `every 6 days`; selected-evidence `1 per 6 day`
- 182: gold `1 per 2 day`; raw `every 2 days`; selected-evidence `1 per 2 day`
- 187: gold `1 per 7 to 9 day`; raw `2 nocturnal generalised tonic–clonic seizures in interval`; selected-evidence `no seizure frequency reference`
- 190: gold `1 per 4 week`; raw `clusters of brief absence episodes every 4 weeks`; selected-evidence `1 per 4 week`
- 198: gold `1 per 4 week`; raw `seizures every 4 weeks`; selected-evidence `1 per 4 week`
- 212: gold `1 per 3 to 4 week`; raw `every 3 - 4 weeks`; selected-evidence `1 per 3 to 4 week`
- 218: gold `1 per 3 week`; raw `seizures every 3 weeks`; selected-evidence `1 per 3 week`
- 278: gold `multiple per week`; raw `multiple times in past week`; selected-evidence `1 per week`
- 338: gold `multiple per month`; raw `many convulsions in past month`; selected-evidence `no seizure frequency reference`
- 409: gold `1 per month`; raw `≤ once per month`; selected-evidence `1 per month`
- 419: gold `2 per year`; raw `approximately twice per year`; selected-evidence `2 per year`
- 446: gold `2 per week`; raw `≤ twice per week`; selected-evidence `2 per week`
- 466: gold `21 to 28 per month`; raw `21 to 28 seizures per month`; selected-evidence `21 to 28 per month`
- 531: gold `12 to 30 per 3 month`; raw `12 to 30 per quarter`; selected-evidence `12 to 30 per 3 month`
- 598: gold `1 per 8 month`; raw `1 per eight months`; selected-evidence `1 per 8 month`
- 659: gold `2 per 4 day`; raw `twice every 4 days`; selected-evidence `2 per 4 day`
