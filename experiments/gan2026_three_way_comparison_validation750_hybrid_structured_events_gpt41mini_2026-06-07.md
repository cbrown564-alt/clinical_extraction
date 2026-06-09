# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-08

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Rare full-validation reason: Phase 1 three-way architecture comparison (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07): full validation750 run across all six PipelineArchitecture configs, gpt-4.1-mini pass (second resume — deterministic, deterministic_canonical_pipeline, hybrid, and llm_only_direct_labeler already completed cleanly. llm_only_structured_events restarted after fixing a schema_repair.py _ASSERTION_ALIASES bug that remapped the already-valid assertion_status value 'unknown' to the invalid 'unclear', confirmed via re-pilot validation25 with 0 failures and 100% accuracy).
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_llm_only_structured_events_v0.5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-08T02:49:44.499501+00:00`
- Run finished UTC: `2026-06-08T02:49:57.912624+00:00`
- Wall-clock elapsed: `13.413` seconds (`0.224` minutes)
- Throughput: `55.915431` rows/sec (`0.018` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `f9845eb`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_three_way_comparison_validation750_llm_only_structured_events_gpt41mini_2026-06-07.jsonl`

## Summary

- Structured records: 748 / 750
- Call failures: 0
- Parse/schema/label issues: 2
- JSON dialect repairs: 0
- Deterministic repair notes: 526
- Exact selection evidence substrings: 691 / 750
- Purist validation accuracy/micro F1 proxy: 0.8813 (661 / 750)
- Pragmatic validation accuracy/micro F1 proxy: 0.9053 (679 / 750)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: 'up to 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '2 per recent interval' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week' |
| 212 | 2 to 3 per month | 1 per 3 to 4 week | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month'; evidence_not_exact_substring |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes | final_label_repaired: 'many per month' -> 'multiple per month' |
| 409 | 1 per month | 1 per month | yes | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 15 per 3 month | 2 per week | yes | final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per month' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 |  | 1 per week | no | schema_validation_error: Field required; evidence_not_exact_substring |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 | multiple per week | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes | final_label_repaired: 'most weekdays for absences; 1 per 8 weeks for tonic–clonic' -> 'multiple per week' |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per 7 to 10 days' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | unknown | multiple per month | yes | final_label_repaired: 'several per month, sometimes clusters' -> 'unknown' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 to 3 per year' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 2 per week | 5 to 7 per 3 week | yes |  |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 2 to 3 per week | 21 to 28 per 3 month | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | final_label_repaired: '5 to 7 per year' -> '5 to 7 per 10 month' |
| 1317 | multiple per day | unknown, multiple per cluster | yes | final_label_repaired: 'multiple seizures in 1 day' -> 'multiple per day' |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 3 per day | 3 per day | yes |  |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes | final_label_repaired: '1 tonic-clonic and 6 petit mal per week' -> '7 per week' |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | multiple per week | 11 per week | no |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 per 2 weeks' -> '3 per 2 week' |
| 1695 | no seizure frequency reference | multiple per month | yes | final_label_repaired: 'a handful per month' -> 'no seizure frequency reference' |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | final_label_repaired: 'multiple per month' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes | final_label_repaired: 'cluster multiple per week' -> 'multiple per week' |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: 'approximately 11 seizures per 6 months' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '3 to 4 per month' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '8 seizures per 4 months' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 1880 | 7 per 2 month | 8 per 2 month | no | final_label_repaired: '7 per 2 months' -> '7 per 2 month' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 per 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 drop attacks and 5 convulsions per 3 months' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '2 to 5 per 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '6 per 2 months' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '3 per 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'a few per month' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2149 | no seizure frequency reference | unknown | yes | final_label_repaired: 'ongoing focal aware and impaired-awareness seizures' -> 'no seizure frequency reference' |
| 2166 | multiple per day | unknown | yes | final_label_repaired: 'frequent petit mal recently' -> 'multiple per day' |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '2 to 3 per week' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | final_label_repaired: '3 per month' -> '6 to 7 per 2 month' |
| 2245 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2259 | 2 to 3 per month | 6 to 8 per 3 month | yes |  |
| 2354 |  | 6 to 7 per week | no | schema_validation_error: Input should be 'frequency_rate', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency' or 'no_reference'; evidence_not_exact_substring |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes | final_label_repaired: '3 to 4 per month, with clustering' -> '3 to 4 per month' |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | evidence_not_exact_substring |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 2 to 3 per month | 5 to 7 per 2 month | yes |  |
| 2456 | 2 to 3 per week | 6 to 7 per 2 week | yes |  |
| 2459 | 5 per 5 month | 7 to 9 per 2 week | no | final_label_repaired: 'multiple per week' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: '8 to 9 per 2 weeks' -> '8 to 9 per 2 week' |
| 2548 | 2 to 3 per month | 5 to 6 per 2 month | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 2 to 3 per month | 3 to 4 per 2 month | yes |  |
| 2609 | 1 per day | 1 per day | yes |  |
| 2622 | 1 per day | 1 per day | yes |  |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: '1 cluster per night' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes |  |
| 2681 | 1 per day | 1 per day | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every 2 days with occasional clusters' -> '1 per 2 day'; evidence_not_exact_substring |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 every 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 7 per 10 month | 1 per month | no | final_label_repaired: '7 per year' -> '7 per 10 month' |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes |  |
| 2812 | 1 per day | 1 per day | yes |  |
| 2822 | 1 per day | 1 per day | yes | final_label_repaired: '1 per day with occasional clusters' -> '1 per day' |
| 2824 | 1 per day | 1 per day | yes |  |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | 13 per 2 month | seizure free for 9 month | no | final_label_repaired: 'seizure free since 29/09/2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '13 per 2 month' |
| 2938 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free for over 7 months' -> 'seizure free for multiple year' |
| 2965 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 2992 | 1 per 8 month | seizure free for 7 month | no | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month'; final_label_repaired: 'seizure free for 7 month' -> '1 per 8 month' |
| 3015 | 1 per 13 month | seizure free for 12 month | no | final_label_repaired: 'seizure free for 1 year' -> '1 per 13 month' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last visit' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '6 to 7 per month in clusters' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month, each with ~5 absences' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month, each about 4 absences' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month, each ≈5 absences' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes | final_label_repaired: '6 per 30 days' -> '6 per month' |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures only after curtailed sleep (conditional frequency)' -> 'no seizure frequency reference' |
| 3371 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures only with significant sleep deprivation' -> 'no seizure frequency reference' |
| 3436 | unknown | unknown | yes | final_label_repaired: 'cluster shortly after early-morning arousal' -> 'unknown' |
| 3468 | unknown | unknown | yes | final_label_repaired: '1 cluster per perimenstrual period' -> 'unknown' |
| 3469 | unknown | unknown | yes | final_label_repaired: 'perimenstrual cluster only' -> 'unknown' |
| 3482 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures perimenstrual window only' -> 'no seizure frequency reference' |
| 3493 | no seizure frequency reference | unknown | yes | final_label_repaired: 'clustered around menstrual period, roughly 3 days before to 3 days after' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 3507 | no seizure frequency reference | unknown | yes | final_label_repaired: 'reduced frequency by 0.3' -> 'no seizure frequency reference' |
| 3512 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased by ~20%' -> 'no seizure frequency reference' |
| 3528 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased frequency of brief jerks and absences' -> 'no seizure frequency reference' |
| 3532 | no seizure frequency reference | unknown | yes | final_label_repaired: '20% increase over baseline frequency' -> 'no seizure frequency reference' |
| 3534 | seizure free for 7 month | unknown | no | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'multiple per week' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 clusters per week in bad weeks' -> '7 per week' |
| 3681 | 9 per month | 9 per month | yes |  |
| 3682 | 6 per month | 6 per month | yes |  |
| 3710 | 5 per week | 5 per week | yes |  |
| 3753 | 1 per day | 1 per day | yes |  |
| 3766 | 8 per year | 8 per year | yes |  |
| 3774 | 9 per year | 9 per year | yes |  |
| 3791 | 10 per year | 10 per year | yes |  |
| 3801 | 9 per month | 9 per month | yes | evidence_not_exact_substring |
| 3806 | 6 per month | 6 per month | yes |  |
| 3827 | 7 per month | 7 per month | yes |  |
| 3846 | 2 per day | 2 per day | yes |  |
| 3849 | 3 per day | 3 per day | yes |  |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 | 3 per year | 3 per year | yes |  |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 | 4 per week | 4 per week | yes |  |
| 3988 | multiple per week | multiple per week | yes |  |
| 3995 | 1 per month | 1 per month | yes | final_label_repaired: 'about 1 per month' -> '1 per month' |
| 3999 | 1 per month | 1 per month | yes | final_label_repaired: 'about 1 per month' -> '1 per month' |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: 'multiple per week' -> '1 per 1 to 2 day' |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 4258 | 4 per week | 4 per week | yes |  |
| 4337 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '3 events in 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '3 per 3 month' |
| 4345 | 4 per 1 month | 4 per month | yes | final_label_repaired: '4 per month' -> '4 per 1 month' |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: 'approximately 2 per month' -> '5 per 2 month' |
| 4402 | 14 per 14 month | 7 per 7 month | yes | final_label_repaired: '1 per month' -> '7 per 7 month'; final_label_repaired: '7 per 7 month' -> '14 per 14 month' |
| 4410 | 8 per 14 month | 4 per 7 month | yes | final_label_repaired: '1 per month' -> '4 per 7 month'; final_label_repaired: '4 per 7 month' -> '8 per 14 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months with occasional clusters' -> '1 per 2 month'; evidence_not_exact_substring |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | 1 to 2 per week | 1 per 3 to 4 day | yes |  |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | final_label_repaired: '1 per 14 to 21 days' -> '1 per 14 to 21 day' |
| 4690 | multiple per day | multiple per day | yes | final_label_repaired: '10 per hour' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | final_label_repaired: 'approximately 9 per hour' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 4709 | multiple per day | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 4731 | multiple per year | unknown | yes | final_label_repaired: 'rare' -> 'multiple per year' |
| 4732 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased breakthrough events' -> 'no seizure frequency reference' |
| 4771 | multiple per month | unknown | yes |  |
| 4839 | 2025 per 4 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 4+ months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2025 per 4 month' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | 1 per 9 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 6+ months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 9 month'; evidence_not_exact_substring |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 4992 | seizure free for multiple year | seizure free for 11 month | yes | final_label_repaired: 'seizure free since 12-Sep-2018' -> 'seizure free for multiple year' |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 5040 | seizure free for multiple year | seizure free for 6 months | yes | final_label_repaired: 'seizure free since 10 March 2025' -> 'seizure free for multiple year' |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5092 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since initial referral' -> 'seizure free for multiple year' |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5141 | seizure free for 1.5 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for approximately 1.5 months' -> 'seizure free for 1.5 month' |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last consultation' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for multiple year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for over 18 months' -> 'seizure free for multiple year' |
| 5379 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 5476 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5490 | unknown | unknown | yes | evidence_not_exact_substring |
| 5491 | 2 per 6 week | unknown | no | final_label_repaired: 'sporadic jerks this year, 2 episodes in last 6 weeks' -> '2 per 6 week' |
| 5504 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic per year' -> 'no seizure frequency reference' |
| 5507 | multiple per week | unknown | yes |  |
| 5528 | 1 per month | 1 per month | yes |  |
| 5534 | 1 per 2 week | 1 per multiple month | no | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 5551 | multiple per day | multiple per day | yes | final_label_repaired: 'several episodes per day' -> 'multiple per day' |
| 5567 | multiple per week | multiple per week | yes | evidence_not_exact_substring |
| 5584 | multiple per week | multiple per week | yes |  |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per 8 days' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 events per 4 months' -> '3 per 4 month' |
| 5763 | 2 per 3 month | 2 per month | no | final_label_repaired: '2 generalised convulsions and 4 focal impaired-awareness episodes per 3 months' -> '2 per 3 month' |
| 5767 | 2 to 4 per month | 1 per 1 to 2 week | yes |  |
| 5791 | unknown | 1 per month | no | final_label_repaired: '1 generalised tonic–clonic seizure in 3 months' -> 'unknown' |
| 5827 | 2 per 8 week | multiple per week | no | final_label_repaired: '2 per 8 weeks' -> '2 per 8 week' |
| 5837 | 1 per 3 week | 2 cluster per 3 week, multiple per cluster | no | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '4 per 6 weeks' -> '4 per 6 week' |
| 5873 | multiple per week | multiple per week | yes | evidence_not_exact_substring |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 cluster per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2-3 weeks' -> '1 per 2 to 3 week' |
| 5974 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures with missed doses, typically within 24-48 hours' -> 'no seizure frequency reference' |
| 5977 | unknown | unknown | yes | final_label_repaired: 'episodes clustering around inconsistent ASM and alcohol use' -> 'unknown' |
| 5995 | 3 per 6 month | 1 per 3 months | yes | final_label_repaired: 'multiple per year, infrequent, clustered' -> 'multiple per year'; final_label_repaired: 'multiple per year' -> '3 per 6 month'; evidence_not_exact_substring |
| 5996 | no seizure frequency reference | unknown | yes | final_label_repaired: 'recent breakthrough events' -> 'no seizure frequency reference' |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 6029 | multiple per week | unknown | yes |  |
| 6034 | no seizure frequency reference | unknown | yes | final_label_repaired: 'clustered nocturnal warnings during disrupted routine' -> 'no seizure frequency reference' |
| 6065 | multiple per month | 5 per month | no |  |
| 6077 | no seizure frequency reference | unknown | yes | final_label_repaired: '1 breakthrough episode on 12/09/2025' -> 'no seizure frequency reference' |
| 6087 | unknown | unknown | yes |  |
| 6094 | 4 per 2 month | 3 per month | yes | final_label_repaired: '5 events in 6 weeks' -> '5 per 6 week'; final_label_repaired: '5 per 6 week' -> '4 per 2 month' |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent generalised seizures provoked by visual stimuli' -> 'no seizure frequency reference' |
| 6137 | 2 to 3 per month | 1 per 2 week | yes |  |
| 6153 | 9 per 4 week | 9 per month | yes | final_label_repaired: 'multiple per week' -> '9 per 4 week' |
| 6180 | multiple per week | multiple per week | yes |  |
| 6192 | unknown | unknown | yes |  |
| 6204 | 1 per 3 to 4 week | 2 per month | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 6209 | multiple per day | multiple per day | yes | final_label_repaired: '1 per day' -> 'multiple per day' |
| 6244 | unknown | unknown | yes |  |
| 6251 | 1 per 4 month | 1 per 1 to 2 month | yes | final_label_repaired: '1 per several months' -> '1 per multiple month'; final_label_repaired: '1 per multiple month' -> '1 per 4 month' |
| 6273 | no seizure frequency reference | unknown | yes | final_label_repaired: 'variable frequency over recent months' -> 'no seizure frequency reference' |
| 6319 | 1 per week | 1 per week | yes |  |
| 6321 | 2 per 3 month | unknown | no | final_label_repaired: '2 events in 3 months' -> '2 per 3 month' |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 6358 | 2 per 2 month | seizure free for 15 to 16 months | no | final_label_repaired: 'seizure free since June 2024' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 2 month' |
| 6368 | 3 per 6 week | unknown | no | final_label_repaired: '3 per 6 weeks' -> '3 per 6 week' |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes | final_label_repaired: 'clusters lasting 2-3 days every few weeks' -> 'unknown' |
| 6509 | no seizure frequency reference | 1 per week | no | final_label_repaired: '2 per fortnight' -> 'no seizure frequency reference' |
| 6571 | 1 per 4 month | unknown | no | final_label_repaired: 'seizure free since mid-June 2025' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month'; evidence_not_exact_substring |
| 6607 | no seizure frequency reference | unknown | yes | final_label_repaired: 'worsening recurrent seizures' -> 'no seizure frequency reference' |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6701 | 4 per 3 week | 4 per 3 week | yes | final_label_repaired: '4 per 3 weeks' -> '4 per 3 week' |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '2 per 3 months' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes |  |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes |  |
| 6987 | 10 to 15 per 1 year | unknown | no | final_label_repaired: 'unknown' -> '10 to 15 per 1 year' |
| 7093 | unknown | unknown | yes | final_label_repaired: 'cluster frequency around menstrual cycle phases' -> 'unknown' |
| 7126 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased seizures 10-14 days per month, infrequent outside' -> 'no seizure frequency reference' |
| 7141 | multiple per month | unknown | yes |  |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no | final_label_repaired: '3 clusters per 6 weeks' -> 'unknown' |
| 7168 | unknown | unknown | yes | final_label_repaired: 'catamenial seizure clusters premenstrually' -> 'unknown' |
| 7192 | multiple per week | multiple per week | yes |  |
| 7195 | 1 per month | unknown | no |  |
| 7196 | multiple per week | 1 per week | no |  |
| 7198 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased seizure frequency postpartum' -> 'no seizure frequency reference' |
| 7275 | 3 per 12 week | 1 per month | yes | final_label_repaired: '3 events per 12 weeks' -> '3 per 12 week' |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | final_label_repaired: '2 clusters per 6 weeks' -> 'unknown' |
| 7409 | multiple per week | unknown | yes |  |
| 7455 | multiple per day | unknown | yes | final_label_repaired: 'cluster several per month' -> 'multiple per day' |
| 7475 | 2 per 4 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 2 month'; final_label_repaired: '2 per 2 month' -> '2 per 4 month' |
| 7491 | unknown | unknown | yes | final_label_repaired: 'unknown frequency with clustering' -> 'unknown' |
| 7506 | unknown | unknown | yes |  |
| 7573 | unknown | 1 per 2 week | no | final_label_repaired: '1 per 2 weeks with occasional clusters' -> 'unknown' |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | 2 per 10 month | 3 to 7 per month | no | final_label_repaired: '2 per year' -> '2 per 10 month' |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 7818 | seizure free for multiple year | seizure free for 2 years | yes | final_label_repaired: 'seizure free since August 2023' -> 'seizure free for multiple year' |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 7859 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sparse events, no convulsive seizures for several weeks' -> 'no seizure frequency reference' |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last clinic contact' -> 'seizure free for multiple year' |
| 7961 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8079 | seizure free for multiple year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 8089 | seizure free for 4 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8144 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8160 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since 11th June 2025' -> 'seizure free for multiple year' |
| 8180 | 1 per 6 month | seizure free for multiple month | no | final_label_repaired: 'seizure free since last review in April' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 6 month' |
| 8188 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last clinic assessment' -> 'seizure free for multiple year' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free during current follow-up period' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8354 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 12+ months' -> 'seizure free for multiple year' |
| 8400 | multiple per month | seizure free for multiple month | no | final_label_repaired: 'occasional brief warning episodes, no convulsions' -> 'multiple per month' |
| 8419 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 8474 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8577 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 18 months' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8581 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since June 2025' -> 'seizure free for multiple year' |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8730 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free since 10 March 2025' -> 'seizure free for multiple year' |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month'; evidence_not_exact_substring |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8808 | 0 per 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> '0 per 10 month'; evidence_not_exact_substring |
| 8820 | seizure free for multiple year | seizure free for 7 month | yes | final_label_repaired: 'seizure free since 29-12-2023' -> 'seizure free for multiple year' |
| 8835 | seizure free for multiple year | seizure free for 10 month | yes | final_label_repaired: 'seizure free for over 10 months' -> 'seizure free for multiple year' |
| 8854 | seizure free for 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; evidence_not_exact_substring |
| 8922 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 8924 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since May 2025' -> 'seizure free for multiple year' |
| 8938 | seizure free for 11 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 8949 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free since 20-Jun-2021' -> 'seizure free for multiple year' |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9002 | 7 per 10 month | 7 per year | yes | final_label_repaired: '7 per year' -> '7 per 10 month' |
| 9063 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free for over 8 months' -> 'seizure free for multiple year' |
| 9103 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent over the past year' -> 'no seizure frequency reference' |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9190 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 9215 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early summer' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9238 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last assessment earlier this year' -> 'seizure free for multiple year' |
| 9250 | unknown | seizure free for multiple month | no | final_label_repaired: 'occasional brief clusters during sleep deprivation' -> 'unknown'; evidence_not_exact_substring |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | unknown | multiple per day | yes | final_label_repaired: 'multiple focal myoclonic seizures per day in clusters' -> 'unknown' |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 8 per 9 month | 4 per 6 month | yes | final_label_repaired: '2 per month' -> '4 per 6 month'; final_label_repaired: '4 per 6 month' -> '8 per 9 month' |
| 9462 | 14 per 22 month | 7 per 11 month | yes | final_label_repaired: '2 per month' -> '7 per 11 month'; final_label_repaired: '7 per 11 month' -> '14 per 22 month' |
| 9496 | 12 per 17 month | 6 per 12 month | yes | final_label_repaired: '2 per month' -> '6 per 12 month'; final_label_repaired: '6 per 12 month' -> '12 per 17 month' |
| 9547 | multiple per week | unknown | yes | evidence_not_exact_substring |
| 9588 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since February 2025' -> 'seizure free for multiple year' |
| 9704 | multiple per day | unknown | yes |  |
| 9815 | multiple per day | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 9877 | unknown | unknown | yes | final_label_repaired: 'unknown frequency focal cognitive seizures' -> 'unknown' |
| 9879 | unknown | unknown | yes | final_label_repaired: 'brief clusters over past 3 months' -> 'unknown' |
| 9888 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9912 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9937 | multiple per month | 1 cluster per month, multiple per cluster | no |  |
| 9943 | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: 'clusters every 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 clusters per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | 3 per month | 3 cluster per month, multiple per cluster | no |  |
| 10147 | unknown | unknown | yes |  |
| 10183 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 10189 | no seizure frequency reference | unknown, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 per cluster sporadically' -> 'no seizure frequency reference' |
| 10200 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster sporadically' -> 'no seizure frequency reference' |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no |  |
| 10245 | 2 per 6 month | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 6 month' |
| 10260 | unknown | unknown | yes | evidence_not_exact_substring |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes |  |
| 10371 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free since 11 Aug 2023' -> 'seizure free for multiple year' |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | final_label_repaired: '1 cluster per week, 5 seizures per cluster' -> '1 cluster per week, 5 per cluster' |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | final_label_repaired: 'weekly, 2 to 3 per cluster' -> '1 cluster per week, 2 to 3 per cluster' |
| 10434 | multiple per week | multiple cluster per week, 2 to 3 per cluster | no |  |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes | final_label_repaired: 'clusters per week' -> 'unknown' |
| 10517 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: '3 to 4 nights per week with clusters' -> '3 to 4 cluster per week, multiple per cluster' |
| 10542 | unknown | unknown, 2 to 4 per cluster | yes | final_label_repaired: 'cluster of 2 to 4 absences per hour on cluster days' -> 'unknown' |
| 10578 | unknown, 3 to 4 per cluster | unknown, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 seizures per cluster, frequency interval unknown' -> 'unknown, 3 to 4 per cluster' |
| 10583 | multiple per week | unknown, 2 to 3 per cluster | yes | evidence_not_exact_substring |
| 10594 | unknown | unknown, 2 per cluster | yes | evidence_not_exact_substring |
| 10618 | no seizure frequency reference | unknown, 4 to 6 per cluster | yes | final_label_repaired: '4 to 6 per cluster' -> 'no seizure frequency reference' |
| 10629 | unknown | unknown | yes |  |
| 10630 | unknown | multiple cluster per 2 week, 5 per cluster | no | final_label_repaired: 'multiple clusters per fortnight' -> 'unknown' |
| 10673 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'multiple per month in clusters' -> 'unknown' |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | multiple per week | unknown | yes | final_label_repaired: 'multiple per week during travel flare-ups' -> 'multiple per week' |
| 10807 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | final_label_repaired: '2 cluster days per month' -> '2 cluster per month, multiple per cluster' |
| 10829 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 3 clusters per month, each cluster ~5 seizures' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month, each ~5 seizures over 24-36 hours' -> '2 cluster per month, 5 per cluster' |
| 10965 | unknown | 2 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '2 clusters per month, each with 4-5 events' -> 'unknown' |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month, each with 4-5 events' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '3 clusters per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | final_label_repaired: '1 to 2 clusters per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 4 clusters per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 cluster days per month, 5+ seizures per cluster day' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 cluster days per month, typically 6 seizures per cluster day' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '2 cluster days per month, 3 to 4 seizures per cluster' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | final_label_repaired: '1 cluster per month, 4 to 6 events per cluster' -> '1 cluster per month, 4 to 6 per cluster' |
| 11216 | seizure free for 4 month | unknown | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 11254 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free since 31-May 2021' -> 'seizure free for multiple year' |
| 11259 | unknown | unknown | yes |  |
| 11262 | multiple per week | unknown | yes |  |
| 11272 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free since 20/Dec' -> 'seizure free for multiple year' |
| 11282 | 1 per 4 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 4 month' |
| 11337 | no seizure frequency reference | unknown | yes | final_label_repaired: '1 seizure on 06-Nov' -> 'no seizure frequency reference' |
| 11350 | multiple per week | unknown | yes | evidence_not_exact_substring |
| 11380 | multiple per day | unknown | yes | final_label_repaired: 'several per two weeks' -> 'multiple per day' |
| 11389 | no seizure frequency reference | unknown | yes | final_label_repaired: '1 event since 21 December' -> 'no seizure frequency reference' |
| 11400 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11409 | unknown | no seizure frequency reference | yes | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11737 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11824 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 12036 | multiple per day | multiple per day | yes |  |
| 12041 | multiple per day | multiple per day | yes |  |
| 12046 | multiple per day | multiple per day | yes |  |
| 12051 | multiple per day | multiple per day | yes |  |
| 12111 | multiple per week | multiple per week | yes |  |
| 12127 | multiple per week | multiple per week | yes |  |
| 12130 | multiple per week | multiple per week | yes |  |
| 12139 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12145 | multiple per week | multiple per week | yes |  |
| 12192 | 1 per day | 1 per day | yes |  |
| 12218 | 1 per day | 1 per day | yes |  |
| 12236 | multiple per day | 1 per day | no |  |
| 12246 | unknown | 1 to 2 per day | no | final_label_repaired: '1 to 2 per day epileptic spasms, occasional tonic-clonic, morning myoclonic clusters' -> 'unknown' |
| 12314 | 3 per week | 3 per week | yes |  |
| 12366 | unknown | 4 per day | no | final_label_repaired: '4 per day simple partial, clusters of drop attacks, 2 per month tonic-clonic' -> 'unknown' |
| 12378 | 4 per day | 4 per day | yes |  |
| 12383 | unknown | 4 per day | no | final_label_repaired: '4 per day (focal onset), clusters (drop attacks), 2 per month (tonic-clonic)' -> 'unknown' |
| 12403 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 12412 | unknown | 2 per day | no | final_label_repaired: '2 per day focal impaired awareness, clusters of drop attacks, 2 per month tonic-clonic' -> 'unknown' |
| 12422 | 1 per day | 1 per day | yes | final_label_repaired: '1 per day (generalised convulsions), 4 per year (tonic seizures)' -> '1 per day' |
| 12438 | 1 per day | 1 per day | yes |  |
| 12456 | 1 per day | 1 per day | yes |  |
| 12460 | 1 per day | 1 per day | yes |  |
| 12468 | 1 per day | 1 per day | yes |  |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12502 | 4 per day | 4 per day | yes |  |
| 12506 | 4 per day | 4 per day | yes |  |
| 12537 | multiple per week | 1 per day | no |  |
| 12548 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12556 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12562 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12573 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12584 | multiple per week | 1 per week | no |  |
| 12641 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day'; evidence_not_exact_substring |
| 12665 | 1 to 2 per month | 1 per day | no |  |
| 12667 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12676 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12679 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | 4 per day | 4 per day | yes |  |
| 12788 | 6 per 4 month | 6 per 4 month | yes | final_label_repaired: '6 per year' -> '6 per 4 month' |
| 12810 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 per year' -> '5 per 2 month' |
| 12823 | 9 per month | 9 per month | yes | final_label_repaired: '9 per year' -> '9 per month' |
| 12827 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12835 | 4 per month | 4 per month | yes | final_label_repaired: '4 per year' -> '4 per month' |
| 12877 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12882 | 7 per 4 month | 7 per 4 month | yes | final_label_repaired: '7 per year' -> '7 per 4 month' |
| 12901 | 8 per 5 month | 8 per 5 month | yes | final_label_repaired: '8 per year' -> '8 per 5 month' |
| 12949 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '9 per year' -> '9 per 6 month' |
| 12950 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per year' -> '7 per 3 month' |
| 12963 | no seizure frequency reference | unknown | yes | final_label_repaired: 'small handful per year' -> 'no seizure frequency reference' |
| 12979 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per year' -> '3 per 4 month' |
| 13008 | 4 per month | 4 per month | yes | final_label_repaired: '4 per year' -> '4 per month' |
| 13011 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per year' -> '3 per 4 month' |
| 13051 | 1 per 8 month | 2 per 8 month | no | final_label_repaired: '1 generalised tonic-clonic seizure 3 weeks ago with recent cluster of absences' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 8 month' |
| 13058 | 1 per 7 month | 2 per 7 month | no | final_label_repaired: '1 generalised tonic-clonic seizure 3 weeks ago with preceding cluster of absences' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 7 month' |
| 13114 | unknown | 1 per year | no | final_label_repaired: '1 tonic seizure 2 weeks ago with recent myoclonic jerks' -> 'unknown'; evidence_not_exact_substring |
| 13122 | 3 per 1 year | 3 per year | yes | final_label_repaired: '3 seizures in one cluster two weeks ago' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year' |
| 13149 | 3 per 1 year | 3 per year | yes | final_label_repaired: '3 tonic seizures 2 weeks ago' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year' |
| 13178 | 1 per 2 week | 1 per 6 month | no | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 13190 | 1 per 5 month | 1 per 5 month | yes | final_label_repaired: '1 event 3 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 5 month' |
| 13209 | 1 per 4 to 5 week | 1 per 8 month | no | final_label_repaired: '1 focal impaired-awareness seizure 2 weeks ago plus clusters every 4-5 weeks' -> '1 per 4 to 5 week'; evidence_not_exact_substring |
| 13267 | no seizure frequency reference | 2 per 5 month | no | final_label_repaired: '1 drop attack 3 weeks ago' -> 'no seizure frequency reference' |
| 13290 | 2 per 2 week | 4 per 6 month | no | final_label_repaired: '2 seizures per 2 weeks' -> '2 per 2 week' |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13349 | seizure free for 12 month | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 12 months or more' -> 'seizure free for 12 month' |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13450 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over one year' -> 'seizure free for multiple year' |
| 13471 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13478 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over one year' -> 'seizure free for multiple year' |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13627 | 20 per 3 month | 64 per 12 month | yes | final_label_repaired: 'multiple per month' -> '64 per 12 month'; final_label_repaired: '64 per 12 month' -> '20 per 3 month' |
| 13635 | 30 per 5 month | 47 per 7 month | yes | final_label_repaired: 'multiple per month' -> '47 per 7 month'; final_label_repaired: '47 per 7 month' -> '30 per 5 month' |
| 13711 | 28 per 6 month | 76 per 12 month | yes | final_label_repaired: 'multiple per month' -> '76 per 12 month'; final_label_repaired: '76 per 12 month' -> '28 per 6 month' |
| 13721 | 26 per 6 month | 77 per 12 month | yes | final_label_repaired: 'multiple per week' -> '77 per 12 month'; final_label_repaired: '77 per 12 month' -> '26 per 6 month' |
| 13732 | 16 per 3 month | 52 per 8 month | yes | final_label_repaired: 'multiple per month' -> '52 per 8 month'; final_label_repaired: '52 per 8 month' -> '16 per 3 month' |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'less intrusive day-to-day' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13893 | 2 per year | 2 per year | yes |  |
| 13922 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 seizures since medication increase' -> 'no seizure frequency reference' |
| 14002 | multiple per day | unknown | yes | final_label_repaired: 'several per recent period' -> 'multiple per day' |
| 14025 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 14029 | multiple per month | unknown | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 14040 | unknown | unknown | yes |  |
| 14076 | unknown | unknown | yes | final_label_repaired: 'increased frequency, unknown exact count' -> 'unknown'; evidence_not_exact_substring |
| 14092 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 myoclonic jerks since last appointment' -> 'no seizure frequency reference' |
| 14096 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 jerks since last appointment' -> 'no seizure frequency reference' |
| 14137 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 to 4 seizures since 3 months ago' -> 'no seizure frequency reference' |
| 14146 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since starting Clobazam' -> 'no seizure frequency reference' |
| 14187 | 2 to 3 per 1 month | 2 to 3 per month | yes | final_label_repaired: 'seizure free since mid July 2019' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 to 3 per 1 month' |
| 14214 | seizure free for multiple year | 2 to 4 per month | no | final_label_repaired: 'seizure free since early December' -> 'seizure free for multiple year' |
| 14250 | 2 per 1 month | 2 per month | yes | final_label_repaired: '2 per week' -> '2 per 1 month' |
| 14282 | 10 per 6 week | multiple per month | no | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '10 per 6 week' |
| 14284 | 2 to 3 per 1 month | 2 to 3 per month | yes | final_label_repaired: 'seizure free since week after 21-Feb' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 to 3 per 1 month' |
| 14317 | 4 per 2 month | 4 per 2 month | yes | final_label_repaired: 'seizure free since early April' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '4 per 2 month'; evidence_not_exact_substring |
| 14332 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: 'seizure free since early October' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '5 per 2 month' |
| 14335 | 3 to 4 per 8 week | 3 to 4 per 2 month | yes | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 8 week' |
| 14383 | 3 to 4 per 3 month | 3 to 4 per 3 month | yes | final_label_repaired: 'seizure free since mid-January' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 3 month'; evidence_not_exact_substring |
| 14454 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'seizure free since mid February 2014' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 2 month' |
| 14524 | unknown | 2 per 6 month | no | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 14530 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'seizure free for 1 month' -> '2 per 2 month'; evidence_not_exact_substring |
| 14540 | 2 per 8 month | 2 per 8 month | yes | final_label_repaired: 'seizure free since early 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 8 month' |
| 14562 | 3 per 6 month | 3 per 6 month | yes | final_label_repaired: 'seizure free for 1 month' -> '3 per 6 month' |
| 14567 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '3 per 3 month' |
| 14581 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: 'seizure free since late October 2014' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14587 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 14592 | 3 per 5 month | 3 per 5 month | yes | final_label_repaired: '3 seizures in 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '3 per 5 month' |
| 14611 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: 'seizure free for 1 month' -> '2 per 4 month' |
| 14628 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: '2 seizures in 3 months' -> '2 per 3 month'; final_label_repaired: '2 per 3 month' -> '2 per 2 month' |
| 14635 | 1 per 5 month | 5 per 4 month | no | final_label_repaired: 'seizure free since end of November 2016' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 5 month' |
| 14645 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'seizure free for 1 month' -> '2 per 6 month' |
| 14662 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '2 to 3 per month' -> '3 per 4 month' |
| 14672 | 3 per 8 month | 3 per 8 month | yes | final_label_repaired: 'seizure free since starting current regimen' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 8 month' |
| 14706 | 2 per 5 month | 2 per 5 month | yes | final_label_repaired: '2 per 5 months' -> '2 per 5 month' |
| 14765 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14806 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14810 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for over 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14821 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3+ weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14872 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14943 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free since 21 Feb' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14949 | 1 per month | 1 per month | yes |  |
| 14965 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free since 20 May' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14973 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free since early February 2023' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month'; evidence_not_exact_substring |
| 15004 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for past months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 15012 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for past months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15021 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for past months' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 15094 | 3 per 13 month | 4 per 13 month | yes | final_label_repaired: '3 jerks since Apr 2022' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 13 month' |
| 15108 | 2 to 3 per 15 month | 3 to 4 per 15 month | no | final_label_repaired: '2 to 3 per month' -> '2 to 3 per 15 month' |
| 15127 | 4 per 13 month | 5 per 13 month | yes | final_label_repaired: '4 jerks since 2-2020' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 13 month' |
| 15129 | 4 per 15 month | 4 per 15 month | yes | final_label_repaired: '4 jerks since 3/2015' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 15 month' |
| 15141 | 3 to 4 per 15 month | 4 to 5 per 15 month | yes | final_label_repaired: '3 to 4 per current period' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 to 4 per 15 month' |
| 15168 | multiple per month | multiple per 15 month | yes | final_label_repaired: 'occasional myoclonic jerks' -> 'multiple per month'; evidence_not_exact_substring |
| 15193 | no seizure frequency reference | multiple per 13 month | yes | final_label_repaired: 'intermittent brief absences' -> 'no seizure frequency reference' |
| 15242 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15262 | multiple per week | multiple cluster per 13 month, multiple per cluster | no |  |
| 15267 | 3 per 14 month | 3 per 14 month | yes | final_label_repaired: '3 jerks per year' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 14 month' |
| 15306 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | final_label_repaired: '2 to 3 per day (situational)' -> '2 to 3 per day'; final_label_repaired: '2 to 3 per day' -> '2 to 3 per 15 month' |
| 15317 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | final_label_repaired: '2 to 3 per unspecified recent period' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 to 3 per 15 month' |
| 15376 | 1 cluster per 2 week, 4 to 6 per cluster | 1 cluster per 2 week, 4 to 6 per cluster | yes | final_label_repaired: '4 to 6 per day' -> '1 cluster per 2 week, 4 to 6 per cluster' |
| 15404 | 3 to 4 per 4 month | 1 cluster per 4 month, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per day' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 4 month' |
| 15429 | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | yes | final_label_repaired: '1 cluster per day' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15431 | 5 per 4 month | 1 cluster per 4 month, 5 per cluster | yes | final_label_repaired: '1 cluster of 5 seizures per 4 months' -> 'unknown'; final_label_repaired: 'unknown' -> '5 per 4 month' |
| 15442 | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | final_label_repaired: 'multiple per day on cluster days' -> '1 cluster per 4 day, 2 per cluster' |
| 15470 | multiple per day | 1 cluster per 5 day, multiple per cluster | no |  |
| 15479 | 1 cluster per 4 to 5 day, 2 per cluster | 1 cluster per 4 to 5 day, 2 per cluster | yes | final_label_repaired: 'multiple per day' -> '1 cluster per 4 to 5 day, 2 per cluster' |
| 15497 | 1 cluster per 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | yes | final_label_repaired: 'multiple per day' -> '1 cluster per 5 day, 5 per cluster' |
| 15503 | 1 cluster per 5 day, 3 to 4 per cluster | 1 cluster per 5 day, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 per day (in clusters)' -> '1 cluster per 5 day, 3 to 4 per cluster' |
| 15513 | 1 cluster per 5 day, 2 to 3 per cluster | 1 cluster per 4 to 5 day, 2 to 3 per cluster | yes | final_label_repaired: '2 to 3 per day in clusters, with seizure-free intervals of 4 to 5 days' -> '1 cluster per 5 day, 2 to 3 per cluster' |
| 15519 | 1 cluster per 4 day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | yes | final_label_repaired: '3 per day in clusters' -> '1 cluster per 4 day, 3 per cluster' |
| 15529 | 1 cluster per 3 day, 4 per cluster | 1 cluster per 3 day, 4 per cluster | yes | final_label_repaired: '1 cluster per day' -> '1 cluster per 3 day, 4 per cluster' |
| 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15614 | 3 per week | 3 per week | yes |  |
| 15628 | multiple per week | multiple per week | yes |  |
| 15639 | 2 per week | 2 per week | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 15672 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 15697 | 1 per day | 1 per day | yes | final_label_repaired: '1 cluster per day' -> '1 per day' |
| 15715 | 1 per day | 1 per day | yes | final_label_repaired: '1 cluster per day' -> '1 per day' |
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
| 15965 | 19 per 3 month | 13 per 2 month | yes | final_label_repaired: 'multiple per month' -> '13 per 2 month'; final_label_repaired: '13 per 2 month' -> '19 per 3 month' |
| 15966 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '3 per month' -> '5 per 3 month' |
| 15982 | 9 per 2 month | 9 per 2 month | yes | final_label_repaired: 'multiple per month' -> '9 per 2 month' |
| 15986 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: 'unknown' -> '11 per 3 month' |
| 15992 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '3 per month' -> '7 per 2 month' |
| 15997 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: 'multiple per month with clustering' -> 'unknown'; final_label_repaired: 'unknown' -> '10 per 3 month'; evidence_not_exact_substring |
| 16021 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '5 per month' -> '9 per 3 month' |
| 16041 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '4 per month' -> '9 per 3 month' |
| 16084 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: 'seizure free for 1 month' -> '8 per 4 month' |
| 16091 | 2 per 2 month | 3 per 3 month | yes | final_label_repaired: '2 per month' -> '3 per 3 month'; final_label_repaired: '3 per 3 month' -> '2 per 2 month' |
| 16097 | 16 per 3 month | 17 per 4 month | yes | final_label_repaired: 'multiple per month' -> '17 per 4 month'; final_label_repaired: '17 per 4 month' -> '16 per 3 month' |
| 16107 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '4 per month' -> '8 per 3 month' |
| 16108 | 12 per 4 month | 12 per 4 month | yes | final_label_repaired: 'multiple per month' -> '12 per 4 month' |
| 16132 | 13 per 2 month | 15 per 3 month | yes | final_label_repaired: 'multiple per month' -> '13 per 2 month' |
| 16133 | 18 per 4 month | 18 per 4 month | yes | final_label_repaired: '6 per month' -> '18 per 4 month' |
| 16161 | 18 per 3 month | 18 per 3 month | yes | final_label_repaired: '7 per month' -> '18 per 3 month' |
| 16162 | 11 per 2 month | 11 per 3 month | no | final_label_repaired: '6 per month' -> '11 per 3 month'; final_label_repaired: '11 per 3 month' -> '11 per 2 month' |
| 16181 | 15 per 4 month | 15 per 4 month | yes | final_label_repaired: '4 per month' -> '15 per 4 month' |
| 16195 | 16 per 4 month | 16 per 4 month | yes | final_label_repaired: '6 per month' -> '16 per 4 month' |
| 16203 | 8 per 2 month | 9 per 3 month | no | final_label_repaired: '1 per month (September)' -> '8 per 2 month' |
| 16204 | 4 per 2 month | 5 per 3 month | yes | final_label_repaired: '1 per month' -> '5 per 3 month'; final_label_repaired: '5 per 3 month' -> '4 per 2 month' |
| 16220 | 11 per 4 month | 11 per 4 month | yes | final_label_repaired: 'seizure free for this month so far' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '11 per 4 month' |
| 16324 | 7 per 2 month | 10 per 3 month | yes | final_label_repaired: 'approximately 1 to 4 per month' -> '7 per 2 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: 'multiple per month' -> '7 per 3 month' |
| 16356 | 3 per 2 month | 1 per 4 day | no | final_label_repaired: '1 cluster every 4 days' -> '1 per 4 day'; final_label_repaired: '1 per 4 day' -> '3 per 2 month' |
| 16394 | 3 per 2 month | 1 per 2 to 4 day | no | final_label_repaired: '1 cluster every 2 to 4 days' -> '1 per 2 to 4 day'; final_label_repaired: '1 per 2 to 4 day' -> '3 per 2 month' |
| 16408 | 1 per 3 day | 1 per 3 day | yes | final_label_repaired: '1 per day' -> '1 per 3 day' |
| 16429 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 per day' -> '1 per 2 to 3 day' |
| 16432 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'daily' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 day' |
| 16450 | 1 per multiple day | 1 per multiple day | yes | final_label_repaired: '1 per day' -> '1 per multiple day' |
| 16529 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster per 5 days' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 cluster every 2 to 3 days' -> '1 per 2 to 3 day' |
| 16574 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster every 4 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 day' |
| 16590 | 1 per 4 to 5 day | 1 per 4 to 5 day | yes | final_label_repaired: '1 cluster every 4 to 5 days, with brief periods of daily seizures' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 to 5 day' |
| 16618 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 per day' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '1 per 5 day' |
| 16645 | 5 per 7 month | 5 per 7 month | yes | final_label_repaired: '1 per month' -> '5 per 7 month' |
| 16674 | 6 per 4 month | 7 per 6 month | yes | final_label_repaired: 'reduced frequency, fewer events' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '6 per 4 month' |
| 16685 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: 'multiple per month' -> '9 per 2 month'; final_label_repaired: '9 per 2 month' -> '10 per 3 month'; evidence_not_exact_substring |
| 16697 | 3 per 4 month | 3 per 6 month | yes | final_label_repaired: '3 seizures in 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '3 per 4 month' |
| 16704 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '7 per month' -> '9 per 6 month' |
| 16714 | 5 per 6 month | 5 per 6 month | yes | final_label_repaired: 'multiple seizures over past 6 months' -> 'multiple per 6 month'; final_label_repaired: 'multiple per 6 month' -> '5 per 6 month' |
| 16717 | 5 per 6 month | 5 per 6 month | yes | final_label_repaired: '1 per 6 months' -> '1 per 6 month'; final_label_repaired: '1 per 6 month' -> '5 per 6 month' |
| 16719 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '1 per week' -> '7 per 6 month' |
| 16728 | 4 per 4 month | 4 per 6 month | no | final_label_repaired: 'variable pattern over last several months' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 4 month'; evidence_not_exact_substring |
| 16750 | 6 per 7 month | 6 per 7 month | yes | final_label_repaired: 'seizure free since late August' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '6 per 7 month' |
| 16757 | 13 per 6 month | 13 per 6 month | yes | final_label_repaired: 'residual breakthrough episodes' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '13 per 6 month' |
| 16758 | 9 per 5 month | 9 per 5 month | yes | final_label_repaired: '5 per month' -> '9 per 5 month' |
| 16772 | 9 per 5 month | 9 per 5 month | yes | final_label_repaired: '1 per month' -> '9 per 5 month' |
| 16774 | 19 per 7 month | 19 per 7 month | yes | final_label_repaired: '3 per month' -> '19 per 7 month' |
| 16780 | 3 per 7 month | 3 per 7 month | yes | final_label_repaired: 'single events in last 6 months' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 7 month' |
| 16824 | 11 per 3 month | 11 per 5 month | yes | final_label_repaired: '1 per month' -> '11 per 3 month' |
| 16833 | 8 per 6 month | 8 per 6 month | yes | final_label_repaired: '5 per month' -> '8 per 6 month' |
| 16839 | 19 per 2 month | 9 per 4 month | no | final_label_repaired: 'multiple per month' -> '14 per 2 month'; final_label_repaired: '14 per 2 month' -> '19 per 2 month'; evidence_not_exact_substring |
| 16867 | 6 per 4 month | 6 per 7 month | no | final_label_repaired: 'multiple per month' -> '6 per 4 month' |
| 16907 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: 'multiple seizures per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '9 per 6 month' |
| 16938 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 per 2 months' -> '1 per 2 month' |
| 16947 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 16961 | 1 per 3 month | 2 per week | no | final_label_repaired: '3 per 3 months' -> '1 per 3 month' |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes |  |
| 17001 | 5 per week | 5 per week | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 17110 | unknown | 4 to 5 cluster per week, multiple per cluster | no | final_label_repaired: 'clusters 4 to 5 days per week' -> 'unknown' |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | final_label_repaired: 'clusters on five days per month' -> '1 cluster per month, multiple per cluster' |
| 17146 | multiple per week | 1 per day | no |  |
| 17167 | 1 per 6 month | 1 per week | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17189 | 1 per 6 month | 1 per month | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17200 | 1 per 6 month | 1 per month | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17201 | 4 per month | 4 per month | yes | final_label_repaired: 'multiple per week' -> '4 per month'; evidence_not_exact_substring |
| 17273 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | final_label_repaired: '1 per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 per day' -> '1 per 1 to 2 day' |
