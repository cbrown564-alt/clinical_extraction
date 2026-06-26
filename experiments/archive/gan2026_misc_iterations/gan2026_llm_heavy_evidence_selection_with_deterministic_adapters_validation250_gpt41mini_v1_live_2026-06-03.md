# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters

- JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl`
- Architecture: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Claim language: LLM-heavy clinical selection with deterministic mechanical adapters.
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Typed output schema version: `selected_fact_operands_v1`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Replay source: `None`
- Primary score layer: `final_projected_label`
- Decision 0007 outcome: `reject`

## Replay Scope

- Surface: `validation250` under `gan2026_split_v1`.
- Primary question: can typed selected fact/evidence/operand output support mechanical adapters and the final projection layer without deterministic clinical replacement?
- Stop rule: do not escalate broader validation until raw/mechanical/final ablations are recorded.

## Replay Summary

- Structured typed outputs: 250/250
- Reused raw outputs: 0/250
- Adapter parse failures: 0
- Selected evidence exact: 242/250
- Selected fact trace mismatches: 0
- Selected operand completeness: 227/250

## Score Layers

- `raw_model_parser_label`: scorable 240, Purist 203/250 (0.8120), Pragmatic 213/250 (0.8520)
- `raw_model_clinical_selection`: scorable 240, Purist 203/250 (0.8120), Pragmatic 213/250 (0.8520)
- `format_only_repair`: scorable 241, Purist 204/250 (0.8160), Pragmatic 214/250 (0.8560)
- `mechanical_adapter_label`: scorable 227, Purist 185/250 (0.7400), Pragmatic 196/250 (0.7840)
- `benchmark_convention_adapter`: scorable 227, Purist 180/250 (0.7200), Pragmatic 194/250 (0.7760)
- `final_projected_label`: scorable 243, Purist 214/250 (0.8560), Pragmatic 218/250 (0.8720)

## Adapter Gate

- Adapted-label Purist: 185/250
- Final projected-label Purist: 214/250
- Adapter raw-wrong to correct: 1
- Adapter raw-correct to wrong: 19
- Final projection raw-wrong to correct: 16
- Final projection raw-correct to wrong: 5
- Final projection mechanical-wrong to correct: 31
- Final projection mechanical-correct to wrong: 2

## Final Projection Families

- `clean_scorer_facing_policy`: 112
- `raw_label_fallback`: 23
- `selected_evidence_bimonthly_policy`: 3
- `selected_evidence_current_monthly_precedence`: 1
- `selected_evidence_every_other_interval`: 5
- `selected_evidence_projection`: 22
- `selected_evidence_vague_weekday_policy`: 1

## Row Review

- 743: adapter regression; gold `multiple per week`; raw `multiple per shift`; adapted `None`; taxonomy `missing_selected_operands`
- 744: raw and adapted miss; gold `multiple per week`; raw `4 to 5 per 7 day`; adapted `4 to 5 per 7 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 816: raw and adapted miss; gold `1 per month`; raw `4 per 1 year`; adapted `4 per 1 year`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 899: adapter regression; gold `1 per 2 week`; raw `0.5 per 1 week`; adapted `0.5 per 2 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 959: raw and adapted miss; gold `1 per 2 month`; raw `2 per 1 to 2 month`; adapted `2 per 1 to 2 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 960: raw and adapted miss; gold `1 per 2 month`; raw `1 to 2 per 1 month`; adapted `1 to 2 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 987: raw and adapted miss; gold `1 per 2 month`; raw `2 per 1 month`; adapted `2 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 1165: adapter regression; gold `5 to 7 per 3 week`; raw `5 to 7 per 3 week`; adapted `1 per 3 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 1317: adapter regression; gold `unknown, multiple per cluster`; raw `multiple per day`; adapted `1 per 1 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 1357: adapter regression; gold `1 per day`; raw `1 per day`; adapted `None`; taxonomy `missing_selected_operands`
- 1363: raw and adapted miss; gold `3 per day`; raw `1 to 2 per week`; adapted `1 to 2 per 1 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 1687: raw and adapted miss; gold `multiple per week`; raw `3 to 7 per 1 week`; adapted `3 to 7 per 1 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 1694: raw and adapted miss; gold `1 cluster per 2 week, 3 per cluster`; raw `1 per 2 week`; adapted `1 per 2 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 1695: raw and adapted miss; gold `multiple per month`; raw `3 to 5 per 1 month`; adapted `3 to 5 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 1706: raw and adapted miss; gold `multiple cluster per month, multiple per cluster`; raw `1 per 1 month`; adapted `None`; taxonomy `missing_selected_operands`
- 1707: adapter regression; gold `multiple per week`; raw `multiple per week`; adapted `1 per 7 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 2149: adapter regression; gold `unknown`; raw `unknown`; adapted `None`; taxonomy `missing_selected_operands`
- 2166: adapter regression; gold `unknown`; raw `frequent per unknown`; adapted `None`; taxonomy `missing_selected_operands`
- 2731: raw and adapted miss; gold `1 per 2 week`; raw `0.5 per 2 week`; adapted `0.5 per 2 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3118: adapter regression; gold `seizure free for multiple month`; raw `seizure free`; adapted `None`; taxonomy `missing_selected_operands`
- 3137: raw and adapted miss; gold `seizure free for multiple month`; raw `no seizure frequency reference`; adapted `no seizure frequency reference`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3224: mechanical adapter gain; gold `1 cluster per month, 6 to 7 per cluster`; raw `1 per month, 6 to 7 per cluster`; adapted `1 cluster per 1 month, 6 to 7 per cluster`; taxonomy `ok`
- 3242: raw and adapted miss; gold `2 cluster per month, 5 per cluster`; raw `2 per 1 month`; adapted `2 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3261: raw and adapted miss; gold `2 cluster per month, 4 per cluster`; raw `2 per 1 month`; adapted `2 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3262: raw and adapted miss; gold `2 cluster per month, 5 per cluster`; raw `2 per 1 month`; adapted `2 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3356: raw and adapted miss; gold `unknown`; raw `occasional per 3 month`; adapted `None`; taxonomy `missing_selected_operands`
- 3371: raw and adapted miss; gold `unknown`; raw `0 per 8 week`; adapted `0 per 8 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3436: adapter regression; gold `unknown`; raw `unknown`; adapted `None`; taxonomy `missing_selected_operands`
- 3468: raw and adapted miss; gold `unknown`; raw `1 per 28 day`; adapted `6 per 28 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3469: raw and adapted miss; gold `unknown`; raw `1 per 7 day`; adapted `1 per 7 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3482: raw and adapted miss; gold `unknown`; raw `1 per 6 month`; adapted `1 per 6 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3493: raw and adapted miss; gold `unknown`; raw `1 per 6 day`; adapted `1 per 6 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3507: adapter regression; gold `unknown`; raw `unknown`; adapted `None`; taxonomy `missing_selected_operands`
- 3512: adapter regression; gold `unknown`; raw `unknown`; adapted `None`; taxonomy `missing_selected_operands`
- 3528: raw and adapted miss; gold `unknown`; raw `frequent per unspecified unit`; adapted `None`; taxonomy `missing_selected_operands`
- 3532: adapter regression; gold `unknown`; raw `unknown`; adapted `None`; taxonomy `missing_selected_operands`
- 3534: raw and adapted miss; gold `unknown`; raw `seizure free for 7 month`; adapted `seizure free for 7 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3623: raw and adapted miss; gold `7 per week`; raw `up to 7 per 1 week`; adapted `None`; taxonomy `missing_selected_operands`
- 3643: adapter regression; gold `7 per week`; raw `7 per 1 week`; adapted `None`; taxonomy `missing_selected_operands`
- 3988: raw and adapted miss; gold `multiple per week`; raw `3 to 7 per 1 week`; adapted `3 to 7 per 1 week`; taxonomy `exact_evidence_failure`
- 3995: raw and adapted miss; gold `1 per month`; raw `multiple per month`; adapted `multiple per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 3999: adapter regression; gold `1 per month`; raw `1 per 1 month`; adapted `None`; taxonomy `missing_selected_operands`
- 4092: raw and adapted miss; gold `1 per 2 to 3 week`; raw `2 to 3 per 1 week`; adapted `2 to 3 per 1 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4116: raw and adapted miss; gold `1 per 1 to 2 day`; raw `1 to 2 per 1 day`; adapted `1 to 2 per 1 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4337: raw and adapted miss; gold `3 per 3 month`; raw `3 per 7 month`; adapted `3 per 7 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4402: raw and adapted miss; gold `7 per 7 month`; raw `1 to 2 per month`; adapted `1 to 2 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4410: raw and adapted miss; gold `4 per 7 month`; raw `1 per month`; adapted `1 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4592: adapter regression; gold `1 per 2 month`; raw `1 per 60 day`; adapted `None`; taxonomy `missing_selected_operands`
- 4690: raw and adapted miss; gold `multiple per day`; raw `frequent per day`; adapted `None`; taxonomy `missing_selected_operands`
- 4694: raw and adapted miss; gold `multiple per day`; raw `9 per day`; adapted `9 per 1 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4700: raw and adapted miss; gold `multiple per day`; raw `4 per hour`; adapted `4 per 1 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4709: raw and adapted miss; gold `multiple per day`; raw `6 per hour`; adapted `6 per 1 year`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4731: raw and adapted miss; gold `unknown`; raw `rare per unspecified unit`; adapted `None`; taxonomy `missing_selected_operands`
- 4732: raw and adapted miss; gold `unknown`; raw `occasional`; adapted `None`; taxonomy `missing_selected_operands`
- 4771: raw and adapted miss; gold `unknown`; raw `1 per 1 month`; adapted `1 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 4842: adapter regression; gold `seizure free for multiple month`; raw `seizure free`; adapted `None`; taxonomy `missing_selected_operands`
- 5092: raw and adapted miss; gold `seizure free for multiple month`; raw `no seizure frequency reference`; adapted `no seizure frequency reference`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 5110: raw and adapted miss; gold `seizure free for multiple month`; raw `no seizure frequency reference`; adapted `no seizure frequency reference`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 5121: raw and adapted miss; gold `seizure free for multiple month`; raw `no seizure frequency reference`; adapted `no seizure frequency reference`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 5197: adapter regression; gold `seizure free for multiple month`; raw `seizure free`; adapted `None`; taxonomy `missing_selected_operands`
- 5210: adapter regression; gold `seizure free for multiple month`; raw `seizure free`; adapted `None`; taxonomy `missing_selected_operands`
- 5476: raw and adapted miss; gold `unknown`; raw `1 per 1 month`; adapted `1 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 5491: raw and adapted miss; gold `unknown`; raw `2 per 6 week`; adapted `2 per 6 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 5504: raw and adapted miss; gold `unknown`; raw `occasional per year`; adapted `None`; taxonomy `missing_selected_operands`
- 5507: raw and adapted miss; gold `unknown`; raw `3 per 4 month`; adapted `3 per 4 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 5534: raw and adapted miss; gold `1 per multiple month`; raw `1 per 14 day`; adapted `1 per 14 day`; taxonomy `wrong_selected_clinical_fact_or_operand`

## Failure Taxonomy

- `exact_evidence_failure`: 9
- `missing_selected_operands`: 23
- `ok`: 177
- `wrong_selected_clinical_fact_or_operand`: 41

## Interpretation

This Decision 0007 replay fails at least one hard selected-fact, evidence, operand, adapter, or projection gate. Do not escalate this artifact.
