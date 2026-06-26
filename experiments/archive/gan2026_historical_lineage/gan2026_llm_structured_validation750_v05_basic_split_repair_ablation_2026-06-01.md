# Gan 2026 Structured LLM V0.5 Repair-Family Ablation

This is a validation development no-call replay over saved raw model outputs. It is not a final holdout or benchmark result.

- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Raw-output source: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- JSON summary: `experiments/gan2026_llm_structured_validation750_v05_basic_split_repair_ablation_2026-06-01.json`

## Condition Summary

| Condition | Purist | Pragmatic | Exact label | Semantic kind | Evidence | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A_raw_llm_final_label_only | 0.6062 | 0.6338 | 0.3138 | 0.6446 | 0.9523 | 0 | 0 |
| B_format_preserving_basic_label_repair | 0.5954 | 0.6231 | 0.3985 | 0.6354 | 0.9523 | 19 | 26 |
| C_full_basic_gan_label_repair | 0.7092 | 0.7369 | 0.4785 | 0.7046 | 0.9523 | 76 | 2 |
| D_selected_evidence_repair | 0.8400 | 0.8554 | 0.6108 | 0.8000 | 0.9523 | 88 | 3 |
| E_monthly_diary_arithmetic | 0.8415 | 0.8569 | 0.5923 | 0.8046 | 0.9523 | 5 | 4 |
| F_usual_interval_override | 0.8431 | 0.8585 | 0.5938 | 0.8062 | 0.9523 | 1 | 0 |
| G_breakthrough_after_seizure_free | 0.8508 | 0.8692 | 0.5954 | 0.8200 | 0.9523 | 6 | 1 |
| H_non_epileptic_override | 0.8538 | 0.8723 | 0.5954 | 0.8231 | 0.9523 | 2 | 0 |
| I_residual_jerk_date_anchor | 0.8631 | 0.8831 | 0.6031 | 0.8292 | 0.9523 | 6 | 0 |
| J_post_change_burst | 0.8754 | 0.8923 | 0.6077 | 0.8385 | 0.9523 | 8 | 0 |
| K_dated_sequence | 0.8908 | 0.9062 | 0.6262 | 0.8492 | 0.9523 | 10 | 0 |
| L_elapsed_anchor | 0.9046 | 0.9200 | 0.6354 | 0.8631 | 0.9523 | 12 | 3 |
| M_full_current_stack | 0.9046 | 0.9200 | 0.6354 | 0.8631 | 0.9523 | 0 | 0 |

## Basic Repair Split Interpretation

The clean LLM-first attribution baseline is raw model selection plus format-preserving basic label repair only. This condition keeps casing, plural units, compact rate syntax, event-word cleanup, and directly stated every/each-period phrasing, but excludes vague-quantity remapping, semantic fallback to unknown/no-reference, impossible-denominator fallback, and final catch-all coercion.

- Raw model selection: 394 / 650 Purist correct = 0.6062.
- Format-preserving basic repair: 387 / 650 Purist correct = 0.5954; 19 improved and 26 regressed versus raw.
- Full basic repair: 461 / 650 Purist correct = 0.7092; this remains an upper-bound diagnostic because it includes semantic fallback and vague-quantity remapping.

Use the format-preserving condition, not the full basic condition, for clean LLM-first attribution. Treat the full basic condition as a named deterministic repair module if it is retained.

## Top Changed Rows

