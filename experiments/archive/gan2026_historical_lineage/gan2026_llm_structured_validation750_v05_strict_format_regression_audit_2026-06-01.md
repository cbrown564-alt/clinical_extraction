# Gan 2026 V0.5 Strict-Format Regression Audit

This is a validation development no-call replay over saved raw model outputs. It is not a final holdout or benchmark result.

- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Raw-output source: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- JSON details: `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.json`
- CSV changed rows: `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.csv`

## Finding

The 26 strict-format regressions in the earlier basic-split replay were caused by the format-noise cleanup deleting `seizure` from the sentinel label `no seizure frequency reference`, producing the unscorable label `no frequency reference` on `row_ok=False` no-reference rows. The strict-format path now preserves `unknown` and `no seizure frequency reference` before event-word cleanup.

## Current Replay Summary

| Condition | Purist correct | Purist accuracy | Changed vs raw | Improved vs raw | Regressed vs raw |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw model final label | 394 / 650 | 0.6062 | 0 | 0 | 0 |
| Strict format-preserving repair | 413 / 650 | 0.6354 | 253 | 19 | 0 |

## Interpretation

- The original 26 regressions are resolved in this no-call replay: strict format-preserving repair has 0 Purist regressions versus raw on the 650 saved-output rows.
- Strict repair now improves 19 rows versus raw while preserving the no-reference sentinel; its score rises from 0.6062 to 0.6354 Purist accuracy on this saved-output surface.
- This supports treating the corrected strict-format subset as benchmark normalization for attribution, while the full basic repair family should remain a named deterministic semantic repair module.

## Regression Rows After Fix

No Purist regressions remain versus raw model selection.

## Top Improvements After Fix

| Row | Raw | Strict | Gold | Notes |
| ---: | --- | --- | --- | --- |
| 891 | 1 every other day | 1 per 2 day | 1 per 2 day | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 978 | 1 every 2 months | 1 per 2 month | 1 per 2 month | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 2698 | 1 every 2 days | 1 per 2 day | 1 per 2 day | final_label_repaired: '1 every 2 days' -> '1 per 2 day' |
| 3468 | cluster perimenstrual | unknown | unknown | final_label_repaired: 'cluster perimenstrual' -> 'unknown' |
| 7141 | cluster per cycle | unknown | unknown | final_label_repaired: 'cluster per cycle' -> 'unknown' |
| 7491 | 1 cluster per week | unknown | unknown | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10200 | 1 cluster per week | unknown | unknown, 2 to 4 per cluster | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10509 | clusters per week | unknown | unknown | final_label_repaired: 'clusters per week' -> 'unknown' |
| 10618 | 1 cluster per week | unknown | unknown, 4 to 6 per cluster | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10894 | weekly clusters | 1 per week | 1 cluster per week, 4 per cluster | final_label_repaired: 'weekly clusters' -> '1 per week' |
| 10896 | weekly clusters | 1 per week | 1 cluster per week, 3 to 4 per cluster | final_label_repaired: 'weekly clusters' -> '1 per week' |
| 11118 | 2 cluster days per month, 6 seizures per cluster day | 2 cluster day per month, 6 per cluster day | 2 cluster per month, 6 per cluster | final_label_repaired: '2 cluster days per month, 6 seizures per cluster day' -> '2 cluster day per month, 6 per cluster day' |
| 11131 | 2 cluster days per month, 3 to 4 seizures per cluster | 2 cluster day per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | final_label_repaired: '2 cluster days per month, 3 to 4 seizures per cluster' -> '2 cluster day per month, 3 to 4 per cluster' |
| 11197 | 1 cluster per month, 4 to 6 events per cluster | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | final_label_repaired: '1 cluster per month, 4 to 6 events per cluster' -> '1 cluster per month, 4 to 6 per cluster' |
| 12548 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12551 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12556 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12641 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
| 12667 | daily | 1 per day | 1 per day | final_label_repaired: 'daily' -> '1 per day' |
