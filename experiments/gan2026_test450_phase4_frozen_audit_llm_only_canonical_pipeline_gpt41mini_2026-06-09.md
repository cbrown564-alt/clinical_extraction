# Gan 2026 LLM-Only Canonical-Pipeline Validation Run

Date: 2026-06-09

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that collapses extract/select/normalize/project/render into one pass, with the now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing — can produce a directly scorable, fully rendered label without any deterministic normalization or projection stage downstream.

Minimal change: add an `llm_only_canonical_pipeline` runner alongside (not replacing) `llm_only_direct_labeler` and `hybrid_structured_events`. No deterministic `CandidateSet` is built or consumed; final_label is the model's directly rendered answer.

Data surface: `test` split, `gan2026_split_v1`, 450 rows.
Rare full-validation reason: Phase 4 frozen test450 aggregate audit (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 6, authorized 2026-06-09): llm_only_canonical_pipeline (v0.5 prompt) over test450, gpt-4.1-mini.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only canonical-pipeline single-shot extract/select/normalize/project/render extractor
- Prompt/program version: `gan2026_llm_only_canonical_pipeline_v0.5`
- Temperature: `0.0`
- Max tokens: `1200`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-09T23:12:42.409204+00:00`
- Run finished UTC: `2026-06-09T23:31:50.819128+00:00`
- Wall-clock elapsed: `1148.41` seconds (`19.14` minutes)
- Throughput: `0.391846` rows/sec (`2.552` sec/row)
- Optimizer: none
- Deterministic rule configuration: none as pre/post processing; the deterministic/hybrid rule taxonomy is embedded as prompt instructions only, and deterministic code is limited to label repair, evidence text-containment checking, and scoring.
- Git commit: `f4d1c2e`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_test450_phase4_frozen_audit_llm_only_canonical_pipeline_gpt41mini_2026-06-09.jsonl`

## Summary

- Decision records: 450 / 450
- Call failures: 0
- Parse/schema/label issues: 0
- Deterministic repair notes: 227
- Evidence text-containment (free-text evidence found verbatim in note, the comparator-appropriate metric in place of `CandidateSet` source-id validity rate): 415 / 450 (0.9222)
- Purist validation accuracy/micro F1 proxy: 0.7244 (326 / 450)
- Pragmatic validation accuracy/micro F1 proxy: 0.7689 (346 / 450)

## Applied Rule-Taxonomy Families (Self-Reported)

These counts reflect which embedded rule-taxonomy families the model itself reported as shaping its answer (`applied_rule_families`); they are a prompt-compliance signal, not a verified trace.

