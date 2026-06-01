# Gan 2026 Clean Policy Freeze Ladder V0

Date: 2026-06-01

This is a validation development no-call replay over saved structured LLM v0.5 raw outputs. It is not a final holdout or benchmark result.

## Freeze Decision

The current clean scorer-facing policy is frozen at the table-backed policy families already documented for vague quantity with explicit denominator, period shorthand, cluster syntax grammar, and single total/window phrasing. Upper-bound, diary, temporal, evidence-state, and cluster-reconstruction behavior remain named deterministic modules outside the clean policy.

- Split: `validation`, `gan2026_split_v1`
- Raw-output source: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- JSON summary: `experiments/gan2026_clean_policy_freeze_ladder_v0_2026-06-01.json`
- Reuse mode: no new model calls; raw, strict format-only, and clean policy are same-raw-output replays.

## Validation Ladder Summary

| Limit | Condition | Purist | Pragmatic | Parse/schema/label failures | Repair notes | Exact evidence | Changed vs previous | Improved | Regressed |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | raw_model_selection | 0.6800 (17 / 25) | 0.6800 (17 / 25) | 7 | 0 | 25 / 25 | 0 | 0 | 0 |
| 25 | strict_format_only | 0.8800 (22 / 25) | 0.8800 (22 / 25) | 2 | 12 | 25 / 25 | 12 | 5 | 0 |
| 25 | clean_scorer_facing_policy | 0.9200 (23 / 25) | 0.9600 (24 / 25) | 0 | 13 | 25 / 25 | 2 | 1 | 0 |
| 50 | raw_model_selection | 0.6800 (34 / 50) | 0.7200 (36 / 50) | 10 | 0 | 50 / 50 | 0 | 0 | 0 |
| 50 | strict_format_only | 0.8200 (41 / 50) | 0.8600 (43 / 50) | 3 | 17 | 50 / 50 | 17 | 7 | 0 |
| 50 | clean_scorer_facing_policy | 0.8600 (43 / 50) | 0.9200 (46 / 50) | 0 | 19 | 50 / 50 | 3 | 2 | 0 |

## 50-Row Clean Policy Delta

Rows changed by the clean scorer-facing policy relative to strict format-only repair:

| Row | Strict label | Clean label | Gold | Strict Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 187 | 1 cluster per week | 1 per week | 1 per 7 to 9 day | no | no | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 190 | 1 cluster per 4 week | 1 per 4 week | 1 per 4 week | no | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 744 | most weekdays | multiple per week | multiple per week | no | yes | final_label_repaired: 'most weekdays' -> 'multiple per week' |

## Interpretation

The 50-row ladder reports the required attribution layers separately: raw model selection, strict format-only benchmark repair, and the frozen clean scorer-facing policy. The clean policy improves the strict condition without regressions on this focused slice, but it remains a scorer-facing normalization layer rather than a route for further semantic score gains.

Further metric gains should come from model selection/prompting or from explicitly named ablated modules. Do not expand the clean policy without a new direct-citation row-table gate and a corresponding policy decision artifact.
