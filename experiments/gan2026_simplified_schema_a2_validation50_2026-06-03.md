# Gan 2026 LLM-Only Sparse Operands Selected State Reasoner

- JSONL: `/Users/cobro/code/clinical-extraction/experiments/gan2026_simplified_schema_a2_validation50_2026-06-03.jsonl`
- Architecture: `llm_only_sparse_operands_selected_state_reasoner`
- Prompt/program version: `gan2026_llm_only_sparse_operands_selected_state_reasoner_v1_boundaryfix`
- Typed output schema version: `sparse_operands_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-only sparse-operands validation development result; format, selected-evidence, and operand rendering are separate adapter layers.

## A2 Target

- one selected clinical state.
- Exact selected evidence.
- Sparse nullable operands for selected count, interval, cluster, or duration.
- No operation graph projection.

## Smoke Summary

- Structured records: 50/50
- Parse/schema failures: 0
- Selected evidence valid: 47/50
- Selected-state trace mismatches: 0
- Sparse operand boundary failures: 0

## Score Layers

- `raw_llm`: scorable 32, Purist 30/50 (0.6000), Pragmatic 31/50 (0.6200)
- `format_only`: scorable 42, Purist 40/50 (0.8000), Pragmatic 41/50 (0.8200)
- `selected_evidence_arithmetic`: scorable 50, Purist 47/50 (0.9400), Pragmatic 48/50 (0.9600)
- `sparse_operand_adapter`: scorable 50, Purist 48/50 (0.9600), Pragmatic 49/50 (0.9800)

## Adapter Delta

- Sparse operand adapter selected-evidence wrong to correct: 1
- Sparse operand adapter selected-evidence correct to wrong: 0

## Row Review

- 278: gold `multiple per week`; selected-evidence `1 per week`; sparse-operands `1 per week`
- 816: gold `1 per month`; selected-evidence `4 per 10 month`; sparse-operands `4 per 1 year`
- 1030: gold `1 to 3 per month`; selected-evidence `1 per month`; sparse-operands `1 to 3 per 1 month`
