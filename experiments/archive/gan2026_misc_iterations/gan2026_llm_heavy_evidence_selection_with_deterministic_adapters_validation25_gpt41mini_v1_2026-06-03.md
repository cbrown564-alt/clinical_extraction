# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters

- JSONL: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_2026-06-03.jsonl`
- Architecture: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Claim language: LLM-heavy clinical selection with deterministic mechanical adapters.
- Prompt/program version: `gan2026_llm_heavy_evidence_selection_deterministic_adapters_v1`
- Typed output schema version: `selected_fact_operands_v1`
- Split: `validation` / `gan2026_split_v1`
- Rows: 1
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Replay source: `None`
- Primary score layer: `final_projected_label`
- Decision 0007 outcome: `reject`

## Replay Scope

- Surface: `validation1` under `gan2026_split_v1`.
- Primary question: can typed selected fact/evidence/operand output support mechanical adapters and the final projection layer without deterministic clinical replacement?
- Stop rule: do not escalate broader validation until raw/mechanical/final ablations are recorded.

## Replay Summary

- Structured typed outputs: 0/1
- Reused raw outputs: 0/1
- Adapter parse failures: 0
- Selected evidence exact: 0/1
- Selected fact trace mismatches: 0
- Selected operand completeness: 0/1

## Score Layers

- `raw_model_parser_label`: scorable 0, Purist 0/1 (0.0000), Pragmatic 0/1 (0.0000)
- `raw_model_clinical_selection`: scorable 0, Purist 0/1 (0.0000), Pragmatic 0/1 (0.0000)
- `format_only_repair`: scorable 0, Purist 0/1 (0.0000), Pragmatic 0/1 (0.0000)
- `mechanical_adapter_label`: scorable 0, Purist 0/1 (0.0000), Pragmatic 0/1 (0.0000)
- `benchmark_convention_adapter`: scorable 0, Purist 0/1 (0.0000), Pragmatic 0/1 (0.0000)
- `final_projected_label`: scorable 0, Purist 0/1 (0.0000), Pragmatic 0/1 (0.0000)

## Adapter Gate

- Adapted-label Purist: 0/1
- Final projected-label Purist: 0/1
- Adapter raw-wrong to correct: 0
- Adapter raw-correct to wrong: 0
- Final projection raw-wrong to correct: 0
- Final projection raw-correct to wrong: 0
- Final projection mechanical-wrong to correct: 0
- Final projection mechanical-correct to wrong: 0

## Final Projection Families

- No final projection repair families fired.

## Row Review

- 10: raw and adapted miss; gold `4 per day`; raw `None`; adapted `None`; taxonomy `call_failure`

## Failure Taxonomy

- `call_failure`: 1

## Interpretation

This Decision 0007 replay fails at least one hard selected-fact, evidence, operand, adapter, or projection gate. Do not escalate this artifact.
