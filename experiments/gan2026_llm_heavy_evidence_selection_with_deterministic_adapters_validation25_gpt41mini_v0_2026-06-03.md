# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters

- JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v0_2026-06-03.jsonl`
- Architecture: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Claim language: LLM-heavy clinical selection with deterministic mechanical adapters.
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v0`
- Typed output schema version: `selected_fact_operands_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Primary adapted layer: `mechanical_adapter_label`
- Decision 0007 outcome: `reject`

## Predeclared Smoke

- Surface: `validation25` under `gan2026_split_v1`.
- Primary question: can typed selected fact/evidence/operand output support mechanical adapters without deterministic clinical replacement?
- Stop rule: promotion requires the Decision 0007 validation25 gate.

## Smoke Summary

- Structured typed outputs: 25/25
- Adapter parse failures: 0
- Selected evidence exact: 19/25
- Selected fact trace mismatches: 0
- Selected operand completeness: 22/25

## Score Layers

- `raw_model_parser_label`: scorable 0, Purist 0/25 (0.0000), Pragmatic 0/25 (0.0000)
- `raw_model_clinical_selection`: scorable 0, Purist 0/25 (0.0000), Pragmatic 0/25 (0.0000)
- `format_only_repair`: scorable 0, Purist 0/25 (0.0000), Pragmatic 0/25 (0.0000)
- `mechanical_adapter_label`: scorable 22, Purist 19/25 (0.7600), Pragmatic 20/25 (0.8000)
- `benchmark_convention_adapter`: scorable 22, Purist 19/25 (0.7600), Pragmatic 20/25 (0.8000)

## Adapter Gate

- Adapted-label Purist: 19/25
- Adapter raw-wrong to correct: 19
- Adapter raw-correct to wrong: 0

## Row Review

- 10: raw and adapted miss; gold `4 per day`; raw `frequency_up_to_4_per_day_with_variable_clustering`; adapted `None`; taxonomy `exact_evidence_failure`
- 40: mechanical adapter gain; gold `4 per week`; raw `frequency_0-4_per_week`; adapted `0 to 4 per 1 week`; taxonomy `exact_evidence_failure`
- 79: mechanical adapter gain; gold `6 to 7 per year`; raw `frequency_6_to_7_per_year`; adapted `6 to 7 per 1 year`; taxonomy `exact_evidence_failure`
- 103: mechanical adapter gain; gold `2 to 4 per year`; raw `frequency`; adapted `2 to 4 per 1 year`; taxonomy `exact_evidence_failure`
- 128: raw and adapted miss; gold `17 per month`; raw `cluster_frequency_17_per_month`; adapted `None`; taxonomy `missing_selected_operands`
- 156: mechanical adapter gain; gold `1 per 6 day`; raw `frequency_1_per_6_days`; adapted `1 per 6 day`; taxonomy `ok`
- 180: mechanical adapter gain; gold `1 per 7 day`; raw `frequency_1_per_7_days`; adapted `1 per 7 day`; taxonomy `ok`
- 182: mechanical adapter gain; gold `1 per 2 day`; raw `frequency_every_2_days`; adapted `1 per 2 day`; taxonomy `ok`
- 187: raw and adapted miss; gold `1 per 7 to 9 day`; raw `cluster_frequency`; adapted `1 cluster per 7 to 9 day, 2 per cluster`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 190: raw and adapted miss; gold `1 per 4 week`; raw `cluster_frequency`; adapted `1 cluster per 4 week, multiple per cluster`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 198: mechanical adapter gain; gold `1 per 4 week`; raw `frequency`; adapted `1 per 4 week`; taxonomy `ok`
- 212: mechanical adapter gain; gold `1 per 3 to 4 week`; raw `frequency_1_per_3_to_4_weeks`; adapted `1 per 3 to 4 week`; taxonomy `ok`
- 218: mechanical adapter gain; gold `1 per 3 week`; raw `frequency`; adapted `1 per 3 week`; taxonomy `ok`
- 243: mechanical adapter gain; gold `1 per 4 month`; raw `frequency_1_per_4_months`; adapted `1 per 4 month`; taxonomy `ok`
- 278: mechanical adapter gain; gold `multiple per week`; raw `frequency`; adapted `multiple per 7 day`; taxonomy `ok`
- 280: raw and adapted miss; gold `multiple per day`; raw `frequency_multiple_seizures_past_day`; adapted `2 per 1 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 338: mechanical adapter gain; gold `multiple per month`; raw `frequency`; adapted `multiple per 1 month`; taxonomy `ok`
- 409: mechanical adapter gain; gold `1 per month`; raw `frequency_<=1_per_month`; adapted `1 per 1 month`; taxonomy `exact_evidence_failure`
- 419: mechanical adapter gain; gold `2 per year`; raw `frequency_2_per_year`; adapted `2 per 1 year`; taxonomy `ok`
- 446: raw and adapted miss; gold `2 per week`; raw `frequency`; adapted `None`; taxonomy `exact_evidence_failure`
- 466: mechanical adapter gain; gold `21 to 28 per month`; raw `frequency_21-28_per_month`; adapted `21 to 28 per 1 month`; taxonomy `ok`
- 467: mechanical adapter gain; gold `9 per month`; raw `frequency_9_per_month`; adapted `9 per 1 month`; taxonomy `ok`
- 531: mechanical adapter gain; gold `12 to 30 per 3 month`; raw `frequency_12-30_per_quarter`; adapted `12 to 30 per 1 month`; taxonomy `ok`
- 598: mechanical adapter gain; gold `1 per 8 month`; raw `frequency_1_per_8_months`; adapted `1 per 8 month`; taxonomy `ok`
- 659: mechanical adapter gain; gold `2 per 4 day`; raw `frequency_2_per_4_days`; adapted `2 per 4 day`; taxonomy `ok`

## Failure Taxonomy

- `exact_evidence_failure`: 6
- `missing_selected_operands`: 1
- `ok`: 15
- `wrong_selected_clinical_fact_or_operand`: 3

## Interpretation

This validation25 Decision 0007 smoke fails at least one hard selected-fact, evidence, operand, or adapter gate. Do not escalate this artifact.
