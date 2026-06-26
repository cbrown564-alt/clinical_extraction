# Gan 2026 Hybrid Rules-Candidates LLM Adjudicator

Date: 2026-06-01

This is a validation development artifact unless the split is explicitly `test` and the candidate was frozen before evaluation. It is not a benchmark claim.

## Experiment Unit

Hypothesis: deterministic V1 can serve as a high-recall candidate generator, while an LLM adjudicator proposes semantic selection changes that pass named overreach gates.

Prediction-bearing component: conservative gated adjudicator final label. The raw LLM decision is retained, but deterministic V1 is the fallback when gate checks find unsupported candidate membership, label support, evidence, empty selection, or boundary-demotion overreach.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Escalation reason: validation50 v0.2 was output-contract clean but saturated; validation250 tests whether deterministic-correct regressions persist beyond the prefix and whether raw adjudicator corrections are frequent enough to justify the conservative gated hybrid.

## Model And Prompt Metadata

- Architecture: `hybrid_rules_candidates_llm_adjudicator`
- Claim type: `hybrid_llm_adjudicator`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: final-selection adjudicator
- Prompt/program version: `gan2026_final_selection_adjudicator_v0.5_conservative`
- Temperature: `0.0`
- Max tokens: `1100`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: frozen V1 candidate generator before LLM adjudication.
- Git commit: `812928d`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.jsonl`

## Summary

- Decision records: 250 / 250
- Call failures: 0
- Parse/schema/label issues: 0
- Candidate-set Purist recall proxy: 0.9840 (246 / 250)
- Deterministic top Purist: 0.9840 (246 / 250)
- Deterministic top Pragmatic: 0.9840 (246 / 250)
- Adjudicator Purist: 0.9760 (244 / 250)
- Adjudicator Pragmatic: 0.9800 (245 / 250)
- Changed final labels: 8
- Raw changed final labels before gates: 9
- Deterministic fallbacks after gates: 1
- Overreach gates: {'unsupported_boundary_demotion_overreach': 1}
- Deterministic-wrong to adjudicator-correct: 0
- Deterministic-correct to adjudicator-wrong: 2

## Rows

| Row | Candidate recall | Deterministic | Raw LLM | Gated final | Gold | Det Purist | Gated Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | yes | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | yes | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | yes | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 128 | yes | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | yes | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | yes | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 187 | yes | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | yes | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | yes | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | yes | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 278 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | yes | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes | final_label_repaired: 'many seizures per month' -> 'no seizure frequency reference' |
| 409 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | yes | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | yes | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | yes | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | yes | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | yes | 1 per 8 month | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | yes | 2 per 4 day | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
| 665 | yes | 2 per 2 week | 2 per 2 week | 2 per 2 week | 2 per 2 week | yes | yes |  |
| 678 | yes | 2 per 4 month | 2 per 4 month | 2 per 4 month | 2 per 4 month | yes | yes |  |
| 694 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | yes | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 725 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | yes | no seizure frequency reference | unknown | unknown | multiple per week | yes | yes |  |
| 744 | yes | multiple per week | 1 per 8 week | 1 per 8 week | multiple per week | yes | no |  |
| 763 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 790 | yes | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | yes | 1 per month | 4 per year | 4 per year | 1 per month | yes | no |  |
| 849 | yes | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 854 | yes | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes |  |
| 891 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 899 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | yes | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | yes | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 1070 | yes | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | yes | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | yes | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes |  |
| 1171 | yes | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes |  |
| 1207 | yes | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | yes |  |
| 1223 | yes | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1249 | yes | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1281 | yes | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | yes | yes |  |
| 1317 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown, multiple per cluster | yes | yes |  |
| 1357 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 1363 | yes | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 1413 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 1454 | yes | 7 per week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 1486 | yes | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1573 | yes | 11 per week | 11 per week | 11 per week | 11 per week | yes | yes |  |
| 1591 | yes | 11 per month | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 1596 | yes | 12 per week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1597 | yes | 12 per month | 12 per month | 12 per month | 12 per month | yes | yes |  |
| 1636 | yes | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1640 | yes | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 1687 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 1694 | yes | 1 cluster per 2 week, 3 per cluster | 1 cluster per 2 week, 3 per cluster | 1 cluster per 2 week, 3 per cluster | 1 cluster per 2 week, 3 per cluster | yes | yes |  |
| 1695 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes |  |
| 1706 | yes | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | yes |  |
| 1707 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per week | yes | yes |  |
| 1772 | yes | 11 per 6 month | 11 per 6 month | 11 per 6 month | 11 per 6 month | yes | yes |  |
| 1773 | yes | 11 per 3 month | 11 per 3 month | 11 per 3 month | 11 per 3 month | yes | yes |  |
| 1790 | yes | 8 per 4 month | 8 per 4 month | 8 per 4 month | 8 per 4 month | yes | yes |  |
| 1794 | yes | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1866 | yes | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1880 | yes | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1887 | yes | 4 per 3 month | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes |  |
| 1914 | yes | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1922 | yes | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1923 | yes | 7 per 6 month | 7 per 6 month | 7 per 6 month | 7 per 6 month | yes | yes |  |
| 1979 | yes | 6 per 2 month | 6 per 2 month | 6 per 2 month | 6 per 2 month | yes | yes |  |
| 1980 | yes | 6 per 3 month | 6 per 3 month | 6 per 3 month | 6 per 3 month | yes | yes |  |
| 2023 | yes | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 2080 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per month | yes | yes |  |
| 2094 | yes | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2114 | yes | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2149 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 2166 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 2228 | yes | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | yes |  |
| 2233 | yes | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | yes |  |
| 2245 | yes | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2259 | yes | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | yes |  |
| 2354 | yes | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2366 | yes | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 2369 | yes | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 2374 | yes | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | yes | yes |  |
| 2425 | yes | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | yes | yes |  |
| 2427 | yes | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 2435 | yes | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | yes |  |
| 2437 | yes | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | yes |  |
| 2440 | yes | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | yes |  |
| 2456 | yes | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | yes |  |
| 2459 | yes | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | yes |  |
| 2487 | yes | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes |  |
| 2513 | yes | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | yes |  |
| 2541 | yes | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | yes |  |
| 2548 | yes | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | yes |  |
| 2554 | yes | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | yes |  |
| 2558 | yes | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | yes |  |
| 2609 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2622 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2628 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2678 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2681 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2698 | yes | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 2731 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 2740 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2748 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2759 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2762 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2765 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2776 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2789 | yes | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2812 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2822 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2824 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2877 | yes | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 2887 | yes | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 2907 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 2932 | yes | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | yes | yes |  |
| 2938 | yes | seizure free for 8 month | seizure free for 8 month | seizure free for 8 month | seizure free for 8 month | yes | yes |  |
| 2965 | yes | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 2992 | yes | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 3015 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3048 | yes | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3058 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3082 | yes | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 3095 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3113 | yes | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 3118 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 3137 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 3224 | yes | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | yes |  |
| 3242 | yes | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3261 | yes | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | yes |  |
| 3262 | yes | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3281 | yes | 8 per month | 8 per month | 8 per month | 8 per month | yes | yes |  |
| 3297 | yes | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3325 | yes | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 3356 | no | seizure free for multiple year | unknown | seizure free for multiple year | unknown | no | no | unsupported_boundary_demotion_overreach |
| 3371 | yes | unknown | unknown | unknown | unknown | yes | yes |  |
| 3436 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3468 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3469 | yes | unknown | unknown | unknown | unknown | yes | yes |  |
| 3482 | yes | unknown | unknown | unknown | unknown | yes | yes |  |
| 3493 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 3507 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3512 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3528 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 3532 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3534 | yes | unknown | unknown | unknown | unknown | yes | yes |  |
| 3600 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3623 | yes | 7 per week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 3643 | yes | 7 per week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 3681 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3682 | yes | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3710 | yes | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 3753 | yes | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 3766 | yes | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3774 | yes | 9 per year | 9 per year | 9 per year | 9 per year | yes | yes |  |
| 3791 | yes | 10 per year | 10 per year | 10 per year | 10 per year | yes | yes |  |
| 3801 | yes | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3806 | yes | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3827 | yes | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 3846 | yes | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 3849 | yes | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3889 | yes | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3892 | yes | 3 per year | 3 per year | 3 per year | 3 per year | yes | yes |  |
| 3940 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3949 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3988 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 3995 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 3999 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4022 | yes | 8 per month | 8 per month | 8 per month | 8 per month | yes | yes |  |
| 4026 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4092 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4100 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4110 | yes | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4116 | yes | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4173 | yes | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 4243 | yes | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4258 | yes | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 4337 | yes | 3 per 3 month | 3 per 3 month | 3 per 3 month | 3 per 3 month | yes | yes |  |
| 4345 | yes | 4 per month | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 4368 | yes | 5 per 2 month | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes |  |
| 4402 | yes | 7 per 7 month | 7 per 7 month | 7 per 7 month | 7 per 7 month | yes | yes |  |
| 4410 | yes | 4 per 7 month | 4 per 7 month | 4 per 7 month | 4 per 7 month | yes | yes |  |
| 4478 | yes | 19 per week | 19 per week | 19 per week | 19 per week | yes | yes |  |
| 4480 | yes | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 4496 | yes | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | yes |  |
| 4562 | yes | 1 per 6 week | 1 per 6 week | 1 per 6 week | 1 per 6 week | yes | yes |  |
| 4563 | yes | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 4574 | yes | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 4592 | yes | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 4597 | yes | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 4624 | yes | 1 per 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | yes |  |
| 4631 | yes | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | yes |  |
| 4690 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | multiple per day | no | no |  |
| 4694 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 4700 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 4709 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | multiple per day | yes | yes |  |
| 4731 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 4732 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 4771 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 4839 | yes | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes |  |
| 4842 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4910 | yes | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4919 | yes | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4926 | yes | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 4951 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4956 | yes | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 4992 | yes | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | yes | yes |  |
| 4994 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 5040 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for 6 months | yes | yes |  |
| 5082 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5092 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5110 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5121 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5136 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5141 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5197 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5210 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5221 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5248 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 5331 | yes | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 5345 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5351 | yes | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 5379 | yes | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5406 | yes | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5476 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5490 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 5491 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5504 | yes | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 5507 | yes | no seizure frequency reference | unknown | unknown | unknown | yes | yes |  |
| 5528 | yes | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 5534 | no | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | 1 per multiple month | no | no |  |
| 5551 | yes | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 5567 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5584 | yes | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