### B_format_preserving_basic_label_repair

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 156 | 1 per 6 days | 1 per 6 day | 1 per 6 day | yes | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 182 | 1 per 2 days | 1 per 2 day | 1 per 2 day | yes | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 218 | 1 per 3 weeks | 1 per 3 week | 1 per 3 week | yes | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 months | 1 per 4 month | 1 per 4 month | yes | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 598 | 1 per 8 months | 1 per 8 month | 1 per 8 month | yes | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 days | 2 per 4 day | 2 per 4 day | yes | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 678 | 2 per 4 months | 2 per 4 month | 2 per 4 month | yes | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 891 | 1 every other day | 1 per 2 day | 1 per 2 day | no | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 | 1 per 2 weeks | 1 per 2 week | 1 per 2 week | yes | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 978 | 1 every 2 months | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 1165 | 5 to 7 per 3 weeks | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes | final_label_repaired: '5 to 7 per 3 weeks' -> '5 to 7 per 3 week' |
| 1887 | 4 per 3 months | 4 per 3 month | 4 per 3 month | yes | yes | final_label_repaired: '4 per 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 months | 7 per 3 month | 7 per 3 month | yes | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1979 | 6 per 2 months | 6 per 2 month | 6 per 2 month | yes | yes | final_label_repaired: '6 per 2 months' -> '6 per 2 month' |
| 1980 | 6 per 3 months | 6 per 3 month | 6 per 3 month | yes | yes | final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 2487 | 2 to 3 per 3 months | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2541 | 8 to 9 per 2 weeks | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | yes | final_label_repaired: '8 to 9 per 2 weeks' -> '8 to 9 per 2 week' |
| 2554 | 1 to 10 per 2 months | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2698 | 1 every 2 days | 1 per 2 day | 1 per 2 day | no | yes | final_label_repaired: '1 every 2 days' -> '1 per 2 day' |
| 2731 | 1 per 2 weeks | 1 per 2 week | 1 per 2 week | yes | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |

### C_full_basic_gan_label_repair

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 409 | 1 per month or less | 1 per month | 1 per month | no | yes | final_label_repaired: '1 per month or less' -> '1 per month' |
| 744 | most weekdays | no seizure frequency reference | multiple per week | no | yes | final_label_repaired: 'most weekdays' -> 'no seizure frequency reference' |
| 1687 | several per week | multiple per week | multiple per week | no | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 1695 | handful per month | no seizure frequency reference | multiple per month | no | yes | final_label_repaired: 'a handful per month' -> 'no seizure frequency reference' |
| 2080 | few per month | multiple per month | multiple per month | no | yes | final_label_repaired: 'a few per month' -> 'multiple per month' |
| 2094 | several per month | multiple per month | multiple per month | no | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2166 | frequent | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'frequent' -> 'no seizure frequency reference' |
| 3356 | after curtailed sleep | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'seizures after curtailed sleep' -> 'no seizure frequency reference' |
| 3371 | only with significant sleep deprivation | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'seizures only with significant sleep deprivation' -> 'no seizure frequency reference' |
| 3436 | cluster shortly after early-morning arousal | unknown | unknown | no | yes | final_label_repaired: 'cluster shortly after early-morning arousal' -> 'unknown' |
| 3469 | perimenstrual cluster | unknown | unknown | no | yes | final_label_repaired: 'perimenstrual cluster' -> 'unknown' |
| 3482 | perimenstrual only (day -3 to +3) | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'seizures perimenstrual only (days -3 to +3)' -> 'no seizure frequency reference' |
| 3493 | clustered period | unknown | unknown | no | yes | final_label_repaired: 'clustered around period' -> 'unknown' |
| 3507 | unknown frequency reduction | unknown | unknown | yes | yes | final_label_repaired: 'unknown frequency reduction' -> 'unknown' |
| 3512 | increased by ~20% after dose increase | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'increased by ~20% after dose increase' -> 'no seizure frequency reference' |
| 3528 | increased frequency | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'increased frequency' -> 'no seizure frequency reference' |
| 3999 | abs1 per month | 1 per month | 1 per month | no | yes | final_label_repaired: 'abs monthly' -> '1 per month' |
| 4690 | multiple per hour | no seizure frequency reference | multiple per day | yes | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4694 | multiple per hour | no seizure frequency reference | multiple per day | yes | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4700 | multiple per hour | no seizure frequency reference | multiple per day | yes | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |

