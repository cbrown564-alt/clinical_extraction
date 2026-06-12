# Gan 2026 Agentic Matched-Budget Trace

Date: 2026-06-12

This is a Phase 6 matched-budget agentic comparison surface.
Prompt-only runs record plans and tool schemas; live runs add model outputs.
Prompt-only mode remains a no-call contract smoke.

## Summary

- Rows: 25
- Conditions: single_greedy, single_self_consistency_temperature, single_agent_tools
- Tool smoke calls: 52
- Prediction-bearing rows: 25
- Model calls attempted: 150
- Call failures: 0
- Decision records: 150
- JSONL artifact: `experiments\gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12.jsonl`

## Claim Boundary

validation-development matched-budget agentic trace; no holdout use, no row-level test inspection, and no benchmark claim

## Condition Budgets

| Condition | Model calls | Tool calls | Tool output tokens | Aggregation calls |
| --- | ---: | ---: | ---: | ---: |
| single_greedy | 1 | 0 | 0 | 0 |
| single_self_consistency_temperature | 4 | 3 | 700 | 1 |
| single_agent_tools | 4 | 3 | 700 | 1 |

## Rows

| Row | Tool smoke calls | Attribution |
| ---: | ---: | --- |
| 10 | 2 | raw_model |
| 40 | 2 | raw_model |
| 79 | 2 | raw_model |
| 103 | 2 | raw_model |
| 128 | 2 | raw_model |
| 156 | 2 | raw_model |
| 180 | 2 | raw_model |
| 182 | 2 | raw_model |
| 187 | 2 | raw_model |
| 190 | 2 | raw_model |
| 198 | 2 | raw_model |
| 212 | 2 | raw_model |
| 218 | 2 | raw_model |
| 243 | 2 | raw_model |
| 278 | 3 | raw_model |
| 280 | 2 | raw_model |
| 338 | 2 | raw_model |
| 409 | 2 | raw_model |
| 419 | 2 | raw_model |
| 446 | 2 | raw_model |
| 466 | 3 | raw_model |
| 467 | 2 | raw_model |
| 531 | 2 | raw_model |
| 598 | 2 | raw_model |
| 659 | 2 | raw_model |
