# Gan 2026 Clean Policy Freeze Ladder 650 V0

Date: 2026-06-01

This is a validation-development no-call replay over 650 saved structured LLM v0.5 raw outputs. It is not a final holdout or benchmark result.

## Condition

- Split: `validation`, `gan2026_split_v1`
- Raw-output source: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- JSON summary: `experiments/gan2026_clean_policy_freeze_ladder650_v0_2026-06-01.json`
- Reuse mode: no new model calls; raw, strict format-only, and clean policy are same-raw-output replays.

## Ladder Summary

| Condition | Purist | Pragmatic | Exact label | Parse/schema/label failures | Repair rows | Repair notes | Exact evidence | Changed vs previous | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model_selection | 0.6062 (394 / 650) | 0.6338 (412 / 650) | 0.3138 (204 / 650) | 140 | 0 | 0 | 619 / 650 | 0 | 0 | 0 |
| strict_format_only | 0.6338 (412 / 650) | 0.6615 (430 / 650) | 0.4431 (288 / 650) | 121 | 224 | 224 | 619 / 650 | 224 | 18 | 0 |
| clean_scorer_facing_policy | 0.6738 (438 / 650) | 0.7308 (475 / 650) | 0.4646 (302 / 650) | 65 | 262 | 262 | 619 / 650 | 61 | 26 | 0 |

## Clean Policy Delta

Rows changed by the clean scorer-facing policy relative to strict format-only repair:

