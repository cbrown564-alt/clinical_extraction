# Gan 2026 LLM-Only Canonical-Pipeline Validation Run

Date: 2026-06-09

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that collapses extract/select/normalize/project/render into one pass, with the now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing — can produce a directly scorable, fully rendered label without any deterministic normalization or projection stage downstream.

Minimal change: add an `llm_only_canonical_pipeline` runner alongside (not replacing) `llm_only_direct_labeler` and `hybrid_structured_events`. No deterministic `CandidateSet` is built or consumed; final_label is the model's directly rendered answer.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Rare full-validation reason: 8c pre-condition A: validate operational confidence instruction across full validation750 surface to measure distribution shift
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only canonical-pipeline single-shot extract/select/normalize/project/render extractor
- Prompt/program version: `gan2026_llm_only_canonical_pipeline_v0.3`
- Temperature: `0.0`
- Max tokens: `1200`
- Mode: `live`
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-09T05:48:31.181474+00:00`
- Run finished UTC: `2026-06-09T06:12:47.161673+00:00`
- Wall-clock elapsed: `1455.98` seconds (`24.266` minutes)
- Throughput: `0.515117` rows/sec (`1.941` sec/row)
- Optimizer: none
- Deterministic rule configuration: none as pre/post processing; the deterministic/hybrid rule taxonomy is embedded as prompt instructions only, and deterministic code is limited to label repair, evidence text-containment checking, and scoring.
- Git commit: `a7c426f`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_8c_canonical_pipeline_v03_validation750_gpt41mini_2026-06-09.jsonl`

## Summary

- Decision records: 750 / 750
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 338
- Evidence text-containment (free-text evidence found verbatim in note, the comparator-appropriate metric in place of `CandidateSet` source-id validity rate): 694 / 750 (0.9253)
- Purist validation accuracy/micro F1 proxy: 0.7600 (570 / 750)
- Pragmatic validation accuracy/micro F1 proxy: 0.8240 (618 / 750)

## Applied Rule-Taxonomy Families (Self-Reported)

These counts reflect which embedded rule-taxonomy families the model itself reported as shaping its answer (`applied_rule_families`); they are a prompt-compliance signal, not a verified trace.

