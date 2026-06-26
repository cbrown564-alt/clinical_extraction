# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-24

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Rare full-validation reason: full_validation750_diagnostic_after_test450_gap_continue_from_validation250_validation_only_error_analysis
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-reasoner`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Temperature: `0.0`
- Max tokens: `32000`
- Mode: `live`
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-24T13:29:46.991656+00:00`
- Run finished UTC: `2026-06-24T17:23:13.079071+00:00`
- Wall-clock elapsed: `14006.087` seconds (`233.435` minutes)
- Throughput: `0.053548` rows/sec (`18.675` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `3a866bf`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260624.jsonl`

## Summary

- Structured records: 745 / 750
- Call failures: 0
- Parse/schema/label issues: 5
- JSON dialect repairs: 0
- Deterministic repair notes: 415
- Exact selection evidence substrings: 731 / 750
- Purist validation accuracy/micro F1 proxy: 0.8213 (616 / 750)
- Pragmatic validation accuracy/micro F1 proxy: 0.8653 (649 / 750)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | final_label_repaired: '6-7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day'; evidence_not_exact_substring |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '1 cluster per 7-9 days' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: 'every 4 weeks' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: 'every 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per month' |
| 409 | 1 per month | 1 per month | yes |  |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 15 per 3 month | 2 per week | yes | final_label_repaired: '≤ twice per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 731 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 743 | multiple per week | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per week' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | unknown | multiple per month | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '2 per month' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every 2 months' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'bimonthly' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every 2 months' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 5 per month | 3 to 5 per month | no | final_label_repaired: '3 or 5 per month' -> '5 per month' |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 7 per 3 week | 5 to 7 per 3 week | yes | final_label_repaired: '5 to 7 seizures in 3 weeks' -> '7 per 3 week' |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes |  |
| 1223 | multiple per week | 3 to 4 per week | no |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | final_label_repaired: '5 to 7 per year' -> '5 to 7 per 10 month' |
| 1317 | unknown | unknown, multiple per cluster | yes | final_label_repaired: 'single cluster in 24 hours' -> 'unknown' |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 1 per day | 3 per day | yes | final_label_repaired: '3 tonic-clonic seizures in one day' -> '1 per day' |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes | final_label_repaired: 'multiple per week' -> '7 per week' |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes | final_label_repaired: 'multiple per week' -> '12 per week' |
| 1597 | 7 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per week | multiple per week | yes |  |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 episodes in 2 weeks' -> '3 per 2 week' |
| 1695 | no seizure frequency reference | multiple per month | yes |  |
| 1706 | unknown | multiple cluster per month, multiple per cluster | no | final_label_repaired: 'multiple clusters per month' -> 'unknown' |
| 1707 | multiple per week | multiple per week | yes | final_label_repaired: '1 cluster per week' -> 'multiple per week' |
| 1772 | 9 per 6 month | 11 per 6 month | yes | final_label_repaired: '9 per 6 months' -> '9 per 6 month' |
| 1773 | 1 to 2 per week | 11 per 3 month | no |  |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '2 per month' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '3 per month' -> '8 per 2 month' |
| 1866 | 2 to 3 per month | 8 per 2 month | no |  |
| 1880 | 3 to 4 per month | 8 per 2 month | no |  |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 in 3 months' -> '4 per 3 month' |
| 1914 | 5 per 3 month | 7 per 3 month | yes | final_label_repaired: '5 per 3 months' -> '5 per 3 month' |
| 1922 | 5 per 3 month | 7 per 3 month | yes | final_label_repaired: '1-2 per month' -> '5 per 3 month' |
| 1923 | no seizure frequency reference | 7 per 6 month | no | final_label_repaired: '5 in 6 months' -> 'no seizure frequency reference' |
| 1979 | 2 per week | 6 per 2 month | no |  |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '2 per month' -> '6 per 3 month' |
| 2023 | 4 per month | 5 per month | no |  |
| 2080 | multiple per month | multiple per month | yes |  |
| 2094 | multiple per month | multiple per month | yes |  |
| 2114 | multiple per month | multiple per month | yes |  |
| 2149 | unknown | unknown | yes |  |
| 2166 | unknown | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: 'multiple per week' -> '3 to 5 per 2 week' |
| 2233 | 3 to 4 per month | 6 to 7 per 2 month | yes |  |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: 'multiple per week' -> '7 to 8 per 3 week' |
| 2259 | 2 to 3 per month | 6 to 8 per 3 month | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | final_label_repaired: '6–8 per month' -> '6 to 8 per month'; evidence_not_exact_substring |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 2 to 3 per month | 5 to 7 per 2 month | yes |  |
| 2456 | 3 to 4 per week | 6 to 7 per 2 week | yes |  |
| 2459 | 5 per 5 month | 7 to 9 per 2 week | no | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 in 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week' |
| 2541 | 4 to 5 per week | 8 to 9 per 2 week | yes |  |
| 2548 | 2 to 3 per month | 5 to 6 per 2 month | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 1 to 2 per month | 3 to 4 per 2 month | yes |  |
| 2609 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | 1 per day | 1 per day | yes |  |
| 2628 | 1 per day | 1 per day | yes |  |
| 2678 | 1 per day | 1 per day | yes |  |
| 2681 | 1 per day | 1 per day | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: 'every other week' -> '1 per 2 week' |
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
| 2932 | 13 per 2 month | seizure free for 9 month | no | final_label_repaired: 'seizure free since 29/09/2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '13 per 2 month' |
| 2938 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free since 13-Nov-2015' -> 'seizure free for multiple year' |
| 2965 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free since 03-Sep-2017' -> 'seizure free for multiple year' |
| 2992 | seizure free for multiple year | seizure free for 7 month | yes | final_label_repaired: 'seizure free since 19-May-2024' -> 'seizure free for multiple year' |
| 3015 | seizure free for 1 year | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month'; evidence_not_exact_substring |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, multiple per cluster | 2 cluster per month, 5 per cluster | no | final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, multiple per cluster | 2 cluster per month, 5 per cluster | no | final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | unknown | unknown | yes |  |
| 3371 | 1 per 8 week | unknown | no | final_label_repaired: '1 event in the past 8 weeks' -> '1 per 8 week' |
| 3436 | unknown | unknown | yes | evidence_not_exact_substring |
| 3468 | unknown | unknown | yes | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 3469 | unknown | unknown | yes | final_label_repaired: 'perimenstrual cluster pattern' -> 'unknown' |
| 3482 | unknown | unknown | yes |  |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 | unknown | unknown | yes |  |
| 3528 | unknown | unknown | yes | evidence_not_exact_substring |
| 3532 | unknown | unknown | yes |  |
| 3534 | unknown | unknown | yes |  |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 per week' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 clusters per week in bad weeks' -> '7 per week' |
| 3681 | multiple per week | 9 per month | no |  |
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
| 3988 | multiple per week | multiple per week | yes |  |
| 3995 | 1 per month | 1 per month | yes | final_label_repaired: 'approximately monthly' -> '1 per month' |
| 3999 | 1 per month | 1 per month | yes |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: 'every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2-3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: 'multiple per week' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4258 | 4 per week | 4 per week | yes | evidence_not_exact_substring |
| 4337 | 23 per 1 month | 3 per 3 month | no | final_label_repaired: '3 events in 4 months' -> '3 per 4 month'; final_label_repaired: '3 per 4 month' -> '23 per 1 month' |
| 4345 | 4 per 1 month | 4 per month | yes | final_label_repaired: '4 per month' -> '4 per 1 month' |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '2 per month' -> '5 per 2 month' |
| 4402 | 14 per 14 month | 7 per 7 month | yes | final_label_repaired: '1 per month' -> '7 per 7 month'; final_label_repaired: '7 per 7 month' -> '14 per 14 month' |
| 4410 | 8 per 14 month | 4 per 7 month | yes | final_label_repaired: '1 per month' -> '4 per 7 month'; final_label_repaired: '4 per 7 month' -> '8 per 14 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: 'approximately every 3 weeks' -> '1 per 3 week' |
| 4624 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | final_label_repaired: '1 cluster per 3 to 4 days' -> '1 per 3 to 4 day' |
| 4631 | 1 to 2 per month | 1 per 14 to 21 day | yes |  |
| 4690 | multiple per day | multiple per day | yes | final_label_repaired: 'approximately 10 per hour' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | final_label_repaired: '9 per hour' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | final_label_repaired: '4 per hour' -> 'multiple per day' |
| 4709 | multiple per day | multiple per day | yes | final_label_repaired: '6 per hour' -> 'multiple per day' |
| 4731 | unknown | unknown | yes |  |
| 4732 | unknown | unknown | yes |  |
| 4771 | multiple per month | unknown | yes |  |
| 4839 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | seizure free for 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5092 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5141 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for approximately 2 months' -> 'seizure free for 2 month' |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early 2024' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free since March 2023' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for multiple year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for over 18 months' -> 'seizure free for multiple year' |
| 5379 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 5476 | unknown | unknown | yes |  |
| 5490 | unknown | unknown | yes | evidence_not_exact_substring |
| 5491 | unknown | unknown | yes |  |
| 5504 | unknown | unknown | yes |  |
| 5507 | 3 per 4 month | unknown | no | final_label_repaired: '3 episodes in 4 months' -> '3 per 4 month' |
| 5528 | 1 per month | 1 per month | yes | final_label_repaired: '1 event in past month' -> '1 per month' |
| 5534 | unknown | 1 per multiple month | yes |  |
| 5551 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 5567 | multiple per week | multiple per week | yes |  |
| 5584 | multiple per week | multiple per week | yes |  |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per 8 days' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 events per 4 months' -> '3 per 4 month' |
| 5763 | 2 to 3 per month | 2 per month | yes |  |
| 5767 | 1 per 1 to 2 week | 1 per 1 to 2 week | yes | final_label_repaired: 'every 1-2 weeks' -> '1 per 1 to 2 week' |
| 5791 | 1 per month | 1 per month | yes |  |
| 5827 | multiple per week | multiple per week | yes |  |
| 5837 | unknown | 2 cluster per 3 week, multiple per cluster | no | final_label_repaired: '2 clusters in 3 weeks' -> 'unknown' |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '2 to 3 per month' -> '4 per 6 week' |
| 5873 | multiple per week | multiple per week | yes |  |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6-8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: 'less than once per week' -> '1 per 2 to 3 week' |
| 5974 | unknown | unknown | yes |  |
| 5977 | multiple per 6 week | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per 6 week' |
| 5995 | 3 per 7 month | 1 per 3 months | yes | final_label_repaired: 'less than 1 per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '3 per 7 month' |
| 5996 | unknown | unknown | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes |  |
| 6034 | unknown | unknown | yes |  |
| 6065 | 5 per month | 5 per month | yes |  |
| 6077 | 1 per 8 month | unknown | no | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 6087 | unknown | unknown | yes |  |
| 6094 | 2 to 3 per month | 3 per month | yes |  |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | unknown | unknown | yes |  |
| 6137 | 1 per 2 to 3 week | 1 per 2 week | yes | final_label_repaired: '1 per 2-3 weeks' -> '1 per 2 to 3 week' |
| 6153 | 6 per month | 9 per month | yes |  |
| 6180 | multiple per week | multiple per week | yes |  |
| 6192 | unknown | unknown | yes |  |
| 6204 | 2 per month | 2 per month | yes |  |
| 6209 | multiple per day | multiple per day | yes | final_label_repaired: 'daily' -> 'multiple per day' |
| 6244 | 2 per week | unknown | no |  |
| 6251 | no seizure frequency reference | 1 per 1 to 2 month | no | final_label_repaired: '1 in 2 months' -> 'no seizure frequency reference' |
| 6273 | unknown | unknown | yes |  |
| 6319 | 1 per week | 1 per week | yes |  |
| 6321 | 1 per month | unknown | no | final_label_repaired: 'approximately 1 per month' -> '1 per month' |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 6358 | seizure free for 16 month | seizure free for 15 to 16 months | yes |  |
| 6368 | 1 per 1 to 2 week | unknown | no | final_label_repaired: '1 cluster per 1-2 weeks' -> '1 per 1 to 2 week' |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 6509 | multiple per week | 1 per week | no |  |
| 6571 | seizure free for 3.5 month | unknown | no | final_label_repaired: 'seizure free for 3.5 months' -> 'seizure free for 3.5 month' |
| 6607 | unknown | unknown | yes | evidence_not_exact_substring |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 events in 4 months' -> '3 per 4 month' |
| 6701 | 4 per 3 week | 4 per 3 week | yes | final_label_repaired: '4 per 3 weeks' -> '4 per 3 week' |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: 'once every 6–8 weeks' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes |  |
| 6952 | 2 per week | 2 per week | yes | final_label_repaired: 'approximately 2 per week' -> '2 per week' |
| 6967 | unknown | unknown | yes |  |
| 6987 | unknown | unknown | yes |  |
| 7093 | unknown | unknown | yes | evidence_not_exact_substring |
| 7126 | unknown | unknown | yes |  |
| 7141 | 1 per month | unknown | no |  |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no | final_label_repaired: '3 clusters in 6 weeks' -> 'unknown' |
| 7168 | unknown | unknown | yes |  |
| 7192 | multiple per week | multiple per week | yes | final_label_repaired: 'multiple clusters per week' -> 'multiple per week' |
| 7195 | 1 per month | unknown | no | final_label_repaired: 'unknown' -> '1 per month' |
| 7196 | 6 per 6 week | 1 per week | yes | final_label_repaired: '1 per week' -> '6 per 6 week' |
| 7198 | unknown | unknown | yes |  |
| 7275 | 3 per 2 month | 1 per month | no | final_label_repaired: '1 per month' -> '3 per 12 week'; final_label_repaired: '3 per 12 week' -> '3 per 2 month' |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | final_label_repaired: '2 clusters in 6 weeks' -> 'unknown' |
| 7409 | multiple per week | unknown | yes | final_label_repaired: 'most weeks' -> 'multiple per week' |
| 7455 | unknown | unknown | yes |  |
| 7475 | 2 per 4 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 2 month'; final_label_repaired: '2 per 2 month' -> '2 per 4 month' |
| 7491 | unknown | unknown | yes |  |
| 7506 | unknown | unknown | yes |  |
| 7573 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '2 per month' -> '1 per 2 week' |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | 3 to 6 per month | 3 to 7 per month | yes |  |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 7818 | seizure free for 2 year | seizure free for 2 years | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free (unspecified duration)' -> 'seizure free for multiple year' |
| 7859 | unknown | unknown | yes |  |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7961 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: 'once every 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8079 | seizure free for 1 year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 1 year 6 months' -> 'seizure free for 1 year' |
| 8089 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free since 29-May-2023' -> 'seizure free for multiple year' |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8144 | unknown | seizure free for multiple month | no |  |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8160 | 1 per month | seizure free for multiple month | no |  |
| 8180 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8188 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8224 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for at least 3 months' -> 'seizure free for multiple year' |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8354 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early June 2025' -> 'seizure free for multiple year' |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 8400 | unknown | seizure free for multiple month | no |  |
| 8419 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 8474 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8577 | seizure free for 18 month | seizure free for multiple month | yes |  |
| 8581 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8808 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month'; evidence_not_exact_substring |
| 8820 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 8835 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 8854 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 8922 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8924 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8938 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9002 | 7 per 10 month | 7 per year | yes | final_label_repaired: '7 in 2024' -> '7 per 10 month' |
| 9063 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 9103 | unknown | unknown | yes |  |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9190 | 0 per 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 month' -> '0 per 3 month' |
| 9215 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 9238 | no seizure frequency reference | seizure free for multiple month | no | final_label_repaired: 'no definite seizures' -> 'no seizure frequency reference' |
| 9250 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since January 2025' -> 'seizure free for multiple year' |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 4 per 2 month | 4 per 6 month | no | final_label_repaired: '2 per month' -> '4 per 2 month' |
| 9462 | 14 per 22 month | 7 per 11 month | yes | final_label_repaired: '0 to 2 per month' -> '7 per 11 month'; final_label_repaired: '7 per 11 month' -> '14 per 22 month' |
| 9496 | 12 per 24 month | 6 per 12 month | yes | final_label_repaired: 'less than 1 per month' -> '6 per 12 month'; final_label_repaired: '6 per 12 month' -> '12 per 24 month' |
| 9547 | unknown | unknown | yes |  |
| 9588 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since February 2025' -> 'seizure free for multiple year' |
| 9704 | unknown | unknown | yes |  |
| 9815 | multiple per day | multiple per day | yes | final_label_repaired: '9 per hour' -> 'multiple per day' |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes |  |
| 9888 | unknown | unknown | yes |  |
| 9912 | unknown | unknown | yes |  |
| 9937 | no seizure frequency reference | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'every few weeks' -> 'no seizure frequency reference' |
| 9943 | unknown | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: 'clusters every 4 to 5 weeks' -> 'unknown' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 clusters per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | 3 per month | 3 cluster per month, multiple per cluster | no |  |
| 10147 | unknown | unknown | yes |  |
| 10183 | unknown | unknown | yes |  |
| 10189 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10200 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes |  |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no | final_label_repaired: '4 clusters per month' -> 'unknown' |
| 10245 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10260 | unknown | unknown | yes |  |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes |  |
| 10371 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free since 11 Aug 2023' -> 'seizure free for multiple year' |
| 10383 | 5 per week | 1 cluster per week, 5 per cluster | yes |  |
| 10386 | unknown | 1 cluster per week, 2 to 3 per cluster | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10434 | multiple per week | multiple cluster per week, 2 to 3 per cluster | no |  |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes |  |
| 10517 | 3 to 4 per week | 3 to 4 cluster per week, multiple per cluster | no | final_label_repaired: '3-4 nights per week' -> '3 to 4 per week' |
| 10542 | 2 per 3 month | unknown, 2 to 4 per cluster | no | final_label_repaired: 'unknown' -> '2 per 3 month' |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10583 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes |  |
| 10618 | multiple per week | unknown, 4 to 6 per cluster | yes |  |
| 10629 | unknown | unknown | yes |  |
| 10630 | no seizure frequency reference | multiple cluster per 2 week, 5 per cluster | no | final_label_repaired: 'several per fortnight' -> 'no seizure frequency reference' |
| 10673 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 10677 | 1 per month | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'monthly' -> '1 per month' |
| 10753 | no seizure frequency reference | unknown | yes |  |
| 10807 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10829 | 2 per 2 year | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 2 year' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, multiple per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 3 clusters per month' -> '2 to 3 cluster per month, multiple per cluster' |
| 10942 | 2 cluster per month, multiple per cluster | 2 cluster per month, 5 per cluster | no | final_label_repaired: '2 clusters per month' -> '2 cluster per month, multiple per cluster' |
| 10965 | unknown | 2 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown' |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '3 clusters per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | final_label_repaired: '1-2 clusters per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 4 clusters per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 cluster days per month' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 per month' -> '2 cluster per month, 6 per cluster' |
| 11131 | unknown | 2 cluster per month, 3 to 4 per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 11197 | unknown | 1 cluster per month, 4 to 6 per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 11216 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free since 25 December 2023' -> 'seizure free for multiple year' |
| 11254 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free since 31 May 2021' -> 'seizure free for multiple year' |
| 11259 | unknown | unknown | yes |  |
| 11262 | unknown | unknown | yes |  |
| 11272 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free since 20 December 2016' -> 'seizure free for multiple year' |
| 11282 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 11337 | unknown | unknown | yes |  |
| 11350 | multiple per week | unknown | yes |  |
| 11380 | unknown | unknown | yes | final_label_repaired: '1 cluster per 2 weeks' -> 'unknown' |
| 11389 | unknown | unknown | yes |  |
| 11400 | 1 per day | no seizure frequency reference | no | final_label_repaired: 'no seizure frequency reference' -> '1 per day' |
| 11405 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11408 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11409 | unknown | no seizure frequency reference | yes |  |
| 11411 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | unknown | no seizure frequency reference | yes |  |
| 11658 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11737 | unknown | no seizure frequency reference | yes |  |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11824 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11841 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 12036 | multiple per day | multiple per day | yes |  |
| 12041 | multiple per day | multiple per day | yes |  |
| 12046 | multiple per day | multiple per day | yes |  |
| 12051 | 1 per day | multiple per day | no | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12111 | multiple per week | multiple per week | yes |  |
| 12127 | multiple per week | multiple per week | yes |  |
| 12130 | multiple per week | multiple per week | yes |  |
| 12139 | multiple per week | multiple per week | yes |  |
| 12145 | multiple per week | multiple per week | yes |  |
| 12192 | 1 per day | 1 per day | yes |  |
| 12218 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12236 | unknown | 1 per day | no | final_label_repaired: '1 cluster per day' -> 'unknown' |
| 12246 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12314 | 3 per week | 3 per week | yes |  |
| 12366 | 4 per day | 4 per day | yes |  |
| 12378 | 4 per day | 4 per day | yes |  |
| 12383 | 4 per day | 4 per day | yes |  |
| 12403 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 12412 | 2 per day | 2 per day | yes |  |
| 12422 | 1 per day | 1 per day | yes |  |
| 12438 | 1 per day | 1 per day | yes |  |
| 12456 | 1 per day | 1 per day | yes |  |
| 12460 | 1 per day | 1 per day | yes |  |
| 12468 | 1 per day | 1 per day | yes |  |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes | final_label_repaired: '3-4 per day' -> '3 to 4 per day' |
| 12502 | 4 per day | 4 per day | yes |  |
| 12506 | 4 per day | 4 per day | yes |  |
| 12537 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12548 | 1 per day | 1 per day | yes |  |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12556 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12562 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12573 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12584 | 1 per week | 1 per week | yes |  |
| 12641 | 1 per day | 1 per day | yes |  |
| 12665 | 1 per day | 1 per day | yes |  |
| 12667 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12676 | 1 per day | 1 per day | yes |  |
| 12679 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | seizure free for multiple year | 4 per day | no | final_label_repaired: 'seizure free since previous review' -> 'seizure free for multiple year' |
| 12788 | 6 per 4 month | 6 per 4 month | yes | final_label_repaired: '1 to 2 per month' -> '6 per 4 month' |
| 12810 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '2 to 3 per month' -> '5 per 2 month' |
| 12823 | 9 per month | 9 per month | yes | final_label_repaired: '9 in 22 days' -> '9 per month' |
| 12827 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '1 per month' -> '5 per 5 month' |
| 12835 | 4 per month | 4 per month | yes | final_label_repaired: '4 seizures in 2015 so far' -> '4 per month' |
| 12877 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '2 to 3 per month' -> '10 per 4 month' |
| 12882 | 7 per 4 month | 7 per 4 month | yes | final_label_repaired: '2 per month' -> '7 per 4 month' |
| 12901 | 8 per 5 month | 8 per 5 month | yes | final_label_repaired: '2 per month' -> '8 per 5 month' |
| 12949 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '1-2 per month' -> '9 per 6 month' |
| 12950 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 12963 | unknown | unknown | yes |  |
| 12979 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 in year to date' -> '3 per 4 month' |
| 13008 | 4 per month | 4 per month | yes | final_label_repaired: '4 seizures in about 3 weeks (since Jan 1, 2021)' -> '4 per month' |
| 13011 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: 'less than 1 per month' -> '3 per 4 month' |
| 13051 | 2 per 8 month | 2 per 8 month | yes | final_label_repaired: 'unknown' -> '2 per 8 month' |
| 13058 | 1 per 7 month | 2 per 7 month | no | final_label_repaired: '1 generalized tonic-clonic seizure with preceding absence cluster in 3 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 7 month' |
| 13114 | multiple per week | 1 per year | no |  |
| 13122 | 3 per 1 year | 3 per year | yes | final_label_repaired: '3 tonic seizures in a single cluster' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year' |
| 13149 | 1 per month | 3 per year | no | final_label_repaired: '1 seizure in the past month' -> '1 per month' |
| 13178 | 1 per 6 month | 1 per 6 month | yes | final_label_repaired: 'unknown' -> '1 per 6 month' |
| 13190 | 1 per 5 month | 1 per 5 month | yes | final_label_repaired: 'unknown' -> '1 per 5 month' |
| 13209 | 1 per 4 to 5 week | 1 per 8 month | no | final_label_repaired: '1 cluster every 4-5 weeks' -> '1 per 4 to 5 week' |
| 13267 | unknown | 2 per 5 month | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 13290 | 2 per 6 month | 4 per 6 month | yes | final_label_repaired: '2 seizures on one day' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 per 6 month' |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13450 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 13471 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13478 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over several years' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 1.5 year | seizure free for 1.5 year | yes |  |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13627 | 1 per month | 64 per 12 month | no | final_label_repaired: '1 day per month' -> '1 per month' |
| 13635 | 40 per 6 month | 47 per 7 month | yes | final_label_repaired: '7 days per month' -> '7 per month'; final_label_repaired: '7 per month' -> '40 per 6 month' |
| 13711 | 35 per 8 month | 76 per 12 month | yes | final_label_repaired: '12 days per month' -> '12 per month'; final_label_repaired: '12 per month' -> '35 per 8 month' |
| 13721 | 10 per month | 77 per 12 month | yes | final_label_repaired: '10 days with seizures per month' -> '10 per month' |
| 13732 | 27 per 6 month | 52 per 8 month | yes | final_label_repaired: '2 days per month' -> '2 per month'; final_label_repaired: '2 per month' -> '27 per 6 month' |
| 13843 | no seizure frequency reference | seizure free for multiple month | no |  |
| 13858 | unknown | seizure free for multiple month | no |  |
| 13889 | unknown | seizure free for multiple month | no |  |
| 13893 | 2 per year | 2 per year | yes |  |
| 13922 | 2 per month | unknown | no | final_label_repaired: '2 seizures' -> '2 per month' |
| 14002 | unknown | unknown | yes |  |
| 14025 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year' |
| 14029 | unknown | unknown | yes |  |
| 14040 | unknown | unknown | yes | evidence_not_exact_substring |
| 14076 | unknown | unknown | yes |  |
| 14092 | 1 per 3 month | unknown | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '1 per 3 month' |
| 14096 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 myoclonic jerks since last clinic appointment' -> 'no seizure frequency reference' |
| 14137 | 1 per month | unknown | no |  |
| 14146 | unknown | unknown | yes |  |
| 14187 | 2 to 3 per month | 2 to 3 per month | yes | final_label_repaired: '2 to 3 seizures' -> '2 to 3 per month' |
| 14214 | no seizure frequency reference | 2 to 4 per month | no | final_label_repaired: '2 to 4 seizures in a cluster' -> 'no seizure frequency reference' |
| 14250 | 2 per week | 2 per month | no |  |
| 14282 | multiple per week | multiple per month | yes |  |
| 14284 | 2 to 3 per week | 2 to 3 per month | no |  |
| 14317 | 4 per month | 4 per 2 month | no | final_label_repaired: '4 seizures' -> '4 per month' |
| 14332 | seizure free for multiple year | 5 per 2 month | no | final_label_repaired: 'seizure free since October 2017' -> 'seizure free for multiple year' |
| 14335 | seizure free for multiple year | 3 to 4 per 2 month | no | final_label_repaired: 'seizure free for approximately 8 weeks' -> 'seizure free for multiple year' |
| 14383 | 3 to 4 per 3 month | 3 to 4 per 3 month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '3 to 4 per 3 month' |
| 14454 | unknown | 2 per 2 month | no |  |
| 14524 | unknown | 2 per 6 month | no | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 14530 | unknown | 2 per 2 month | no |  |
| 14540 | seizure free for multiple year | 2 per 8 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14562 | unknown | 3 per 6 month | no |  |
| 14567 | unknown | 3 per 3 month | no |  |
| 14581 | 1 per 1 month | 2 per 3 month | no | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14587 | unknown | 2 per 3 month | no |  |
| 14592 | unknown | 3 per 5 month | no |  |
| 14611 | seizure free for multiple year | 2 per 4 month | no | final_label_repaired: 'seizure free since May 2020' -> 'seizure free for multiple year' |
| 14628 | unknown | 2 per 2 month | no |  |
| 14635 | seizure free for multiple year | 5 per 4 month | no | final_label_repaired: 'seizure free since November 2016' -> 'seizure free for multiple year' |
| 14645 | seizure free for multiple year | 2 per 6 month | no | final_label_repaired: 'seizure free for less than 1 month' -> 'seizure free for multiple year' |
| 14662 | unknown | 3 per 4 month | no |  |
| 14672 | seizure free for multiple year | 3 per 8 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14706 | 2 per 5 month | 2 per 5 month | yes | final_label_repaired: '2 per 5 months' -> '2 per 5 month' |
| 14765 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14806 | no seizure frequency reference | 1 per 2 month | no | final_label_repaired: '1 cluster of auras' -> 'no seizure frequency reference' |
| 14810 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for over 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14821 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for over 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14872 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14943 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 14949 | 1 per month | 1 per month | yes |  |
| 14965 | unknown | 1 per 3 month | no |  |
| 14973 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 15004 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for 2.5 months' -> 'seizure free for 2.5 month'; final_label_repaired: 'seizure free for 2.5 month' -> '1 per 3 month' |
| 15012 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15021 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 15094 | 3 per 13 month | 4 per 13 month | yes | final_label_repaired: 'less than 1 per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '3 per 13 month' |
| 15108 | 2 to 3 per 15 month | 3 to 4 per 15 month | no | final_label_repaired: 'less than 1 per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '2 to 3 per 15 month' |
| 15127 | 4 per 13 month | 5 per 13 month | yes | final_label_repaired: '4 events in 13 months' -> '4 per 13 month' |
| 15129 | unknown | 4 per 15 month | no |  |
| 15141 | 3 to 4 per 15 month | 4 to 5 per 15 month | yes | final_label_repaired: 'less than 1 per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '3 to 4 per 15 month' |
| 15168 | unknown | multiple per 15 month | yes |  |
| 15193 | unknown | multiple per 13 month | yes |  |
| 15242 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15262 | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | yes | final_label_repaired: 'unknown' -> 'multiple cluster per 13 month, multiple per cluster' |
| 15267 | 3 per 14 month | 3 per 14 month | yes | final_label_repaired: '3 single jerks' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 14 month' |
| 15306 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | final_label_repaired: 'unknown' -> '2 to 3 per 15 month' |
| 15317 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | final_label_repaired: '2 to 3' -> '2 to 3 per month'; final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |
| 15376 | multiple per day | 1 cluster per 2 week, 4 to 6 per cluster | no |  |
| 15404 | multiple per day | 1 cluster per 4 month, 3 to 4 per cluster | no |  |
| 15429 | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | yes | final_label_repaired: 'multiple per day (clusters)' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15431 | 5 per 4 month | 1 cluster per 4 month, 5 per cluster | yes | final_label_repaired: 'unknown' -> '5 per 4 month' |
| 15442 | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per 4 day, 2 per cluster' |
| 15470 | multiple per week | 1 cluster per 5 day, multiple per cluster | no |  |
| 15479 | unknown | 1 cluster per 4 to 5 day, 2 per cluster | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 15497 | no seizure frequency reference | 1 cluster per 4 to 5 day, 5 per cluster | no | final_label_repaired: '5 per 24 hours' -> 'no seizure frequency reference' |
| 15503 | unknown | 1 cluster per 5 day, 3 to 4 per cluster | no | final_label_repaired: '3-4 seizures per 24 hours in clusters' -> 'unknown' |
| 15513 | 1 cluster per 5 day, 2 to 3 per cluster | 1 cluster per 4 to 5 day, 2 to 3 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 2 to 3 per cluster' |
| 15519 | 2 per month | 1 cluster per 4 day, 3 per cluster | no | final_label_repaired: '2 clusters per month' -> '2 per month' |
| 15529 | no seizure frequency reference | 1 cluster per 3 day, 4 per cluster | no | final_label_repaired: '4 in 24 hours' -> 'no seizure frequency reference' |
| 15593 | 13 per 7 month | 1 cluster per 5 day, 2 to 4 per cluster | no | final_label_repaired: '2-4 seizures per cluster, clusters every 5-6 days' -> '1 cluster per 5 day, 2 to 4 per cluster'; final_label_repaired: '1 cluster per 5 day, 2 to 4 per cluster' -> '13 per 7 month'; evidence_not_exact_substring |
| 15614 | 3 per week | 3 per week | yes |  |
| 15628 | multiple per week | multiple per week | yes |  |
| 15639 | 2 per week | 2 per week | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 15672 | 1 per day | 1 per day | yes | final_label_repaired: '1 cluster per day' -> '1 per day' |
| 15697 | 1 per day | 1 per day | yes | final_label_repaired: 'nearly 1 per day' -> '1 per day' |
| 15715 | 1 per day | 1 per day | yes | final_label_repaired: '1 cluster per day' -> '1 per day' |
| 15745 | 2 to 3 per week | 2 to 3 per week | yes | final_label_repaired: '2-3 days per week' -> '2 to 3 per week' |
| 15766 | 4 per week | 4 per week | yes | final_label_repaired: '4 days per week' -> '4 per week' |
| 15768 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15771 | 3 per week | 3 per week | yes | final_label_repaired: '3 days per week' -> '3 per week' |
| 15772 | 2 per week | 2 per week | yes |  |
| 15774 | 2 per week | 2 per week | yes |  |
| 15783 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15802 | 7 per week | 7 per week | yes |  |
| 15831 | 2 to 4 per day | 2 to 4 per day | yes |  |
| 15834 | 5 per week | 5 per week | yes |  |
| 15964 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: 'multiple per week' -> '11 per 3 month' |
| 15965 | 13 per 2 month | 13 per 2 month | yes | final_label_repaired: '6 per month' -> '13 per 2 month' |
| 15966 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: 'unknown' -> '5 per 3 month' |
| 15982 | 4 per 2 month | 9 per 2 month | no | final_label_repaired: '5 per month' -> '4 per 2 month' |
| 15986 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '1 per month' -> '11 per 3 month' |
| 15992 | 10 per 2 month | 7 per 2 month | no | final_label_repaired: '3 per month' -> '10 per 2 month' |
| 15997 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: 'unknown' -> '10 per 3 month' |
| 16021 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '5 per month' -> '9 per 3 month' |
| 16041 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '4 per month' -> '9 per 3 month' |
| 16084 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '4 per month' -> '8 per 4 month' |
| 16091 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '2 per month' -> '3 per 3 month' |
| 16097 | 16 per 3 month | 17 per 4 month | yes | final_label_repaired: '6 per month' -> '17 per 4 month'; final_label_repaired: '17 per 4 month' -> '16 per 3 month' |
| 16107 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '4 per month' -> '8 per 3 month' |
| 16108 | 12 per 4 month | 12 per 4 month | yes | final_label_repaired: '5 per month' -> '12 per 4 month' |
| 16132 | 15 per 3 month | 15 per 3 month | yes | final_label_repaired: '2 per month' -> '15 per 3 month' |
| 16133 | 18 per 4 month | 18 per 4 month | yes | final_label_repaired: '6 per month' -> '18 per 4 month' |
| 16161 | 11 per 3 month | 18 per 3 month | no | final_label_repaired: '7 per month' -> '11 per 3 month' |
| 16162 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '6 per month' -> '11 per 3 month' |
| 16181 | 11 per 3 month | 15 per 4 month | yes | final_label_repaired: '4 per month' -> '11 per 3 month' |
| 16195 | 16 per 4 month | 16 per 4 month | yes | final_label_repaired: '6 per month' -> '16 per 4 month' |
| 16203 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '1 per month' -> '9 per 3 month' |
| 16204 | 4 per 2 month | 5 per 3 month | yes | final_label_repaired: '1 per month' -> '4 per 2 month' |
| 16220 | 11 per 4 month | 11 per 4 month | yes | final_label_repaired: '4 per month' -> '11 per 4 month' |
| 16324 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: '3 to 4 per month' -> '7 per 2 month'; final_label_repaired: '7 per 2 month' -> '10 per 3 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '1 per month' -> '7 per 3 month' |
| 16356 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster every 4 days' -> '1 per 4 day' |
| 16394 | 1 per 2 to 4 day | 1 per 2 to 4 day | yes | final_label_repaired: 'cluster every 2 to 4 days' -> '1 per 2 to 4 day' |
| 16408 | 1 per 3 day | 1 per 3 day | yes | final_label_repaired: 'every 3 days' -> '1 per 3 day' |
| 16429 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: 'every 2 to 3 days' -> '1 per 2 to 3 day' |
| 16432 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'multiple per week' -> '1 per 2 day' |
| 16450 | multiple per week | 1 per multiple day | yes |  |
| 16529 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster every 5 days' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '2-3 per week' -> '1 per 2 to 3 day' |
| 16574 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster every 4 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 day' |
| 16590 | 1 per 4 to 5 day | 1 per 4 to 5 day | yes | final_label_repaired: '1 cluster per 4 to 5 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 to 5 day' |
| 16618 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster per 5 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 5 day' |
| 16645 | 5 per 4 month | 5 per 7 month | no | final_label_repaired: 'unknown' -> '4 per 2 month'; final_label_repaired: '4 per 2 month' -> '5 per 4 month' |
| 16674 | 6 per 4 month | 7 per 6 month | yes | final_label_repaired: 'unknown' -> '6 per 4 month' |
| 16685 | 9 per 2 month | 10 per 3 month | no | final_label_repaired: '6 per month' -> '9 per 2 month' |
| 16697 | unknown | 3 per 6 month | no | evidence_not_exact_substring |
| 16704 | unknown | 9 per 6 month | no |  |
| 16714 | 5 per 4 month | 5 per 6 month | no | final_label_repaired: 'no seizure frequency reference' -> '5 per 4 month' |
| 16717 | unknown | 5 per 6 month | no |  |
| 16719 | 7 per 4 month | 7 per 6 month | yes | final_label_repaired: 'once weekly' -> '1 per week'; final_label_repaired: '1 per week' -> '7 per 4 month' |
| 16728 | 4 per 4 month | 4 per 6 month | no | final_label_repaired: 'unknown' -> '4 per 4 month' |
| 16750 | 4 per 4 month | 6 per 7 month | no | final_label_repaired: 'seizure free for less than 1 month' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '4 per 4 month'; evidence_not_exact_substring |
| 16757 | 18 per 3 month | 13 per 6 month | no | final_label_repaired: 'recent clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '18 per 3 month' |
| 16758 | 9 per 5 month | 9 per 5 month | yes | final_label_repaired: '1 tonic seizure in April 2011' -> 'unknown'; final_label_repaired: 'unknown' -> '9 per 5 month' |
| 16772 | 15 per 2 month | 9 per 5 month | no | final_label_repaired: 'multiple per month' -> '15 per 2 month' |
| 16774 | 19 per 4 month | 19 per 7 month | no | final_label_repaired: '3 per month' -> '19 per 4 month' |
| 16780 | unknown | 3 per 7 month | no |  |
| 16824 | 11 per 3 month | 11 per 5 month | yes | final_label_repaired: '7 per month' -> '11 per 3 month' |
| 16833 | 7 per 3 month | 8 per 6 month | yes | final_label_repaired: '2 events' -> '2 per month'; final_label_repaired: '2 per month' -> '7 per 3 month' |
| 16839 | 12 per 3 month | 9 per 4 month | no | final_label_repaired: '2 to 3 per month' -> '12 per 3 month' |
| 16867 | 5 per 4 month | 6 per 7 month | no | final_label_repaired: 'unknown' -> '5 per 4 month' |
| 16907 | 8 per 4 month | 9 per 6 month | yes | final_label_repaired: 'unknown' -> '8 per 4 month' |
| 16938 | 2 per week | 2 per week | yes | final_label_repaired: 'up to 2 per week' -> '2 per week' |
| 16947 | 2 per week | 2 per week | yes |  |
| 16961 | 2 per week | 2 per week | yes | final_label_repaired: 'twice per week' -> '2 per week' |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes |  |
| 17001 | 5 per week | 5 per week | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 17110 | 4 to 5 per week | 4 to 5 cluster per week, multiple per cluster | no |  |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | final_label_repaired: '5 days per month with clusters' -> '1 cluster per month, multiple per cluster' |
| 17146 | 1 per day | 1 per day | yes |  |
| 17167 | 1 per week | 1 per week | yes |  |
| 17189 | 1 per month | 1 per month | yes |  |
| 17200 | 1 per month | 1 per month | yes |  |
| 17201 | 4 per month | 4 per month | yes |  |
| 17273 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | final_label_repaired: '1 per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 every 1 to 2 days' -> '1 per 1 to 2 day' |