### D_selected_evidence_repair

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | multiple per day | 4 per day | 4 per day | no | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 40 | multiple per week | 4 per week | 4 per week | no | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | multiple per year | 6 to 7 per year | 6 to 7 per year | no | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 180 | 1 per week | 1 per 7 day | 1 per 7 day | yes | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 187 | unknown | 1 per 7 to 9 day | 1 per 7 to 9 day | no | yes | final_label_repaired: '1 cluster per week' -> '1 per 7 to 9 day' |
| 190 | unknown | 1 per 4 week | 1 per 4 week | no | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per month | 1 per 4 week | 1 per 4 week | yes | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 212 | 1 per month | 1 per 3 to 4 week | 1 per 3 to 4 week | no | yes | final_label_repaired: '1 per month' -> '1 per 3 to 4 week' |
| 531 | no seizure frequency reference | 12 to 30 per 3 month | 12 to 30 per 3 month | no | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 665 | 2 per month | 2 per 2 week | 2 per 2 week | no | yes | final_label_repaired: '2 per month' -> '2 per 2 week' |
| 790 | 1 per week | 1 per 7 to 10 day | 1 per 7 to 10 day | no | yes | final_label_repaired: '1 per week' -> '1 per 7 to 10 day' |
| 869 | multiple per month | multiple per day | multiple per month | yes | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 959 | 2 per month | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 2 to 3 per month | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 987 | 2 per month | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1281 | multiple per month | 5 to 7 per 10 month | 5 to 7 per year | no | yes | final_label_repaired: 'less than 1 per month' -> '5 to 7 per 10 month' |
| 1486 | 3 per month | 2 per month | 3 per month | yes | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1591 | 11 per month | 5 per month | 11 per month | yes | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1597 | 2 to 3 per week | 12 per month | 12 per month | yes | yes | final_label_repaired: '2 to 3 per week' -> '12 per month' |
| 1687 | multiple per week | multiple per day | multiple per week | yes | yes | final_label_repaired: 'several per week' -> 'multiple per day' |

### E_monthly_diary_arithmetic

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 446 | 2 per week | 15 per 3 month | 2 per week | yes | yes | final_label_repaired: '2 per week' -> '15 per 3 month' |
| 4402 | 7 per 7 month | 14 per 14 month | 7 per 7 month | yes | yes | final_label_repaired: '1 to 2 per month' -> '7 per 7 month'; final_label_repaired: '7 per 7 month' -> '14 per 14 month' |
| 4410 | 4 per 7 month | 8 per 14 month | 4 per 7 month | yes | yes | final_label_repaired: '1 per month' -> '4 per 7 month'; final_label_repaired: '4 per 7 month' -> '8 per 14 month' |
| 5995 | 1 to 2 per month | 3 per 7 month | 1 per 3 months | no | yes | final_label_repaired: '1 to 2 per month' -> '3 per 7 month' |
| 6094 | 5 per 6 week | 4 per 2 month | 3 per month | yes | yes | final_label_repaired: '5 events in 6 weeks' -> '5 per 6 week'; final_label_repaired: '5 per 6 week' -> '4 per 2 month' |
| 6251 | no seizure frequency reference | 1 per 4 month | 1 per 1 to 2 month | no | yes | final_label_repaired: 'rare events' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 4 month' |
| 7475 | 2 per 2 month | 2 per 4 month | 2 per 6 month | no | yes | final_label_repaired: '2 per 6 months' -> '2 per 2 month'; final_label_repaired: '2 per 2 month' -> '2 per 4 month' |
| 9449 | 4 per 6 month | 8 per 9 month | 4 per 6 month | yes | yes | final_label_repaired: '2 per month' -> '4 per 6 month'; final_label_repaired: '4 per 6 month' -> '8 per 9 month' |
| 9496 | no seizure frequency reference | 6 per 12 month | 6 per 12 month | no | yes | final_label_repaired: 'low-frequency' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '6 per 12 month' |
| 13627 | 64 per 12 month | 20 per 3 month | 64 per 12 month | yes | yes | final_label_repaired: 'multiple per month' -> '64 per 12 month'; final_label_repaired: '64 per 12 month' -> '20 per 3 month' |
| 13635 | 47 per 7 month | 30 per 5 month | 47 per 7 month | yes | yes | final_label_repaired: 'multiple per month' -> '47 per 7 month'; final_label_repaired: '47 per 7 month' -> '30 per 5 month' |
| 13711 | 76 per 12 month | 28 per 6 month | 76 per 12 month | yes | yes | final_label_repaired: 'multiple per month' -> '76 per 12 month'; final_label_repaired: '76 per 12 month' -> '28 per 6 month' |
| 13721 | 77 per 12 month | 26 per 6 month | 77 per 12 month | yes | yes | final_label_repaired: 'multiple per month' -> '77 per 12 month'; final_label_repaired: '77 per 12 month' -> '26 per 6 month' |
| 13732 | 52 per 8 month | 16 per 3 month | 52 per 8 month | yes | yes | final_label_repaired: 'multiple per week' -> '52 per 8 month'; final_label_repaired: '52 per 8 month' -> '16 per 3 month' |
| 14581 | seizure free for multiple year | 1 per 4 month | 2 per 3 month | no | yes | final_label_repaired: 'seizure free since late October 2014' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month' |
| 2459 | 7 to 9 per 2 week | 5 per 5 month | 7 to 9 per 2 week | yes | no | final_label_repaired: 'multiple per week' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2932 | seizure free for 9 month | 26 per 2 month | seizure free for 9 month | yes | no | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month'; final_label_repaired: 'seizure free for 9 month' -> '26 per 2 month' |
| 6065 | 5 per month | 12 per 3 month | 5 per month | yes | no | final_label_repaired: '5 per month' -> '12 per 3 month' |
| 12979 | 3 per 4 month | 3 per 2 month | 3 per 4 month | yes | no | final_label_repaired: '3 per year' -> '3 per 4 month'; final_label_repaired: '3 per 4 month' -> '3 per 2 month' |
| 14562 | unknown | 0 per 7 month | 3 per 6 month | no | no | final_label_repaired: 'unknown' -> '0 per 7 month' |

