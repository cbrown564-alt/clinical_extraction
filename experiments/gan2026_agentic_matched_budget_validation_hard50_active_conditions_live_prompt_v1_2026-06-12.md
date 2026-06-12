# Gan 2026 Agentic Matched-Budget Trace

Date: 2026-06-12

This is a Phase 6 matched-budget agentic comparison surface.
Prompt-only runs record plans and tool schemas; live runs add model outputs.
Prompt-only mode remains a no-call contract smoke.

## Summary

- Rows: 50
- Conditions: single_greedy, single_self_consistency_temperature, single_agent_tools, multi_agent_matched
- Tool smoke calls: 248
- Prediction-bearing rows: 50
- Model calls attempted: 500
- Call failures: 0
- Decision records: 500
- Blocking parse/validation failures: 0
- Normalized-label vote repairs: 0
- Hard-slice manifest:
  `experiments\gan2026_agentic_validation_hard50_manifest_2026-06-12.json`
- JSONL artifact: `experiments\gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.jsonl`

## Experiment Unit

- Saturation evidence: validation25 active single-agent conditions and
  `multi_agent_matched` all reached `25/25` Purist/Pragmatic condition-final
  accuracy.
- Surface: fixed validation hard50 slice from the validation-only atlas manifest;
  first 50 unique source rows in source-manifest order, selected before this run.
- Targeted failure modes: unknown/seizure-free boundaries, current versus
  historical conflict, competing semiologies, cluster burden, denominator/rate
  conversion, benchmark-format conventions, and projection arbitration.
- Inspection policy: validation row-level review only; no locked-test row-level
  inspection and no scorer/prompt tuning from holdout.
- Stop rule: do not move an agentic condition to full validation unless hard50
  produces an interpretable promote/revise signal without systemic call, parse,
  or schema failures.

## Condition-Final Accuracy

| Condition | Purist | Pragmatic | Unscorable final labels |
| --- | ---: | ---: | ---: |
| single_greedy | 34/50 | 36/50 | 0 |
| single_self_consistency_temperature | 32/50 | 34/50 | 0 |
| single_agent_tools | 20/50 | 22/50 | 0 |
| multi_agent_matched | 22/50 | 24/50 | 0 |

## Slice Summary

Rows can belong to more than one predeclared slice.

| Slice | Rows | single_greedy | self_consistency_temperature | single_agent_tools | multi_agent_matched |
| --- | ---: | ---: | ---: | ---: | ---: |
| candidate_generation_rescue | 44 | 29/44 | 27/44 | 15/44 | 17/44 |
| candidate_generation_unknown_seizure_free_boundary | 26 | 16/26 | 15/26 | 11/26 | 11/26 |
| projection_arbitration | 6 | 5/6 | 5/6 | 5/6 | 5/6 |
| projection_unknown_seizure_free_arbitration | 2 | 1/2 | 1/2 | 1/2 | 1/2 |

## Matched-Budget Win/Loss

Compared with `single_self_consistency_temperature` on Purist condition-final
correctness:

| Candidate | Wins | Losses | Both correct | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| single_agent_tools | 0 | 12 | 20 | 18 |
| multi_agent_matched | 0 | 10 | 22 | 18 |

The regression rows cluster around seizure-free/current-history confusion,
competing semiologies, rate-denominator selection, and cluster-burden handling.
Several tool/multi-agent failures convert a frequency-bearing hard case into a
seizure-free or low-frequency answer.

## Interpretation

This hard validation50 slice differentiates the saturated validation25 result:
the active tool-using and multi-agent conditions are revise/reject signals as
currently shaped, not candidates for full validation. `single_greedy` is the
best condition-final performer on this slice, followed by same-model
self-consistency. `multi_agent_matched` does not show a high-precision correction
profile over the matched single-agent comparator and should not be promoted or
escalated to full validation without redesigning the tool context/role policy
and rerunning this fixed hard slice.

## Claim Boundary

validation-development matched-budget agentic trace; no holdout use, no row-level test inspection, and no benchmark claim

## Condition Budgets

| Condition | Model calls | Tool calls | Tool output tokens | Aggregation calls |
| --- | ---: | ---: | ---: | ---: |
| single_greedy | 1 | 0 | 0 | 0 |
| single_self_consistency_temperature | 4 | 3 | 700 | 1 |
| single_agent_tools | 4 | 3 | 700 | 1 |
| multi_agent_matched | 4 | 3 | 700 | 1 |

## Rows

| Row | Tool smoke calls | Attribution |
| ---: | ---: | --- |
| 3356 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 3528 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 4690 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 5534 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 5974 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 6077 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 6094 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 6131 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 6153 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 6209 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 6244 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 6321 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 6368 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 6501 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 6571 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 6987 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 7168 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 7615 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 9496 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 9888 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 9937 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 9943 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 9955 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 10266 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 10618 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 10677 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 10996 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 12422 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 12438 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 12456 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 12460 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 12468 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 13843 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 13858 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 13889 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 14025 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 14076 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 14810 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 14821 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 15168 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 15193 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 15593 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 15672 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 15834 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 2748 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 4368 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 5921 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 6889 | 4 | raw_model, raw_model_plus_deterministic_format_vote |
| 10386 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
| 11216 | 6 | raw_model, raw_model_plus_deterministic_format_vote |
