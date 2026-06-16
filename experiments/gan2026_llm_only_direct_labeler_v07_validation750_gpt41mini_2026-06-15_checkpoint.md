# Gan 2026 LLM-First Validation Run

Date: 2026-06-15

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 600 rows.
Rare full-validation reason: Cycle-3 v0.7 label-binding authorised validation750 live pass after the v0.7 robustness battery cleared Panels A/B/C (verdict transfers).
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only direct-labeler note-to-label extractor
- Prompt/program version: `gan2026_llm_only_direct_labeler_v0.7`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `600`
- Reuse source: `C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `af23a16a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `C:/Users/cbrow/Code/clinical_extraction/experiments/gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15.jsonl`

## Summary

- Decision records: 600 / 600
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 104
- Exact evidence substrings: 539 / 600
- Purist validation accuracy/micro F1 proxy: 0.6950 (417 / 600)
- Pragmatic validation accuracy/micro F1 proxy: 0.7233 (434 / 600)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'multiple per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes |  |
| 79 | unknown | 6 to 7 per year | no |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | unknown | 17 per month | no | v0_7_binding_coerce_no_rate: answer_kind='unknown' -> 'unknown' (was '17 per month') |
| 156 | 1 per 6 day | 1 per 6 day | yes |  |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 cluster per week, multiple per cluster | 1 per 7 to 9 day | no | final_label_repaired: '1 cluster per 1 week, multiple per cluster' -> '1 cluster per week, multiple per cluster' |
| 190 | 1 cluster per 4 week, multiple per cluster | 1 per 4 week | no | evidence_not_exact_substring |
| 198 | 1 per 4 week | 1 per 4 week | yes |  |
| 212 | unknown | 1 per 3 to 4 week | no |  |
| 218 | 1 per 3 week | 1 per 3 week | yes |  |
| 243 | 1 per 4 month | 1 per 4 month | yes | evidence_not_exact_substring |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | unknown | multiple per day | yes |  |
| 338 | unknown | multiple per month | yes |  |
| 409 | 1 per month | 1 per month | yes |  |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | unknown | 12 to 30 per 3 month | no |  |
| 598 | unknown | 1 per 8 month | no |  |
| 659 | unknown | 2 per 4 day | no | evidence_not_exact_substring |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per month' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes |  |
| 694 | unknown | 1 per week | no |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 731 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 743 | unknown | multiple per week | yes | evidence_not_exact_substring |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 2 to 3 per month | 1 per 7 to 10 day | yes |  |
| 816 | 4 per year | 1 per month | no |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | unknown | 1 per year | no | v0_7_binding_coerce_no_rate: answer_kind='unknown' -> 'unknown' (was '1 per year') |
| 869 | unknown | multiple per month | yes |  |
| 891 | unknown | 1 per 2 day | no |  |
| 899 | 1 per 2 week | 1 per 2 week | yes |  |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 987 | unknown | 1 per 2 month | no |  |
| 1030 | unknown | 1 to 3 per month | no |  |
| 1046 | unknown | 3 to 5 per month | no |  |
| 1070 | unknown | 3 to 4 per week | no | evidence_not_exact_substring |
| 1094 | unknown | 3 to 5 per week | no |  |
| 1165 | unknown | 5 to 7 per 3 week | no |  |
| 1171 | unknown | 7 to 9 per 3 week | no |  |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes | evidence_not_exact_substring |
| 1223 | unknown | 3 to 4 per week | no | evidence_not_exact_substring |
| 1249 | unknown | 2 to 4 per week | no |  |
| 1281 | 5 to 7 per year | 5 to 7 per year | yes |  |
| 1317 | unknown | unknown, multiple per cluster | yes | evidence_not_exact_substring |
| 1357 | unknown | 1 per day | no |  |
| 1363 | unknown | 3 per day | no |  |
| 1413 | 9 per month | 9 per month | yes | final_label_repaired: '2 to 3 per week' -> '9 per month' |
| 1454 | 7 per week | 7 per week | yes | final_label_repaired: '1 tonic-clonic and 6 petit mal per week' -> '7 per week' |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '2 to 3 per month' -> '2 per month' |
| 1573 | unknown | 11 per week | no |  |
| 1591 | unknown | 11 per month | no |  |
| 1596 | 12 per week | 12 per week | yes | final_label_repaired: 'multiple per week' -> '12 per week' |
| 1597 | unknown | 12 per month | no |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | unknown | 5 per week | no |  |
| 1687 | unknown | multiple per week | yes |  |
| 1694 | unknown | 1 cluster per 2 week, 3 per cluster | no |  |
| 1695 | unknown | multiple per month | yes |  |
| 1706 | unknown | multiple cluster per month, multiple per cluster | no |  |
| 1707 | unknown | multiple per week | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '2 to 3 per month' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '3 to 4 per month' -> '11 per 3 month' |
| 1790 | 1 cluster per month, multiple per cluster | 8 per 4 month | yes |  |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '4 per month' -> '8 per 2 month' |
| 1866 | unknown | 8 per 2 month | no |  |
| 1880 | 1 cluster per month, multiple per cluster | 8 per 2 month | no |  |
| 1887 | unknown | 4 per 3 month | no | evidence_not_exact_substring |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '1 to 2 per month' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '6 per 2 month' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '2 per month' -> '6 per 3 month' |
| 2023 | unknown | 5 per month | no |  |
| 2080 | unknown | multiple per month | yes |  |
| 2094 | unknown | multiple per month | yes | evidence_not_exact_substring |
| 2114 | unknown | multiple per month | yes |  |
| 2149 | unknown | unknown | yes |  |
| 2166 | unknown | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '2 to 3 per week' -> '3 to 5 per 2 week' |
| 2233 | unknown | 6 to 7 per 2 month | no |  |
| 2245 | unknown | 7 to 8 per 3 week | no | evidence_not_exact_substring |
| 2259 | unknown | 6 to 8 per 3 month | no |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | unknown | 3 to 4 per month | no |  |
| 2374 | unknown | 7 to 9 per month | no |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 2427 | unknown | 3 to 5 per month | no |  |
| 2435 | unknown | 5 to 7 per 2 week | no | evidence_not_exact_substring |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes |  |
| 2440 | unknown | 5 to 7 per 2 month | no |  |
| 2456 | unknown | 6 to 7 per 2 week | no | v0_7_binding_coerce_no_rate: answer_kind='unknown' -> 'unknown' (was '6 to 7 per 2 week') |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | final_label_repaired: 'multiple per week' -> '7 to 9 per 2 week' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes |  |
| 2513 | unknown | 2 to 3 per 2 week | no | evidence_not_exact_substring |
| 2541 | 4 to 5 per week | 8 to 9 per 2 week | yes |  |
| 2548 | unknown | 5 to 6 per 2 month | no |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes |  |
| 2558 | 2 to 3 per month | 3 to 4 per 2 month | yes |  |
| 2609 | 1 per day | 1 per day | yes |  |
| 2622 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes |  |
| 2681 | unknown | 1 per day | no |  |
| 2698 | unknown | 1 per 2 day | no |  |
| 2731 | 1 per 2 week | 1 per 2 week | yes |  |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 1 per month | 1 per month | yes |  |
| 2759 | 1 per month | 1 per month | yes | evidence_not_exact_substring |
| 2762 | 2 to 3 per month | 1 per month | no |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes |  |
| 2812 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2822 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2824 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | seizure free for 9 month | seizure free for 9 month | yes |  |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 2965 | seizure free for 18 month | seizure free for 16 month | yes |  |
| 2992 | seizure free for 7 month | seizure free for 7 month | yes | evidence_not_exact_substring |
| 3015 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3224 | 1 cluster per month, multiple per cluster | 1 cluster per month, 6 to 7 per cluster | no |  |
| 3242 | 1 cluster per 2 week, multiple per cluster | 2 cluster per month, 5 per cluster | yes |  |
| 3261 | 1 cluster per month, multiple per cluster | 2 cluster per month, 4 per cluster | no |  |
| 3262 | 2 clusters per month, multiple per cluster | 2 cluster per month, 5 per cluster | no |  |
| 3281 | unknown | 8 per month | no |  |
| 3297 | unknown | 6 per month | no |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | unknown | unknown | yes |  |
| 3371 | unknown | unknown | yes |  |
| 3436 | unknown | unknown | yes |  |
| 3468 | 1 cluster per month, multiple per cluster | unknown | no |  |
| 3469 | unknown | unknown | yes |  |
| 3482 | unknown | unknown | yes |  |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 | unknown | unknown | yes |  |
| 3528 | unknown | unknown | yes |  |
| 3532 | unknown | unknown | yes | evidence_not_exact_substring |
| 3534 | seizure free for 7 month | unknown | no |  |
| 3600 | unknown | unknown | yes |  |
| 3623 | unknown | 7 per week | no |  |
| 3643 | unknown | 7 per week | no |  |
| 3681 | 9 per month | 9 per month | yes |  |
| 3682 | 6 per month | 6 per month | yes |  |
| 3710 | 5 per week | 5 per week | yes |  |
| 3753 | 1 per day | 1 per day | yes |  |
| 3766 | 8 per year | 8 per year | yes |  |
| 3774 | 9 per year | 9 per year | yes |  |
| 3791 | 10 per year | 10 per year | yes |  |
| 3801 | unknown | 9 per month | no | v0_7_binding_coerce_no_rate: answer_kind='unknown' -> 'unknown' (was '9 per month') |
| 3806 | 6 per month | 6 per month | yes |  |
| 3827 | 1 cluster per month, multiple per cluster | 7 per month | no |  |
| 3846 | multiple per day | 2 per day | no |  |
| 3849 | multiple per day | 3 per day | no |  |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 | 3 per year | 3 per year | yes |  |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 | 4 per week | 4 per week | yes |  |
| 3988 | unknown | multiple per week | yes | evidence_not_exact_substring |
| 3995 | unknown | 1 per month | no |  |
| 3999 | 2 to 3 per month | 1 per month | no |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 cluster per 2 to 3 week, multiple per cluster | 1 per 2 to 3 week | yes |  |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: 'multiple per day' -> '1 per 1 to 2 day' |
| 4173 | 1 cluster per 2 week, multiple per cluster | 1 per 2 week | no |  |
| 4243 | 2 to 3 per week | 1 per 2 to 3 week | no |  |
| 4258 | 4 per 2 week | 4 per week | yes | final_label_repaired: '4 per week' -> '4 per 2 week' |
| 4337 | unknown | 3 per 3 month | no |  |
| 4345 | unknown | 4 per month | no | evidence_not_exact_substring |
| 4368 | unknown | 5 per 2 month | no |  |
| 4402 | unknown | 7 per 7 month | no |  |
| 4410 | 4 per 7 month | 4 per 7 month | yes | final_label_repaired: '2 to 3 per month' -> '4 per 7 month' |
| 4478 | unknown | 19 per week | no | evidence_not_exact_substring |
| 4480 | unknown | 3 to 5 per week | no |  |
| 4496 | unknown | 7 to 8 per 3 month | no |  |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '2 per month' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '2 to 3 per year' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '2 to 3 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes |  |
| 4624 | 1 cluster per 3 to 4 day, multiple per cluster | 1 per 3 to 4 day | yes |  |
| 4631 | 2 to 3 per month | 1 per 14 to 21 day | yes |  |
| 4690 | unknown | multiple per day | yes | evidence_not_exact_substring |
| 4694 | unknown | multiple per day | yes |  |
| 4700 | unknown | multiple per day | yes |  |
| 4709 | unknown | multiple per day | yes |  |
| 4731 | unknown | unknown | yes |  |
| 4732 | unknown | unknown | yes |  |
| 4771 | unknown | unknown | yes | evidence_not_exact_substring |
| 4839 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4910 | seizure free for 24 month | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 12 month | seizure free for 1 year | yes |  |
| 4951 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for multiple year | seizure free for 6 months | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5092 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes |  |
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
| 5490 | unknown | unknown | yes |  |
| 5491 | unknown | unknown | yes | evidence_not_exact_substring |
| 5504 | unknown | unknown | yes |  |
| 5507 | unknown | unknown | yes |  |
| 5528 | unknown | 1 per month | no |  |
| 5534 | unknown | 1 per multiple month | yes |  |
| 5551 | multiple per day | multiple per day | yes |  |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | unknown | multiple per week | yes | v0_7_binding_coerce_no_rate: answer_kind='unknown' -> 'unknown' (was 'several per week') |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '3 per month' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per week' -> '1 per 8 day' |
| 5682 | unknown | 2 to 4 per month | no |  |
| 5696 | unknown | 3 per 4 month | no |  |
| 5763 | unknown | 2 per month | no |  |
| 5767 | unknown | 1 per 1 to 2 week | no |  |
| 5791 | unknown | 1 per month | no |  |
| 5827 | multiple per day | multiple per week | yes |  |
| 5837 | unknown | 2 cluster per 3 week, multiple per cluster | no |  |
| 5866 | unknown | 4 per 6 week | no |  |
| 5873 | 1 cluster per month, multiple per cluster | multiple per week | no | evidence_not_exact_substring |
| 5921 | 1 cluster per 6 to 8 week, multiple per cluster | 1 per 6 to 8 week | no |  |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 5974 | unknown | unknown | yes | evidence_not_exact_substring |
| 5977 | unknown | unknown | yes |  |
| 5995 | unknown | 1 per 3 months | no |  |
| 5996 | unknown | unknown | yes |  |
| 6026 | unknown | 3 per 2 month | no | evidence_not_exact_substring |
| 6029 | unknown | unknown | yes |  |
| 6034 | unknown | unknown | yes |  |
| 6065 | unknown | 5 per month | no |  |
| 6077 | unknown | unknown | yes | evidence_not_exact_substring |
| 6087 | unknown | unknown | yes |  |
| 6094 | unknown | 3 per month | no |  |
| 6112 | unknown | 3 to 5 per month | no |  |
| 6131 | seizure free for 12 month | unknown | no |  |
| 6137 | unknown | 1 per 2 week | no |  |
| 6153 | unknown | 9 per month | no |  |
| 6180 | unknown | multiple per week | yes |  |
| 6192 | no seizure frequency reference | unknown | yes |  |
| 6204 | unknown | 2 per month | no |  |
| 6209 | multiple per day | multiple per day | yes |  |
| 6244 | unknown | unknown | yes |  |
| 6251 | unknown | 1 per 1 to 2 month | no |  |
| 6273 | unknown | unknown | yes |  |
| 6319 | unknown | 1 per week | no |  |
| 6321 | unknown | unknown | yes |  |
| 6331 | unknown | 2 per 6 weeks | no |  |
| 6358 | seizure free for 4 month | seizure free for 15 to 16 months | yes |  |
| 6368 | unknown | unknown | yes |  |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | 1 cluster per 3 week, multiple per cluster | unknown | no |  |
| 6509 | 1 cluster per 2 week, multiple per cluster | 1 per week | yes |  |
| 6571 | unknown | unknown | yes | evidence_not_exact_substring |
| 6607 | unknown | unknown | yes |  |
| 6684 | unknown | 3 per 4 month | no |  |
| 6701 | unknown | 4 per 3 week | no |  |
| 6738 | 2 to 3 per 2 month | 1 per 6 to 8 week | no |  |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | unknown | multiple per week | yes | v0_7_binding_coerce_no_rate: answer_kind='unknown' -> 'unknown' (was 'seizure free for multiple month') |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes |  |
| 6987 | unknown | unknown | yes |  |
| 7093 | unknown | unknown | yes |  |
| 7126 | unknown | unknown | yes |  |
| 7141 | unknown | unknown | yes |  |
| 7167 | 1 cluster per 2 week, multiple per cluster | 1 cluster per 2 weeks, 2 to 4 per cluster | yes |  |
| 7168 | unknown | unknown | yes |  |
| 7192 | unknown | multiple per week | yes |  |
| 7195 | unknown | unknown | yes |  |
| 7196 | 1 cluster per 6 week, multiple per cluster | 1 per week | no |  |
| 7198 | unknown | unknown | yes |  |
| 7275 | unknown | 1 per month | no |  |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no |  |
| 7409 | 2 to 3 per week | unknown | no |  |
| 7455 | unknown | unknown | yes |  |
| 7475 | unknown | 2 per 6 month | no | evidence_not_exact_substring |
| 7491 | unknown | unknown | yes |  |
| 7506 | unknown | unknown | yes |  |
| 7573 | unknown | 1 per 2 week | no |  |
| 7581 | unknown | 2 to 3 per week | no |  |
| 7615 | 3 to 6 per month | 3 to 7 per month | yes | final_label_repaired: '3 to 6 per 5 days per cycle' -> '3 to 6 per month' |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 7818 | seizure free for 21 month | seizure free for 2 years | yes |  |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 7859 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 7911 | no seizure frequency reference | seizure free for multiple month | no |  |
| 7961 | seizure free for 24 month | seizure free for multiple year | yes |  |
| 8002 | unknown | 1 per 6 to 8 week | no |  |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8079 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 8089 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes |  |
| 8144 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8160 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8180 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8188 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes |  |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8354 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8355 | seizure free for 12 month | seizure free for multiple year | yes | evidence_not_exact_substring |
| 8400 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8419 | unknown | 1 to 2 per week | no |  |
| 8474 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8577 | seizure free for 18 month | seizure free for multiple month | yes |  |
| 8581 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes | evidence_not_exact_substring |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes | evidence_not_exact_substring |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8808 | 0 per 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 month' -> '0 per 10 month'; evidence_not_exact_substring |
| 8820 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 8835 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 8854 | seizure free for 8 month | seizure free for multiple month | yes |  |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes | evidence_not_exact_substring |
| 8922 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8924 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 8938 | seizure free for 10 month | seizure free for 10 month | yes | evidence_not_exact_substring |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9002 | seizure free for multiple year | 7 per year | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 9063 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 9103 | unknown | unknown | yes |  |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 9190 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9215 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 9238 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 9250 | unknown | seizure free for multiple month | no |  |
| 9259 | no seizure frequency reference | seizure free for 1 year | no |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | unknown | multiple per day | yes |  |
| 9365 | unknown | 1 per 2 day | no |  |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 2 to 3 per month | 1 per month | no |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '2 per month' -> '4 per 6 month' |
| 9462 | 7 per 11 month | 7 per 11 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 11 month' |
| 9496 | unknown | 6 per 12 month | no |  |
| 9547 | unknown | unknown | yes |  |
| 9588 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9704 | unknown | unknown | yes |  |
| 9815 | multiple per day | multiple per day | yes |  |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes |  |
| 9888 | unknown | unknown | yes |  |
| 9912 | unknown | unknown | yes |  |
| 9937 | 1 cluster per 3 week, multiple per cluster | 1 cluster per month, multiple per cluster | yes |  |
| 9943 | 1 cluster per 4 to 5 week, multiple per cluster | 1 cluster per 4 to 5 week, multiple per cluster | yes |  |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes |  |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes |  |
| 10047 | 1 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | no |  |
| 10063 | 1 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | no |  |
| 10097 | 1 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | no |  |
| 10147 | unknown | unknown | yes |  |
| 10183 | unknown | unknown | yes |  |
| 10189 | 1 cluster per multiple week, multiple per cluster | unknown, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per several weeks, multiple per cluster' -> '1 cluster per multiple week, multiple per cluster' |
| 10200 | unknown | unknown, 2 to 4 per cluster | yes |  |
| 10237 | 1 cluster per week, multiple per cluster | 4 cluster per month, multiple per cluster | yes |  |
| 10245 | unknown | 3 cluster per month, multiple per cluster | no |  |
| 10260 | unknown | unknown | yes | evidence_not_exact_substring |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes | evidence_not_exact_substring |
| 10371 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 10383 | 1 cluster per week, multiple per cluster | 1 cluster per week, 5 per cluster | yes |  |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes |  |
| 10434 | multiple per week | multiple cluster per week, 2 to 3 per cluster | no |  |
| 10481 | 1 cluster per week, multiple per cluster | 4 cluster per month, multiple per cluster | yes |  |
| 10487 | unknown | 4 cluster per month, multiple per cluster | no |  |
| 10509 | 1 cluster per week, multiple per cluster | unknown | no | evidence_not_exact_substring |
| 10517 | 1 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | no |  |
| 10542 | unknown | unknown, 2 to 4 per cluster | yes |  |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10583 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes |  |
| 10618 | 1 cluster per 2 week, multiple per cluster | unknown, 4 to 6 per cluster | no |  |
| 10629 | unknown | unknown | yes |  |
| 10630 | unknown | multiple cluster per 2 week, 5 per cluster | no | evidence_not_exact_substring |
| 10673 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes |  |
| 10753 | unknown | unknown | yes |  |
| 10807 | 1 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | no |  |
| 10829 | unknown | 2 cluster per month, multiple per cluster | no |  |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes |  |
| 10865 | unknown | 1 cluster per week, multiple per cluster | no |  |
| 10873 | unknown | 1 cluster per week, 6 per cluster | no |  |
| 10894 | 1 cluster per week, multiple per cluster | 1 cluster per week, 4 per cluster | yes |  |
| 10896 | 1 cluster per week, multiple per cluster | 1 cluster per week, 3 to 4 per cluster | yes |  |
| 10902 | 1 cluster per week, multiple per cluster | 1 cluster per week, 4 per cluster | yes |  |
| 10933 | 1 cluster per week, multiple per cluster | 2 to 3 cluster per month, 5 per cluster | yes |  |
| 10942 | 1 cluster per 2 week, multiple per cluster | 2 cluster per month, 5 per cluster | yes |  |
| 10965 | 1 cluster per week, multiple per cluster | 2 cluster per month, 4 to 5 per cluster | yes |  |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | evidence_not_exact_substring |
| 10984 | unknown | 3 cluster per month, 3 to 4 per cluster | no |  |
| 10996 | 1 cluster per month, multiple per cluster | 1 to 2 cluster per month, 4 per cluster | no |  |
| 11002 | 1 cluster per 2 week, multiple per cluster | 2 to 4 cluster per month, 5 per cluster | yes |  |
| 11035 | 1 cluster per 3 month, multiple per cluster | 1 cluster per 3 month, 1 per cluster | yes |  |
| 11109 | unknown | 2 cluster per month, 5 per cluster | no |  |
| 11118 | 1 cluster per 2 week, multiple per cluster | 2 cluster per month, 6 per cluster | yes |  |
| 11131 | 1 cluster per 2 week, multiple per cluster | 2 cluster per month, 3 to 4 per cluster | yes |  |
| 11197 | 1 cluster per month, multiple per cluster | 1 cluster per month, 4 to 6 per cluster | no |  |
| 11216 | seizure free for 4 month | unknown | no | evidence_not_exact_substring |
| 11254 | seizure free for 3 month | unknown | no |  |
| 11259 | unknown | unknown | yes |  |
| 11262 | unknown | unknown | yes |  |
| 11272 | seizure free for 3 month | unknown | no |  |
| 11282 | seizure free for 3 month | unknown | no |  |
| 11337 | unknown | unknown | yes |  |
| 11350 | 1 cluster per week, multiple per cluster | unknown | no | evidence_not_exact_substring |
| 11380 | unknown | unknown | yes |  |
| 11389 | unknown | unknown | yes |  |
| 11400 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11409 | unknown | no seizure frequency reference | yes |  |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11737 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11824 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 12036 | multiple per day | multiple per day | yes |  |
| 12041 | multiple per day | multiple per day | yes |  |
| 12046 | multiple per day | multiple per day | yes |  |
| 12051 | unknown | multiple per day | yes |  |
| 12111 | unknown | multiple per week | yes |  |
| 12127 | 2 per year | multiple per week | no |  |
| 12130 | unknown | multiple per week | yes |  |
| 12139 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12145 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12192 | multiple per day | 1 per day | no |  |
| 12218 | multiple per day | 1 per day | no |  |
| 12236 | multiple per day | 1 per day | no |  |
| 12246 | multiple per day | 1 to 2 per day | no |  |
| 12314 | 3 per week | 3 per week | yes |  |
| 12366 | 4 per day | 4 per day | yes |  |
| 12378 | 4 per day | 4 per day | yes |  |
| 12383 | 4 per day | 4 per day | yes |  |
| 12403 | multiple per day | 2 to 3 per day | no |  |
| 12412 | multiple per day | 2 per day | no |  |
| 12422 | 1 per day | 1 per day | yes |  |
| 12438 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12456 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12460 | 1 per day | 1 per day | yes |  |
| 12468 | 1 per day | 1 per day | yes | final_label_repaired: '4 per year' -> '1 per day' |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12502 | 4 per day | 4 per day | yes |  |
| 12506 | 4 per day | 4 per day | yes |  |
| 12537 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12548 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12556 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12562 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12573 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12584 | 1 per 3 month | 1 per week | no |  |
| 12641 | unknown | 1 per day | no |  |
| 12665 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_exact_substring |
| 12667 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12676 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12679 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | 4 per day | 4 per day | yes |  |
| 12788 | unknown | 6 per 4 month | no |  |
| 12810 | unknown | 5 per 2 month | no |  |
| 12823 | 1 per 3 to 4 week | 9 per month | no |  |
| 12827 | unknown | 5 per 5 month | no |  |
| 12835 | 4 per year | 4 per month | no |  |
| 12877 | unknown | 10 per 4 month | no |  |
| 12882 | 2 per month | 7 per 4 month | yes |  |
| 12901 | unknown | 8 per 5 month | no |  |
| 12949 | unknown | 9 per 6 month | no |  |
| 12950 | unknown | 7 per 3 month | no |  |
| 12963 | seizure free for 2 month | unknown | no |  |
| 12979 | 3 per year | 3 per 4 month | yes |  |
| 13008 | unknown | 4 per month | no |  |
| 13011 | unknown | 3 per 4 month | no |  |
| 13051 | unknown | 2 per 8 month | no |  |
| 13058 | unknown | 2 per 7 month | no |  |
| 13114 | unknown | 1 per year | no |  |
| 13122 | unknown | 3 per year | no | evidence_not_exact_substring |
| 13149 | unknown | 3 per year | no |  |
| 13178 | seizure free for 6 month | 1 per 6 month | no |  |
| 13190 | unknown | 1 per 5 month | no | evidence_not_exact_substring |
| 13209 | unknown | 1 per 8 month | no |  |
| 13267 | unknown | 2 per 5 month | no |  |
| 13290 | unknown | 4 per 6 month | no | evidence_not_exact_substring |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several year' -> 'seizure free for multiple year' |
| 13336 | seizure free for 18 month | seizure free for 1.5 year | yes |  |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 13385 | seizure free for 18 month | seizure free for 1.5 year | yes |  |
| 13450 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 13471 | seizure free for 5 year | seizure free for 5 year | yes |  |
| 13478 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 13513 | seizure free for 18 month | seizure free for 1.5 year | yes |  |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13627 | unknown | 64 per 12 month | no |  |
| 13635 | 1 cluster per month, multiple per cluster | 47 per 7 month | no |  |
| 13711 | 76 per 12 month | 76 per 12 month | yes | final_label_repaired: '2 to 3 per month' -> '76 per 12 month' |
| 13721 | unknown | 77 per 12 month | no |  |
| 13732 | unknown | 52 per 8 month | no |  |
| 13843 | no seizure frequency reference | seizure free for multiple month | no |  |
| 13858 | no seizure frequency reference | seizure free for multiple month | no |  |
| 13889 | unknown | seizure free for multiple month | no |  |
| 13893 | unknown | 2 per year | no |  |
| 13922 | unknown | unknown | yes |  |
| 14002 | unknown | unknown | yes |  |
| 14025 | unknown | unknown | yes |  |
| 14029 | unknown | unknown | yes |  |
| 14040 | unknown | unknown | yes |  |
| 14076 | unknown | unknown | yes |  |
| 14092 | unknown | unknown | yes | evidence_not_exact_substring |
| 14096 | unknown | unknown | yes |  |
| 14137 | 3 to 4 per 3 month | unknown | no |  |
| 14146 | unknown | unknown | yes |  |
| 14187 | seizure free for 1 month | 2 to 3 per month | no |  |
| 14214 | seizure free for 1 month | 2 to 4 per month | no |  |
| 14250 | unknown | 2 per month | no |  |
| 14282 | unknown | multiple per month | yes |  |
