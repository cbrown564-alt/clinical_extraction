# Gan 2026 Agentic Matched-Budget Trace

Date: 2026-06-12

This is a Phase 6 matched-budget agentic comparison surface.
Prompt-only runs record plans and tool schemas; live runs add model outputs.
Prompt-only mode remains a no-call contract smoke.

## Summary

- Rows: 25
- Conditions: multi_agent_matched
- Tool smoke calls: 52
- Prediction-bearing rows: 25
- Model calls attempted: 100
- Call failures: 0
- Decision records: 100
- Blocking parse/validation failures: 0
- Normalized-label vote repairs: 0
- JSONL artifact: `experiments\gan2026_agentic_matched_budget_validation25_multi_agent_live_prompt_v1_2026-06-12.jsonl`

## Condition-Final Accuracy

| Condition | Purist | Pragmatic | Unscorable final labels |
| --- | ---: | ---: | ---: |
| multi_agent_matched | 25/25 | 25/25 | 0 |

## Comparator Notes

The corrected condition-final vote uses parser-repaired decision labels while
retaining raw model labels for attribution. All disagreement rows below remain
Purist/Pragmatic correct under the current mapping.

| Row | multi_agent_matched | single_greedy | single_self_consistency_temperature | single_agent_tools |
| ---: | --- | --- | --- | --- |
| 10 | `4 per day` | `multiple per day` | `multiple per day` | `4 per day` |
| 103 | `2 to 4 per year` | `2 or 4 per year` | `2 or 4 per year` | `2 or 4 per year` |
| 180 | `1 per 7 day` | `1 per week` | `1 per week` | `1 per 7 day` |
| 182 | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `0.5 per day` |
| 187 | `1 per 7 to 9 day` | `2 per month` | `2 per month` | `1 per 7 to 9 day` |
| 190 | `1 per 4 week` | `clusters 1 per 4 week` | `clusters 1 per 4 week` | `clusters 1 per 4 week` |
| 198 | `1 per 4 week` | `1 per month` | `1 per month` | `1 per month` |
| 212 | `1 per 3 to 4 week` | `1 per month` | `1 per month` | `1 per month` |
| 338 | `multiple per month` | `multiple per day` | `multiple per month` | `unknown` |

Interpretation: this validation25 smoke does not support a multi-agent
superiority claim over the matched-budget single-agent comparator; both are at
ceiling on this surface. It does show that specialist roles can reach the same
score while shifting format and boundary selections, so the next useful step is
a compact failure-mode and hard-slice comparison rather than another broad
validation25 repeat.

## Claim Boundary

validation-development matched-budget agentic trace; no holdout use, no row-level test inspection, and no benchmark claim

## Condition Budgets

| Condition | Model calls | Tool calls | Tool output tokens | Aggregation calls |
| --- | ---: | ---: | ---: | ---: |
| multi_agent_matched | 4 | 3 | 700 | 1 |

## Rows

| Row | Tool smoke calls | Attribution |
| ---: | ---: | --- |
| 10 | 2 | raw_model_plus_deterministic_format_vote |
| 40 | 2 | raw_model_plus_deterministic_format_vote |
| 79 | 2 | raw_model_plus_deterministic_format_vote |
| 103 | 2 | raw_model_plus_deterministic_format_vote |
| 128 | 2 | raw_model_plus_deterministic_format_vote |
| 156 | 2 | raw_model_plus_deterministic_format_vote |
| 180 | 2 | raw_model_plus_deterministic_format_vote |
| 182 | 2 | raw_model_plus_deterministic_format_vote |
| 187 | 2 | raw_model_plus_deterministic_format_vote |
| 190 | 2 | raw_model_plus_deterministic_format_vote |
| 198 | 2 | raw_model_plus_deterministic_format_vote |
| 212 | 2 | raw_model_plus_deterministic_format_vote |
| 218 | 2 | raw_model_plus_deterministic_format_vote |
| 243 | 2 | raw_model_plus_deterministic_format_vote |
| 278 | 3 | raw_model_plus_deterministic_format_vote |
| 280 | 2 | raw_model_plus_deterministic_format_vote |
| 338 | 2 | raw_model_plus_deterministic_format_vote |
| 409 | 2 | raw_model_plus_deterministic_format_vote |
| 419 | 2 | raw_model_plus_deterministic_format_vote |
| 446 | 2 | raw_model_plus_deterministic_format_vote |
| 466 | 3 | raw_model_plus_deterministic_format_vote |
| 467 | 2 | raw_model_plus_deterministic_format_vote |
| 531 | 2 | raw_model_plus_deterministic_format_vote |
| 598 | 2 | raw_model_plus_deterministic_format_vote |
| 659 | 2 | raw_model_plus_deterministic_format_vote |
