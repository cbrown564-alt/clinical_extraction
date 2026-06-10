# Gan 2026 LLM-Only Canonical-Pipeline Validation Run

Date: 2026-06-10

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that collapses extract/select/normalize/project/render into one pass, with the now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing — can produce a directly scorable, fully rendered label without any deterministic normalization or projection stage downstream.

Minimal change: add an `llm_only_canonical_pipeline` runner alongside (not replacing) `llm_only_direct_labeler` and `hybrid_structured_events`. No deterministic `CandidateSet` is built or consumed; final_label is the model's directly rendered answer.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-chat`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only canonical-pipeline single-shot extract/select/normalize/project/render extractor
- Prompt/program version: `gan2026_llm_only_canonical_pipeline_v0.7`
- Temperature: `0.0`
- Max tokens: `2400`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-10T07:45:30.148621+00:00`
- Run finished UTC: `2026-06-10T07:55:50.557701+00:00`
- Wall-clock elapsed: `620.409` seconds (`10.34` minutes)
- Throughput: `0.40296` rows/sec (`2.482` sec/row)
- Optimizer: none
- Deterministic rule configuration: none as pre/post processing; the deterministic/hybrid rule taxonomy is embedded as prompt instructions only, and deterministic code is limited to label repair, evidence text-containment checking, and scoring.
- Git commit: `facfd07`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v07_validation250_llm_only_canonical_pipeline_deepseek_2026-06-10.jsonl`

## Summary

- Decision records: 250 / 250
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 107
- Evidence text-containment (free-text evidence found verbatim in note, the comparator-appropriate metric in place of `CandidateSet` source-id validity rate): 242 / 250 (0.9680)
- Purist validation accuracy/micro F1 proxy: 0.9320 (233 / 250)
- Pragmatic validation accuracy/micro F1 proxy: 0.9360 (234 / 250)

## Applied Rule-Taxonomy Families (Self-Reported)

These counts reflect which embedded rule-taxonomy families the model itself reported as shaping its answer (`applied_rule_families`); they are a prompt-compliance signal, not a verified trace.