### F_usual_interval_override

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 4624 | unknown | 1 per 3 to 4 day | 1 per 3 to 4 day | no | yes | final_label_repaired: '1 cluster every 3 to 4 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 3 to 4 day' |

### G_breakthrough_after_seizure_free

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 13149 | no seizure frequency reference | 3 per 1 year | 3 per year | no | yes | final_label_repaired: '3 seizures 2 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 1 year' |
| 13178 | no seizure frequency reference | 1 per 6 month | 1 per 6 month | no | yes | final_label_repaired: '1 event 2 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 6 month' |
| 13190 | no seizure frequency reference | 1 per 5 month | 1 per 5 month | no | yes | final_label_repaired: '1 event 3 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 5 month' |
| 15404 | unknown | 3 to 4 per 4 month | 1 cluster per 4 month, 3 to 4 per cluster | no | yes | final_label_repaired: '1 cluster per day' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 4 month' |
| 15429 | unknown | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | no | yes | final_label_repaired: '1 cluster per day' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15431 | unknown | 5 per 4 month | 1 cluster per 4 month, 5 per cluster | no | yes | final_label_repaired: '1 cluster per day' -> 'unknown'; final_label_repaired: 'unknown' -> '5 per 4 month' |
| 6987 | unknown | 10 to 15 per 1 year | unknown | yes | no | final_label_repaired: 'unknown' -> '10 to 15 per 1 year' |
| 10245 | unknown | 1 to 3 per 6 month | 3 cluster per month, multiple per cluster | no | no | final_label_repaired: '1 to 3 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '1 to 3 per 6 month' |
| 10829 | unknown | 2 per 2 year | 2 cluster per month, multiple per cluster | no | no | final_label_repaired: '2 cluster days per month' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 2 year' |
| 13051 | unknown | 1 per 8 month | 2 per 8 month | no | no | final_label_repaired: '1 generalised tonic-clonic seizure 3 weeks ago with preceding cluster of absences' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 8 month' |
| 13058 | unknown | 1 per 7 month | 2 per 7 month | no | no | final_label_repaired: '1 cluster plus 1 tonic-clonic seizure in 3 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 7 month' |

