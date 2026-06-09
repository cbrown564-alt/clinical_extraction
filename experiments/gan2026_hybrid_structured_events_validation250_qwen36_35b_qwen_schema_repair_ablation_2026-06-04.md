# Gan 2026 Structured LLM V0.5 Repair-Family Ablation

This is a validation development no-call replay over saved raw model outputs. It is not a final holdout or benchmark result.

- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Raw-output source: `experiments\gan2026_hybrid_structured_events_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`
- JSON summary: `experiments\gan2026_hybrid_structured_events_validation250_qwen36_35b_qwen_schema_repair_ablation_2026-06-04.json`

## Condition Summary

| Condition | Structured | Blocking parse/schema | JSON dialect repairs | Label repair notes | Purist | Pragmatic | Exact label | Semantic kind | Evidence | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A_strict_json_raw_llm_final_label_only | 167 | 114 | 0 | 0 | 0.4400 | 0.4520 | 0.2320 | 0.4560 | 0.6040 | 0 | 0 |
| B_python_literal_dialect_repair_only | 250 | 53 | 83 | 0 | 0.6320 | 0.6480 | 0.3520 | 0.6440 | 0.8920 | 48 | 0 |
| C_format_preserving_basic_label_repair | 250 | 38 | 83 | 88 | 0.6920 | 0.7080 | 0.5240 | 0.7040 | 0.8920 | 15 | 0 |
| D_full_basic_gan_label_repair | 250 | 0 | 83 | 114 | 0.7360 | 0.7600 | 0.5240 | 0.7040 | 0.8920 | 19 | 8 |
| E_selected_evidence_repair | 250 | 0 | 83 | 153 | 0.9440 | 0.9520 | 0.7160 | 0.9000 | 0.8920 | 53 | 1 |
| F_monthly_diary_arithmetic | 250 | 0 | 83 | 153 | 0.9400 | 0.9480 | 0.7120 | 0.9000 | 0.8920 | 1 | 2 |
| G_usual_interval_override | 250 | 0 | 83 | 153 | 0.9400 | 0.9480 | 0.7120 | 0.9000 | 0.8920 | 0 | 0 |
| H_breakthrough_after_seizure_free | 250 | 0 | 83 | 153 | 0.9400 | 0.9480 | 0.7120 | 0.9000 | 0.8920 | 0 | 0 |
| I_non_epileptic_override | 250 | 0 | 83 | 153 | 0.9400 | 0.9480 | 0.7120 | 0.9000 | 0.8920 | 0 | 0 |
| J_residual_jerk_date_anchor | 250 | 0 | 83 | 153 | 0.9400 | 0.9480 | 0.7120 | 0.9000 | 0.8920 | 0 | 0 |
| K_post_change_burst | 250 | 0 | 83 | 153 | 0.9400 | 0.9480 | 0.7120 | 0.9000 | 0.8920 | 0 | 0 |
| L_dated_sequence | 250 | 0 | 83 | 153 | 0.9400 | 0.9480 | 0.7120 | 0.9000 | 0.8920 | 0 | 0 |
| M_elapsed_anchor | 250 | 0 | 83 | 155 | 0.9280 | 0.9360 | 0.7120 | 0.8880 | 0.8920 | 0 | 3 |
| N_full_current_stack | 250 | 0 | 83 | 155 | 0.9280 | 0.9360 | 0.7120 | 0.8880 | 0.8920 | 0 | 0 |

## Dialect And Basic Repair Split Interpretation

The first two conditions separate strict JSON compliance from non-semantic Python-literal dialect repair. The clean LLM-only structured-events attribution baseline is dialect repair plus format-preserving basic label repair only. This condition keeps casing, plural units, compact rate syntax, event-word cleanup, and directly stated every/each-period phrasing, but excludes vague-quantity remapping, semantic fallback to unknown/no-reference, impossible-denominator fallback, and final catch-all coercion.