- `cluster_axis_ambiguity`: 5
- `cluster_cadence_as_event_rate`: 14
- `concrete_frequency_precedence`: 39
- `conditional_only_trigger`: 26
- `conditional_only_trigger and relative_only_trend`: 3
- `denominator_window_mismatch`: 70
- `dominant_vague_current_burden`: 4
- `multiple_current_primary_facts`: 2
- `relative_only_trend`: 3
- `same_window_additive_frequency`: 9
- `seizure_free_conflict`: 15
- `seizure_free_proxy_evidence_overreach`: 4
- `unknown_cadence_cluster_burden`: 3

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'multiple per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per week' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '1 cluster per 7 to 9 days' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: 'every 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes |  |
| 409 | 1 per month | 1 per month | yes | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: 'unknown' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '1 per week' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 731 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 743 | multiple per day | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: 'unknown' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | unknown | 1 per year | no | evidence_not_text_contained |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | unknown | multiple per month | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'unknown' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every other month' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1030 | 1 per month | 1 to 3 per month | no | final_label_repaired: 'unknown' -> '1 per month' |
| 1046 | unknown | 3 to 5 per month | no |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 5 to 7 per 6 week | 5 to 7 per 3 week | yes | final_label_repaired: 'unknown' -> '5 to 7 per 6 week'; evidence_not_text_contained |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 28 per 3 month | 21 to 28 per 3 month | yes | final_label_repaired: 'unknown' -> '28 per 3 month' |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 3 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per year | 5 to 7 per year | yes | final_label_repaired: 'unknown' -> '5 to 7 per year' |
| 1317 | unknown | unknown, multiple per cluster | yes |  |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 1 per day | 3 per day | yes | final_label_repaired: 'unknown' -> '1 per day' |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes | final_label_repaired: 'multiple per week' -> '7 per week' |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: 'unknown' -> '2 per month' |
| 1573 | multiple per day | 11 per week | no |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: 'unknown' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes | final_label_repaired: 'multiple per week' -> '12 per week' |
| 1597 | 12 per month | 12 per month | yes | final_label_repaired: 'unknown' -> '12 per month' |
| 1636 | 5 per month | 5 per month | yes | final_label_repaired: '2 to 3 per month' -> '5 per month' |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: 'unknown' -> '3 per 2 week' |
| 1695 | unknown | multiple per month | yes | evidence_not_text_contained |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | final_label_repaired: 'unknown' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes | final_label_repaired: 'unknown' -> 'multiple per week' |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: 'unknown' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: 'unknown' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: 'unknown' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'unknown' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'unknown' -> '8 per 2 month' |
| 1880 | multiple per week | 8 per 2 month | no |  |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: 'unknown' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: 'unknown' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: 'unknown' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: 'unknown' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: 'unknown' -> '6 per 3 month' |
| 2023 | 4 per month | 5 per month | no |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | unknown | multiple per month | yes |  |
| 2149 | unknown | unknown | yes |  |
| 2166 | multiple per day | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: 'unknown' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | final_label_repaired: 'unknown' -> '6 to 7 per 2 month' |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: 'unknown' -> '7 to 8 per 3 week' |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | final_label_repaired: 'unknown' -> '6 to 8 per 3 month' |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes | final_label_repaired: 'unknown' -> '2 to 4 per year' |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | evidence_not_text_contained |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes |  |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: 'unknown' -> '5 to 7 per 2 month' |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | final_label_repaired: '6 to 7 per 2 weeks' -> '6 to 7 per 2 week' |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: 'unknown' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: 'unknown' -> '8 to 9 per 2 week' |
| 2548 | unknown | 5 to 6 per 2 month | no |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: 'unknown' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | final_label_repaired: 'unknown' -> '3 to 4 per 2 month' |
| 2609 | 1 per day | 1 per day | yes |  |
| 2622 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2681 | 1 per day | 1 per day | yes |  |
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
| 2822 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2824 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | seizure free for 9 month | seizure free for 9 month | yes |  |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 2965 | seizure free for 6 month | seizure free for 16 month | yes |  |
| 2992 | seizure free for 6 month | seizure free for 7 month | yes |  |
| 3015 | seizure free for 1 year | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 3118 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 3137 | unknown | seizure free for multiple month | no |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | unknown | unknown | yes |  |
| 3371 | unknown | unknown | yes |  |
| 3436 | unknown | unknown | yes |  |
| 3468 | unknown | unknown | yes |  |
| 3469 | unknown | unknown | yes |  |
| 3482 | unknown | unknown | yes |  |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 | unknown | unknown | yes |  |
| 3528 | unknown | unknown | yes |  |
| 3532 | unknown | unknown | yes |  |
| 3534 | unknown | unknown | yes | evidence_not_text_contained |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'unknown' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes |  |
| 3681 | 9 per month | 9 per month | yes |  |
| 3682 | 6 per month | 6 per month | yes |  |
| 3710 | 5 per week | 5 per week | yes |  |
| 3753 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day'; evidence_not_text_contained |
| 3766 | 8 per year | 8 per year | yes |  |
| 3774 | unknown | 9 per year | no |  |
| 3791 | 10 per year | 10 per year | yes |  |
| 3801 | 9 per month | 9 per month | yes |  |
| 3806 | 6 per month | 6 per month | yes |  |
| 3827 | 7 per month | 7 per month | yes |  |
| 3846 | 2 per day | 2 per day | yes |  |
| 3849 | multiple per day | 3 per day | no |  |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 | 3 per year | 3 per year | yes |  |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 | 4 per week | 4 per week | yes |  |
| 3988 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 3995 | unknown | 1 per month | no |  |
| 3999 | unknown | 1 per month | no |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 cluster per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: 'multiple per day' -> '1 per 1 to 2 day' |
| 4173 | unknown | 1 per 2 week | no | final_label_repaired: '1 cluster per 2 weeks' -> 'unknown' |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: 'every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4258 | 4 per week | 4 per week | yes |  |
| 4337 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: 'unknown' -> '3 per 3 month' |
| 4345 | 4 per month | 4 per month | yes | final_label_repaired: 'unknown' -> '4 per month' |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: 'unknown' -> '5 per 2 month' |
| 4402 | 7 per 7 month | 7 per 7 month | yes | final_label_repaired: 'unknown' -> '7 per 7 month' |
| 4410 | 4 per 7 month | 4 per 7 month | yes | final_label_repaired: 'unknown' -> '4 per 7 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: 'unknown' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: 'unknown' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: 'unknown' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: 'unknown' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'unknown' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: 'unknown' -> '1 per 3 week' |
| 4624 | unknown | 1 per 3 to 4 day | no |  |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | final_label_repaired: 'unknown' -> '1 per 14 to 21 day' |
| 4690 | multiple per day | multiple per day | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4709 | multiple per day | multiple per day | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4731 | unknown | unknown | yes |  |
| 4732 | unknown | unknown | yes |  |
| 4771 | unknown | unknown | yes |  |
| 4839 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 4842 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5092 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5110 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5121 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5136 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5141 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 5197 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5210 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5221 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5248 | seizure free for 6 month | seizure free for multiple year | yes |  |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 5379 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5406 | unknown | seizure free for multiple month | no |  |
| 5476 | unknown | unknown | yes |  |
| 5490 | unknown | unknown | yes | evidence_not_text_contained |
| 5491 | unknown | unknown | yes |  |
| 5504 | unknown | unknown | yes |  |
| 5507 | unknown | unknown | yes |  |
| 5528 | 1 per month | 1 per month | yes | final_label_repaired: 'unknown' -> '1 per month' |
| 5534 | unknown | 1 per multiple month | yes | evidence_not_text_contained |
| 5551 | multiple per day | multiple per day | yes |  |
| 5567 | multiple per week | multiple per week | yes |  |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
