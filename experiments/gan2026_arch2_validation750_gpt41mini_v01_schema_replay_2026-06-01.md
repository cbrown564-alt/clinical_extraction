# Gan 2026 Architecture 2 Candidate Adjudicator

Date: 2026-06-01

This is a validation development artifact unless the split is explicitly `test` and the candidate was frozen before evaluation. It is not a benchmark claim.

## Experiment Unit

Hypothesis: deterministic V1 can serve as a high-recall candidate generator, while an LLM adjudicator makes the prediction-bearing semantic selection.

Prediction-bearing component: LLM final-selection adjudicator over unscored deterministic candidate evidence. Deterministic code generates candidate labels, validates output shape, applies existing label repair, and scores.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Escalation reason: no-call schema replay of full Architecture 2 validation after non-semantic nullable-string and temporality alias repairs

## Model And Prompt Metadata

- Architecture: `architecture_2_deterministic_candidates_llm_adjudicator`
- Claim type: `hybrid_llm_adjudicator`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: final-selection adjudicator
- Prompt/program version: `gan2026_final_selection_adjudicator_v0.4`
- Temperature: `0.0`
- Max tokens: `1100`
- Mode: `live`
- Reused raw model outputs: `750`
- Reuse source: `experiments/gan2026_arch2_validation750_gpt41mini_v01_2026-06-01.jsonl`
- Deterministic rule configuration: frozen V1 candidate generator before LLM adjudication.
- Git commit: `691903d`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_arch2_validation750_gpt41mini_v01_schema_replay_2026-06-01.jsonl`

## Summary

- Decision records: 748 / 750
- Call failures: 0
- Parse/schema/label issues: 2
- Candidate-set Purist recall proxy: 0.9427 (707 / 750)
- Deterministic top Purist: 0.9293 (697 / 750)
- Deterministic top Pragmatic: 0.9387 (704 / 750)
- Adjudicator Purist: 0.9053 (679 / 750)
- Adjudicator Pragmatic: 0.9173 (688 / 750)
- Changed final labels: 43
- Deterministic-wrong to adjudicator-correct: 7
- Deterministic-correct to adjudicator-wrong: 24

## Rows

| Row | Candidate recall | Deterministic | Adjudicator | Gold | Det Purist | Adj Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | yes | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | yes | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | yes | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | yes | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 128 | yes | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | yes | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | yes | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 187 | yes | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | yes | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | yes | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | yes | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 278 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | yes | no seizure frequency reference | unknown | multiple per month | yes | yes |  |
| 409 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | yes | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | yes | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | yes | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | yes | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | yes | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | yes | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | yes | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
| 665 | yes | 2 per 2 week | 2 per 2 week | 2 per 2 week | yes | yes |  |
| 678 | yes | 2 per 4 month | 2 per 4 month | 2 per 4 month | yes | yes |  |
| 694 | yes | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | yes | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 725 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | yes | no seizure frequency reference | no seizure frequency reference | multiple per week | yes | yes |  |
| 744 | yes | multiple per week | 1 per 8 week | multiple per week | yes | no |  |
| 763 | yes | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 790 | yes | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | yes | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 854 | yes | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | yes | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes |  |
| 891 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 899 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | yes | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | yes | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 1070 | yes | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | yes | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | yes | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes |  |
| 1171 | yes | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes |  |
| 1207 | yes | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | yes |  |
| 1223 | yes | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1249 | yes | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1281 | yes | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | yes | yes |  |
| 1317 | yes | no seizure frequency reference | no seizure frequency reference | unknown, multiple per cluster | yes | yes |  |
| 1357 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 1363 | yes | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 1413 | yes | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 1454 | yes | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 1486 | yes | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1573 | yes | 11 per week | 11 per week | 11 per week | yes | yes |  |
| 1591 | yes | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 1596 | yes | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1597 | yes | 12 per month | 12 per month | 12 per month | yes | yes |  |
| 1636 | yes | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1640 | yes | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 1687 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 1694 | yes | 1 cluster per 2 week, 3 per cluster | 1 cluster per 2 week, 3 per cluster | 1 cluster per 2 week, 3 per cluster | yes | yes |  |
| 1695 | yes | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes |  |
| 1706 | yes | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | yes |  |
| 1707 | yes | no seizure frequency reference | no seizure frequency reference | multiple per week | yes | yes |  |
| 1772 | yes | 11 per 6 month | 11 per 6 month | 11 per 6 month | yes | yes |  |
| 1773 | yes | 11 per 3 month | 11 per 3 month | 11 per 3 month | yes | yes |  |
| 1790 | yes | 8 per 4 month | 8 per 4 month | 8 per 4 month | yes | yes |  |
| 1794 | yes | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1866 | yes | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1880 | yes | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1887 | yes | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes |  |
| 1914 | yes | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1922 | yes | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1923 | yes | 7 per 6 month | 7 per 6 month | 7 per 6 month | yes | yes |  |
| 1979 | yes | 6 per 2 month | 6 per 2 month | 6 per 2 month | yes | yes |  |
| 1980 | yes | 6 per 3 month | 6 per 3 month | 6 per 3 month | yes | yes |  |
| 2023 | yes | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 2080 | yes | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes |  |
| 2094 | yes | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2114 | yes | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2149 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 2166 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 2228 | yes | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | yes |  |
| 2233 | yes | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | yes |  |
| 2245 | yes | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2259 | yes | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | yes |  |
| 2354 | yes | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2366 | yes | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 2369 | yes | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 2374 | yes | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | yes | yes |  |
| 2425 | yes | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | yes | yes |  |
| 2427 | yes | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 2435 | yes | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | yes |  |
| 2437 | yes | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | yes |  |
| 2440 | yes | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | yes |  |
| 2456 | yes | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | yes |  |
| 2459 | yes | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | yes |  |
| 2487 | yes | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes |  |
| 2513 | yes | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | yes |  |
| 2541 | yes | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | yes |  |
| 2548 | yes | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | yes |  |
| 2554 | yes | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | yes |  |
| 2558 | yes | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | yes |  |
| 2609 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2622 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2628 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2678 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2681 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2698 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 2731 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 2740 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2748 | yes | 1 per month | 7 per 10 month | 1 per month | yes | no |  |
| 2759 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2762 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2765 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2776 | yes | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2789 | yes | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2812 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2822 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2824 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2877 | yes | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 2887 | yes | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 2907 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 2932 | yes | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | yes | yes |  |
| 2938 | yes | seizure free for 8 month | seizure free for 8 month | seizure free for 8 month | yes | yes |  |
| 2965 | yes | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 2992 | yes | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 3015 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3048 | yes | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3058 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3082 | yes | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 3095 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3113 | yes | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 3118 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 3137 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 3224 | yes | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | yes |  |
| 3242 | yes | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3261 | yes | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | yes |  |
| 3262 | yes | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3281 | yes | 8 per month | 8 per month | 8 per month | yes | yes |  |
| 3297 | yes | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3325 | yes | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 3356 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 3371 | yes | unknown | unknown | unknown | yes | yes |  |
| 3436 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3468 | yes | no seizure frequency reference | unknown | unknown | yes | yes |  |
| 3469 | yes | unknown | unknown | unknown | yes | yes |  |
| 3482 | yes | unknown | unknown | unknown | yes | yes |  |
| 3493 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3507 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3512 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3528 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 3532 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3534 | yes | unknown | 1 per year | unknown | yes | no |  |
| 3600 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3623 | yes | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 3643 | yes | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 3681 | yes | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3682 | yes | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3710 | yes | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 3753 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 3766 | yes | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3774 | yes | 9 per year | 9 per year | 9 per year | yes | yes |  |
| 3791 | yes | 10 per year | 10 per year | 10 per year | yes | yes |  |
| 3801 | yes | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3806 | yes | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3827 | yes | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 3846 | yes | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 3849 | yes | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3889 | yes | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3892 | yes | 3 per year | 3 per year | 3 per year | yes | yes |  |
| 3940 | yes | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3949 | yes | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3988 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 3995 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 3999 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4022 | yes | 8 per month | 8 per month | 8 per month | yes | yes |  |
| 4026 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4092 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4100 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4110 | yes | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4116 | yes | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4173 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 4243 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4258 | yes | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 4337 | yes | 3 per 3 month | 3 per 3 month | 3 per 3 month | yes | yes |  |
| 4345 | yes | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 4368 | yes | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes |  |
| 4402 | yes | 7 per 7 month | 7 per 7 month | 7 per 7 month | yes | yes |  |
| 4410 | yes | 4 per 7 month | 4 per 7 month | 4 per 7 month | yes | yes |  |
| 4478 | yes | 19 per week | 19 per week | 19 per week | yes | yes |  |
| 4480 | yes | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 4496 | yes | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | yes |  |
| 4562 | yes | 1 per 6 week | 1 per 6 week | 1 per 6 week | yes | yes |  |
| 4563 | yes | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 4574 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 4592 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 4597 | yes | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 4624 | yes | 1 per 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | yes |  |
| 4631 | yes | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | yes |  |
| 4690 | no | seizure free for multiple year | seizure free for multiple year | multiple per day | no | no |  |
| 4694 | yes | no seizure frequency reference | unknown | multiple per day | yes | yes |  |
| 4700 | yes | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 4709 | yes | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 4731 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 4732 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 4771 | yes | no seizure frequency reference | unknown | unknown | yes | yes |  |
| 4839 | yes | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes |  |
| 4842 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4910 | yes | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4919 | yes | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4926 | yes | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 4951 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4956 | yes | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 4992 | yes | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | yes | yes |  |
| 4994 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 5040 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 6 months | yes | yes |  |
| 5082 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5092 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5110 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5121 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5136 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5141 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5197 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5210 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5221 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5248 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 5331 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 5345 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5351 | yes | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 5379 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5406 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5476 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5490 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5491 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5504 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5507 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5528 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 5534 | no | seizure free for multiple year | seizure free for multiple year | 1 per multiple month | no | no |  |
| 5551 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 5567 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5584 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5624 | yes | 1 per 10 day | 1 per 10 day | 1 per 10 day | yes | yes |  |
| 5652 | yes | 1 per 8 day | 1 per 8 day | 1 per 8 day | yes | yes |  |
| 5682 | yes | 2 to 4 per month | 2 to 4 per month | 2 to 4 per month | yes | yes |  |
| 5696 | yes | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 5763 | yes | 6 per 3 month | 6 per 3 month | 2 per month | yes | yes |  |
| 5767 | yes | 1 per 1 to 2 week | 1 per 1 to 2 week | 1 per 1 to 2 week | yes | yes |  |
| 5791 | yes | 3 per 3 month | 3 per 3 month | 1 per month | yes | yes |  |
| 5827 | yes | multiple per week | 2 per 8 week | multiple per week | yes | no |  |
| 5837 | yes | 2 cluster per 3 week, multiple per cluster | 2 cluster per 3 week, multiple per cluster | 2 cluster per 3 week, multiple per cluster | yes | yes |  |
| 5866 | yes | 4 per 6 week | 4 per 6 week | 4 per 6 week | yes | yes |  |
| 5873 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5921 | yes | 1 per day | 1 per 6 to 8 week | 1 per 6 to 8 week | no | yes |  |
| 5954 | yes | 3 per week | 2 per week | 2 per week | yes | yes |  |
| 5961 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 5974 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 5977 | yes | multiple per 6 week | multiple per 6 week | unknown | yes | yes |  |
| 5995 | yes | 3 per 9 month | 3 per 9 month | 1 per 3 months | yes | yes |  |
| 5996 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6026 | yes | 3 per 2 month | 3 per 2 month | 3 per 2 month | yes | yes |  |
| 6029 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6034 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6065 | yes | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 6077 | no | seizure free for 8 month | seizure free for 8 month | unknown | no | no |  |
| 6087 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6094 | no | 3 per week | 3 per week | 3 per month | no | no |  |
| 6112 | yes | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 6131 | no | seizure free for 6 month | seizure free for 6 month | unknown | no | no |  |
| 6137 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 week | yes | yes |  |
| 6153 | no | 1 per 1 to 2 week | 3 per 4 week | 9 per month | no | no |  |
| 6180 | yes | no seizure frequency reference | unknown | multiple per week | yes | yes |  |
| 6192 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6204 | yes | 2 per month | 1 per 3 to 4 week | 2 per month | yes | yes |  |
| 6209 | no | 1 per day | 1 per day | multiple per day | no | no |  |
| 6244 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 6251 | yes | 1 per 1 to 2 month | 1 per 1 to 2 month | 1 per 1 to 2 month | yes | yes |  |
| 6273 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6319 | yes | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 6321 | no | 1 per day | unknown | unknown | no | yes |  |
| 6331 | yes | 2 per 6 week | 2 per 6 week | 2 per 6 weeks | yes | yes |  |
| 6358 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 15 to 16 months | yes | yes |  |
| 6368 | no | 1 per 1 to 2 week | 3 per 6 week | unknown | no | no |  |
| 6395 | yes | 1 to 2 per month | 1 to 2 per month | 1 to 2 per month | yes | yes |  |
| 6501 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 6509 | yes | 2 per 2 week | 2 per 2 week | 1 per week | yes | yes |  |
| 6571 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 6607 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6684 | yes | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 6701 | yes | 4 per 3 week | 4 per 3 week | 4 per 3 week | yes | yes |  |
| 6738 | yes | 1 per 6 to 8 week | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | yes |  |
| 6852 | yes | 4 to 6 per month | 4 to 6 per month | 4 to 6 per month | yes | yes |  |
| 6889 | yes | 1 per 2 to 3 week | multiple per week | multiple per week | no | yes |  |
| 6952 | yes | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 6967 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 6987 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 7093 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7126 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7141 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7167 | yes | 3 cluster per 6 week, 2 to 4 per cluster | 3 cluster per 6 week, 2 to 4 per cluster | 1 cluster per 2 weeks, 2 to 4 per cluster | yes | yes |  |
| 7168 | no | 2 per year | 2 per year | unknown | no | no |  |
| 7192 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 7195 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7196 | yes | 6 per 6 week | 6 per 6 week | 1 per week | yes | yes |  |
| 7198 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7275 | yes | 3 per 3 month | 3 per 3 month | 1 per month | yes | yes |  |
| 7290 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7316 | yes | 1 to 2 per month | 1 to 2 per month | 1 to 2 per month | yes | yes |  |
| 7389 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7392 | yes | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 7401 | yes | 2 cluster per 6 week, 1 to 2 per cluster | 2 cluster per 6 week, 1 to 2 per cluster | 2 cluster per 6 week, 1 to 2 per cluster | yes | yes |  |
| 7409 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7455 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7475 | yes | 2 per 6 month | 2 per 6 month | 2 per 6 month | yes | yes |  |
| 7491 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7506 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7573 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 7581 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 7615 | no | 2 per year | 2 per year | 3 to 7 per month | no | no |  |
| 7650 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7738 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7785 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 7818 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 2 years | yes | yes |  |
| 7834 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7859 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 7872 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7911 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 7961 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 8002 | yes | 1 per 6 to 8 week | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | yes |  |
| 8006 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8079 | yes | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 8089 | yes | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 8124 | yes | seizure free for 13 month | seizure free for 13 month | seizure free for 13 month | yes | yes |  |
| 8144 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8145 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month | yes | yes |  |
| 8160 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8180 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8188 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8203 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8224 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8235 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8264 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 4 month | yes | yes |  |
| 8265 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month | yes | yes |  |
| 8354 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8355 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 8400 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8419 | yes | 2 per week | 2 per week | 1 to 2 per week | yes | yes |  |
| 8474 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8512 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8564 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 8577 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8581 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8593 | yes | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 8596 | yes | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | yes | yes |  |
| 8674 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8724 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8730 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month | yes | yes |  |
| 8794 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 6 month | yes | yes |  |
| 8802 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 12 month | yes | yes |  |
| 8805 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8808 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 10 month | yes | yes |  |
| 8820 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 7 month | yes | yes |  |
| 8835 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 10 month | yes | yes |  |
| 8854 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8893 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8922 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8924 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 8938 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 10 month | yes | yes |  |
| 8949 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 8969 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9002 | yes | 7 per year | 7 per year | 7 per year | yes | yes |  |
| 9063 | yes | seizure free for 8 month | seizure free for 8 month | seizure free for 8 month | yes | yes |  |
| 9103 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9163 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9190 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9215 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9238 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9250 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9259 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 1 year | yes | yes |  |
| 9287 | yes | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 9299 | yes | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 9300 | yes | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 9344 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 9365 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 9368 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 9391 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 9397 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 9449 | yes | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 9462 | yes | 7 per 11 month | 7 per 11 month | 7 per 11 month | yes | yes |  |
| 9496 | yes | 2 per week | 2 per week | 6 per 12 month | no | no |  |
| 9547 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9588 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 9704 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9815 | yes | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 9877 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9879 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9888 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 9912 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 9937 | no | 1 per multiple week | 1 per multiple week | 1 cluster per month, multiple per cluster | no | no |  |
| 9943 | no | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | no |  |
| 9955 | no | 1 per month | 1 per month | 1 cluster per month, multiple per cluster | no | no |  |
| 10003 | yes | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | yes |  |
| 10047 | yes | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | yes |  |
| 10063 | yes | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | yes |  |
| 10097 | yes | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | yes | yes |  |
| 10147 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10183 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10189 | yes | no seizure frequency reference | no seizure frequency reference | unknown, 3 to 4 per cluster | yes | yes |  |
| 10200 | yes | no seizure frequency reference | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | yes |  |
| 10237 | yes | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | yes |  |
| 10245 | yes | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | yes | yes |  |
| 10260 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10264 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10266 | no | 1 per 5 day | 1 per 5 day | unknown | no | no |  |
| 10268 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10371 | yes | seizure free for 25 month | seizure free for 25 month | seizure free for multiple year | yes | yes |  |
| 10383 | yes | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | yes |  |
| 10386 | yes | 1 per day | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | no | yes |  |
| 10434 | yes | multiple cluster per week, 2 to 3 per cluster | multiple cluster per week, 2 to 3 per cluster | multiple cluster per week, 2 to 3 per cluster | yes | yes |  |
| 10481 | yes | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | yes |  |
| 10487 | yes | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | yes |  |
| 10509 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10517 | yes | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | yes |  |
| 10542 | yes | no seizure frequency reference | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | yes |  |
| 10578 | yes | unknown, 3 to 4 per cluster | unknown, 3 to 4 per cluster | unknown, 3 to 4 per cluster | yes | yes |  |
| 10583 | yes | unknown, 2 to 3 per cluster | unknown, 2 to 3 per cluster | unknown, 2 to 3 per cluster | yes | yes |  |
| 10594 | yes | unknown, 2 per cluster | unknown, 2 per cluster | unknown, 2 per cluster | yes | yes |  |
| 10618 | no | seizure free for multiple year | unknown | unknown, 4 to 6 per cluster | no | yes |  |
| 10629 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10630 | yes | multiple cluster per 2 week, 5 per cluster | multiple cluster per 2 week, 5 per cluster | multiple cluster per 2 week, 5 per cluster | yes | yes |  |
| 10673 | yes | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | yes |  |
| 10677 | no | 1 per month | 1 per month | 1 cluster per month, multiple per cluster | no | no |  |
| 10753 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 10807 | yes | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | yes |  |
| 10829 | yes | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | yes |  |
| 10862 | yes | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | yes |  |
| 10865 | yes | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | yes |  |
| 10873 | yes | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | yes |  |
| 10894 | yes | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | yes |  |
| 10896 | yes | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | yes |  |
| 10902 | yes | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | yes |  |
| 10933 | yes | 2 to 3 cluster per month, multiple per cluster | 2 to 3 cluster per month, multiple per cluster | 2 to 3 cluster per month, 5 per cluster | yes | yes |  |
| 10942 | yes | 5 per month | 5 per month | 2 cluster per month, 5 per cluster | yes | yes |  |
| 10965 | yes | 2 cluster per month, 4 to 5 per cluster | 2 cluster per month, 4 to 5 per cluster | 2 cluster per month, 4 to 5 per cluster | yes | yes |  |
| 10967 | yes | 3 cluster per month, 4 to 5 per cluster | 3 cluster per month, 4 to 5 per cluster | 3 cluster per month, 4 to 5 per cluster | yes | yes |  |
| 10984 | yes | 3 cluster per month, multiple per cluster | 3 cluster per month, multiple per cluster | 3 cluster per month, 3 to 4 per cluster | yes | yes |  |
| 10996 | no | 1 to 2 cluster per month, multiple per cluster | 1 to 2 cluster per month, multiple per cluster | 1 to 2 cluster per month, 4 per cluster | no | no |  |
| 11002 | yes | 2 to 4 cluster per month, multiple per cluster | 2 to 4 cluster per month, multiple per cluster | 2 to 4 cluster per month, 5 per cluster | yes | yes |  |
| 11035 | yes | 1 per 3 month | 1 per 3 month | 1 cluster per 3 month, 1 per cluster | yes | yes |  |
| 11109 | yes | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 11118 | yes | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | yes |  |
| 11131 | yes | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | yes |  |
| 11197 | yes | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | yes |  |
| 11216 | yes | seizure free for 4 month | seizure free for 4 month | unknown | no | no |  |
| 11254 | yes | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 11259 | yes | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 11262 | yes | unknown | unknown | unknown | yes | yes |  |
| 11272 | yes | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 11282 | yes | unknown | unknown | unknown | yes | yes |  |
| 11337 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 11350 | yes | multiple per week | multiple per week | unknown | yes | yes |  |
| 11380 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 11389 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 11400 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11405 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11408 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11409 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11411 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11434 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11463 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11562 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11585 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11606 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11614 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11632 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11640 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11658 | yes | no seizure frequency reference |  | no seizure frequency reference | yes |  | schema_validation_error: Input should be 'low', 'medium' or 'high' |
| 11681 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11706 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11711 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11728 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11734 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11737 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11752 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11756 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11763 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11804 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11824 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11841 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 11852 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | yes | yes |  |
| 12036 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12041 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12046 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12051 | yes | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 12111 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12127 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12130 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12139 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12145 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 12192 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12218 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12236 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12246 | yes | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | yes | yes |  |
| 12314 | yes | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 12366 | yes | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12378 | yes | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12383 | yes | 4 per day | 4 per day | 4 per day | yes | yes | final_label_repaired: '4 per day and 2 per month' -> '4 per day' |
| 12403 | yes | 2 to 3 per day | 2 to 3 per day | 2 to 3 per day | yes | yes |  |
| 12412 | yes | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 12422 | no | 4 per year | 4 per year | 1 per day | no | no |  |
| 12438 | no | 2 to 3 per year | 2 to 3 per year | 1 per day | no | no |  |
| 12456 | no | 3 per year | 3 per year | 1 per day | no | no |  |
| 12460 | no | 2 per year | 2 per year | 1 per day | no | no |  |
| 12468 | no | 4 per year | 4 per year | 1 per day | no | no |  |
| 12484 | yes | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | yes | yes |  |
| 12502 | yes | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12506 | yes | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12537 | yes | 1 per day | 3 per week | 1 per day | yes | no |  |
| 12548 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12551 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12556 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12562 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12573 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12584 | yes | 1 per week | 1 per 3 month | 1 per week | yes | no |  |
| 12641 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12665 | yes | 5 per day | 1 to 2 per month | 1 per day | yes | no |  |
| 12667 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12676 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12679 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 12749 | yes | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | yes | yes |  |
| 12751 | yes | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 12788 | yes | 6 per 4 month | 6 per 4 month | 6 per 4 month | yes | yes |  |
| 12810 | yes | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes |  |
| 12823 | yes | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 12827 | yes | 5 per 5 month | 5 per 5 month | 5 per 5 month | yes | yes |  |
| 12835 | yes | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 12877 | yes | 10 per 4 month | 10 per 4 month | 10 per 4 month | yes | yes |  |
| 12882 | yes | 7 per 4 month | 7 per 4 month | 7 per 4 month | yes | yes |  |
| 12901 | yes | 8 per 5 month | 8 per 5 month | 8 per 5 month | yes | yes |  |
| 12949 | yes | 9 per 6 month | 9 per 6 month | 9 per 6 month | yes | yes |  |
| 12950 | yes | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 12963 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 12979 | yes | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 13008 | yes | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 13011 | yes | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 13051 | yes | 2 per 8 month | 2 per 8 month | 2 per 8 month | yes | yes |  |
| 13058 | yes | 2 per 7 month | 2 per 7 month | 2 per 7 month | yes | yes |  |
| 13114 | yes | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 13122 | yes | 3 per year | 3 per year | 3 per year | yes | yes |  |
| 13149 | yes | 3 per year | 3 per year | 3 per year | yes | yes |  |
| 13178 | yes | 1 per 6 month | 1 per 6 month | 1 per 6 month | yes | yes |  |
| 13190 | yes | 1 per 5 month | 1 per 5 month | 1 per 5 month | yes | yes |  |
| 13209 | yes | 1 per 4 to 5 week | 1 per 8 month | 1 per 8 month | no | yes |  |
| 13267 | yes | 2 per 5 month | 2 per 5 month | 2 per 5 month | yes | yes |  |
| 13290 | yes | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 13327 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13336 | yes | seizure free for 1.5 year | seizure free for 1.5 year | seizure free for 1.5 year | yes | yes |  |
| 13349 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13385 | yes | seizure free for 1.5 year | seizure free for 1.5 year | seizure free for 1.5 year | yes | yes |  |
| 13450 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 1 year | yes | yes |  |
| 13471 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 5 year | yes | yes |  |
| 13478 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for 1 year | yes | yes |  |
| 13485 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13487 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13513 | yes | seizure free for 1.5 year | seizure free for 1.5 year | seizure free for 1.5 year | yes | yes |  |
| 13574 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13595 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13598 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13608 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 13627 | yes | 64 per 12 month | 64 per 12 month | 64 per 12 month | yes | yes |  |
| 13635 | yes | 2 to 3 per week | 47 per 7 month | 47 per 7 month | yes | yes |  |
| 13711 | yes | 76 per 12 month | 76 per 12 month | 76 per 12 month | yes | yes |  |
| 13721 | yes | 77 per 12 month | 77 per 12 month | 77 per 12 month | yes | yes |  |
| 13732 | yes | 52 per 8 month | 52 per 8 month | 52 per 8 month | yes | yes |  |
| 13843 | no | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 13858 | no | no seizure frequency reference |  | seizure free for multiple month | no |  | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical', 'unclear' or 'mixed' |
| 13889 | no | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 13893 | yes | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 13922 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14002 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14025 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 14029 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14040 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14076 | no | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 14092 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14096 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14137 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14146 | yes | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 14187 | yes | 2 to 3 per month | seizure free for multiple year | 2 to 3 per month | yes | no |  |
| 14214 | yes | 2 to 4 per month | seizure free for multiple year | 2 to 4 per month | yes | no |  |
| 14250 | yes | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 14282 | yes | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 14284 | yes | 2 to 3 per month | 2 to 3 per month | 2 to 3 per month | yes | yes |  |
| 14317 | yes | 4 per 2 month | seizure free for multiple year | 4 per 2 month | yes | no |  |
| 14332 | yes | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes |  |
| 14335 | yes | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | yes |  |
| 14383 | yes | 3 to 4 per 3 month | seizure free for multiple year | 3 to 4 per 3 month | yes | no |  |
| 14454 | yes | 2 per 2 month | seizure free for multiple year | 2 per 2 month | yes | no |  |
| 14524 | yes | 2 per 6 month | 2 per 6 month | 2 per 6 month | yes | yes |  |
| 14530 | yes | 2 per 2 month | 2 per 2 month | 2 per 2 month | yes | yes |  |
| 14540 | yes | 2 per 8 month | 2 per 8 month | 2 per 8 month | yes | yes |  |
| 14562 | yes | 3 per 6 month | seizure free for multiple year | 3 per 6 month | yes | no |  |
| 14567 | yes | 3 per 3 month | 3 per 3 month | 3 per 3 month | yes | yes |  |
| 14581 | yes | 2 per 3 month | seizure free for multiple year | 2 per 3 month | yes | no |  |
| 14587 | yes | 2 per 3 month | 2 per 3 month | 2 per 3 month | yes | yes |  |
| 14592 | yes | 3 per 5 month | 3 per 5 month | 3 per 5 month | yes | yes |  |
| 14611 | yes | 2 per 4 month | seizure free for multiple year | 2 per 4 month | yes | no |  |
| 14628 | yes | 2 per 2 month | 2 per 2 month | 2 per 2 month | yes | yes |  |
| 14635 | yes | 5 per 4 month | seizure free for multiple year | 5 per 4 month | yes | no |  |
| 14645 | yes | 2 per 6 month | seizure free for multiple year | 2 per 6 month | yes | no |  |
| 14662 | yes | 3 per 4 month | 3 per 4 month | 3 per 4 month | yes | yes |  |
| 14672 | yes | 3 per 8 month | seizure free for multiple year | 3 per 8 month | yes | no |  |
| 14706 | yes | 2 per 5 month | 2 per 5 month | 2 per 5 month | yes | yes |  |
| 14765 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 14806 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 14810 | no | 12 per month | seizure free for multiple year | 1 per month | no | no |  |
| 14821 | no | 17 per month | seizure free for multiple year | 1 per month | no | no |  |
| 14872 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 14943 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 14949 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 14965 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 14973 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 15004 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 15012 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 15021 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 15029 | yes | 1 per 3 month | 1 per 3 month | 1 per 3 month | yes | yes |  |
| 15094 | yes | 4 per 13 month | 4 per 13 month | 4 per 13 month | yes | yes |  |
| 15108 | yes | 3 to 4 per 15 month | 3 to 4 per 15 month | 3 to 4 per 15 month | yes | yes |  |
| 15127 | yes | 5 per 13 month | 5 per 13 month | 5 per 13 month | yes | yes |  |
| 15129 | yes | 4 per 15 month | 4 per 15 month | 4 per 15 month | yes | yes |  |
| 15141 | yes | 4 to 5 per 15 month | 4 to 5 per 15 month | 4 to 5 per 15 month | yes | yes |  |
| 15168 | no | seizure free for multiple year | seizure free for multiple year | multiple per 15 month | no | no |  |
| 15193 | no | seizure free for multiple year | seizure free for multiple year | multiple per 13 month | no | no |  |
| 15242 | yes | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | yes |  |
| 15262 | yes | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | yes | yes |  |
| 15267 | yes | 3 per 14 month | 3 per 14 month | 3 per 14 month | yes | yes |  |
| 15306 | yes | 2 to 3 per 15 month | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | yes |  |
| 15317 | yes | 2 to 3 per 15 month | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | yes |  |
| 15376 | yes | 1 cluster per 2 week, 4 to 6 per cluster | 1 cluster per 2 week, 4 to 6 per cluster | 1 cluster per 2 week, 4 to 6 per cluster | yes | yes |  |
| 15404 | yes | 1 cluster per 4 month, 3 to 4 per cluster | 1 cluster per 4 month, 3 to 4 per cluster | 1 cluster per 4 month, 3 to 4 per cluster | yes | yes |  |
| 15429 | yes | 1 cluster per 2 month, 4 per cluster | 1 cluster per 2 month, 4 per cluster | 1 cluster per 2 month, 4 per cluster | yes | yes |  |
| 15431 | yes | 1 cluster per 4 month, 5 per cluster | 1 cluster per 4 month, 5 per cluster | 1 cluster per 4 month, 5 per cluster | yes | yes |  |
| 15442 | yes | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | yes |  |
| 15470 | yes | 1 cluster per 5 day, multiple per cluster | 1 cluster per 5 day, multiple per cluster | 1 cluster per 5 day, multiple per cluster | yes | yes |  |
| 15479 | yes | 1 cluster per 4 to 5 day, 2 per cluster | 1 cluster per 4 to 5 day, 2 per cluster | 1 cluster per 4 to 5 day, 2 per cluster | yes | yes |  |
| 15497 | yes | 1 cluster per 4 to 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | yes | yes |  |
| 15503 | yes | 1 cluster per 5 day, 3 to 4 per cluster | 1 cluster per 5 day, 3 to 4 per cluster | 1 cluster per 5 day, 3 to 4 per cluster | yes | yes |  |
| 15513 | yes | 1 cluster per 4 to 5 day, 2 to 3 per cluster | 1 cluster per 4 to 5 day, 2 to 3 per cluster | 1 cluster per 4 to 5 day, 2 to 3 per cluster | yes | yes |  |
| 15519 | yes | 1 cluster per 4 day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | yes | yes |  |
| 15529 | yes | 1 cluster per 3 day, 4 per cluster | 1 cluster per 3 day, 4 per cluster | 1 cluster per 3 day, 4 per cluster | yes | yes |  |
| 15593 | no | 2 per 6 month | 2 per 6 month | 1 cluster per 5 day, 2 to 4 per cluster | no | no |  |
| 15614 | yes | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 15628 | yes | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 15639 | yes | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 15642 | yes | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 15650 | yes | 3 to 4 per day | 3 to 4 per day | 3 to 4 per day | yes | yes |  |
| 15672 | no | 2 per 6 week | 2 per 6 week | 1 per day | no | no |  |
| 15697 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 15715 | yes | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 15745 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15766 | yes | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 15768 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15771 | yes | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 15772 | yes | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 15774 | yes | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 15783 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 15802 | yes | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 15831 | yes | 2 to 4 per day | 2 to 4 per day | 2 to 4 per day | yes | yes |  |
| 15834 | no | 1 per multiple month | 1 per multiple month | 5 per week | no | no |  |
| 15964 | yes | 11 per 3 month | 11 per 3 month | 11 per 3 month | yes | yes |  |
| 15965 | yes | 13 per 2 month | 13 per 2 month | 13 per 2 month | yes | yes |  |
| 15966 | yes | 5 per 3 month | 5 per 3 month | 5 per 3 month | yes | yes |  |
| 15982 | yes | 9 per 2 month | 9 per 2 month | 9 per 2 month | yes | yes |  |
| 15986 | yes | 1 per 5 to 7 day | 11 per 3 month | 11 per 3 month | no | yes |  |
| 15992 | yes | 7 per 2 month | 7 per 2 month | 7 per 2 month | yes | yes |  |
| 15997 | yes | 10 per 3 month | 10 per 3 month | 10 per 3 month | yes | yes |  |
| 16021 | yes | 9 per 3 month | 9 per 3 month | 9 per 3 month | yes | yes |  |
| 16041 | yes | 9 per 3 month | 9 per 3 month | 9 per 3 month | yes | yes |  |
| 16084 | yes | 8 per 4 month | 8 per 4 month | 8 per 4 month | yes | yes |  |
| 16091 | yes | 3 per 3 month | 3 per 3 month | 3 per 3 month | yes | yes |  |
| 16097 | yes | 17 per 4 month | 17 per 4 month | 17 per 4 month | yes | yes |  |
| 16107 | yes | 8 per 3 month | 8 per 3 month | 8 per 3 month | yes | yes |  |
| 16108 | yes | 12 per 4 month | 12 per 4 month | 12 per 4 month | yes | yes |  |
| 16132 | yes | 15 per 3 month | 15 per 3 month | 15 per 3 month | yes | yes |  |
| 16133 | yes | 18 per 4 month | 18 per 4 month | 18 per 4 month | yes | yes |  |
| 16161 | yes | 18 per 3 month | 18 per 3 month | 18 per 3 month | yes | yes |  |
| 16162 | yes | 11 per 3 month | 11 per 3 month | 11 per 3 month | yes | yes |  |
| 16181 | yes | 15 per 4 month | 15 per 4 month | 15 per 4 month | yes | yes |  |
| 16195 | yes | 16 per 4 month | 16 per 4 month | 16 per 4 month | yes | yes |  |
| 16203 | yes | 9 per 3 month | 9 per 3 month | 9 per 3 month | yes | yes |  |
| 16204 | yes | 5 per 3 month | 5 per 3 month | 5 per 3 month | yes | yes |  |
| 16220 | yes | 11 per 4 month | 11 per 4 month | 11 per 4 month | yes | yes |  |
| 16324 | yes | 10 per 3 month | 10 per 3 month | 10 per 3 month | yes | yes |  |
| 16335 | yes | 6 per 2 month | 6 per 2 month | 7 per 3 month | yes | yes |  |
| 16356 | yes | 1 per 4 day | 1 per 4 day | 1 per 4 day | yes | yes |  |
| 16394 | yes | 1 per 2 to 4 day | 1 per 2 to 4 day | 1 per 2 to 4 day | yes | yes |  |
| 16408 | yes | 1 per 3 day | 1 per 3 day | 1 per 3 day | yes | yes |  |
| 16429 | yes | 1 per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | yes |  |
| 16432 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 16450 | yes | 1 per multiple day | 1 per multiple day | 1 per multiple day | yes | yes |  |
| 16529 | yes | 1 per 5 day | 1 per 5 day | 1 per 5 day | yes | yes |  |
| 16557 | yes | 1 per 2 to 3 day | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | yes |  |
| 16574 | yes | 1 per 4 day | 1 per 4 day | 1 per 4 day | yes | yes |  |
| 16590 | yes | 1 per 4 to 5 day | 1 per 4 to 5 day | 1 per 4 to 5 day | yes | yes |  |
| 16618 | yes | 1 per 5 day | 1 per 5 day | 1 per 5 day | yes | yes |  |
| 16645 | yes | 5 per 7 month | 5 per 7 month | 5 per 7 month | yes | yes |  |
| 16674 | yes | 7 per 6 month | 7 per 6 month | 7 per 6 month | yes | yes |  |
| 16685 | yes | 10 per 3 month | 10 per 3 month | 10 per 3 month | yes | yes |  |
| 16697 | yes | 3 per 6 month | 3 per 6 month | 3 per 6 month | yes | yes |  |
| 16704 | yes | 9 per 6 month | 9 per 6 month | 9 per 6 month | yes | yes |  |
| 16714 | yes | 5 per 6 month | 5 per 6 month | 5 per 6 month | yes | yes |  |
| 16717 | yes | 5 per 6 month | 5 per 6 month | 5 per 6 month | yes | yes |  |
| 16719 | yes | 7 per 6 month | 7 per 6 month | 7 per 6 month | yes | yes |  |
| 16728 | yes | 4 per 6 month | 4 per 6 month | 4 per 6 month | yes | yes |  |
| 16750 | yes | 6 per 7 month | 6 per 7 month | 6 per 7 month | yes | yes |  |
| 16757 | yes | 13 per 6 month | 13 per 6 month | 13 per 6 month | yes | yes |  |
| 16758 | yes | 9 per 5 month | 9 per 5 month | 9 per 5 month | yes | yes |  |
| 16772 | yes | 9 per 5 month | 9 per 5 month | 9 per 5 month | yes | yes |  |
| 16774 | yes | 19 per 7 month | 19 per 7 month | 19 per 7 month | yes | yes |  |
| 16780 | yes | 3 per 7 month | 3 per 7 month | 3 per 7 month | yes | yes |  |
| 16824 | yes | 11 per 5 month | 11 per 5 month | 11 per 5 month | yes | yes |  |
| 16833 | yes | 8 per 6 month | 8 per 6 month | 8 per 6 month | yes | yes |  |
| 16839 | yes | 9 per 4 month | 9 per 4 month | 9 per 4 month | yes | yes |  |
| 16867 | yes | 6 per 7 month | 6 per 7 month | 6 per 7 month | yes | yes |  |
| 16907 | yes | 9 per 6 month | 9 per 6 month | 9 per 6 month | yes | yes |  |
| 16938 | yes | 2 per week | 2 per 2 month | 2 per week | yes | no |  |
| 16947 | yes | 2 per week | 4 per 2 month | 2 per week | yes | no |  |
| 16961 | yes | 2 per week | 3 per 3 month | 2 per week | yes | no |  |
| 16983 | yes | 2 to 3 per week | 2 to 3 per week | 2 to 3 per week | yes | yes |  |
| 16990 | yes | 4 to 5 per week | 4 to 5 per week | 4 to 5 per week | yes | yes |  |
| 17001 | yes | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 17003 | yes | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 17110 | yes | 4 to 5 cluster per week, multiple per cluster | 4 to 5 cluster per week, multiple per cluster | 4 to 5 cluster per week, multiple per cluster | yes | yes |  |
| 17135 | yes | 5 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | yes | yes |  |
| 17146 | yes | 1 per day | 1 per 6 month | 1 per day | yes | no |  |
| 17167 | yes | 1 per week | 1 per 6 month | 1 per week | yes | no |  |
| 17189 | yes | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 17200 | yes | 1 per month | 1 per 6 month | 1 per month | yes | no |  |
| 17201 | yes | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 17273 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 17279 | yes | 1 per 4 to 5 week | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | yes |  |
| 17287 | yes | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