- Strict JSON raw model selection: 110 / 250 Purist correct = 0.4400.
- Python-literal dialect repair only: 158 / 250 Purist correct = 0.6320; 48 improved and 0 regressed versus strict JSON.
- Format-preserving basic repair: 173 / 250 Purist correct = 0.6920; 15 improved and 0 regressed versus raw.
- Full basic repair: 184 / 250 Purist correct = 0.7360; this remains an upper-bound diagnostic because it includes semantic fallback and vague-quantity remapping.

Use the format-preserving condition, not the full basic condition, for clean LLM-only structured-events attribution. Treat the full basic condition as a named deterministic repair module if it is retained.

## Top Changed Rows

### B_python_literal_dialect_repair_only

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 180 | None | 1 per week | 1 per 7 day | no | yes | json_dialect_repaired: python_literal |
| 198 | None | 1 per month | 1 per 4 week | no | yes | json_dialect_repaired: python_literal |
| 278 | None | multiple per week | multiple per week | no | yes | json_dialect_repaired: python_literal |
| 467 | None | 9 per month | 9 per month | no | yes | json_dialect_repaired: python_literal |
| 659 | None | 2 per 4 days | 2 per 4 day | no | yes | json_dialect_repaired: python_literal |
| 665 | None | 2 per 2 weeks | 2 per 2 week | no | yes | json_dialect_repaired: python_literal |
| 743 | None | multiple per week | multiple per week | no | yes | json_dialect_repaired: python_literal |
| 744 | None | multiple per week | multiple per week | no | yes | json_dialect_repaired: python_literal |
| 763 | None | 1 per week | 1 per week | no | yes | json_dialect_repaired: python_literal |
| 899 | None | 1 per 2 weeks | 1 per 2 week | no | yes | json_dialect_repaired: python_literal |
| 1281 | None | 5 to 7 per year | 5 to 7 per year | no | yes | json_dialect_repaired: python_literal |
| 1317 | None | multiple per day | unknown, multiple per cluster | no | yes | json_dialect_repaired: python_literal |
| 1591 | None | 11 per month | 11 per month | no | yes | json_dialect_repaired: python_literal |
| 1636 | None | 5 per month | 5 per month | no | yes | json_dialect_repaired: python_literal |
| 2094 | None | unknown | multiple per month | no | yes | json_dialect_repaired: python_literal |
| 2114 | None | unknown | multiple per month | no | yes | json_dialect_repaired: python_literal |
| 2354 | None | 6 to 7 per week | 6 to 7 per week | no | yes | json_dialect_repaired: python_literal |
| 2369 | None | 3 to 4 per month | 3 to 4 per month | no | yes | json_dialect_repaired: python_literal |
| 2425 | None | 6 to 8 per month | 6 to 8 per month | no | yes | json_dialect_repaired: python_literal |
| 2427 | None | 3 to 5 per month | 3 to 5 per month | no | yes | json_dialect_repaired: python_literal |

### C_format_preserving_basic_label_repair

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | ≤ 4 per day | 4 per day | 4 per day | no | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 40 | ≤ 4 per week | 4 per week | 4 per week | no | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | no | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | ≤ 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | no | yes | final_label_repaired: '≤ 2 to 4 per year' -> '2 to 4 per year' |
| 156 | 1 per 6 days | 1 per 6 day | 1 per 6 day | yes | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 218 | 1 per 3 weeks | 1 per 3 week | 1 per 3 week | yes | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 months | 1 per 4 month | 1 per 4 month | yes | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 338 | many per month | multiple per month | multiple per month | no | yes | final_label_repaired: 'many per month' -> 'multiple per month' |
| 409 | ≤ 1 per month | 1 per month | 1 per month | no | yes | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 446 | ≤ 2 per week | 2 per week | 2 per week | no | yes | final_label_repaired: '≤ 2 per week' -> '2 per week' |
| 531 | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | no | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per eight months | 1 per 8 month | 1 per 8 month | no | yes | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 659 | 2 per 4 days | 2 per 4 day | 2 per 4 day | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 weeks | 2 per 2 week | 2 per 2 week | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 678 | 2 per 4 months | 2 per 4 month | 2 per 4 month | yes | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 891 | 1 every other day | 1 per 2 day | 1 per 2 day | no | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 | 1 per 2 weeks | 1 per 2 week | 1 per 2 week | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 978 | 1 per 2 months | 1 per 2 month | 1 per 2 month | yes | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 1694 | 3 per 2 weeks | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | yes | final_label_repaired: '3 per 2 weeks' -> '3 per 2 week' |
| 2233 | 6 to 7 per 2 months | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | yes | final_label_repaired: '6 to 7 per 2 months' -> '6 to 7 per 2 month' |

