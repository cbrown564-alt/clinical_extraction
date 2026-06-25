# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-24

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `test` split, `gan2026_split_v1`, 450 rows.
Rare full-validation reason: frozen_v07_deepseek_reasoner_structured_events_test450_aggregate_audit_authorized_20260625
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-reasoner`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.7`
- Temperature: `0.0`
- Max tokens: `32000`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-24T23:50:46.530120+00:00`
- Run finished UTC: `2026-06-25T03:03:53.111573+00:00`
- Wall-clock elapsed: `11586.581` seconds (`193.11` minutes)
- Throughput: `0.038838` rows/sec (`25.748` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `207bcaf`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v07_test450_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260625.jsonl`

## Summary

- Structured records: 446 / 450
- Call failures: 0
- Parse/schema/label issues: 4
- JSON dialect repairs: 0
- Deterministic repair notes: 270
- Exact selection evidence substrings: 442 / 450
- Purist validation accuracy/micro F1 proxy: 0.7689 (346 / 450)
- Pragmatic validation accuracy/micro F1 proxy: 0.8111 (365 / 450)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 31 | 4 per day | 4 per day | yes | final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 51 | 5 per week | 5 per week | yes |  |
| 61 | 4 per week | 4 per week | yes |  |
| 115 | 7 to 8 per month | 7 to 8 per month | yes |  |
| 136 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 174 | 1 per 1 to 3 day | 1 per 1 to 3 day | yes | final_label_repaired: 'every 1-3 days' -> '1 per 1 to 3 day' |
| 176 | 1 per 6 to 7 day | 1 per 6 to 7 day | yes | final_label_repaired: 'every 6 to 7 days' -> '1 per 6 to 7 day' |
| 234 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 240 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: 'every 2 to 3 months' -> '1 per 2 to 3 month' |
| 364 | unknown | 1 per week | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 493 | 11 per month | 11 per month | yes |  |
| 503 | 11 to 28 per 3 month | 11 to 28 per 3 month | yes | final_label_repaired: '11 to 28 per quarter' -> '11 to 28 per 3 month' |
| 538 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 610 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 every 2-3 months' -> '1 per 2 to 3 month' |
| 632 | 92 per 24 month | 1 per 1 to 2 month | no | final_label_repaired: 'once every 1 to 2 months' -> '1 per 1 to 2 month'; final_label_repaired: '1 per 1 to 2 month' -> '92 per 24 month' |
| 666 | 2 per 2 to 3 month | 2 per 2 to 3 month | yes | final_label_repaired: '2 per 2 to 3 months' -> '2 per 2 to 3 month' |
| 685 | 1 per day | 1 per day | yes |  |
| 714 | 2 per day | 2 per day | yes |  |
| 722 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 735 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 739 | multiple per week | multiple per week | yes |  |
| 748 | 2 per 4 month | 1 per 2 month | yes | final_label_repaired: '2 episodes in 4 months' -> '2 per 4 month' |
| 750 | multiple per week | multiple per week | yes |  |
| 803 | 1 per month | 1 per month | yes |  |
| 804 | 1 per month | 1 per month | yes | final_label_repaired: 'at most monthly' -> '1 per month' |
| 824 | 1 per month | 1 per month | yes |  |
| 836 | 1 per year | 1 per year | yes |  |
| 841 | 1 per year | 1 per year | yes | final_label_repaired: 'yearly' -> '1 per year' |
| 892 | no seizure frequency reference | 1 per 2 day | no | final_label_repaired: '2 per fortnight' -> 'no seizure frequency reference' |
| 934 | 2 to 3 per month | 1 per 2 week | yes |  |
| 938 | 2 per week | 1 per 2 week | no |  |
| 1005 | 1 per 3 month | multiple per 3 month | no | final_label_repaired: '1 cluster every 3 months' -> '1 per 3 month' |
| 1017 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'once every 3 months' -> '1 per 3 month' |
| 1060 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 1182 | 2 to 5 per month | 6 to 14 per 3 month | yes |  |
| 1184 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | final_label_repaired: '6 to 14 per 3 months' -> '6 to 14 per 3 month' |
| 1250 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1289 | 5 to 6 per 10 month | 5 to 6 per year | yes | final_label_repaired: '5 to 6 per year' -> '5 to 6 per 10 month' |
| 1290 | 8 to 9 per 5 month | 8 to 9 per year | no | final_label_repaired: '8 to 9 per year' -> '8 to 9 per 5 month' |
| 1326 | multiple per week | multiple per day | yes |  |
| 1378 | 5 per month | 5 per month | yes |  |
| 1422 | 9 per week | 9 per week | yes |  |
| 1433 | 3 per month | 4 per month | no |  |
| 1460 | 7 per month | 7 per month | yes | final_label_repaired: '7 per month (1 tonic-clonic, 6 petit mal)' -> '7 per month' |
| 1497 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1511 | 7 per month | 7 per month | yes |  |
| 1534 | 6 per month | 9 per month | yes |  |
| 1624 | 12 per week | 12 per week | yes |  |
| 1629 | 12 per month | 12 per month | yes |  |
| 1633 | 7 per week | 12 per week | yes | final_label_repaired: '12 per week' -> '7 per week' |
| 1656 | 5 per month | 5 per month | yes |  |
| 1683 | multiple per month | multiple per month | yes |  |
| 1705 | unknown | 1 cluster per month, multiple per cluster | no |  |
| 1722 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '1.5 per month' -> '3 per 2 month' |
| 1736 | 1 per 6 month | 4 per 6 month | no | final_label_repaired: '4 per 6 months' -> '1 per 6 month' |
| 1812 | 5 per 3 month | 12 per 3 month | no | final_label_repaired: '5 per 3 months' -> '5 per 3 month' |
| 1868 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '1 per week' -> '8 per 2 month' |
| 1883 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '1 to 2 per month' -> '4 per 3 month' |
| 1889 | 3 per 6 month | 4 per 6 month | yes | final_label_repaired: '3 per 6 months' -> '3 per 6 month' |
| 1898 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 events in 6 months' -> '4 per 6 month' |
| 1911 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '3 to 4 per month' -> '7 per 2 month' |
| 1934 | 5 per 2 month | 7 per 2 month | yes | final_label_repaired: '5 events in 2 months' -> '5 per 2 month' |
| 1938 | 1 per month | 5 per 4 month | no |  |
| 2071 | multiple per week | multiple per week | yes |  |
| 2112 | unknown | multiple per week | yes | final_label_repaired: '2 cluster days per week' -> 'unknown' |
| 2135 | multiple per month | unknown | yes |  |
| 2220 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 seizures in the last two months' -> '5 to 7 per 2 month' |
| 2226 | 3 to 10 per 2 week | 3 to 10 per 2 week | yes | final_label_repaired: '3 to 10 seizures per 2 weeks' -> '3 to 10 per 2 week' |
| 2246 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: 'about 7 to 8 in 3 weeks' -> '7 to 8 per 3 week' |
| 2262 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 2306 | 8 to 9 per month | 8 to 9 per month | yes | final_label_repaired: '8 or 9 per month' -> '8 to 9 per month' |
| 2311 | 5 to 7 per month | 5 to 7 per month | yes | final_label_repaired: '5 or 7 per month' -> '5 to 7 per month' |
| 2356 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2404 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 2486 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: 'less than 1 per month' -> '2 to 3 per 3 month' |
| 2543 | 4 to 8 per month | 2 to 4 per 2 week | yes |  |
| 2564 | 3 to 5 per 1 year | 3 to 5 per 2 month | no | final_label_repaired: '3 to 5 in two months' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 to 5 per 1 year' |
| 2596 | 2 per day | 2 per day | yes | final_label_repaired: '2 per night' -> '2 per day' |
| 2597 | 2 per day | 2 per day | yes | final_label_repaired: '2 per night' -> '2 per day' |
| 2652 | 1 per day | 1 per day | yes |  |
| 2684 | 1 per day | 1 per day | yes | final_label_repaired: 'nightly' -> '1 per day' |
| 2725 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: 'every other week' -> '1 per 2 week' |
| 2749 | 1 per month | 1 per month | yes | final_label_repaired: 'monthly' -> '1 per month' |
| 2781 | 1 per week | 1 per week | yes |  |
| 2795 | 1 per week | 1 per week | yes |  |
| 2854 | 2 per month | 2 per month | yes |  |
| 2879 | 2 per day | 2 per day | yes |  |
| 2978 | 2 cluster per month, 4 per cluster | seizure free for 9 month | no | final_label_repaired: '2 cluster days per month, 3-4 seizures per cluster' -> '2 cluster per month, 4 per cluster' |
| 3054 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3102 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3214 | 1 cluster per month, 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | final_label_repaired: 'monthly clusters with 5-7 seizures per cluster' -> '1 cluster per month, 7 per cluster' |
| 3225 | 1 cluster per month, 10 per cluster | 1 cluster per month, 3 to 10 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 10 per cluster' |
| 3237 | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, 5 per cluster' |
| 3246 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3291 | 9 per month | 9 per month | yes |  |
| 3293 | 8 per month | 8 per month | yes |  |
| 3300 | 9 per month | 9 per month | yes | final_label_repaired: '9 seizure days per month' -> '9 per month' |
| 3327 | 5 to 6 per year | 5 to 6 per year | yes |  |
| 3329 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 3340 | 2 to 3 per month | 2 to 3 per month | yes |  |
| 3353 | unknown | unknown | yes |  |
| 3355 | 2 per 6 month | 1 per 3 month | yes | final_label_repaired: '2 seizures in 6 months' -> '2 per 6 month' |
| 3407 | multiple per week | multiple per week | yes |  |
| 3452 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 3514 | unknown | unknown | yes |  |
| 3630 | 7 per week | 7 per week | yes | final_label_repaired: 'multiple per week' -> '7 per week' |
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
| 4003 | 1 per month | 1 per month | yes |  |
| 4004 | 1 per month | 1 per month | yes |  |
| 4073 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 to 2 per month' -> '1 per 2 to 3 week' |
| 4076 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4197 | no seizure frequency reference | 1 per 2 day | no | final_label_repaired: 'every second day' -> 'no seizure frequency reference' |
| 4217 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 4239 | unknown | unknown | yes |  |
| 4342 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '5 events in 4 months' -> '5 per 4 month'; final_label_repaired: '5 per 4 month' -> '5 per 3 month' |
| 4352 | 5 per 10 month | 5 per 3 month | no | final_label_repaired: '1 to 2 per month' -> '5 per 10 month' |
| 4424 | 2 per 2 month | 3 per 6 month | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free for 4 month' -> '2 per 2 month' |
| 4679 | multiple per day | multiple per day | yes | final_label_repaired: '~10 per hour' -> 'multiple per day' |
| 4707 | multiple per day | multiple per day | yes |  |
| 4809 | unknown | unknown | yes | final_label_repaired: '1 cluster episode per several weeks' -> 'unknown' |
| 4831 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4892 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4903 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4967 | unknown | seizure free for multiple month | no |  |
| 4996 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free since 20/Apr/2018' -> 'seizure free for multiple year' |
| 5088 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5174 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5213 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5385 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5395 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5505 | unknown | unknown | yes |  |
| 5527 | 1 per year | 1 per year | yes |  |
| 5540 | 1 per month | 1 per 4 to 5 month | no |  |
| 5555 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5627 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: 'every 5 days' -> '1 per 5 day' |
| 5653 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 5684 | 2 per 2 week | unknown | no | final_label_repaired: '2 per fortnight' -> '2 per 2 week' |
| 5708 | unknown | unknown | yes |  |
| 5764 | 3 per month | 3 per month | yes |  |
| 5766 | multiple per week | multiple per week | yes |  |
| 5976 | unknown | unknown | yes |  |
| 6025 | unknown | unknown | yes |  |
| 6028 | seizure free for 3 month | 1 per 3 months | no | final_label_repaired: 'seizure free for approximately 3 months' -> 'seizure free for 3 month' |
| 6063 | 3 per 2 week | unknown | no | final_label_repaired: '3 per fortnight' -> '3 per 2 week' |
| 6073 | 1 per 6 month | 1 per 3 to 4 weeks | no | final_label_repaired: '1 per 3–4 weeks' -> '1 per 6 month' |
| 6164 | unknown | unknown | yes |  |
| 6216 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '5 per 6 weeks' -> '4 per 6 week' |
| 6252 | 2 to 4 per month | 2 to 4 per month | yes |  |
| 6288 | no seizure frequency reference | 2 per 10 week | no | final_label_repaired: '2 in 10 weeks' -> 'no seizure frequency reference' |
| 6296 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6303 | multiple per month | unknown | yes |  |
| 6330 | multiple per week | multiple per month | yes |  |
| 6365 | 10 per 20 month | unknown, 1 to 2 per cluster | no | final_label_repaired: 'less than 1 per month' -> '5 per 10 month'; final_label_repaired: '5 per 10 month' -> '10 per 20 month' |
| 6380 | 2 per 3 month | unknown | no | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 6387 | 2 per month | unknown | no | final_label_repaired: '2 seizures' -> '2 per month' |
| 6408 | unknown | unknown | yes |  |
| 6592 | unknown | unknown | yes |  |
| 6661 | 3 per 6 week | 0.5 per week | yes | final_label_repaired: '3 events in 6 weeks' -> '3 per 6 week' |
| 6763 | 1 per week | 1 per week | yes |  |
| 6775 | seizure free for 4 month | 1 per 5 month | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 6787 | 8 per 6 week | 8 per 6 week | yes | final_label_repaired: 'multiple per month' -> '8 per 6 week' |
| 6909 | 1 per 2 to 3 week | 1 per 2 to 3 weeks | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 6929 | multiple per week | multiple per week | yes |  |
| 6930 | unknown | unknown | yes |  |
| 6976 | unknown | unknown | yes |  |
| 6979 | unknown | unknown | yes |  |
| 6986 | unknown | unknown | yes |  |
| 7005 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 in 6 months' -> '2 per 6 month' |
| 7047 | unknown | unknown | yes |  |
| 7061 | 2 to 3 per week | 2 per 6 week | no |  |
| 7232 | 6 to 8 per month | 6 to 8 cluster per month, multiple per cluster | yes | final_label_repaired: '6 to 8 days per month' -> '6 to 8 per month' |
| 7280 | 5 per month | 5 per month | yes |  |
| 7318 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2–3 weeks' -> '1 per 2 to 3 week' |
| 7327 | no seizure frequency reference | 2 per 4 months | no | final_label_repaired: '2 in 4 months' -> 'no seizure frequency reference' |
| 7328 | unknown | unknown | yes |  |
| 7341 | 2 per month | unknown | no |  |
| 7386 | no seizure frequency reference | 7 per 8 week | no | final_label_repaired: '5 over 8 weeks' -> 'no seizure frequency reference' |
| 7393 | multiple per month | unknown | yes |  |
| 7405 | unknown | 1 per multiple months | yes |  |
| 7431 | 2 per 8 week | 1 per month | yes | final_label_repaired: '2 episodes in 8 weeks' -> '2 per 8 week' |
| 7670 | 1 per day | multiple per week | no | final_label_repaired: 'daily' -> '1 per day' |
| 7688 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for at least 1 year' -> 'seizure free for multiple year' |
| 7708 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 7712 | 2 per month | 2 per 3 month | no |  |
| 7719 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7783 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7816 | 2 per 2 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 1 month' -> '2 per 2 month' |
| 7863 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early August 2025' -> 'seizure free for multiple year' |
| 7884 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7892 | unknown | seizure free for multiple month | no |  |
| 7935 | unknown | seizure free for multiple month | no |  |
| 7958 | seizure free for 3 year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 3 years' -> 'seizure free for 3 year' |
| 7987 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free (unknown duration)' -> 'seizure free for multiple year' |
| 7993 | unknown | unknown, 2 to 3 per cluster | yes | final_label_repaired: '2-3 events per 48 hours (cluster)' -> 'unknown' |
| 8109 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8116 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 8127 | seizure free for 18 month | seizure free for 18 month | yes | final_label_repaired: 'seizure free for 18 months' -> 'seizure free for 18 month' |
| 8135 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since June 2025' -> 'seizure free for multiple year' |
| 8169 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8221 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8222 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 8244 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8286 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8342 | seizure free for 9 month | seizure free for 9 month | yes |  |
| 8346 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since late February 2025' -> 'seizure free for multiple year' |
| 8423 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 10 weeks' -> 'seizure free for multiple year' |
| 8432 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2-3 months' -> '1 per 2 to 3 month' |
| 8488 | 11 per 2 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month'; final_label_repaired: 'seizure free for 6 month' -> '11 per 2 month' |
| 8540 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8624 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8645 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 8723 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year' |
| 8790 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 8791 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year' |
| 8799 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8813 | 1 per multiple week | seizure free for multiple month | no | final_label_repaired: '1 per few weeks' -> '1 per multiple week' |
| 8852 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 8858 | seizure free for 15 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 15 months' -> 'seizure free for 15 month' |
| 8954 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 8957 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free since 06/07/2016' -> 'seizure free for multiple year' |
| 8979 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free since March 2021' -> 'seizure free for multiple year' |
| 9014 | unknown | seizure free for 11 month | no |  |
| 9065 | unknown | seizure free for 13 month | no |  |
| 9109 | unknown | unknown | yes |  |
| 9114 | 1 per 4 to 6 week | 1 per 4 to 6 week | yes | final_label_repaired: '1 per 4-6 weeks' -> '1 per 4 to 6 week' |
| 9147 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9179 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since August 2025' -> 'seizure free for multiple year' |
| 9189 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for extended interval' -> 'seizure free for multiple year' |
| 9202 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9212 | seizure free for 3 month | seizure free for 3 months | yes |  |
| 9251 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9279 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 9294 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 9377 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: 'once every 2 weeks' -> '1 per 2 week' |
| 9471 | 14 per 22 month | 7 per 11 month | yes | final_label_repaired: '1 per month' -> '14 per 22 month' |
| 9483 | 16 per 12 month | 8 per 6 month | yes | final_label_repaired: '1 to 2 per month' -> '8 per 6 month'; final_label_repaired: '8 per 6 month' -> '16 per 12 month' |
| 9562 | 1 to 2 per 1 year | unknown | no | final_label_repaired: 'unknown' -> '1 to 2 per 1 year' |
| 9566 | 1 to 2 per 8 week | unknown | no | final_label_repaired: 'unknown' -> '1 to 2 per 8 week' |
| 9601 | seizure free for 2 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 9618 | seizure free for 5 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 5 months' -> 'seizure free for 5 month' |
| 9654 | unknown | seizure free for multiple month | no |  |
| 9696 | 2 per 6 month | unknown | no | final_label_repaired: 'unknown' -> '2 per 6 month' |
| 9786 | unknown | unknown | yes |  |
| 9801 | unknown | unknown | yes | evidence_not_exact_substring |
| 9891 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9926 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 9942 | 1 per month | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> '1 per month' |
| 9946 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 9979 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: '3 to 4 clusters per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10009 | unknown | 1 cluster per week, multiple per cluster | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10031 | unknown | 1 cluster per week, multiple per cluster | no |  |
| 10052 | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '4 clusters per quarter' -> '4 cluster per 3 month, multiple per cluster' |
| 10159 | unknown | unknown | yes |  |
| 10186 | 3 to 5 per 12 month | unknown, 3 to 5 per cluster | no | final_label_repaired: 'unknown' -> '3 to 5 per 12 month' |
| 10213 | unknown | unknown, 3 per cluster | yes | final_label_repaired: '1-2 clusters per month' -> 'unknown' |
| 10292 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 in 6 weeks' -> 'no seizure frequency reference' |
| 10298 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 10316 | unknown | unknown | yes |  |
| 10330 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 events since May 2025 (approx 5 months)' -> 'no seizure frequency reference' |
| 10398 | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | yes |  |
| 10408 | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | yes | final_label_repaired: '1 cluster per week, 3-5 seizures per cluster' -> '1 cluster per week, 3 to 5 per cluster' |
| 10441 | multiple per week | unknown | yes |  |
| 10445 | multiple per week | 9 cluster per month, 2 to 4 per cluster | no |  |
| 10447 | multiple per week | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per week' |
| 10514 | 2 per 6 week | unknown | no | final_label_repaired: '2 seizures in 6 weeks' -> '2 per 6 week' |
| 10538 | unknown | unknown, 6 per cluster | yes |  |
| 10553 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10621 | multiple per week | multiple cluster per week, 4 to 6 per cluster | no |  |
| 10737 | unknown | unknown | yes |  |
| 10751 | seizure free for 4 month | unknown | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 10794 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 cluster days per month' -> 'unknown' |
| 10795 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10863 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10884 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10908 | 4 cluster per month, 4 per cluster | 4 cluster per month, 4 per cluster | yes | final_label_repaired: '4 clusters per month, each with ~4 seizures' -> '4 cluster per month, 4 per cluster' |
| 10931 | 6 cluster per month, 4 per cluster | 6 cluster per month, 4 per cluster | yes | final_label_repaired: '6 clusters per month' -> '6 cluster per month, 4 per cluster' |
| 10941 | 6 cluster per month, 5 per cluster | 6 cluster per month, 5 per cluster | yes | final_label_repaired: '6 clusters per month' -> '6 cluster per month, 5 per cluster' |
| 10954 | unknown | 3 cluster per month, 5 to 6 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10977 | unknown | 4 cluster per month, 5 per cluster | no | final_label_repaired: '4 clusters per month' -> 'unknown' |
| 10994 | 3 to 4 per 1 year | 3 to 4 cluster per month, 3 per cluster | no | final_label_repaired: '3 to 4 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 1 year' |
| 11076 | unknown | 1 cluster per 2 months, 2 to 4 per cluster | no | final_label_repaired: '1 cluster every 2 months' -> 'unknown' |
| 11196 | unknown | 3 cluster per month, 5 per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 11207 | unknown | 2 cluster per month, 6 per cluster | no | final_label_repaired: '2 clusters per month' -> 'unknown' |
| 11221 | 1 per 5 month | unknown | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free for 4 month' -> '1 per 5 month' |
| 11334 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '1 per 2 month' |
| 11401 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11431 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11472 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11492 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11499 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11576 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11590 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11733 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11748 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11787 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11825 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11842 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11844 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11864 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11867 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11889 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11918 | 5 per week | 5 per week | yes |  |
| 11936 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 11983 | 1 per day | 2 to 3 per day | yes | final_label_repaired: '2 to 3 per day' -> '1 per day' |
| 12005 | 1 per day | 2 to 6 per day | yes | final_label_repaired: '2 to 6 per day' -> '1 per day' |
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
| 12392 | 4 per day | 4 per day | yes |  |
| 12504 | 1 to 2 per week | 3 per day | no |  |
| 12590 | 1 per week | 1 per week | yes |  |
| 12643 | 1 per day | 1 per day | yes |  |
| 12645 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12674 | 1 per day | 1 per day | yes | final_label_repaired: 'daily' -> '1 per day' |
| 12778 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '8 per 3 month' |
| 12791 | 6 per month | 6 per month | yes | final_label_repaired: 'multiple per week' -> '6 per month' |
| 12826 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '2 to 3 per month' -> '10 per 4 month' |
| 12866 | 10 per 5 month | 10 per 5 month | yes | final_label_repaired: '2 to 3 per month' -> '10 per 5 month' |
| 12919 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '1 per month' -> '5 per 5 month' |
| 12948 | 7 per 5 month | 7 per 5 month | yes | final_label_repaired: '1 to 2 per month' -> '7 per 5 month' |
| 12985 | 3 per 5 month | 3 per 5 month | yes | final_label_repaired: '3 episodes in 5 months' -> '3 per 5 month' |
| 13043 | 1 per 1 month | 2 per 5 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 13064 | 1 per 2 week | 2 per 5 month | no | final_label_repaired: '1 seizure in the past 2 weeks' -> '1 per 2 week' |
| 13069 | 1 per 5 month | 2 per 5 month | yes | final_label_repaired: '1 generalized tonic-clonic seizure in the last 2 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 5 month' |
| 13077 | 3 per 3 month | 2 per 3 month | no | final_label_repaired: '2 in 3 months' -> '3 per 3 month' |
| 13079 | 2 per 8 month | 2 per 8 month | yes | final_label_repaired: 'unknown' -> '2 per 8 month' |
| 13109 | 2 per 1 year | 2 per year | yes | final_label_repaired: '2 tonic seizures in one day' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 1 year' |
| 13162 | 1 per 3 week | 1 per 4 month | no | final_label_repaired: '1 seizure in 3 weeks' -> '1 per 3 week' |
| 13167 | 1 per 3 week | 1 per 3 month | no | final_label_repaired: '1 seizure in the last 3 weeks' -> '1 per 3 week' |
| 13183 | 1 per month | 1 per 8 month | no | final_label_repaired: '1 seizure in the past month' -> '1 per month' |
| 13210 | 1 per 2 week | 1 per 5 month | no | final_label_repaired: '1 seizure in the past 2 weeks' -> '1 per 2 week' |
| 13266 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 events in 3 months' -> '2 per 3 month' |
| 13376 | seizure free for 2 year | seizure free for 2 year | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 13473 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13590 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13591 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13600 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13611 | 37 per 11 month | 57 per 11 month | no | final_label_repaired: '3 days per month' -> '3 per month'; final_label_repaired: '3 per month' -> '37 per 11 month' |
| 13645 | 15 per 2 month | 85 per 12 month | yes | final_label_repaired: '12 days per month' -> '12 per month'; final_label_repaired: '12 per month' -> '15 per 2 month' |
| 13753 | 10 per 6 month | 33 per 9 month | yes | final_label_repaired: '5 days per month' -> '5 per month'; final_label_repaired: '5 per month' -> '10 per 6 month' |
| 13765 | 19 per 6 month | 50 per 9 month | no | final_label_repaired: '5 days per month' -> '5 per month'; final_label_repaired: '5 per month' -> '19 per 6 month' |
| 13796 | seizure free for multiple year | unknown | no |  |
| 13822 | seizure free for multiple year | seizure free for multiple month | yes |  |
| 13841 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 13901 | 3 per month | unknown | no | final_label_repaired: '3 seizures' -> '3 per month' |
| 13912 | 2 to 3 per month | unknown | no | final_label_repaired: '2 to 3 seizures' -> '2 to 3 per month' |
| 13970 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since discharge' -> 'no seizure frequency reference' |
| 13990 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 4 seizures since discharge' -> 'no seizure frequency reference' |
| 14009 | 2 per month | unknown | no |  |
| 14031 | unknown | unknown | yes | final_label_repaired: '2 clusters in July' -> 'unknown' |
| 14036 | no seizure frequency reference | unknown | yes | final_label_repaired: '4 drop attacks' -> 'no seizure frequency reference' |
| 14081 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 3 total myoclonic jerks since last clinic' -> 'no seizure frequency reference' |
| 14145 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 3 total' -> 'no seizure frequency reference' |
| 14236 | seizure free for multiple year | 4 per month | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14237 | 3 per week | 3 per month | no |  |
| 14243 | 4 per 1 month | 4 per month | yes | final_label_repaired: '4 per week' -> '4 per 1 month' |
| 14271 | 2 to 3 per week | 2 to 3 per month | no |  |
| 14306 | 4 per month | 4 per 2 month | no | final_label_repaired: '4 seizures' -> '4 per month' |
| 14369 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '2 per 3 month' |
| 14390 | seizure free for 3 month | 2 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 14443 | 4 per 3 month | 4 per 2 month | yes | final_label_repaired: '4 per month' -> '4 per 3 month' |
| 14468 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'unknown' -> '2 per 6 month' |
| 14483 | 4 per 3 month | 4 per 2 month | yes | final_label_repaired: '3 per month' -> '4 per 3 month' |
| 14485 | seizure free for 1 month | 2 per 3 month | no |  |
| 14551 | unknown | 2 per 2 month | no |  |
| 14590 | 2 per 12 month | 2 per 6 month | no | final_label_repaired: '2 per year' -> '2 per 12 month' |
| 14598 | multiple per month | 5 per 8 month | no | final_label_repaired: 'less than 1 per month' -> 'multiple per month' |
| 14655 | 1 per 1 month | 2 per 2 month | yes | final_label_repaired: 'seizure free for approximately 1 month' -> 'seizure free for 1 month'; final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14689 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '1 to 2 per month' -> '3 per 3 month'; final_label_repaired: '3 per 3 month' -> '3 per 2 month' |
| 14792 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 26 days' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14823 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 24 days' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14824 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14845 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14877 | 1 per month | 1 per month | yes |  |
| 14881 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14888 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14930 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 14944 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free since 10 March 2016' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 14954 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free since 26 April 2022' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 15039 | unknown | multiple per 12 month | yes |  |
| 15113 | 2 to 3 per 16 month | 3 to 4 per 16 month | no | final_label_repaired: '2 to 3 total' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 to 3 per 16 month' |
| 15148 | 1 to 2 per 16 month | 2 to 3 per 16 month | yes | final_label_repaired: 'less than 1 per month' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '1 to 2 per 16 month' |
| 15203 | unknown | multiple per 13 month | yes |  |
| 15240 | unknown | multiple cluster per 12 month, multiple per cluster | no | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 15250 | unknown | multiple cluster per 15 month, multiple per cluster | no |  |
| 15255 | unknown | multiple cluster per 15 month, multiple per cluster | no | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 15268 | 3 per 15 month | 3 per 15 month | yes | final_label_repaired: '3 single jerks since May 2015' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '3 per 15 month' |
| 15302 | unknown | 1 to 2 per 14 month | no |  |
| 15385 | 3 per 2 month | 1 cluster per 2 month, 3 per cluster | yes | final_label_repaired: 'unknown' -> '3 per 2 month' |
| 15396 | 4 per 2 month | 1 cluster per 2 month, 4 per cluster | yes | final_label_repaired: '1 cluster every 2 months (4 seizures per cluster)' -> 'unknown'; final_label_repaired: 'unknown' -> '4 per 2 month' |
| 15399 | 2 to 4 per 4 month | 1 cluster per 4 month, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 seizures per cluster' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 to 4 per 4 month' |
| 15434 | multiple per week | 1 cluster per 5 day, 2 per cluster | no |  |
| 15518 | 5 per day | 1 cluster per 5 day, 5 per cluster | yes |  |
| 15544 | multiple per week | 1 cluster per 5 day, 2 to 4 per cluster | no |  |
| 15609 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15620 | 3 per day | 3 per day | yes |  |
| 15685 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 15737 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15847 | 6 per week | 6 per week | yes |  |
| 15900 | 12 per 2 month | 12 per 2 month | yes | final_label_repaired: '8 seizures per month' -> '8 per month'; final_label_repaired: '8 per month' -> '12 per 2 month' |
| 15927 | 18 per 2 month | 18 per 2 month | yes | final_label_repaired: '8 per month' -> '18 per 2 month' |
| 16050 | 11 per 2 month | 6 per 2 month | no | final_label_repaired: '5 per month' -> '11 per 2 month' |
| 16128 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: '4 per month' -> '10 per 3 month' |
| 16158 | 13 per 4 month | 13 per 4 month | yes | final_label_repaired: '2 per month' -> '13 per 4 month' |
| 16253 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '7 per month' -> '8 per 3 month' |
| 16257 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '5 seizures in July' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '7 per 3 month' |
| 16281 | 21 per 4 month | 21 per 4 month | yes | final_label_repaired: '6 per month' -> '21 per 4 month' |
| 16286 | 13 per 3 month | 13 per 3 month | yes | final_label_repaired: '6 per month' -> '13 per 3 month' |
| 16357 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 cluster per 2 days' -> '1 per 2 day' |
| 16368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 cluster every 2 days' -> '1 per 2 day' |
| 16422 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: 'every 2-3 days' -> '1 per 2 to 3 day' |
| 16436 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | final_label_repaired: '1 every 3-4 days' -> '1 per 3 to 4 day' |
| 16512 | multiple per week | 1 per multiple day | yes |  |
| 16718 | 8 per 3 month | 9 per 6 month | yes | final_label_repaired: '7 per month' -> '8 per 3 month' |
| 16727 | 8 per 5 month | 8 per 5 month | yes | final_label_repaired: '1 per month' -> '8 per 5 month' |
| 16807 | 7 per 2 month | 8 per 3 month | yes | final_label_repaired: '5 per month' -> '7 per 2 month' |
| 16820 | 6 per 2 month | 7 per 3 month | yes | final_label_repaired: '5 drop attacks in a cluster in August 2011' -> 'unknown'; final_label_repaired: 'unknown' -> '6 per 2 month' |
| 16825 | 10 per 6 month | 10 per 6 month | yes | final_label_repaired: '1 tonic seizure in January' -> 'unknown'; final_label_repaired: 'unknown' -> '10 per 6 month' |
| 16834 | 7 per 5 month | 7 per 5 month | yes | final_label_repaired: '3 per month' -> '7 per 5 month' |
| 16962 | 1 per 3 month | 2 per week | no | final_label_repaired: '2 to 3 per three months' -> '1 per 3 month' |
| 16964 | 2 per week | 2 per week | yes | final_label_repaired: 'twice weekly' -> '2 per week'; evidence_not_exact_substring |
| 16977 | 4 to 5 per month | 4 to 5 per month | yes |  |
| 16991 | multiple per month | multiple per month | yes |  |
| 17107 | unknown | 5 cluster per week, multiple per cluster | no | final_label_repaired: '5 days per week with clusters' -> 'unknown' |
| 17133 | unknown | 2 cluster per week, multiple per cluster | no | final_label_repaired: '2 days per week with clusters' -> 'unknown' |
| 17202 | 4 per week | 4 per week | yes |  |
| 17207 | 1 per day | 3 to 4 per day | yes | final_label_repaired: '3 to 4 per day' -> '1 per day' |
| 17229 | 2 per week | 2 per week | yes |  |
| 17258 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 every 4 days' -> '1 per 4 day' |
| 17292 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 17297 | unknown | 1 per multiple week | yes | final_label_repaired: '1 absence seizure every several weeks' -> 'unknown' |
