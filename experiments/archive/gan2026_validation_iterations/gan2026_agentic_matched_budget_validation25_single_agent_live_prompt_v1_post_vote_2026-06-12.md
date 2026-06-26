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
- Blocking parse/validation failures: 0
- Normalized-label vote repairs: 70
- JSONL artifact: `experiments\gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.jsonl`

## Condition-Final Accuracy

| Condition | Purist | Pragmatic | Vote repair events |
| --- | ---: | ---: | ---: |
| single_greedy | 25/25 | 25/25 | 11 |
| single_self_consistency_temperature | 25/25 | 25/25 | 48 |
| single_agent_tools | 25/25 | 25/25 | 11 |

## Disagreement Rows

All condition-final labels on these rows are Purist/Pragmatic correct under the
current mapping.

| Row | single_greedy | single_self_consistency_temperature | single_agent_tools |
| ---: | --- | --- | --- |
| 10 | `multiple per day` | `multiple per day` | `4 per day` |
| 180 | `1 per week` | `1 per week` | `1 per 7 day` |
| 182 | `1 per 2 day` | `1 per 2 day` | `0.5 per day` |
| 187 | `2 per month` | `2 per month` | `1 per 7 to 9 day` |
| 338 | `multiple per day` | `multiple per month` | `unknown` |

Row `187` remains the expected scoring-equivalent disagreement. The
`single_agent_tools` raw label was `1 per 7 to 9 days`, normalized by
`benchmark_repair.normalize_units_first` to `1 per 7 to 9 day`; the other two
conditions selected `2 per month` without vote repair.

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
| 10 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 40 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 79 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 103 | 2 | raw_model_plus_deterministic_format_vote |
| 128 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 156 | 2 | raw_model_plus_deterministic_format_vote |
| 180 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 182 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 187 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 190 | 2 | raw_model_plus_deterministic_format_vote |
| 198 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 212 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 218 | 2 | raw_model_plus_deterministic_format_vote |
| 243 | 2 | raw_model_plus_deterministic_format_vote |
| 278 | 3 | raw_model, raw_model_plus_deterministic_format_vote |
| 280 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 338 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 409 | 2 | raw_model_plus_deterministic_format_vote |
| 419 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 446 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 466 | 3 | raw_model, raw_model_plus_deterministic_format_vote |
| 467 | 2 | raw_model, raw_model_plus_deterministic_format_vote |
| 531 | 2 | raw_model_plus_deterministic_format_vote |
| 598 | 2 | raw_model_plus_deterministic_format_vote |
| 659 | 2 | raw_model_plus_deterministic_format_vote |