### D_full_basic_gan_label_repair

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 869 | several per month | multiple per month | multiple per month | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per month' -> 'multiple per month' |
| 1223 | 3 or 4 per week | 4 per week | 3 to 4 per week | no | yes | final_label_repaired: '3 or 4 per week' -> '4 per week' |
| 1687 | several per week | multiple per week | multiple per week | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 2149 | occasional | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'occasional' -> 'no seizure frequency reference' |
| 2166 | frequent | no seizure frequency reference | unknown | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'frequent' -> 'no seizure frequency reference' |
| 3468 | perimenstrual only | no seizure frequency reference | unknown | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'perimenstrual only' -> 'no seizure frequency reference' |
| 3469 | 1 cluster per week | unknown | unknown | no | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week' -> 'unknown' |
| 3482 | perimenstrual only | no seizure frequency reference | unknown | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'perimenstrual only' -> 'no seizure frequency reference' |
| 3493 | cluster frequency | unknown | unknown | no | yes | final_label_repaired: 'cluster frequency' -> 'unknown' |
| 3532 | increased frequency | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'increased frequency' -> 'no seizure frequency reference' |
| 3988 | several per week | multiple per week | multiple per week | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 4690 | multiple per hour | no seizure frequency reference | multiple per day | yes | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4694 | multiple per hour | no seizure frequency reference | multiple per day | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4700 | multiple per hour | no seizure frequency reference | multiple per day | yes | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4732 | occasional | no seizure frequency reference | unknown | no | yes | final_label_repaired: 'occasional' -> 'no seizure frequency reference' |
| 4771 | 2 in last 6 week | no seizure frequency reference | unknown | no | yes | final_label_repaired: '2 in the last six weeks' -> 'no seizure frequency reference' |
| 5491 | 2 in 6 week | no seizure frequency reference | unknown | no | yes | final_label_repaired: '2 episodes in 6 weeks' -> 'no seizure frequency reference' |
| 5507 | 3 since june | no seizure frequency reference | unknown | no | yes | final_label_repaired: '3 since June' -> 'no seizure frequency reference' |
| 5534 | very infrequent | no seizure frequency reference | 1 per multiple month | no | yes | final_label_repaired: 'very infrequent' -> 'no seizure frequency reference' |
| 5551 | several per day | multiple per day | multiple per day | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per day' -> 'multiple per day' |

### E_selected_evidence_repair

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | multiple per day | 4 per day | 4 per day | no | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 40 | multiple per week | 4 per week | 4 per week | no | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | multiple per year | 6 to 7 per year | 6 to 7 per year | no | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | multiple per year | 2 to 4 per year | 2 to 4 per year | no | yes | final_label_repaired: '≤ 2 to 4 per year' -> '2 to 4 per year' |
| 180 | 1 per week | 1 per 7 day | 1 per 7 day | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per day | 1 per 2 day | 1 per 2 day | no | yes | final_label_repaired: '1 per day' -> '1 per 2 day' |
| 187 | multiple per week | 1 per 7 to 9 day | 1 per 7 to 9 day | no | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 7 to 9 day' |
| 190 | unknown | 1 per 4 week | 1 per 4 week | no | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 per 4 week' |
| 198 | 1 per month | 1 per 4 week | 1 per 4 week | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '1 per 4 week' |
| 409 | multiple per month | 1 per month | 1 per month | no | yes | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 446 | multiple per week | 2 per week | 2 per week | no | yes | final_label_repaired: '≤ 2 per week' -> '2 per week' |
| 531 | no seizure frequency reference | 12 to 30 per 3 month | 12 to 30 per 3 month | no | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 790 | 1 per week | 1 per 7 to 10 day | 1 per 7 to 10 day | no | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per week' -> '1 per 7 to 10 day' |
| 816 | no seizure frequency reference | 1 per month | 1 per month | no | yes | final_label_repaired: '4 in 2017' -> '1 per month' |
| 869 | multiple per month | multiple per day | multiple per month | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per month' -> 'multiple per day' |
| 959 | 2 per month | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 2 per month | 1 per 2 month | 1 per 2 month | no | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per month' -> '1 per 2 month' |
| 987 | 2 per month | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1171 | multiple per week | 9 per 3 week | 7 to 9 per 3 week | no | yes | final_label_repaired: 'multiple per week' -> '9 per 3 week' |
| 1207 | multiple per week | 21 to 28 per 3 month | 21 to 28 per 3 month | no | yes | final_label_repaired: 'multiple per week' -> '21 to 28 per 3 month' |

