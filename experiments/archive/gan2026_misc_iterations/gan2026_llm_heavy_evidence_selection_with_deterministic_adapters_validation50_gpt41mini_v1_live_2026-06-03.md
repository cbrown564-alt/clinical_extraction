# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters

- JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation50_gpt41mini_v1_live_2026-06-03.jsonl`
- Architecture: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Claim language: LLM-heavy clinical selection with deterministic mechanical adapters.
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Typed output schema version: `selected_fact_operands_v1`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Primary adapted layer: `mechanical_adapter_label`
- Decision 0007 outcome: `promote_to_validation50_allowed_by_gate`

## Predeclared Smoke

- Surface: `validation25` under `gan2026_split_v1`.
- Primary question: can typed selected fact/evidence/operand output support mechanical adapters without deterministic clinical replacement?
- Stop rule: promotion requires the Decision 0007 validation25 gate.

## Smoke Summary

- Structured typed outputs: 50/50
- Adapter parse failures: 0
- Selected evidence exact: 47/50
- Selected fact trace mismatches: 0
- Selected operand completeness: 49/50

## Score Layers

- `raw_model_parser_label`: scorable 49, Purist 44/50 (0.8800), Pragmatic 45/50 (0.9000)
- `raw_model_clinical_selection`: scorable 49, Purist 44/50 (0.8800), Pragmatic 45/50 (0.9000)
- `format_only_repair`: scorable 49, Purist 44/50 (0.8800), Pragmatic 45/50 (0.9000)
- `mechanical_adapter_label`: scorable 49, Purist 44/50 (0.8800), Pragmatic 45/50 (0.9000)
- `benchmark_convention_adapter`: scorable 49, Purist 44/50 (0.8800), Pragmatic 45/50 (0.9000)

## Adapter Gate

- Adapted-label Purist: 44/50
- Adapter raw-wrong to correct: 1
- Adapter raw-correct to wrong: 1

## Row Review

- 10: raw and adapted miss; gold `4 per day`; raw `multiple per day`; adapted `multiple per 1 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 743: adapter regression; gold `multiple per week`; raw `multiple per shift`; adapted `None`; taxonomy `missing_selected_operands`
- 744: raw and adapted miss; gold `multiple per week`; raw `4 to 5 per 7 day`; adapted `4 to 5 per 7 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 790: mechanical adapter gain; gold `1 per 7 to 10 day`; raw `1 per 7 to 1 per 10 day`; adapted `1 per 7 to 10 day`; taxonomy `ok`
- 816: raw and adapted miss; gold `1 per month`; raw `4 per year`; adapted `4 per 1 year`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 959: raw and adapted miss; gold `1 per 2 month`; raw `1 to 2 per 1 to 2 month`; adapted `1 to 2 per 1 to 2 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 987: raw and adapted miss; gold `1 per 2 month`; raw `2 per 1 to 2 month`; adapted `2 per 1 to 2 month`; taxonomy `wrong_selected_clinical_fact_or_operand`

## Failure Taxonomy

- `exact_evidence_failure`: 3
- `missing_selected_operands`: 1
- `ok`: 41
- `wrong_selected_clinical_fact_or_operand`: 5

## Interpretation

This validation25 Decision 0007 smoke passes the typed-output and mechanical-adapter gate. Escalation may be considered only as a separately predeclared validation50 run.