### H_non_epileptic_override

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 5406 | unknown | seizure free for multiple year | seizure free for multiple month | no | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13858 | unknown | seizure free for multiple year | seizure free for multiple month | no | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |

### I_residual_jerk_date_anchor

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 15141 | 3 to 4 per day | 3 to 4 per 15 month | 4 to 5 per 15 month | no | yes | final_label_repaired: '3 to 4 per morning' -> '3 to 4 per day'; final_label_repaired: '3 to 4 per day' -> '3 to 4 per 15 month' |
| 15242 | unknown | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | no | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15262 | unknown | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | no | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 13 month, multiple per cluster' |
| 15267 | no seizure frequency reference | 3 per 14 month | 3 per 14 month | no | yes | final_label_repaired: '3 jerks per year' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 14 month' |
| 15306 | no seizure frequency reference | 2 to 3 per 15 month | 2 to 3 per 15 month | no | yes | final_label_repaired: '2 to 3 per current period' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 to 3 per 15 month' |
| 15317 | 2 to 3 per month | 2 to 3 per 15 month | 2 to 3 per 15 month | no | yes | final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |
| 15108 | 2 to 3 per month | 2 to 3 per 15 month | 3 to 4 per 15 month | no | no | final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |

### J_post_change_burst

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 14187 | seizure free for 1 month | 2 to 3 per 1 month | 2 to 3 per month | no | yes | final_label_repaired: 'seizure free for 1 month' -> '2 to 3 per 1 month' |
| 14214 | seizure free for 1 month | 2 to 4 per 1 month | 2 to 4 per month | no | yes | final_label_repaired: 'seizure free for 1 month' -> '2 to 4 per 1 month' |
| 14250 | 2 per week | 2 per 1 month | 2 per month | no | yes | final_label_repaired: '2 per week' -> '2 per 1 month' |
| 14284 | 2 to 3 per week | 2 to 3 per 1 month | 2 to 3 per month | no | yes | final_label_repaired: '2 to 3 per week' -> '2 to 3 per 1 month' |
| 14317 | seizure free for 2 month | 4 per 2 month | 4 per 2 month | no | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '4 per 2 month' |
| 14335 | seizure free for multiple year | 3 to 4 per 8 week | 3 to 4 per 2 month | no | yes | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 8 week' |
| 14383 | seizure free for multiple year | 3 to 4 per 3 month | 3 to 4 per 3 month | no | yes | final_label_repaired: 'seizure free since mid-January' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 3 month' |
| 14454 | seizure free for 2 month | 2 per 2 month | 2 per 2 month | no | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '2 per 2 month' |
| 14282 | seizure free for multiple year | 10 per 6 week | multiple per month | no | no | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '10 per 6 week' |

### K_dated_sequence

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 14524 | unknown | 2 per 6 month | 2 per 6 month | no | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 6 month' |
| 14530 | unknown | 2 per 2 month | 2 per 2 month | no | yes | final_label_repaired: 'unknown' -> '2 per 2 month' |
| 14540 | seizure free for multiple year | 2 per 8 month | 2 per 8 month | no | yes | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 8 month' |
| 14562 | 0 per 7 month | 3 per 6 month | 3 per 6 month | no | yes | final_label_repaired: 'unknown' -> '0 per 7 month'; final_label_repaired: '0 per 7 month' -> '3 per 6 month' |
| 14567 | 2 to 3 per month | 3 per 3 month | 3 per 3 month | no | yes | final_label_repaired: '2 to 3 per month' -> '3 per 3 month' |
| 14581 | 1 per 4 month | 2 per 3 month | 2 per 3 month | yes | yes | final_label_repaired: 'seizure free since late October 2014' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month'; final_label_repaired: '1 per 4 month' -> '2 per 3 month' |
| 14592 | 3 per 6 month | 3 per 5 month | 3 per 5 month | yes | yes | final_label_repaired: '3 seizures in 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '3 per 5 month' |
| 14611 | seizure free for 1 year | 2 per 4 month | 2 per 4 month | no | yes | final_label_repaired: 'seizure free for 1 year' -> '2 per 4 month' |
| 14628 | 2 per 3 month | 2 per 2 month | 2 per 2 month | no | yes | final_label_repaired: '2 events in 3 months' -> '2 per 3 month'; final_label_repaired: '2 per 3 month' -> '2 per 2 month' |
| 14645 | seizure free for 6 month | 2 per 6 month | 2 per 6 month | no | yes | final_label_repaired: 'seizure free for 6 month' -> '2 per 6 month' |
| 14662 | 2 to 3 per month | 3 per 4 month | 3 per 4 month | no | yes | final_label_repaired: '2 to 3 per month' -> '3 per 4 month' |
| 14672 | seizure free for multiple year | 3 per 8 month | 3 per 8 month | no | yes | final_label_repaired: 'seizure free since starting current regimen' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 8 month' |

