# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters

- JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation50_gpt41mini_v1_2026-06-03.jsonl`
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
- Selected evidence exact: 49/50
- Selected fact trace mismatches: 0
- Selected operand completeness: 49/50

## Score Layers

- `raw_model_parser_label`: scorable 50, Purist 45/50 (0.9000), Pragmatic 47/50 (0.9400)
- `raw_model_clinical_selection`: scorable 50, Purist 45/50 (0.9000), Pragmatic 47/50 (0.9400)
- `format_only_repair`: scorable 50, Purist 45/50 (0.9000), Pragmatic 47/50 (0.9400)
- `mechanical_adapter_label`: scorable 49, Purist 44/50 (0.8800), Pragmatic 46/50 (0.9200)
- `benchmark_convention_adapter`: scorable 49, Purist 44/50 (0.8800), Pragmatic 46/50 (0.9200)

## Adapter Gate

- Adapted-label Purist: 44/50
- Adapter raw-wrong to correct: 0
- Adapter raw-correct to wrong: 1

## Row Review

- 743: adapter regression; gold `multiple per week`; raw `multiple per shift`; adapted `None`; taxonomy `missing_selected_operands`
- 744: raw and adapted miss; gold `multiple per week`; raw `3 to 5 per 7 day`; adapted `3 to 5 per 7 day`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 816: raw and adapted miss; gold `1 per month`; raw `4 per 1 year`; adapted `4 per 1 year`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 891: raw and adapted miss; gold `1 per 2 day`; raw `3 to 4 per 6 week`; adapted `3 to 4 per 6 week`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 959: raw and adapted miss; gold `1 per 2 month`; raw `2 per 1 to 2 month`; adapted `2 per 1 to 2 month`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 987: raw and adapted miss; gold `1 per 2 month`; raw `2 per 1 month`; adapted `2 per 1 month`; taxonomy `wrong_selected_clinical_fact_or_operand`

## Failure Taxonomy

- `exact_evidence_failure`: 1
- `missing_selected_operands`: 1
- `ok`: 43
- `wrong_selected_clinical_fact_or_operand`: 5

## Interpretation

This validation25 Decision 0007 smoke passes the typed-output and mechanical-adapter gate. Escalation may be considered only as a separately predeclared validation50 run.
