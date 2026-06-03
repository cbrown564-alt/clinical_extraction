# Gan 2026 LLM-Only Simplified Selected State Reasoner V0

- JSONL: `/Users/cobro/code/clinical-extraction/experiments/gan2026_simplified_schema_a1_validation50_2026-06-03.jsonl`
- Architecture: `llm_only_simplified_selected_state_reasoner`
- Prompt/program version: `gan2026_llm_only_simplified_selected_state_reasoner_v0`
- Typed output schema version: `simplified_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-only selection-only validation development result; format-only and selected-evidence arithmetic are deterministic adapter layers.

## A1 Target

- one selected clinical state.
- Exact selected evidence.
- No graph projection.

## Smoke Summary

- Structured records: 50/50
- Parse/schema failures: 0
- Selected evidence valid: 50/50
- Selected-state trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 6, Purist 6/50 (0.1200), Pragmatic 6/50 (0.1200)
- `format_only`: scorable 30, Purist 29/50 (0.5800), Pragmatic 30/50 (0.6000)
- `selected_evidence_arithmetic`: scorable 50, Purist 45/50 (0.9000), Pragmatic 45/50 (0.9000)

## Adapter Delta

- Selected-evidence arithmetic raw-wrong to correct: 39
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
- 665: gold `2 per 2 week`; raw `twice every two weeks`; selected-evidence `2 per 2 week`
- 694: gold `1 per week`; raw `once a week`; selected-evidence `1 per week`
- 704: gold `2 per month`; raw `twice a month`; selected-evidence `2 per month`
- 725: gold `1 per day`; raw `daily`; selected-evidence `1 per day`
- 731: gold `1 per day`; raw `daily brief episodes`; selected-evidence `1 per day`
- 743: gold `multiple per week`; raw `most shifts`; selected-evidence `no seizure frequency reference`
- 744: gold `multiple per week`; raw `brief absences most weekdays, one generalised tonic–clonic seizure in last eight weeks`; selected-evidence `no seizure frequency reference`
- 763: gold `1 per week`; raw `weekly`; selected-evidence `1 per week`
- 790: gold `1 per 7 to 10 day`; raw `roughly once every seven to ten days`; selected-evidence `1 per 7 to 10 day`
- 816: gold `1 per month`; raw `monthly seizures`; selected-evidence `1 per month`
- 849: gold `1 per year`; raw `yearly seizures`; selected-evidence `1 per year`
- 854: gold `1 per year`; raw `roughly yearly`; selected-evidence `1 per year`
- 869: gold `multiple per month`; raw `several events spread across most months`; selected-evidence `multiple per day`
- 891: gold `1 per 2 day`; raw `seizures every other day`; selected-evidence `1 per 2 day`
- 899: gold `1 per 2 week`; raw `seizures every other week`; selected-evidence `1 per 2 week`
- 959: gold `1 per 2 month`; raw `bimonthly`; selected-evidence `1 per 2 month`
- 960: gold `1 per 2 month`; raw `bimonthly seizures`; selected-evidence `1 per 2 month`
- 978: gold `1 per 2 month`; raw `focal impaired-awareness events every other month`; selected-evidence `1 per 2 month`
- 987: gold `1 per 2 month`; raw `bimonthly seizures`; selected-evidence `1 per 2 month`
- 1030: gold `1 to 3 per month`; raw `one or three seizures last month`; selected-evidence `1 per month`
- 1046: gold `3 to 5 per month`; raw `3 to 5 seizures per month`; selected-evidence `3 to 5 per month`
- 1070: gold `3 to 4 per week`; raw `3 or 4 seizures last week`; selected-evidence `no seizure frequency reference`
- 1094: gold `3 to 5 per week`; raw `3 to 5 seizures last week`; selected-evidence `no seizure frequency reference`
- 1165: gold `5 to 7 per 3 week`; raw `5 or 7 focal onset seizures in three weeks`; selected-evidence `7 per 3 week`
