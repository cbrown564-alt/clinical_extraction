# Gan 2026 Agentic Matched-Budget Prompt-Only Trace

Date: 2026-06-12

This is a no-call contract smoke for the Phase 6 agentic comparison surface.
It records prompt plans, matched budgets, and tool trace schemas only.

## Summary

- Rows: 25
- Conditions: single_greedy, single_self_consistency_temperature, single_self_consistency_cross_model, single_agent_tools, multi_agent_matched
- Tool smoke calls: 104
- Prediction-bearing rows: 0
- JSONL artifact: `experiments\gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12.jsonl`

## Claim Boundary

validation-development prompt-only/no-call contract smoke; no prediction-bearing model outputs and no benchmark claim

## Condition Budgets

| Condition | Model calls | Tool calls | Tool output tokens | Aggregation calls |
| --- | ---: | ---: | ---: | ---: |
| single_greedy | 1 | 0 | 0 | 0 |
| single_self_consistency_temperature | 4 | 3 | 700 | 1 |
| single_self_consistency_cross_model | 4 | 3 | 700 | 1 |
| single_agent_tools | 4 | 3 | 700 | 1 |
| multi_agent_matched | 4 | 3 | 700 | 1 |

## Rows

| Row | Tool smoke calls | Attribution |
| ---: | ---: | --- |
| 10 | 4 | no_prediction |
| 40 | 4 | no_prediction |
| 79 | 4 | no_prediction |
| 103 | 4 | no_prediction |
| 128 | 4 | no_prediction |
| 156 | 4 | no_prediction |
| 180 | 4 | no_prediction |
| 182 | 4 | no_prediction |
| 187 | 4 | no_prediction |
| 190 | 4 | no_prediction |
| 198 | 4 | no_prediction |
| 212 | 4 | no_prediction |
| 218 | 4 | no_prediction |
| 243 | 4 | no_prediction |
| 278 | 6 | no_prediction |
| 280 | 4 | no_prediction |
| 338 | 4 | no_prediction |
| 409 | 4 | no_prediction |
| 419 | 4 | no_prediction |
| 446 | 4 | no_prediction |
| 466 | 6 | no_prediction |
| 467 | 4 | no_prediction |
| 531 | 4 | no_prediction |
| 598 | 4 | no_prediction |
| 659 | 4 | no_prediction |
