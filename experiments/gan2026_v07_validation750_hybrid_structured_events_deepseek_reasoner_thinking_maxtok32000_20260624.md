# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-24

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 490 rows.
Rare full-validation reason: validation750_v07_deepseek_reasoner_prompt_iteration_after_validation_error_analysis_validation250_too_low_signal
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-reasoner`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.7`
- Temperature: `0.0`
- Max tokens: `32000`
- Mode: `live`
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `992d74a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v07_validation750_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260624.jsonl`

## Summary

- Structured records: 486 / 490
- Call failures: 0
- Parse/schema/label issues: 4
- JSON dialect repairs: 0
- Deterministic repair notes: 267
- Exact selection evidence substrings: 480 / 490
- Purist validation accuracy/micro F1 proxy: 0.8776 (430 / 490)
- Pragmatic validation accuracy/micro F1 proxy: 0.8898 (436 / 490)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: '≤4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: 'every 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '1 cluster per week' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: 'every 4 weeks' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: 'every 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 every 3 weeks' -> '1 per 3 week' |
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
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '1 per week' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: 'twice every 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 | unknown | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: 'once every 7 to 10 days' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | unknown | multiple per month | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: 'every other week' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'bimonthly' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every 2 months' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every other month' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 seizure every 2 months' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 7 per 3 week | 5 to 7 per 3 week | yes | final_label_repaired: 'multiple per week' -> '7 per 3 week' |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | final_label_repaired: '5 to 7 per year' -> '5 to 7 per 10 month' |
| 1317 | unknown | unknown, multiple per cluster | yes | final_label_repaired: 'multiple episodes in one day (cluster)' -> 'unknown' |
| 1357 | 1 per day | 1 per day | yes | final_label_repaired: '1 seizure (yesterday)' -> '1 per day' |
| 1363 | 1 per day | 3 per day | yes | final_label_repaired: '1 cluster of 3 tonic-clonic seizures' -> '1 per day' |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes | final_label_repaired: '1 per day' -> '7 per week' |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 7 per week | 12 per week | yes |  |
| 1597 | 7 per month | 12 per month | yes |  |
| 1636 | 3 per month | 5 per month | no |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per week | multiple per week | yes |  |
| 1694 | 5 per week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: 'approximately 1.5 per week' -> '5 per week' |
| 1695 | multiple per month | multiple per month | yes |  |
| 1706 | unknown | multiple cluster per month, multiple per cluster | no | final_label_repaired: 'multiple clusters per month' -> 'unknown' |
| 1707 | multiple per week | multiple per week | yes |  |
| 1772 | 5 per month | 11 per 6 month | no | final_label_repaired: '1.5 per month' -> '5 per month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '11 in 3 months' -> '11 per 3 month' |
| 1790 | no seizure frequency reference | 8 per 4 month | no | final_label_repaired: '6 in 4 months' -> 'no seizure frequency reference' |
| 1794 | 3 per month | 8 per 2 month | no |  |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '4 per month' -> '8 per 2 month' |
| 1880 | 3 cluster per month, 4 per cluster | 8 per 2 month | no | final_label_repaired: '3 clusters per month' -> '3 cluster per month, 4 per cluster' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 events in past 3 months' -> '4 per 3 month' |
| 1914 | 1 to 2 per month | 7 per 3 month | yes |  |
| 1922 | 5 per 3 month | 7 per 3 month | yes | final_label_repaired: '5 per 3 months' -> '5 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 per 6 months' -> '7 per 6 month' |
| 1979 | unknown | 6 per 2 month | no | final_label_repaired: '2 clusters per week' -> 'unknown' |
| 1980 | 1 per month | 6 per 3 month | no |  |
| 2023 | 4 per month | 5 per month | no |  |
| 2080 | multiple per month | multiple per month | yes |  |
| 2094 | multiple per month | multiple per month | yes |  |
| 2114 | multiple per month | multiple per month | yes |  |
| 2149 | unknown | unknown | yes |  |
| 2166 | unknown | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per 2 weeks' -> '3 to 5 per 2 week' |
| 2233 | 3 to 4 per month | 6 to 7 per 2 month | yes |  |
| 2245 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2259 | 2 to 3 per month | 6 to 8 per 3 month | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | multiple per week | 7 to 9 per month | no |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5-7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 in 2 months' -> '2 to 3 per 2 month' |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 or 7 per 2 months' -> '5 to 7 per 2 month' |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | final_label_repaired: '6 to 7 per 2 weeks' -> '6 to 7 per 2 week' |
| 2459 | 5 per 5 month | 7 to 9 per 2 week | no | final_label_repaired: 'multiple per week' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 in 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per two weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: 'multiple per week' -> '8 to 9 per 2 week' |
| 2548 | 2 to 3 per month | 5 to 6 per 2 month | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | final_label_repaired: '3 to 4 per 2 months' -> '3 to 4 per 2 month' |
| 2609 | 1 per day | 1 per day | yes |  |
| 2622 | 1 per day | 1 per day | yes |  |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per night' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
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
| 2907 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free since 27 March 2024' -> 'seizure free for multiple year' |
| 2932 | 13 per 2 month | seizure free for 9 month | no | final_label_repaired: 'seizure free for 9 month' -> '13 per 2 month' |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 2965 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 2992 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 3015 | seizure free for 1 year | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last visit' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '1 cluster per month, 6-7 seizures per cluster' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month, each with ~5 absences' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes | final_label_repaired: '3 days per week' -> '3 per week' |
| 3356 | unknown | unknown | yes |  |
| 3371 | 1 per 8 week | unknown | no | final_label_repaired: '1 event in 8 weeks' -> '1 per 8 week' |
| 3436 | unknown | unknown | yes |  |
| 3468 | unknown | unknown | yes | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 3469 | unknown | unknown | yes |  |
| 3482 | unknown | unknown | yes |  |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 | unknown | unknown | yes |  |
| 3528 | unknown | unknown | yes |  |
| 3532 | unknown | unknown | yes |  |
| 3534 | unknown | unknown | yes | evidence_not_exact_substring |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes |  |
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
| 3988 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 3995 | 1 per month | 1 per month | yes | final_label_repaired: 'monthly' -> '1 per month' |
| 3999 | 1 per month | 1 per month | yes | final_label_repaired: 'monthly' -> '1 per month' |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: 'every 1 to 2 days' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day on workdays' -> '1 per 1 to 2 day' |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: 'every two to three weeks' -> '1 per 2 to 3 week' |
| 4258 | 4 per week | 4 per week | yes |  |
| 4337 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: 'approximately 1 per month' -> '3 per 3 month' |
| 4345 | 4 per 1 month | 4 per month | yes | final_label_repaired: '4 per month' -> '4 per 1 month' |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '2 per month' -> '5 per 2 month' |
| 4402 | 14 per 14 month | 7 per 7 month | yes | final_label_repaired: '1 per month' -> '7 per 7 month'; final_label_repaired: '7 per 7 month' -> '14 per 14 month' |
| 4410 | 8 per 14 month | 4 per 7 month | yes | final_label_repaired: '1 per month' -> '4 per 7 month'; final_label_repaired: '4 per 7 month' -> '8 per 14 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: 'approximately 1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 every 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | final_label_repaired: '1 seizure every 3-4 days' -> '1 per 3 to 4 day' |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | final_label_repaired: 'every 14 to 21 days' -> '1 per 14 to 21 day' |
| 4690 | multiple per day | multiple per day | yes | final_label_repaired: '10 per hour' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | final_label_repaired: '9 per hour' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | final_label_repaired: '4 per hour' -> 'multiple per day' |
| 4709 |  | multiple per day | no | schema_validation_error: Field required; evidence_not_exact_substring |
| 4731 | unknown | unknown | yes |  |
| 4732 | unknown | unknown | yes |  |
| 4771 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 in 6 weeks' -> 'no seizure frequency reference' |
| 4839 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | seizure free for 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 4992 | seizure free for multiple year | seizure free for 11 month | yes | final_label_repaired: 'seizure free since 12-Sep-2018' -> 'seizure free for multiple year' |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5092 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5121 | no seizure frequency reference | seizure free for multiple month | no | final_label_repaired: 'no seizures since last review' -> 'no seizure frequency reference' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5141 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year' |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early 2024' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for multiple year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for over 18 months' -> 'seizure free for multiple year' |
| 5379 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for approximately 6 months' -> 'seizure free for 6 month'; evidence_not_exact_substring |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 5476 | 1 per month | unknown | no | final_label_repaired: '1 cluster per month' -> '1 per month' |
| 5490 | unknown | unknown | yes |  |
| 5491 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 5504 | unknown | unknown | yes |  |
| 5507 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 events since June 2025' -> 'no seizure frequency reference' |
| 5528 | 1 per month | 1 per month | yes |  |
| 5534 | 1 per month | 1 per multiple month | no | final_label_repaired: '1 event in the last month' -> '1 per month' |
| 5551 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes |  |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: 'every 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: 'every 8 days' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 5696 | no seizure frequency reference | 3 per 4 month | no | final_label_repaired: '3 in 4 months' -> 'no seizure frequency reference' |
| 5763 | 4 per 3 month | 2 per month | yes | final_label_repaired: '4 per 3 months' -> '4 per 3 month' |
| 5767 | 1 per 1 to 2 week | 1 per 1 to 2 week | yes | final_label_repaired: 'every 1-2 weeks' -> '1 per 1 to 2 week' |
| 5791 | 1 per month | 1 per month | yes |  |
| 5827 | multiple per week | multiple per week | yes |  |
| 5837 | unknown | 2 cluster per 3 week, multiple per cluster | no | final_label_repaired: '2 clusters in 3 weeks' -> 'unknown' |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '4 per 6 weeks' -> '4 per 6 week' |
| 5873 | multiple per week | multiple per week | yes |  |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: 'once every 6-8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: 'once every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 5974 | unknown | unknown | yes |  |
| 5977 | multiple per 6 week | unknown | yes |  |
| 5995 | 3 per 7 month | 1 per 3 months | yes | final_label_repaired: '1 in August 2025' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 7 month' |
| 5996 | unknown | unknown | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 events in 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes |  |
| 6034 | unknown | unknown | yes |  |
| 6065 | 4 per 2 month | 5 per month | no | final_label_repaired: '5 per month' -> '4 per 2 month' |
| 6077 | 1 per 8 month | unknown | no | final_label_repaired: '1 seizure (single breakthrough)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 8 month' |
| 6087 | unknown | unknown | yes |  |
| 6094 | 4 per 2 month | 3 per month | yes | final_label_repaired: '2 to 3 per month' -> '4 per 2 month' |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for over 12 months' -> 'seizure free for multiple year' |
| 6137 | 1 per 2 to 3 week | 1 per 2 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 6153 | multiple per week | 9 per month | no |  |
| 6180 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 6192 | unknown | unknown | yes |  |
| 6204 | 2 per month | 2 per month | yes |  |
| 6209 | multiple per day | multiple per day | yes | final_label_repaired: '1 per day' -> 'multiple per day' |
| 6244 | 2 per week | unknown | no |  |
| 6251 | 1 per 4 month | 1 per 1 to 2 month | yes | final_label_repaired: '1 event since August 2025' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 4 month' |
| 6273 | unknown | unknown | yes |  |
| 6319 | 1 per week | 1 per week | yes |  |
| 6321 | 2 per 2 month | unknown | no | final_label_repaired: '2 events over 2 months' -> '2 per 2 month' |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: '2 events per 6 weeks' -> '2 per 6 week' |
| 6358 | seizure free for 16 month | seizure free for 15 to 16 months | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 6368 | 1 per 1 to 2 week | unknown | no | final_label_repaired: '1 cluster per 1 to 2 weeks' -> '1 per 1 to 2 week' |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes |  |
| 6509 | multiple per week | 1 per week | no |  |
| 6571 | seizure free for 4 month | unknown | no |  |
| 6607 | unknown | unknown | yes |  |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6701 | 4 per 3 week | 4 per 3 week | yes | final_label_repaired: '4 per 3 weeks' -> '4 per 3 week' |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6–8 weeks' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes |  |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes |  |
| 6987 | unknown | unknown | yes |  |
| 7093 | unknown | unknown | yes |  |
| 7126 | unknown | unknown | yes |  |
| 7141 | unknown | unknown | yes | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no | final_label_repaired: '3 clusters in 6 weeks' -> 'unknown' |
| 7168 | unknown | unknown | yes |  |
| 7192 | multiple per week | multiple per week | yes | final_label_repaired: 'several clusters per week' -> 'multiple per week' |
| 7195 | 1 per month | unknown | no | final_label_repaired: 'unknown' -> '1 per month' |
| 7196 | 6 per 6 week | 1 per week | yes | final_label_repaired: '1 per week' -> '6 per 6 week' |
| 7198 | 3 per 2 month | unknown | no | final_label_repaired: '3 episodes in 2 months' -> '3 per 2 month' |
| 7275 | 3 per 2 month | 1 per month | no | final_label_repaired: '2 per month' -> '3 per 2 month' |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | final_label_repaired: '2 clusters in 6 weeks' -> 'unknown' |
| 7409 | 1 per week | unknown | no |  |
| 7455 | unknown | unknown | yes |  |
| 7475 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 7491 | unknown | unknown | yes |  |
| 7506 | unknown | unknown | yes |  |
| 7573 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '2 per month' -> '1 per 2 week' |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | 3 to 6 per month | 3 to 7 per month | yes |  |
| 7650 | unknown | unknown | yes |  |
| 7738 | unknown | seizure free for multiple month | no |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 7818 | seizure free for 2 year | seizure free for 2 years | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7859 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year' |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7961 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8079 | seizure free for 18 month | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 8089 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8144 | unknown | seizure free for multiple month | no |  |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8160 | no seizure frequency reference | seizure free for multiple month | no | final_label_repaired: 'once every few weeks' -> 'no seizure frequency reference' |
| 8180 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8188 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8354 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 12 months' -> 'seizure free for multiple year' |
| 8400 | unknown | seizure free for multiple month | no |  |
| 8419 | 1 to 2 per week | 1 to 2 per week | yes | final_label_repaired: '1-2 per week' -> '1 to 2 per week' |
| 8474 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8577 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since March 2024' -> 'seizure free for multiple year' |
| 8581 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes | evidence_not_exact_substring |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8808 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 8820 | seizure free for multiple year | seizure free for 7 month | yes | final_label_repaired: 'seizure free since 29-12-2023' -> 'seizure free for multiple year' |
| 8835 | seizure free for multiple year | seizure free for 10 month | yes | final_label_repaired: 'seizure free since 12 June 2020' -> 'seizure free for multiple year' |
| 8854 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; evidence_not_exact_substring |
| 8922 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8924 | seizure free for 5 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 5 months' -> 'seizure free for 5 month' |
| 8938 | seizure free for multiple year | seizure free for 10 month | yes | final_label_repaired: 'seizure free since 25 Jun 2015' -> 'seizure free for multiple year' |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9002 | 7 per 10 month | 7 per year | yes | final_label_repaired: '7 seizures in 2024' -> '7 per 10 month' |
| 9063 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free since 19-Mar-2017' -> 'seizure free for multiple year' |
| 9103 | unknown | unknown | yes |  |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9190 | 0 per 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month'; final_label_repaired: 'seizure free for 6 month' -> '0 per 3 month' |
| 9215 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early summer 2025' -> 'seizure free for multiple year' |
| 9238 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9250 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | multiple per day | multiple per day | yes |  |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'once every two days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 8 per 9 month | 4 per 6 month | yes | final_label_repaired: '2 per month' -> '8 per 9 month' |
| 9462 | 14 per 22 month | 7 per 11 month | yes | final_label_repaired: '0-2 per month' -> '7 per 11 month'; final_label_repaired: '7 per 11 month' -> '14 per 22 month' |
| 9496 | 12 per 24 month | 6 per 12 month | yes | final_label_repaired: '1 per month' -> '6 per 12 month'; final_label_repaired: '6 per 12 month' -> '12 per 24 month' |
| 9547 | unknown | unknown | yes |  |
| 9588 | seizure free for 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 9704 | unknown | unknown | yes |  |
| 9815 | multiple per day | multiple per day | yes | final_label_repaired: '9 per hour' -> 'multiple per day' |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes |  |
| 9888 | unknown | unknown | yes |  |
| 9912 | unknown | unknown | yes |  |
| 9937 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'clusters every few weeks' -> 'unknown' |
| 9943 | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: '1 cluster per 4-5 weeks' -> '1 per 4 to 5 week' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: 'weekly clusters' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 clusters per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10147 | unknown | unknown | yes |  |
| 10183 | 2 per 6 week | unknown | no | final_label_repaired: '2 episodes in 6 weeks' -> '2 per 6 week' |
| 10189 | unknown | unknown, 3 to 4 per cluster | yes | final_label_repaired: 'clusters every several weeks with 3-4 events per cluster' -> 'unknown' |
| 10200 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes |  |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no | final_label_repaired: 'approx 4 clusters per month' -> 'unknown' |
| 10245 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10260 | unknown | unknown | yes |  |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | no seizure frequency reference | unknown | yes | final_label_repaired: 'several days per month' -> 'no seizure frequency reference' |
| 10371 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free since 11 Aug 2023' -> 'seizure free for multiple year' |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | final_label_repaired: '5 per week' -> '1 cluster per week, 5 per cluster' |
| 10386 | 2 to 3 per week | 1 cluster per week, 2 to 3 per cluster | yes |  |
| 10434 | multiple cluster per week, 2 to 3 per cluster | multiple cluster per week, 2 to 3 per cluster | yes | final_label_repaired: 'multiple clusters per week, 2-3 events per cluster' -> 'multiple cluster per week, 2 to 3 per cluster' |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes |  |
| 10517 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: '3-4 nights per week with clusters' -> '3 to 4 cluster per week, multiple per cluster' |
| 10542 | 2 to 4 per 3 month | unknown, 2 to 4 per cluster | no | final_label_repaired: 'no seizure frequency reference' -> '2 to 4 per 3 month' |
| 10578 | no seizure frequency reference | unknown, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 per cluster' -> 'no seizure frequency reference' |
| 10583 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes |  |
| 10618 | no seizure frequency reference | unknown, 4 to 6 per cluster | yes | final_label_repaired: '4 to 6 per cluster' -> 'no seizure frequency reference' |
| 10629 | unknown | unknown | yes |  |
| 10630 | multiple per week | multiple cluster per 2 week, 5 per cluster | no |  |
| 10673 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: 'approximately 1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | unknown | unknown | yes |  |
| 10807 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | final_label_repaired: '2 cluster days per month' -> '2 cluster per month, multiple per cluster' |
| 10829 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week, 4 events per cluster' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week (4+ events per cluster)' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2-3 clusters per month, each ~5 focal impaired-awareness seizures' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 10965 | unknown | 2 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown' |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month, each with 4-5 seizures' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '3 clusters per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | final_label_repaired: '1 to 2 clusters per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 4 clusters per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 cluster days per month with 5+ seizures per cluster' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 cluster days per month, 6 seizures per cluster' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '2 cluster days per month, 3-4 seizures per cluster' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | final_label_repaired: '1 cluster per month with 4-6 events per cluster' -> '1 cluster per month, 4 to 6 per cluster' |
| 11216 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free since 25 December 2023' -> 'seizure free for multiple year' |
| 11254 | seizure free for 3 month | unknown | no |  |
| 11259 | unknown | unknown | yes |  |
| 11262 | unknown | unknown | yes |  |
| 11272 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free since 20/Dec' -> 'seizure free for multiple year' |
| 11282 | 1 per 3 month | unknown | no | final_label_repaired: 'seizure free since 05-Aug-2015' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 11337 | no seizure frequency reference | unknown | yes | final_label_repaired: '1 seizure since last review' -> 'no seizure frequency reference' |
| 11350 | multiple per week | unknown | yes |  |
| 11380 | unknown | unknown | yes |  |
| 11389 | 1 per 2 month | unknown | no | final_label_repaired: '1 seizure in 2 months' -> '1 per 2 month' |
| 11400 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11409 | unknown | no seizure frequency reference | yes |  |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11562 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11706 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes |  |
