# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-08

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 750 rows.
Rare full-validation reason: Phase 1 three-way architecture comparison (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07): RESUME of full validation750 run, deepseek-v4-flash (via deepseek-chat alias = non-thinking mode) pass. hybrid is being resumed via --resume-existing after a transient Windows OS I/O error (OSError: [Errno 22] Invalid argument) that killed the original run at row 560/750 during a checkpoint file write -- 560 rows were written cleanly (0 call_failures, 0 parse_or_validation_failures) before the crash; --resume-existing skips those source_row_indices and appends only the remaining 190 rows, then merges at the end into the final artifact. The other three architectures (llm_only_direct_labeler, hybrid_structured_events, llm_only_canonical_pipeline) had not yet been started when the crash occurred and use --overwrite-existing. MODEL NOTE: deepseek-chat is used rather than deepseek-v4-flash directly because calling the latter defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model. Pilot25 with deepseek-chat was perfectly clean (0/25 failures across all 4 architectures). deterministic and deterministic_canonical_pipeline are rule-based and make no LLM calls -- reused from the gpt-4.1-mini canonical artifacts (2026-06-07), not re-run.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `deepseek/deepseek-chat`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-08T23:50:08.724283+00:00`
- Run finished UTC: `2026-06-09T00:33:07.410101+00:00`
- Wall-clock elapsed: `2578.686` seconds (`42.978` minutes)
- Throughput: `0.290846` rows/sec (`3.438` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `c11e96c`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08.jsonl`

## Summary

