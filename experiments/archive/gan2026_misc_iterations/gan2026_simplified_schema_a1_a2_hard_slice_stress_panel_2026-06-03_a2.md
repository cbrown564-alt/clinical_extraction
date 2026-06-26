# Gan 2026 LLM-Only Sparse Operands Selected State Reasoner

- JSONL: `/Users/cobro/code/clinical-extraction/experiments/gan2026_simplified_schema_a1_a2_hard_slice_stress_panel_2026-06-03_a2.jsonl`
- Architecture: `llm_only_sparse_operands_selected_state_reasoner`
- Prompt/program version: `gan2026_llm_only_sparse_operands_selected_state_reasoner_v1_boundaryfix`
- Typed output schema version: `sparse_operands_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 21
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-only sparse-operands validation development result; format, selected-evidence, and operand rendering are separate adapter layers.

## A2 Target

- one selected clinical state.
- Exact selected evidence.
- Sparse nullable operands for selected count, interval, cluster, or duration.
- No operation graph projection.

## Smoke Summary

- Structured records: 21/21
- Parse/schema failures: 0
- Selected evidence valid: 20/21
- Selected-state trace mismatches: 0
- Sparse operand boundary failures: 0

## Score Layers

- `raw_llm`: scorable 6, Purist 5/21 (0.2381), Pragmatic 6/21 (0.2857)
- `format_only`: scorable 6, Purist 5/21 (0.2381), Pragmatic 6/21 (0.2857)
- `selected_evidence_arithmetic`: scorable 21, Purist 21/21 (1.0000), Pragmatic 21/21 (1.0000)
- `sparse_operand_adapter`: scorable 21, Purist 21/21 (1.0000), Pragmatic 21/21 (1.0000)

## Adapter Delta

- Sparse operand adapter selected-evidence wrong to correct: 0
- Sparse operand adapter selected-evidence correct to wrong: 0

## Row Review

- No selected-evidence misses or sparse-operand adapter regressions.
