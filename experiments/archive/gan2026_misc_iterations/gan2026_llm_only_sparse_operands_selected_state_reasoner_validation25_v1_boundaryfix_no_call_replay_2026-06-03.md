# Gan 2026 LLM-Only Sparse Operands Selected State Reasoner

- JSONL: `experiments/gan2026_llm_only_sparse_operands_selected_state_reasoner_validation25_v1_boundaryfix_no_call_replay_2026-06-03.jsonl`
- Architecture: `llm_only_sparse_operands_selected_state_reasoner`
- Prompt/program version: `gan2026_llm_only_sparse_operands_selected_state_reasoner_v1_boundaryfix`
- Typed output schema version: `sparse_operands_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `no-call-replay`
- Claim language: LLM-only sparse-operands validation development result; format, selected-evidence, and operand rendering are separate adapter layers.

## A2 Target

- one selected clinical state.
- Exact selected evidence.
- Sparse nullable operands for selected count, interval, cluster, or duration.
- No operation graph projection.

## Smoke Summary

- Structured records: 25/25
- Parse/schema failures: 0
- Selected evidence valid: 23/25
- Selected-state trace mismatches: 0
- Sparse operand boundary failures: 0

## Score Layers

- `raw_llm`: scorable 14, Purist 14/25 (0.5600), Pragmatic 14/25 (0.5600)
- `format_only`: scorable 21, Purist 21/25 (0.8400), Pragmatic 21/25 (0.8400)
- `selected_evidence_arithmetic`: scorable 25, Purist 23/25 (0.9200), Pragmatic 23/25 (0.9200)
- `sparse_operand_adapter`: scorable 25, Purist 23/25 (0.9200), Pragmatic 23/25 (0.9200)

## Adapter Delta

- Sparse operand adapter selected-evidence wrong to correct: 0
- Sparse operand adapter selected-evidence correct to wrong: 0

## Row Review

- 187: gold `1 per 7 to 9 day`; selected-evidence `no seizure frequency reference`; sparse-operands `no seizure frequency reference`
- 278: gold `multiple per week`; selected-evidence `1 per week`; sparse-operands `1 per week`
