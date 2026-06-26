# Gan 2026 LLM-First Validation Run

Date: 2026-06-09

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only direct-labeler note-to-label extractor
- Prompt/program version: `gan2026_llm_only_direct_labeler_v0.4`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-09T06:43:29.004712+00:00`
- Run finished UTC: `2026-06-09T06:52:20.030832+00:00`
- Wall-clock elapsed: `531.026` seconds (`8.85` minutes)
- Throughput: `0.470787` rows/sec (`2.124` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `a7c426f`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_direct_labeler_v04_validation250_gpt41mini_2026-06-09.jsonl`

## Summary

- Decision records: 250 / 250
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 112
- Exact evidence substrings: 242 / 250
- Purist validation accuracy/micro F1 proxy: 0.9560 (239 / 250)
- Pragmatic validation accuracy/micro F1 proxy: 0.9680 (242 / 250)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'multiple per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes |  |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 2 per month | 1 per 7 to 9 day | yes |  |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: '1 per month' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month'; evidence_not_exact_substring |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes | final_label_repaired: 'many per month' -> 'multiple per month' |
| 409 | 1 per month | 1 per month | yes |  |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 731 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 743 | multiple per day | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per 7 to 10 days' -> '1 per 7 to 10 day' |
| 816 | 4 per year | 1 per month | no |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | seizure free for multiple year | 5 to 7 per 3 week | no | final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year' |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes | evidence_not_exact_substring |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per year | 5 to 7 per year | yes |  |
| 1317 | multiple per day | unknown, multiple per cluster | yes |  |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 3 per day | 3 per day | yes |  |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes | final_label_repaired: '1 tonic-clonic and 6 petit mal per week' -> '7 per week' |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes | final_label_repaired: '2 to 3 per month' -> '5 per month' |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per day' |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 per fortnight' -> '3 per 2 week' |
| 1695 | no seizure frequency reference | multiple per month | yes |  |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | final_label_repaired: 'multiple per cluster' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '2 to 3 per month' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '3 per month' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '2 per month' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '4 per month' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '4 per month' -> '8 per 2 month' |
| 1880 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '7 convulsions in 2 months' -> '8 per 2 month' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 per 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 per 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '3 per 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | unknown | multiple per month | yes |  |
| 2149 | multiple per month | unknown | yes | final_label_repaired: 'occasional tonic-clonic over last year' -> 'multiple per month' |
| 2166 | unknown | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per 2 weeks' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | final_label_repaired: '6 to 7 per 2 months' -> '6 to 7 per 2 month' |
| 2245 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2259 | 2 to 3 per month | 6 to 8 per 3 month | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 2 to 3 per month | 5 to 7 per 2 month | yes |  |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | final_label_repaired: '6 to 7 per 2 weeks' -> '6 to 7 per 2 week' |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: '8 to 9 per 2 weeks' -> '8 to 9 per 2 week' |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | final_label_repaired: '5 to 6 per 2 months' -> '5 to 6 per 2 month' |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | final_label_repaired: '3 to 4 per 2 months' -> '3 to 4 per 2 month' |
| 2609 | 1 per day | 1 per day | yes |  |
| 2622 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2681 | 1 per day | 1 per day | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 1 per month | 1 per month | yes |  |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes | evidence_not_exact_substring |
| 2812 | 1 per day | 1 per day | yes |  |
| 2822 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2824 | 1 per day | 1 per day | yes |  |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | seizure free for multiple year | seizure free for 9 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 2938 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 2965 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 2992 | seizure free for 7 month | seizure free for 7 month | yes | evidence_not_exact_substring |
| 3015 | seizure free for multiple year | seizure free for 12 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 per month' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 per month' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, multiple per cluster | 2 cluster per month, 5 per cluster | no | final_label_repaired: '2 per month' -> '2 cluster per month, multiple per cluster' |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | unknown | unknown | yes |  |
| 3371 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes |  |
| 3468 | unknown | unknown | yes | evidence_not_exact_substring |
| 3469 | unknown | unknown | yes |  |
| 3482 | unknown | unknown | yes |  |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 | unknown | unknown | yes |  |
| 3528 | unknown | unknown | yes |  |
| 3532 | unknown | unknown | yes |  |
| 3534 | seizure free for 7 month | unknown | no |  |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'unknown' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes |  |
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
| 3995 | 2 to 3 per month | 1 per month | no |  |
| 3999 | 2 to 3 per month | 1 per month | no |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes |  |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day on workdays' -> '1 per 1 to 2 day' |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 4258 | 4 per 2 week | 4 per week | yes | final_label_repaired: '4 per week' -> '4 per 2 week' |
| 4337 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '3 per year' -> '3 per 3 month' |
| 4345 | 4 per month | 4 per month | yes |  |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '2 to 3 per month' -> '5 per 2 month' |
| 4402 | 7 per 7 month | 7 per 7 month | yes | final_label_repaired: '1 per month' -> '7 per 7 month' |
| 4410 | 4 per 7 month | 4 per 7 month | yes | final_label_repaired: '1 per month' -> '4 per 7 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '2 per month' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | 2 per month | 1 per 3 to 4 day | no |  |
| 4631 | 1 per 2 to 3 week | 1 per 14 to 21 day | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4690 | no seizure frequency reference | multiple per day | yes |  |
| 4694 | multiple per day | multiple per day | yes |  |
| 4700 | multiple per day | multiple per day | yes |  |
| 4709 | unknown | multiple per day | yes |  |
| 4731 | unknown | unknown | yes |  |
| 4732 | unknown | unknown | yes |  |
| 4771 | unknown | unknown | yes |  |
| 4839 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for one year' -> 'seizure free for 1 year' |
| 4951 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for multiple year | seizure free for 6 months | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5092 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5110 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | evidence_not_exact_substring |
| 5141 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several month' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 5379 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 5476 | unknown | unknown | yes |  |
| 5490 | unknown | unknown | yes | evidence_not_exact_substring |
| 5491 | unknown | unknown | yes |  |
| 5504 | unknown | unknown | yes | evidence_not_exact_substring |
| 5507 | 3 per 4 month | unknown | no | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5528 | 1 per month | 1 per month | yes | final_label_repaired: 'unknown' -> '1 per month' |
| 5534 | 2 to 3 per month | 1 per multiple month | no |  |
| 5551 | multiple per day | multiple per day | yes |  |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
