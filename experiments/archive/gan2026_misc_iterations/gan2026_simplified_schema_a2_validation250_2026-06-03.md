# Gan 2026 LLM-Only Sparse Operands Selected State Reasoner

- JSONL: `/Users/cobro/code/clinical-extraction/experiments/gan2026_simplified_schema_a2_validation250_2026-06-03.jsonl`
- Architecture: `llm_only_sparse_operands_selected_state_reasoner`
- Prompt/program version: `gan2026_llm_only_sparse_operands_selected_state_reasoner_v1_boundaryfix`
- Typed output schema version: `sparse_operands_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-only sparse-operands validation development result; format, selected-evidence, and operand rendering are separate adapter layers.

## A2 Target

- one selected clinical state.
- Exact selected evidence.
- Sparse nullable operands for selected count, interval, cluster, or duration.
- No operation graph projection.

## Smoke Summary

- Structured records: 248/250
- Parse/schema failures: 2
- Selected evidence valid: 237/250
- Selected-state trace mismatches: 0
- Sparse operand boundary failures: 0

## Score Layers

- `raw_llm`: scorable 160, Purist 148/250 (0.5920), Pragmatic 152/250 (0.6080)
- `format_only`: scorable 177, Purist 164/250 (0.6560), Pragmatic 169/250 (0.6760)
- `selected_evidence_arithmetic`: scorable 248, Purist 232/250 (0.9280), Pragmatic 238/250 (0.9520)
- `sparse_operand_adapter`: scorable 248, Purist 232/250 (0.9280), Pragmatic 240/250 (0.9600)

## Adapter Delta

- Sparse operand adapter selected-evidence wrong to correct: 4
- Sparse operand adapter selected-evidence correct to wrong: 4

## Row Review

- 187: gold `1 per 7 to 9 day`; selected-evidence `no seizure frequency reference`; sparse-operands `no seizure frequency reference`
- 816: gold `1 per month`; selected-evidence `4 per 10 month`; sparse-operands `4 per 1 year`
- 1030: gold `1 to 3 per month`; selected-evidence `1 per month`; sparse-operands `1 to 3 per 1 month`
- 1573: gold `11 per week`; selected-evidence `5 to 6 per week`; sparse-operands `11 per 1 week`
- 1695: gold `multiple per month`; selected-evidence `no seizure frequency reference`; sparse-operands `3 to 5 per 1 month`
- 1880: gold `8 per 2 month`; selected-evidence `None`; sparse-operands `None`
- 2023: gold `5 per month`; selected-evidence `no seizure frequency reference`; sparse-operands `5 per 1 month`
- 2080: gold `multiple per month`; selected-evidence `multiple per day`; sparse-operands `2 to 5 per 1 month`
- 3242: gold `2 cluster per month, 5 per cluster`; selected-evidence `2 cluster per month, multiple per cluster`; sparse-operands `2 cluster per month, multiple per cluster`
- 3261: gold `2 cluster per month, 4 per cluster`; selected-evidence `2 cluster per month, multiple per cluster`; sparse-operands `2 cluster per month, multiple per cluster`
- 3262: gold `2 cluster per month, 5 per cluster`; selected-evidence `2 cluster per month, multiple per cluster`; sparse-operands `2 cluster per month, multiple per cluster`
- 3371: gold `unknown`; selected-evidence `seizure free for multiple year`; sparse-operands `seizure free for 8 week`
- 3534: gold `unknown`; selected-evidence `seizure free for 7 month`; sparse-operands `seizure free for 7 month`
- 3681: gold `9 per month`; selected-evidence `9 per month`; sparse-operands `9 per 3 month`
- 4337: gold `3 per 3 month`; selected-evidence `no seizure frequency reference`; sparse-operands `3 per 1 year`
- 4410: gold `4 per 7 month`; selected-evidence `4 per 7 month`; sparse-operands `1 per 1 month`
- 4562: gold `1 per 6 week`; selected-evidence `None`; sparse-operands `None`
- 4592: gold `1 per 2 month`; selected-evidence `no seizure frequency reference`; sparse-operands `1 per 2 month`
- 4624: gold `1 per 3 to 4 day`; selected-evidence `2 per month`; sparse-operands `2 per 1 month`
- 5092: gold `seizure free for multiple month`; selected-evidence `no seizure frequency reference`; sparse-operands `no seizure frequency reference`
- 5406: gold `seizure free for multiple month`; selected-evidence `no seizure frequency reference`; sparse-operands `no seizure frequency reference`
- 5534: gold `1 per multiple month`; selected-evidence `1 per 14 day`; sparse-operands `1 per 14 day`
