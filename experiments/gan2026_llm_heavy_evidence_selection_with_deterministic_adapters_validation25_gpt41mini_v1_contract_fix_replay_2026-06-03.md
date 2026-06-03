# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters

- JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_contract_fix_replay_2026-06-03.jsonl`
- Architecture: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Claim language: LLM-heavy clinical selection with deterministic mechanical adapters.
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Typed output schema version: `selected_fact_operands_v1`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `saved-output-replay`
- Primary adapted layer: `mechanical_adapter_label`
- Decision 0007 outcome: `promote_to_validation50_allowed_by_gate`

## Predeclared Smoke

- Surface: `validation25` under `gan2026_split_v1`.
- Primary question: can typed selected fact/evidence/operand output support mechanical adapters without deterministic clinical replacement?
- Stop rule: promotion requires the Decision 0007 validation25 gate.

## Smoke Summary

- Structured typed outputs: 25/25
- Adapter parse failures: 0
- Selected evidence exact: 25/25
- Selected fact trace mismatches: 0
- Selected operand completeness: 25/25

## Score Layers

- `raw_model_parser_label`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `raw_model_clinical_selection`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `format_only_repair`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `mechanical_adapter_label`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `benchmark_convention_adapter`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)

## Adapter Gate

- Adapted-label Purist: 25/25
- Adapter raw-wrong to correct: 0
- Adapter raw-correct to wrong: 0

## Row Review

- No raw misses or mechanical-adapter regressions.

## Failure Taxonomy

- `ok`: 25

## Interpretation

This validation25 Decision 0007 smoke passes the typed-output and mechanical-adapter gate. Escalation may be considered only as a separately predeclared validation50 run.
