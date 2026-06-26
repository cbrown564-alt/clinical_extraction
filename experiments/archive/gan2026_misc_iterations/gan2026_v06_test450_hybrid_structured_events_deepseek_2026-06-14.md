# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-14

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `test` split, `gan2026_split_v1`, 450 rows.
Rare full-validation reason: User-authorized DeepSeek structured-events test450 source coverage run to correct missing cross-model holdout artifact; aggregate-only artifact generation, no row-level tuning.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-chat`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.6`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-14T17:49:41.430964+00:00`
- Run finished UTC: `2026-06-14T18:22:35.533922+00:00`
- Wall-clock elapsed: `1974.103` seconds (`32.902` minutes)
- Throughput: `0.227952` rows/sec (`4.387` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `6f80af0e`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl`

## Summary

- Structured records: 446 / 450
- Call failures: 0
- Parse/schema/label issues: 4
- JSON dialect repairs: 0
- Deterministic repair notes: 307
- Exact selection evidence substrings: 440 / 450
- Purist validation accuracy/micro F1 proxy: 0.7867 (354 / 450)
- Pragmatic validation accuracy/micro F1 proxy: 0.8178 (368 / 450)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 31 | 4 per day | 4 per day | yes | final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 51 | 5 per week | 5 per week | yes |  |
| 61 | 4 per week | 4 per week | yes |  |
| 115 | 7 to 8 per month | 7 to 8 per month | yes |  |
| 136 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 174 | 1 per 1 to 3 day | 1 per 1 to 3 day | yes | final_label_repaired: '1 per 1 to 3 days' -> '1 per 1 to 3 day' |
| 176 | 1 per 6 to 7 day | 1 per 6 to 7 day | yes | final_label_repaired: '1 per 6 to 7 days' -> '1 per 6 to 7 day' |
| 234 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 240 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2 to 3 months' -> '1 per 2 to 3 month' |
| 364 | 1 per week | 1 per week | yes |  |
| 493 | 11 per month | 11 per month | yes |  |
| 503 | 11 to 28 per 3 month | 11 to 28 per 3 month | yes | final_label_repaired: '11 to 28 per quarter' -> '11 to 28 per 3 month' |
| 538 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 610 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 every 2 to 3 months' -> '1 per 2 to 3 month' |
| 632 | 46 per 12 month | 1 per 1 to 2 month | no | final_label_repaired: '1 to 2 per month' -> '46 per 12 month' |
| 666 | 1 per 2 to 3 month | 2 per 2 to 3 month | yes | final_label_repaired: '2 clusters per 2 to 3 months' -> '1 per 2 to 3 month' |
| 685 | 1 per day | 1 per day | yes |  |
| 714 | 2 per day | 2 per day | yes |  |
| 722 | 1 per day | 1 per day | yes |  |
| 735 | 1 per day | 1 per day | yes |  |
| 739 | multiple per week | multiple per week | yes |  |
| 748 | 2 per 4 month | 1 per 2 month | yes | final_label_repaired: '2 episodes over 4 months' -> '2 per 4 month' |
| 750 | no seizure frequency reference | multiple per week | yes | final_label_repaired: 'most days of the working week' -> 'no seizure frequency reference' |
| 803 | 1 per month | 1 per month | yes | evidence_not_exact_substring |
| 804 | 1 per month | 1 per month | yes |  |
| 824 | 1 per month | 1 per month | yes |  |
| 836 | 1 per year | 1 per year | yes |  |
| 841 | 1 per year | 1 per year | yes |  |
| 892 | multiple per week | 1 per 2 day | no |  |
| 934 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 938 | 2 per month | 1 per 2 week | yes |  |
| 1005 | 1 per 3 month | multiple per 3 month | no | final_label_repaired: '1 cluster per 3 months' -> '1 per 3 month' |
| 1017 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 1060 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 1182 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | final_label_repaired: '6 to 14 per 3 months' -> '6 to 14 per 3 month' |
| 1184 | 6 to 14 per 3 month | 6 to 14 per 3 month | yes | final_label_repaired: '6 to 14 per 3 months' -> '6 to 14 per 3 month' |
| 1250 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1289 | 5 to 6 per 10 month | 5 to 6 per year | yes | final_label_repaired: '5 to 6 per year' -> '5 to 6 per 10 month' |
| 1290 | 8 to 9 per 5 month | 8 to 9 per year | no | final_label_repaired: '8 or 9 per year' -> '8 to 9 per 5 month' |
| 1326 | multiple per day | multiple per day | yes | final_label_repaired: 'multiple clusters per week' -> 'multiple per day' |
| 1378 | 5 per month | 5 per month | yes |  |
| 1422 | 9 per week | 9 per week | yes |  |
| 1433 | 4 per month | 4 per month | yes |  |
| 1460 | 7 per month | 7 per month | yes |  |
| 1497 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1511 | 7 per month | 7 per month | yes |  |
| 1534 | 9 per month | 9 per month | yes | final_label_repaired: '6 per month' -> '9 per month' |
| 1624 | 12 per week | 12 per week | yes |  |
| 1629 | 7 per month | 12 per month | yes | final_label_repaired: '12 per month' -> '7 per month' |
| 1633 | 7 per week | 12 per week | yes | final_label_repaired: '12 per week' -> '7 per week' |
| 1656 | 5 per month | 5 per month | yes |  |
| 1683 | multiple per day | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per day' |
| 1705 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 1722 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 events over 2 months' -> '3 per 2 month' |
| 1736 | 1 per 6 month | 4 per 6 month | no | final_label_repaired: '4 events in 6 months' -> '1 per 6 month' |
| 1812 | 12 per 3 month | 12 per 3 month | yes | final_label_repaired: '12 events in 3 months (7 drop attacks + 5 convulsions)' -> '12 per 3 month' |
| 1868 | 7 per 2 month | 8 per 2 month | no | final_label_repaired: '7 per 2 months' -> '7 per 2 month' |
| 1883 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 events in 3 months' -> '4 per 3 month' |
| 1889 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 events in 6 months' -> '4 per 6 month' |
| 1898 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: '4 events in 6 months' -> '4 per 6 month' |
| 1911 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '7 events in 2 months' -> '7 per 2 month' |
| 1934 | 2 per 2 month | 7 per 2 month | no | final_label_repaired: '7 events in 2 months' -> '2 per 2 month' |
| 1938 | 5 per 4 month | 5 per 4 month | yes | final_label_repaired: '5 events in 4 months' -> '5 per 4 month' |
| 2071 | multiple per week | multiple per week | yes |  |
| 2112 | multiple per week | multiple per week | yes | evidence_not_exact_substring |
| 2135 | multiple per month | unknown | yes | final_label_repaired: 'occasional over last year' -> 'multiple per month' |
| 2220 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2226 | 3 to 10 per 2 week | 3 to 10 per 2 week | yes | final_label_repaired: '3 to 10 per 2 weeks' -> '3 to 10 per 2 week' |
| 2246 | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | final_label_repaired: '7 to 8 per 3 weeks' -> '7 to 8 per 3 week' |
| 2262 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | final_label_repaired: '7 to 9 per 3 weeks' -> '7 to 9 per 3 week' |
| 2306 | 8 to 9 per month | 8 to 9 per month | yes |  |
| 2311 | 5 to 7 per month | 5 to 7 per month | yes |  |
| 2356 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2404 | 6 to 7 per month | 6 to 7 per month | yes |  |
| 2486 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2543 | 2 to 4 per 2 week | 2 to 4 per 2 week | yes | final_label_repaired: '2 to 4 per 2 weeks' -> '2 to 4 per 2 week' |
| 2564 | 3 to 5 per 2 month | 3 to 5 per 2 month | yes | final_label_repaired: '3 to 5 per 2 months' -> '3 to 5 per 2 month' |
| 2596 | 2 per day | 2 per day | yes | final_label_repaired: '2 per night' -> '2 per day' |
| 2597 | unknown | 2 per day | no | final_label_repaired: '1 cluster per night' -> 'unknown' |
| 2652 | 1 per day | 1 per day | yes |  |
| 2684 | 1 per day | 1 per day | yes | final_label_repaired: 'every night' -> '1 per day' |
| 2725 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2749 | 1 per month | 1 per month | yes |  |
| 2781 | 1 per week | 1 per week | yes |  |
| 2795 | 1 per week | 1 per week | yes |  |
| 2854 | 2 per month | 2 per month | yes |  |
| 2879 | 2 per day | 2 per day | yes |  |
| 2978 | seizure free for 9 month | seizure free for 9 month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 3054 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3102 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3214 | 1 cluster per month, 7 per cluster | 1 cluster per month, 5 to 7 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 7 per cluster' |
| 3225 | 1 cluster per month, 10 per cluster | 1 cluster per month, 3 to 10 per cluster | yes | final_label_repaired: 'monthly clusters of 3-10 seizures over 24 hours' -> '1 cluster per month, 10 per cluster' |
| 3237 | 4 cluster per month, 5 per cluster | 4 cluster per month, 5 per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, 5 per cluster' |
| 3246 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 4 per cluster' |
| 3291 | 9 per month | 9 per month | yes |  |
| 3293 | 8 per month | 8 per month | yes | final_label_repaired: '8 per 30 days' -> '8 per month' |
| 3300 | 9 per month | 9 per month | yes | final_label_repaired: '9 per 30 days' -> '9 per month' |
| 3327 | no seizure frequency reference | 5 to 6 per year | no | final_label_repaired: '5 to 6 seizure days per year' -> 'no seizure frequency reference' |
| 3329 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 3340 | 2 to 3 per month | 2 to 3 per month | yes |  |
| 3353 | unknown | unknown | yes |  |
| 3355 | 2 per 2 month | 1 per 3 month | no | final_label_repaired: '2 per 6 months' -> '2 per 6 month'; final_label_repaired: '2 per 6 month' -> '2 per 2 month' |
| 3407 | multiple per week | multiple per week | yes |  |
| 3452 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 3514 | unknown | unknown | yes |  |
| 3630 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 per week' -> '7 per week' |
| 3638 | 3 per week | 3 per week | yes | final_label_repaired: 'up to 3 clusters per week' -> '3 per week' |
| 3675 | 1 per month | 1 per month | yes |  |
| 3706 | 6 per week | 6 per week | yes |  |
| 3747 | 3 per day | 3 per day | yes | final_label_repaired: '3 per day during perimenstrual days' -> '3 per day' |
| 3831 | 7 per month | 7 per month | yes |  |
| 3864 | 3 per day | 3 per day | yes |  |
| 3867 | 3 per day | 3 per day | yes |  |
| 3888 | 8 per year | 8 per year | yes |  |
| 3906 | 4 per year | 4 per year | yes |  |
| 3918 | 9 per week | 9 per week | yes |  |
| 3934 | 9 per week | 9 per week | yes |  |
| 4003 | 1 per month | 1 per month | yes |  |
| 4004 | 1 per month | 1 per month | yes |  |
| 4073 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4076 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: 'every 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4197 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 4217 | 3 to 4 per week | 1 per 2 day | yes | final_label_repaired: 'alternate days (approximately 3-4 per week)' -> '3 to 4 per week' |
| 4239 | unknown | unknown | yes |  |
| 4342 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: '5 events over approximately 6.5 months' -> '5 per 3 month' |
| 4352 | 5 per 10 month | 5 per 3 month | no | final_label_repaired: '5 events over 3.5 months' -> '5 per 10 month' |
| 4424 | 6 per 12 month | 3 per 6 month | yes | final_label_repaired: '1 per month average (Jan x1, Feb x2, then 0 from Mar to Jun)' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '6 per 12 month' |
| 4679 | multiple per day | multiple per day | yes | final_label_repaired: '10 per hour' -> 'multiple per day' |
| 4707 | multiple per day | multiple per day | yes |  |
| 4809 | unknown | unknown | yes | final_label_repaired: 'clusters triggered by intercurrent illness' -> 'unknown' |
| 4831 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4892 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 4903 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4967 | multiple per year | seizure free for multiple month | no | final_label_repaired: 'rare (auras only under sleep deprivation), otherwise no definite events for many months' -> 'multiple per year' |
| 4996 | seizure free for 1 year | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 1 year 4 months' -> 'seizure free for 1 year' |
| 5088 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for recent months' -> 'seizure free for multiple year' |
| 5174 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 5213 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for at least 6 months (since last review)' -> 'seizure free for multiple year' |
| 5385 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for current period' -> 'seizure free for multiple year' |
| 5395 | 3 per 6 month | seizure free for 6 month | no | final_label_repaired: '3 per 6 months' -> '3 per 6 month' |
| 5505 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5527 | seizure free for 1 year | 1 per year | no | final_label_repaired: 'seizure free for 1 year with one brief event' -> 'seizure free for 1 year' |
| 5540 | 1 per month | 1 per 4 to 5 month | no |  |
| 5555 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5627 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 per 5 days' -> '1 per 5 day' |
| 5653 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 5684 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 5708 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per month (variable, with weeks of quiet and short clusters)' -> 'unknown' |
| 5764 | 3 per month | 3 per month | yes |  |
| 5766 | multiple per week | multiple per week | yes |  |
| 5976 | unknown | unknown | yes |  |
| 6025 | seizure free for multiple year | unknown | no | final_label_repaired: 'clusters during illness, otherwise seizure-free' -> 'seizure free for multiple year' |
| 6028 | seizure free for 3 month | 1 per 3 months | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 6063 | 3 per 2 week | unknown | no | final_label_repaired: '3 per 2 weeks' -> '3 per 2 week' |
| 6073 | 1 per 3 to 4 week | 1 per 3 to 4 weeks | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 6164 | unknown | unknown | yes |  |
| 6216 | 5 per 6 week | 4 per 6 week | yes | final_label_repaired: '5 events over 6 weeks' -> '5 per 6 week' |
| 6252 | unknown | 2 to 4 per month | no | final_label_repaired: '2 to 4 clusters per month' -> 'unknown' |
| 6288 | 2 per 10 week | 2 per 10 week | yes | final_label_repaired: '2 per 10 weeks' -> '2 per 10 week' |
| 6296 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6303 | unknown | unknown | yes | final_label_repaired: 'multiple episodes over several days per month (clusters)' -> 'unknown' |
| 6330 | multiple per week | multiple per month | yes | final_label_repaired: 'multiple per week (myoclonic jerks) and 2 per 3 months (tonic-clonic)' -> 'multiple per week' |
| 6365 | 3 per 7 month | unknown, 1 to 2 per cluster | no | final_label_repaired: '1 to 2 per day on stimulant days' -> '1 to 2 per day'; final_label_repaired: '1 to 2 per day' -> '3 per 7 month' |
| 6380 | 2 per 3 month | unknown | no | final_label_repaired: '2 to 3 per 3 months' -> '2 per 3 month' |
| 6387 | 2 per 6 month | unknown | no | final_label_repaired: '2 events in 6 months' -> '2 per 6 month' |
| 6408 | unknown | unknown | yes |  |
| 6592 | multiple per month | unknown | yes | final_label_repaired: 'intermittent with occasional prolonged events' -> 'multiple per month' |
| 6661 | 3 per 6 week | 0.5 per week | yes | final_label_repaired: '3 per 6 weeks' -> '3 per 6 week' |
| 6763 | 1 per week | 1 per week | yes |  |
| 6775 | seizure free for 4 month | 1 per 5 month | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 6787 | 8 per 6 week | 8 per 6 week | yes | final_label_repaired: '8 per 6 weeks' -> '8 per 6 week' |
| 6909 | 4 per 3 month | 1 per 2 to 3 weeks | yes | final_label_repaired: 'multiple per month' -> '4 per 3 month' |
| 6929 | multiple per week | multiple per week | yes |  |
| 6930 | unknown | unknown | yes |  |
| 6976 | unknown | unknown | yes |  |
| 6979 | unknown | unknown | yes |  |
| 6986 | no seizure frequency reference | unknown | yes | final_label_repaired: 'intermittent (at least 1 episode in past few weeks)' -> 'no seizure frequency reference' |
| 7005 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 7047 | unknown | unknown | yes |  |
| 7061 | 2 to 3 per week | 2 per 6 week | no |  |
| 7232 | no seizure frequency reference | 6 to 8 cluster per month, multiple per cluster | no | final_label_repaired: '6 to 8 days per month' -> 'no seizure frequency reference' |
| 7280 | multiple per day | 5 per month | no | final_label_repaired: '5 per month' -> 'multiple per day' |
| 7318 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 7327 | 2 per 4 month | 2 per 4 months | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 7328 | multiple per month | unknown | yes | final_label_repaired: 'occasional' -> 'multiple per month' |
| 7341 | 2 per month | unknown | no |  |
| 7386 | 2 per 8 week | 7 per 8 week | no | final_label_repaired: '7 events over 8 weeks (approximately 1 per week)' -> '2 per 8 week' |
| 7393 | multiple per month | unknown | yes |  |
| 7405 | no seizure frequency reference | 1 per multiple months | yes | final_label_repaired: 'every few months' -> 'no seizure frequency reference' |
| 7431 | 2 per 8 week | 1 per month | yes | final_label_repaired: '2 per 8 weeks' -> '2 per 8 week' |
| 7670 | multiple per day | multiple per week | yes | final_label_repaired: '1 per day' -> 'multiple per day' |
| 7688 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 7708 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 7712 | 0 per 1 month | 2 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '0 per 1 month' |
| 7719 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7783 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 7816 | 2 per 2 month | seizure free for multiple month | no | final_label_repaired: 'seizure free since start of last month' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 2 month' |
| 7863 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early August 2025' -> 'seizure free for multiple year' |
| 7884 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 7892 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 7935 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for recent weeks' -> 'seizure free for multiple year' |
| 7958 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 3 years' -> 'seizure free for multiple year' |
| 7987 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7993 | unknown | unknown, 2 to 3 per cluster | yes | final_label_repaired: '2 to 3 per 24-48 hours (cluster pattern)' -> 'unknown' |
| 8109 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 8116 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 8127 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 8135 | 1 per 1 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 4 month' -> '1 per 1 month' |
| 8169 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month' |
| 8221 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8222 | seizure free for 9 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 9 months' -> 'seizure free for 9 month' |
| 8244 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last review' -> 'seizure free for multiple year' |
| 8286 | no seizure frequency reference | seizure free for multiple month | no |  |
| 8342 | seizure free for 9 month | seizure free for 9 month | yes |  |
| 8346 | seizure free for 7 month | seizure free for multiple month | yes |  |
| 8423 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 10 weeks' -> 'seizure free for multiple year' |
| 8432 | 1 per 2 to 3 month | 1 per 2 to 3 month | yes | final_label_repaired: '1 per 2 to 3 months' -> '1 per 2 to 3 month' |
| 8488 | 11 per 2 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 6 month' -> '11 per 2 month' |
| 8540 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8624 | seizure free for 13 month | seizure free for 13 month | yes | final_label_repaired: 'seizure free for 13 months' -> 'seizure free for 13 month' |
| 8645 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8723 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year' |
| 8790 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 8791 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year' |
| 8799 | 0 per month | unknown | no | final_label_repaired: 'essentially 0 per month' -> '0 per month' |
| 8813 | seizure free for 3 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 8852 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 8858 | seizure free for 15 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 15 months' -> 'seizure free for 15 month' |
| 8954 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 8957 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 8979 | seizure free for 4.5 year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for 4.5 years' -> 'seizure free for 4.5 year' |
| 9014 | seizure free for 1 year | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 1 year 1 month' -> 'seizure free for 1 year' |
| 9065 | multiple per year | seizure free for 13 month | no | final_label_repaired: 'rare' -> 'multiple per year'; evidence_not_exact_substring |
| 9109 | no seizure frequency reference | unknown | yes | final_label_repaired: 'fewer per day (unspecified count)' -> 'no seizure frequency reference' |
| 9114 | 1 per 4 to 6 week | 1 per 4 to 6 week | yes | final_label_repaired: '1 per 4 to 6 weeks' -> '1 per 4 to 6 week' |
| 9147 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9179 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since mid-August 2025' -> 'seizure free for multiple year' |
| 9189 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for extended interval' -> 'seizure free for multiple year' |
| 9202 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last appointment' -> 'seizure free for multiple year' |
| 9212 | seizure free for 3 month | seizure free for 3 months | yes |  |
| 9251 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9279 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 9294 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 9377 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 9471 | 14 per 22 month | 7 per 11 month | yes | final_label_repaired: '1 per month or less' -> '7 per 11 month'; final_label_repaired: '7 per 11 month' -> '14 per 22 month' |
| 9483 | 16 per 12 month | 8 per 6 month | yes | final_label_repaired: 'approximately 1 per month' -> '8 per 6 month'; final_label_repaired: '8 per 6 month' -> '16 per 12 month' |
| 9562 | 1 to 2 per 1 year | unknown | no | final_label_repaired: 'clusters over 1–2 days after illness, individual episodes under a minute' -> 'unknown'; final_label_repaired: 'unknown' -> '1 to 2 per 1 year' |
| 9566 | 1 to 2 per 8 week | unknown | no | final_label_repaired: '1 to 2 per morning (episodic, triggered by sleep deprivation)' -> '1 to 2 per 8 week' |
| 9601 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 9618 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 9654 | unknown | seizure free for multiple month | no |  |
| 9696 | unknown | unknown | yes |  |
| 9786 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per day (inferred from context of frequent triggers and deterioration)' -> 'unknown' |
| 9801 | unknown | unknown | yes |  |
| 9891 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9926 | unknown | 1 cluster per month, multiple per cluster | no | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 9942 | 1 per month | 1 cluster per month, multiple per cluster | no |  |
| 9946 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 9979 | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes | final_label_repaired: '3 to 4 clusters per week' -> '3 to 4 cluster per week, multiple per cluster' |
| 10009 | unknown | 1 cluster per week, multiple per cluster | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 10031 | unknown | 1 cluster per week, multiple per cluster | no | final_label_repaired: 'clusters on some mornings' -> 'unknown' |
| 10052 | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '4 clusters per quarter' -> '4 cluster per 3 month, multiple per cluster' |
| 10159 | unknown | unknown | yes |  |
| 10186 | 3 to 5 per 12 month | unknown, 3 to 5 per cluster | no | final_label_repaired: '3 to 5 per cluster day, clusters sporadic' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 5 per 12 month' |
| 10213 | 1 cluster per week, 3 per cluster | unknown, 3 per cluster | no | final_label_repaired: '1 cluster per week (approximately, with 3 events per cluster)' -> '1 cluster per week, 3 per cluster' |
| 10292 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per month' -> 'unknown' |
| 10298 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 10316 | unknown | unknown | yes | final_label_repaired: 'clustering around off-duty days' -> 'unknown' |
| 10330 | unknown | unknown | yes | final_label_repaired: 'multiple seizure types with possible clustering, frequency not fully quantified' -> 'unknown'; evidence_not_exact_substring |
| 10398 | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster | yes | final_label_repaired: '1 cluster per week, 2 seizures per cluster' -> '1 cluster per week, 2 per cluster' |
| 10408 | 1 cluster per week, 3 to 5 per cluster | 1 cluster per week, 3 to 5 per cluster | yes | final_label_repaired: '1 cluster per week, 3-5 seizures per cluster' -> '1 cluster per week, 3 to 5 per cluster' |
| 10441 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 10445 | 24 per 4 month | 9 cluster per month, 2 to 4 per cluster | yes | final_label_repaired: 'several days per week' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '24 per 4 month' |
| 10447 | multiple per week | unknown | yes | final_label_repaired: 'multiple per week (clusters on several weekdays)' -> 'multiple per week' |
| 10514 | unknown | unknown | yes | final_label_repaired: 'multiple per week (including 2 GTCs in 6 weeks, daily absence episodes with myoclonic jerks, and nightly clustering)' -> 'unknown' |
| 10538 | unknown | unknown, 6 per cluster | yes | final_label_repaired: 'cluster frequency: six absences over ~1 hour; overall frequency unknown' -> 'unknown' |
| 10553 | unknown | unknown, 2 to 3 per cluster | yes |  |
| 10621 | unknown | multiple cluster per week, 4 to 6 per cluster | no | final_label_repaired: '1 cluster per day (most evenings)' -> 'unknown' |
| 10737 | unknown | unknown | yes |  |
| 10751 | no seizure frequency reference | unknown | yes | final_label_repaired: 'none in the last 4 months' -> 'no seizure frequency reference' |
| 10794 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 cluster days per month' -> 'unknown' |
| 10795 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10863 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10884 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10908 | 4 cluster per month, 4 per cluster | 4 cluster per month, 4 per cluster | yes | final_label_repaired: '4 clusters per month, each cluster ~4 seizures' -> '4 cluster per month, 4 per cluster' |
| 10931 | 6 cluster per month, 4 per cluster | 6 cluster per month, 4 per cluster | yes | final_label_repaired: '6 clusters per month' -> '6 cluster per month, 4 per cluster' |
| 10941 | 6 cluster per month, 5 per cluster | 6 cluster per month, 5 per cluster | yes | final_label_repaired: '6 clusters per month, each with ~5 seizures' -> '6 cluster per month, 5 per cluster' |
| 10954 | unknown | 3 cluster per month, 5 to 6 per cluster | no | final_label_repaired: '3 clusters per month, each with 5-6 events' -> 'unknown' |
| 10977 | unknown | 4 cluster per month, 5 per cluster | no | final_label_repaired: '4 clusters per month, each with ~5 events' -> 'unknown' |
| 10994 | 3 to 4 per 1 year | 3 to 4 cluster per month, 3 per cluster | no | final_label_repaired: '3 to 4 clusters per month' -> 'unknown'; final_label_repaired: 'unknown' -> '3 to 4 per 1 year' |
| 11076 | unknown | 1 cluster per 2 months, 2 to 4 per cluster | no | final_label_repaired: '1 cluster every 2 months' -> 'unknown' |
| 11196 | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster | yes | final_label_repaired: '3 clusters per month, ~5 events per cluster' -> '3 cluster per month, 5 per cluster' |
| 11207 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 clusters per month, ~6 events per cluster' -> '2 cluster per month, 6 per cluster' |
| 11221 | 1 per 5 month | unknown | no | final_label_repaired: 'seizure free for 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free for 4 month' -> '1 per 5 month' |
| 11334 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '1 per 2 month' |
| 11401 | 1 per day | no seizure frequency reference | no | final_label_repaired: 'no seizure frequency reference' -> '1 per day' |
| 11431 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11472 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11492 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11499 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11576 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11590 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11733 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11748 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11787 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11825 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11842 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11844 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11864 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11867 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11889 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11918 | 5 per week | 5 per week | yes |  |
| 11936 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 11983 | 1 per day | 2 to 3 per day | yes | final_label_repaired: '2 to 3 per day' -> '1 per day' |
| 12005 | 2 to 6 per day | 2 to 6 per day | yes |  |
| 12060 | multiple per day | multiple per day | yes |  |
| 12080 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12090 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 12169 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
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
| 12590 | 1 per 2 to 3 month | 1 per week | no | final_label_repaired: '1 per 2-3 months' -> '1 per 2 to 3 month' |
| 12643 | multiple per week | 1 per day | no |  |
| 12645 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12674 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day (daily absences) plus 1-2 per year (tonic-clonic) plus every 3-4 weeks (focal tonic) plus drop attacks' -> '1 per day' |
| 12778 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '8 per 3 months' -> '8 per 3 month' |
| 12791 | 6 per month | 6 per month | yes | final_label_repaired: '6 per year (year to date)' -> '6 per month' |
| 12826 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12866 | 10 per 5 month | 10 per 5 month | yes | final_label_repaired: '10 per 5 months (approximately 2 per month)' -> '10 per 5 month' |
| 12919 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '5 per 5 months (approximately 1 per month)' -> '5 per 5 month' |
| 12948 | 7 per 5 month | 7 per 5 month | yes | final_label_repaired: '7 per 5 months (approximately 1.4 per month)' -> '7 per 5 month' |
| 12985 | 3 per 5 month | 3 per 5 month | yes | final_label_repaired: '3 per 5 months' -> '3 per 5 month' |
| 13043 | 1 per 5 month | 2 per 5 month | yes | final_label_repaired: '1 seizure in 5 months' -> '1 per 5 month' |
| 13064 | seizure free for multiple year | 2 per 5 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 13069 | 1 per 5 month | 2 per 5 month | yes | final_label_repaired: '1 generalised tonic-clonic seizure in the past ~2 weeks with a preceding cluster of absences' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 5 month' |
| 13077 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 13079 | 2 per 8 month | 2 per 8 month | yes | final_label_repaired: '1 cluster per week (absences) and 1 GTC in recent weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 8 month' |
| 13109 | 2 per 1 year | 2 per year | yes | final_label_repaired: '2 tonic seizures in the past 3 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 1 year' |
| 13162 | 1 per 3 week | 1 per 4 month | no | final_label_repaired: '1 seizure in 3 weeks' -> '1 per 3 week' |
| 13167 | 1 per 3 week | 1 per 3 month | no | final_label_repaired: '1 focal impaired-awareness seizure in the last 3 weeks' -> '1 per 3 week' |
| 13183 | 2 per 8 month | 1 per 8 month | no | final_label_repaired: 'unknown' -> '2 per 8 month' |
| 13210 | 1 per 5 month | 1 per 5 month | yes | final_label_repaired: '1 per 5 months' -> '1 per 5 month' |
| 13266 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 events per 3 months' -> '2 per 3 month' |
| 13376 | seizure free for 2 year | seizure free for 2 year | yes | final_label_repaired: 'seizure free for 2 years' -> 'seizure free for 2 year' |
| 13473 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13590 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13591 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13600 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13611 | 37 per 11 month | 57 per 11 month | no | final_label_repaired: '3 days per month' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '37 per 11 month' |
| 13645 | 61 per 12 month | 85 per 12 month | yes | final_label_repaired: 'multiple per month (worsening trend, more days affected)' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '61 per 12 month' |
| 13753 | 47 per 9 month | 33 per 9 month | no | final_label_repaired: '5 days per month' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '47 per 9 month' |
| 13765 | 14 per 5 month | 50 per 9 month | no | final_label_repaired: 'unknown' -> '14 per 5 month' |
| 13796 | unknown | unknown | yes |  |
| 13822 | 1 per 28 to 32 day | seizure free for multiple month | no | final_label_repaired: '1 cluster per month' -> '1 per 28 to 32 day' |
| 13841 | seizure free for 6 month | seizure free for 6 months | yes | final_label_repaired: 'seizure free for 6 months' -> 'seizure free for 6 month' |
| 13901 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since August 2020' -> 'no seizure frequency reference' |
| 13912 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 3 per unspecified period' -> 'no seizure frequency reference' |
| 13970 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 seizures since discharge (approximately 2 months)' -> 'no seizure frequency reference' |
| 13990 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 4 seizures since discharge' -> 'no seizure frequency reference' |
| 14009 | 2 per month | unknown | no |  |
| 14031 | multiple per month | unknown | yes |  |
| 14036 | no seizure frequency reference | unknown | yes | final_label_repaired: '4 since diet start' -> 'no seizure frequency reference' |
| 14081 | 2 to 3 per 4 month | unknown | no | final_label_repaired: '2 to 3 per 4 months' -> '2 to 3 per 4 month' |
| 14145 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 to 3 per unspecified period' -> 'no seizure frequency reference' |
| 14236 | seizure free for multiple year | 4 per month | no | final_label_repaired: 'seizure free since transition period' -> 'seizure free for multiple year' |
| 14237 | 3 per 4 week | 3 per month | yes | final_label_repaired: 'seizure free for approximately 3-4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 4 week' |
| 14243 | 1 per 2 month | 4 per month | no | final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14271 | 1 per 1 month | 2 to 3 per month | no | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14306 | seizure free for 2 month | 4 per 2 month | no |  |
| 14369 | seizure free for 3 month | 2 per 3 month | no |  |
| 14390 | seizure free for multiple year | 2 per 3 month | no | final_label_repaired: 'seizure free since 31/Jan' -> 'seizure free for multiple year' |
| 14443 | seizure free for multiple year | 4 per 2 month | no | final_label_repaired: 'seizure free since recent cluster of four seizures' -> 'seizure free for multiple year' |
| 14468 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'no seizure frequency reference' -> '2 per 6 month' |
| 14483 | 4 per 3 month | 4 per 2 month | yes | final_label_repaired: 'intermittent (some mornings)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 3 month' |
| 14485 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: 'seizure free for 1 month' -> '2 per 3 month' |
| 14551 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'occasional' -> 'multiple per month'; final_label_repaired: 'multiple per month' -> '2 per 2 month' |
| 14590 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: '2 per year' -> '2 per 12 month'; final_label_repaired: '2 per 12 month' -> '2 per 6 month' |
| 14598 | 5 per 9 month | 5 per 8 month | yes | final_label_repaired: 'seizure free for less than 1 month' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '5 per 9 month' |
| 14655 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'; final_label_repaired: 'seizure free for 2 month' -> '2 per 2 month' |
| 14689 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: 'seizure free for less than 1 month' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 2 month' |
| 14792 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 26 days' -> 'seizure free for multiple year' |
| 14823 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14824 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14845 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14877 | 1 per month | 1 per month | yes |  |
| 14881 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14888 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year' |
| 14930 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 14944 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free since 10/Mar' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 2 month' |
| 14954 | multiple per day | 1 per 2 month | no | final_label_repaired: 'less frequent (qualitative)' -> 'multiple per day' |
| 15039 | multiple per month | multiple per 12 month | yes | final_label_repaired: 'occasional' -> 'multiple per month' |
| 15113 | 2 to 3 per 16 month | 3 to 4 per 16 month | no | final_label_repaired: '2 to 3 per interval (since May-2016)' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '2 to 3 per 16 month' |
| 15148 | 1 to 2 per 16 month | 2 to 3 per 16 month | yes | final_label_repaired: '1 to 2 per year' -> '1 to 2 per 16 month' |
| 15203 | unknown | multiple per 13 month | yes |  |
| 15240 | no seizure frequency reference | multiple cluster per 12 month, multiple per cluster | no | final_label_repaired: 'intermittent' -> 'no seizure frequency reference' |
| 15250 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15255 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'multiple per week' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15268 | 3 per 6 month | 3 per 15 month | yes | final_label_repaired: '3 per 6 months' -> '3 per 6 month' |
| 15302 | 1 to 2 per 14 month | 1 to 2 per 14 month | yes | final_label_repaired: '1 to 2 per unspecified period' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 to 2 per 14 month' |
| 15385 | 1 cluster per day, 3 per cluster | 1 cluster per 2 month, 3 per cluster | no | final_label_repaired: '1 cluster per day (3 seizures per cluster)' -> '1 cluster per day, 3 per cluster' |
| 15396 | 1 cluster per day, 4 per cluster | 1 cluster per 2 month, 4 per cluster | no | final_label_repaired: '1 cluster per day (4 seizures per cluster day)' -> '1 cluster per day, 4 per cluster' |
| 15399 | 2 to 4 per 4 month | 1 cluster per 4 month, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per day (cluster)' -> 'unknown'; final_label_repaired: 'unknown' -> '2 to 4 per 4 month' |
| 15434 | multiple per day | 1 cluster per 5 day, 2 per cluster | no | final_label_repaired: 'variable clustering with up to 2 seizures per day on cluster days' -> 'multiple per day' |
| 15518 | 1 cluster per 5 day, 5 per cluster | 1 cluster per 5 day, 5 per cluster | yes | final_label_repaired: 'clusters of up to 5 seizures per 24 hours, with up to 5-day seizure-free intervals' -> '1 cluster per 5 day, 5 per cluster' |
| 15544 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: 'multiple per week with clusters' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15609 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15620 | 3 per day | 3 per day | yes |  |
| 15685 | 1 per day | 1 per day | yes | final_label_repaired: 'almost daily' -> '1 per day' |
| 15737 | 2 to 3 per week | 2 to 3 per week | yes | final_label_repaired: '2 to 3 days per week' -> '2 to 3 per week' |
| 15847 | 6 per week | 6 per week | yes |  |
| 15900 | 12 per 2 month | 12 per 2 month | yes | final_label_repaired: '8 per month' -> '12 per 2 month' |
| 15927 | 18 per 2 month | 18 per 2 month | yes | final_label_repaired: 'clusters' -> 'unknown'; final_label_repaired: 'unknown' -> '18 per 2 month' |
| 16050 | 0 per 2 month | 6 per 2 month | no | final_label_repaired: '5 per month' -> '0 per 2 month' |
| 16128 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: '4 per month (Sep), 2 per month (Aug), 4 per month (Jul)' -> '10 per 3 month' |
| 16158 | 13 per 4 month | 13 per 4 month | yes | final_label_repaired: '2 per month' -> '13 per 4 month' |
| 16253 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '7 per month' -> '8 per 3 month' |
| 16257 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '0 per month (September), 2 per month (August), 5 per month (July)' -> '7 per 2 month'; final_label_repaired: '7 per 2 month' -> '7 per 3 month' |
| 16281 | 21 per 4 month | 21 per 4 month | yes | final_label_repaired: '6 per month' -> '21 per 4 month' |
| 16286 | 13 per 3 month | 13 per 3 month | yes | final_label_repaired: '6 per month (September to date)' -> '6 per month'; final_label_repaired: '6 per month' -> '13 per 3 month' |
| 16357 | 2 per 2 month | 1 per 2 day | no | final_label_repaired: '1 cluster per 2 days' -> '1 per 2 day'; final_label_repaired: '1 per 2 day' -> '2 per 2 month' |
| 16368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 cluster per 2 days' -> '1 per 2 day' |
| 16422 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 every 2 to 3 days' -> '1 per 2 to 3 day' |
| 16436 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | final_label_repaired: 'every 3 to 4 days' -> '1 per 3 to 4 day' |
| 16512 | 1 per multiple day | 1 per multiple day | yes | final_label_repaired: '1 cluster per several days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per multiple day' |
| 16718 | 8 per 3 month | 9 per 6 month | yes | final_label_repaired: '7 per month' -> '8 per 3 month' |
| 16727 | 11 per 3 month | 8 per 5 month | yes | final_label_repaired: 'multiple per month (cluster in Jan, 4 in Mar, 1 GTC in May)' -> 'unknown'; final_label_repaired: 'unknown' -> '11 per 3 month'; evidence_not_exact_substring |
| 16807 | 8 per 2 month | 8 per 3 month | no | final_label_repaired: 'multiple seizure types with variable frequency over recent months' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '8 per 2 month' |
| 16820 | 6 per 2 month | 7 per 3 month | yes | final_label_repaired: 'unknown' -> '6 per 2 month' |
| 16825 | 9 per 3 month | 10 per 6 month | yes | final_label_repaired: 'multiple per year' -> '9 per 2 month'; final_label_repaired: '9 per 2 month' -> '9 per 3 month' |
| 16834 | 7 per 5 month | 7 per 5 month | yes | final_label_repaired: 'multiple per year' -> '7 per 5 month'; evidence_not_exact_substring |
| 16962 | 1 per 3 month | 2 per week | no | final_label_repaired: '2 to 3 per 3 months' -> '1 per 3 month' |
| 16964 | 1 per 2 month | 2 per week | no | final_label_repaired: '4 to 5 per 2 months' -> '1 per 2 month' |
| 16977 | 4 to 5 per month | 4 to 5 per month | yes |  |
| 16991 | multiple per month | multiple per month | yes | final_label_repaired: 'few times per month' -> 'multiple per month' |
| 17107 | unknown | 5 cluster per week, multiple per cluster | no | final_label_repaired: '5 days per week with clusters' -> 'unknown' |
| 17133 | unknown | 2 cluster per week, multiple per cluster | no | final_label_repaired: '2 clusters per week' -> 'unknown' |
| 17202 | 4 per week | 4 per week | yes |  |
| 17207 | 1 per day | 3 to 4 per day | yes | final_label_repaired: '3 to 4 per day' -> '1 per day' |
| 17229 | 2 per week | 2 per week | yes |  |
| 17258 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 per 4 days' -> '1 per 4 day' |
| 17292 | 1 per 3 week | 1 per 3 week | yes |  |
| 17297 | 1 per multiple week | 1 per multiple week | yes | final_label_repaired: '1 per several weeks' -> '1 per multiple week' |
