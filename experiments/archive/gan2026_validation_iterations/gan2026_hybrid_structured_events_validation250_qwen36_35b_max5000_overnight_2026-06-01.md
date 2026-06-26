# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `False`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `a11bedc`
- Working tree note: `clean`
- JSONL artifact: `experiments/gan2026_hybrid_structured_events_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`

## Summary

- Structured records: 167 / 250
- Call failures: 0
- Parse/schema/label issues: 83
- Deterministic repair notes: 105
- Exact selection evidence substrings: 151 / 250
- Purist validation accuracy/micro F1 proxy: 0.6080 (152 / 250)
- Pragmatic validation accuracy/micro F1 proxy: 0.6200 (155 / 250)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 |  | 4 per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | yes | final_label_repaired: '≤ 2 to 4 per year' -> '2 to 4 per year' |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day'; evidence_not_exact_substring |
| 180 |  | 1 per 7 day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per day' -> '1 per 2 day' |
| 187 |  | 1 per 7 to 9 day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 190 |  | 1 per 4 week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 198 |  | 1 per 4 week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 212 | 1 to 2 per month | 1 per 3 to 4 week | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 |  | multiple per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | no seizure frequency reference | multiple per month | yes | final_label_repaired: 'many per month' -> 'no seizure frequency reference' |
| 409 | 1 per month | 1 per month | yes | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 15 per 3 month | 2 per week | yes | final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 |  | 9 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 659 |  | 2 per 4 day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 665 |  | 2 per 2 week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 |  | multiple per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 744 |  | multiple per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 763 |  | 1 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 790 |  | 1 per 7 to 10 day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 816 | 4 per 10 month | 1 per month | no | final_label_repaired: '4 in 2017' -> '4 per 10 month'; evidence_not_exact_substring |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 |  | multiple per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 |  | 1 per 2 week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month'; evidence_not_exact_substring |
| 960 |  | 1 per 2 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month'; evidence_not_exact_substring |
| 1030 | 1 per month | 1 to 3 per month | no | final_label_repaired: 'unknown' -> '1 per month' |
| 1046 | unknown | 3 to 5 per month | no |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 |  | 5 to 7 per 3 week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1171 | 9 per 3 week | 7 to 9 per 3 week | yes | final_label_repaired: 'multiple per week' -> '9 per 3 week' |
| 1207 | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | final_label_repaired: 'multiple per week' -> '21 to 28 per 3 month' |
| 1223 | 4 per week | 3 to 4 per week | yes | final_label_repaired: '3 or 4 per week' -> '4 per week' |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 |  | 5 to 7 per year | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1317 |  | unknown, multiple per cluster | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 |  | 3 per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 |  | 7 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes | evidence_not_exact_substring |
| 1591 |  | 11 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 |  | 5 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1640 | 5 per week | 5 per week | yes | final_label_repaired: 'multiple per week' -> '5 per week' |
| 1687 |  | multiple per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 per 2 weeks' -> '3 per 2 week' |
| 1695 | seizure free for multiple year | multiple per month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | final_label_repaired: 'multiple per week' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '11 seizures in 6 months' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: 'multiple per week' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '8 in the past four months' -> '8 per 4 month' |
| 1794 |  | 8 per 2 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1866 |  | 8 per 2 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1880 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'multiple per week' -> '8 per 2 month'; evidence_not_exact_substring |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 seizures in 3 months' -> '4 per 3 month' |
| 1914 |  | 7 per 3 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1922 |  | 7 per 3 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1923 |  | 7 per 6 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1979 |  | 6 per 2 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '6 in the past three months' -> '6 per 3 month' |
| 2023 | 4 per month | 5 per month | no |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day'; evidence_not_exact_substring |
| 2094 |  | multiple per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2114 |  | multiple per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2149 | no seizure frequency reference | unknown | yes | final_label_repaired: 'occasional' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 2166 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: 'multiple per week' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | final_label_repaired: '6 to 7 per 2 months' -> '6 to 7 per 2 month' |
| 2245 |  | 7 to 8 per 3 week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | final_label_repaired: '6 to 8 per 3 months' -> '6 to 8 per 3 month' |
| 2354 |  | 6 to 7 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 |  | 3 to 4 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 |  | 6 to 8 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2427 |  | 3 to 5 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: 'multiple per week' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: 'multiple per week' -> '5 to 7 per 2 month' |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | final_label_repaired: 'multiple per week' -> '6 to 7 per 2 week' |
| 2459 |  | 7 to 9 per 2 week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: 'multiple per week' -> '8 to 9 per 2 week' |
| 2548 |  | 5 to 6 per 2 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | final_label_repaired: '3 to 4 per 2 months' -> '3 to 4 per 2 month' |
| 2609 |  | 1 per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2622 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 |  | 1 per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2681 |  | 1 per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 1 per month | 1 per month | yes |  |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 |  | 1 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2776 |  | 1 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2789 | 1 per week | 1 per week | yes |  |
| 2812 | 1 per day | 1 per day | yes |  |
| 2822 | 1 per day | 1 per day | yes |  |
| 2824 | 1 per day | 1 per day | yes |  |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free since 27 March 2024' -> 'seizure free for multiple year' |
| 2932 | 13 per 2 month | seizure free for 9 month | no | final_label_repaired: 'seizure free since 29/09/2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '13 per 2 month' |
| 2938 |  | seizure free for 8 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2965 |  | seizure free for 16 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 2992 | 1 per 8 month | seizure free for 7 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 8 month' |
| 3015 | 1 per 13 month | seizure free for 12 month | no | final_label_repaired: 'seizure free for 1 year' -> '1 per 13 month' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 |  | seizure free for multiple month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '6 to 7 per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 |  | 2 cluster per month, 5 per cluster | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3262 |  | 2 cluster per month, 5 per cluster | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 |  | 3 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3356 | unknown | unknown | yes |  |
| 3371 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes | evidence_not_exact_substring |
| 3468 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3469 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3482 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3493 | unknown | unknown | yes | final_label_repaired: 'cluster frequency' -> 'unknown' |
| 3507 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3512 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3528 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3532 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased frequency' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 3534 | seizure free for 7 month | unknown | no | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 3600 | unknown | unknown | yes |  |
| 3623 |  | 7 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3643 |  | 7 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3681 |  | 9 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3682 | 6 per month | 6 per month | yes |  |
| 3710 | 5 per week | 5 per week | yes |  |
| 3753 | 1 per day | 1 per day | yes |  |
| 3766 | 8 per year | 8 per year | yes |  |
| 3774 | 9 per year | 9 per year | yes |  |
| 3791 |  | 10 per year | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3801 |  | 9 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3806 | 6 per month | 6 per month | yes |  |
| 3827 | 7 per month | 7 per month | yes |  |
| 3846 |  | 2 per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3849 |  | 3 per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 | 3 per year | 3 per year | yes |  |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 |  | 4 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3988 |  | multiple per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 3995 | 1 per month | 1 per month | yes |  |
| 3999 | 1 per month | 1 per month | yes |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 |  | 1 per month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 |  | 1 per 1 to 2 day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: 'multiple per week' -> '1 per 1 to 2 day'; evidence_not_exact_substring |
| 4173 | no seizure frequency reference | 1 per 2 week | no | final_label_repaired: '1 per fortnight' -> 'no seizure frequency reference' |
| 4243 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 4258 |  | 4 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4337 |  | 3 per 3 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4345 | 4 per month | 4 per month | yes |  |
| 4368 | 5 per month | 5 per 2 month | no | final_label_repaired: '5 events' -> '5 per month' |
| 4402 | 14 per 14 month | 7 per 7 month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '14 per 14 month' |
| 4410 |  | 4 per 7 month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4478 |  | 19 per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes | final_label_repaired: '3-5 per week' -> '3 to 5 per week' |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '7 to 8 per quarter' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 every 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 |  | 1 per 3 to 4 day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4631 | 1 per 2 to 3 week | 1 per 14 to 21 day | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4690 | no seizure frequency reference | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4694 |  | multiple per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4700 | no seizure frequency reference | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4709 |  | multiple per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4731 | unknown | unknown | yes |  |
| 4732 | no seizure frequency reference | unknown | yes | final_label_repaired: 'occasional' -> 'no seizure frequency reference' |
| 4771 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 in the last six weeks' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 4839 | 1 per 5 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 4 month' -> '1 per 5 month' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 |  | seizure free for 2 year | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 |  | seizure free for multiple month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 4992 | seizure free for multiple year | seizure free for 11 month | yes | final_label_repaired: 'seizure free since 12-Sep-2018' -> 'seizure free for multiple year' |
| 4994 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free since 25/06/2021' -> 'seizure free for multiple year' |
| 5040 | seizure free for multiple year | seizure free for 6 months | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5092 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5110 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5141 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5197 |  | seizure free for multiple month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 5379 |  | seizure free for multiple month | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 5406 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5476 | unknown | unknown | yes | evidence_not_exact_substring |
| 5490 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 5491 | 2 per 6 week | unknown | no | final_label_repaired: '2 episodes in 6 weeks' -> '2 per 6 week' |
| 5504 |  | unknown | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 5507 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 since June' -> 'no seizure frequency reference' |
| 5528 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5534 | no seizure frequency reference | 1 per multiple month | yes | final_label_repaired: 'very infrequent' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 5551 |  | multiple per day | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 |  | multiple per week | no | invalid_json: Expecting property name enclosed in double quotes; evidence_not_exact_substring |
