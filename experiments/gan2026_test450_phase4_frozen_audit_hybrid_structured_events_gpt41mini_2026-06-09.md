# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-09

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `test` split, `gan2026_split_v1`, 450 rows.
Rare full-validation reason: Phase 4 frozen test450 aggregate audit (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 6, authorized 2026-06-09): hybrid_structured_events over test450, gpt-4.1-mini.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-09T23:12:27.939056+00:00`
- Run finished UTC: `2026-06-10T00:00:29.295180+00:00`
- Wall-clock elapsed: `2880.16` seconds (`48.003` minutes)
- Throughput: `0.156241` rows/sec (`6.4` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `f4d1c2e`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl`

## Summary

- Structured records: 448 / 450
- Call failures: 0
- Parse/schema/label issues: 2
- JSON dialect repairs: 0
- Deterministic repair notes: 306
- Exact selection evidence substrings: 418 / 450
- Purist validation accuracy/micro F1 proxy: 0.8089 (364 / 450)
- Pragmatic validation accuracy/micro F1 proxy: 0.8467 (381 / 450)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 31 | 4 per day | 4 per day | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 51 | 5 per week | 5 per week | yes |  |
| 61 | 4 per week | 4 per week | yes |  |
| 115 | 7 to 8 per month | 7 to 8 per month | yes | evidence_not_exact_substring |
| 136 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 174 | 1 to 3 per day | 1 per 1 to 3 day | no | evidence_not_exact_substring |
| 176 | 1 per 6 to 7 day | 1 per 6 to 7 day | yes | final_label_repaired: '1 per week' -> '1 per 6 to 7 day' |
| 234 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 240 | 2 to 3 per month | 1 per 2 to 3 month | no |  |
| 364 | 1 per week | 1 per week | yes |  |
| 493 | 11 per month | 11 per month | yes |  |
| 503 | 11 to 28 per 3 month | 11 to 28 per 3 month | yes | final_label_repaired: '11 to 28 per quarter' -> '11 to 28 per 3 month' |
| 538 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 per 4 days' -> '1 per 4 day'; evidence_not_exact_substring |
| 610 | 2 to 3 per year | 1 per 2 to 3 month | yes |  |
| 632 | 2 to 3 per month | 1 per 1 to 2 month | no |  |
| 666 | 2 per 2 to 3 month | 2 per 2 to 3 month | yes | final_label_repaired: '2 per 2 to 3 months' -> '2 per 2 to 3 month' |
| 685 | multiple per day | 1 per day | no | final_label_repaired: '1 per day' -> 'multiple per day' |
| 714 | 2 per day | 2 per day | yes |  |
| 722 | 1 per day | 1 per day | yes |  |
| 735 | 1 per day | 1 per day | yes |  |
| 739 | multiple per week | multiple per week | yes |  |
| 748 | 2 per 4 month | 1 per 2 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 750 | multiple per week | multiple per week | yes |  |
| 803 | 1 per month | 1 per month | yes |  |
| 804 | 1 per month | 1 per month | yes |  |
| 824 | 1 per month | 1 per month | yes |  |
| 836 | 1 per year | 1 per year | yes |  |
| 841 | 1 per year | 1 per year | yes |  |
| 892 | no seizure frequency reference | 1 per 2 day | no | final_label_repaired: '2 per fortnight' -> 'no seizure frequency reference' |
| 934 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 938 | 2 per month | 1 per 2 week | yes |  |
| 1005 | 1 per 3 month | multiple per 3 month | no | final_label_repaired: '1 cluster per 3 months' -> '1 per 3 month' |
| 1017 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 1060 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 1182 | 2 to 5 per month | 6 to 14 per 3 month | yes |  |
| 1184 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | final_label_repaired: '6 to 14 per 3 months' -> '6 to 14 per 3 month' |
| 1250 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1289 | 5 to 6 per 10 month | 5 to 6 per year | yes | final_label_repaired: '5 to 6 per year' -> '5 to 6 per 10 month' |
| 1290 | 8 to 9 per 5 month | 8 to 9 per year | no | final_label_repaired: '8 to 9 per year' -> '8 to 9 per 5 month' |
| 1326 | multiple per day | multiple per day | yes |  |
| 1378 | 5 per month | 5 per month | yes | final_label_repaired: 'multiple per month' -> '5 per month' |
| 1422 | 9 per week | 9 per week | yes |  |
| 1433 | 4 per month | 4 per month | yes |  |
| 1460 | 7 per month | 7 per month | yes | final_label_repaired: '1 tonic-clonic and 6 petit mal per month' -> '7 per month' |
| 1497 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1511 | 7 per month | 7 per month | yes |  |
| 1534 | 6 per month | 9 per month | yes |  |
| 1624 | 12 per week | 12 per week | yes |  |
| 1629 | 7 per month | 12 per month | yes | final_label_repaired: '12 per month' -> '7 per month' |
| 1633 | 7 per week | 12 per week | yes | final_label_repaired: '12 per week' -> '7 per week' |
| 1656 | 5 per month | 5 per month | yes |  |
| 1683 | multiple per day | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per day' |
| 1705 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 1722 |  | 3 per 2 month | no | schema_validation_error: Input should be 'frequency_rate', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency' or 'no_reference'; evidence_not_exact_substring |
| 1736 | 1 per 6 month | 4 per 6 month | no | final_label_repaired: '4 seizures per 6 months' -> '1 per 6 month' |
| 1812 | 12 per 3 month | 12 per 3 month | yes | final_label_repaired: 'multiple per month' -> '12 per 3 month' |
| 1868 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: 'approximately 4 per month' -> '8 per 2 month' |
| 1883 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '3 per 3 months' -> '4 per 3 month' |
| 1889 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 per 6 months' -> '4 per 6 month' |
| 1898 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 per 6 months' -> '4 per 6 month' |
| 1911 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '7 events per 2 months' -> '7 per 2 month' |
| 1934 | 2 per 2 month | 7 per 2 month | no | final_label_repaired: '7 seizures per 2 months' -> '2 per 2 month' |
| 1938 | 4 per 4 month | 5 per 4 month | no | final_label_repaired: '1 per month' -> '4 per 4 month' |
| 2071 | multiple per week | multiple per week | yes |  |
| 2112 | unknown | multiple per week | yes | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 2135 | multiple per year | unknown | yes | final_label_repaired: 'occasional per year' -> 'multiple per year' |
| 2220 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2226 | 3 to 10 per 2 week | 3 to 10 per 2 week | yes | final_label_repaired: '3 to 10 per 2 weeks' -> '3 to 10 per 2 week' |
| 2246 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2262 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 2306 | 8 to 9 per month | 8 to 9 per month | yes |  |
| 2311 | 5 to 7 per month | 5 to 7 per month | yes |  |
| 2356 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2404 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 2486 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2543 | 2 to 4 per 2 week | 2 to 4 per 2 week | yes | final_label_repaired: '2 to 4 per 2 weeks' -> '2 to 4 per 2 week' |
| 2564 | 2 to 3 per month | 3 to 5 per 2 month | yes |  |
| 2596 | 2 per day | 2 per day | yes | final_label_repaired: '2 per night' -> '2 per day' |
| 2597 | 2 per day | 2 per day | yes | final_label_repaired: '2 per night' -> '2 per day' |
| 2652 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 2684 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2725 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 every 2 weeks' -> '1 per 2 week' |
| 2749 | 1 per month | 1 per month | yes |  |
| 2781 | 1 per week | 1 per week | yes |  |
| 2795 | 1 per week | 1 per week | yes |  |
| 2854 | 2 per month | 2 per month | yes |  |
| 2879 | 2 per day | 2 per day | yes |  |
| 2978 | seizure free for multiple year | seizure free for 9 month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 3054 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3102 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month'; evidence_not_exact_substring |
| 3214 | 1 cluster per month, 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | final_label_repaired: 'monthly clusters of 5 to 7 seizures per 24 hours' -> '1 cluster per month, 7 per cluster' |
| 3225 | 3 to 10 per 4 month | 1 cluster per month, 3 to 10 per cluster | no | final_label_repaired: '3 to 10 per month in clusters' -> '1 cluster per month, 10 per cluster'; final_label_repaired: '1 cluster per month, 10 per cluster' -> '3 to 10 per 4 month' |
| 3237 | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | final_label_repaired: '4 clusters per month, each with ~5 absences' -> '4 cluster per month, 5 per cluster' |
| 3246 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month, each with about 4 absences' -> '2 cluster per month, 4 per cluster' |
| 3291 | 9 per month | 9 per month | yes | final_label_repaired: '9 per 30 days' -> '9 per month' |
| 3293 | 8 per month | 8 per month | yes | final_label_repaired: '8 per 30 days' -> '8 per month' |
| 3300 | 9 per month | 9 per month | yes |  |
| 3327 | 5 to 6 per year | 5 to 6 per year | yes |  |
| 3329 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 3340 | 2 to 3 per month | 2 to 3 per month | yes |  |
| 3353 | unknown | unknown | yes | evidence_not_exact_substring |
| 3355 | 2 per 2 month | 1 per 3 month | no | final_label_repaired: '2 per 6 months' -> '2 per 6 month'; final_label_repaired: '2 per 6 month' -> '2 per 2 month' |
| 3407 | multiple per week | multiple per week | yes |  |
| 3452 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 3514 | no seizure frequency reference | unknown | yes | final_label_repaired: 'improved frequency, ~30% reduction' -> 'no seizure frequency reference' |
| 3630 | 7 per week | 7 per week | yes | final_label_repaired: 'multiple per week' -> '7 per week' |
| 3638 | 3 per week | 3 per week | yes | final_label_repaired: 'up to 3 per week (in bad weeks)' -> '3 per week' |
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
| 4003 | 1 per month | 1 per month | yes | final_label_repaired: 'about 1 per month' -> '1 per month'; evidence_not_exact_substring |
| 4004 | 1 per month | 1 per month | yes | final_label_repaired: 'absences monthly' -> '1 per month' |
| 4073 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per month' -> '1 per 2 to 3 week' |
| 4076 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per month, often clustering' -> '1 per 2 to 3 week' |
| 4197 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every 2 days' -> '1 per 2 day' |
| 4217 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every 2 days' -> '1 per 2 day' |
| 4239 | unknown | unknown | yes |  |
| 4342 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: 'multiple per month' -> '5 per 3 month' |
| 4352 | 5 per 10 month | 5 per 3 month | no | final_label_repaired: '2 to 3 per month' -> '5 per 10 month' |
| 4424 | 6 per 12 month | 3 per 6 month | yes | final_label_repaired: 'unknown' -> '6 per 12 month' |
| 4679 | multiple per day | multiple per day | yes | final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 4707 | multiple per day | multiple per day | yes |  |
| 4809 | unknown | unknown | yes | final_label_repaired: 'clusters during illness episodes' -> 'unknown' |
| 4831 | seizure free for 6 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 4892 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 4903 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4967 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 4996 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 5088 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for recent months' -> 'seizure free for multiple year' |
| 5174 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5213 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 5385 | no seizure frequency reference | seizure free for 1 year | no |  |
| 5395 | seizure free for 6 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 5505 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic jerks this year' -> 'no seizure frequency reference' |
| 5527 | 1 per 2 month | 1 per year | no | final_label_repaired: 'seizure free since late August' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 5540 | 1 per month | 1 per 4 to 5 month | no | final_label_repaired: '1 event per month' -> '1 per month' |
| 5555 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5627 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 per 5 days' -> '1 per 5 day' |
| 5653 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 5684 | unknown | unknown | yes | final_label_repaired: 'clusters over 24-48 hours' -> 'unknown' |
| 5708 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per month' -> 'unknown' |
| 5764 | 3 per month | 3 per month | yes |  |
| 5766 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 5976 | unknown | unknown | yes |  |
| 6025 | unknown | unknown | yes | final_label_repaired: '2 clusters in 6 months' -> 'unknown' |
| 6028 | unknown | 1 per 3 months | no |  |
| 6063 | 3 per month | unknown | no | final_label_repaired: 'multiple per week' -> '3 per month' |
| 6073 | 1 per 3 to 4 week | 1 per 3 to 4 weeks | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 6164 | multiple per month | unknown | yes | final_label_repaired: 'occasional absence and myoclonic jerks after prolonged screen time' -> 'multiple per month' |
| 6216 | multiple per month | 4 per 6 week | no |  |
| 6252 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 6288 | 2 per 10 week | 2 per 10 week | yes | final_label_repaired: '2 per 10 weeks' -> '2 per 10 week' |
| 6296 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6303 | multiple per multiple day | unknown | yes | final_label_repaired: 'multiple per several days' -> 'multiple per multiple day' |
| 6330 | 2 per 3 month | multiple per month | no | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 6365 | 5 per 10 month | unknown, 1 to 2 per cluster | no | final_label_repaired: '1 to 2 per month on stimulant days' -> '5 per 10 month' |
| 6380 | 2 per 3 month | unknown | no | final_label_repaired: '2 to 3 per 3 months' -> '2 per 3 month' |
| 6387 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 events since last contact' -> 'no seizure frequency reference' |
| 6408 | unknown | unknown | yes |  |
| 6592 | no seizure frequency reference | unknown | yes | final_label_repaired: 'intermittent brief generalised seizures over past two months' -> 'no seizure frequency reference' |
| 6661 | 3 per 6 week | 0.5 per week | yes | final_label_repaired: '3 per 6 weeks' -> '3 per 6 week' |
| 6763 | 1 per week | 1 per week | yes |  |
| 6775 | seizure free for 4 month | 1 per 5 month | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 6787 | 8 per 6 week | 8 per 6 week | yes | final_label_repaired: '8 per 6 weeks' -> '8 per 6 week' |
| 6909 | 4 per 3 month | 1 per 2 to 3 weeks | yes | final_label_repaired: 'multiple per month' -> '4 per 3 month' |
| 6929 | multiple per week | multiple per week | yes |  |
| 6930 | unknown | unknown | yes |  |
| 6976 | unknown | unknown | yes |  |
| 6979 | unknown | unknown | yes |  |
| 6986 | no seizure frequency reference | unknown | yes | final_label_repaired: 'intermittent in past few weeks' -> 'no seizure frequency reference' |
| 7005 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 7047 | unknown | unknown | yes |  |
| 7061 | 2 to 3 per week | 2 per 6 week | no |  |
| 7232 | no seizure frequency reference | 6 to 8 cluster per month, multiple per cluster | no | final_label_repaired: '6 to 8 days per month' -> 'no seizure frequency reference' |
| 7280 | multiple per day | 5 per month | no | final_label_repaired: '5 per month' -> 'multiple per day' |
| 7318 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 7327 | 2 per 4 month | 2 per 4 months | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 7328 | multiple per month | unknown | yes | final_label_repaired: 'occasional absence seizures' -> 'multiple per month' |
| 7341 | 2 per month | unknown | no |  |
| 7386 | 2 per 8 week | 7 per 8 week | no | final_label_repaired: 'approximately 7 seizures over 8 weeks' -> '2 per 8 week' |
| 7393 | unknown | unknown | yes | final_label_repaired: '1 cluster every few weeks' -> 'unknown' |
| 7405 | 2 to 3 per year | 1 per multiple months | no |  |
| 7431 | 2 per 8 week | 1 per month | yes | final_label_repaired: '2 per 8 weeks' -> '2 per 8 week' |
| 7670 | multiple per day | multiple per week | yes | final_label_repaired: '1 per day' -> 'multiple per day' |
| 7688 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 3 years' -> 'seizure free for multiple year' |
| 7708 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 7712 | seizure free for 3 month | 2 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7719 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7783 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 7816 | seizure free for 1 month | seizure free for multiple month | yes |  |
| 7863 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early August' -> 'seizure free for multiple year' |
| 7884 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 7892 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7935 | unknown | seizure free for multiple month | no | evidence_not_exact_substring |
| 7958 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 3 years' -> 'seizure free for multiple year' |
| 7987 | no seizure frequency reference | seizure free for multiple month | no | final_label_repaired: 'stable seizure control' -> 'no seizure frequency reference' |
| 7993 | 2 to 3 per 1 to 2 day | unknown, 2 to 3 per cluster | no | final_label_repaired: '2 to 3 per 1-2 days' -> '2 to 3 per 1 to 2 day' |
| 8109 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8116 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8127 | seizure free for 18 month | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 8135 |  | seizure free for multiple month | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 8169 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8221 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8222 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for approximately 9 months' -> 'seizure free for 9 month' |
| 8244 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 8286 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8342 | seizure free for 9 month | seizure free for 9 month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 8346 | seizure free for 7 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 7 months' -> 'seizure free for 7 month' |
| 8423 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 10 weeks' -> 'seizure free for multiple year' |
| 8432 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2-3 months' -> '1 per 2 to 3 month' |
| 8488 | 11 per 2 month | seizure free for multiple month | no | final_label_repaired: 'seizure free since April' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '11 per 2 month' |
| 8540 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; evidence_not_exact_substring |
| 8624 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8645 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 8723 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since rota change' -> 'seizure free for multiple year' |
| 8790 | 0 per 8 week | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 weeks' -> '0 per 8 week'; evidence_not_exact_substring |
| 8791 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8799 | no seizure frequency reference | unknown | yes | final_label_repaired: 'essentially 0% seizures over last 3 months' -> 'no seizure frequency reference' |
| 8813 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8852 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 8858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 8954 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free since 11 May 2021' -> 'seizure free for multiple year' |
| 8957 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free since 06/07/2016' -> 'seizure free for multiple year' |
| 8979 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 4+ years' -> 'seizure free for multiple year' |
| 9014 | seizure free for multiple year | seizure free for 11 month | yes | final_label_repaired: 'seizure free for over 11 months' -> 'seizure free for multiple year' |
| 9065 | multiple per year | seizure free for 13 month | no | final_label_repaired: 'rare brief episodes' -> 'multiple per year' |
| 9109 | no seizure frequency reference | unknown | yes | final_label_repaired: 'reduced frequency, fewer daytime episodes' -> 'no seizure frequency reference' |
| 9114 | 2 to 3 per month | 1 per 4 to 6 week | no |  |
| 9147 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9179 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since mid-August' -> 'seizure free for multiple year' |
| 9189 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for extended interval' -> 'seizure free for multiple year' |
| 9202 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 9212 | seizure free for 3 month | seizure free for 3 months | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 9251 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 12 months' -> 'seizure free for multiple year' |
| 9279 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 9294 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 9377 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '2 per month' -> '1 per 2 week' |
| 9471 | 7 per 11 month | 7 per 11 month | yes | final_label_repaired: '1 per month or less' -> '7 per 11 month' |
| 9483 | 16 per 12 month | 8 per 6 month | yes | final_label_repaired: '1 to 2 per month' -> '8 per 6 month'; final_label_repaired: '8 per 6 month' -> '16 per 12 month' |
| 9562 | 1 to 2 per 1 year | unknown | no | final_label_repaired: 'cluster over 1–2 days after illness' -> 'unknown'; final_label_repaired: 'unknown' -> '1 to 2 per 1 year' |
| 9566 | 1 to 2 per day | unknown | no |  |
| 9601 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; evidence_not_exact_substring |
| 9618 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since May 2025' -> 'seizure free for multiple year' |
| 9654 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9696 | multiple per week | unknown | yes |  |
| 9786 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased frequency over past two months' -> 'no seizure frequency reference' |
| 9801 | unknown | unknown | yes |  |
| 9891 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic focal seizures this year' -> 'no seizure frequency reference' |
| 9926 | 1 per month | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'monthly clusters' -> '1 per month' |
| 9942 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 per month during cluster periods' -> 'unknown' |
| 9946 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 9979 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: '3 to 4 clusters per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10009 | unknown | 1 cluster per week, multiple per cluster | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10031 | multiple per week | 1 cluster per week, multiple per cluster | no |  |
| 10052 | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '4 clusters per quarter' -> '4 cluster per 3 month, multiple per cluster' |
| 10159 | unknown | unknown | yes |  |
| 10186 | 3 to 5 per day | unknown, 3 to 5 per cluster | no | final_label_repaired: '3 to 5 per cluster day' -> '3 to 5 per day' |
| 10213 | unknown | unknown, 3 per cluster | yes | final_label_repaired: '3 events per cluster over 24 hours' -> 'unknown' |
| 10292 | multiple per day | unknown | yes | final_label_repaired: 'more frequent over the past six weeks' -> 'multiple per day' |
| 10298 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increase in breakthrough events over the last three months' -> 'no seizure frequency reference' |
| 10316 | no seizure frequency reference | unknown | yes | final_label_repaired: 'clustered events around off-duty days' -> 'no seizure frequency reference' |
| 10330 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 events since early May 2025' -> 'no seizure frequency reference' |
| 10398 | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 2 per cluster' |
| 10408 | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | yes | final_label_repaired: '1 cluster per week, 3 to 5 seizures per cluster' -> '1 cluster per week, 3 to 5 per cluster' |
| 10441 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 10445 | multiple per week | 9 cluster per month, 2 to 4 per cluster | no |  |
| 10447 | multiple per week | unknown | yes | final_label_repaired: 'cluster frequency several times per week' -> 'multiple per week' |
| 10514 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 in 6 weeks' -> 'no seizure frequency reference' |
| 10538 | unknown | unknown, 6 per cluster | yes | final_label_repaired: '6 per hour (cluster)' -> 'unknown' |
| 10553 | unknown | unknown, 2 to 3 per cluster | yes | final_label_repaired: '2 to 3 per hour (cluster)' -> 'unknown' |
| 10621 | multiple per week | multiple cluster per week, 4 to 6 per cluster | no |  |
| 10737 | unknown | unknown | yes |  |
| 10751 | no seizure frequency reference | unknown | yes | final_label_repaired: 'short bursts around travel' -> 'no seizure frequency reference' |
| 10794 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 cluster days per month' -> 'unknown' |
| 10795 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10863 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10884 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week, 3-4 events per cluster' -> '1 cluster per week, 3 to 4 per cluster' |
| 10908 | 4 cluster per month, 4 per cluster | 4 cluster per month, 4 per cluster | yes | final_label_repaired: '4 clusters per month, each with ~4 seizures' -> '4 cluster per month, 4 per cluster' |
| 10931 | 6 cluster per month, 4 per cluster | 6 cluster per month, 4 per cluster | yes | final_label_repaired: '6 clusters per month, each cluster ~4 seizures' -> '6 cluster per month, 4 per cluster' |
| 10941 | 6 cluster per month, 5 per cluster | 6 cluster per month, 5 per cluster | yes | final_label_repaired: 'multiple clusters per month' -> '6 cluster per month, 5 per cluster' |
| 10954 | unknown | 3 cluster per month, 5 to 6 per cluster | no | final_label_repaired: '3 clusters per month, each with ~5-6 events' -> 'unknown' |
| 10977 | unknown | 4 cluster per month, 5 per cluster | no | final_label_repaired: '4 clusters per month' -> 'unknown' |
| 10994 | 3 to 4 per 1 year | 3 to 4 cluster per month, 3 per cluster | no | final_label_repaired: '3 to 4 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 1 year' |
| 11076 | unknown | 1 cluster per 2 months, 2 to 4 per cluster | no | final_label_repaired: '1 cluster every 2 months' -> 'unknown' |
| 11196 | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster | yes | final_label_repaired: '3 clusters per month, ~5 events per cluster' -> '3 cluster per month, 5 per cluster' |
| 11207 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 clusters per month, ~6 events per cluster' -> '2 cluster per month, 6 per cluster' |
| 11221 | 1 per 5 month | unknown | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free for 4 month' -> '1 per 5 month' |
| 11334 | no seizure frequency reference | 1 per 2 month | no | final_label_repaired: '1 seizure since 23-Jun' -> 'no seizure frequency reference' |
| 11401 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11431 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11472 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11492 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11499 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11576 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11590 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11733 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11748 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11787 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11825 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11842 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11844 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11864 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11867 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11889 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11918 | unknown | 5 per week | no | final_label_repaired: '5 per week with occasional clusters' -> 'unknown' |
| 11936 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 11983 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 12005 | 2 to 6 per day | 2 to 6 per day | yes | final_label_repaired: '2 to 6 per day, sometimes clustered' -> '2 to 6 per day' |
| 12060 | multiple per day | multiple per day | yes |  |
| 12080 | multiple per week | multiple per week | yes |  |
| 12090 | multiple per week | multiple per week | yes |  |
| 12169 | multiple per week | multiple per week | yes |  |
| 12173 | multiple per week | multiple per week | yes |  |
| 12258 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12300 | 3 per week | 3 per week | yes |  |
| 12319 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 12326 | 4 per week | 4 per week | yes |  |
| 12330 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 12335 | 3 per week | 3 per week | yes |  |
| 12348 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 12392 | 4 per day | 4 per day | yes | evidence_not_exact_substring |
| 12504 | 1 to 2 per week | 3 per day | no |  |
| 12590 | 1 per 2 to 3 month | 1 per week | no | final_label_repaired: '1 per 2-3 months' -> '1 per 2 to 3 month' |
| 12643 | 1 to 2 per week | 1 per day | no |  |
| 12645 | 1 per day | 1 per day | yes |  |
| 12674 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12778 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '8 per year' -> '8 per 3 month' |
| 12791 | 6 per month | 6 per month | yes | final_label_repaired: '6 per year' -> '6 per month' |
| 12826 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12866 | 10 per 5 month | 10 per 5 month | yes | final_label_repaired: '10 per year' -> '10 per 5 month' |
| 12919 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12948 | 7 per 5 month | 7 per 5 month | yes | final_label_repaired: '7 per year' -> '7 per 5 month' |
| 12985 | 3 per year | 3 per 5 month | yes |  |
| 13043 | 10 to 20 per 5 month | 2 per 5 month | no | final_label_repaired: 'cluster of absences several times that morning plus 1 tonic-clonic seizure 2 weeks ago' -> 'unknown'; final_label_repaired: 'unknown' -> '10 to 20 per 5 month'; evidence_not_exact_substring |
| 13064 | 1 per 5 month | 2 per 5 month | yes | final_label_repaired: '1 generalised tonic-clonic seizure 2 weeks ago with preceding cluster of absences, no further events since' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 5 month'; evidence_not_exact_substring |
| 13069 | 2 per 5 month | 2 per 5 month | yes | final_label_repaired: '1 cluster per 2 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 5 month' |
| 13077 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 seizures in 3 months' -> '2 per 3 month'; evidence_not_exact_substring |
| 13079 | 1 per 8 month | 2 per 8 month | no | final_label_repaired: '1 generalised tonic-clonic seizure three weeks ago plus cluster of absences over preceding weekend' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 8 month' |
| 13109 | 2 per 1 year | 2 per year | yes | final_label_repaired: '2 tonic seizures three weeks ago' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 1 year' |
| 13162 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 seizure three weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 4 month' |
| 13167 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 focal impaired-awareness seizure 3 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 3 month' |
| 13183 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 event 3 weeks ago' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per 8 month' |
| 13210 | 1 per 2 week | 1 per 5 month | no | final_label_repaired: '1 seizure in 2 weeks' -> '1 per 2 week' |
| 13266 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 13376 | seizure free for 2 year | seizure free for 2 year | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 13473 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13590 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13591 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13600 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13611 | 9 per 4 month | 57 per 11 month | no | final_label_repaired: 'multiple per month' -> '71 per 11 month'; final_label_repaired: '71 per 11 month' -> '9 per 4 month' |
| 13645 | 46 per 4 month | 85 per 12 month | yes | final_label_repaired: 'multiple days per month, up to 12 days' -> '85 per 12 month'; final_label_repaired: '85 per 12 month' -> '46 per 4 month' |
| 13753 | 10 per 6 month | 33 per 9 month | yes | final_label_repaired: 'multiple per month' -> '47 per 9 month'; final_label_repaired: '47 per 9 month' -> '10 per 6 month' |
| 13765 | 14 per 5 month | 50 per 9 month | no | final_label_repaired: '4 to 10 days per month' -> '50 per 9 month'; final_label_repaired: '50 per 9 month' -> '14 per 5 month' |
| 13796 | seizure free for multiple year | unknown | no | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13822 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13841 | seizure free for 6 month | seizure free for 6 months | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 13901 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since medication increase' -> 'no seizure frequency reference' |
| 13912 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 3 per recent period' -> 'no seizure frequency reference' |
| 13970 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since discharge (recent)' -> 'no seizure frequency reference' |
| 13990 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 4 seizures since discharge' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 14009 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 since ketogenic diet start' -> 'no seizure frequency reference' |
| 14031 | no seizure frequency reference | unknown | yes | final_label_repaired: '4 drop attacks since May 2019' -> 'no seizure frequency reference' |
| 14036 | no seizure frequency reference | unknown | yes | final_label_repaired: '4 drop attacks since ketogenic diet start' -> 'no seizure frequency reference' |
| 14081 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 3 myoclonic jerks since last appointment' -> 'no seizure frequency reference' |
| 14145 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 3 per recent period' -> 'no seizure frequency reference' |
| 14236 | 4 per 1 month | 4 per month | yes | final_label_repaired: 'seizure free since late February 2021' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '4 per 1 month' |
| 14237 | 3 per 1 month | 3 per month | yes | final_label_repaired: '3 per week' -> '3 per 1 month' |
| 14243 | 4 per 1 month | 4 per month | yes | final_label_repaired: '4 per week' -> '4 per 1 month' |
| 14271 | 2 to 3 per 1 month | 2 to 3 per month | yes | final_label_repaired: '2 to 3 per week' -> '2 to 3 per 1 month' |
| 14306 | 4 per 2 month | 4 per 2 month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '4 per 2 month' |
| 14369 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: 'seizure free since January' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14390 | seizure free for multiple year | 2 per 3 month | no | final_label_repaired: 'seizure free for over 3 months' -> 'seizure free for multiple year' |
| 14443 | no seizure frequency reference | 4 per 2 month | no | final_label_repaired: '4 seizures since 20 Feb' -> 'no seizure frequency reference' |
| 14468 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'unknown' -> '2 per 6 month' |
| 14483 | 4 per 2 month | 4 per 2 month | yes | final_label_repaired: '4 seizures over 3 months' -> '4 per 3 month'; final_label_repaired: '4 per 3 month' -> '4 per 2 month' |
| 14485 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: 'seizure free since July 2019' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14551 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'occasional' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '2 per 2 month' |
| 14590 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per year' -> '2 per 12 month'; final_label_repaired: '2 per 12 month' -> '2 per 7 month'; final_label_repaired: '2 per 7 month' -> '2 per 6 month' |
| 14598 | 5 per 8 month | 5 per 8 month | yes | final_label_repaired: 'seizure free since late November 2023' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '10 per 10 month'; final_label_repaired: '10 per 10 month' -> '5 per 8 month' |
| 14655 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month'; final_label_repaired: '1 per 2 month' -> '2 per 2 month'; evidence_not_exact_substring |
| 14689 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: 'seizure free since early February 2017' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 2 month' |
| 14792 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14823 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14824 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14845 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3+ weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14877 | 1 per month | 1 per month | yes |  |
| 14881 | 29 per 2 month | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '29 per 2 month' |
| 14888 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14930 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free since 23-May' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month' |
| 14944 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free since 10 March' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 14954 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for nearly 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '1 per 2 month' |
| 15039 | unknown | multiple per 12 month | yes |  |
| 15113 | 2 to 3 per 16 month | 3 to 4 per 16 month | no | final_label_repaired: '2 to 3 per year' -> '2 to 3 per 16 month' |
| 15148 | 1 to 2 per 16 month | 2 to 3 per 16 month | yes | final_label_repaired: '1 to 2 per month' -> '1 to 2 per 16 month' |
| 15203 | no seizure frequency reference | multiple per 13 month | yes | final_label_repaired: 'brief jumps from time to time' -> 'no seizure frequency reference' |
| 15240 | 2017 per 9 month | multiple cluster per 12 month, multiple per cluster | no | final_label_repaired: 'intermittent myoclonic jerks and occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '2017 per 9 month'; evidence_not_exact_substring |
| 15250 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15255 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters per week' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15268 | 3 per 15 month | 3 per 15 month | yes | final_label_repaired: 'infrequent single jerks' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 15 month' |
| 15302 | 1 to 2 per 14 month | 1 to 2 per 14 month | yes | final_label_repaired: '1 to 2 per day' -> '1 to 2 per 14 month' |
| 15385 | 3 per 2 month | 1 cluster per 2 month, 3 per cluster | yes | final_label_repaired: '3 seizures per day in clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 2 month' |
| 15396 | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | yes | final_label_repaired: '1 cluster of 4 seizures per day' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15399 | 2 to 4 per day | 1 cluster per 4 month, 2 to 4 per cluster | no | final_label_repaired: '2 to 4 seizures per cluster day' -> '2 to 4 per day' |
| 15434 | 1 cluster per 5 day, 2 per cluster | 1 cluster per 5 day, 2 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 2 per cluster' |
| 15518 | 1 cluster per 5 day, 5 per cluster | 1 cluster per 5 day, 5 per cluster | yes | final_label_repaired: 'multiple per day' -> '1 cluster per 5 day, 5 per cluster' |
| 15544 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per day in clusters' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15609 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15620 | 3 per day | 3 per day | yes |  |
| 15685 | multiple per week | 1 per day | no |  |
| 15737 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15847 | 6 per week | 6 per week | yes |  |
| 15900 | 12 per 2 month | 12 per 2 month | yes | final_label_repaired: '8 per month' -> '12 per 2 month' |
| 15927 | 18 per 2 month | 18 per 2 month | yes | final_label_repaired: 'multiple per week' -> '18 per 2 month' |
| 16050 | 6 per 2 month | 6 per 2 month | yes | final_label_repaired: '5 per month' -> '6 per 2 month' |
| 16128 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: '2 to 4 per month' -> '10 per 3 month' |
| 16158 | 13 per 4 month | 13 per 4 month | yes | final_label_repaired: '2 per month' -> '13 per 4 month' |
| 16253 | 1 per 2 month | 8 per 3 month | no | final_label_repaired: 'multiple per month' -> '8 per 3 month'; final_label_repaired: '8 per 3 month' -> '1 per 2 month' |
| 16257 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 per month' -> '7 per 3 month' |
| 16281 | 15 per 3 month | 21 per 4 month | yes | final_label_repaired: 'multiple per month' -> '21 per 4 month'; final_label_repaired: '21 per 4 month' -> '15 per 3 month' |
| 16286 | 7 per 2 month | 13 per 3 month | no | final_label_repaired: 'multiple per week' -> '7 per 2 month' |
| 16357 | 2 per 2 month | 1 per 2 day | no | final_label_repaired: '1 cluster every 2 days' -> '1 per 2 day'; final_label_repaired: '1 per 2 day' -> '2 per 2 month' |
| 16368 | 2 per 2 month | 1 per 2 day | no | final_label_repaired: '1 cluster every 2 days' -> '1 per 2 day'; final_label_repaired: '1 per 2 day' -> '2 per 2 month' |
| 16422 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: 'daily' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 to 3 day' |
| 16436 | 1 per day | 1 per 3 to 4 day | no |  |
| 16512 | 1 per multiple day | 1 per multiple day | yes | final_label_repaired: '1 cluster every several days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per multiple day' |
| 16718 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '7 per month' -> '9 per 6 month' |
| 16727 | 8 per 5 month | 8 per 5 month | yes | final_label_repaired: '1 per month' -> '8 per 5 month' |
| 16807 | 8 per 2 month | 8 per 3 month | no | final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 16820 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '5 per month' -> '7 per 3 month' |
| 16825 | 10 per 4 month | 10 per 6 month | yes | final_label_repaired: 'unknown' -> '10 per 4 month' |
| 16834 | 7 per 5 month | 7 per 5 month | yes | final_label_repaired: '3 per month' -> '7 per 5 month' |
| 16962 | 1 per 3 month | 2 per week | no | final_label_repaired: '2 to 3 per 3 months' -> '1 per 3 month' |
| 16964 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 to 3 per month' -> '1 per 2 month' |
| 16977 | 4 to 5 per month | 4 to 5 per month | yes |  |
| 16991 | multiple per month | multiple per month | yes | final_label_repaired: 'few times per month' -> 'multiple per month' |
| 17107 | unknown | 5 cluster per week, multiple per cluster | no | final_label_repaired: 'clusters 5 days per week' -> 'unknown' |
| 17133 | unknown | 2 cluster per week, multiple per cluster | no | final_label_repaired: '2 days per week clusters' -> 'unknown' |
| 17202 | 4 per week | 4 per week | yes |  |
| 17207 | 1 per day | 3 to 4 per day | yes | final_label_repaired: '3 to 4 per day' -> '1 per day' |
| 17229 | 2 per week | 2 per week | yes |  |
| 17258 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 17292 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 17297 | 1 per multiple week | 1 per multiple week | yes | final_label_repaired: '1 per several weeks' -> '1 per multiple week' |
