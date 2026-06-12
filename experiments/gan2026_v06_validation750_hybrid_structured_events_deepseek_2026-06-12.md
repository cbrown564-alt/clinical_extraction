# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-12

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Rare full-validation reason: User-approved Gan close-off confirmation: extend SE v0.6 from completed validation250 prefix to full validation750 for cross-model DeepSeek comparison; 250 rows are insufficient for the approved close-off report confirmation.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-chat`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-12T07:14:30.997884+00:00`
- Run finished UTC: `2026-06-12T08:00:58.809683+00:00`
- Wall-clock elapsed: `2787.812` seconds (`46.464` minutes)
- Throughput: `0.269028` rows/sec (`3.717` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `9edf9806`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.jsonl`

## Summary

- Structured records: 745 / 750
- Call failures: 0
- Parse/schema/label issues: 5
- JSON dialect repairs: 0
- Deterministic repair notes: 500
- Exact selection evidence substrings: 719 / 750
- Purist validation accuracy/micro F1 proxy: 0.8293 (622 / 750)
- Pragmatic validation accuracy/micro F1 proxy: 0.8613 (646 / 750)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per 7 days' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '1 cluster every 7 to 9 days' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes |  |
| 409 | 1 per month | 1 per month | yes | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 15 per 3 month | 2 per week | yes | final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 | no seizure frequency reference | multiple per week | yes | final_label_repaired: 'most shifts' -> 'no seizure frequency reference' |
| 744 | multiple per week | multiple per week | yes | final_label_repaired: 'most weekdays' -> 'multiple per week' |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per 7 to 10 days' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per day | multiple per month | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 seizure every 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | final_label_repaired: '5 to 7 per 3 weeks' -> '5 to 7 per 3 week' |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | final_label_repaired: '7 to 9 per 3 weeks' -> '7 to 9 per 3 week' |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | final_label_repaired: '5 to 7 per year' -> '5 to 7 per 10 month' |
| 1317 | unknown | unknown, multiple per cluster | yes | final_label_repaired: '1 cluster per day' -> 'unknown' |
| 1357 | 1 per day | 1 per day | yes | final_label_repaired: '1 seizure yesterday' -> '1 per day' |
| 1363 | 1 per day | 3 per day | yes | final_label_repaired: '3 per day (cluster)' -> '1 per day' |
| 1413 | 9 per month | 9 per month | yes | evidence_not_exact_substring |
| 1454 | 7 per week | 7 per week | yes |  |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 per 2 weeks' -> '3 per 2 week' |
| 1695 | no seizure frequency reference | multiple per month | yes | final_label_repaired: 'a handful per month' -> 'no seizure frequency reference' |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | final_label_repaired: 'multiple per month' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes | final_label_repaired: 'multiple per week (cluster)' -> 'multiple per week' |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '11 events in 6 months' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '11 events in 3 months' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '8 events in 4 months' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 events in 2 months' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1880 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '4 per month (overall: 1 drop attack + 7 convulsions in 2 months = 8 events in 2 months ≈ 4 per month)' -> '8 per 2 month' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 events in 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 events in 3 months' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 events in 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2149 | multiple per month | unknown | yes | final_label_repaired: 'occasional over last year' -> 'multiple per month' |
| 2166 | multiple per week | unknown | yes | evidence_not_exact_substring |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per 2 weeks' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | final_label_repaired: '6 to 7 per 2 months' -> '6 to 7 per 2 month' |
| 2245 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | final_label_repaired: '6 to 8 per 3 months' -> '6 to 8 per 3 month' |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | final_label_repaired: '6 to 7 per 2 weeks' -> '6 to 7 per 2 week' |
| 2459 | 5 per 5 month | 7 to 9 per 2 week | no | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: '8 to 9 per 2 weeks' -> '8 to 9 per 2 week' |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | final_label_repaired: '5 to 6 per 2 months' -> '5 to 6 per 2 month' |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | final_label_repaired: '3 to 4 per 2 months' -> '3 to 4 per 2 month' |
| 2609 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | 1 per day | 1 per day | yes |  |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2681 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 1 per month | 1 per month | yes |  |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes |  |
| 2812 | 1 per day | 1 per day | yes |  |
| 2822 | 1 per day | 1 per day | yes |  |
| 2824 | 1 per day | 1 per day | yes |  |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | 13 per 2 month | seizure free for 9 month | no | final_label_repaired: 'seizure free for 9 month' -> '13 per 2 month' |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 2965 | seizure free for 1 year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 1 year 4 months' -> 'seizure free for 1 year' |
| 2992 | 1 per 7 month | seizure free for 7 month | no | final_label_repaired: 'seizure free for 7 month' -> '1 per 7 month' |
| 3015 | 1 per 13 month | seizure free for 12 month | no | final_label_repaired: 'seizure free for 1 year' -> '1 per 13 month' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last visit' -> 'seizure free for multiple year' |
| 3137 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes | final_label_repaired: '8 per 30 days' -> '8 per month' |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | multiple per month | unknown | yes | final_label_repaired: 'less than 1 per month' -> 'multiple per month' |
| 3371 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes | final_label_repaired: 'cluster pattern, unspecified frequency' -> 'unknown' |
| 3468 | unknown | unknown | yes | final_label_repaired: '1 cluster per menstrual cycle' -> 'unknown' |
| 3469 | unknown | unknown | yes | final_label_repaired: '1 cluster per month (perimenstrual)' -> 'unknown' |
| 3482 | no seizure frequency reference | unknown | yes | final_label_repaired: 'perimenstrual only (days -3 to +3)' -> 'no seizure frequency reference' |
| 3493 | unknown | unknown | yes | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 3507 | unknown | unknown | yes |  |
| 3512 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased by ~20%' -> 'no seizure frequency reference' |
| 3528 | multiple per week | unknown | yes |  |
| 3532 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased by ~20% over 3 weeks' -> 'no seizure frequency reference' |
| 3534 | seizure free for 7 month | unknown | no | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'multiple per week' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 clusters per week' -> '7 per week' |
| 3681 | 9 per month | 9 per month | yes |  |
| 3682 | 6 per month | 6 per month | yes |  |
| 3710 | 5 per week | 5 per week | yes |  |
| 3753 | 1 per day | 1 per day | yes |  |
| 3766 | 8 per year | 8 per year | yes |  |
| 3774 | 9 per year | 9 per year | yes |  |
| 3791 | 10 per year | 10 per year | yes |  |
| 3801 | 9 per month | 9 per month | yes |  |
| 3806 | 6 per month | 6 per month | yes |  |
| 3827 | 7 per month | 7 per month | yes |  |
| 3846 | 2 per day | 2 per day | yes |  |
| 3849 | 3 per day | 3 per day | yes |  |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 | 3 per year | 3 per year | yes |  |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 | 4 per week | 4 per week | yes |  |
| 3988 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 3995 | 1 per month | 1 per month | yes |  |
| 3999 | 1 per month | 1 per month | yes |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day on workdays, with near-daily auras and 3 convulsions in 10 days' -> '1 per 1 to 2 day' |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 4258 | 4 per week | 4 per week | yes |  |
| 4337 | 26 per 4 month | 3 per 3 month | no | final_label_repaired: '3 events over 4 months' -> '3 per 4 month'; final_label_repaired: '3 per 4 month' -> '26 per 4 month' |
| 4345 | 4 per 1 month | 4 per month | yes | final_label_repaired: '4 per month' -> '4 per 1 month' |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 events over 2.5 months (approximately 2 per month)' -> '5 per 2 month' |
| 4402 | 14 per 14 month | 7 per 7 month | yes | final_label_repaired: 'less than 1 per month' -> '7 per 7 month'; final_label_repaired: '7 per 7 month' -> '14 per 14 month' |
| 4410 | 8 per 14 month | 4 per 7 month | yes | final_label_repaired: '1 per month' -> '4 per 7 month'; final_label_repaired: '4 per 7 month' -> '8 per 14 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '7 to 8 per quarter' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | final_label_repaired: '1 per 3 to 4 days' -> '1 per 3 to 4 day' |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | final_label_repaired: 'every 14 to 21 days' -> '1 per 14 to 21 day' |
| 4690 | multiple per day | multiple per day | yes | final_label_repaired: '10 per hour' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | final_label_repaired: '9 per hour' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | final_label_repaired: '4 per hour' -> 'multiple per day' |
| 4709 | multiple per day | multiple per day | yes | final_label_repaired: '6 per hour' -> 'multiple per day' |
| 4731 | multiple per year | unknown | yes | final_label_repaired: 'rare' -> 'multiple per year' |
| 4732 | multiple per month | unknown | yes | final_label_repaired: 'occasional' -> 'multiple per month' |
| 4771 | multiple per month | unknown | yes |  |
| 4839 | 1 per 5 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free for 4 month' -> '1 per 5 month' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for many months' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 8 years' -> 'seizure free for multiple year' |
| 5092 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5110 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5141 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since mid-August 2025' -> 'seizure free for multiple year' |
| 5197 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5210 | seizure free for 1 year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 1 year or more' -> 'seizure free for 1 year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early 2024' -> 'seizure free for multiple year' |
| 5248 | seizure free for 2.5 year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 2.5 years' -> 'seizure free for 2.5 year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 5379 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5406 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5476 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic (not quantified per day/week/month)' -> 'no seizure frequency reference' |
| 5490 | unknown | unknown | yes | evidence_not_exact_substring |
| 5491 | unknown | unknown | yes | final_label_repaired: 'multiple per week (estimated from sporadic jerks with clustering and two episodes of loss of awareness over six weeks)' -> 'unknown' |
| 5504 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5507 | 3 per 4 month | unknown | no | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5528 | 1 per month | 1 per month | yes |  |
| 5534 | 1 per 2 week | 1 per multiple month | no | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 5551 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per 8 days' -> '1 per 8 day' |
| 5682 | 2 to 3 per month | 2 to 4 per month | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5763 | 2 per 3 month | 2 per month | no | final_label_repaired: '2 per 3 months (generalised) and 4 per 3 months (focal impaired-awareness)' -> '2 per 3 month' |
| 5767 | 1 to 2 per week | 1 per 1 to 2 week | no |  |
| 5791 | 3 per 3 month | 1 per month | yes | final_label_repaired: '3 events in 3 months' -> '3 per 3 month' |
| 5827 | multiple per week | multiple per week | yes |  |
| 5837 | unknown | 2 cluster per 3 week, multiple per cluster | no | final_label_repaired: '2 clusters and 1 tonic-clonic seizure over 3 weeks' -> 'unknown' |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '4 per 6 weeks' -> '4 per 6 week' |
| 5873 | multiple per week | multiple per week | yes | final_label_repaired: 'multiple per week (focal) and 3 in 6 weeks (generalised)' -> 'multiple per week'; evidence_not_exact_substring |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 5974 | no seizure frequency reference | unknown | yes | final_label_repaired: 'within 24–48 hours of missed dose' -> 'no seizure frequency reference' |
| 5977 | multiple per 6 week | unknown | yes | final_label_repaired: 'several per 6 weeks' -> 'multiple per 6 week' |
| 5995 | 1 per 9 month | 1 per 3 months | no | final_label_repaired: 'less than 1 per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '1 per 9 month' |
| 5996 | unknown | unknown | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes | final_label_repaired: 'clusters triggered by illness, with less frequent but ongoing events between clusters' -> 'unknown' |
| 6034 | no seizure frequency reference | unknown | yes | final_label_repaired: 'clustered nocturnal warnings (not quantified)' -> 'no seizure frequency reference' |
| 6065 | 5 per month | 5 per month | yes |  |
| 6077 | seizure free for 8 month | unknown | no | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month'; evidence_not_exact_substring |
| 6087 | unknown | unknown | yes | evidence_not_exact_substring |
| 6094 | 4 per 2 month | 3 per month | yes | final_label_repaired: '2 clusters over 6 weeks (3 in September, 2 in early October)' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 6137 | 1 per 2 to 3 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 6153 | 9 per 4 week | 9 per month | yes | final_label_repaired: '9 per 4 weeks' -> '9 per 4 week' |
| 6180 | multiple per week | multiple per week | yes |  |
| 6192 | unknown | unknown | yes |  |
| 6204 | 1 per 3 to 4 week | 2 per month | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 6209 | multiple per day | multiple per day | yes | final_label_repaired: 'daily brief events and 2 to 3 per month' -> 'multiple per day' |
| 6244 | 2 per week | unknown | no |  |
| 6251 | multiple per year | 1 per 1 to 2 month | no | final_label_repaired: 'rare (single event since August 2025)' -> 'multiple per year' |
| 6273 | unknown | unknown | yes |  |
| 6319 | 1 per week | 1 per week | yes |  |
| 6321 | 2 per 3 month | unknown | no | final_label_repaired: '2 episodes in 3 months' -> '2 per 3 month' |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 6358 | 1 per 16 month | seizure free for 15 to 16 months | no | final_label_repaired: 'seizure free for 1 year 4 months' -> 'seizure free for 1 year'; final_label_repaired: 'seizure free for 1 year' -> '1 per 16 month' |
| 6368 | 1 to 2 per week | unknown | no |  |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes | final_label_repaired: '1 cluster every 2-3 weeks (clusters over 2-3 days, then several weeks without events)' -> 'unknown' |
| 6509 | multiple per week | 1 per week | no | final_label_repaired: 'multiple per week (flurries with daily myoclonic jerks and absences, plus 2 GTCs in 2 weeks)' -> 'multiple per week'; evidence_not_exact_substring |
| 6571 | 1 per 4 month | unknown | no | final_label_repaired: 'seizure free for 3.5 months' -> 'seizure free for 3.5 month'; final_label_repaired: 'seizure free for 3.5 month' -> '1 per 4 month' |
| 6607 | unknown | unknown | yes | final_label_repaired: 'clusters on high-stress maintenance nights' -> 'unknown' |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6701 | 4 per 3 week | 4 per 3 week | yes | final_label_repaired: '4 per 3 weeks' -> '4 per 3 week' |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes |  |
| 6987 | unknown | unknown | yes |  |
| 7093 | unknown | unknown | yes | final_label_repaired: 'clusters per menstrual cycle' -> 'unknown' |
| 7126 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent with mid-cycle surge' -> 'no seizure frequency reference' |
| 7141 | unknown | unknown | yes | final_label_repaired: 'multiple per month (clusters and convulsions)' -> 'unknown' |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no | final_label_repaired: '3 clusters over 6 weeks, each with 2-4 events' -> 'unknown' |
| 7168 | multiple per week | unknown | yes | final_label_repaired: 'intermittent (multiple per week)' -> 'multiple per week' |
| 7192 | multiple per week | multiple per week | yes |  |
| 7195 | 1 per month | unknown | no |  |
| 7196 | 6 per 6 week | 1 per week | yes | final_label_repaired: '6 events over 6 weeks' -> '6 per 6 week' |
| 7198 | unknown | unknown | yes |  |
| 7275 | 3 per 12 week | 1 per month | yes | final_label_repaired: '3 events over 12 weeks' -> '3 per 12 week' |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | final_label_repaired: '2 clusters in 6 weeks, each with 1-2 spells' -> 'unknown' |
| 7409 | multiple per week | unknown | yes | final_label_repaired: 'most weeks' -> 'multiple per week' |
| 7455 | multiple per day | unknown | yes | final_label_repaired: '1 cluster in late August' -> 'multiple per day' |
| 7475 | 2 per 4 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 2 month'; final_label_repaired: '2 per 2 month' -> '2 per 4 month' |
| 7491 | unknown | unknown | yes | final_label_repaired: 'variable, with clustering' -> 'unknown' |
| 7506 | unknown | unknown | yes |  |
| 7573 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | no seizure frequency reference | 3 to 7 per month | no | final_label_repaired: '3 to 6 per menstrual cycle' -> 'no seizure frequency reference' |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 7818 | seizure free for 2 year | seizure free for 2 years | yes |  |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7859 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sparse events, no turns for several weeks' -> 'no seizure frequency reference' |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last clinic contact' -> 'seizure free for multiple year' |
| 7961 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8079 | seizure free for 1 year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 1 year 6 months' -> 'seizure free for 1 year' |
| 8089 | 1 per 1 month | seizure free for 16 month | no | final_label_repaired: 'seizure free for 1 year 4 months' -> 'seizure free for 1 year'; final_label_repaired: 'seizure free for 1 year' -> '1 per 1 month' |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes |  |
| 8144 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for sustained period' -> 'seizure free for multiple year' |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8160 | no seizure frequency reference | seizure free for multiple month | no | final_label_repaired: 'once every few weeks' -> 'no seizure frequency reference' |
| 8180 | no seizure frequency reference | seizure free for multiple month | no |  |
| 8188 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last clinic assessment' -> 'seizure free for multiple year' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for current follow-up period' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes |  |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8354 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 12+ months' -> 'seizure free for multiple year' |
| 8400 | multiple per month | seizure free for multiple month | no | final_label_repaired: 'occasional' -> 'multiple per month' |
| 8419 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 8474 | seizure free for 6 to 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6-8 months' -> 'seizure free for 6 to 8 month' |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8577 | seizure free for 18 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 8581 | seizure free for 4 month | seizure free for multiple month | yes | evidence_not_exact_substring |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8808 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 8820 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 8835 | seizure free for multiple year | seizure free for 10 month | yes | final_label_repaired: 'seizure free since 12 June 2020' -> 'seizure free for multiple year' |
| 8854 | seizure free for 8 month | seizure free for multiple month | yes |  |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8922 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8924 | 1 per 5 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 5 month' -> '1 per 5 month' |
| 8938 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for sustained postoperative period' -> 'seizure free for multiple year' |
| 9002 | 7 per 10 month | 7 per year | yes | final_label_repaired: '7 per year' -> '7 per 10 month' |
| 9063 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 9103 | 1 per 4 month | unknown | no | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 9190 | seizure free for 7 to 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 7 to 8 months' -> 'seizure free for 7 to 8 month' |
| 9215 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for approximately 4 months' -> 'seizure free for 4 month' |
| 9238 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9250 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | multiple per day | multiple per day | yes |  |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 3 per 6 month | 4 per 6 month | yes | final_label_repaired: '2 per month (most recent month) with prior months 0-1 per month' -> '4 per 6 month'; final_label_repaired: '4 per 6 month' -> '3 per 6 month' |
| 9462 | 16 per 25 month | 7 per 11 month | yes | final_label_repaired: '0 to 1 per month' -> '7 per 11 month'; final_label_repaired: '7 per 11 month' -> '16 per 25 month' |
| 9496 | 12 per 24 month | 6 per 12 month | yes | final_label_repaired: 'less than 1 per month' -> '6 per 12 month'; final_label_repaired: '6 per 12 month' -> '12 per 24 month' |
| 9547 | unknown | unknown | yes |  |
| 9588 | seizure free for 8 month | seizure free for multiple month | yes |  |
| 9704 | multiple per week | unknown | yes |  |
| 9815 | unknown | multiple per day | yes | final_label_repaired: 'multiple clusters per day' -> 'unknown' |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per 3 months' -> 'unknown' |
| 9888 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9912 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9937 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'multiple per month (clusters every few weeks)' -> 'unknown' |
| 9943 | multiple per month | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: 'multiple per month (clustered every 4-5 weeks)' -> 'multiple per month' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 clusters per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | 3 per month | 3 cluster per month, multiple per cluster | no |  |
| 10147 | unknown | unknown | yes |  |
| 10183 | unknown | unknown | yes |  |
| 10189 | unknown | unknown, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per several weeks, each cluster 3-4 events' -> 'unknown' |
| 10200 | unknown | unknown, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster, clusters occur sporadically' -> 'unknown' |
| 10237 | no seizure frequency reference | 4 cluster per month, multiple per cluster | no | final_label_repaired: 'unresolved_multiple' -> 'no seizure frequency reference' |
| 10245 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10260 | unknown | unknown | yes |  |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes |  |
| 10371 | no seizure frequency reference | seizure free for multiple year | no |  |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | final_label_repaired: '1 cluster per week, 5 seizures per cluster' -> '1 cluster per week, 5 per cluster' |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | final_label_repaired: '1 cluster per week, 2 to 3 seizures per cluster' -> '1 cluster per week, 2 to 3 per cluster' |
| 10434 | multiple per week | multiple cluster per week, 2 to 3 per cluster | no |  |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 10517 | no seizure frequency reference | 3 to 4 cluster per week, multiple per cluster | no | final_label_repaired: '3 to 4 nights per week' -> 'no seizure frequency reference' |
| 10542 | unknown | unknown, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster, cluster frequency not tracked' -> 'unknown' |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10583 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes |  |
| 10618 | unknown | unknown, 4 to 6 per cluster | yes | final_label_repaired: '4 to 6 per cluster day, with several days between clusters' -> 'unknown' |
| 10629 | unknown | unknown | yes |  |
| 10630 | no seizure frequency reference | multiple cluster per 2 week, 5 per cluster | no | final_label_repaired: 'several evenings per fortnight' -> 'no seizure frequency reference' |
| 10673 | multiple per month | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'multiple per month (clustered)' -> 'multiple per month' |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | unknown | unknown | yes | final_label_repaired: '1 cluster per 2-3 days during travel flare-ups' -> 'unknown' |
| 10807 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10829 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: '1 cluster per week (6 or more events per cluster)' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week (usually 4 events per cluster)' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 3 clusters per month' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 10965 | unknown | 2 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '2 clusters per month, each with 4-5 events' -> 'unknown' |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '3 clusters per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | final_label_repaired: '1 to 2 clusters per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 4 clusters per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months with 1 convulsion per cluster' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: 'multiple per week (clusters twice per month with 5+ seizures per cluster, plus weekly isolated events)' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 cluster days per month, each with ~6 seizures' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | final_label_repaired: '1 cluster per month with 4 to 6 events per cluster' -> '1 cluster per month, 4 to 6 per cluster' |
| 11216 | seizure free for 4 month | unknown | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 11254 | seizure free for 3 month | unknown | no |  |
| 11259 | unknown | unknown | yes |  |
| 11262 | multiple per week | unknown | yes |  |
| 11272 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 11282 | 1 per 4 month | unknown | no | final_label_repaired: 'seizure free for 3 month' -> '1 per 4 month' |
| 11337 | 1 per 6 month | unknown | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 11350 | multiple per day | unknown | yes | final_label_repaired: 'several per week' -> 'multiple per day' |
| 11380 | unknown | unknown | yes | final_label_repaired: 'multiple per month with perimenstrual clustering' -> 'unknown' |
| 11389 | seizure free for 2 month | unknown | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 11400 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11409 | unknown | no seizure frequency reference | yes | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11606 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11658 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11737 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11763 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11824 | 1 per day | no seizure frequency reference | no | final_label_repaired: 'no seizure frequency reference' -> '1 per day' |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 12036 | multiple per day | multiple per day | yes |  |
| 12041 | multiple per day | multiple per day | yes |  |
| 12046 | multiple per day | multiple per day | yes |  |
| 12051 | multiple per day | multiple per day | yes |  |
| 12111 | multiple per week | multiple per week | yes |  |
| 12127 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12130 | multiple per week | multiple per week | yes |  |
| 12139 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12145 | multiple per week | multiple per week | yes |  |
| 12192 | 1 per day | 1 per day | yes |  |
| 12218 | 1 per day | 1 per day | yes |  |
| 12236 | unknown | 1 per day | no | final_label_repaired: 'multiple per day (daily absence seizures, morning clusters of myoclonic jerks, occasional GTCS)' -> 'unknown'; evidence_not_exact_substring |
| 12246 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12314 | 3 per week | 3 per week | yes |  |
| 12366 | multiple per day | 4 per day | no |  |
| 12378 | multiple per day | 4 per day | no |  |
| 12383 | multiple per day | 4 per day | no |  |
| 12403 | multiple per day | 2 to 3 per day | no |  |
| 12412 | multiple per day | 2 per day | no | final_label_repaired: 'multiple per day (focal impaired awareness seizures 2/day, drop attacks in batches, tonic-clonic 2/month)' -> 'multiple per day' |
| 12422 | 1 per day | 1 per day | yes |  |
| 12438 | 1 per day | 1 per day | yes |  |
| 12456 | 1 per day | 1 per day | yes |  |
| 12460 | 1 per day | 1 per day | yes |  |
| 12468 | 1 per day | 1 per day | yes |  |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12502 | 1 cluster per month, multiple per cluster | 4 per day | no | final_label_repaired: 'multiple per day (4 absences per day) plus monthly tonic-clonic and myoclonic clusters' -> '1 cluster per month, multiple per cluster'; evidence_not_exact_substring |
| 12506 | 4 per day | 4 per day | yes |  |
| 12537 | 3 per 6 month | 1 per day | no | final_label_repaired: 'multiple per week' -> '3 per 6 month' |
| 12548 | 13 per 6 month | 1 per day | no | final_label_repaired: 'multiple per day (daily drop attacks) and 3 per year (generalised tonic-clonic) and every 4-6 weeks (focal impaired-awareness)' -> '13 per 6 month' |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12556 | multiple per day | 1 per day | no | final_label_repaired: 'multiple per week' -> 'multiple per day'; evidence_not_exact_substring |
| 12562 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week (3-4 GTCS/week, daily drop attacks, focal seizures every 4-6 weeks)' -> '1 per day'; evidence_not_exact_substring |
| 12573 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12584 | 1 per 3 month | 1 per week | no | final_label_repaired: 'multiple per week (weekly absences) plus several per month (tonic-clonic every 3 months, atonic and focal every few months)' -> '1 per 3 month'; evidence_not_exact_substring |
| 12641 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day'; evidence_not_exact_substring |
| 12665 | 1 to 2 per month | 1 per day | no |  |
| 12667 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per month (1-2 GTCS/month, daily absences, focal clonic every 3-4 weeks, drop attacks)' -> '1 per day'; evidence_not_exact_substring |
| 12676 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12679 | 1 to 2 per month | 1 per day | no |  |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | 4 per day | 4 per day | yes |  |
| 12788 | 6 per 4 month | 6 per 4 month | yes | final_label_repaired: '6 per year' -> '6 per 4 month' |
| 12810 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 per 2 months (approximately 2-3 per month)' -> '5 per 2 month' |
| 12823 | 9 per month | 9 per month | yes | final_label_repaired: '9 per year' -> '9 per month' |
| 12827 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12835 | 4 per month | 4 per month | yes | final_label_repaired: '4 per year (projected)' -> '4 per month' |
| 12877 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12882 | 7 per 4 month | 7 per 4 month | yes | final_label_repaired: '7 per 4 months (approximately 1.75 per month)' -> '7 per 4 month' |
| 12901 | unknown | 8 per 5 month | no | final_label_repaired: '8 tonic seizures per 5 months (approximately 1.6 per month) plus clusters of focal episodes' -> 'unknown'; evidence_not_exact_substring |
| 12949 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '9 per 6 months' -> '9 per 6 month' |
| 12950 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months (approximately 2-3 per month)' -> '7 per 3 month' |
| 12963 | no seizure frequency reference | unknown | yes | final_label_repaired: 'a small handful per year' -> 'no seizure frequency reference' |
| 12979 | 4 per 3 month | 3 per 4 month | no | final_label_repaired: '3 per 4 months' -> '3 per 4 month'; final_label_repaired: '3 per 4 month' -> '4 per 3 month' |
| 13008 | 4 per month | 4 per month | yes | final_label_repaired: '4 per 3 weeks (approximately 1.3 per week)' -> '4 per month' |
| 13011 | 3 per 2 month | 3 per 4 month | no | final_label_repaired: '3 per 4 months (approximately 0.75 per month)' -> '3 per 4 month'; final_label_repaired: '3 per 4 month' -> '3 per 2 month' |
| 13051 | seizure free for multiple year | 2 per 8 month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 13058 | 2 per 7 month | 2 per 7 month | yes | final_label_repaired: '1 cluster per month (approximate)' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 7 month' |
| 13114 | 1 per 1 year | 1 per year | yes | final_label_repaired: 'myoclonic jerks on 2 of the last 2 days' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 1 year' |
| 13122 | 3 per 1 year | 3 per year | yes | final_label_repaired: '1 cluster (3 tonic seizures) in recent 2 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year' |
| 13149 | 3 per 1 year | 3 per year | yes | final_label_repaired: '3 tonic seizures on one day (single event)' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year' |
| 13178 | 1 per 2 week | 1 per 6 month | no | final_label_repaired: '1 event in 2 weeks' -> '1 per 2 week' |
| 13190 | 1 per 5 month | 1 per 5 month | yes | final_label_repaired: '1 seizure in recent weeks (single breakthrough)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 5 month' |
| 13209 | 1 per 4 to 5 week | 1 per 8 month | no | final_label_repaired: '1 cluster per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 13267 | unknown | 2 per 5 month | no | final_label_repaired: '1 drop attack and cluster of myoclonic jerks per month (catamenial pattern)' -> 'unknown' |
| 13290 | 2 per 6 month | 4 per 6 month | yes | final_label_repaired: '2 seizures on one day, two weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 per 6 month' |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13450 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 13471 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13478 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13627 | 20 per 3 month | 64 per 12 month | yes | final_label_repaired: 'variable, ranging from 1 to 12 seizure-days per month' -> '64 per 12 month'; final_label_repaired: '64 per 12 month' -> '20 per 3 month' |
| 13635 | 30 per 5 month | 47 per 7 month | yes | final_label_repaired: 'multiple per month' -> '47 per 7 month'; final_label_repaired: '47 per 7 month' -> '30 per 5 month' |
| 13711 | 36 per 8 month | 76 per 12 month | yes | final_label_repaired: '10 days per month' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '36 per 8 month' |
| 13721 | 26 per 6 month | 77 per 12 month | yes | final_label_repaired: '10 days per month with seizures' -> '20 per 2 month'; final_label_repaired: '20 per 2 month' -> '26 per 6 month' |
| 13732 | 16 per 3 month | 52 per 8 month | yes | final_label_repaired: 'variable monthly seizure days (1 to 11 days per month)' -> '52 per 8 month'; final_label_repaired: '52 per 8 month' -> '16 per 3 month' |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13893 | 2 per year | 2 per year | yes |  |
| 13922 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 seizures since medication increase' -> 'no seizure frequency reference' |
| 14002 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 14025 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 14029 | multiple per week | unknown | yes | final_label_repaired: 'several per week (variable)' -> 'multiple per week' |
| 14040 | unknown | unknown | yes |  |
| 14076 | multiple per week | unknown | yes |  |
| 14092 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 over approximately 4 months' -> 'no seizure frequency reference' |
| 14096 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 per interval (since last appointment)' -> 'no seizure frequency reference' |
| 14137 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 to 4 in 3 months' -> 'no seizure frequency reference' |
| 14146 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 since starting Clobazam' -> 'no seizure frequency reference' |
| 14187 | 1 per 1 month | 2 to 3 per month | no | final_label_repaired: 'seizure free for approximately 1 month' -> 'seizure free for 1 month'; final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14214 | 8 per 2 month | 2 to 4 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '8 per 2 month' |
| 14250 | 1 per 2 month | 2 per month | no | final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14282 | 2022 per 4 week | multiple per month | yes | final_label_repaired: 'seizure free for 3 to 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2022 per 4 week' |
| 14284 | 1 per 2 month | 2 to 3 per month | no | final_label_repaired: 'seizure free since late February 2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 14317 | seizure free for multiple year | 4 per 2 month | no | final_label_repaired: 'seizure free since early April' -> 'seizure free for multiple year' |
| 14332 | seizure free for 2 month | 5 per 2 month | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 14335 | 12 per 3 month | 3 to 4 per 2 month | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '12 per 3 month' |
| 14383 | seizure free for 3 month | 3 to 4 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 14454 | seizure free for 2 month | 2 per 2 month | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 14524 | 2 per 3 month | 2 per 6 month | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 3 month' |
| 14530 | no seizure frequency reference | 2 per 2 month | no | evidence_not_exact_substring |
| 14540 | 2 per 8 month | 2 per 8 month | yes | final_label_repaired: 'seizure free since August 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 8 month' |
| 14562 | 3 per 6 month | 3 per 6 month | yes | final_label_repaired: 'seizure free for 1 month' -> '3 per 6 month' |
| 14567 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month'; final_label_repaired: '2 to 3 per 2 month' -> '3 per 3 month' |
| 14581 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: 'seizure free for less than 1 month' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14587 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 14592 | 3 per 5 month | 3 per 5 month | yes | final_label_repaired: '2 events in June 2024' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 5 month' |
| 14611 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: 'seizure free since May 2020' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 4 month' |
| 14628 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'unknown' -> '2 per 2 month' |
| 14635 | 5 per 5 month | 5 per 4 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '5 per 5 month' |
| 14645 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'seizure free since November 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 6 month' |
| 14662 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: 'unknown' -> '3 per 4 month' |
| 14672 | seizure free for multiple year | 3 per 8 month | no | final_label_repaired: 'seizure free since starting current regimen' -> 'seizure free for multiple year' |
| 14706 | 2 per 5 month | 2 per 5 month | yes | final_label_repaired: '2 per 5 months' -> '2 per 5 month' |
| 14765 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14806 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14810 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14821 | 18 per 2 month | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '18 per 2 month' |
| 14872 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 14943 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free since 21 Feb 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14949 | 1 per month | 1 per month | yes |  |
| 14965 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free since 20 May 2015' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14973 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 15004 | seizure free for 3 month | 1 per 3 month | no | final_label_repaired: 'seizure free for nearly 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 15012 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for approximately 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '1 per 2 month' |
| 15021 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | seizure free for 3 month | 1 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 15094 | 3 per 13 month | 4 per 13 month | yes | final_label_repaired: '3 since Apr/2022' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 13 month' |
| 15108 | 2 to 3 per 15 month | 3 to 4 per 15 month | no | final_label_repaired: '2 to 3 per 15 months' -> '2 to 3 per 15 month' |
| 15127 | 4 per 13 month | 5 per 13 month | yes | final_label_repaired: '4 since February 2020' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 13 month' |
| 15129 | 4 per 15 month | 4 per 15 month | yes | final_label_repaired: '4 events since March 2015' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 15 month' |
| 15141 | 3 to 4 per 15 month | 4 to 5 per 15 month | yes | final_label_repaired: '3 to 4 per 15 months' -> '3 to 4 per 15 month' |
| 15168 | multiple per month | multiple per 15 month | yes | final_label_repaired: 'occasional to intermittent' -> 'multiple per month'; evidence_not_exact_substring |
| 15193 | unknown | multiple per 13 month | yes |  |
| 15242 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15262 | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 13 month, multiple per cluster' |
| 15267 | 3 per 14 month | 3 per 14 month | yes | final_label_repaired: '3 jerks (since last visit, during sleep restriction)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 14 month' |
| 15306 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | final_label_repaired: '2 to 3 per unspecified period' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 to 3 per 15 month' |
| 15317 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |
| 15376 | unknown | 1 cluster per 2 week, 4 to 6 per cluster | no | final_label_repaired: '4 to 6 per day during clusters' -> 'unknown' |
| 15404 | 1 cluster per day, 3 to 4 per cluster | 1 cluster per 4 month, 3 to 4 per cluster | no | final_label_repaired: '1 cluster per day (3-4 seizures per cluster)' -> '1 cluster per day, 3 to 4 per cluster' |
| 15429 | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15431 | 5 per 4 month | 1 cluster per 4 month, 5 per cluster | yes | final_label_repaired: '5 seizures per day (in clusters)' -> 'unknown'; final_label_repaired: 'unknown' -> '5 per 4 month' |
| 15442 | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | final_label_repaired: 'multiple per week (seizure-free 4 days then cluster day with 2 tonic seizures)' -> '1 cluster per 4 day, 2 per cluster' |
| 15470 | multiple per day | 1 cluster per 5 day, multiple per cluster | no | final_label_repaired: 'multiple per week (clustering pattern with seizure-free days)' -> 'multiple per day' |
| 15479 | multiple per day | 1 cluster per 4 to 5 day, 2 per cluster | no | final_label_repaired: '2 tonic seizures per day on cluster days, with 4-5 seizure-free days between clusters' -> 'multiple per day' |
| 15497 | unknown | 1 cluster per 4 to 5 day, 5 per cluster | no | final_label_repaired: '5 per 24 hours (clusters)' -> 'unknown' |
| 15503 | unknown | 1 cluster per 5 day, 3 to 4 per cluster | no | final_label_repaired: '3 to 4 per 24 hours (clusters)' -> 'unknown' |
| 15513 | unknown | 1 cluster per 4 to 5 day, 2 to 3 per cluster | no | final_label_repaired: '2 to 3 per 24 hours during clusters' -> 'unknown' |
| 15519 | unknown | 1 cluster per 4 day, 3 per cluster | no | final_label_repaired: 'multiple per week (clusters of 3 focal seizures within 24 hours, occurring approximately twice monthly)' -> 'unknown' |
| 15529 | unknown | 1 cluster per 3 day, 4 per cluster | no | final_label_repaired: '4 per 24 hours (clusters)' -> 'unknown' |
| 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster day, with cluster days every 5-6 days' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15614 | 3 per week | 3 per week | yes |  |
| 15628 | multiple per week | multiple per week | yes |  |
| 15639 | 2 per week | 2 per week | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 15672 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple clusters per week (almost daily)' -> '1 per day' |
| 15697 | 1 per day | 1 per day | yes | final_label_repaired: 'almost 1 per day' -> '1 per day' |
| 15715 | 1 per day | 1 per day | yes | final_label_repaired: 'almost 1 per day' -> '1 per day' |
| 15745 | 2 to 3 per week | 2 to 3 per week | yes | final_label_repaired: '2 to 3 days per week' -> '2 to 3 per week' |
| 15766 | 4 per week | 4 per week | yes | final_label_repaired: '4 days per week' -> '4 per week' |
| 15768 | 2 to 3 per week | 2 to 3 per week | yes | final_label_repaired: '2 to 3 days per week' -> '2 to 3 per week' |
| 15771 | 3 per week | 3 per week | yes | final_label_repaired: '3 days per week' -> '3 per week' |
| 15772 | 2 per week | 2 per week | yes | final_label_repaired: '2 days per week' -> '2 per week' |
| 15774 | 2 per week | 2 per week | yes | final_label_repaired: '2 days per week' -> '2 per week' |
| 15783 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15802 | 7 per week | 7 per week | yes |  |
| 15831 | 2 to 4 per day | 2 to 4 per day | yes |  |
| 15834 | 5 per week | 5 per week | yes |  |
| 15964 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '6 per month' -> '11 per 3 month' |
| 15965 | 13 per 2 month | 13 per 2 month | yes | final_label_repaired: '6 per month' -> '13 per 2 month' |
| 15966 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: 'no seizure frequency reference' -> '5 per 3 month' |
| 15982 | 9 per 2 month | 9 per 2 month | yes | final_label_repaired: '8 per month' -> '9 per 2 month' |
| 15986 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '1 per month (most recent month May)' -> '11 per 2 month'; final_label_repaired: '11 per 2 month' -> '11 per 3 month' |
| 15992 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '3 per month' -> '7 per 2 month' |
| 15997 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: '6 per month (January)' -> '6 per month'; final_label_repaired: '6 per month' -> '10 per 3 month' |
| 16021 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '5 per month (nocturnal)' -> '5 per month'; final_label_repaired: '5 per month' -> '9 per 3 month' |
| 16041 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '9 per 2 month'; final_label_repaired: '9 per 2 month' -> '9 per 3 month' |
| 16084 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: 'seizure free for 1 month' -> '8 per 4 month' |
| 16091 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '2 per month' -> '3 per 3 month' |
| 16097 | 16 per 3 month | 17 per 4 month | yes | final_label_repaired: 'multiple per month' -> '17 per 4 month'; final_label_repaired: '17 per 4 month' -> '16 per 3 month' |
| 16107 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '4 per month (average over April and May), 0 in June' -> '8 per 3 month' |
| 16108 | 12 per 4 month | 12 per 4 month | yes | final_label_repaired: '1 per month (current month to date), with recent average of 3-5 per month' -> '12 per 4 month' |
| 16132 | 15 per 3 month | 15 per 3 month | yes | final_label_repaired: '2 per month' -> '15 per 3 month' |
| 16133 | 18 per 4 month | 18 per 4 month | yes | final_label_repaired: '6 per month' -> '18 per 4 month' |
| 16161 | 11 per 3 month | 18 per 3 month | no | final_label_repaired: '7 per month' -> '11 per 3 month' |
| 16162 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '6 per month' -> '11 per 3 month' |
| 16181 | 15 per 4 month | 15 per 4 month | yes | final_label_repaired: '4 per month' -> '15 per 4 month' |
| 16195 | 16 per 4 month | 16 per 4 month | yes | final_label_repaired: '6 per month' -> '16 per 4 month' |
| 16203 | 8 per 2 month | 9 per 3 month | no | final_label_repaired: '1 per month (September), 5 per month (August), 3 per month (July)' -> '8 per 2 month' |
| 16204 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '1 per month' -> '5 per 3 month' |
| 16220 | 11 per 2 month | 11 per 4 month | no | final_label_repaired: 'seizure free for 1 month' -> '11 per 2 month' |
| 16324 | 17 per 3 month | 10 per 3 month | no | final_label_repaired: '3 per month' -> '17 per 3 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: 'multiple per month' -> '7 per 3 month' |
| 16356 | 3 per 2 month | 1 per 4 day | no | final_label_repaired: '1 cluster per 4 days' -> '1 per 4 day'; final_label_repaired: '1 per 4 day' -> '3 per 2 month' |
| 16394 | 3 per 2 month | 1 per 2 to 4 day | no | final_label_repaired: '1 cluster every 2 to 4 days' -> '1 per 2 to 4 day'; final_label_repaired: '1 per 2 to 4 day' -> '3 per 2 month' |
| 16408 | 1 per 3 day | 1 per 3 day | yes | final_label_repaired: '1 per 3 days' -> '1 per 3 day' |
| 16429 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 per 2 to 3 days' -> '1 per 2 to 3 day' |
| 16432 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'approximately every two days, occasionally daily' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 day' |
| 16450 | 1 per multiple day | 1 per multiple day | yes | final_label_repaired: 'multiple per week' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per multiple day' |
| 16529 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster every 5 days' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 cluster per 2-3 days' -> '1 per 2 to 3 day' |
| 16574 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster every 4 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 day' |
| 16590 | 1 per 4 to 5 day | 1 per 4 to 5 day | yes | final_label_repaired: '1 cluster per 4 to 5 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 to 5 day' |
| 16618 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster every 5 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 5 day' |
| 16645 | 5 per 7 month | 5 per 7 month | yes | final_label_repaired: '1 seizure in February 2024' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '5 per 7 month' |
| 16674 | 6 per 4 month | 7 per 6 month | yes | final_label_repaired: '4 events in 6 months (1 cluster + 3 isolated)' -> 'unknown'; final_label_repaired: 'unknown' -> '6 per 4 month' |
| 16685 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: 'multiple per month' -> '9 per 2 month'; final_label_repaired: '9 per 2 month' -> '10 per 3 month' |
| 16697 | 2 per 3 month | 3 per 6 month | yes | final_label_repaired: 'no seizure frequency reference' -> '2 per 3 month' |
| 16704 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '7 per month (myoclonic jerks in Sep)' -> '7 per month'; final_label_repaired: '7 per month' -> '9 per 6 month' |
| 16714 | 5 per 4 month | 5 per 6 month | no | final_label_repaired: 'unknown' -> '5 per 4 month' |
| 16717 | 5 per 6 month | 5 per 6 month | yes | final_label_repaired: 'multiple per 6 months' -> 'multiple per 6 month'; final_label_repaired: 'multiple per 6 month' -> '5 per 6 month' |
| 16719 | 7 per 4 month | 7 per 6 month | yes | final_label_repaired: '1 per week' -> '7 per 4 month' |
| 16728 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: 'variable, with 3 discrete events over 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '4 per 6 month' |
| 16750 | 6 per 7 month | 6 per 7 month | yes | final_label_repaired: 'seizure free for less than 1 month' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '6 per 7 month' |
| 16757 | 18 per 3 month | 13 per 6 month | no | final_label_repaired: 'multiple clusters per year' -> 'unknown'; final_label_repaired: 'unknown' -> '18 per 3 month' |
| 16758 | 9 per 5 month | 9 per 5 month | yes | final_label_repaired: 'multiple per month' -> '9 per 5 month' |
| 16772 | 15 per 2 month | 9 per 5 month | no | final_label_repaired: 'multiple per month (clusters in Nov, Dec; single in Mar)' -> 'unknown'; final_label_repaired: 'unknown' -> '15 per 2 month'; evidence_not_exact_substring |
| 16774 | 19 per 4 month | 19 per 7 month | no | final_label_repaired: '3 per month (May)' -> '3 per month'; final_label_repaired: '3 per month' -> '19 per 4 month' |
| 16780 | 3 per 7 month | 3 per 7 month | yes | final_label_repaired: 'multiple isolated events over 7 months (Jan, Apr, Jul)' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '3 per 7 month' |
| 16824 | 11 per 5 month | 11 per 5 month | yes | final_label_repaired: 'multiple per month' -> '8 per 2 month'; final_label_repaired: '8 per 2 month' -> '11 per 5 month'; evidence_not_exact_substring |
| 16833 | 8 per 6 month | 8 per 6 month | yes | final_label_repaired: 'unknown' -> '8 per 6 month' |
| 16839 | 12 per 3 month | 9 per 4 month | no | final_label_repaired: 'multiple per month (clusters and isolated seizures) plus ongoing subtle events' -> 'unknown'; final_label_repaired: 'unknown' -> '12 per 3 month'; evidence_not_exact_substring |
| 16867 | 5 per 4 month | 6 per 7 month | no | final_label_repaired: 'multiple per year (3 in December, 2 in March, 1 in June)' -> 'multiple per year'; final_label_repaired: 'multiple per year' -> '5 per 4 month' |
| 16907 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: 'multiple per month' -> '9 per 6 month'; evidence_not_exact_substring |
| 16938 | 1 per 2 month | 2 per week | no | final_label_repaired: '1 per month' -> '1 per 2 month' |
| 16947 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 16961 | 1 per 3 month | 2 per week | no | final_label_repaired: '1 per month' -> '1 per 3 month' |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes |  |
| 17001 | 5 per week | 5 per week | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 17110 | 4 to 5 per week | 4 to 5 cluster per week, multiple per cluster | no | final_label_repaired: '4 to 5 days per week' -> '4 to 5 per week' |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | final_label_repaired: '5 days per month' -> '1 cluster per month, multiple per cluster' |
| 17146 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 17167 | multiple per week | 1 per week | no |  |
| 17189 | 1 per 6 month | 1 per month | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17200 | 1 per month | 1 per month | yes |  |
| 17201 | 4 per month | 4 per month | yes |  |
| 17273 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | final_label_repaired: '1 per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 every 1 to 2 days' -> '1 per 1 to 2 day' |