- Structured records: 742 / 750
- Call failures: 0
- Parse/schema/label issues: 8
- JSON dialect repairs: 0
- Deterministic repair notes: 455
- Exact selection evidence substrings: 718 / 750
- Purist validation accuracy/micro F1 proxy: 0.8120 (609 / 750)
- Pragmatic validation accuracy/micro F1 proxy: 0.8453 (634 / 750)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per 7 days' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '1 cluster every 7 to 9 days' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: '1 per 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes |  |
| 409 | 1 per month | 1 per month | yes | final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 15 per 3 month | 2 per week | yes | final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '2 per 2 weeks' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 | no seizure frequency reference | multiple per week | yes | final_label_repaired: 'most shifts' -> 'no seizure frequency reference' |
| 744 | multiple per week | multiple per week | yes | final_label_repaired: 'most weekdays' -> 'multiple per week' |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: '1 per 7 to 10 days' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | 1 per year | 1 per year | yes | final_label_repaired: 'yearly seizures' -> '1 per year'; evidence_not_exact_substring |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per day | multiple per month | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | seizure free for multiple year | 5 to 7 per 3 week | no | final_label_repaired: 'seizure free for 6 weeks' -> 'seizure free for multiple year' |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | final_label_repaired: '7 to 9 per 3 weeks' -> '7 to 9 per 3 week' |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | final_label_repaired: '5 to 7 per year' -> '5 to 7 per 10 month' |
| 1317 | unknown | unknown, multiple per cluster | yes | final_label_repaired: '1 cluster per day' -> 'unknown' |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 3 per day | 3 per day | yes |  |
| 1413 | 9 per month | 9 per month | yes | evidence_not_exact_substring |
| 1454 | 7 per week | 7 per week | yes |  |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 episodes over 2 weeks' -> '3 per 2 week' |
| 1695 | seizure free for 1 month | multiple per month | no |  |
| 1706 | multiple per week | multiple cluster per month, multiple per cluster | no |  |
| 1707 | multiple per week | multiple per week | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '11 events per 6 months' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '11 events in 3 months' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '6 drop attacks and 2 epileptic spasms over 4 months' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1880 | multiple per week | 8 per 2 month | no | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 events in 3 months' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 events per 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 events in 3 months' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 events per 6 months' -> '7 per 6 month' |
| 1979 | 2 per week | 6 per 2 month | no |  |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '6 events in 3 months' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2149 | unknown | unknown | yes |  |
| 2166 | multiple per day | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per 2 weeks' -> '3 to 5 per 2 week' |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | final_label_repaired: '6 to 7 per 2 months' -> '6 to 7 per 2 month' |
| 2245 | 2 to 3 per month | 7 to 8 per 3 week | no |  |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | final_label_repaired: '6 to 8 per 3 months' -> '6 to 8 per 3 month' |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 per 2 months' -> '2 to 3 per 2 month' |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 to 7 per 2 months' -> '5 to 7 per 2 month' |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | final_label_repaired: '6 to 7 per 2 weeks' -> '6 to 7 per 2 week' |
| 2459 | 5 per 5 month | 7 to 9 per 2 week | no | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 per 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per 2 weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: '8 to 9 per 2 weeks' -> '8 to 9 per 2 week' |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | final_label_repaired: '5 to 6 per 2 months' -> '5 to 6 per 2 month' |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | final_label_repaired: '3 to 4 per 2 months' -> '3 to 4 per 2 month' |
| 2609 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 2628 | 1 per day | 1 per day | yes |  |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2681 | 1 per day | 1 per day | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 7 per 10 month | 1 per month | no | final_label_repaired: '1 per month' -> '7 per 10 month' |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 | 1 per week | 1 per week | yes |  |
| 2812 | 1 per day | 1 per day | yes |  |
| 2822 | 1 per day | 1 per day | yes |  |
| 2824 | 1 per day | 1 per day | yes |  |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 2932 | 13 per 2 month | seizure free for 9 month | no | final_label_repaired: 'seizure free for 9 month' -> '13 per 2 month' |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 2965 | seizure free for multiple year | seizure free for 16 month | yes | final_label_repaired: 'seizure free since 03-Sep-2017' -> 'seizure free for multiple year' |
| 2992 | 1 per 7 month | seizure free for 7 month | no | final_label_repaired: 'seizure free for 7 month' -> '1 per 7 month' |
| 3015 | 1 per 13 month | seizure free for 12 month | no | final_label_repaired: 'seizure free for 1 year' -> '1 per 13 month' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last visit' -> 'seizure free for multiple year' |
| 3137 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, 6 to 7 per cluster' |
| 3242 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3261 | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | yes | final_label_repaired: '2 clusters per month, each with approximately 4 absences' -> '2 cluster per month, 4 per cluster' |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 3281 | 8 per month | 8 per month | yes | final_label_repaired: '8 per 30 days' -> '8 per month' |
| 3297 | 6 per month | 6 per month | yes |  |
| 3325 | 3 per week | 3 per week | yes |  |
| 3356 | unknown | unknown | yes |  |
| 3371 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes |  |
| 3468 | unknown | unknown | yes | final_label_repaired: '1 cluster per month' -> 'unknown' |
| 3469 | no seizure frequency reference | unknown | yes | final_label_repaired: 'perimenstrual only (days -3 to +3)' -> 'no seizure frequency reference' |
| 3482 | no seizure frequency reference | unknown | yes | final_label_repaired: 'perimenstrual only (days -3 to +3)' -> 'no seizure frequency reference' |
| 3493 | multiple per month | unknown | yes | final_label_repaired: 'multiple per month (clustered around menses)' -> 'multiple per month' |
| 3507 | 1 per day | unknown | no | final_label_repaired: 'unknown' -> '1 per day' |
| 3512 | unknown | unknown | yes |  |
| 3528 | multiple per week | unknown | yes |  |
| 3532 | unknown | unknown | yes | final_label_repaired: 'unknown (20% increase from unspecified baseline)' -> 'unknown' |
| 3534 | seizure free for 7 month | unknown | no |  |
| 3600 | unknown | unknown | yes |  |
| 3623 | 7 per week | 7 per week | yes | final_label_repaired: 'multiple per week' -> '7 per week' |
| 3643 | 7 per week | 7 per week | yes | final_label_repaired: 'up to 7 clusters per week' -> '7 per week' |
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
| 3988 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 3995 | 1 per month | 1 per month | yes |  |
| 3999 | 1 per month | 1 per month | yes |  |
| 4022 | 8 per month | 8 per month | yes |  |
| 4026 | 1 per month | 1 per month | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '2 to 3 per week' -> '1 per 2 to 3 week' |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day' -> '1 per 1 to 2 day' |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 to 2 per day on workdays' -> '1 per 1 to 2 day' |
| 4173 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 4243 | 2 to 3 per month | 1 per 2 to 3 week | yes |  |
| 4258 | 4 per week | 4 per week | yes |  |
| 4337 | 23 per 4 month | 3 per 3 month | no | final_label_repaired: '3 events over approximately 4 months' -> '3 per 3 month'; final_label_repaired: '3 per 3 month' -> '23 per 4 month' |
| 4345 | 4 per 1 month | 4 per month | yes | final_label_repaired: '4 per month' -> '4 per 1 month' |
| 4368 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 events over approximately 2.5 months' -> '5 per 2 month' |
| 4402 | 14 per 14 month | 7 per 7 month | yes | final_label_repaired: '1 per month' -> '7 per 7 month'; final_label_repaired: '7 per 7 month' -> '14 per 14 month' |
| 4410 | 8 per 14 month | 4 per 7 month | yes | final_label_repaired: '1 per month' -> '4 per 7 month'; final_label_repaired: '4 per 7 month' -> '8 per 14 month' |
| 4478 | 19 per week | 19 per week | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | final_label_repaired: '7 to 8 per quarter' -> '7 to 8 per 3 month' |
| 4562 | 1 per 6 week | 1 per 6 week | yes | final_label_repaired: '1 per 6 weeks' -> '1 per 6 week' |
| 4563 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 4574 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per 4 weeks' -> '1 per 4 week' |
| 4592 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 4597 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 4624 | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | final_label_repaired: '1 per 3 to 4 days' -> '1 per 3 to 4 day' |
| 4631 | 1 per 2 to 3 week | 1 per 14 to 21 day | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 4690 | multiple per day | multiple per day | yes | final_label_repaired: '10 per hour' -> 'multiple per day' |
| 4694 | multiple per day | multiple per day | yes | final_label_repaired: '9 per hour' -> 'multiple per day' |
| 4700 | multiple per day | multiple per day | yes | final_label_repaired: '4 per hour' -> 'multiple per day' |
| 4709 | multiple per day | multiple per day | yes | final_label_repaired: '6 per hour' -> 'multiple per day' |
| 4731 | multiple per year | unknown | yes | final_label_repaired: 'rare' -> 'multiple per year' |
| 4732 | multiple per month | unknown | yes | final_label_repaired: 'occasional' -> 'multiple per month' |
| 4771 | multiple per month | unknown | yes |  |
| 4839 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for over 4 months' -> 'seizure free for multiple year' |
| 4842 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 4951 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for many months' -> 'seizure free for multiple year' |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for 11 month | seizure free for 11 month | yes | final_label_repaired: 'seizure free for 11 months' -> 'seizure free for 11 month' |
| 4994 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for sustained period' -> 'seizure free for multiple year' |
| 5092 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5121 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5141 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last consultation' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since early 2024' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free since March 2023' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 5351 | seizure free for 18 month | seizure free for 18 month | yes |  |
| 5379 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5406 | no seizure frequency reference | seizure free for multiple month | no |  |
| 5476 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5490 | unknown | unknown | yes |  |
| 5491 | multiple per week | unknown | yes |  |
| 5504 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5507 | multiple per month | unknown | yes | evidence_not_exact_substring |
| 5528 | 1 per month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per month' |
| 5534 | 1 per 2 week | 1 per multiple month | no | final_label_repaired: '1 event per 2 weeks' -> '1 per 2 week' |
| 5551 | multiple per day | multiple per day | yes |  |
| 5567 | multiple per week | multiple per week | yes |  |
| 5584 | multiple per week | multiple per week | yes |  |
| 5624 | 1 per 10 day | 1 per 10 day | yes | final_label_repaired: '1 per 10 days' -> '1 per 10 day' |
| 5652 | 1 per 8 day | 1 per 8 day | yes | final_label_repaired: '1 per 8 days' -> '1 per 8 day' |
| 5682 | 2 to 3 per month | 2 to 4 per month | yes |  |
| 5696 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 5763 | 2 per 3 month | 2 per month | no | final_label_repaired: '2 per 3 months and 4 per 3 months' -> '2 per 3 month' |
| 5767 | 1 to 2 per week | 1 per 1 to 2 week | no |  |
| 5791 | 3 per 3 month | 1 per month | yes | final_label_repaired: '3 events per 3 months' -> '3 per 3 month' |
| 5827 | no seizure frequency reference | multiple per week | yes | final_label_repaired: 'most days' -> 'no seizure frequency reference' |
| 5837 | multiple per week | 2 cluster per 3 week, multiple per cluster | no | evidence_not_exact_substring |
| 5866 | 4 per 6 week | 4 per 6 week | yes | final_label_repaired: '4 per 6 weeks' -> '4 per 6 week' |
| 5873 | no seizure frequency reference | multiple per week | yes | final_label_repaired: 'most nights of the week' -> 'no seizure frequency reference' |
| 5921 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5954 | 2 per week | 2 per week | yes |  |
| 5961 | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 5974 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free when adherent' -> 'seizure free for multiple year' |
| 5977 | multiple per 6 week | unknown | yes | final_label_repaired: 'several per 6 weeks' -> 'multiple per 6 week' |
| 5995 | 2 per 5 month | 1 per 3 months | yes | final_label_repaired: 'infrequent (0-1 per month)' -> '0 to 1 per month'; final_label_repaired: '0 to 1 per month' -> '2 per 5 month' |
| 5996 | unknown | unknown | yes |  |
| 6026 | 3 per 2 month | 3 per 2 month | yes | final_label_repaired: '3 per 2 months' -> '3 per 2 month' |
| 6029 | unknown | unknown | yes | final_label_repaired: 'multiple per month with clusters' -> 'unknown' |
| 6034 | unknown | unknown | yes | final_label_repaired: 'clusters during disrupted routine' -> 'unknown' |
| 6065 | 5 per month | 5 per month | yes |  |
| 6077 | 1 per 1 month | unknown | no | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month'; final_label_repaired: 'seizure free for 8 month' -> '1 per 1 month' |
| 6087 | unknown | unknown | yes | evidence_not_exact_substring |
| 6094 | 4 per 2 month | 3 per month | yes | final_label_repaired: 'multiple per month' -> '4 per 2 month' |
| 6112 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 6131 | seizure free for 12 month | unknown | no | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
| 6137 | 1 per 2 to 3 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 to 3 weeks' -> '1 per 2 to 3 week' |
| 6153 | 3 per month | 9 per month | no | final_label_repaired: '3 per 4 weeks (nocturnal convulsions) and 6 per 4 weeks (focal aware events)' -> '3 per month' |
| 6180 | multiple per week | multiple per week | yes |  |
| 6192 | unknown | unknown | yes |  |
| 6204 | 1 per 3 to 4 week | 2 per month | yes | final_label_repaired: 'multiple per month' -> '1 per 3 to 4 week' |
| 6209 | multiple per day | multiple per day | yes |  |
| 6244 | 2 per week | unknown | no |  |
| 6251 | multiple per year | 1 per 1 to 2 month | no | final_label_repaired: 'rare' -> 'multiple per year' |
| 6273 | unknown | unknown | yes |  |
| 6319 | 1 per week | 1 per week | yes |  |
| 6321 | 2 per 3 month | unknown | no | final_label_repaired: '2 per 3 months' -> '2 per 3 month' |
| 6331 | 2 per 6 week | 2 per 6 weeks | yes | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 6358 | 1 per 16 month | seizure free for 15 to 16 months | no | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month'; final_label_repaired: 'seizure free for 16 month' -> '1 per 16 month' |
| 6368 | multiple per day | unknown | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 6395 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 6501 | unknown | unknown | yes | final_label_repaired: '1 cluster every 2-3 days followed by weeks without events' -> 'unknown' |
| 6509 | unknown | 1 per week | no | final_label_repaired: 'multiple per week (with clustering)' -> 'unknown'; evidence_not_exact_substring |
| 6571 | 1 per 4 month | unknown | no | final_label_repaired: 'seizure free for 3.5 months' -> 'seizure free for 3.5 month'; final_label_repaired: 'seizure free for 3.5 month' -> '1 per 4 month' |
| 6607 | multiple per week | unknown | yes |  |
| 6684 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per 4 months' -> '3 per 4 month' |
| 6701 | 4 per 3 week | 4 per 3 week | yes | final_label_repaired: '4 per 3 weeks' -> '4 per 3 week' |
| 6738 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 6852 | 4 to 6 per month | 4 to 6 per month | yes |  |
| 6889 | multiple per week | multiple per week | yes | final_label_repaired: 'multiple per week (myoclonic jerks), 3 per 6 months (tonic-clonic), 1 per 2-3 weeks (focal)' -> 'multiple per week'; evidence_not_exact_substring |
| 6952 | 2 per week | 2 per week | yes |  |
| 6967 | unknown | unknown | yes |  |
| 6987 | unknown | unknown | yes |  |
| 7093 | unknown | unknown | yes | final_label_repaired: 'clusters per menstrual cycle' -> 'unknown' |
| 7126 | no seizure frequency reference | unknown | yes | final_label_repaired: 'infrequent with mid-cycle surge' -> 'no seizure frequency reference' |
| 7141 | unknown | unknown | yes | final_label_repaired: 'multiple per month (clusters of focal-aware episodes with 2 convulsions in 2 months)' -> 'unknown' |
| 7167 | unknown | 1 cluster per 2 weeks, 2 to 4 per cluster | no | final_label_repaired: '3 clusters over 6 weeks' -> 'unknown' |
| 7168 | unknown | unknown | yes | final_label_repaired: 'intermittent (myoclonic jerks) with catamenial clustering' -> 'unknown'; evidence_not_exact_substring |
| 7192 | multiple per week | multiple per week | yes |  |
| 7195 | 1 per month | unknown | no |  |
| 7196 | 6 per 6 week | 1 per week | yes | final_label_repaired: '6 events over 6 weeks' -> '6 per 6 week' |
| 7198 | unknown | unknown | yes |  |
| 7275 | 3 per 12 week | 1 per month | yes | final_label_repaired: '3 events over 12 weeks' -> '3 per 12 week' |
| 7290 | unknown | unknown | yes |  |
| 7316 | 1 to 2 per month | 1 to 2 per month | yes |  |
| 7389 | unknown | unknown | yes |  |
| 7392 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 7401 | unknown | 2 cluster per 6 week, 1 to 2 per cluster | no | final_label_repaired: '2 clusters per 6 weeks' -> 'unknown' |
| 7409 | multiple per week | unknown | yes | final_label_repaired: 'most weeks' -> 'multiple per week' |
| 7455 | unknown | unknown | yes |  |
| 7475 | 2 per month | 2 per 6 month | no | final_label_repaired: '2 per 6 months (uncertain current frequency)' -> '2 per month' |
| 7491 | unknown | unknown | yes |  |
| 7506 | unknown | unknown | yes |  |
| 7573 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 7581 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 7615 | no seizure frequency reference | 3 to 7 per month | no | final_label_repaired: '3 to 6 per cycle' -> 'no seizure frequency reference' |
| 7650 | unknown | unknown | yes |  |
| 7738 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 7785 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 7818 | seizure free for multiple year | seizure free for 2 years | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 7834 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7859 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for several weeks' -> 'seizure free for multiple year' |
| 7872 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 7911 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since last clinic contact' -> 'seizure free for multiple year' |
| 7961 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 2 years' -> 'seizure free for multiple year' |
| 8002 | 1 per 6 to 8 week | 1 per 6 to 8 week | yes | final_label_repaired: '1 per 6-8 weeks' -> '1 per 6 to 8 week' |
| 8006 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8079 | seizure free for multiple year | seizure free for 18 month | yes | final_label_repaired: 'seizure free since 25 Jan 2019' -> 'seizure free for multiple year' |
| 8089 | 1 per 1 month | seizure free for 16 month | no | final_label_repaired: 'seizure free for 16 month' -> '1 per 1 month' |
| 8124 | seizure free for 13 month | seizure free for 13 month | yes |  |
| 8144 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for current period' -> 'seizure free for multiple year' |
| 8145 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8160 | 1 per multiple week | seizure free for multiple month | no | final_label_repaired: '1 per few weeks' -> '1 per multiple week' |
| 8180 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8188 | seizure free for 18 month | seizure free for multiple month | yes |  |
| 8203 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8224 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8235 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for current follow-up period' -> 'seizure free for multiple year' |
| 8264 | seizure free for 4 month | seizure free for 4 month | yes |  |
| 8265 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8354 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8355 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 8400 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months (with occasional auras)' -> 'seizure free for multiple year' |
| 8419 | 1 to 2 per week | 1 to 2 per week | yes |  |
| 8474 | seizure free for 6 to 8 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for 6-8 month' -> 'seizure free for 6 to 8 month' |
| 8512 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8564 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8577 | seizure free for 18 month | seizure free for multiple month | yes |  |
| 8581 | 1 per 4 month | seizure free for multiple month | no | final_label_repaired: 'seizure free for 4 month' -> '1 per 4 month' |
| 8593 | seizure free for 14 month | seizure free for 14 month | yes | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 8596 | seizure free for 11 month | seizure free for 11 month | yes |  |
| 8674 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 8724 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8730 | 0 per 7 month | seizure free for 6 month | yes | final_label_repaired: 'seizure free for 6 month' -> '0 per 7 month' |
| 8794 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8802 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 8805 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 8808 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 8820 | seizure free for multiple year | seizure free for 7 month | yes | final_label_repaired: 'seizure free since 29-12-2023' -> 'seizure free for multiple year' |
| 8835 | seizure free for multiple year | seizure free for 10 month | yes | final_label_repaired: 'seizure free since 12 June 2020' -> 'seizure free for multiple year' |
| 8854 | seizure free for 8 month | seizure free for multiple month | yes |  |
| 8893 | seizure free for 4 month | seizure free for multiple month | yes |  |
| 8922 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 8924 | seizure free for 5 month | seizure free for multiple month | yes |  |
| 8938 | seizure free for 10 month | seizure free for 10 month | yes |  |
| 8949 | seizure free for 6 month | seizure free for 6 month | yes |  |
| 8969 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free since meningioma resection' -> 'seizure free for multiple year' |
| 9002 | 7 per 10 month | 7 per year | yes | final_label_repaired: '7 per year' -> '7 per 10 month' |
| 9063 | seizure free for 8 month | seizure free for 8 month | yes |  |
| 9103 | unknown | unknown | yes | final_label_repaired: 'infrequent over the past year (tonic-clonic); absence episodes ongoing with unspecified frequency' -> 'unknown' |
| 9163 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for several months' -> 'seizure free for multiple year' |
| 9190 | seizure free for 2 month | seizure free for multiple month | yes |  |
| 9215 | seizure free for 4 month | seizure free for multiple month | yes | final_label_repaired: 'seizure free for approximately 4 months' -> 'seizure free for 4 month' |
| 9238 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9250 | no seizure frequency reference | seizure free for multiple month | no |  |
| 9259 | seizure free for 1 year | seizure free for 1 year | yes |  |
| 9287 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 9299 | 5 per week | 5 per week | yes |  |
| 9300 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 9344 | unknown | multiple per day | yes | final_label_repaired: 'multiple clusters per day' -> 'unknown' |
| 9365 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9368 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 9391 | 1 per month | 1 per month | yes |  |
| 9397 | 1 per month | 1 per month | yes |  |
| 9449 | 8 per 12 month | 4 per 6 month | yes | final_label_repaired: '2 per month' -> '4 per 6 month'; final_label_repaired: '4 per 6 month' -> '8 per 12 month' |
| 9462 | 14 per 22 month | 7 per 11 month | yes | final_label_repaired: '0 to 2 per month' -> '7 per 11 month'; final_label_repaired: '7 per 11 month' -> '14 per 22 month' |
| 9496 | 6 per 12 month | 6 per 12 month | yes | final_label_repaired: 'less than 1 per month' -> '6 per 12 month' |
| 9547 | unknown | unknown | yes | final_label_repaired: 'infrequent clusters over 1-2 days' -> 'unknown' |
| 9588 | seizure free for 6 month | seizure free for multiple month | yes |  |
| 9704 | no seizure frequency reference | unknown | yes |  |
| 9815 | multiple per day | multiple per day | yes | final_label_repaired: '9 per hour' -> 'multiple per day' |
| 9877 | unknown | unknown | yes |  |
| 9879 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per month' -> 'unknown'; evidence_not_exact_substring |
| 9888 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9912 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9937 | multiple per month | 1 cluster per month, multiple per cluster | no |  |
| 9943 | unknown | 1 cluster per 4 to 5 week, multiple per cluster | no | final_label_repaired: 'multiple per month (clustered, every 4-5 weeks, count per burst unknown)' -> 'unknown' |
| 9955 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 cluster per month' -> '1 cluster per month, multiple per cluster' |
| 10003 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10047 | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '2 clusters per quarter' -> '2 cluster per 3 month, multiple per cluster' |
| 10063 | 3 cluster per 3 month, multiple per cluster | 3 cluster per 3 month, multiple per cluster | yes | final_label_repaired: '3 clusters per quarter' -> '3 cluster per 3 month, multiple per cluster' |
| 10097 | unknown | 3 cluster per month, multiple per cluster | no | final_label_repaired: '3 clusters per month' -> 'unknown' |
| 10147 | unknown | unknown | yes |  |
| 10183 | unknown | unknown | yes |  |
| 10189 | unknown | unknown, 3 to 4 per cluster | yes | final_label_repaired: 'multiple per month (clusters sporadically, 3-4 per cluster)' -> 'unknown' |
| 10200 | unknown | unknown, 2 to 4 per cluster | yes | final_label_repaired: 'multiple clusters per month' -> 'unknown'; evidence_not_exact_substring |
| 10237 | unknown | 4 cluster per month, multiple per cluster | no |  |
| 10245 | 2 per 6 month | 3 cluster per month, multiple per cluster | no | final_label_repaired: 'unknown' -> '2 per 6 month' |
| 10260 | unknown | unknown | yes |  |
| 10264 | unknown | unknown | yes |  |
| 10266 | unknown | unknown | yes |  |
| 10268 | unknown | unknown | yes |  |
| 10371 | no seizure frequency reference | seizure free for multiple year | no |  |
| 10383 | 1 cluster per week, 5 per cluster | 1 cluster per week, 5 per cluster | yes | final_label_repaired: '1 cluster per week, 5 seizures per cluster' -> '1 cluster per week, 5 per cluster' |
| 10386 | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes | final_label_repaired: '1 cluster per week, 2 to 3 seizures per cluster' -> '1 cluster per week, 2 to 3 per cluster' |
| 10434 | unknown | multiple cluster per week, 2 to 3 per cluster | no | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 10481 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10487 | 4 cluster per month, multiple per cluster | 4 cluster per month, multiple per cluster | yes | final_label_repaired: '4 clusters per month' -> '4 cluster per month, multiple per cluster' |
| 10509 | unknown | unknown | yes | final_label_repaired: 'multiple clusters per week' -> 'unknown' |
| 10517 | no seizure frequency reference | 3 to 4 cluster per week, multiple per cluster | no | final_label_repaired: '3 to 4 nights per week' -> 'no seizure frequency reference' |
| 10542 | unknown, 2 to 4 per cluster | unknown, 2 to 4 per cluster | yes | final_label_repaired: '2 to 4 per cluster, frequency of clusters unknown' -> 'unknown, 2 to 4 per cluster' |
| 10578 | unknown | unknown, 3 to 4 per cluster | yes |  |
| 10583 | multiple per week | unknown, 2 to 3 per cluster | yes |  |
| 10594 | unknown | unknown, 2 per cluster | yes |  |
| 10618 | 4 to 6 per day | unknown, 4 to 6 per cluster | no | final_label_repaired: '4 to 6 per cluster day' -> '4 to 6 per day' |
| 10629 | unknown | unknown | yes | evidence_not_exact_substring |
| 10630 | no seizure frequency reference | multiple cluster per 2 week, 5 per cluster | no | final_label_repaired: 'multiple per fortnight' -> 'no seizure frequency reference' |
| 10673 | multiple per month | 1 cluster per month, multiple per cluster | no |  |
| 10677 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10753 | unknown | unknown | yes | final_label_repaired: 'multiple per month (with travel-related clusters)' -> 'unknown' |
| 10807 | unknown | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown' |
| 10829 | 2 per 2 year | 2 cluster per month, multiple per cluster | no | final_label_repaired: '2 cluster days per month' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 2 year' |
| 10862 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10865 | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, multiple per cluster' |
| 10873 | 1 cluster per week, 6 per cluster | 1 cluster per week, 6 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 6 per cluster' |
| 10894 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week (approximately 4 events per cluster)' -> '1 cluster per week, 4 per cluster' |
| 10896 | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 3 to 4 per cluster' |
| 10902 | 1 cluster per week, 4 per cluster | 1 cluster per week, 4 per cluster | yes | final_label_repaired: '1 cluster per week' -> '1 cluster per week, 4 per cluster' |
| 10933 | 2 to 3 cluster per month, multiple per cluster | 2 to 3 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 3 clusters per month' -> '2 to 3 cluster per month, multiple per cluster' |
| 10942 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 5 per cluster' |
| 10965 | unknown | 2 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '2 clusters per month, each with 4-5 events' -> 'unknown' |
| 10967 | unknown | 3 cluster per month, 4 to 5 per cluster | no | final_label_repaired: '3 clusters per month, each with 4-5 events' -> 'unknown' |
| 10984 | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '3 clusters per month' -> '3 cluster per month, 3 to 4 per cluster' |
| 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | yes | final_label_repaired: '1 to 2 clusters per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 11002 | 2 to 4 cluster per month, 5 per cluster | 2 to 4 cluster per month, 5 per cluster | yes | final_label_repaired: '2 to 4 per month (clusters)' -> '2 to 4 cluster per month, 5 per cluster' |
| 11035 | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster | yes | final_label_repaired: '1 cluster per 3 months' -> '1 cluster per 3 month, 1 per cluster' |
| 11109 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | final_label_repaired: 'multiple per week' -> '2 cluster per month, 5 per cluster' |
| 11118 | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster | yes | final_label_repaired: '2 cluster days per month, typically 6 seizures per cluster' -> '2 cluster per month, 6 per cluster' |
| 11131 | 2 cluster per month, 3 to 4 per cluster | 2 cluster per month, 3 to 4 per cluster | yes | final_label_repaired: '2 clusters per month' -> '2 cluster per month, 3 to 4 per cluster' |
| 11197 | 1 cluster per month, 4 to 6 per cluster | 1 cluster per month, 4 to 6 per cluster | yes | final_label_repaired: '1 cluster per month with 4 to 6 events per cluster' -> '1 cluster per month, 4 to 6 per cluster' |
| 11216 | seizure free for 4 month | unknown | no |  |
| 11254 | seizure free for 3 month | unknown | no |  |
| 11259 | unknown | unknown | yes |  |
| 11262 | multiple per week | unknown | yes |  |
| 11272 | seizure free for 3 month | unknown | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 11282 | 1 per 4 month | unknown | no | final_label_repaired: 'seizure free since 05-Aug' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 4 month' |
| 11337 | 1 per 6 month | unknown | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 11350 | multiple per day | unknown | yes | final_label_repaired: 'several per week' -> 'multiple per day' |
| 11380 | multiple per day | unknown | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 11389 | seizure free for 2 month | unknown | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 11400 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11405 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11408 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11409 | unknown | no seizure frequency reference | yes |  |
| 11411 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11434 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11463 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11562 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11585 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11606 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11614 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11632 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11640 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11658 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11681 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11706 | 1 per day | no seizure frequency reference | no | final_label_repaired: 'no seizure frequency reference' -> '1 per day' |
| 11711 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11728 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11734 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11737 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11752 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11756 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11763 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 11804 | no seizure frequency reference | no seizure frequency reference | yes | evidence_not_exact_substring |
| 11824 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11841 |  | no seizure frequency reference | no | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; evidence_not_exact_substring |
| 11852 | no seizure frequency reference | no seizure frequency reference | yes |  |
| 12036 | multiple per day | multiple per day | yes |  |
| 12041 | multiple per day | multiple per day | yes |  |
| 12046 | multiple per day | multiple per day | yes |  |
| 12051 | multiple per day | multiple per day | yes |  |
| 12111 | multiple per week | multiple per week | yes |  |
| 12127 | multiple per week | multiple per week | yes |  |
| 12130 | multiple per week | multiple per week | yes |  |
| 12139 | multiple per week | multiple per week | yes |  |
| 12145 | multiple per week | multiple per week | yes |  |
| 12192 | 1 per day | 1 per day | yes |  |
| 12218 | multiple per day | 1 per day | no |  |
| 12236 | unknown | 1 per day | no | final_label_repaired: 'multiple per day (absence seizures daily, myoclonic jerks in morning clusters, occasional GTCS)' -> 'unknown'; evidence_not_exact_substring |
| 12246 | 1 to 2 per day | 1 to 2 per day | yes |  |
| 12314 | multiple per week | 3 per week | no |  |
| 12366 | multiple per day | 4 per day | no |  |
| 12378 | 4 per day | 4 per day | yes |  |
| 12383 | 4 per day | 4 per day | yes |  |
| 12403 | 2 to 3 per day | 2 to 3 per day | yes |  |
| 12412 | multiple per day | 2 per day | no | evidence_not_exact_substring |
| 12422 | 1 per day | 1 per day | yes |  |
| 12438 | 1 per day | 1 per day | yes |  |
| 12456 | 1 per day | 1 per day | yes |  |
| 12460 | 1 per day | 1 per day | yes |  |
| 12468 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 12484 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12502 | 4 per day | 4 per day | yes |  |
| 12506 | 1 cluster per month, multiple per cluster | 4 per day | no | final_label_repaired: 'multiple per day (4 absences per day) plus 1-2 per month (tonic-clonic) plus clusters monthly' -> '1 cluster per month, multiple per cluster'; evidence_not_exact_substring |
| 12537 | multiple per week | 1 per day | no |  |
| 12548 | 13 per 6 month | 1 per day | no | final_label_repaired: 'multiple per day (daily drop attacks) plus 3 per year GTCS and every 4-6 weeks FIAS' -> '13 per 6 month' |
| 12551 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12556 | multiple per day | 1 per day | no | final_label_repaired: 'multiple per week' -> 'multiple per day'; evidence_not_exact_substring |
| 12562 | 3 to 4 per week | 1 per day | no |  |
| 12573 | multiple per day | 1 per day | no | final_label_repaired: 'multiple per month (2 GTCS/month, daily drop attacks, focal impaired-awareness every 4-6 weeks)' -> 'multiple per day'; evidence_not_exact_substring |
| 12584 | multiple per week | 1 per week | no |  |
| 12641 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day'; evidence_not_exact_substring |
| 12665 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per month' -> '1 per day' |
| 12667 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12676 | 1 per day | 1 per day | yes |  |
| 12679 | 1 to 2 per 6 month | 1 per day | no | final_label_repaired: '1 to 2 per month (generalised tonic-clonic), daily (absences), every 3-4 weeks (focal non-motor), drop attacks (frequency unspecified)' -> '1 to 2 per 6 month' |
| 12749 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 12751 | 4 per day | 4 per day | yes |  |
| 12788 | 6 per 4 month | 6 per 4 month | yes | final_label_repaired: '6 per year' -> '6 per 4 month' |
| 12810 | 5 per 2 month | 5 per 2 month | yes | final_label_repaired: '5 per 2 months (approximately 2-3 per month)' -> '5 per 2 month' |
| 12823 | 9 per month | 9 per month | yes | final_label_repaired: '9 per year' -> '9 per month' |
| 12827 | 5 per 5 month | 5 per 5 month | yes | final_label_repaired: '5 per year' -> '5 per 5 month' |
| 12835 | 4 per month | 4 per month | yes | final_label_repaired: '4 per year (estimated, based on 4 in ~3.5 weeks of 2015)' -> '4 per month' |
| 12877 | 10 per 4 month | 10 per 4 month | yes | final_label_repaired: '10 per year' -> '10 per 4 month' |
| 12882 | 7 per 4 month | 7 per 4 month | yes | final_label_repaired: '7 per 4 months (approximately 1.75 per month)' -> '7 per 4 month' |
| 12901 | 8 per 5 month | 8 per 5 month | yes | final_label_repaired: '8 per year (tonic seizures) with clusters after focal episodes' -> '8 per 5 month' |
| 12949 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '9 per 6 months (approximately 1.5 per month)' -> '9 per 6 month' |
| 12950 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 per year' -> '7 per 3 month' |
| 12963 | no seizure frequency reference | unknown | yes | final_label_repaired: 'a small handful per year' -> 'no seizure frequency reference' |
| 12979 | 4 per 3 month | 3 per 4 month | no | final_label_repaired: '3 per 4 months' -> '3 per 4 month'; final_label_repaired: '3 per 4 month' -> '4 per 3 month' |
| 13008 | 4 per month | 4 per month | yes | final_label_repaired: '4 per 3 weeks (approximately 1 per week)' -> '4 per month' |
| 13011 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: '3 per year' -> '3 per 4 month' |
| 13051 | seizure free for multiple year | 2 per 8 month | no | final_label_repaired: 'seizure free since last event' -> 'seizure free for multiple year' |
| 13058 | 2 per 7 month | 2 per 7 month | yes | final_label_repaired: '1 cluster per 3 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '2 per 7 month' |
| 13114 | 1 per 1 year | 1 per year | yes | final_label_repaired: '1 tonic seizure and 2 days of myoclonic jerks in the past 2 weeks' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 1 year'; evidence_not_exact_substring |
| 13122 | 3 per 1 year | 3 per year | yes | final_label_repaired: '3 seizures in a single day (cluster)' -> 'unknown'; final_label_repaired: 'unknown' -> '3 per 1 year' |
| 13149 | 3 per 2 week | 3 per year | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 2 week' |
| 13178 | seizure free for 6 month | 1 per 6 month | no |  |
| 13190 | seizure free for 5 month | 1 per 5 month | no | final_label_repaired: 'seizure free for 5 months' -> 'seizure free for 5 month' |
| 13209 | 1 per 4 to 5 week | 1 per 8 month | no | final_label_repaired: '1 cluster per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 13267 | multiple per day | 2 per 5 month | no | final_label_repaired: 'multiple seizure types with different frequencies' -> 'multiple per day' |
| 13290 | 2 per day | 4 per 6 month | no | final_label_repaired: '2 per day (on the day of occurrence), with additional occasional myoclonic jerks' -> '2 per day' |
| 13327 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13336 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13349 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13385 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13450 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 13471 | seizure free for multiple year | seizure free for 5 year | yes | final_label_repaired: 'seizure free for over 5 years' -> 'seizure free for multiple year' |
| 13478 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for over 1 year' -> 'seizure free for multiple year' |
| 13485 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for a long duration' -> 'seizure free for multiple year' |
| 13487 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for several years' -> 'seizure free for multiple year' |
| 13513 | seizure free for 1.5 year | seizure free for 1.5 year | yes | final_label_repaired: 'seizure free for 1.5 years' -> 'seizure free for 1.5 year' |
| 13574 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13595 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13598 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13608 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for years' -> 'seizure free for multiple year' |
| 13627 | 20 per 3 month | 64 per 12 month | yes | final_label_repaired: 'multiple per month' -> '64 per 12 month'; final_label_repaired: '64 per 12 month' -> '20 per 3 month' |
| 13635 | 30 per 5 month | 47 per 7 month | yes | final_label_repaired: 'multiple per month' -> '47 per 7 month'; final_label_repaired: '47 per 7 month' -> '30 per 5 month' |
| 13711 | 36 per 8 month | 76 per 12 month | yes | final_label_repaired: '10 to 12 days per month' -> '22 per 2 month'; final_label_repaired: '22 per 2 month' -> '36 per 8 month' |
| 13721 | 26 per 6 month | 77 per 12 month | yes | final_label_repaired: '10 days per month with seizures' -> '20 per 2 month'; final_label_repaired: '20 per 2 month' -> '26 per 6 month' |
| 13732 | 16 per 3 month | 52 per 8 month | yes | final_label_repaired: 'unknown' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '16 per 3 month' |
| 13843 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13858 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'no seizure frequency reference' -> 'seizure free for multiple year' |
| 13889 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13893 | 2 per year | 2 per year | yes |  |
| 13922 | no seizure frequency reference | unknown | yes | final_label_repaired: '2 seizures since medication increase' -> 'no seizure frequency reference' |
| 14002 | multiple per day | unknown | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 14025 | 2 per 6 week | unknown | no | final_label_repaired: '2 per 6 weeks' -> '2 per 6 week' |
| 14029 | multiple per week | unknown | yes | final_label_repaired: 'multiple per week (variable)' -> 'multiple per week' |
| 14040 | unknown | unknown | yes |  |
| 14076 | unknown | unknown | yes |  |
| 14092 | 5 per 4 month | unknown | no | final_label_repaired: '5 per 4 months' -> '5 per 4 month' |
| 14096 | no seizure frequency reference | unknown | yes | final_label_repaired: '5 per interval (since last appointment)' -> 'no seizure frequency reference' |
| 14137 | 3 to 4 per 3 month | unknown | no | final_label_repaired: '3 to 4 per 3 months' -> '3 to 4 per 3 month' |
| 14146 | no seizure frequency reference | unknown | yes | final_label_repaired: '3 since beginning Clobazam' -> 'no seizure frequency reference' |
| 14187 | seizure free for multiple year | 2 to 3 per month | no | final_label_repaired: 'seizure free since shortly after 10 Jul' -> 'seizure free for multiple year' |
| 14214 | seizure free for 1 month | 2 to 4 per month | no |  |
| 14250 | 1 per 1 month | 2 per month | no | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14282 | multiple per 6 week | multiple per month | yes | final_label_repaired: 'seizure free for at least several weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> 'multiple per 6 week' |
| 14284 | 2 to 3 per 1 month | 2 to 3 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '2 to 3 per 1 month' |
| 14317 | seizure free for 2 month | 4 per 2 month | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 14332 | seizure free for 2 month | 5 per 2 month | no | final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month' |
| 14335 | 12 per 3 month | 3 to 4 per 2 month | no | final_label_repaired: 'seizure free for 8 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '12 per 3 month' |
| 14383 | seizure free for 3 month | 3 to 4 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 14454 | seizure free for multiple year | 2 per 2 month | no | final_label_repaired: 'seizure free since February 2014' -> 'seizure free for multiple year' |
| 14524 | unknown | 2 per 6 month | no | final_label_repaired: 'occasional clusters' -> 'unknown' |
| 14530 | no seizure frequency reference | 2 per 2 month | no |  |
| 14540 | 2 per 8 month | 2 per 8 month | yes | final_label_repaired: 'seizure free for 6 week' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 8 month' |
| 14562 | 3 per 6 month | 3 per 6 month | yes | final_label_repaired: 'seizure free for 1 month' -> '3 per 6 month' |
| 14567 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: 'unknown' -> '3 per 3 month' |
| 14581 | 1 per 1 month | 2 per 3 month | no | final_label_repaired: 'seizure free for 2 to 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14587 | 2 per 3 month | 2 per 3 month | yes | final_label_repaired: '2 events in 3 months' -> '2 per 3 month' |
| 14592 | 3 per 5 month | 3 per 5 month | yes | final_label_repaired: 'no seizure frequency reference' -> '3 per 5 month' |
| 14611 | seizure free for 0 month | 2 per 4 month | no |  |
| 14628 | 2 per 2 month | 2 per 2 month | yes | final_label_repaired: 'no seizure frequency reference' -> '2 per 2 month' |
| 14635 | 5 per 5 month | 5 per 4 month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '5 per 5 month' |
| 14645 | 2 per 6 month | 2 per 6 month | yes | final_label_repaired: 'seizure free since November 2018' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '2 per 6 month' |
| 14662 | 3 per 4 month | 3 per 4 month | yes | final_label_repaired: 'unknown' -> '3 per 4 month' |
| 14672 | 3 per 8 month | 3 per 8 month | yes | final_label_repaired: 'seizure free since starting current regimen' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '3 per 8 month' |
| 14706 | 2 per 5 month | 2 per 5 month | yes | final_label_repaired: '2 per 5 months' -> '2 per 5 month' |
| 14765 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month' |
| 14806 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'seizure free for 1 month' -> '1 per 2 month' |
| 14810 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14821 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free for 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 14872 | seizure free for multiple year | 1 per month | no | final_label_repaired: 'seizure free for 2 weeks' -> 'seizure free for multiple year' |
| 14943 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 14949 | 1 per month | 1 per month | yes |  |
| 14965 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free since 20/May' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 3 month'; evidence_not_exact_substring |
| 14973 | 1 per 1 month | 1 per month | yes | final_label_repaired: 'seizure free since early February' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '1 per 1 month' |
| 15004 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free for 3 month' -> '1 per 3 month' |
| 15012 | seizure free for multiple year | 1 per 2 month | no | final_label_repaired: 'seizure free for at least 2 months' -> 'seizure free for multiple year' |
| 15021 | 1 per 3 month | 1 per 3 month | yes | final_label_repaired: '1 per 3 months' -> '1 per 3 month' |
| 15029 | seizure free for 3 month | 1 per 3 month | no | final_label_repaired: 'seizure free for 3 months' -> 'seizure free for 3 month' |
| 15094 | 3 per 13 month | 4 per 13 month | yes | final_label_repaired: '3 per 13 months' -> '3 per 13 month' |
| 15108 | 2 to 3 per 15 month | 3 to 4 per 15 month | no | final_label_repaired: '2 to 3 per several months' -> '2 to 3 per multiple month'; final_label_repaired: '2 to 3 per multiple month' -> '2 to 3 per 15 month' |
| 15127 | 4 per 13 month | 5 per 13 month | yes | final_label_repaired: '4 since February 2020' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '4 per 13 month' |
| 15129 | 4 per 15 month | 4 per 15 month | yes | final_label_repaired: '4 per 15 months' -> '4 per 15 month' |
| 15141 | 3 to 4 per 15 month | 4 to 5 per 15 month | yes | final_label_repaired: '3 to 4 per 15 months' -> '3 to 4 per 15 month' |
| 15168 | multiple per week | multiple per 15 month | yes | evidence_not_exact_substring |
| 15193 | unknown | multiple per 13 month | yes |  |
| 15242 | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 15 month, multiple per cluster' |
| 15262 | multiple cluster per 13 month, multiple per cluster | multiple cluster per 13 month, multiple per cluster | yes | final_label_repaired: 'occasional clusters' -> 'unknown'; final_label_repaired: 'unknown' -> 'multiple cluster per 13 month, multiple per cluster' |
| 15267 | seizure free for 14 month | 3 per 14 month | no | final_label_repaired: 'seizure free for 14 months' -> 'seizure free for 14 month' |
| 15306 | seizure free for multiple year | 2 to 3 per 15 month | no | final_label_repaired: 'seizure free for tonic-clonic since 12/2020; 2 to 3 single jerks currently' -> 'seizure free for multiple year' |
| 15317 | 2 to 3 per 15 month | 2 to 3 per 15 month | yes | final_label_repaired: '2 to 3 per day' -> '2 to 3 per 15 month' |
| 15376 | 1 cluster per 2 week, 4 to 6 per cluster | 1 cluster per 2 week, 4 to 6 per cluster | yes | final_label_repaired: '4 to 6 per day (clustered)' -> '1 cluster per 2 week, 4 to 6 per cluster' |
| 15404 | 1 cluster per day, 3 to 4 per cluster | 1 cluster per 4 month, 3 to 4 per cluster | no | final_label_repaired: '1 cluster per day (3-4 seizures per cluster)' -> '1 cluster per day, 3 to 4 per cluster' |
| 15429 | 1 cluster per day, 4 per cluster | 1 cluster per 2 month, 4 per cluster | no | final_label_repaired: '1 cluster per day (4 seizures per cluster)' -> '1 cluster per day, 4 per cluster' |
| 15431 | 5 per 4 month | 1 cluster per 4 month, 5 per cluster | yes | final_label_repaired: '1 cluster per day' -> 'unknown'; final_label_repaired: 'unknown' -> '5 per 4 month' |
| 15442 | multiple per day | 1 cluster per 4 day, 2 per cluster | no | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 15470 | multiple per day | 1 cluster per 5 day, multiple per cluster | no | final_label_repaired: 'multiple per week' -> 'multiple per day' |
| 15479 | multiple per day | 1 cluster per 4 to 5 day, 2 per cluster | no | final_label_repaired: '2 per day (on cluster days)' -> 'multiple per day' |
| 15497 | 1 cluster per 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 5 per cluster' |
| 15503 | unknown | 1 cluster per 5 day, 3 to 4 per cluster | no | final_label_repaired: '3 to 4 per 24 hours (clusters)' -> 'unknown' |
| 15513 | 1 cluster per 5 day, 2 to 3 per cluster | 1 cluster per 4 to 5 day, 2 to 3 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 2 to 3 per cluster' |
| 15519 | multiple per week | 1 cluster per 4 day, 3 per cluster | no |  |
| 15529 | no seizure frequency reference | 1 cluster per 3 day, 4 per cluster | no | final_label_repaired: '4 per 24 hours' -> 'no seizure frequency reference' |
| 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | yes | final_label_repaired: 'multiple per week' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15614 | 3 per week | 3 per week | yes |  |
| 15628 | multiple per week | multiple per week | yes |  |
| 15639 | 2 per week | 2 per week | yes |  |
| 15642 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 15650 | 3 to 4 per day | 3 to 4 per day | yes |  |
| 15672 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week (clusters almost daily)' -> '1 per day' |
| 15697 | 1 per day | 1 per day | yes | final_label_repaired: '1 cluster per day' -> '1 per day' |
| 15715 | 1 per day | 1 per day | yes | final_label_repaired: 'almost 1 per day' -> '1 per day' |
| 15745 | 2 to 3 per week | 2 to 3 per week | yes | final_label_repaired: '2 to 3 days per week' -> '2 to 3 per week' |
| 15766 | 4 per week | 4 per week | yes | final_label_repaired: '4 days per week' -> '4 per week' |
| 15768 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15771 | 3 per week | 3 per week | yes | final_label_repaired: '3 days per week' -> '3 per week' |
| 15772 | 2 per week | 2 per week | yes | final_label_repaired: '2 days per week' -> '2 per week' |
| 15774 | 2 per week | 2 per week | yes |  |
| 15783 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 15802 | 7 per week | 7 per week | yes |  |
| 15831 | 2 to 4 per day | 2 to 4 per day | yes |  |
| 15834 | 5 per week | 5 per week | yes |  |
| 15964 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: 'unknown' -> '11 per 3 month' |
| 15965 | 13 per 2 month | 13 per 2 month | yes | final_label_repaired: '6 per month' -> '13 per 2 month' |
| 15966 | 5 per 3 month | 5 per 3 month | yes | final_label_repaired: 'no seizure frequency reference' -> '5 per 3 month'; evidence_not_exact_substring |
| 15982 | 9 per 2 month | 9 per 2 month | yes | final_label_repaired: '8 per month' -> '9 per 2 month' |
| 15986 | 5 per 3 month | 11 per 3 month | yes | final_label_repaired: 'multiple per month' -> '11 per 2 month'; final_label_repaired: '11 per 2 month' -> '5 per 3 month' |
| 15992 | 7 per 2 month | 7 per 2 month | yes | final_label_repaired: '3 per month' -> '7 per 2 month' |
| 15997 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: 'multiple per month with clustering' -> 'unknown'; final_label_repaired: 'unknown' -> '10 per 3 month' |
| 16021 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: '5 per month' -> '9 per 3 month' |
| 16041 | 9 per 3 month | 9 per 3 month | yes | final_label_repaired: 'multiple per month' -> '9 per 2 month'; final_label_repaired: '9 per 2 month' -> '9 per 3 month' |
| 16084 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: 'seizure free for 1 month' -> '8 per 4 month' |
| 16091 | 3 per 3 month | 3 per 3 month | yes | final_label_repaired: '2 per month' -> '3 per 3 month' |
| 16097 | 17 per 4 month | 17 per 4 month | yes | final_label_repaired: 'multiple per month' -> '17 per 4 month' |
| 16107 | 8 per 3 month | 8 per 3 month | yes | final_label_repaired: '4 per month' -> '8 per 3 month' |
| 16108 | 12 per 4 month | 12 per 4 month | yes | final_label_repaired: '1 per month (current month to date), 5 per month (recent months)' -> '12 per 4 month' |
| 16132 | 15 per 3 month | 15 per 3 month | yes | final_label_repaired: '2 per month' -> '15 per 3 month' |
| 16133 | 18 per 4 month | 18 per 4 month | yes | final_label_repaired: 'approximately 1.5 per week' -> '18 per 4 month' |
| 16161 | 11 per 3 month | 18 per 3 month | no | final_label_repaired: '7 per month' -> '11 per 3 month' |
| 16162 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '6 per month' -> '11 per 3 month' |
| 16181 | 15 per 4 month | 15 per 4 month | yes | final_label_repaired: '4 per month' -> '15 per 4 month' |
| 16195 | 16 per 4 month | 16 per 4 month | yes | final_label_repaired: '6 per month' -> '16 per 4 month' |
| 16203 | 8 per 2 month | 9 per 3 month | no | final_label_repaired: '1 per month (September), 5 per month (August), 3 per month (July)' -> '8 per 2 month' |
| 16204 | 4 per 2 month | 5 per 3 month | yes | final_label_repaired: '1 per month' -> '5 per 3 month'; final_label_repaired: '5 per 3 month' -> '4 per 2 month' |
| 16220 | 11 per 2 month | 11 per 4 month | no | final_label_repaired: 'seizure free for 1 month' -> '11 per 2 month' |
| 16324 | 17 per 3 month | 10 per 3 month | no | final_label_repaired: '3 to 4 per month' -> '7 per 2 month'; final_label_repaired: '7 per 2 month' -> '17 per 3 month' |
| 16335 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: 'multiple per month' -> '7 per 3 month' |
| 16356 | 3 per 2 month | 1 per 4 day | no | final_label_repaired: '1 cluster per 4 days' -> '1 per 4 day'; final_label_repaired: '1 per 4 day' -> '3 per 2 month' |
| 16394 | 3 per 2 month | 1 per 2 to 4 day | no | final_label_repaired: '1 cluster per 2 to 4 days' -> '1 per 2 to 4 day'; final_label_repaired: '1 per 2 to 4 day' -> '3 per 2 month' |
| 16408 | 1 per 3 day | 1 per 3 day | yes | final_label_repaired: '1 per 3 days' -> '1 per 3 day' |
| 16429 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 per 2 to 3 days' -> '1 per 2 to 3 day' |
| 16432 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'approximately every 2 days, escalating to daily' -> '1 per day'; final_label_repaired: '1 per day' -> '1 per 2 day' |
| 16450 | 1 per multiple day | 1 per multiple day | yes | final_label_repaired: 'every several days' -> 'no seizure frequency reference'; final_label_repaired: 'no seizure frequency reference' -> '1 per multiple day' |
| 16529 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster per 5 days' -> '1 per 5 day' |
| 16557 | 1 per 2 to 3 day | 1 per 2 to 3 day | yes | final_label_repaired: '1 cluster per 2-3 days' -> '1 per 2 to 3 day' |
| 16574 | 1 per 4 day | 1 per 4 day | yes | final_label_repaired: '1 cluster every 4 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 day' |
| 16590 | 1 per 4 to 5 day | 1 per 4 to 5 day | yes | final_label_repaired: '1 cluster every 4 to 5 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 4 to 5 day' |
| 16618 | 1 per 5 day | 1 per 5 day | yes | final_label_repaired: '1 cluster per 5 days' -> 'unknown'; final_label_repaired: 'unknown' -> '1 per 5 day' |
| 16645 | 5 per 7 month | 5 per 7 month | yes | final_label_repaired: 'no seizure frequency reference' -> '5 per 7 month' |
| 16674 | 6 per 4 month | 7 per 6 month | yes | final_label_repaired: '3 events in 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '6 per 4 month' |
| 16685 | 10 per 3 month | 10 per 3 month | yes | final_label_repaired: 'multiple per month' -> '10 per 3 month' |
| 16697 | 2 per 3 month | 3 per 6 month | yes | final_label_repaired: '3 per 6 months' -> '3 per 6 month'; final_label_repaired: '3 per 6 month' -> '2 per 3 month' |
| 16704 | 9 per 6 month | 9 per 6 month | yes | final_label_repaired: '7 per month' -> '9 per 6 month' |
| 16714 | 5 per 4 month | 5 per 6 month | no | final_label_repaired: '1 per 3 months' -> '1 per 3 month'; final_label_repaired: '1 per 3 month' -> '5 per 4 month' |
| 16717 | 12 per 6 month | 5 per 6 month | no | final_label_repaired: 'unknown' -> '12 per 6 month' |
| 16719 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '1 per week' -> '7 per 6 month' |
| 16728 | 4 per 6 month | 4 per 6 month | yes | final_label_repaired: 'variable pattern with multiple seizure types' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '4 per 6 month' |
| 16750 | 6 per 7 month | 6 per 7 month | yes | final_label_repaired: 'seizure free since late August' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free for multiple year' -> '6 per 7 month' |
| 16757 | 12 per 3 month | 13 per 6 month | no | final_label_repaired: 'multiple per month' -> '12 per 3 month' |
| 16758 | 8 per 4 month | 9 per 5 month | yes | final_label_repaired: 'multiple seizure types with varying frequencies' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '8 per 4 month' |
| 16772 | 8 per 2 month | 9 per 5 month | no | final_label_repaired: 'unknown' -> '8 per 2 month' |
| 16774 | 19 per 4 month | 19 per 7 month | no | final_label_repaired: '3 per month' -> '19 per 4 month' |
| 16780 | 3 per 7 month | 3 per 7 month | yes | final_label_repaired: 'unknown' -> '3 per 7 month' |
| 16824 | 11 per 5 month | 11 per 5 month | yes | final_label_repaired: 'multiple per month' -> '11 per 5 month' |
| 16833 | 8 per 6 month | 8 per 6 month | yes | final_label_repaired: 'multiple seizure types with different frequencies' -> 'multiple per day'; final_label_repaired: 'multiple per day' -> '8 per 6 month'; evidence_not_exact_substring |
| 16839 | 9 per 3 month | 9 per 4 month | yes | final_label_repaired: 'multiple per month' -> '9 per 3 month'; evidence_not_exact_substring |
| 16867 | 5 per 4 month | 6 per 7 month | no | final_label_repaired: '3 per 7 months' -> '3 per 7 month'; final_label_repaired: '3 per 7 month' -> '5 per 4 month' |
| 16907 | 8 per 4 month | 9 per 6 month | yes | final_label_repaired: 'unknown' -> '8 per 4 month' |
| 16938 | 1 per 2 month | 2 per week | no | final_label_repaired: '1 per month' -> '1 per 2 month' |
| 16947 | 1 per 2 month | 2 per week | no | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 16961 | 1 per 3 month | 2 per week | no | final_label_repaired: '1 per month' -> '1 per 3 month' |
| 16983 | 2 to 3 per week | 2 to 3 per week | yes |  |
| 16990 | 4 to 5 per week | 4 to 5 per week | yes |  |
| 17001 | 5 per week | 5 per week | yes |  |
| 17003 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 17110 | 4 to 5 per week | 4 to 5 cluster per week, multiple per cluster | no | final_label_repaired: '4 to 5 days per week' -> '4 to 5 per week' |
| 17135 | 1 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster | no | final_label_repaired: '5 days per month' -> '1 cluster per month, multiple per cluster' |
| 17146 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 17167 | 1 per week | 1 per week | yes |  |
| 17189 | 1 per 6 month | 1 per month | no | final_label_repaired: '1 per 6 months' -> '1 per 6 month' |
| 17200 | multiple per month | 1 per month | no |  |
| 17201 | 4 per month | 4 per month | yes |  |
| 17273 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 17279 | 1 per 4 to 5 week | 1 per 4 to 5 week | yes | final_label_repaired: '1 per 4 to 5 weeks' -> '1 per 4 to 5 week' |
| 17287 | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | final_label_repaired: '1 every 1 to 2 days' -> '1 per 1 to 2 day' |