### L_elapsed_anchor

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 14765 | seizure free for 1 month | 1 per 1 month | 1 per month | no | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14806 | seizure free for 1 month | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14810 | seizure free for multiple year | 1 per 1 month | 1 per month | no | yes | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14821 | seizure free for multiple year | 1 per 1 month | 1 per month | no | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14872 | seizure free for multiple year | 1 per 1 month | 1 per month | no | yes | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14943 | seizure free for 3 month | 1 per 3 month | 1 per 3 month | no | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 14965 | seizure free for 3 month | 1 per 3 month | 1 per 3 month | no | yes | final_label_repaired: 'seizure free for nearly 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 14973 | seizure free for 1 month | 1 per 1 month | 1 per month | no | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 15004 | seizure free for multiple year | 1 per 3 month | 1 per 3 month | no | yes | final_label_repaired: 'seizure free for past months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 15012 | seizure free for multiple year | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: 'seizure free for months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15029 | seizure free for multiple year | 1 per 3 month | 1 per 3 month | no | yes | final_label_repaired: 'seizure free for months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 15094 | 3 per year | 3 per 13 month | 4 per 13 month | yes | yes | final_label_repaired: '3 per year' -> '3 per 13 month' |
| 15127 | 4 per year | 4 per 13 month | 5 per 13 month | yes | yes | final_label_repaired: '4 per year' -> '4 per 13 month' |
| 15129 | no seizure frequency reference | 4 per 15 month | 4 per 15 month | no | yes | final_label_repaired: '4 since 3/2015' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 15 month' |
| 2992 | seizure free for 7 month | 1 per 8 month | seizure free for 7 month | yes | no | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month'; final_label_repaired: 'seizure free for 7 month' -> '1 per 8 month' |
| 3015 | seizure free for 1 year | 1 per 13 month | seizure free for 12 month | yes | no | final_label_repaired: 'seizure free for 1 year' -> '1 per 13 month' |
| 6571 | seizure free for 3 month | 1 per 4 month | unknown | no | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 4 month' |
| 8180 | seizure free for multiple year | 1 per 6 month | seizure free for multiple month | yes | no | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 6 month' |
| 11282 | seizure free for 3 month | 1 per 4 month | unknown | no | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 4 month' |

### M_full_current_stack

No final-label changes versus the previous condition.

## Minimum Row-Level Slices

### A_raw_llm_final_label_only

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9375 | 0.0982 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.5630 | 0.4370 | 0 | 0 |
| cluster_gold | 61 | 0.0984 | 0.0000 | 0 | 0 |
| monthly_diary | 650 | 0.6062 | 0.3138 | 0 | 0 |
| year_to_date_or_current_year | 67 | 0.4478 | 0.2836 | 0 | 0 |
| dated_sequence | 48 | 0.3125 | 0.0833 | 0 | 0 |
| row_ok_false | 32 | 0.8750 | 0.8125 | 0 | 0 |
| purist_correct_exact_label_wrong | 190 | 1.0000 | 0.0000 | 0 | 0 |