### F_monthly_diary_arithmetic

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 446 | 2 per week | 15 per 3 month | 2 per week | yes | yes | final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 4402 | seizure free for multiple year | 14 per 14 month | 7 per 7 month | no | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '14 per 14 month' |
| 4410 | 1 per 2 to 3 month | 4 per 7 month | 4 per 7 month | yes | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 per 2 to 3 month'; final_label_repaired: '1 per 2 to 3 month' -> '4 per 7 month' |
| 2459 | 7 to 9 per 2 week | 5 per 5 month | 7 to 9 per 2 week | yes | no | json_dialect_repaired: python_literal; final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2932 | seizure free for multiple year | 13 per 2 month | seizure free for 9 month | yes | no | final_label_repaired: 'seizure free since 29/09/2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '13 per 2 month' |

### G_usual_interval_override

No final-label changes versus the previous condition.

### H_breakthrough_after_seizure_free

No final-label changes versus the previous condition.

### I_non_epileptic_override

No final-label changes versus the previous condition.

### J_residual_jerk_date_anchor

No final-label changes versus the previous condition.

### K_post_change_burst

No final-label changes versus the previous condition.

### L_dated_sequence

No final-label changes versus the previous condition.

### M_elapsed_anchor

| Row | Previous | New | Gold | Purist Before | Purist After | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 2992 | seizure free for multiple year | 1 per 8 month | seizure free for 7 month | yes | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 8 month' |
| 3015 | seizure free for 1 year | 1 per 13 month | seizure free for 12 month | yes | no | final_label_repaired: 'seizure free for 1 year' -> '1 per 13 month' |
| 4839 | seizure free for 4 month | 1 per 5 month | seizure free for multiple month | yes | no | final_label_repaired: 'seizure free for 4 month' -> '1 per 5 month' |

### N_full_current_stack

No final-label changes versus the previous condition.

## Minimum Row-Level Slices

### A_strict_json_raw_llm_final_label_only

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.8158 | 0.1316 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.2174 | 0.2174 | 0 | 0 |
| cluster_gold | 7 | 0.2857 | 0.0000 | 0 | 0 |
| monthly_diary | 250 | 0.4400 | 0.2320 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.3750 | 0.3333 | 0 | 0 |
| dated_sequence | 13 | 0.2308 | 0.0000 | 0 | 0 |
| row_ok_false | 1 | 0.0000 | 0.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 52 | 1.0000 | 0.0000 | 0 | 0 |

### B_python_literal_dialect_repair_only

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 1.0000 | 0.1579 | 7 | 0 |
| unknown_or_no_reference_gold | 23 | 0.4348 | 0.4348 | 5 | 0 |
| cluster_gold | 7 | 0.4286 | 0.0000 | 1 | 0 |
| monthly_diary | 250 | 0.6320 | 0.3520 | 48 | 0 |
| year_to_date_or_current_year | 24 | 0.5417 | 0.5000 | 4 | 0 |
| dated_sequence | 13 | 0.3077 | 0.0769 | 1 | 0 |
| row_ok_false | 1 | 0.0000 | 0.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 70 | 1.0000 | 0.0000 | 18 | 0 |

