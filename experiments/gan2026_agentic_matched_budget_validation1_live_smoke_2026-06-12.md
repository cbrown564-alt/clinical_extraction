# Gan 2026 Agentic Matched-Budget Trace

Date: 2026-06-12

This is a Phase 6 matched-budget agentic comparison surface.
Prompt-only runs record plans and tool schemas; live runs add model outputs.
Prompt-only mode remains a no-call contract smoke.

## Summary

- Rows: 1
- Conditions: single_greedy, single_self_consistency_temperature, single_self_consistency_cross_model, single_agent_tools, multi_agent_matched
- Tool smoke calls: 4
- Prediction-bearing rows: 1
- Model calls attempted: 14
- Call failures: 0
- Decision records: 14
- JSONL artifact: `experiments\gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12.jsonl`

## Claim Boundary

validation-development matched-budget agentic trace; no holdout use, no row-level test inspection, and no benchmark claim

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
| 10 | 4 | raw_model |
