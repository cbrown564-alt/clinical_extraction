# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-first structured event extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
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
- Reused raw model outputs: `250`
- Reuse source: `experiments/gan2026_llm_structured_validation250_gpt41mini_v02_2026-06-01.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Git commit: `4d03192`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_structured_validation250_gpt41mini_v02_reparse_2026-06-01.jsonl`

## Summary

- Structured records: 248 / 250
- Call failures: 0
- Parse/schema/label issues: 2
- Deterministic repair notes: 131
- Exact selection evidence substrings: 241 / 250
- Purist validation accuracy/micro F1 proxy: 0.9560 (239 / 250)
- Pragmatic validation accuracy/micro F1 proxy: 0.9560 (239 / 250)

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
| 869 | multiple per month | multiple per month | yes |  |
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
| 1281 | 5 to 7 per year | 5 to 7 per year | yes | final_label_repaired: 'less than 1 per month' -> '5 to 7 per year' |
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
| 1687 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
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
| 2080 | multiple per month | multiple per month | yes | final_label_repaired: 'a few per month' -> 'multiple per month' |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
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
| 3224 | 6 to 7 per month | 1 cluster per month, 6 to 7 per cluster | yes |  |
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
| 3469 | unknown | unknown | yes | final_label_repaired: 'perimenstrual cluster' -> 'unknown' |
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
| 4771 |  | unknown | no | schema_validation_error: Field required; evidence_not_exact_substring |
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
| 5406 | unknown | seizure free for multiple month | no |  |
| 5476 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5490 | unknown | unknown | yes |  |
| 5491 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic per year' -> 'no seizure frequency reference' |
| 5504 | unknown | unknown | yes |  |
| 5507 | multiple per week | unknown | yes |  |
| 5528 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 5534 | 1 per 2 week | 1 per multiple month | no | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 5551 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'Several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
