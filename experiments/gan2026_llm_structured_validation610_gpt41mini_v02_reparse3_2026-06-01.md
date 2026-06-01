# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-first structured event extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 610 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first structured event extractor and clinical selector
- Prompt/program version: `gan2026_llm_structured_event_selector_v0.2`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `prompt-only`
- DSPy cache enabled: `True`
- Reused raw model outputs: `610`
- Reuse source: `experiments/gan2026_llm_structured_validation630_gpt41mini_v02_completion2_2026-06-01.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Git commit: `4d03192`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_structured_validation610_gpt41mini_v02_reparse3_2026-06-01.jsonl`

## Summary

- Structured records: 610 / 610
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 358
- Exact selection evidence substrings: 580 / 610
- Purist validation accuracy/micro F1 proxy: 0.9016 (550 / 610)
- Pragmatic validation accuracy/micro F1 proxy: 0.9131 (557 / 610)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '1 cluster per week' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: '1 per month' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes |  |
| 409 | 1 per month | 1 per month | yes | final_label_repaired: '1 per month or less' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per month' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 | multiple per week | multiple per week | yes |  |
| 744 | no seizure frequency reference | multiple per week | yes | final_label_repaired: 'most weekdays' -> 'no seizure frequency reference' |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per week' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per day | multiple per month | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | final_label_repaired: '5 to 7 per 3 weeks' -> '5 to 7 per 3 week' |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 2 to 3 per week | 21 to 28 per 3 month | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes | evidence_not_exact_substring |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | final_label_repaired: 'less than 1 per month' -> '5 to 7 per 10 month' |
| 1317 | multiple per day | unknown, multiple per cluster | yes |  |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 3 per day | 3 per day | yes |  |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes |  |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes | final_label_repaired: '2 to 3 per week' -> '12 per month' |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per day' |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 per fortnight' -> '3 per 2 week' |
| 1695 | no seizure frequency reference | multiple per month | yes | final_label_repaired: 'a handful per month' -> 'no seizure frequency reference' |
| 1706 | multiple per week | multiple cluster per month, multiple per cluster | no |  |
| 1707 | multiple per week | multiple per week | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '2 to 3 per month' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '3 to 4 per month' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '2 per month' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 1880 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 per 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '2 to 5 per 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '6 per 2 months' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'a few per month' -> 'multiple per day' |
| 2094 | multiple per day | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per day' |
| 2114 | 2 to 3 per month | multiple per month | no |  |
| 2149 | unknown | unknown | yes |  |
| 2166 | no seizure frequency reference | unknown | yes | final_label_repaired: 'frequent' -> 'no seizure frequency reference' |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '2 to 3 per week' -> '3 to 5 per 2 week' |
| 2233 | 2 to 3 per month | 6 to 7 per 2 month | yes |  |
| 2245 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | final_label_repaired: '2 per month' -> '6 to 8 per 3 month' |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | evidence_not_exact_substring |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 2 to 3 per week | 5 to 7 per 2 week | yes | evidence_not_exact_substring |
| 2437 | 2 to 3 per month | 2 to 3 per 2 month | yes |  |
| 2440 | 2 to 3 per month | 5 to 7 per 2 month | yes |  |
| 2456 | 2 to 3 per week | 6 to 7 per 2 week | yes |  |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | final_label_repaired: 'multiple per week' -> '7 to 9 per 2 week' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per fortnight' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: '8 to 9 per 2 weeks' -> '8 to 9 per 2 week' |
| 2548 | 2 to 3 per month | 5 to 6 per 2 month | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 2 to 3 per month | 3 to 4 per 2 month | yes |  |
| 2609 | 1 per day | 1 per day | yes |  |
| 2622 | 1 per day | 1 per day | yes |  |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: '1 cluster per night' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes |  |
| 2681 | 1 per day | 1 per day | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every 2 days' -> '1 per 2 day'; evidence_not_exact_substring |
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
| 2932 | seizure free for 9 month | seizure free for 9 month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 2938 | seizure free for 6 month | seizure free for 8 month | yes |  |
| 2965 | seizure free for 1 year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 1 year 4 months' -> 'seizure free for 1 year' |
| 2992 | seizure free for 7 month | seizure free for 7 month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 3015 | seizure free for 1 year | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last visit' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '6 to 7 per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes | final_label_repaired: '6 per month with clustering' -> '6 per month' |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures after curtailed sleep' -> 'no seizure frequency reference' |
| 3371 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures only with significant sleep deprivation' -> 'no seizure frequency reference' |
| 3436 | unknown | unknown | yes | final_label_repaired: 'cluster shortly after early-morning arousal' -> 'unknown' |
| 3468 | unknown | unknown | yes | final_label_repaired: 'cluster perimenstrual' -> 'unknown' |
| 3469 | 2 per 6 month | unknown | no | final_label_repaired: 'perimenstrual cluster' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 6 month' |
| 3482 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures perimenstrual only (days -3 to +3)' -> 'no seizure frequency reference' |
| 3493 | unknown | unknown | yes | final_label_repaired: 'clustered around period' -> 'unknown'; evidence_not_exact_substring |
| 3507 | unknown | unknown | yes | final_label_repaired: 'unknown frequency reduction' -> 'unknown' |
| 3512 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased by ~20% after dose increase' -> 'no seizure frequency reference' |
| 3528 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased frequency' -> 'no seizure frequency reference' |
| 3532 | unknown | unknown | yes | evidence_not_exact_substring |
| 3534 | seizure free for 7 month | unknown | no | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 3600 | unknown | unknown | yes |  |
| 3623 | multiple per week | 7 per week | no |  |
| 3643 | multiple per week | 7 per week | no | final_label_repaired: 'up to 7 per week' -> 'multiple per week' |
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
| 3995 | 1 per month | 1 per month | yes |  |
| 3999 | 1 per month | 1 per month | yes | final_label_repaired: 'abs monthly' -> '1 per month' |
| 4022 | 8 per month | 8 per month | yes | final_label_repaired: '2 to 3 per month' -> '8 per month' |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4173 | 2 per month | 1 per 2 week | yes |  |
| 4243 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 4258 | 4 per week | 4 per week | yes |  |
| 4337 | no seizure frequency reference | 3 per 3 month | no | final_label_repaired: '3 events in last 6 months' -> 'no seizure frequency reference' |
| 4345 | 4 per month | 4 per month | yes |  |
| 4368 | 2 per month | 5 per 2 month | yes |  |
| 4402 | 7 per 7 month | 7 per 7 month | yes | final_label_repaired: '1 to 2 per month' -> '7 per 7 month' |
| 4410 | 4 per 7 month | 4 per 7 month | yes | final_label_repaired: '1 per month' -> '4 per 7 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '7 to 8 per quarter' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | unknown | 1 per 3 to 4 day | no | final_label_repaired: '1 cluster every 3 to 4 days' -> 'unknown' |
| 4631 | 1 per 2 to 3 week | 1 per 14 to 21 day | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4690 | no seizure frequency reference | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4694 | no seizure frequency reference | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4700 | no seizure frequency reference | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4709 | no seizure frequency reference | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 4731 | no seizure frequency reference | unknown | yes | final_label_repaired: 'rare' -> 'no seizure frequency reference' |
| 4732 | unknown | unknown | yes | final_label_repaired: 'occasional seizures with clustering' -> 'unknown' |
| 4771 | multiple per week | unknown | yes | evidence_not_exact_substring |
| 4839 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 4956 | seizure free for 6 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5092 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5141 | seizure free for 1.5 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 1.5 months' -> 'seizure free for 1.5 month' |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last consultation' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 5379 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5406 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 5476 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5490 | unknown | unknown | yes |  |
| 5491 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic per year' -> 'no seizure frequency reference' |
| 5504 | unknown | unknown | yes |  |
| 5507 | multiple per week | unknown | yes |  |
| 5528 | 1 per month | 1 per month | yes | final_label_repaired: '1 isolated event last month' -> '1 per month' |
| 5534 | 1 per 2 week | 1 per multiple month | no | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 5551 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'Several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per week' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5763 | 2 per 3 month | 2 per month | no | final_label_repaired: '6 per 3 months' -> '2 per 3 month' |
| 5767 | 2 per month | 1 per 1 to 2 week | yes | final_label_repaired: '2 to 4 per month' -> '2 per month' |
| 5791 | 2 to 3 per 3 month | 1 per month | no | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 5827 | 2 per 8 week | multiple per week | no | final_label_repaired: '2 per 8 weeks' -> '2 per 8 week' |
| 5837 | multiple per week | 2 cluster per 3 week, multiple per cluster | no |  |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '4 per 6 weeks' -> '4 per 6 week' |
| 5873 | multiple per week | multiple per week | yes |  |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 5974 | unknown | unknown | yes | final_label_repaired: 'unknown frequency but seizures occur with missed doses' -> 'unknown'; evidence_not_exact_substring |
| 5977 | multiple per month | unknown | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 5995 | 1 to 2 per month | 1 per 3 months | no | evidence_not_exact_substring |
| 5996 | unknown | unknown | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes | final_label_repaired: 'ongoing focal aware and impaired-awareness seizures with clustering episodes' -> 'unknown'; evidence_not_exact_substring |
| 6034 | unknown | unknown | yes | final_label_repaired: 'clustered episodes during disrupted routine' -> 'unknown' |
| 6065 | 5 per month | 5 per month | yes |  |
| 6077 | no seizure frequency reference | unknown | yes | final_label_repaired: '1 breakthrough episode' -> 'no seizure frequency reference' |
| 6087 | unknown | unknown | yes |  |
| 6094 | no seizure frequency reference | 3 per month | no | final_label_repaired: '5 events in 6 weeks' -> 'no seizure frequency reference' |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 6137 | 2 to 3 per month | 1 per 2 week | yes |  |
| 6153 | multiple per week | 9 per month | no |  |
| 6180 | multiple per week | multiple per week | yes |  |
| 6192 | unknown | unknown | yes |  |
| 6204 | 1 per 3 to 4 week | 2 per month | yes | final_label_repaired: '1 per month' -> '1 per 3 to 4 week' |
| 6209 | multiple per day | multiple per day | yes | final_label_repaired: '1 per day' -> 'multiple per day' |
| 6244 | 2 per week | unknown | no | evidence_not_exact_substring |
| 6251 | no seizure frequency reference | 1 per 1 to 2 month | no | final_label_repaired: 'rare events' -> 'no seizure frequency reference' |
| 6273 | unknown | unknown | yes | final_label_repaired: 'unknown frequency' -> 'unknown' |
| 6319 | 1 per week | 1 per week | yes |  |
| 6321 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 per summer' -> 'no seizure frequency reference' |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 6358 | seizure free for 4 month | seizure free for 15 to 16 months | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 6368 | multiple per day | unknown | yes | final_label_repaired: '3 per 6 weeks' -> 'multiple per day' |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes | final_label_repaired: 'clusters lasting 2 to 3 days every few weeks' -> 'unknown' |
| 6509 | multiple per week | 1 per week | no |  |
| 6571 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 6607 | no seizure frequency reference | unknown | yes | final_label_repaired: 'worsening seizure frequency' -> 'no seizure frequency reference' |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6701 | 1 to 2 per week | 4 per 3 week | yes |  |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes |  |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes |  |
| 6987 | 10 to 15 per 1 year | unknown | no | final_label_repaired: 'unknown' -> '10 to 15 per 1 year'; evidence_not_exact_substring |
| 7093 | unknown | unknown | yes | final_label_repaired: 'cluster frequency related to menstrual cycle' -> 'unknown' |
| 7126 | multiple per week | unknown | yes |  |
| 7141 | unknown | unknown | yes | final_label_repaired: 'cluster per cycle' -> 'unknown' |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no | final_label_repaired: '3 clusters per 6 weeks' -> 'unknown' |
| 7168 | 2 per year | unknown | no |  |
| 7192 | multiple per week | multiple per week | yes |  |
| 7195 | 1 per month | unknown | no |  |
| 7196 | multiple per week | 1 per week | no |  |
| 7198 | multiple per month | unknown | yes |  |
| 7275 | 2 to 3 per month | 1 per month | no |  |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | final_label_repaired: '2 clusters per 6 weeks' -> 'unknown' |
| 7409 | multiple per week | unknown | yes |  |
| 7455 | unknown | unknown | yes |  |
| 7475 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month'; evidence_not_exact_substring |
| 7491 | unknown | unknown | yes | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 7506 | unknown | unknown | yes |  |
| 7573 | 2 to 3 per month | 1 per 2 week | yes |  |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | 2 per 10 month | 3 to 7 per month | no | final_label_repaired: '2 per year' -> '2 per 10 month' |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 7818 | seizure free for multiple year | seizure free for 2 years | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7859 | unknown | unknown | yes |  |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7961 | seizure free for 2 year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8079 | seizure free for 1 year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 1 year 7 months' -> 'seizure free for 1 year' |
| 8089 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8144 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8160 | 1 per multiple week | seizure free for multiple month | no | final_label_repaired: '1 per few weeks' -> '1 per multiple week' |
| 8180 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 8188 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last clinic assessment' -> 'seizure free for multiple year' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for current follow-up period' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8354 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 12+ months' -> 'seizure free for multiple year' |
| 8400 | no seizure frequency reference | seizure free for multiple month | no | final_label_repaired: 'occasional' -> 'no seizure frequency reference' |
| 8419 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 8474 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8577 | seizure free for 18 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 8581 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8808 | 0 per 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> '0 per 10 month'; evidence_not_exact_substring |
| 8820 | seizure free for 7 month | seizure free for 7 month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 8835 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 8854 | seizure free for 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; evidence_not_exact_substring |
| 8922 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 8924 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since May 2025' -> 'seizure free for multiple year' |
| 8938 | seizure free for multiple year | seizure free for 10 month | yes | final_label_repaired: 'seizure free for over 10 months' -> 'seizure free for multiple year' |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9002 | 7 per 10 month | 7 per year | yes | final_label_repaired: '7 per year' -> '7 per 10 month' |
| 9063 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free for over 8 months' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9103 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent over the past year' -> 'no seizure frequency reference' |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9190 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 9215 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 9238 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 9250 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '2 per month' -> '4 per 6 month' |
| 9462 | 7 per 11 month | 7 per 11 month | yes | final_label_repaired: '2 per month' -> '7 per 11 month' |
| 9496 | no seizure frequency reference | 6 per 12 month | no | final_label_repaired: 'low-frequency' -> 'no seizure frequency reference' |
| 9547 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent events with variable spacing' -> 'no seizure frequency reference' |
| 9588 | seizure free for 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 9704 | unknown | unknown | yes | final_label_repaired: 'unknown frequency' -> 'unknown' |
| 9815 | no seizure frequency reference | multiple per day | yes | final_label_repaired: '9 per hour' -> 'no seizure frequency reference' |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes | final_label_repaired: 'brief clusters over past 3 months' -> 'unknown' |
| 9888 | unknown | unknown | yes | final_label_repaired: 'unknown frequency' -> 'unknown' |
| 9912 | unknown | unknown | yes | final_label_repaired: 'unknown frequency' -> 'unknown' |
| 9937 | multiple per month | 1 cluster per month, multiple per cluster | no |  |
| 9943 | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: '1 cluster every 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 clusters per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | 3 per month | 3 cluster per month, multiple per cluster | no |  |
| 10147 | unknown | unknown | yes |  |
| 10183 | unknown | unknown | yes |  |
| 10189 | no seizure frequency reference | unknown, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 per cluster sporadically' -> 'no seizure frequency reference' |
| 10200 | unknown | unknown, 2 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no | final_label_repaired: '4 clusters per month' -> 'unknown' |
| 10245 | 1 to 3 per 6 month | 3 cluster per month, multiple per cluster | no | final_label_repaired: '1 to 3 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '1 to 3 per 6 month' |
| 10260 | unknown | unknown | yes | final_label_repaired: 'unknown cluster frequency' -> 'unknown' |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes | evidence_not_exact_substring |
| 10371 | unknown | seizure free for multiple year | no |  |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 5 per cluster' |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 2 to 3 per cluster' |
| 10434 | multiple per week | multiple cluster per week, 2 to 3 per cluster | no |  |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes | final_label_repaired: 'clusters per week' -> 'unknown' |
| 10517 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: 'multiple per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10542 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | final_label_repaired: 'multiple per hour' -> 'no seizure frequency reference' |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes | final_label_repaired: 'unknown cluster frequency' -> 'unknown' |
| 10583 | multiple per week | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes | final_label_repaired: 'unknown frequency' -> 'unknown' |
| 10618 | unknown | unknown, 4 to 6 per cluster | yes | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10629 | unknown | unknown | yes |  |
| 10630 | multiple per week | multiple cluster per 2 week, 5 per cluster | no |  |
| 10673 | multiple per month | 1 cluster per month, multiple per cluster | no |  |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | multiple per week | unknown | yes |  |
| 10807 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | final_label_repaired: '2 cluster days per month' -> '2 cluster per month, multiple per cluster' |
| 10829 | 2 per 2 year | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 2 year' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: 'weekly clusters' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: 'weekly clusters' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 3 clusters per month' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 10965 | unknown | 2 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown' |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '3 per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | final_label_repaired: '1 to 2 clusters per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 4 per month' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 cluster days per month with 5+ seizures per day' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 cluster days per month, 6 seizures per cluster day' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '2 cluster days per month, 3 to 4 seizures per cluster' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | final_label_repaired: '1 cluster per month, 4 to 6 events per cluster' -> '1 cluster per month, 4 to 6 per cluster' |
| 11216 | seizure free for 4 month | unknown | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 11254 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 11259 | unknown | unknown | yes |  |
| 11262 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased absence and myoclonic seizures recent' -> 'no seizure frequency reference' |
| 11272 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 11282 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 11337 | no seizure frequency reference | unknown | yes | final_label_repaired: '1 seizure in 2 months' -> 'no seizure frequency reference' |
| 11350 | multiple per week | unknown | yes |  |
| 11380 | multiple per day | unknown | yes | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 11389 | no seizure frequency reference | unknown | yes | final_label_repaired: 'low-frequency breakthrough seizures' -> 'no seizure frequency reference' |
| 11400 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11409 | unknown | no seizure frequency reference | yes | final_label_repaired: 'occasional cluster patterns' -> 'unknown' |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11737 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11824 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
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
| 12236 | 1 per day | 1 per day | yes |  |
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
| 12484 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12502 | 4 per day | 4 per day | yes |  |
| 12506 | 4 per day | 4 per day | yes |  |
| 12537 | 1 per day | 1 per day | yes |  |
| 12548 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12556 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12562 | multiple per day | 1 per day | no | final_label_repaired: 'multiple per week' -> 'multiple per day'; evidence_not_exact_substring |
| 12573 | 1 per day | 1 per day | yes |  |
| 12584 | multiple per week | 1 per week | no |  |
| 12641 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12665 | 1 per day | 1 per day | yes |  |
| 12667 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12676 | 1 per day | 1 per day | yes |  |
| 12679 | 1 to 2 per month | 1 per day | no |  |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | 4 per day | 4 per day | yes |  |
| 12788 | 6 per 4 month | 6 per 4 month | yes | final_label_repaired: '6 per year' -> '6 per 4 month' |
| 12810 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 per year' -> '5 per 2 month' |
| 12823 | 9 per month | 9 per month | yes | final_label_repaired: '9 per year' -> '9 per month' |
| 12827 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12835 | 4 per month | 4 per month | yes | final_label_repaired: '4 per year' -> '4 per month' |
| 12877 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12882 | 7 per 4 month | 7 per 4 month | yes | final_label_repaired: '7 per year' -> '7 per 4 month' |
| 12901 | 8 per 5 month | 8 per 5 month | yes | final_label_repaired: 'multiple per month' -> '8 per 5 month' |
| 12949 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '9 per year' -> '9 per 6 month' |
| 12950 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per year' -> '7 per 3 month' |
| 12963 | multiple per year | unknown | yes | final_label_repaired: 'few per year' -> 'multiple per year' |
| 12979 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per year' -> '3 per 4 month' |
| 13008 | 4 per month | 4 per month | yes | final_label_repaired: 'multiple per year' -> '4 per month' |
| 13011 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per year' -> '3 per 4 month' |
| 13051 | 1 per 8 month | 2 per 8 month | no | final_label_repaired: '1 generalised tonic-clonic seizure 3 weeks ago with preceding cluster of absences' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 8 month' |
| 13058 | 1 per 7 month | 2 per 7 month | no | final_label_repaired: '1 cluster plus 1 tonic-clonic seizure in 3 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 7 month' |
| 13114 | multiple per week | 1 per year | no | evidence_not_exact_substring |
| 13122 | 3 per 1 year | 3 per year | yes | final_label_repaired: '3 seizures in one day' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 1 year' |
| 13149 | 3 per 1 year | 3 per year | yes | final_label_repaired: '3 seizures 2 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 1 year' |
| 13178 | 1 per 6 month | 1 per 6 month | yes | final_label_repaired: '1 event 2 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 6 month' |
| 13190 | 1 per 5 month | 1 per 5 month | yes | final_label_repaired: '1 event 3 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 5 month' |
| 13209 | 1 per 4 to 5 week | 1 per 8 month | no | final_label_repaired: '1 cluster per month' -> '1 per 4 to 5 week' |
| 13267 | 1 per month | 2 per 5 month | no |  |
| 13290 | 2 per 6 month | 4 per 6 month | yes | final_label_repaired: '2 seizures in 2 weeks' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 per 6 month' |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13349 | seizure free for 12 month | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13450 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over one year' -> 'seizure free for multiple year' |
| 13471 | seizure free for 5 year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for 5 years' -> 'seizure free for 5 year' |
| 13478 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13627 | 64 per 12 month | 64 per 12 month | yes | final_label_repaired: 'multiple per month' -> '64 per 12 month' |
| 13635 | 47 per 7 month | 47 per 7 month | yes | final_label_repaired: 'multiple per month' -> '47 per 7 month' |
| 13711 | 76 per 12 month | 76 per 12 month | yes | final_label_repaired: 'multiple per month' -> '76 per 12 month' |
| 13721 | 77 per 12 month | 77 per 12 month | yes | final_label_repaired: 'multiple per month' -> '77 per 12 month' |
| 13732 | 52 per 8 month | 52 per 8 month | yes | final_label_repaired: 'multiple per week' -> '52 per 8 month'; evidence_not_exact_substring |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13893 | 2 per year | 2 per year | yes |  |
| 13922 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 seizures since medication increase' -> 'no seizure frequency reference' |
| 14002 | unknown | unknown | yes |  |
| 14025 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 14029 | multiple per month | unknown | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 14040 | unknown | unknown | yes |  |
| 14076 | no seizure frequency reference | unknown | yes | final_label_repaired: 'more frequent brief morning myoclonic jerks' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 14092 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 events since last appointment' -> 'no seizure frequency reference' |
| 14096 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 per recent period' -> 'no seizure frequency reference' |
| 14137 | 3 to 4 per 3 month | unknown | no | final_label_repaired: '3 to 4 per 3 months' -> '3 to 4 per 3 month' |
| 14146 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 per recent period' -> 'no seizure frequency reference' |
| 14187 | 2 to 3 per 1 month | 2 to 3 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '2 to 3 per 1 month' |
| 14214 | 2 to 4 per 1 month | 2 to 4 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '2 to 4 per 1 month' |
| 14250 | 2 per 1 month | 2 per month | yes | final_label_repaired: '2 per week' -> '2 per 1 month' |
| 14282 | 10 per 6 week | multiple per month | no | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '10 per 6 week' |
| 14284 | 2 to 3 per 1 month | 2 to 3 per month | yes | final_label_repaired: '2 to 3 per week' -> '2 to 3 per 1 month' |
| 14317 | 4 per 2 month | 4 per 2 month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '4 per 2 month' |
| 14332 | no seizure frequency reference | 5 per 2 month | no | final_label_repaired: '5 per cluster' -> 'no seizure frequency reference' |
| 14335 | 3 to 4 per 8 week | 3 to 4 per 2 month | yes | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 8 week' |
| 14383 | 3 to 4 per 3 month | 3 to 4 per 3 month | yes | final_label_repaired: 'seizure free since mid-January' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 to 4 per 3 month'; evidence_not_exact_substring |
| 14454 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '2 per 2 month' |
| 14524 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 6 month' |
| 14530 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'unknown' -> '2 per 2 month' |
| 14540 | seizure free for multiple year | 2 per 8 month | no | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year' |
| 14562 | 3 per 6 month | 3 per 6 month | yes | final_label_repaired: 'unknown' -> '3 per 6 month' |