### C_format_preserving_basic_label_repair

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 1.0000 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.4348 | 0.4348 | 0 | 0 |
| cluster_gold | 7 | 0.4286 | 0.0000 | 0 | 0 |
| monthly_diary | 250 | 0.6920 | 0.5240 | 15 | 0 |
| year_to_date_or_current_year | 24 | 0.5833 | 0.5417 | 1 | 0 |
| dated_sequence | 13 | 0.3077 | 0.1538 | 0 | 0 |
| row_ok_false | 1 | 0.0000 | 0.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 42 | 1.0000 | 0.0000 | 0 | 0 |

### D_full_basic_gan_label_repair

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 1.0000 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.9130 | 0.5217 | 11 | 0 |
| cluster_gold | 7 | 0.4286 | 0.0000 | 0 | 0 |
| monthly_diary | 250 | 0.7360 | 0.5240 | 19 | 8 |
| year_to_date_or_current_year | 24 | 0.6667 | 0.5833 | 2 | 0 |
| dated_sequence | 13 | 0.3077 | 0.1538 | 0 | 0 |
| row_ok_false | 1 | 0.0000 | 0.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 53 | 1.0000 | 0.0000 | 11 | 0 |

### E_selected_evidence_repair

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 1.0000 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 1 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 4 | 0 |
| monthly_diary | 250 | 0.9440 | 0.7160 | 53 | 1 |
| year_to_date_or_current_year | 24 | 0.8750 | 0.7500 | 6 | 1 |
| dated_sequence | 13 | 0.7692 | 0.5385 | 6 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 1 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 4 | 0 |

### F_monthly_diary_arithmetic

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.9737 | 0.3158 | 0 | 1 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9400 | 0.7120 | 1 | 2 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 1 | 0 |
| dated_sequence | 13 | 0.8462 | 0.5385 | 1 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 1 | 0 |

### G_usual_interval_override

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.9737 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9400 | 0.7120 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.8462 | 0.5385 | 0 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 0 | 0 |

### H_breakthrough_after_seizure_free

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.9737 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9400 | 0.7120 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.8462 | 0.5385 | 0 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 0 | 0 |

### I_non_epileptic_override

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.9737 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9400 | 0.7120 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.8462 | 0.5385 | 0 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 0 | 0 |

### J_residual_jerk_date_anchor

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.9737 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9400 | 0.7120 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.8462 | 0.5385 | 0 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 0 | 0 |

### K_post_change_burst

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.9737 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9400 | 0.7120 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.8462 | 0.5385 | 0 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 0 | 0 |

### L_dated_sequence

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.9737 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9400 | 0.7120 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.8462 | 0.5385 | 0 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 57 | 1.0000 | 0.0000 | 0 | 0 |

### M_elapsed_anchor

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.8947 | 0.3158 | 0 | 3 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9280 | 0.7120 | 0 | 3 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.7692 | 0.5385 | 0 | 1 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 54 | 1.0000 | 0.0000 | 0 | 0 |

### N_full_current_stack

| Slice | Rows | Purist | Exact label | Improved | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| seizure_free_gold | 38 | 0.8947 | 0.3158 | 0 | 0 |
| unknown_or_no_reference_gold | 23 | 0.8696 | 0.5217 | 0 | 0 |
| cluster_gold | 7 | 1.0000 | 0.7143 | 0 | 0 |
| monthly_diary | 250 | 0.9280 | 0.7120 | 0 | 0 |
| year_to_date_or_current_year | 24 | 0.9167 | 0.7917 | 0 | 0 |
| dated_sequence | 13 | 0.7692 | 0.5385 | 0 | 0 |
| row_ok_false | 1 | 1.0000 | 1.0000 | 0 | 0 |
| purist_correct_exact_label_wrong | 54 | 1.0000 | 0.0000 | 0 | 0 |