- `cluster_axis_ambiguity`: 53
- `cluster_cadence_as_event_rate`: 15
- `concrete_frequency_precedence`: 154
- `conditional_only_trigger`: 72
- `conditional_only_trigger and relative_only_trend`: 1
- `denominator_window_mismatch`: 66
- `dominant_vague_current_burden`: 101
- `medication_cadence_ambiguity`: 3
- `no seizure frequency reference`: 1
- `same_window_additive_frequency`: 39
- `seizure_free_conflict`: 91
- `seizure_free_proxy_evidence_overreach`: 77
- `unknown_cadence_cluster_burden`: 49

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
| 187 | 2 per 4 month | 1 per 7 to 9 day | no | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: '1 per month' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month'; evidence_not_text_contained |
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
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per month' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 | multiple per week | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per 7 to 10 days' -> '1 per 7 to 10 day' |
| 816 | 4 per year | 1 per month | no |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per day | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | no seizure frequency reference | 5 to 7 per 3 week | no | final_label_repaired: 'no seizures for 6 weeks' -> 'no seizure frequency reference' |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | final_label_repaired: '7 to 9 per 3 weeks' -> '7 to 9 per 3 week' |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes | evidence_not_text_contained |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per year | 5 to 7 per year | yes |  |
| 1317 | multiple per day | unknown, multiple per cluster | yes |  |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 3 per day | 3 per day | yes |  |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes |  |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per day' |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 per 2 weeks' -> '3 per 2 week' |
| 1695 | no seizure frequency reference | multiple per month | yes |  |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | final_label_repaired: 'unknown' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes | final_label_repaired: 'unknown' -> 'multiple per week' |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '11 per 6 months' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '11 per 3 months' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '8 per 4 months' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1880 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 per 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 per 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '6 per 2 months' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2149 | multiple per month | unknown | yes | final_label_repaired: 'occasional tonic-clonic over last year' -> 'multiple per month' |
| 2166 | unknown | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per 2 weeks' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | final_label_repaired: '6 to 7 per 2 months' -> '6 to 7 per 2 month' |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: '7 to 8 per 3 weeks' -> '7 to 8 per 3 week' |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | final_label_repaired: '6 to 8 per 3 months' -> '6 to 8 per 3 month' |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week'; evidence_not_text_contained |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
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
| 2628 | 1 per day | 1 per day | yes |  |
| 2678 | 1 per day | 1 per day | yes | evidence_not_text_contained |
| 2681 | 1 per day | 1 per day | yes | evidence_not_text_contained |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 1 per month | 1 per month | yes | evidence_not_text_contained |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes | evidence_not_text_contained |
| 2812 | 1 per day | 1 per day | yes |  |
| 2822 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2824 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | seizure free for 9 month | seizure free for 9 month | yes |  |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 2965 | seizure free for 1 year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 1 year 4 month' -> 'seizure free for 1 year' |
| 2992 | 1 per 7 month | seizure free for 7 month | no | final_label_repaired: '1 per 7 months' -> '1 per 7 month'; evidence_not_text_contained |
| 3015 | seizure free for 1 year | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last visit' -> 'seizure free for multiple year' |
| 3137 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '6 to 7 per cluster' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 per month' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, multiple per cluster | 2 cluster per month, 5 per cluster | no | final_label_repaired: '2 per month' -> '2 cluster per month, multiple per cluster' |
| 3281 | 8 per month | 8 per month | yes |  |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | unknown | unknown | yes | final_label_repaired: 'brief generalised tonic–clonic seizures after nights of curtailed sleep over the past three months' -> 'unknown' |
| 3371 | 1 per 8 week | unknown | no | final_label_repaired: '1 per 8 weeks' -> '1 per 8 week' |
| 3436 | unknown | unknown | yes |  |
| 3468 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free outside perimenstrual window' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 3469 | unknown | unknown | yes |  |
| 3482 | no seizure frequency reference | unknown | yes | final_label_repaired: 'seizures happen perimenstrual only (days -3 to +3)' -> 'no seizure frequency reference' |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 | unknown | unknown | yes |  |
| 3528 | unknown | unknown | yes |  |
| 3532 | unknown | unknown | yes |  |
| 3534 | seizure free for 7 month | unknown | no | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'unknown' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 per week' -> '7 per week' |
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
| 3995 | 1 per month | 1 per month | yes |  |
| 3999 | 1 per month | 1 per month | yes | final_label_repaired: 'about 1 per month' -> '1 per month' |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per workday' -> '1 per 1 to 2 day' |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 4258 | 4 per week | 4 per week | yes |  |
| 4337 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '3 per 6 months' -> '3 per 3 month' |
| 4345 | 4 per month | 4 per month | yes |  |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 per month' -> '5 per 2 month' |
| 4402 | 7 per 7 month | 7 per 7 month | yes | final_label_repaired: '1 per month' -> '7 per 7 month' |
| 4410 | 4 per 7 month | 4 per 7 month | yes | final_label_repaired: '5 per year' -> '4 per 7 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '7 to 8 per quarter' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | 2 per month | 1 per 3 to 4 day | no |  |
| 4631 | 1 to 2 per month | 1 per 14 to 21 day | yes |  |
| 4690 | multiple per day | multiple per day | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4709 | unknown | multiple per day | yes |  |
| 4731 | unknown | unknown | yes |  |
| 4732 | unknown | unknown | yes |  |
| 4771 | unknown | unknown | yes |  |
| 4839 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 4842 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for one year' -> 'seizure free for 1 year' |
| 4951 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5092 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5121 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 5141 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last consultation' -> 'seizure free for multiple year' |
| 5210 | seizure free for 1 year | seizure free for multiple month | yes |  |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 5379 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5406 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 5476 | 1 per month | unknown | no | final_label_repaired: 'approximately 1 per month' -> '1 per month' |
| 5490 | unknown | unknown | yes | evidence_not_text_contained |
| 5491 | unknown | unknown | yes |  |
| 5504 | unknown | unknown | yes |  |
| 5507 | 3 per 4 month | unknown | no | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5528 | 1 per month | 1 per month | yes |  |
| 5534 | 1 per 2 month | 1 per multiple month | no | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 5551 | multiple per day | multiple per day | yes |  |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '3 per month' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per 8 days' -> '1 per 8 day' |
| 5682 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5763 | 6 per 3 month | 2 per month | yes | final_label_repaired: '6 per 3 months' -> '6 per 3 month' |
| 5767 | 2 per month | 1 per 1 to 2 week | yes |  |
| 5791 | 3 per 3 month | 1 per month | yes | final_label_repaired: '3 per 3 months' -> '3 per 3 month' |
| 5827 | 2 per month | multiple per week | no |  |
| 5837 | 3 to 4 per month | 2 cluster per 3 week, multiple per cluster | no |  |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '4 per 6 weeks' -> '4 per 6 week' |
| 5873 | multiple per week | multiple per week | yes |  |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes | evidence_not_text_contained |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 5974 | unknown | unknown | yes | evidence_not_text_contained |
| 5977 | multiple per 6 week | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per 6 week' |
| 5995 | 4 per year | 1 per 3 months | yes |  |
| 5996 | unknown | unknown | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes |  |
| 6034 | unknown | unknown | yes |  |
| 6065 | 12 per 3 month | 5 per month | no | final_label_repaired: '12 per 3 months' -> '12 per 3 month' |
| 6077 | 1 per 8 month | unknown | no | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 6087 | unknown | unknown | yes |  |
| 6094 | 5 per month | 3 per month | no |  |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | no seizure frequency reference | unknown | yes | final_label_repaired: 'no unprovoked seizures for over 12 months' -> 'no seizure frequency reference' |
| 6137 | 1 per 2 to 3 week | 1 per 2 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 6153 | 9 per 4 week | 9 per month | yes | final_label_repaired: '9 per month' -> '9 per 4 week' |
| 6180 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week'; evidence_not_text_contained |
| 6192 | unknown | unknown | yes |  |
| 6204 | 1 per 3 to 4 week | 2 per month | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 6209 | multiple per day | multiple per day | yes | final_label_repaired: 'multiple per day and 2 to 3 per month' -> 'multiple per day' |
| 6244 | unknown | unknown | yes |  |
| 6251 | 2 per 4 month | 1 per 1 to 2 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 6273 | unknown | unknown | yes |  |
| 6319 | 1 per week | 1 per week | yes |  |
| 6321 | 2 per 6 month | unknown | no |  |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 6358 | seizure free for 4 month | seizure free for 15 to 16 months | yes |  |
| 6368 | 3 per 6 week | unknown | no | final_label_repaired: '3 per 6 weeks' -> '3 per 6 week' |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes |  |
| 6509 | no seizure frequency reference | 1 per week | no | final_label_repaired: '2 per fortnight' -> 'no seizure frequency reference' |
| 6571 | seizure free for 3.5 month | unknown | no | evidence_not_text_contained |
| 6607 | unknown | unknown | yes |  |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6701 | 4 per 3 week | 4 per 3 week | yes | final_label_repaired: '4 per 3 weeks' -> '4 per 3 week' |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes |  |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes |  |
| 6987 | unknown | unknown | yes |  |
| 7093 | unknown | unknown | yes |  |
| 7126 | unknown | unknown | yes |  |
| 7141 | unknown | unknown | yes |  |
| 7167 | no seizure frequency reference | 1 cluster per 2 weeks, 2 to 4 per cluster | no | final_label_repaired: '3 to 4 per cluster' -> 'no seizure frequency reference' |
| 7168 | 2 per year | unknown | no |  |
| 7192 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 7195 | 1 per month | unknown | no |  |
| 7196 | no seizure frequency reference | 1 per week | no | final_label_repaired: '6 focal seizures per 6 weeks' -> 'no seizure frequency reference' |
| 7198 | 3 per 2 month | unknown | no | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 7275 | 3 per 12 week | 1 per month | yes | final_label_repaired: '3 per 3 months' -> '3 per 12 week' |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | final_label_repaired: '2 clusters per 6 weeks' -> 'unknown' |
| 7409 | multiple per week | unknown | yes | final_label_repaired: 'focal aware seizures most weeks' -> 'multiple per week' |
| 7455 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 7475 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 7491 | unknown | unknown | yes |  |
| 7506 | unknown | unknown | yes |  |
| 7573 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | 3 to 6 per month | 3 to 7 per month | yes | final_label_repaired: '3 to 6 per 5 days per cycle' -> '3 to 6 per month' |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 7818 | seizure free for 2 year | seizure free for 2 years | yes |  |
| 7834 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7859 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year' |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for at least since last clinic contact' -> 'seizure free for multiple year' |
| 7961 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8079 | seizure free for 1 year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 1 year 7 months' -> 'seizure free for 1 year' |
| 8089 | seizure free for 1 year | seizure free for 16 month | yes |  |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes |  |
| 8144 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8160 | no seizure frequency reference | seizure free for multiple month | no |  |
| 8180 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8188 | seizure free for 18 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 8203 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for the current interval' -> 'seizure free for multiple year' |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for current follow-up period' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes |  |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8354 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 12+ month' -> 'seizure free for multiple year' |
| 8400 | no seizure frequency reference | seizure free for multiple month | no |  |
| 8419 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 8474 | seizure free for 8 month | seizure free for multiple month | yes |  |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8577 | seizure free for 18 month | seizure free for multiple month | yes |  |
| 8581 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes |  |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8730 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes | evidence_not_text_contained |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8808 | 0 per 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 month' -> '0 per 10 month'; evidence_not_text_contained |
| 8820 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 8835 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 8854 | seizure free for 8 month | seizure free for multiple month | yes |  |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8922 | seizure free for 3 month | seizure free for multiple month | yes | evidence_not_text_contained |
| 8924 | seizure free for 5 month | seizure free for multiple month | yes |  |
| 8938 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8969 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9002 | 7 per year | 7 per year | yes |  |
| 9063 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 9103 | 1 per 4 month | unknown | no | final_label_repaired: '1 per 4 months' -> '1 per 4 month'; evidence_not_text_contained |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9190 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9215 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 9238 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9250 | seizure free for 9 month | seizure free for multiple month | yes |  |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | multiple per day | multiple per day | yes | final_label_repaired: 'several per day' -> 'multiple per day' |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 per month' -> '4 per 6 month' |
| 9462 | 7 per 11 month | 7 per 11 month | yes | final_label_repaired: '7 per year' -> '7 per 11 month' |
| 9496 | 6 per 12 month | 6 per 12 month | yes | final_label_repaired: '2 per month' -> '6 per 12 month' |
| 9547 | unknown | unknown | yes |  |
| 9588 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9704 | unknown | unknown | yes |  |
| 9815 | multiple per day | multiple per day | yes |  |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes |  |
| 9888 | unknown | unknown | yes |  |
| 9912 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic per year' -> 'no seizure frequency reference' |
| 9937 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 9943 | 1 per 4 to 5 week | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: 'unknown' -> '1 per 4 to 5 week' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | 3 per month | 3 cluster per month, multiple per cluster | no |  |
| 10147 | unknown | unknown | yes | evidence_not_text_contained |
| 10183 | unknown | unknown | yes |  |
| 10189 | no seizure frequency reference | unknown, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 per cluster' -> 'no seizure frequency reference' |
| 10200 | no seizure frequency reference | unknown, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster' -> 'no seizure frequency reference' |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no |  |
| 10245 | 3 per month | 3 cluster per month, multiple per cluster | no |  |
| 10260 | unknown | unknown | yes | evidence_not_text_contained |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes |  |
| 10371 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes |  |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | final_label_repaired: '2 to 3 per cluster' -> '1 cluster per week, 2 to 3 per cluster' |
| 10434 | 2 to 3 per week | multiple cluster per week, 2 to 3 per cluster | yes |  |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes |  |
| 10517 | 3 to 4 per week | 3 to 4 cluster per week, multiple per cluster | no |  |
| 10542 | unknown | unknown, 2 to 4 per cluster | yes | evidence_not_text_contained |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10583 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes |  |
| 10618 | no seizure frequency reference | unknown, 4 to 6 per cluster | yes | final_label_repaired: '2 to 3 per cluster' -> 'no seizure frequency reference' |
| 10629 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 10630 | unknown | multiple cluster per 2 week, 5 per cluster | no | final_label_repaired: '5 per cluster, several clusters per fortnight' -> 'unknown' |
| 10673 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | multiple per month | unknown | yes | final_label_repaired: 'occasional isolated episodes' -> 'multiple per month' |
| 10807 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | final_label_repaired: '2 cluster days per month' -> '2 cluster per month, multiple per cluster' |
| 10829 | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes | final_label_repaired: 'unknown' -> '2 cluster per month, multiple per cluster' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '4 per week' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '4 or more per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, 5 per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '10 to 15 per month' -> '2 to 3 cluster per month, 5 per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 10965 | 8 to 10 per month | 2 cluster per month, 4 to 5 per cluster | yes |  |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10984 | 3 per month | 3 cluster per month, 3 to 4 per cluster | no |  |
| 10996 | 1 to 2 per month | 1 to 2 cluster per month, 4 per cluster | no |  |
| 11002 | 2 to 4 per month | 2 to 4 cluster per month, 5 per cluster | no |  |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: 'cluster days twice this month with typically 5 or more seizures in 24 h; isolated events roughly weekly' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '12 per month' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 per month | 2 cluster per month, 3 to 4 per cluster | no |  |
| 11197 | unknown | 1 cluster per month, 4 to 6 per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 11216 | seizure free for 4 month | unknown | no | evidence_not_text_contained |
| 11254 | seizure free for 3 month | unknown | no |  |
| 11259 | unknown | unknown | yes |  |
| 11262 | unknown | unknown | yes | final_label_repaired: '1 tonic–clonic seizure on 12-Jun' -> 'unknown' |
| 11272 | 1 per 3 month | unknown | no |  |
| 11282 | seizure free for 3 month | unknown | no |  |
| 11337 | 1 per 3 month | unknown | no | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 11350 | multiple per day | unknown | yes | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 11380 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 11389 | 1 per 2 month | unknown | no |  |
| 11400 | 1 per day | no seizure frequency reference | no | final_label_repaired: 'no seizure frequency reference' -> '1 per day' |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11409 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11681 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11706 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11711 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11728 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11737 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11824 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11841 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 12036 | multiple per day | multiple per day | yes |  |
| 12041 | multiple per day | multiple per day | yes |  |
| 12046 | multiple per day | multiple per day | yes |  |
| 12051 | multiple per day | multiple per day | yes |  |
| 12111 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12127 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12130 | multiple per week | multiple per week | yes | final_label_repaired: '3 per year and several per week' -> 'multiple per week' |
| 12139 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12145 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12192 | multiple per day | 1 per day | no |  |
| 12218 | multiple per day | 1 per day | no |  |
| 12236 | multiple per day | 1 per day | no |  |
| 12246 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12314 | 3 per week | 3 per week | yes |  |
| 12366 | 4 per day | 4 per day | yes | final_label_repaired: '4 per day and 2 per month' -> '4 per day' |
| 12378 | 4 per day | 4 per day | yes |  |
| 12383 | 4 per day | 4 per day | yes | final_label_repaired: '4 per day and 2 per month' -> '4 per day' |
| 12403 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 12412 | 2 per day | 2 per day | yes |  |
| 12422 | 1 per day | 1 per day | yes | final_label_repaired: 'nightly generalised convulsions and 4 per year tonic seizures' -> '1 per day' |
| 12438 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12456 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12460 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12468 | 1 per day | 1 per day | yes | final_label_repaired: 'nightly' -> '1 per day' |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12502 | 1 cluster per month, multiple per cluster | 4 per day | no | final_label_repaired: '1 to 2 per month tonic-clonic, 4 per day absences, clusters of myoclonic jerks and occasional tonic seizures roughly once a month' -> '1 cluster per month, multiple per cluster' |
| 12506 | 1 cluster per month, multiple per cluster | 4 per day | no | final_label_repaired: '1 to 2 per month for generalized tonic-clonic seizures; 4 per day for absences; 1 cluster per month for myoclonic jerks and occasional tonic seizures' -> '1 cluster per month, multiple per cluster' |
| 12537 | multiple per week | 1 per day | no | final_label_repaired: 'up to 3 per week' -> 'multiple per week' |
| 12548 | 1 per day | 1 per day | yes | final_label_repaired: 'daily drop attacks' -> '1 per day' |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'daily drop attacks' -> '1 per day' |
| 12556 | 2 to 3 per week | 1 per day | no |  |
| 12562 | 3 to 4 per week | 1 per day | no |  |
| 12573 | multiple per month | 1 per day | no | final_label_repaired: 'up to 2 per month' -> 'multiple per month' |
| 12584 | 1 per 3 month | 1 per week | no | final_label_repaired: '1 per 3 months plus weekly' -> '1 per 3 month' |
| 12641 | 1 to 2 per week | 1 per day | no |  |
| 12665 | 1 to 2 per month | 1 per day | no |  |
| 12667 | 1 to 2 per month | 1 per day | no |  |
| 12676 | 1 to 2 per year | 1 per day | no |  |
| 12679 | 1 to 2 per month | 1 per day | no |  |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | 4 per day | 4 per day | yes |  |
| 12788 | 6 per year | 6 per 4 month | no |  |
| 12810 | 5 per year | 5 per 2 month | no |  |
| 12823 | 9 per year | 9 per month | no | final_label_repaired: '9 per year; 1 per 3 to 4 weeks' -> '9 per year'; evidence_not_text_contained |
| 12827 | 5 per year | 5 per 5 month | no |  |
| 12835 | 4 per year | 4 per month | no | final_label_repaired: '4 per month' -> '4 per year' |
| 12877 | 10 per year | 10 per 4 month | no |  |
| 12882 | 7 per year | 7 per 4 month | no | final_label_repaired: '7 per year and 1 to 2 per month' -> '7 per year' |
| 12901 | 8 per year | 8 per 5 month | no | final_label_repaired: 'unknown' -> '8 per year' |
| 12949 | 9 per year | 9 per 6 month | no |  |
| 12950 | 7 per year | 7 per 3 month | no | final_label_repaired: '7 per year and 1 per 2 to 3 weeks' -> '7 per year' |
| 12963 | unknown | unknown | yes |  |
| 12979 | 3 per year | 3 per 4 month | yes |  |
| 13008 | 4 per year | 4 per month | no |  |
| 13011 | 3 per year | 3 per 4 month | yes |  |
| 13051 | unknown | 2 per 8 month | no | final_label_repaired: '1 generalised tonic-clonic seizure 3 weeks ago with brief absences earlier that week, no further events since' -> 'unknown'; evidence_not_text_contained |
| 13058 | 1 per month | 2 per 7 month | no |  |
| 13114 | unknown | 1 per year | no | final_label_repaired: '1 tonic seizure 2 weeks ago with brief myoclonic jerks preceding' -> 'unknown'; evidence_not_text_contained |
| 13122 | no seizure frequency reference | 3 per year | no | final_label_repaired: '3 per cluster' -> 'no seizure frequency reference' |
| 13149 | unknown | 3 per year | no | final_label_repaired: '3 tonic seizures in 1 day' -> 'unknown' |
| 13178 | 1 per month | 1 per 6 month | no |  |
| 13190 | 1 per month | 1 per 5 month | no |  |
| 13209 | 1 per month | 1 per 8 month | no |  |
| 13267 | no seizure frequency reference | 2 per 5 month | no | final_label_repaired: '1 drop attack per month' -> 'no seizure frequency reference' |
| 13290 | 2 per month | 4 per 6 month | no | evidence_not_text_contained |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes |  |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | yes |  |
| 13450 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over one year' -> 'seizure free for multiple year' |
| 13471 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13478 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over one year' -> 'seizure free for multiple year' |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 1.5 year | seizure free for 1.5 year | yes |  |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13627 | 64 per 12 month | 64 per 12 month | yes | final_label_repaired: 'unknown' -> '64 per 12 month' |
| 13635 | 47 per 7 month | 47 per 7 month | yes | final_label_repaired: 'multiple per month' -> '47 per 7 month' |
| 13711 | 76 per 12 month | 76 per 12 month | yes | final_label_repaired: 'multiple per month' -> '76 per 12 month' |
| 13721 | 77 per 12 month | 77 per 12 month | yes | final_label_repaired: 'multiple per month' -> '77 per 12 month' |
| 13732 | 52 per 8 month | 52 per 8 month | yes | final_label_repaired: 'unknown' -> '52 per 8 month'; evidence_not_text_contained |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13893 | 2 per year | 2 per year | yes |  |
| 13922 | 2 per 3 month | unknown | no | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 14002 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 14025 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 drop attacks per 6 weeks' -> 'no seizure frequency reference' |
| 14029 | unknown | unknown | yes |  |
| 14040 | unknown | unknown | yes |  |
| 14076 | unknown | unknown | yes |  |
| 14092 | 5 per month | unknown | no |  |
| 14096 | 5 per month | unknown | no |  |
| 14137 | 3 to 4 per 3 month | unknown | no | final_label_repaired: '3 to 4 per 3 months' -> '3 to 4 per 3 month' |
| 14146 | 3 per 2 month | unknown | no | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 14187 | seizure free for 1 month | 2 to 3 per month | no |  |
| 14214 | seizure free for 1 month | 2 to 4 per month | no |  |
| 14250 | seizure free for multiple year | 2 per month | no | final_label_repaired: '2 per week for the first week after stopping Levetiracetam, then seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14282 | seizure free for multiple year | multiple per month | no | final_label_repaired: 'seizure free for 5 weeks' -> 'seizure free for multiple year' |
| 14284 | no seizure frequency reference | 2 to 3 per month | no |  |
| 14317 | seizure free for 2 month | 4 per 2 month | no |  |
| 14332 | seizure free for 2 month | 5 per 2 month | no |  |
| 14335 | seizure free for multiple year | 3 to 4 per 2 month | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 14383 | seizure free for 3 month | 3 to 4 per 3 month | no |  |
| 14454 | seizure free for 2 month | 2 per 2 month | no |  |
| 14524 | unknown | 2 per 6 month | no |  |
| 14530 | no seizure frequency reference | 2 per 2 month | no | final_label_repaired: '2 events total, no current frequency stated' -> 'no seizure frequency reference' |
| 14540 | seizure free for multiple year | 2 per 8 month | no | final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year' |
| 14562 | no seizure frequency reference | 3 per 6 month | no | evidence_not_text_contained |
| 14567 | 3 per 4 month | 3 per 3 month | no | final_label_repaired: '3 seizures over 4 months' -> '3 per 4 month'; evidence_not_text_contained |
| 14581 | seizure free for multiple year | 2 per 3 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 14587 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 14592 | 3 per 6 month | 3 per 5 month | yes |  |
| 14611 | no seizure frequency reference | 2 per 4 month | no |  |
| 14628 | 2 per year | 2 per 2 month | no |  |
| 14635 | seizure free for multiple year | 5 per 4 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 14645 | no seizure frequency reference | 2 per 6 month | no | final_label_repaired: '2 seizures total, no further events to date' -> 'no seizure frequency reference' |
| 14662 | 3 per month | 3 per 4 month | no | evidence_not_text_contained |
| 14672 | seizure free for 6 month | 3 per 8 month | no |  |
| 14706 | 2 per 5 month | 2 per 5 month | yes | final_label_repaired: '2 per 5 months' -> '2 per 5 month' |
| 14765 | seizure free for 1 month | 1 per month | no |  |
| 14806 | seizure free for 1 month | 1 per 2 month | no | evidence_not_text_contained |
| 14810 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year' |
| 14821 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14872 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 14943 | seizure free for 3 month | 1 per 3 month | no |  |
| 14949 | 1 per month | 1 per month | yes |  |
| 14965 | seizure free for 3 month | 1 per 3 month | no | final_label_repaired: 'seizure free for nearly 3 month' -> 'seizure free for 3 month' |
| 14973 | seizure free for 1 month | 1 per month | no |  |
| 15004 | seizure free for 2 month | 1 per 3 month | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 15012 | seizure free for 2 month | 1 per 2 month | no |  |
| 15021 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | seizure free for 3 month | 1 per 3 month | no |  |
| 15094 | 3 per year | 4 per 13 month | yes |  |
| 15108 | 2 to 3 per month | 3 to 4 per 15 month | no |  |
| 15127 | 4 per year | 5 per 13 month | yes |  |
| 15129 | 4 per year | 4 per 15 month | yes |  |
| 15141 | 3 to 4 per month | 4 to 5 per 15 month | no |  |
| 15168 | multiple per week | multiple per 15 month | yes | evidence_not_text_contained |
| 15193 | multiple per month | multiple per 13 month | yes | evidence_not_text_contained |
| 15242 | unknown | multiple cluster per 15 month, multiple per cluster | no | final_label_repaired: 'occasional clusters of myoclonic jerks' -> 'unknown' |
| 15262 | unknown | multiple cluster per 13 month, multiple per cluster | no | final_label_repaired: 'occasional clusters of myoclonic jerks' -> 'unknown' |
| 15267 | no seizure frequency reference | 3 per 14 month | no |  |
| 15306 | 2 to 3 per month | 2 to 3 per 15 month | no |  |
| 15317 | 2 to 3 per month | 2 to 3 per 15 month | no |  |
| 15376 | 4 to 6 per day | 1 cluster per 2 week, 4 to 6 per cluster | no |  |
| 15404 | 3 to 4 per day | 1 cluster per 4 month, 3 to 4 per cluster | no | evidence_not_text_contained |
| 15429 | seizure free for multiple year | 1 cluster per 2 month, 4 per cluster | no | final_label_repaired: '4 per day during clusters, seizure free for up to 2 month' -> 'seizure free for multiple year' |
| 15431 | 5 per day | 1 cluster per 4 month, 5 per cluster | no |  |
| 15442 | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster | yes | final_label_repaired: 'multiple per day' -> '1 cluster per 4 day, 2 per cluster' |
| 15470 | multiple per day | 1 cluster per 5 day, multiple per cluster | no |  |
| 15479 | multiple per day | 1 cluster per 4 to 5 day, 2 per cluster | no |  |
| 15497 | 5 per day | 1 cluster per 4 to 5 day, 5 per cluster | yes |  |
| 15503 | 1 cluster per 5 day, 3 to 4 per cluster | 1 cluster per 5 day, 3 to 4 per cluster | yes | final_label_repaired: '3 to 4 per day' -> '1 cluster per 5 day, 3 to 4 per cluster'; evidence_not_text_contained |
| 15513 | 2 per day | 1 cluster per 4 to 5 day, 2 to 3 per cluster | no |  |
| 15519 | 1 cluster per 4 day, 3 per cluster | 1 cluster per 4 day, 3 per cluster | yes | final_label_repaired: 'multiple per month' -> '1 cluster per 4 day, 3 per cluster' |
| 15529 | unknown | 1 cluster per 3 day, 4 per cluster | no | final_label_repaired: '4 per day during clusters' -> 'unknown' |
| 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per day' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15614 | 3 per week | 3 per week | yes |  |
| 15628 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 15639 | 2 per week | 2 per week | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 15672 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 15697 | multiple per week | 1 per day | no | final_label_repaired: 'multiple per day' -> 'multiple per week' |
| 15715 | multiple per month | 1 per day | no | final_label_repaired: 'multiple per day' -> 'multiple per month' |
| 15745 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15766 | 4 per week | 4 per week | yes |  |
| 15768 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15771 | 3 per week | 3 per week | yes |  |
| 15772 | 2 per week | 2 per week | yes |  |
| 15774 | 2 per week | 2 per week | yes |  |
| 15783 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15802 | 7 per week | 7 per week | yes |  |
| 15831 | 2 to 4 per day | 2 to 4 per day | yes |  |
| 15834 | 5 per week | 5 per week | yes |  |
| 15964 | 11 per 2 month | 11 per 3 month | no | final_label_repaired: '11 per month' -> '11 per 2 month' |
| 15965 | 13 per 2 month | 13 per 2 month | yes | final_label_repaired: '9 per month' -> '13 per 2 month' |
| 15966 | 5 per 2 month | 5 per 3 month | yes | final_label_repaired: '5 per 3 months' -> '5 per 2 month' |
| 15982 | 9 per 2 month | 9 per 2 month | yes | final_label_repaired: '8 per month' -> '9 per 2 month' |
| 15986 | 11 per 2 month | 11 per 3 month | no | final_label_repaired: '6 per month' -> '11 per 2 month' |
| 15992 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '7 per month' -> '7 per 2 month' |
| 15997 | 10 per 2 month | 10 per 3 month | no | final_label_repaired: '9 per 3 months' -> '10 per 2 month' |
| 16021 | 9 per 2 month | 9 per 3 month | no | final_label_repaired: '8 per month' -> '9 per 2 month' |
| 16041 | 9 per 2 month | 9 per 3 month | no | final_label_repaired: '7 per month' -> '9 per 2 month' |
| 16084 | no seizure frequency reference | 8 per 4 month | no | final_label_repaired: 'no seizures so far this month' -> 'no seizure frequency reference' |
| 16091 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '3 per month' -> '3 per 3 month' |
| 16097 | 1 per month | 17 per 4 month | no |  |
| 16107 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '4 per month' -> '8 per 3 month' |
| 16108 | 1 per month | 12 per 4 month | no |  |
| 16132 | 13 per 2 month | 15 per 3 month | yes | final_label_repaired: '15 per month' -> '13 per 2 month' |
| 16133 | 18 per 4 month | 18 per 4 month | yes | final_label_repaired: '6 per month' -> '18 per 4 month' |
| 16161 | 7 per month | 18 per 3 month | yes |  |
| 16162 | 6 per month | 11 per 3 month | no |  |
| 16181 | 15 per 4 month | 15 per 4 month | yes | final_label_repaired: '11 per month' -> '15 per 4 month' |
| 16195 | 6 per month | 16 per 4 month | no |  |
| 16203 | 8 per 2 month | 9 per 3 month | no | final_label_repaired: '9 per month' -> '8 per 2 month' |
| 16204 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '5 per month' -> '5 per 3 month' |
| 16220 | no seizure frequency reference | 11 per 4 month | no | final_label_repaired: 'no seizures this month' -> 'no seizure frequency reference' |
| 16324 | 7 per 2 month | 10 per 3 month | yes | final_label_repaired: '10 per month' -> '7 per 2 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per 3 months' -> '7 per 3 month' |
| 16356 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster every 4 days' -> '1 per 4 day' |
| 16394 | 1 per 2 to 4 day | 1 per 2 to 4 day | yes | final_label_repaired: 'unknown' -> '1 per 2 to 4 day' |
| 16408 | 1 per day | 1 per 3 day | no | final_label_repaired: '1 per 3 days' -> '1 per day' |
| 16429 | 1 per day | 1 per 2 to 3 day | no | final_label_repaired: '1 to 3 per week' -> '1 per day' |
| 16432 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'approximately 1 every 2 days' -> '1 per 2 day' |
| 16450 | 1 per day | 1 per multiple day | no | final_label_repaired: 'multiple per week' -> '1 per day' |
| 16529 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster every 5 days' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: 'multiple per week' -> '1 per 2 to 3 day' |
| 16574 | unknown | 1 per 4 day | no | final_label_repaired: '1 cluster per 4 days' -> 'unknown' |
| 16590 | unknown | 1 per 4 to 5 day | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 16618 | 1 cluster per month, multiple per cluster | 1 per 5 day | no | final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster' |
| 16645 | 4 per 2 month | 5 per 7 month | no | final_label_repaired: '3 per 6 month' -> '4 per 2 month' |
| 16674 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 per 6 months' -> '7 per 6 month' |
| 16685 | 9 per 2 month | 10 per 3 month | no | final_label_repaired: '10 per month' -> '9 per 2 month'; evidence_not_text_contained |
| 16697 | 3 per 6 month | 3 per 6 month | yes |  |
| 16704 | unknown | 9 per 6 month | no |  |
| 16714 | 5 per 3 month | 5 per 6 month | no | final_label_repaired: '3 seizures in November, 1 in February, 1 in April' -> '5 per 3 month' |
| 16717 | 5 per 6 month | 5 per 6 month | yes |  |
| 16719 | 1 per week | 7 per 6 month | no |  |
| 16728 | 4 per year | 4 per 6 month | yes |  |
| 16750 | unknown | 6 per 7 month | no | final_label_repaired: '1 generalized tonic-clonic and 4 absence seizures over 7 months' -> 'unknown' |
| 16757 | unknown | 13 per 6 month | no |  |
| 16758 | 9 per 4 month | 9 per 5 month | yes | final_label_repaired: '9 per 4 months' -> '9 per 4 month' |
| 16772 | 8 per 5 month | 9 per 5 month | yes | final_label_repaired: '8 per 5 months' -> '8 per 5 month' |
| 16774 | 19 per 6 month | 19 per 7 month | yes |  |
| 16780 | unknown | 3 per 7 month | no |  |
| 16824 | 10 per 2 month | 11 per 5 month | no | final_label_repaired: '11 per 4 months' -> '10 per 2 month' |
| 16833 | unknown | 8 per 6 month | no |  |
| 16839 | 8 per 3 month | 9 per 4 month | yes | final_label_repaired: '8 per 3 months' -> '8 per 3 month' |
| 16867 | 6 per 7 month | 6 per 7 month | yes | final_label_repaired: '6 per 7 months' -> '6 per 7 month' |
| 16907 | 9 per 6 month | 9 per 6 month | yes | evidence_not_text_contained |
| 16938 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 16947 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 16961 | 1 per 3 month | 2 per week | no | final_label_repaired: '3 per 3 months' -> '1 per 3 month' |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes |  |
| 17001 | 5 per week | 5 per week | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 17110 | 4 to 5 per week | 4 to 5 cluster per week, multiple per cluster | no |  |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | final_label_repaired: 'clusters of absence seizures on five days each month, nocturnal tonic seizures around once per year' -> '1 cluster per month, multiple per cluster' |
| 17146 | 1 per 6 month | 1 per day | no |  |
| 17167 | 1 per 6 month | 1 per week | no |  |
| 17189 | 1 per 6 month | 1 per month | no |  |
| 17200 | 1 per month | 1 per month | yes | final_label_repaired: '1 tonic-clonic seizure per 6 month, myoclonic jerks monthly' -> '1 per month' |
| 17201 | 4 per month | 4 per month | yes |  |
| 17273 | 1 per 2 day | 1 per 2 day | yes |  |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes |  |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 per 1 to 2 days' -> '1 per 1 to 2 day' |