### B_format_preserving_basic_label_repair

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9375 | 0.4018 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.3782 | 0.2521 | 4 | 26 |
| cluster_gold | 61 | 0.2131 | 0.0164 | 7 | 0 |
| monthly_diary | 650 | 0.5954 | 0.3985 | 19 | 26 |
| year_to_date_or_current_year | 67 | 0.4925 | 0.3582 | 3 | 0 |
| dated_sequence | 48 | 0.3333 | 0.1875 | 1 | 0 |
| row_ok_false | 32 | 0.0625 | 0.0312 | 0 | 26 |
| purist_correct_exact_label_wrong | 128 | 1.0000 | 0.0000 | 6 | 0 |

### C_full_basic_gan_label_repair

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9375 | 0.4018 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8992 | 0.6050 | 62 | 0 |
| cluster_gold | 61 | 0.1967 | 0.0164 | 1 | 2 |
| monthly_diary | 650 | 0.7092 | 0.4785 | 76 | 2 |
| year_to_date_or_current_year | 67 | 0.5821 | 0.4478 | 7 | 1 |
| dated_sequence | 48 | 0.3958 | 0.1875 | 3 | 0 |
| row_ok_false | 32 | 0.9062 | 0.8438 | 27 | 0 |
| purist_correct_exact_label_wrong | 150 | 1.0000 | 0.0000 | 31 | 0 |

### D_selected_evidence_repair

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9554 | 0.3929 | 2 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8992 | 0.6050 | 1 | 1 |
| cluster_gold | 61 | 0.6885 | 0.5410 | 30 | 0 |
| monthly_diary | 650 | 0.8400 | 0.6108 | 88 | 3 |
| year_to_date_or_current_year | 67 | 0.8806 | 0.7313 | 20 | 0 |
| dated_sequence | 48 | 0.5625 | 0.3333 | 9 | 1 |
| row_ok_false | 32 | 0.9375 | 0.8125 | 1 | 0 |
| purist_correct_exact_label_wrong | 149 | 1.0000 | 0.0000 | 8 | 0 |

### E_monthly_diary_arithmetic

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9464 | 0.3839 | 0 | 1 |
| unknown_or_no_reference_gold | 119 | 0.8992 | 0.6050 | 0 | 0 |
| cluster_gold | 61 | 0.6885 | 0.5410 | 0 | 0 |
| monthly_diary | 650 | 0.8415 | 0.5923 | 5 | 4 |
| year_to_date_or_current_year | 67 | 0.8657 | 0.6716 | 0 | 1 |
| dated_sequence | 48 | 0.6042 | 0.2917 | 2 | 0 |
| row_ok_false | 32 | 0.9375 | 0.8125 | 0 | 0 |
| purist_correct_exact_label_wrong | 162 | 1.0000 | 0.0000 | 4 | 0 |

### F_usual_interval_override

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9464 | 0.3839 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8992 | 0.6050 | 0 | 0 |
| cluster_gold | 61 | 0.6885 | 0.5410 | 0 | 0 |
| monthly_diary | 650 | 0.8431 | 0.5938 | 1 | 0 |
| year_to_date_or_current_year | 67 | 0.8657 | 0.6716 | 0 | 0 |
| dated_sequence | 48 | 0.6042 | 0.2917 | 0 | 0 |
| row_ok_false | 32 | 0.9375 | 0.8125 | 0 | 0 |
| purist_correct_exact_label_wrong | 162 | 1.0000 | 0.0000 | 0 | 0 |

### G_breakthrough_after_seizure_free

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9464 | 0.3839 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8908 | 0.5966 | 0 | 1 |
| cluster_gold | 61 | 0.7377 | 0.5410 | 3 | 0 |
| monthly_diary | 650 | 0.8508 | 0.5954 | 6 | 1 |
| year_to_date_or_current_year | 67 | 0.8657 | 0.6716 | 0 | 0 |
| dated_sequence | 48 | 0.6042 | 0.2917 | 0 | 0 |
| row_ok_false | 32 | 0.9375 | 0.8125 | 0 | 0 |
| purist_correct_exact_label_wrong | 166 | 1.0000 | 0.0000 | 4 | 0 |