| Row | Strict label | Clean label | Gold | Strict Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 187 | 1 cluster per week | 1 per week | 1 per 7 to 9 day | no | no | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 190 | 1 cluster per 4 week | 1 per 4 week | 1 per 4 week | no | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 744 | most weekdays | multiple per week | multiple per week | no | yes | final_label_repaired: 'most weekdays' -> 'multiple per week' |
| 1687 | several per week | multiple per week | multiple per week | no | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 2080 | few per month | multiple per month | multiple per month | no | yes | final_label_repaired: 'a few per month' -> 'multiple per month' |
| 2094 | several per month | multiple per month | multiple per month | no | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2628 | 1 cluster per day | 1 per day | 1 per day | no | yes | final_label_repaired: '1 cluster per night' -> '1 per day' |
| 3242 | 2 clusters per month | 2 per month | 2 cluster per month, 5 per cluster | no | no | final_label_repaired: '2 clusters per month' -> '2 per month' |
| 3261 | 2 clusters per month | 2 per month | 2 cluster per month, 4 per cluster | no | no | final_label_repaired: '2 clusters per month' -> '2 per month' |
| 3262 | 2 clusters per month | 2 per month | 2 cluster per month, 5 per cluster | no | no | final_label_repaired: '2 clusters per month' -> '2 per month' |
| 4337 | 3 in last 6 month | 3 per 6 month | 3 per 3 month | no | no | final_label_repaired: '3 events in last 6 months' -> '3 per 6 month' |
| 4624 | 1 cluster every 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | no | yes | final_label_repaired: '1 cluster every 3 to 4 days' -> '1 per 3 to 4 day' |
| 5551 | several per day | multiple per day | multiple per day | no | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 5567 | several per week | multiple per week | multiple per week | no | yes | final_label_repaired: 'Several per week' -> 'multiple per week' |
| 5584 | several per week | multiple per week | multiple per week | no | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5977 | several per month | multiple per month | unknown | no | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 6094 | 5 in 6 week | 5 per 6 week | 3 per month | no | yes | final_label_repaired: '5 events in 6 weeks' -> '5 per 6 week' |
| 7167 | 3 clusters per 6 week | 3 per 6 week | 1 cluster per 2 weeks, 2 to 4 per cluster | no | no | final_label_repaired: '3 clusters per 6 weeks' -> '3 per 6 week' |
| 7401 | 2 clusters per 6 week | 2 per 6 week | 2 cluster per 6 week, 1 to 2 per cluster | no | yes | final_label_repaired: '2 clusters per 6 weeks' -> '2 per 6 week' |
| 7491 | 1 cluster per week | 1 per week | unknown | no | no | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 9344 | several per day | multiple per day | multiple per day | no | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 9943 | 1 cluster every 4 to 5 week | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | no | final_label_repaired: '1 cluster every 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 9955 | 1 cluster per month | 1 per month | 1 cluster per month, multiple per cluster | no | no | final_label_repaired: '1 cluster per month' -> '1 per month' |
| 10003 | 1 cluster per week | 1 per week | 1 cluster per week, multiple per cluster | no | yes | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10047 | 2 clusters per 3 month | 2 per 3 month | 2 cluster per 3 month, multiple per cluster | no | no | final_label_repaired: '2 clusters per quarter' -> '2 per 3 month' |
| 10063 | 3 clusters per 3 month | 3 per 3 month | 3 cluster per 3 month, multiple per cluster | no | no | final_label_repaired: '3 clusters per quarter' -> '3 per 3 month' |
| 10200 | 1 cluster per week | 1 per week | unknown, 2 to 4 per cluster | no | no | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10237 | 4 clusters per month | 4 per month | 4 cluster per month, multiple per cluster | no | no | final_label_repaired: '4 clusters per month' -> '4 per month' |
| 10245 | 1 to 3 clusters per month | 1 to 3 per month | 3 cluster per month, multiple per cluster | no | no | final_label_repaired: '1 to 3 clusters per month' -> '1 to 3 per month' |
| 10383 | 1 cluster per week | 1 per week | 1 cluster per week, 5 per cluster | no | yes | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10386 | 1 cluster per week | 1 per week | 1 cluster per week, 2 to 3 per cluster | no | yes | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10481 | 4 clusters per month | 4 per month | 4 cluster per month, multiple per cluster | no | no | final_label_repaired: '4 clusters per month' -> '4 per month' |
| 10487 | 4 clusters per month | 4 per month | 4 cluster per month, multiple per cluster | no | no | final_label_repaired: '4 clusters per month' -> '4 per month' |
| 10618 | 1 cluster per week | 1 per week | unknown, 4 to 6 per cluster | no | no | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10807 | 2 cluster day per month | 2 cluster per month | 2 cluster per month, multiple per cluster | no | no | final_label_repaired: '2 cluster days per month' -> '2 cluster per month'; unscorable_final_label: Unparsable cluster label: '2 cluster per month' |
| 10829 | 2 cluster day per month | 2 cluster per month | 2 cluster per month, multiple per cluster | no | no | final_label_repaired: '2 cluster days per month' -> '2 cluster per month'; unscorable_final_label: Unparsable cluster label: '2 cluster per month' |
| 10862 | 1 cluster per week | 1 per week | 1 cluster per week, multiple per cluster | no | yes | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10865 | 1 cluster per week | 1 per week | 1 cluster per week, multiple per cluster | no | yes | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10873 | 1 cluster per week | 1 per week | 1 cluster per week, 6 per cluster | no | yes | final_label_repaired: '1 cluster per week' -> '1 per week' |
| 10902 | 1 cluster per week | 1 per week | 1 cluster per week, 4 per cluster | no | yes | final_label_repaired: '1 cluster per week' -> '1 per week' |

## Interpretation

The 650-row replay keeps the same attribution boundary as the 25/50-row freeze ladder. Raw model selection reaches 394/650 Purist = 0.6062. Strict format-only repair reaches 412/650 Purist = 0.6338, with 18 raw-wrong to strict-correct improvements and 0 raw-correct to strict-wrong regressions. The frozen clean scorer-facing policy reaches 438/650 Purist = 0.6738, with 26 additional improvements and 0 regressions relative to strict format-only.

This remains a clean attribution replay, not the repair-heavy hybrid stack. Further gains should come from model-side selection or named ablated deterministic modules rather than expanding the clean scorer-facing policy without a new policy review.
