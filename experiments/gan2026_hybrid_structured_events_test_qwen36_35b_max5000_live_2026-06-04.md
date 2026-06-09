# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-04

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `test` split, `gan2026_split_v1`, 450 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_llm_only_structured_events_v0.5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `False`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-04T05:48:27.974325+00:00`
- Run finished UTC: `2026-06-04T18:05:14.649550+00:00`
- Wall-clock elapsed: `44204.513` seconds (`736.742` minutes)
- Throughput: `0.01018` rows/sec (`98.232` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `93aab1a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_structured_events_test_qwen36_35b_max5000_live_2026-06-04.jsonl`

## Summary

- Structured records: 438 / 450
- Call failures: 0
- Parse/schema/label issues: 12
- JSON dialect repairs: 173
- Deterministic repair notes: 307
- Exact selection evidence substrings: 377 / 450
- Purist validation accuracy/micro F1 proxy: 0.7489 (337 / 450)
- Pragmatic validation accuracy/micro F1 proxy: 0.7911 (356 / 450)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 31 | 4 per day | 4 per day | yes | final_label_repaired: '≤ 4 per day' -> '4 per day'; evidence_not_exact_substring |
| 51 | 5 per week | 5 per week | yes | json_dialect_repaired: python_literal |
| 61 | 4 per week | 4 per week | yes |  |
| 115 | 7 to 8 per month | 7 to 8 per month | yes | final_label_repaired: '≤ 7 to 8 per month' -> '7 to 8 per month' |
| 136 | 6 to 7 per month | 6 to 7 per month | yes | final_label_repaired: '≤ 6 or 7 per month' -> '6 to 7 per month' |
| 174 | 1 to 3 per day | 1 per 1 to 3 day | no |  |
| 176 | 1 per 6 to 7 day | 1 per 6 to 7 day | yes | final_label_repaired: '1 per week' -> '1 per 6 to 7 day' |
| 234 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 240 | 2 to 3 per month | 1 per 2 to 3 month | no |  |
| 364 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal |
| 493 | 11 per month | 11 per month | yes | json_dialect_repaired: python_literal |
| 503 | 11 to 28 per 3 month | 11 to 28 per 3 month | yes | final_label_repaired: '11 to 28 per quarter' -> '11 to 28 per 3 month' |
| 538 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 610 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2 to 3 months' -> '1 per 2 to 3 month' |
| 632 | 46 per 12 month | 1 per 1 to 2 month | no | final_label_repaired: '1 per 1-2 months' -> '1 per 1 to 2 month'; final_label_repaired: '1 per 1 to 2 month' -> '46 per 12 month' |
| 666 | 1 per 2 to 3 month | 2 per 2 to 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 2-3 months' -> '1 per 2 to 3 month' |
| 685 | multiple per day | 1 per day | no | final_label_repaired: '1 per day' -> 'multiple per day'; evidence_not_exact_substring |
| 714 | 2 per day | 2 per day | yes |  |
| 722 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 735 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal |
| 739 | no seizure frequency reference | multiple per week | yes | final_label_repaired: 'most days of the week' -> 'no seizure frequency reference' |
| 748 | 2 per 4 month | 1 per 2 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 750 | multiple per day | multiple per week | yes | json_dialect_repaired: python_literal |
| 803 | 1 per month | 1 per month | yes |  |
| 804 | multiple per month | 1 per month | no | final_label_repaired: 'at most 1 per month' -> 'multiple per month' |
| 824 | 1 per month | 1 per month | yes |  |
| 836 | 1 per year | 1 per year | yes |  |
| 841 | 1 per year | 1 per year | yes | evidence_not_exact_substring |
| 892 | no seizure frequency reference | 1 per 2 day | no | final_label_repaired: '2 per fortnight' -> 'no seizure frequency reference' |
| 934 | no seizure frequency reference | 1 per 2 week | no | json_dialect_repaired: python_literal; final_label_repaired: 'roughly every fortnight' -> 'no seizure frequency reference' |
| 938 | 2 per week | 1 per 2 week | no | json_dialect_repaired: python_literal |
| 1005 | 1 per 3 month | multiple per 3 month | no | final_label_repaired: '1 cluster per 3 months' -> '1 per 3 month' |
| 1017 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 1060 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 1182 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '6 to 14 per 3 months' -> '6 to 14 per 3 month' |
| 1184 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | final_label_repaired: '6-14 per 3 months' -> '6 to 14 per 3 month'; evidence_not_exact_substring |
| 1250 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1289 |  | 5 to 6 per year | no | schema_validation_error: Field required; evidence_not_exact_substring |
| 1290 | 8 to 9 per 5 month | 8 to 9 per year | no | json_dialect_repaired: python_literal; final_label_repaired: '8 to 9 per year' -> '8 to 9 per 5 month' |
| 1326 | multiple per day | multiple per day | yes | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 1378 | 5 per month | 5 per month | yes | json_dialect_repaired: python_literal |
| 1422 | 9 per week | 9 per week | yes |  |
| 1433 | 4 per month | 4 per month | yes | json_dialect_repaired: python_literal |
| 1460 | 7 per month | 7 per month | yes |  |
| 1497 | 2 per month | 3 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per month' -> '2 per month' |
| 1511 | 7 per month | 7 per month | yes | json_dialect_repaired: python_literal |
| 1534 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 1624 | 12 per week | 12 per week | yes | json_dialect_repaired: python_literal |
| 1629 | 7 per month | 12 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '12 per month' -> '7 per month' |
| 1633 | 7 per week | 12 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '12 per week' -> '7 per week' |
| 1656 | 5 per month | 5 per month | yes | json_dialect_repaired: python_literal |
| 1683 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 1705 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: 'cluster' -> 'unknown' |
| 1722 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 events in 2 months' -> '3 per 2 month' |
| 1736 | 1 per 6 month | 4 per 6 month | no | final_label_repaired: '4 in the past six months' -> '1 per 6 month' |
| 1812 | 12 per 3 month | 12 per 3 month | yes | final_label_repaired: '12 events in the past three months' -> '12 per 3 month' |
| 1868 | 8 per 2 month | 8 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '8 in 2 months' -> '8 per 2 month' |
| 1883 | 4 per 3 month | 4 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 seizures per 3 months' -> '4 per 3 month' |
| 1889 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 seizures in the past six months' -> '4 per 6 month' |
| 1898 | 4 per 6 month | 4 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 seizures in 6 months' -> '4 per 6 month' |
| 1911 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '7 events in the past two months' -> '7 per 2 month' |
| 1934 | 2 per 2 month | 7 per 2 month | no | json_dialect_repaired: python_literal; final_label_repaired: '7 seizures in 2 months' -> '2 per 2 month' |
| 1938 | 5 per 4 month | 5 per 4 month | yes | final_label_repaired: '5 seizures in 4 months' -> '5 per 4 month' |
| 2071 | multiple per day | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per day' |
| 2112 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 2135 | no seizure frequency reference | unknown | yes | final_label_repaired: 'occasional' -> 'no seizure frequency reference' |
| 2220 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2226 | 3 to 10 per 2 week | 3 to 10 per 2 week | yes | final_label_repaired: '3 to 10 per 2 weeks' -> '3 to 10 per 2 week' |
| 2246 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: '7 to 8 per 3 weeks' -> '7 to 8 per 3 week' |
| 2262 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 to 9 per 3 weeks' -> '7 to 9 per 3 week' |
| 2306 | 8 to 9 per month | 8 to 9 per month | yes |  |
| 2311 | 5 to 7 per month | 5 to 7 per month | yes |  |
| 2356 | 6 to 7 per week | 6 to 7 per week | yes | json_dialect_repaired: python_literal |
| 2404 | 6 to 7 per month | 6 to 7 per month | yes | json_dialect_repaired: python_literal |
| 2486 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2543 | 2 to 4 per 2 week | 2 to 4 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 per 2 weeks' -> '2 to 4 per 2 week' |
| 2564 | 3 to 5 per 2 month | 3 to 5 per 2 month | yes | final_label_repaired: '3 to 5 per 2 months' -> '3 to 5 per 2 month' |
| 2596 | 2 per day | 2 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per night' -> '2 per day' |
| 2597 | multiple per day | 2 per day | no | final_label_repaired: 'multiple per night' -> 'multiple per day' |
| 2652 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal |
| 2684 | 1 per day | 1 per day | yes | final_label_repaired: 'every night' -> '1 per day' |
| 2725 | 1 per 2 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 2 week'; evidence_not_exact_substring |
| 2749 | 1 per month | 1 per month | yes |  |
| 2781 | 1 per week | 1 per week | yes | json_dialect_repaired: python_literal |
| 2795 | 1 per week | 1 per week | yes |  |
| 2854 | 2 per month | 2 per month | yes | json_dialect_repaired: python_literal |
| 2879 | 2 per day | 2 per day | yes |  |
| 2978 | seizure free for multiple year | seizure free for 9 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3054 | seizure free for 16 month | seizure free for 16 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3102 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3214 | 1 cluster per month, 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | final_label_repaired: 'monthly clusters of 5-7 seizures' -> '1 cluster per month, 7 per cluster' |
| 3225 | 1 cluster per month, 10 per cluster | 1 cluster per month, 3 to 10 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'monthly clusters of 3-10 seizures' -> '1 cluster per month, 10 per cluster' |
| 3237 | 4 cluster per month, multiple per cluster | 4 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 3246 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3291 | 9 per month | 9 per month | yes |  |
| 3293 | 8 per month | 8 per month | yes | json_dialect_repaired: python_literal |
| 3300 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 3327 | 5 to 6 per year | 5 to 6 per year | yes |  |
| 3329 | 2 to 3 per day | 2 to 3 per day | yes | json_dialect_repaired: python_literal |
| 3340 | 2 to 3 per month | 2 to 3 per month | yes | json_dialect_repaired: python_literal |
| 3353 | unknown | unknown | yes | evidence_not_exact_substring |
| 3355 | 2 per 6 month | 1 per 3 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 3407 | 1 per week | multiple per week | no | final_label_repaired: 'majority of nights each week' -> '1 per week' |
| 3452 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 3514 | unknown | unknown | yes |  |
| 3630 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 per week' -> '7 per week' |
| 3638 | 3 per week | 3 per week | yes | final_label_repaired: 'up to 3 per week' -> '3 per week' |
| 3675 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 3706 | 6 per week | 6 per week | yes |  |
| 3747 | 3 per day | 3 per day | yes | evidence_not_exact_substring |
| 3831 | 7 per month | 7 per month | yes | json_dialect_repaired: python_literal |
| 3864 | 3 per day | 3 per day | yes |  |
| 3867 | 3 per day | 3 per day | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 3888 | 8 per year | 8 per year | yes |  |
| 3906 | 4 per year | 4 per year | yes |  |
| 3918 | 9 per week | 9 per week | yes |  |
| 3934 | 9 per week | 9 per week | yes |  |
| 4003 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal |
| 4004 | unknown | 1 per month | no |  |
| 4073 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4076 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 to 2 per month' -> '1 per 2 to 3 week' |
| 4197 | no seizure frequency reference | 1 per 2 day | no | final_label_repaired: 'approximately every second day' -> 'no seizure frequency reference' |
| 4217 | 1 per day | 1 per 2 day | no | final_label_repaired: '1 per day every other day' -> '1 per day' |
| 4239 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 4342 | 5 per 6 month | 5 per 3 month | no | final_label_repaired: '5 events in 6 months' -> '5 per 6 month' |
| 4352 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '5 events in past 3 months' -> '5 per 3 month' |
| 4424 | 6 per 12 month | 3 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free since February 2014' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '6 per 12 month' |
| 4679 | no seizure frequency reference | multiple per day | yes | final_label_repaired: '10 per hour' -> 'no seizure frequency reference' |
| 4707 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 4809 | unknown | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'cluster' -> 'unknown' |
| 4831 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 4892 | seizure free for 11 month | seizure free for 11 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 4903 | seizure free for 1 year | seizure free for 1 year | yes | json_dialect_repaired: python_literal |
| 4967 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for many months' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 4996 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5088 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5174 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5213 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5385 | seizure free for multiple year | seizure free for 1 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5395 | seizure free for multiple year | seizure free for 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 6 month' -> 'seizure free for multiple year' |
| 5505 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 5527 | seizure free for 6 month | 1 per year | no | evidence_not_exact_substring |
| 5540 | seizure free for multiple year | 1 per 4 to 5 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 5555 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several per week' -> 'multiple per week' |
| 5627 | 1 per 5 day | 1 per 5 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 5 days' -> '1 per 5 day' |
| 5653 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 5684 | multiple per week | unknown | yes |  |
| 5708 | unknown | unknown | yes | final_label_repaired: 'multiple per week (clusters)' -> 'unknown'; evidence_not_exact_substring |
| 5764 | 3 per month | 3 per month | yes |  |
| 5766 | 1 per 3 to 4 week | multiple per week | no | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> '1 per 3 to 4 week' |
| 5976 | unknown | unknown | yes |  |
| 6025 | unknown | unknown | yes | final_label_repaired: '2 clusters in 6 months' -> 'unknown' |
| 6028 | seizure free for multiple year | 1 per 3 months | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 6063 | 3 per 2 week | unknown | no | final_label_repaired: 'multiple per week' -> '3 per 2 week'; evidence_not_exact_substring |
| 6073 | 1 per 3 to 4 week | 1 per 3 to 4 weeks | yes | final_label_repaired: '1 per 3-4 weeks' -> '1 per 3 to 4 week' |
| 6164 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional' -> 'no seizure frequency reference' |
| 6216 | no seizure frequency reference | 4 per 6 week | no | final_label_repaired: '5 in 6 weeks' -> 'no seizure frequency reference' |
| 6252 | 2 to 4 per month | 2 to 4 per month | yes | json_dialect_repaired: python_literal |
| 6288 | no seizure frequency reference | 2 per 10 week | no | json_dialect_repaired: python_literal; final_label_repaired: '2 in 10 weeks' -> 'no seizure frequency reference' |
| 6296 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 over 4 months' -> '3 per 4 month' |
| 6303 | no seizure frequency reference | unknown | yes | final_label_repaired: 'multiple episodes over several days' -> 'no seizure frequency reference' |
| 6330 | multiple per week | multiple per month | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 6365 | 10 per 20 month | unknown, 1 to 2 per cluster | no | final_label_repaired: '1 to 2 per week' -> '10 per 20 month' |
| 6380 | 2 per 3 month | unknown | no | final_label_repaired: 'multiple per month' -> '2 per 3 month' |
| 6387 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 recent seizures' -> 'no seizure frequency reference' |
| 6408 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6592 | no seizure frequency reference | unknown | yes | final_label_repaired: 'occasional' -> 'no seizure frequency reference' |
| 6661 | 3 per 6 week | 0.5 per week | yes | final_label_repaired: '3 per 6 weeks' -> '3 per 6 week' |
| 6763 | 1 per 2 to 3 month | 1 per week | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 2 to 3 month' |
| 6775 | 0 per 2 month | 1 per 5 month | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free for 4 month' -> '0 per 2 month'; evidence_not_exact_substring |
| 6787 | 8 per 6 week | 8 per 6 week | yes | final_label_repaired: '8 events in 6 weeks' -> '8 per 6 week' |
| 6909 | 4 per 3 month | 1 per 2 to 3 weeks | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 per 3 months' -> '4 per 3 month' |
| 6929 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 6930 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 6976 | unknown | unknown | yes |  |
| 6979 |  | unknown | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 6986 | unknown | unknown | yes |  |
| 7005 | 2 per 6 month | 2 per 6 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 in 6 months' -> '2 per 6 month' |
| 7047 | unknown | unknown | yes |  |
| 7061 | 2 to 3 per week | 2 per 6 week | no |  |
| 7232 | 6 to 8 per month | 6 to 8 cluster per month, multiple per cluster | yes |  |
| 7280 | multiple per day | 5 per month | no | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 7318 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2-3 weeks' -> '1 per 2 to 3 week' |
| 7327 | no seizure frequency reference | 2 per 4 months | no | json_dialect_repaired: python_literal; final_label_repaired: '2 over 4 months' -> 'no seizure frequency reference' |
| 7328 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 7341 | 2 per month | unknown | no | json_dialect_repaired: python_literal |
| 7386 | 2 per 8 week | 7 per 8 week | no | json_dialect_repaired: python_literal; final_label_repaired: '7 seizures in 8 weeks' -> '2 per 8 week' |
| 7393 | multiple per week | unknown | yes |  |
| 7405 | no seizure frequency reference | 1 per multiple months | yes | final_label_repaired: 'every few months' -> 'no seizure frequency reference' |
| 7431 | 2 per 8 week | 1 per month | yes | final_label_repaired: '2 per 8 weeks' -> '2 per 8 week' |
| 7670 | multiple per day | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'daily' -> 'multiple per day'; evidence_not_exact_substring |
| 7688 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 7708 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7712 | seizure free for 3 month | 2 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7719 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7783 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7816 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7863 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7884 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7892 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; evidence_not_exact_substring |
| 7935 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 7958 | seizure free for 3 year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 3 years' -> 'seizure free for 3 year' |
| 7987 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7993 | no seizure frequency reference | unknown, 2 to 3 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 3 per 24-48 hours' -> 'no seizure frequency reference' |
| 8109 | seizure free for 12 month | seizure free for 12 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8116 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8127 | seizure free for 18 month | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 8135 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8169 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8221 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8222 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 8244 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8286 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8342 | seizure free for 9 month | seizure free for 9 month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 8346 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8423 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 10 weeks' -> 'seizure free for multiple year' |
| 8432 | seizure free for 6 month | 1 per 2 to 3 month | no |  |
| 8488 | 11 per 2 month | seizure free for multiple month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '11 per 2 month' |
| 8540 | seizure free for 3 month | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8624 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8645 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8723 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8790 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8791 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year' |
| 8799 | seizure free for multiple year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8813 | 0 per 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> '0 per 3 month' |
| 8852 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 8858 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8954 | seizure free for multiple year | seizure free for 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8957 | seizure free for multiple year | seizure free for 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 8979 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9014 | seizure free for multiple year | seizure free for 11 month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 9065 | seizure free for 1 year | seizure free for 13 month | yes | evidence_not_exact_substring |
| 9109 | no seizure frequency reference | unknown | yes | final_label_repaired: 'decreased frequency' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 9114 | 1 per 4 to 6 week | 1 per 4 to 6 week | yes | final_label_repaired: '1 per 4-6 weeks' -> '1 per 4 to 6 week' |
| 9147 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9179 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9189 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9202 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9212 | seizure free for 3 month | seizure free for 3 months | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 9251 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9279 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 9294 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 9377 | 1 per 2 week | 1 per 2 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 2 weeks' -> '1 per 2 week'; evidence_not_exact_substring |
| 9471 | 14 per 22 month | 7 per 11 month | yes | final_label_repaired: 'rare (0-1 per month)' -> '0 per 2 month'; final_label_repaired: '0 per 2 month' -> '14 per 22 month'; evidence_not_exact_substring |
| 9483 | 8 per 6 month | 8 per 6 month | yes | final_label_repaired: '1 to 2 per month' -> '8 per 6 month' |
| 9562 | 1 to 2 per 1 year | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters over 1-2 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 to 2 per 1 year'; evidence_not_exact_substring |
| 9566 | 1 to 2 per 8 week | unknown | no | final_label_repaired: '1 to 2 per episode' -> '1 to 2 per 8 week' |
| 9601 | seizure free for multiple year | seizure free for multiple month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9618 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9654 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9696 | unknown | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 9786 | no seizure frequency reference | unknown | yes | final_label_repaired: 'increased frequency' -> 'no seizure frequency reference'; evidence_not_exact_substring |
| 9801 | unknown | unknown | yes | evidence_not_exact_substring |
| 9891 | unknown | unknown | yes |  |
| 9926 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 9942 | 1 per month | 1 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal |
| 9946 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 9979 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: '3 to 4 clusters per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10009 | 1 per week | 1 cluster per week, multiple per cluster | yes | final_label_repaired: 'weekly' -> '1 per week' |
| 10031 | unknown | 1 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal |
| 10052 | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '4 clusters per quarter' -> '4 cluster per 3 month, multiple per cluster' |
| 10159 | unknown | unknown | yes | json_dialect_repaired: python_literal |
| 10186 | 3 to 5 per 12 month | unknown, 3 to 5 per cluster | no | final_label_repaired: 'sporadic clusters of 3-5 events' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 5 per 12 month' |
| 10213 | multiple per week | unknown, 3 per cluster | yes | json_dialect_repaired: python_literal |
| 10292 | multiple per week | unknown | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10298 | 2 per 3 month | unknown | no | final_label_repaired: 'unknown' -> '2 per 3 month'; evidence_not_exact_substring |
| 10316 | unknown | unknown | yes | final_label_repaired: 'clustering around off-duty days' -> 'unknown' |
| 10330 | unknown | unknown | yes | evidence_not_exact_substring |
| 10398 | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week, 2 seizures per cluster' -> '1 cluster per week, 2 per cluster' |
| 10408 | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | yes | final_label_repaired: 'weekly, 3-5 per cluster' -> '1 cluster per week, 3 to 5 per cluster' |
| 10441 | multiple per week | unknown | yes |  |
| 10445 | multiple per week | 9 cluster per month, 2 to 4 per cluster | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 10447 | multiple per week | unknown | yes |  |
| 10514 | multiple per week | unknown | yes |  |
| 10538 | unknown | unknown, 6 per cluster | yes |  |
| 10553 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10621 | multiple per week | multiple cluster per week, 4 to 6 per cluster | no | json_dialect_repaired: python_literal |
| 10737 |  | unknown | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 10751 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 10794 | unknown | 3 cluster per month, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10795 | 2 per month | 2 cluster per month, multiple per cluster | no |  |
| 10863 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster'; evidence_not_exact_substring |
| 10884 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'weekly clusters of 3-4 events' -> '1 cluster per week, 3 to 4 per cluster' |
| 10908 | 4 cluster per month, 4 per cluster | 4 cluster per month, 4 per cluster | yes | final_label_repaired: '16 seizures per month' -> '4 cluster per month, 4 per cluster' |
| 10931 | 6 cluster per month, 4 per cluster | 6 cluster per month, 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '24 per month' -> '6 cluster per month, 4 per cluster' |
| 10941 | 6 cluster per month, 5 per cluster | 6 cluster per month, 5 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '30 per month' -> '6 cluster per month, 5 per cluster' |
| 10954 | unknown | 3 cluster per month, 5 to 6 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10977 | unknown | 4 cluster per month, 5 per cluster | no | final_label_repaired: '4 clusters per month' -> 'unknown' |
| 10994 | 3 to 4 per 1 year | 3 to 4 cluster per month, 3 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 1 year' |
| 11076 | unknown | 1 cluster per 2 months, 2 to 4 per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 2 months' -> 'unknown' |
| 11196 | unknown | 3 cluster per month, 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 11207 | unknown | 2 cluster per month, 6 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown' |
| 11221 | 1 per 5 month | unknown | no | final_label_repaired: 'seizure free since 30/5/2020' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 5 month' |
| 11334 | seizure free for multiple year | 1 per 2 month | no | final_label_repaired: 'seizure free since 23-Jun' -> 'seizure free for multiple year' |
| 11401 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 11431 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11472 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11492 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 11499 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11576 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 11590 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 11733 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11748 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 11787 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 11825 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11842 | no seizure frequency reference | no seizure frequency reference | yes | json_dialect_repaired: python_literal |
| 11844 | seizure free for multiple year | no seizure frequency reference | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 11864 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11867 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 11889 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 11918 | 5 per week | 5 per week | yes | final_label_repaired: '5 times weekly' -> '5 per week' |
| 11936 | 3 to 4 per week | 3 to 4 per week | yes | json_dialect_repaired: python_literal |
| 11983 | 2 to 3 per day | 2 to 3 per day | yes | json_dialect_repaired: python_literal |
| 12005 | 2 to 6 per day | 2 to 6 per day | yes | json_dialect_repaired: python_literal |
| 12060 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'dozens per day' -> 'multiple per day'; evidence_not_exact_substring |
| 12080 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12090 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12169 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12173 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12258 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12300 | multiple per week | 3 per week | no | json_dialect_repaired: python_literal |
| 12319 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 12326 | multiple per week | 4 per week | no |  |
| 12330 | 3 to 4 per week | 3 to 4 per week | yes | json_dialect_repaired: python_literal |
| 12335 | 3 per week | 3 per week | yes | json_dialect_repaired: python_literal |
| 12348 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 12392 | multiple per day | 4 per day | no |  |
| 12504 | 1 cluster per month, multiple per cluster | 3 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> '1 cluster per month, multiple per cluster' |
| 12590 | 1 per 6 month | 1 per week | no | json_dialect_repaired: python_literal; final_label_repaired: '1 every 2-3 months' -> '1 per 6 month' |
| 12643 | 1 to 2 per week | 1 per day | no |  |
| 12645 | 1 to 2 per 6 month | 1 per day | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 to 2 per 6 month'; evidence_not_exact_substring |
| 12674 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12778 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '8 in 2019' -> '8 per 3 month' |
| 12791 | 6 per month | 6 per month | yes | final_label_repaired: 'multiple per week' -> '6 per month'; evidence_not_exact_substring |
| 12826 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12866 | 10 per 5 month | 10 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '10 in 2020 so far' -> '10 per 5 month' |
| 12919 | 5 per 5 month | 5 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12948 | 7 per 5 month | 7 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '7 per year' -> '7 per 5 month' |
| 12985 | 3 per year | 3 per 5 month | yes |  |
| 13043 | 10 to 20 per 5 month | 2 per 5 month | no | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per week' -> 'unknown'; final_label_repaired: 'unknown' -> '10 to 20 per 5 month' |
| 13064 | seizure free for 5 month | 2 per 5 month | no | final_label_repaired: 'seizure free for 5 months' -> 'seizure free for 5 month'; evidence_not_exact_substring |
| 13069 | 2 per 5 month | 2 per 5 month | yes | final_label_repaired: '1 GTC and cluster of absences in recent past' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 5 month' |
| 13077 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 13079 | multiple per week | 2 per 8 month | no | json_dialect_repaired: python_literal |
| 13109 | unknown | 2 per year | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 13162 | seizure free for multiple year | 1 per 4 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 13167 | 1 per 3 week | 1 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 13183 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: 'unknown' -> '1 per 8 month'; evidence_not_exact_substring |
| 13210 | 1 per 5 month | 1 per 5 month | yes | final_label_repaired: 'unknown' -> '1 per 5 month'; evidence_not_exact_substring |
| 13266 | 2 per 3 month | 2 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 13376 | seizure free for 2 year | seizure free for 2 year | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 13473 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 13590 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 13591 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13600 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13611 | 10 per 6 month | 57 per 11 month | no | final_label_repaired: 'multiple per week' -> '24 per 3 month'; final_label_repaired: '24 per 3 month' -> '10 per 6 month'; evidence_not_exact_substring |
| 13645 | 46 per 4 month | 85 per 12 month | yes | final_label_repaired: '3 days per month' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '46 per 4 month' |
| 13753 | 8 per 6 month | 33 per 9 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '47 per 9 month'; final_label_repaired: '47 per 9 month' -> '8 per 6 month' |
| 13765 |  | 50 per 9 month | no | schema_validation_error: Input should be 'asserted', 'negated', 'historical', 'hypothetical' or 'unknown'; evidence_not_exact_substring |
| 13796 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 13822 | 1 per 28 to 32 day | seizure free for multiple month | no | final_label_repaired: '1 cluster per month' -> '1 per 28 to 32 day' |
| 13841 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 13901 | 3 per month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: '3 seizures' -> '3 per month' |
| 13912 | 2 to 3 per month | unknown | no | json_dialect_repaired: python_literal |
| 13970 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 seizures since discharge' -> 'no seizure frequency reference' |
| 13990 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 seizures since discharge' -> 'no seizure frequency reference' |
| 14009 | 2 per month | unknown | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '2 per month'; evidence_not_exact_substring |
| 14031 | no seizure frequency reference | unknown | yes | json_dialect_repaired: python_literal; final_label_repaired: '4 drop attacks since May 2019' -> 'no seizure frequency reference' |
| 14036 | no seizure frequency reference | unknown | yes | final_label_repaired: '4 drop attacks' -> 'no seizure frequency reference' |
| 14081 | 2 to 3 per month | unknown | no |  |
| 14145 | 2 to 3 per month | unknown | no | json_dialect_repaired: python_literal |
| 14236 | 1 per 2 month | 4 per month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 14237 | 3 per 1 week | 3 per month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 1 week' |
| 14243 | 4 per 1 month | 4 per month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '4 per 1 month' |
| 14271 | 3 per 1 month | 2 to 3 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 1 month'; evidence_not_exact_substring |
| 14306 | seizure free for multiple year | 4 per 2 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14369 | 2 per 3 month | 2 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14390 | seizure free for multiple year | 2 per 3 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14443 | seizure free for multiple year | 4 per 2 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14468 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'unknown' -> '2 per 6 month'; evidence_not_exact_substring |
| 14483 | 4 per 3 month | 4 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '4 per 3 month' |
| 14485 | 2 per 3 month | 2 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month' |
| 14551 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'seizure free for 6 month' -> '2 per 2 month'; evidence_not_exact_substring |
| 14590 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per year' -> '2 per 12 month'; final_label_repaired: '2 per 12 month' -> '2 per 6 month'; evidence_not_exact_substring |
| 14598 | 5 per 5 month | 5 per 8 month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '5 per 5 month' |
| 14655 | 2 per 2 month | 2 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 2 month' |
| 14689 | 3 per 2 month | 3 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 2 month' |
| 14792 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14823 | seizure free for multiple year | 1 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14824 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14845 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14877 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14881 | 29 per 2 month | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '29 per 2 month'; evidence_not_exact_substring |
| 14888 | seizure free for multiple year | 1 per month | no | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14930 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free since 23-May' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month'; evidence_not_exact_substring |
| 14944 | 1 per 2 month | 1 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month'; evidence_not_exact_substring |
| 14954 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15039 | unknown | multiple per 12 month | yes | json_dialect_repaired: python_literal |
| 15113 | 2 to 3 per 16 month | 3 to 4 per 16 month | no | final_label_repaired: '2 to 3 per day' -> '2 to 3 per 16 month' |
| 15148 | 1 to 2 per 16 month | 2 to 3 per 16 month | yes | final_label_repaired: '1 to 2 per month' -> '1 to 2 per 16 month' |
| 15203 | seizure free for 1 year | multiple per 13 month | no |  |
| 15240 | multiple cluster per 12 month, multiple per cluster | multiple cluster per 12 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 12 month, multiple per cluster'; evidence_not_exact_substring |
| 15250 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: 'occasional' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15255 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters per week' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster'; evidence_not_exact_substring |
| 15268 | 3 per 15 month | 3 per 15 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'sporadic' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 15 month' |
| 15302 | 1 to 2 per 14 month | 1 to 2 per 14 month | yes | final_label_repaired: '1 to 2 per unspecified interval' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 to 2 per 14 month' |
| 15385 | 3 per day | 1 cluster per 2 month, 3 per cluster | no | final_label_repaired: 'clusters of 3 seizures per day' -> '3 per day' |
| 15396 | 4 per day | 1 cluster per 2 month, 4 per cluster | no | final_label_repaired: 'clusters of 4 seizures per day' -> '4 per day' |
| 15399 | 2 to 4 per day | 1 cluster per 4 month, 2 to 4 per cluster | no | final_label_repaired: 'clusters of 2 to 4 per day' -> '2 to 4 per day' |
| 15434 | 2 per day | 1 cluster per 5 day, 2 per cluster | no |  |
| 15518 | unknown | 1 cluster per 5 day, 5 per cluster | no | final_label_repaired: '5 per 24 hours (in clusters)' -> 'unknown' |
| 15544 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 to 4 per day' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15609 | 2 to 3 per week | 2 to 3 per week | yes | json_dialect_repaired: python_literal |
| 15620 | 3 per day | 3 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 times per day' -> '3 per day' |
| 15685 | 1 per day | 1 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'almost daily' -> '1 per day'; evidence_not_exact_substring |
| 15737 | 2 to 3 per week | 2 to 3 per week | yes | final_label_repaired: '2 to 3 days per week' -> '2 to 3 per week' |
| 15847 | 1 per 2 week | 6 per week | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 2 week'; evidence_not_exact_substring |
| 15900 | 12 per 2 month | 12 per 2 month | yes | final_label_repaired: '8 per month' -> '12 per 2 month' |
| 15927 | 18 per 2 month | 18 per 2 month | yes | final_label_repaired: '8 per month' -> '18 per 2 month' |
| 16050 | 6 per 2 month | 6 per 2 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'ongoing daytime events' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '6 per 2 month' |
| 16128 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: '2 to 4 per month' -> '10 per 3 month' |
| 16158 | 13 per 4 month | 13 per 4 month | yes | final_label_repaired: '11 seizures in 3 months' -> '13 per 4 month' |
| 16253 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '7 per month' -> '8 per 3 month' |
| 16257 | 7 per 2 month | 7 per 3 month | yes | final_label_repaired: '5 per month' -> '7 per 2 month' |
| 16281 | 15 per 3 month | 21 per 4 month | yes | final_label_repaired: 'multiple per week' -> '21 per 4 month'; final_label_repaired: '21 per 4 month' -> '15 per 3 month' |
| 16286 | 7 per 2 month | 13 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: '6 per month' -> '7 per 2 month' |
| 16357 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster every 2 days' -> '1 per 2 day' |
| 16368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 cluster every two days' -> '1 per 2 day' |
| 16422 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: 'daily' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 to 3 day' |
| 16436 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | final_label_repaired: 'daily' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 3 to 4 day' |
| 16512 | multiple per week | 1 per multiple day | yes | json_dialect_repaired: python_literal |
| 16718 | 16 per 6 month | 9 per 6 month | yes | final_label_repaired: '9 seizures this year' -> '9 per 6 month'; final_label_repaired: '9 per 6 month' -> '16 per 6 month' |
| 16727 | 8 per 5 month | 8 per 5 month | yes | final_label_repaired: 'multiple per month' -> '8 per 5 month' |
| 16807 | 8 per 2 month | 8 per 3 month | no | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '8 per 2 month' |
| 16820 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '5 in Aug' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '7 per 3 month' |
| 16825 | 10 per 4 month | 10 per 6 month | yes | final_label_repaired: 'multiple per month' -> '9 per 2 month'; final_label_repaired: '9 per 2 month' -> '10 per 4 month'; evidence_not_exact_substring |
| 16834 | 7 per 5 month | 7 per 5 month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per month' -> '7 per 5 month' |
| 16962 | 2 per week | 2 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'twice weekly' -> '2 per week' |
| 16964 |  | 2 per week | no | schema_validation_error: Field required; evidence_not_exact_substring |
| 16977 | 4 to 5 per month | 4 to 5 per month | yes |  |
| 16991 | multiple per month | multiple per month | yes | final_label_repaired: 'few times per month' -> 'multiple per month' |
| 17107 | 5 per week | 5 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: '5 days per week' -> '5 per week' |
| 17133 | unknown | 2 cluster per week, multiple per cluster | no | json_dialect_repaired: python_literal; final_label_repaired: 'clusters on 2 days per week' -> 'unknown' |
| 17202 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal |
| 17207 | 1 per day | 3 to 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '3 to 4 per day' -> '1 per day' |
| 17229 | 2 per week | 2 per week | yes |  |
| 17258 | 1 per 4 day | 1 per 4 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 17292 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week'; evidence_not_exact_substring |
| 17297 | no seizure frequency reference | 1 per multiple week | yes | final_label_repaired: 'infrequent' -> 'no seizure frequency reference'; evidence_not_exact_substring |
