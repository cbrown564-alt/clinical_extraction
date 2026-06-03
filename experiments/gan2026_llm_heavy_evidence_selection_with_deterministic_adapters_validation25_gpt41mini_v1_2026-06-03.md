# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters

- JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_2026-06-03.jsonl`
- Architecture: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Claim language: LLM-heavy clinical selection with deterministic mechanical adapters.
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Typed output schema version: `selected_fact_operands_v1`
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
- Selected evidence exact: 22/25
- Selected fact trace mismatches: 0
- Selected operand completeness: 25/25

## Score Layers

- `raw_model_parser_label`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `raw_model_clinical_selection`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `format_only_repair`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `mechanical_adapter_label`: scorable 25, Purist 23/25 (0.9200), Pragmatic 24/25 (0.9600)
- `benchmark_convention_adapter`: scorable 25, Purist 23/25 (0.9200), Pragmatic 24/25 (0.9600)

## Adapter Gate

- Adapted-label Purist: 23/25
- Adapter raw-wrong to correct: 0
- Adapter raw-correct to wrong: 2

## Row Review

- 187: adapter regression; gold `1 per 7 to 9 day`; raw `1 per 7 to 9 day`; adapted `1 cluster per 7 to 9 day, multiple per cluster`; taxonomy `wrong_selected_clinical_fact_or_operand`
- 190: adapter regression; gold `1 per 4 week`; raw `1 per 4 week`; adapted `1 cluster per 4 week, multiple per cluster`; taxonomy `wrong_selected_clinical_fact_or_operand`

## Failure Taxonomy

- `exact_evidence_failure`: 3
- `ok`: 20
- `wrong_selected_clinical_fact_or_operand`: 2

## Interpretation

This validation25 Decision 0007 smoke fails at least one hard selected-fact, evidence, operand, or adapter gate. Do not escalate this artifact.
