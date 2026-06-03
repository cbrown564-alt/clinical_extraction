# Gan 2026 LLM-Only Simplified Selected State Reasoner V0

- JSONL: `/Users/cobro/code/clinical-extraction/experiments/gan2026_simplified_schema_a1_a2_hard_slice_stress_panel_2026-06-03_a1.jsonl`
- Architecture: `llm_only_simplified_selected_state_reasoner`
- Prompt/program version: `gan2026_llm_only_simplified_selected_state_reasoner_v0`
- Typed output schema version: `simplified_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 21
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-only selection-only validation development result; format-only and selected-evidence arithmetic are deterministic adapter layers.

## A1 Target

- one selected clinical state.
- Exact selected evidence.
- No graph projection.

## Smoke Summary

- Structured records: 21/21
- Parse/schema failures: 0
- Selected evidence valid: 20/21
- Selected-state trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 3, Purist 3/21 (0.1429), Pragmatic 3/21 (0.1429)
- `format_only`: scorable 3, Purist 3/21 (0.1429), Pragmatic 3/21 (0.1429)
- `selected_evidence_arithmetic`: scorable 21, Purist 17/21 (0.8095), Pragmatic 17/21 (0.8095)

## Adapter Delta

- Selected-evidence arithmetic raw-wrong to correct: 14
- Selected-evidence arithmetic raw-correct to wrong: 0

## Row Review

- 187: gold `1 per 7 to 9 day`; raw `2 nocturnal generalised tonic–clonic seizures in interval`; selected-evidence `no seizure frequency reference`
- 278: gold `multiple per week`; raw `multiple times in past week`; selected-evidence `1 per week`
- 190: gold `1 per 4 week`; raw `clusters of brief absence episodes every 4 weeks`; selected-evidence `1 per 4 week`
- 338: gold `multiple per month`; raw `many convulsions in past month`; selected-evidence `no seizure frequency reference`
- 4092: gold `1 per 2 to 3 week`; raw `qtwo - threewk`; selected-evidence `1 per 2 to 3 week`
- 2245: gold `7 to 8 per 3 week`; raw `7 to 8 seizures in the last three weeks`; selected-evidence `7 to 8 per 3 week`
- 1706: gold `multiple cluster per month, multiple per cluster`; raw `cluster of short events on multiple days`; selected-evidence `multiple cluster per month, multiple per cluster`
- 3507: gold `unknown`; raw `frequency reduced by 0.3 after dose increase`; selected-evidence `1 per day`
- 3512: gold `unknown`; raw `~20% increase in frequency after dose increase`; selected-evidence `no seizure frequency reference`
- 3532: gold `unknown`; raw `increased frequency after dose increase`; selected-evidence `no seizure frequency reference`
- 5996: gold `unknown`; raw `breakthrough events predominantly following lapses in prescribed antiseizure medication`; selected-evidence `no seizure frequency reference`
- 6029: gold `unknown`; raw `ongoing focal aware and focal impaired-awareness events with clustering pattern`; selected-evidence `unknown`
- 3468: gold `unknown`; raw `perimenstrual only (days -2 to +2)`; selected-evidence `no seizure frequency reference`
- 3469: gold `unknown`; raw `seizures perimenstrual only`; selected-evidence `no seizure frequency reference`
- 3482: gold `unknown`; raw `seizures perimenstrual only`; selected-evidence `no seizure frequency reference`
- 3493: gold `unknown`; raw `seizure clustering around menstrual period`; selected-evidence `unknown`
- 3949: gold `4 per week`; raw `sz Xfour/wk on average over the last 8 weeks`; selected-evidence `no seizure frequency reference`
- 9815: gold `multiple per day`; raw `~9 per hour focal clonic events`; selected-evidence `no seizure frequency reference`
