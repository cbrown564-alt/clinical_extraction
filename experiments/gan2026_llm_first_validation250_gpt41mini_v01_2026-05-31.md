# Gan 2026 LLM-First Validation Run

Date: 2026-05-31

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-first direct extraction runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation[:250]` split, `gan2026_split_v1`, 250 rows.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first note-to-label extractor
- Prompt/program version: `gan2026_llm_first_direct_extractor_v0.1`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `5ba74ea`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.jsonl`

## Summary

- Decision records: 250 / 250
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 96
- Exact evidence substrings: 86 / 250
- Purist validation accuracy/micro F1 proxy: 0.8200 (205 / 250)
- Pragmatic validation accuracy/micro F1 proxy: 0.8560 (214 / 250)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: '≤ four per day' -> '4 per day'; evidence_not_exact_substring |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤ four per week' -> '4 per week'; evidence_not_exact_substring |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year'; evidence_not_exact_substring |
| 103 | 2 to 4 per year | 2 to 4 per year | yes | evidence_not_exact_substring |
| 128 | 17 per month | 17 per month | yes | evidence_not_exact_substring |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day'; evidence_not_exact_substring |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day'; evidence_not_exact_substring |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every 2 days' -> '1 per 2 day'; evidence_not_exact_substring |
| 187 | no seizure frequency reference | 1 per 7 to 9 day | no | final_label_repaired: '2 nocturnal generalised tonic–clonic seizures per 4 months' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week'; evidence_not_exact_substring |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week'; evidence_not_exact_substring |
| 218 | 1 per 3 week | 1 per 3 week | yes | evidence_not_exact_substring |
| 243 | 1 per 4 month | 1 per 4 month | yes | evidence_not_exact_substring |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | no seizure frequency reference | multiple per month | yes | final_label_repaired: 'many per month' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 409 | multiple per month | 1 per month | no | final_label_repaired: '≤ once per month' -> 'multiple per month'; evidence_not_exact_substring |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | multiple per week | 2 per week | no | final_label_repaired: '≤ twice per week' -> 'multiple per week'; evidence_not_exact_substring |
| 466 | 21 to 28 per month | 21 to 28 per month | yes | evidence_not_exact_substring |
| 467 | 9 per month | 9 per month | yes | evidence_not_exact_substring |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month'; evidence_not_exact_substring |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 659 | 1 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '1 per 4 day'; evidence_not_exact_substring |
| 665 | 1 per 2 week | 2 per 2 week | no | final_label_repaired: '2 per 2 weeks' -> '1 per 2 week'; evidence_not_exact_substring |
| 678 | 1 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 month' -> '1 per 4 month'; evidence_not_exact_substring |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | multiple per day | 1 per day | no | evidence_not_exact_substring |
| 731 | multiple per day | 1 per day | no | evidence_not_exact_substring |
| 743 | multiple per week | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per 7 to 10 days' -> '1 per 7 to 10 day'; evidence_not_exact_substring |
| 816 | 4 per year | 1 per month | no | evidence_not_exact_substring |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month'; evidence_not_exact_substring |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day'; evidence_not_exact_substring |
| 899 | 1 per 2 week | 1 per 2 week | yes | evidence_not_exact_substring |
| 959 | 2 per month | 1 per 2 month | no |  |
| 960 | 2 per month | 1 per 2 month | no |  |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 every other month' -> '1 per 2 month'; evidence_not_exact_substring |
| 987 | 2 per month | 1 per 2 month | no |  |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes | evidence_not_exact_substring |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes | evidence_not_exact_substring |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes | evidence_not_exact_substring |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes | evidence_not_exact_substring |
| 1165 | 7 per month | 5 to 7 per 3 week | yes | final_label_repaired: '5 or 7 per 3 week' -> '7 per month'; evidence_not_exact_substring |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | evidence_not_exact_substring |
| 1207 | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | evidence_not_exact_substring |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes | evidence_not_exact_substring |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes | evidence_not_exact_substring |
| 1281 | 5 to 7 per year | 5 to 7 per year | yes | evidence_not_exact_substring |
| 1317 | unknown | unknown, multiple per cluster | yes | final_label_repaired: '1 cluster per day' -> 'unknown'; evidence_not_exact_substring |
| 1357 | no seizure frequency reference | 1 per day | no | final_label_repaired: '1 tonic-clonic seizure yesterday' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 1363 | 3 per day | 3 per day | yes | evidence_not_exact_substring |
| 1413 | 9 per month | 9 per month | yes | evidence_not_exact_substring |
| 1454 | no seizure frequency reference | 7 per week | no | final_label_repaired: '1 tonic-clonic and 6 petit mal in last week' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 1486 | 2 to 3 per month | 3 per month | yes | evidence_not_exact_substring |
| 1573 | 11 per week | 11 per week | yes | evidence_not_exact_substring |
| 1591 | 11 per month | 11 per month | yes | evidence_not_exact_substring |
| 1596 | 12 per week | 12 per week | yes | evidence_not_exact_substring |
| 1597 | 12 per month | 12 per month | yes | evidence_not_exact_substring |
| 1636 | 2 to 3 per month | 5 per month | no | evidence_not_exact_substring |
| 1640 | 5 per week | 5 per week | yes | evidence_not_exact_substring |
| 1687 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week'; evidence_not_exact_substring |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | evidence_not_exact_substring |
| 1695 | no seizure frequency reference | multiple per month | yes | final_label_repaired: 'a handful per month' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 1706 | unknown | multiple cluster per month, multiple per cluster | no | final_label_repaired: 'cluster of short events on multiple days' -> 'unknown' |
| 1707 | unknown | multiple per week | yes | final_label_repaired: 'brief cluster of events occurring on multiple days within the past week' -> 'unknown'; evidence_not_exact_substring |
| 1772 | 11 per 6 month | 11 per 6 month | yes | evidence_not_exact_substring |
| 1773 | 11 per 3 month | 11 per 3 month | yes | evidence_not_exact_substring |
| 1790 | 8 per 4 month | 8 per 4 month | yes | evidence_not_exact_substring |
| 1794 | no seizure frequency reference | 8 per 2 month | no | final_label_repaired: '6 drop attacks and 2 absence seizures in the past two months' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 1866 | 1 per month | 8 per 2 month | no | final_label_repaired: '1 per 2 month for drop attacks, 7 per 2 month for absence seizures' -> '1 per month'; evidence_not_exact_substring |
| 1880 | 7 per 2 month | 8 per 2 month | no | final_label_repaired: '7 per 2 months' -> '7 per 2 month'; evidence_not_exact_substring |
| 1887 | 4 per 3 month | 4 per 3 month | yes | evidence_not_exact_substring |
| 1914 | 7 per 3 month | 7 per 3 month | yes | evidence_not_exact_substring |
| 1922 | 7 per 3 month | 7 per 3 month | yes | evidence_not_exact_substring |
| 1923 | 7 per 6 month | 7 per 6 month | yes | evidence_not_exact_substring |
| 1979 | 6 per 2 month | 6 per 2 month | yes | final_label_repaired: '6 per 2 months' -> '6 per 2 month'; evidence_not_exact_substring |
| 1980 | 3 per 3 month | 6 per 3 month | no | evidence_not_exact_substring |
| 2023 | 5 per month | 5 per month | yes | evidence_not_exact_substring |
| 2080 | multiple per month | multiple per month | yes | final_label_repaired: 'a few per month' -> 'multiple per month'; evidence_not_exact_substring |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | seizure free for multiple year | multiple per month | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 2149 | no seizure frequency reference | unknown | yes | final_label_repaired: 'occasional tonic-clonic over last year' -> 'no seizure frequency reference' |
| 2166 | no seizure frequency reference | unknown | yes | final_label_repaired: 'frequent' -> 'no seizure frequency reference' |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | evidence_not_exact_substring |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | evidence_not_exact_substring |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | evidence_not_exact_substring |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | evidence_not_exact_substring |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes | evidence_not_exact_substring |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes | evidence_not_exact_substring |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes | evidence_not_exact_substring |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes | evidence_not_exact_substring |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | evidence_not_exact_substring |
| 2427 | 5 per month | 3 to 5 per month | no | final_label_repaired: '3 or 5 per month' -> '5 per month'; evidence_not_exact_substring |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | evidence_not_exact_substring |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | evidence_not_exact_substring |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | evidence_not_exact_substring |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | evidence_not_exact_substring |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | evidence_not_exact_substring |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | evidence_not_exact_substring |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | evidence_not_exact_substring |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | evidence_not_exact_substring |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | evidence_not_exact_substring |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | evidence_not_exact_substring |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | evidence_not_exact_substring |
| 2609 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | no seizure frequency reference | 1 per day | no | final_label_repaired: 'every night' -> 'no seizure frequency reference' |
| 2628 | multiple per day | 1 per day | no |  |
| 2678 | multiple per day | 1 per day | no |  |
| 2681 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day'; evidence_not_exact_substring |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | evidence_not_exact_substring |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 1 per month | 1 per month | yes | evidence_not_exact_substring |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes | evidence_not_exact_substring |
| 2812 | 1 per day | 1 per day | yes | evidence_not_exact_substring |
| 2822 | multiple per day | 1 per day | no |  |
| 2824 | multiple per day | 1 per day | no | evidence_not_exact_substring |
| 2877 | 2 per year | 2 per year | yes | evidence_not_exact_substring |
| 2887 | 2 per week | 2 per week | yes | evidence_not_exact_substring |
| 2907 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 2932 | seizure free for multiple year | seizure free for 9 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 2938 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 2965 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 2992 | seizure free for multiple year | seizure free for 7 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 3015 | seizure free for multiple year | seizure free for 12 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for multiple year | seizure free for 12 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | evidence_not_exact_substring |
| 3095 | seizure free for multiple year | seizure free for 12 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3113 | seizure free for multiple year | seizure free for 14 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3224 | unknown | 1 cluster per month, 6 to 7 per cluster | no | final_label_repaired: 'monthly clusters, typically 6 to 7 seizures over 24 h' -> 'unknown'; evidence_not_exact_substring |
| 3242 | unknown | 2 cluster per month, 5 per cluster | no | final_label_repaired: '2 clusters per month, each ≈five absences' -> 'unknown'; evidence_not_exact_substring |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month, 4 per cluster' -> '2 cluster per month, 4 per cluster'; evidence_not_exact_substring |
| 3262 | unknown | 2 cluster per month, 5 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown'; evidence_not_exact_substring |
| 3281 | 8 per 30 day | 8 per month | yes | final_label_repaired: '8 per 30 days' -> '8 per 30 day'; evidence_not_exact_substring |
| 3297 | 6 per 30 day | 6 per month | yes | final_label_repaired: '6 per 30 days' -> '6 per 30 day'; evidence_not_exact_substring |
| 3325 | 3 per week | 3 per week | yes | evidence_not_exact_substring |
| 3356 | no seizure frequency reference | unknown | yes | final_label_repaired: 'brief generalised tonic–clonic seizures exclusively after nights of curtailed sleep over the past three months' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 3371 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes |  |
| 3468 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3469 | multiple per month | unknown | yes |  |
| 3482 | unknown | unknown | yes | evidence_not_exact_substring |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 | unknown | unknown | yes | evidence_not_exact_substring |
| 3528 | multiple per day | unknown | yes |  |
| 3532 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 brief morning absences per 3 week' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 3534 | seizure free for 7 month | unknown | no |  |
| 3600 | unknown | unknown | yes |  |
| 3623 | multiple per week | 7 per week | no |  |
| 3643 | 7 per week | 7 per week | yes | evidence_not_exact_substring |
| 3681 | 9 per month | 9 per month | yes | evidence_not_exact_substring |
| 3682 | 6 per month | 6 per month | yes | evidence_not_exact_substring |
| 3710 | 5 per week | 5 per week | yes | evidence_not_exact_substring |
| 3753 | 1 per day | 1 per day | yes | evidence_not_exact_substring |
| 3766 | 8 per year | 8 per year | yes | evidence_not_exact_substring |
| 3774 | 9 per year | 9 per year | yes | evidence_not_exact_substring |
| 3791 | 10 per year | 10 per year | yes | evidence_not_exact_substring |
| 3801 | 9 per month | 9 per month | yes | evidence_not_exact_substring |
| 3806 | 6 per month | 6 per month | yes | evidence_not_exact_substring |
| 3827 | 7 per month | 7 per month | yes | evidence_not_exact_substring |
| 3846 | 2 per day | 2 per day | yes |  |
| 3849 | 3 per day | 3 per day | yes |  |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 | 3 per year | 3 per year | yes | evidence_not_exact_substring |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 | 4 per week | 4 per week | yes |  |
| 3988 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 3995 | 1 per month | 1 per month | yes | final_label_repaired: 'abs monthly' -> '1 per month' |
| 3999 | 1 per month | 1 per month | yes | final_label_repaired: 'abs monthly' -> '1 per month'; evidence_not_exact_substring |
| 4022 | 8 per month | 8 per month | yes | evidence_not_exact_substring |
| 4026 | 1 per month | 1 per month | yes | evidence_not_exact_substring |
| 4092 | 2 to 3 per week | 1 per 2 to 3 week | no |  |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | evidence_not_exact_substring |
| 4110 | 1 to 2 per day | 1 per 1 to 2 day | no | evidence_not_exact_substring |
| 4116 | 1 to 2 per day | 1 per 1 to 2 day | no | evidence_not_exact_substring |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week'; evidence_not_exact_substring |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per 3 week' -> '1 per 2 to 3 week'; evidence_not_exact_substring |
| 4258 | no seizure frequency reference | 4 per week | no | final_label_repaired: '4 per 7' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 4337 | 3 per 3 month | 3 per 3 month | yes | evidence_not_exact_substring |
| 4345 | 4 per month | 4 per month | yes | evidence_not_exact_substring |
| 4368 | 5 per 3 month | 5 per 2 month | yes | evidence_not_exact_substring |
| 4402 | 1 to 2 per month | 7 per 7 month | no | evidence_not_exact_substring |
| 4410 | 1 per month | 4 per 7 month | no | evidence_not_exact_substring |
| 4478 | 19 per week | 19 per week | yes | evidence_not_exact_substring |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes | evidence_not_exact_substring |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | evidence_not_exact_substring |
| 4562 | 2 to 3 per month | 1 per 6 week | no | evidence_not_exact_substring |
| 4563 | 1 per 4 month | 1 per 4 month | yes | evidence_not_exact_substring |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week'; evidence_not_exact_substring |
| 4592 | 2 per month | 1 per 2 month | no | evidence_not_exact_substring |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week'; evidence_not_exact_substring |
| 4624 | no seizure frequency reference | 1 per 3 to 4 day | no | final_label_repaired: '2 focal impaired-awareness events per month' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 4631 | 2 to 3 per month | 1 per 14 to 21 day | yes |  |
| 4690 | unknown | multiple per day | yes | evidence_not_exact_substring |
| 4694 | multiple per day | multiple per day | yes | evidence_not_exact_substring |
| 4700 | multiple per day | multiple per day | yes | evidence_not_exact_substring |
| 4709 | unknown | multiple per day | yes | evidence_not_exact_substring |
| 4731 | no seizure frequency reference | unknown | yes | final_label_repaired: 'rare' -> 'no seizure frequency reference' |
| 4732 | unknown | unknown | yes |  |
| 4771 | 2 to 3 per month | unknown | no | evidence_not_exact_substring |
| 4839 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4951 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for multiple year | seizure free for 11 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4994 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5092 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | evidence_not_exact_substring |
| 5141 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5351 | seizure free for multiple year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5379 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes | evidence_not_exact_substring |
| 5476 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5490 | unknown | unknown | yes | evidence_not_exact_substring |
| 5491 | unknown | unknown | yes | evidence_not_exact_substring |
| 5504 | unknown | unknown | yes |  |
| 5507 | 3 per 4 month | unknown | no | evidence_not_exact_substring |
| 5528 | no seizure frequency reference | 1 per month | no | final_label_repaired: '1 isolated event last month' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 5534 | 1 per 2 week | 1 per multiple month | no | evidence_not_exact_substring |
| 5551 | multiple per day | multiple per day | yes |  |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
