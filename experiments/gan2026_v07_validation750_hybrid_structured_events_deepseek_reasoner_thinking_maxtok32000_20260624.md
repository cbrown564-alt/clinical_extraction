# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-24

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 140 rows.
Rare full-validation reason: validation750_v07_deepseek_reasoner_prompt_iteration_after_validation_error_analysis_validation250_too_low_signal
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
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `992d74a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v07_validation750_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260624.jsonl`

## Summary

- Structured records: 140 / 140
- Call failures: 0
- Parse/schema/label issues: 0
- JSON dialect repairs: 0
- Deterministic repair notes: 67
- Exact selection evidence substrings: 140 / 140
- Purist validation accuracy/micro F1 proxy: 0.9143 (128 / 140)
- Pragmatic validation accuracy/micro F1 proxy: 0.9500 (133 / 140)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: '≤4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | final_label_repaired: '≤4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: 'every 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: '1 cluster per week' -> '1 per 7 to 9 day' |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: 'every 4 weeks' -> '1 per 4 week' |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | final_label_repaired: 'every 3 to 4 weeks' -> '1 per 3 to 4 week' |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 every 3 weeks' -> '1 per 3 week' |
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
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '1 per week' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: 'twice every 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | 1 per day | 1 per day | yes |  |
| 731 | 1 per day | 1 per day | yes |  |
| 743 | unknown | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | final_label_repaired: 'once every 7 to 10 days' -> '1 per 7 to 10 day' |
| 816 | 1 per month | 1 per month | yes |  |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | unknown | multiple per month | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'every other day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: 'every other week' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'bimonthly' -> '1 per 2 month' |
| 960 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every 2 months' -> '1 per 2 month' |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: 'every other month' -> '1 per 2 month' |
| 987 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 seizure every 2 months' -> '1 per 2 month' |
| 1030 | 1 to 3 per month | 1 to 3 per month | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 7 per 3 week | 5 to 7 per 3 week | yes | final_label_repaired: 'multiple per week' -> '7 per 3 week' |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 7 to 9 per month | 21 to 28 per 3 month | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per 10 month | 5 to 7 per year | yes | final_label_repaired: '5 to 7 per year' -> '5 to 7 per 10 month' |
| 1317 | unknown | unknown, multiple per cluster | yes | final_label_repaired: 'multiple episodes in one day (cluster)' -> 'unknown' |
| 1357 | 1 per day | 1 per day | yes | final_label_repaired: '1 seizure (yesterday)' -> '1 per day' |
| 1363 | 1 per day | 3 per day | yes | final_label_repaired: '1 cluster of 3 tonic-clonic seizures' -> '1 per day' |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes | final_label_repaired: '1 per day' -> '7 per week' |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 7 per week | 12 per week | yes |  |
| 1597 | 7 per month | 12 per month | yes |  |
| 1636 | 3 per month | 5 per month | no |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per week | multiple per week | yes |  |
| 1694 | 5 per week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: 'approximately 1.5 per week' -> '5 per week' |
| 1695 | multiple per month | multiple per month | yes |  |
| 1706 | unknown | multiple cluster per month, multiple per cluster | no | final_label_repaired: 'multiple clusters per month' -> 'unknown' |
| 1707 | multiple per week | multiple per week | yes |  |
| 1772 | 5 per month | 11 per 6 month | no | final_label_repaired: '1.5 per month' -> '5 per month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '11 in 3 months' -> '11 per 3 month' |
| 1790 | no seizure frequency reference | 8 per 4 month | no | final_label_repaired: '6 in 4 months' -> 'no seizure frequency reference' |
| 1794 | 3 per month | 8 per 2 month | no |  |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '4 per month' -> '8 per 2 month' |
| 1880 | 3 cluster per month, 4 per cluster | 8 per 2 month | no | final_label_repaired: '3 clusters per month' -> '3 cluster per month, 4 per cluster' |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '4 events in past 3 months' -> '4 per 3 month' |
| 1914 | 1 to 2 per month | 7 per 3 month | yes |  |
| 1922 | 5 per 3 month | 7 per 3 month | yes | final_label_repaired: '5 per 3 months' -> '5 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 per 6 months' -> '7 per 6 month' |
| 1979 | unknown | 6 per 2 month | no | final_label_repaired: '2 clusters per week' -> 'unknown' |
| 1980 | 1 per month | 6 per 3 month | no |  |
| 2023 | 4 per month | 5 per month | no |  |
| 2080 | multiple per month | multiple per month | yes |  |
| 2094 | multiple per month | multiple per month | yes |  |
| 2114 | multiple per month | multiple per month | yes |  |
| 2149 | unknown | unknown | yes |  |
| 2166 | unknown | unknown | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per 2 weeks' -> '3 to 5 per 2 week' |
| 2233 | 3 to 4 per month | 6 to 7 per 2 month | yes |  |
| 2245 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2259 | 2 to 3 per month | 6 to 8 per 3 month | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | multiple per week | 7 to 9 per month | no |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5-7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | final_label_repaired: '2 to 3 in 2 months' -> '2 to 3 per 2 month' |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | final_label_repaired: '5 or 7 per 2 months' -> '5 to 7 per 2 month' |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | final_label_repaired: '6 to 7 per 2 weeks' -> '6 to 7 per 2 week' |
| 2459 | 5 per 5 month | 7 to 9 per 2 week | no | final_label_repaired: 'multiple per week' -> '7 to 9 per 2 week'; final_label_repaired: '7 to 9 per 2 week' -> '5 per 5 month' |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | final_label_repaired: '2 to 3 in 3 months' -> '2 to 3 per 3 month' |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | final_label_repaired: '2 to 3 per two weeks' -> '2 to 3 per 2 week' |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | final_label_repaired: 'multiple per week' -> '8 to 9 per 2 week' |
| 2548 | 2 to 3 per month | 5 to 6 per 2 month | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | final_label_repaired: '1 to 10 per 2 months' -> '1 to 10 per 2 month' |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | final_label_repaired: '3 to 4 per 2 months' -> '3 to 4 per 2 month' |
| 2609 | 1 per day | 1 per day | yes |  |
| 2622 | 1 per day | 1 per day | yes |  |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per night' -> '1 per day' |
| 2678 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per week' -> '1 per day' |
| 2681 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
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
| 2822 | 1 per day | 1 per day | yes |  |
| 2824 | 1 per day | 1 per day | yes |  |
| 2877 | 2 per year | 2 per year | yes |  |
| 2887 | 2 per week | 2 per week | yes |  |
| 2907 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free since 27 March 2024' -> 'seizure free for multiple year' |
| 2932 | 13 per 2 month | seizure free for 9 month | no | final_label_repaired: 'seizure free for 9 month' -> '13 per 2 month' |
| 2938 | seizure free for 8 month | seizure free for 8 month | yes | final_label_repaired: 'seizure free for 8 months' -> 'seizure free for 8 month' |
| 2965 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 2992 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 3015 | seizure free for 1 year | seizure free for 12 month | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes | final_label_repaired: 'seizure free for 16 months' -> 'seizure free for 16 month' |
| 3058 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | yes | final_label_repaired: 'seizure free for 10 months' -> 'seizure free for 10 month' |
| 3095 | seizure free for 12 month | seizure free for 12 month | yes | final_label_repaired: 'seizure free for 12 months' -> 'seizure free for 12 month' |