### H_non_epileptic_override

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9643 | 0.3839 | 2 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8908 | 0.5966 | 0 | 0 |
| cluster_gold | 61 | 0.7377 | 0.5410 | 0 | 0 |
| monthly_diary | 650 | 0.8538 | 0.5954 | 2 | 0 |
| year_to_date_or_current_year | 67 | 0.8657 | 0.6716 | 0 | 0 |
| dated_sequence | 48 | 0.6042 | 0.2917 | 0 | 0 |
| row_ok_false | 32 | 0.9375 | 0.8125 | 0 | 0 |
| purist_correct_exact_label_wrong | 168 | 1.0000 | 0.0000 | 2 | 0 |

### I_residual_jerk_date_anchor

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9643 | 0.3839 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8908 | 0.5966 | 0 | 0 |
| cluster_gold | 61 | 0.7705 | 0.5738 | 2 | 0 |
| monthly_diary | 650 | 0.8631 | 0.6031 | 6 | 0 |
| year_to_date_or_current_year | 67 | 0.8806 | 0.6866 | 1 | 0 |
| dated_sequence | 48 | 0.6042 | 0.2917 | 0 | 0 |
| row_ok_false | 32 | 0.9375 | 0.8125 | 0 | 0 |
| purist_correct_exact_label_wrong | 169 | 1.0000 | 0.0000 | 1 | 0 |

### J_post_change_burst

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9643 | 0.3839 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8908 | 0.5966 | 0 | 0 |
| cluster_gold | 61 | 0.7705 | 0.5738 | 0 | 0 |
| monthly_diary | 650 | 0.8754 | 0.6077 | 8 | 0 |
| year_to_date_or_current_year | 67 | 0.8806 | 0.6866 | 0 | 0 |
| dated_sequence | 48 | 0.6042 | 0.2917 | 0 | 0 |
| row_ok_false | 32 | 0.9375 | 0.8125 | 0 | 0 |
| purist_correct_exact_label_wrong | 174 | 1.0000 | 0.0000 | 5 | 0 |

### K_dated_sequence

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9643 | 0.3839 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8908 | 0.5966 | 0 | 0 |
| cluster_gold | 61 | 0.7705 | 0.5738 | 0 | 0 |
| monthly_diary | 650 | 0.8908 | 0.6262 | 10 | 0 |
| year_to_date_or_current_year | 67 | 0.8955 | 0.7015 | 1 | 0 |
| dated_sequence | 48 | 0.8125 | 0.5417 | 10 | 0 |
| row_ok_false | 32 | 1.0000 | 0.9062 | 2 | 0 |
| purist_correct_exact_label_wrong | 172 | 1.0000 | 0.0000 | 0 | 0 |

### L_elapsed_anchor

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9375 | 0.3750 | 0 | 3 |
| unknown_or_no_reference_gold | 119 | 0.8908 | 0.5966 | 0 | 0 |
| cluster_gold | 61 | 0.7705 | 0.5738 | 0 | 0 |
| monthly_diary | 650 | 0.9046 | 0.6354 | 12 | 3 |
| year_to_date_or_current_year | 67 | 0.8955 | 0.7015 | 0 | 0 |
| dated_sequence | 48 | 0.7917 | 0.5417 | 0 | 1 |
| row_ok_false | 32 | 1.0000 | 0.9062 | 0 | 0 |
| purist_correct_exact_label_wrong | 175 | 1.0000 | 0.0000 | 5 | 0 |

### M_full_current_stack

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 112 | 0.9375 | 0.3750 | 0 | 0 |
| unknown_or_no_reference_gold | 119 | 0.8908 | 0.5966 | 0 | 0 |
| cluster_gold | 61 | 0.7705 | 0.5738 | 0 | 0 |
| monthly_diary | 650 | 0.9046 | 0.6354 | 0 | 0 |
| year_to_date_or_current_year | 67 | 0.8955 | 0.7015 | 0 | 0 |
| dated_sequence | 48 | 0.7917 | 0.5417 | 0 | 0 |
| row_ok_false | 32 | 1.0000 | 0.9062 | 0 | 0 |
| purist_correct_exact_label_wrong | 175 | 1.0000 | 0.0000 | 0 | 0 |