- `cluster_axis_ambiguity`: 51
- `cluster_cadence_as_event_rate`: 2
- `concrete_frequency_precedence`: 4
- `conditional_only_trigger`: 61
- `denominator_window_mismatch`: 123
- `dominant_vague_current_burden`: 111
- `same_window_additive_frequency`: 1
- `seizure_free_conflict`: 118
- `seizure_free_proxy_evidence_overreach`: 36
- `unknown_cadence_cluster_burden`: 25

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 31 | 4 per day | 4 per day | yes | final_label_repaired: 'multiple per day' -> '4 per day' |
| 51 | 5 per week | 5 per week | yes |  |
| 61 | 4 per week | 4 per week | yes |  |
| 115 | 7 to 8 per month | 7 to 8 per month | yes |  |
| 136 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 174 | 1 to 3 per day | 1 per 1 to 3 day | no | evidence_not_text_contained |
| 176 | 1 per 6 to 7 day | 1 per 6 to 7 day | yes | final_label_repaired: '1 per week' -> '1 per 6 to 7 day' |
| 234 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 240 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2 to 3 months' -> '1 per 2 to 3 month' |
| 364 | multiple per week | 1 per week | no |  |
| 493 | 11 per month | 11 per month | yes |  |
| 503 | 11 to 28 per 3 month | 11 to 28 per 3 month | yes | final_label_repaired: '11 to 28 per quarter' -> '11 to 28 per 3 month' |
| 538 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 seizure every 4 days' -> '1 per 4 day'; evidence_not_text_contained |
| 610 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2 to 3 months' -> '1 per 2 to 3 month' |
| 632 | 1 per 1 to 2 month | 1 per 1 to 2 month | yes | final_label_repaired: '1 per 1 to 2 months' -> '1 per 1 to 2 month' |
| 666 | 2 per 2 to 3 month | 2 per 2 to 3 month | yes | final_label_repaired: '2 per 2 to 3 months' -> '2 per 2 to 3 month' |
| 685 | multiple per day | 1 per day | no | final_label_repaired: '1 per day' -> 'multiple per day' |
| 714 | 2 per day | 2 per day | yes |  |
| 722 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 735 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 739 | multiple per week | multiple per week | yes |  |
| 748 | 2 per 4 month | 1 per 2 month | yes | final_label_repaired: '2 isolated episodes in 4 months' -> '2 per 4 month' |
| 750 | multiple per week | multiple per week | yes |  |
| 803 | 1 per month | 1 per month | yes |  |
| 804 | 2 cluster per month, 2 per cluster | 1 per month | no | final_label_repaired: '2 per month' -> '2 cluster per month, 2 per cluster' |
| 824 | 1 per month | 1 per month | yes |  |
| 836 | 1 per year | 1 per year | yes |  |
| 841 | 1 per year | 1 per year | yes |  |
| 892 | 1 per month | 1 per 2 day | no | final_label_repaired: '1 every 2 days for focal aware seizures, 2 per fortnight for generalised tonic–clonic seizures' -> '1 per month' |
| 934 | 1 to 2 per month | 1 per 2 week | yes |  |
| 938 | 2 per month | 1 per 2 week | yes |  |
| 1005 | 1 per 3 month | multiple per 3 month | no | final_label_repaired: '1 cluster per 3 months' -> '1 per 3 month' |
| 1017 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 1060 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 1182 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | final_label_repaired: '6 to 14 per 3 months' -> '6 to 14 per 3 month' |
| 1184 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | final_label_repaired: '6 to 14 per 3 months' -> '6 to 14 per 3 month' |
| 1250 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1289 | 5 to 6 per year | 5 to 6 per year | yes | final_label_repaired: 'unknown' -> '5 to 6 per year' |
| 1290 | 8 to 9 per year | 8 to 9 per year | yes | final_label_repaired: '8 or 9 tonic-clonic seizures this year' -> '8 to 9 per year' |
| 1326 | multiple per day | multiple per day | yes |  |
| 1378 | 5 per month | 5 per month | yes | final_label_repaired: '1 tonic-clonic and 4 petit mal per month' -> '5 per month' |
| 1422 | 9 per week | 9 per week | yes |  |
| 1433 | 4 per month | 4 per month | yes |  |
| 1460 | 7 per month | 7 per month | yes | final_label_repaired: '1 tonic-clonic and 6 petit mal per month' -> '7 per month' |
| 1497 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1511 | 7 per month | 7 per month | yes |  |
| 1534 | 9 per month | 9 per month | yes |  |
| 1624 | 12 per week | 12 per week | yes | final_label_repaired: '5 convulsions and 7 petit mal per week' -> '12 per week' |
| 1629 | 7 per month | 12 per month | yes | final_label_repaired: '12 per month' -> '7 per month' |
| 1633 | 7 per week | 12 per week | yes | final_label_repaired: '12 per week' -> '7 per week' |
| 1656 | 5 per month | 5 per month | yes | final_label_repaired: '2 convulsions and 3 petit mal per month' -> '5 per month' |
| 1683 | multiple per day | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per day' |
| 1705 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'cluster of short focal events in the latter part of last month' -> 'unknown' |
| 1722 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 1736 | 1 per 6 month | 4 per 6 month | no | final_label_repaired: '1 to 4 per 6 months' -> '1 per 6 month' |
| 1812 | 12 per 3 month | 12 per 3 month | yes | final_label_repaired: '12 per 3 months' -> '12 per 3 month' |
| 1868 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '4 per month' -> '8 per 2 month' |
| 1883 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 per 3 months' -> '4 per 3 month' |
| 1889 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 per 6 months' -> '4 per 6 month' |
| 1898 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 per 6 months' -> '4 per 6 month' |
| 1911 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '7 in the past 2 months' -> '7 per 2 month' |
| 1934 | 2 per 2 month | 7 per 2 month | no | final_label_repaired: '2 to 3 per month' -> '2 per 2 month' |
| 1938 | 5 per 4 month | 5 per 4 month | yes | final_label_repaired: '1 per 4 months for drop attacks, 4 per 4 months for epileptic spasms' -> '5 per 4 month' |
| 2071 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 2112 | multiple per week | multiple per week | yes |  |
| 2135 | unknown | unknown | yes |  |
| 2220 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2226 | 3 to 10 per 2 week | 3 to 10 per 2 week | yes | final_label_repaired: '3 to 10 per 2 weeks' -> '3 to 10 per 2 week' |
| 2246 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: 'about 7 to 8 in 3 weeks' -> '7 to 8 per 3 week' |
| 2262 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 2306 | 8 to 9 per month | 8 to 9 per month | yes |  |
| 2311 | 5 to 7 per month | 5 to 7 per month | yes |  |
| 2356 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2404 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 2486 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2543 | 2 to 4 per 2 week | 2 to 4 per 2 week | yes | final_label_repaired: '2 to 4 per 2 weeks' -> '2 to 4 per 2 week' |
| 2564 | 3 to 5 per 2 month | 3 to 5 per 2 month | yes | final_label_repaired: '3 to 5 per 2 months' -> '3 to 5 per 2 month' |
| 2596 | 2 per day | 2 per day | yes | final_label_repaired: '2 per night' -> '2 per day' |
| 2597 | 2 per day | 2 per day | yes | final_label_repaired: '2 per night' -> '2 per day' |
| 2652 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2684 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2725 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 every other week' -> '1 per 2 week' |
| 2749 | 1 per month | 1 per month | yes | evidence_not_text_contained |
| 2781 | 1 per week | 1 per week | yes |  |
| 2795 | 1 per week | 1 per week | yes |  |
| 2854 | 2 per month | 2 per month | yes | evidence_not_text_contained |
| 2879 | multiple per day | 2 per day | no |  |
| 2978 | seizure free for 9 month | seizure free for 9 month | yes |  |
| 3054 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3102 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3214 | 1 cluster per month, 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 7 per cluster' |
| 3225 | 1 cluster per month, 10 per cluster | 1 cluster per month, 3 to 10 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 10 per cluster' |
| 3237 | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, 5 per cluster' |
| 3246 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3291 | 9 per month | 9 per month | yes |  |
| 3293 | 8 per month | 8 per month | yes |  |
| 3300 | 9 per month | 9 per month | yes |  |
| 3327 | 5 to 6 per year | 5 to 6 per year | yes |  |
| 3329 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 3340 | 2 to 3 per month | 2 to 3 per month | yes | evidence_not_text_contained |
| 3353 | unknown | unknown | yes |  |
| 3355 | 2 per 6 month | 1 per 3 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 3407 | multiple per week | multiple per week | yes |  |
| 3452 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 3514 | unknown | unknown | yes |  |
| 3630 | 7 per week | 7 per week | yes | final_label_repaired: 'unknown' -> '7 per week' |
| 3638 | 3 per week | 3 per week | yes | final_label_repaired: 'up to 3 per week' -> '3 per week' |
| 3675 | 1 per month | 1 per month | yes |  |
| 3706 | 6 per week | 6 per week | yes |  |
| 3747 | 3 per day | 3 per day | yes |  |
| 3831 | 7 per month | 7 per month | yes |  |
| 3864 | 3 per day | 3 per day | yes |  |
| 3867 | 3 per day | 3 per day | yes |  |
| 3888 | 8 per year | 8 per year | yes |  |
| 3906 | 4 per year | 4 per year | yes |  |
| 3918 | 9 per week | 9 per week | yes |  |
| 3934 | 9 per week | 9 per week | yes |  |
| 4003 | 2 to 3 per month | 1 per month | no | evidence_not_text_contained |
| 4004 | multiple per month | 1 per month | no |  |
| 4073 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4076 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4197 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every 2 days' -> '1 per 2 day' |
| 4217 | multiple per week | 1 per 2 day | no |  |
| 4239 | unknown | unknown | yes |  |
| 4342 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '5 events over several months with clustering' -> '5 per 3 month' |
| 4352 | 5 per 10 month | 5 per 3 month | no | final_label_repaired: '5 events over approximately 3 months' -> '5 per 10 month' |
| 4424 | 3 per 6 month | 3 per 6 month | yes | final_label_repaired: 'unknown' -> '3 per 6 month' |
| 4679 | multiple per day | multiple per day | yes |  |
| 4707 | multiple per day | multiple per day | yes |  |
| 4809 | unknown | unknown | yes |  |
| 4831 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4892 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4903 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4967 | multiple per year | seizure free for multiple month | no | final_label_repaired: 'rare auras under sleep deprivation' -> 'multiple per year' |
| 4996 | seizure free for 1 year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 1 year 4 months' -> 'seizure free for 1 year' |
| 5088 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for recent months' -> 'seizure free for multiple year' |
| 5174 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5213 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5385 | no seizure frequency reference | seizure free for 1 year | no |  |
| 5395 | no seizure frequency reference | seizure free for 6 month | no |  |
| 5505 | unknown | unknown | yes |  |
| 5527 | 1 per year | 1 per year | yes |  |
| 5540 | 1 per month | 1 per 4 to 5 month | no |  |
| 5555 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5627 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 per 5 days' -> '1 per 5 day' |
| 5653 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 5684 | unknown | unknown | yes |  |
| 5708 | unknown | unknown | yes |  |
| 5764 | 3 per month | 3 per month | yes |  |
| 5766 | 1 per 3 to 4 week | multiple per week | no | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 5976 | unknown | unknown | yes |  |
| 6025 | unknown | unknown | yes |  |
| 6028 | unknown | 1 per 3 months | no |  |
| 6063 | 3 per 2 week | unknown | no | final_label_repaired: '3 per fortnight' -> '3 per 2 week' |
| 6073 | 1 per 3 to 4 week | 1 per 3 to 4 weeks | yes | final_label_repaired: '1 per month' -> '1 per 3 to 4 week' |
| 6164 | unknown | unknown | yes |  |
| 6216 | 5 per 6 week | 4 per 6 week | yes | final_label_repaired: '5 per 6 weeks' -> '5 per 6 week' |
| 6252 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 6288 | 2 per 10 week | 2 per 10 week | yes | final_label_repaired: '2 per 10 weeks' -> '2 per 10 week'; evidence_not_text_contained |
| 6296 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 over 4 months' -> '3 per 4 month' |
| 6303 | multiple per week | unknown | yes |  |
| 6330 | 2 per 3 month | multiple per month | no | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 6365 | no seizure frequency reference | unknown, 1 to 2 per cluster | yes | final_label_repaired: '1 to 2 per stimulant-associated day' -> 'no seizure frequency reference' |
| 6380 | 2 per 3 month | unknown | no | final_label_repaired: 'unknown' -> '2 per 3 month' |
| 6387 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 per travel event' -> 'no seizure frequency reference' |
| 6408 | no seizure frequency reference | unknown | yes |  |
| 6592 | unknown | unknown | yes |  |
| 6661 | 3 per 6 week | 0.5 per week | yes | final_label_repaired: '3 over 6 weeks' -> '3 per 6 week' |
| 6763 | 1 per 2 to 3 month | 1 per week | no | final_label_repaired: 'once weekly for focal-like episodes, 2 to 3 per 3 months for generalised tonic–clonic seizures' -> '1 per 2 to 3 month'; evidence_not_text_contained |
| 6775 | seizure free for 4 month | 1 per 5 month | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 6787 | 8 per 6 week | 8 per 6 week | yes | final_label_repaired: '8 events over 6 weeks' -> '8 per 6 week' |
| 6909 | 4 per 3 month | 1 per 2 to 3 weeks | yes | final_label_repaired: '1 focal event every 2 to 3 weeks, 3 generalised tonic-clonic seizures in 3 months' -> '4 per 3 month' |
| 6929 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 6930 | unknown | unknown | yes |  |
| 6976 | unknown | unknown | yes |  |
| 6979 | unknown | unknown | yes |  |
| 6986 | unknown | unknown | yes |  |
| 7005 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 7047 | no seizure frequency reference | unknown | yes | evidence_not_text_contained |
| 7061 | 2 to 3 per week | 2 per 6 week | no |  |
| 7232 | 6 to 8 per month | 6 to 8 cluster per month, multiple per cluster | yes |  |
| 7280 | multiple per day | 5 per month | no | final_label_repaired: '5 per month' -> 'multiple per day' |
| 7318 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 7327 | 2 per 4 month | 2 per 4 months | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 7328 | multiple per month | unknown | yes | final_label_repaired: 'occasional brief absence episodes' -> 'multiple per month' |
| 7341 | unknown | unknown | yes |  |
| 7386 | 2 per 8 week | 7 per 8 week | no | final_label_repaired: '7 events over 8 weeks' -> '2 per 8 week' |
| 7393 | unknown | unknown | yes |  |
| 7405 | 2 to 3 per month | 1 per multiple months | no |  |
| 7431 | 2 per 8 week | 1 per month | yes | final_label_repaired: '2 per 8 weeks' -> '2 per 8 week' |
| 7670 | multiple per day | multiple per week | yes |  |
| 7688 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 7708 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 7712 | seizure free for 3 month | 2 per 3 month | no |  |
| 7719 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7783 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7816 | seizure free for 1 month | seizure free for multiple month | yes |  |
| 7863 | unknown | seizure free for multiple month | no |  |
| 7884 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 7892 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7935 | unknown | seizure free for multiple month | no |  |
| 7958 | seizure free for 3 year | seizure free for multiple year | yes |  |
| 7987 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7993 | 2 to 3 per 2 day | unknown, 2 to 3 per cluster | no | final_label_repaired: '2 to 3 per 2 days' -> '2 to 3 per 2 day' |
| 8109 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 8116 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8127 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 8135 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8169 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8221 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8222 | seizure free for 9 month | seizure free for multiple month | yes |  |
| 8244 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8286 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8342 | seizure free for 9 month | seizure free for 9 month | yes |  |
| 8346 | seizure free for 7 month | seizure free for multiple month | yes |  |
| 8423 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 10 weeks' -> 'seizure free for multiple year' |
| 8432 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2 to 3 months' -> '1 per 2 to 3 month' |
| 8488 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8540 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_text_contained |
| 8624 | seizure free for 13 month | seizure free for 13 month | yes |  |
| 8645 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8723 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year' |
| 8790 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 8791 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year' |
| 8799 | unknown | unknown | yes |  |
| 8813 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8852 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 8858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since July 2024' -> 'seizure free for multiple year' |
| 8954 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 8957 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 8979 | seizure free for 4 year | seizure free for multiple year | yes |  |
| 9014 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 9065 | no seizure frequency reference | seizure free for 13 month | no |  |
| 9109 | unknown | unknown | yes |  |
| 9114 | 1 per 4 to 6 week | 1 per 4 to 6 week | yes | final_label_repaired: '1 per 4 to 6 weeks' -> '1 per 4 to 6 week' |
| 9147 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9179 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since mid-August' -> 'seizure free for multiple year' |
| 9189 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for an extended interval' -> 'seizure free for multiple year' |
| 9202 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9212 | seizure free for 3 month | seizure free for 3 months | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 9251 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9279 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 9294 | 3 to 4 per week | 3 to 4 per week | yes | evidence_not_text_contained |
| 9377 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 9471 | 7 per 11 month | 7 per 11 month | yes | final_label_repaired: '1 per month' -> '7 per 11 month' |
| 9483 | 8 per 6 month | 8 per 6 month | yes | final_label_repaired: '1 to 2 per month' -> '8 per 6 month' |
| 9562 | unknown | unknown | yes |  |
| 9566 | 1 to 2 per week | unknown | no |  |
| 9601 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 9618 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 9654 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9696 | unknown | unknown | yes |  |
| 9786 | unknown | unknown | yes |  |
| 9801 | 2 per year | unknown | no | final_label_repaired: 'unknown' -> '2 per year' |
| 9891 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9926 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 9942 | 1 per month | 1 cluster per month, multiple per cluster | no |  |
| 9946 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 9979 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: '3 to 4 per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10009 | 1 per week | 1 cluster per week, multiple per cluster | yes | final_label_repaired: 'weekly morning bursts' -> '1 per week' |
| 10031 | unknown | 1 cluster per week, multiple per cluster | no |  |
| 10052 | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '4 per quarter' -> '4 cluster per 3 month, multiple per cluster' |
| 10159 | unknown | unknown | yes |  |
| 10186 | no seizure frequency reference | unknown, 3 to 5 per cluster | yes | final_label_repaired: '3 to 5 per cluster' -> 'no seizure frequency reference' |
| 10213 | no seizure frequency reference | unknown, 3 per cluster | yes | final_label_repaired: '3 per cluster' -> 'no seizure frequency reference' |
| 10292 | unknown | unknown | yes |  |
| 10298 | unknown | unknown | yes |  |
| 10316 | unknown | unknown | yes |  |
| 10330 | unknown | unknown | yes |  |
| 10398 | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 2 per cluster' |
| 10408 | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 5 per cluster' |
| 10441 | multiple per week | unknown | yes |  |
| 10445 | multiple per week | 9 cluster per month, 2 to 4 per cluster | no |  |
| 10447 | multiple per week | unknown | yes |  |
| 10514 | multiple per week | unknown | yes |  |
| 10538 | unknown | unknown, 6 per cluster | yes |  |
| 10553 | unknown | unknown, 2 to 3 per cluster | yes | evidence_not_text_contained |
| 10621 | unknown | multiple cluster per week, 4 to 6 per cluster | no | final_label_repaired: 'small clusters on most evenings' -> 'unknown' |
| 10737 | unknown | unknown | yes |  |
| 10751 | unknown | unknown | yes |  |
| 10794 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 cluster days per month' -> 'unknown' |
| 10795 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10863 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster'; evidence_not_text_contained |
| 10884 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: 'weekly clusters, usually 3 to 4 events within ~2 h' -> '1 cluster per week, 3 to 4 per cluster' |
| 10908 | 4 cluster per month, 4 per cluster | 4 cluster per month, 4 per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, 4 per cluster' |
| 10931 | 6 cluster per month, 4 per cluster | 6 cluster per month, 4 per cluster | yes | final_label_repaired: '6 clusters per month' -> '6 cluster per month, 4 per cluster' |
| 10941 | 6 cluster per month, 5 per cluster | 6 cluster per month, 5 per cluster | yes | final_label_repaired: '6 clusters per month' -> '6 cluster per month, 5 per cluster' |
| 10954 | unknown | 3 cluster per month, 5 to 6 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10977 | 4 per month | 4 cluster per month, 5 per cluster | no |  |
| 10994 | 3 to 4 per month | 3 to 4 cluster per month, 3 per cluster | no |  |
| 11076 | unknown | 1 cluster per 2 months, 2 to 4 per cluster | no | final_label_repaired: '1 cluster every 2 months' -> 'unknown' |
| 11196 | 3 per month | 3 cluster per month, 5 per cluster | no |  |
| 11207 | unknown | 2 cluster per month, 6 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown' |
| 11221 | seizure free for 4 month | unknown | no | evidence_not_text_contained |
| 11334 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month'; evidence_not_text_contained |
| 11401 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11431 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11472 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11492 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11499 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11576 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11590 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11733 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11748 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11787 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11825 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11842 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11844 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11864 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11867 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11889 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_text_contained |
| 11918 | 5 per week | 5 per week | yes |  |
| 11936 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 11983 | 1 per day | 2 to 3 per day | yes | final_label_repaired: '2 to 3 per day' -> '1 per day' |
| 12005 | 2 to 6 per day | 2 to 6 per day | yes |  |
| 12060 | multiple per day | multiple per day | yes |  |
| 12080 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12090 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12169 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12173 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 12258 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12300 | 3 per week | 3 per week | yes |  |
| 12319 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 12326 | 4 per week | 4 per week | yes |  |
| 12330 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 12335 | 3 per week | 3 per week | yes |  |
| 12348 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 12392 | 4 per day | 4 per day | yes |  |
| 12504 | 1 to 2 per week | 3 per day | no |  |
| 12590 | 1 per 2 to 3 month | 1 per week | no | final_label_repaired: '1 per 2 to 3 months' -> '1 per 2 to 3 month' |
| 12643 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12645 | 1 per day | 1 per day | yes | final_label_repaired: 'daily absences' -> '1 per day' |
| 12674 | 1 per day | 1 per day | yes | final_label_repaired: 'daily absences' -> '1 per day' |
| 12778 | 8 per year | 8 per 3 month | no | final_label_repaired: 'unknown' -> '8 per year'; evidence_not_text_contained |
| 12791 | 6 per year | 6 per month | no | final_label_repaired: 'unknown' -> '6 per year' |
| 12826 | 10 per year | 10 per 4 month | no | final_label_repaired: 'unknown' -> '10 per year' |
| 12866 | 10 per year | 10 per 5 month | no | final_label_repaired: 'unknown' -> '10 per year' |
| 12919 | 5 per year | 5 per 5 month | no | final_label_repaired: '5 in 2021 so far' -> '5 per year' |
| 12948 | 7 per year | 7 per 5 month | no | final_label_repaired: '7 so far this year' -> '7 per year' |
| 12985 | 3 per year | 3 per 5 month | yes |  |
| 13043 | multiple per day | 2 per 5 month | no |  |
| 13064 | unknown | 2 per 5 month | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 13069 | multiple per week | 2 per 5 month | no |  |
| 13077 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 in 3 months' -> '2 per 3 month' |
| 13079 | multiple per week | 2 per 8 month | no |  |
| 13109 | 2 per 3 week | 2 per year | no | final_label_repaired: '2 tonic seizures per 3 weeks' -> '2 per 3 week' |
| 13162 | 1 per month | 1 per 4 month | no |  |
| 13167 | 1 per month | 1 per 3 month | no |  |
| 13183 | 1 per month | 1 per 8 month | no |  |
| 13210 | 1 per 2 week | 1 per 5 month | no | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 13266 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 13376 | seizure free for 2 year | seizure free for 2 year | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 13473 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13590 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13591 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13600 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_text_contained |
| 13611 | 71 per 11 month | 57 per 11 month | yes | final_label_repaired: 'multiple per month' -> '71 per 11 month' |
| 13645 | 85 per 12 month | 85 per 12 month | yes | final_label_repaired: 'multiple per month' -> '85 per 12 month' |
| 13753 | 47 per 9 month | 33 per 9 month | no | final_label_repaired: 'multiple per week' -> '47 per 9 month' |
| 13765 | 50 per 9 month | 50 per 9 month | yes | final_label_repaired: 'unknown' -> '50 per 9 month' |
| 13796 | seizure free for multiple year | unknown | no | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13822 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13841 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 13901 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since medication increase in May 2020' -> 'no seizure frequency reference' |
| 13912 | 2 to 3 per month | unknown | no |  |
| 13970 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 events since discharge' -> 'no seizure frequency reference' |
| 13990 | 2 to 4 per month | unknown | no | evidence_not_text_contained |
| 14009 | 2 to 3 per month | unknown | no |  |
| 14031 | no seizure frequency reference | unknown | yes | final_label_repaired: '4 drop attacks since May 2019' -> 'no seizure frequency reference' |
| 14036 | no seizure frequency reference | unknown | yes | final_label_repaired: '4 drop attacks since starting ketogenic diet' -> 'no seizure frequency reference' |
| 14081 | 2 to 3 per month | unknown | no |  |
| 14145 | 2 to 3 per month | unknown | no |  |
| 14236 | seizure free for multiple year | 4 per month | no | final_label_repaired: 'seizure free since early March 2021' -> 'seizure free for multiple year' |
| 14237 | 3 per week | 3 per month | no | final_label_repaired: '3 seizures in one week' -> '3 per week' |
| 14243 | no seizure frequency reference | 4 per month | no | final_label_repaired: '4 in one week' -> 'no seizure frequency reference' |
| 14271 | seizure free for multiple year | 2 to 3 per month | no | final_label_repaired: '2 to 3 in the week after 10 January, then seizure free' -> 'seizure free for multiple year' |
| 14306 | no seizure frequency reference | 4 per 2 month | no | final_label_repaired: '4 seizures around mid-August' -> 'no seizure frequency reference' |
| 14369 | seizure free for multiple year | 2 per 3 month | no | final_label_repaired: 'seizure free since January' -> 'seizure free for multiple year' |
| 14390 | seizure free for multiple year | 2 per 3 month | no | final_label_repaired: 'seizure free since 31 Jan 2022' -> 'seizure free for multiple year' |
| 14443 | no seizure frequency reference | 4 per 2 month | no | final_label_repaired: '4 seizures since 20 February' -> 'no seizure frequency reference' |
| 14468 | no seizure frequency reference | 2 per 6 month | no | final_label_repaired: '2 events since June 2020' -> 'no seizure frequency reference'; evidence_not_text_contained |
| 14483 | multiple per day | 4 per 2 month | no | final_label_repaired: 'unknown' -> 'multiple per day' |
| 14485 | seizure free for 1 month | 2 per 3 month | no |  |
| 14551 | multiple per month | 2 per 2 month | no | final_label_repaired: 'occasional' -> 'multiple per month' |
| 14590 | 2 per year | 2 per 6 month | no | final_label_repaired: '2 events this year' -> '2 per year' |
| 14598 | seizure free for multiple year | 5 per 8 month | no | final_label_repaired: 'seizure free since late November 2023' -> 'seizure free for multiple year' |
| 14655 | seizure free for 1 month | 2 per 2 month | no | evidence_not_text_contained |
| 14689 | seizure free for multiple year | 3 per 2 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 14792 | seizure free for 1 month | 1 per month | no | evidence_not_text_contained |
| 14823 | 1 per month | 1 per month | yes |  |
| 14824 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year' |
| 14845 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14877 | 1 per month | 1 per month | yes |  |
| 14881 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14888 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14930 | seizure free for multiple year | 1 per 3 month | no | final_label_repaired: 'seizure free for almost 3 month' -> 'seizure free for multiple year' |
| 14944 | seizure free for 2 month | 1 per 2 month | no |  |
| 14954 | seizure free for 2 month | 1 per 2 month | no | final_label_repaired: 'seizure free for nearly 2 months' -> 'seizure free for 2 month' |
| 15039 | unknown | multiple per 12 month | yes |  |
| 15113 | 2 to 3 per year | 3 to 4 per 16 month | yes |  |
| 15148 | 1 to 2 per month | 2 to 3 per 16 month | no |  |
| 15203 | unknown | multiple per 13 month | yes |  |
| 15240 | unknown | multiple cluster per 12 month, multiple per cluster | no | final_label_repaired: 'clusters of brief myoclonic jerks intermittently' -> 'unknown' |
| 15250 | unknown | multiple cluster per 15 month, multiple per cluster | no |  |
| 15255 | multiple per week | multiple cluster per 15 month, multiple per cluster | no |  |
| 15268 | 3 per 6 month | 3 per 15 month | yes | final_label_repaired: '3 per 6 months' -> '3 per 6 month' |
| 15302 | 1 to 2 per month | 1 to 2 per 14 month | no |  |
| 15385 | unknown | 1 cluster per 2 month, 3 per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 15396 | unknown | 1 cluster per 2 month, 4 per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 15399 | no seizure frequency reference | 1 cluster per 4 month, 2 to 4 per cluster | no | final_label_repaired: '2 to 4 per cluster' -> 'no seizure frequency reference'; evidence_not_text_contained |
| 15434 | 1 cluster per 5 day, 2 per cluster | 1 cluster per 5 day, 2 per cluster | yes | final_label_repaired: 'multiple per day' -> '1 cluster per 5 day, 2 per cluster' |
| 15518 | unknown | 1 cluster per 5 day, 5 per cluster | no | final_label_repaired: '5 per day during clusters' -> 'unknown' |
| 15544 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per day during clusters' -> '1 cluster per 5 day, 2 to 4 per cluster'; evidence_not_text_contained |
| 15609 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15620 | 3 per day | 3 per day | yes |  |
| 15685 | multiple per day | 1 per day | no |  |
| 15737 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15847 | 6 per week | 6 per week | yes |  |
| 15900 | 12 per 2 month | 12 per 2 month | yes | final_label_repaired: '8 per month' -> '12 per 2 month' |
| 15927 | 18 per 2 month | 18 per 2 month | yes | final_label_repaired: 'unknown' -> '18 per 2 month' |
| 16050 | 5 per month | 6 per 2 month | no |  |
| 16128 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: '4 per month' -> '10 per 3 month' |
| 16158 | 13 per 4 month | 13 per 4 month | yes | final_label_repaired: 'unknown' -> '13 per 4 month' |
| 16253 | 7 per month | 8 per 3 month | no |  |
| 16257 | 7 per 2 month | 7 per 3 month | yes | final_label_repaired: 'unknown' -> '7 per 2 month' |
| 16281 | 21 per 4 month | 21 per 4 month | yes | final_label_repaired: 'multiple per month' -> '21 per 4 month' |
| 16286 | 6 per month | 13 per 3 month | yes |  |
| 16357 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 cluster every 2 days' -> '1 per 2 day' |
| 16368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 cluster every 2 days' -> '1 per 2 day' |
| 16422 | 1 per day | 1 per 2 to 3 day | no | final_label_repaired: '2 to 3 per week' -> '1 per day' |
| 16436 | 1 per day | 1 per 3 to 4 day | no | final_label_repaired: 'multiple per week' -> '1 per day' |
| 16512 | unknown | 1 per multiple day | yes | final_label_repaired: '1 cluster every several days' -> 'unknown' |
| 16718 | unknown | 9 per 6 month | no |  |
| 16727 | unknown | 8 per 5 month | no |  |
| 16807 | unknown | 8 per 3 month | no |  |
| 16820 | unknown | 7 per 3 month | no |  |
| 16825 | 9 per 2 month | 10 per 6 month | no | final_label_repaired: 'unknown' -> '9 per 2 month' |
| 16834 | unknown | 7 per 5 month | no |  |
| 16962 | 1 per 3 month | 2 per week | no | final_label_repaired: '2 to 3 per month' -> '1 per 3 month' |
| 16964 | 1 per 2 month | 2 per week | no | final_label_repaired: '4 to 5 per 2 months' -> '1 per 2 month' |
| 16977 | 4 to 5 per month | 4 to 5 per month | yes |  |
| 16991 | multiple per month | multiple per month | yes | final_label_repaired: 'few times per month' -> 'multiple per month' |
| 17107 | unknown | 5 cluster per week, multiple per cluster | no | final_label_repaired: 'clusters on five days per week' -> 'unknown' |
| 17133 | 2 per week | 2 cluster per week, multiple per cluster | yes |  |
| 17202 | 4 per week | 4 per week | yes |  |
| 17207 | 1 per day | 3 to 4 per day | yes | final_label_repaired: '3 to 4 per day' -> '1 per day' |
| 17229 | 2 per week | 2 per week | yes |  |
| 17258 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 17292 | 1 per 3 week | 1 per 3 week | yes |  |
| 17297 | 1 per multiple week | 1 per multiple week | yes | final_label_repaired: '1 per several week' -> '1 per multiple week' |
