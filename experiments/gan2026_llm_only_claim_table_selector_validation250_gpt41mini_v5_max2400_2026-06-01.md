# Gan 2026 LLM-Only Claim Table Selector V5

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Pipeline: `gan2026_llm_only_claim_table_selector_v5`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only direct-labeler claim extractor and final query selector
- Prompt/program version: `gan2026_llm_only_claim_table_selector_v5`
- Temperature: `0.0`
- Max tokens: `2400`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Prompt policy taxonomy: `sct_v5.schema.scalar_enum_output`, `sct_v5.schema.strict_json_object`, `sct_v5.evidence.exact_substring`, `sct_v5.gan_label.parser_ready_surface`, `sct_v5.gan_label.interval_preservation`, `sct_v5.gan_label.cluster_dual_axis`, `sct_v5.schema.cluster_axis_state`, `sct_v5.selection.current_burden_precedence`, `sct_v5.selection.add_same_window_counts`, `sct_v5.boundary.unknown_no_reference_seizure_free`, `sct_v5.schema.boundary_state`, `sct_v5.exclusion.proxy_or_conditional_frequency`, `sct_v5.gan_label.compact_interval_notation`, `sct_v5.gan_label.maximum_burden`, `sct_v5.selection.constrained_selector`
- Required ablations before 25/50/250 ladder runs: `raw_model_claim_table`, `strict_schema_repair`, `constrained_selector_state`, `clean_scorer_facing_policy`
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `ac00cff`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 248 / 250
- Call failures: 0
- Parse/schema/label issues: 2
- Exact claim evidence substrings: 567 / 574
- Exact selected final evidence substrings: 246 / 250
- raw final-query score: Purist 0.8920 (223 / 250), Pragmatic 0.9040 (226 / 250)
- Strict-format score: Purist 0.8960 (224 / 250), Pragmatic 0.9080 (227 / 250)
- Frozen clean scorer-facing score: Purist 0.9080 (227 / 250), Pragmatic 0.9200 (230 / 250)
- Rows changed by downstream repair layers: 23

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 15 |
| claim_extraction | 9 |
| temporality_conflict | 1 |
| final_query | 4 |
| parse_schema | 2 |
| scorer_format | 8 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 190 |  | unparsable_label: 1 cluster per 4 week (Unparsable cluster label: '1 cluster per 4 week') |  |
| 1454 | claim evidence not exact (c2: The shorter episodes often occur towards the end of longer, hotter shifts and tend to cluster on consecutive days when the weather is warmer.) | unparsable_label: 1 per 7 day, 6 per 7 day (Unparsable label (raw: '1 per 7 day, 6 per 7 day' / normalized: '1 per 7 day, 6 per 7 day')) |  |
| 1694 | claim evidence not exact (c2: She has been generally stable for several months prior to this cluster) |  |  |
| 1923 | claim evidence not exact (c2: Over the past six months he describes ... five epileptic spasms) |  |  |
| 2166 |  | unparsable_label: frequent (Unparsable label (raw: 'frequent' / normalized: 'frequent')) |  |
| 2609 |  | unparsable_label: 1 per night (Unparsable label (raw: '1 per night' / normalized: '1 per night')) |  |
| 3532 | claim evidence not exact (c2: Frequency increased by ~20% after dose increase. This has been over a 3‑week observation window); selected evidence not exact (Frequency increased by ~20% after dose increase. This has been over a 3‑week observation window) |  |  |
| 3766 |  | missing_final_label | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event' |
| 3774 | claim evidence not exact (c2: a recent work rota change with earlier starts appears to have coincided with two nocturnal events in the past quarter) |  |  |
| 3849 | claim evidence not exact (c1: "Frequency currently described as \"sz x3/d\" on their seizure diary, with clustering on late shifts."); selected evidence not exact ("Frequency currently described as \"sz x3/d\" on their seizure diary, with clustering on late shifts.") |  |  |
| 3988 | claim evidence not exact (c5: a rescue buccal midazolam plan remains in place for any prolonged event lasting more than 5 minutes, although this has not been required over the last year) |  |  |
| 5379 |  | missing_final_label | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple' |
| 5551 |  | unparsable_label: several per day (Unparsable label (raw: 'several per day' / normalized: 'several per day')) |  |
| 5567 |  | unparsable_label: Several per week (Unparsable label (raw: 'several per week' / normalized: 'several per week')) |  |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes | segmentation_sectioning |
| 128 | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | 1 cluster per 4 week | 1 cluster per 4 week | 1 per 4 week | 1 per 4 week |  | yes | scorer_format |
| 198 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 278 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster | multiple per month | no | no |  |
| 409 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | 1 per 8 month | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | 2 per 4 day | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
| 665 | 2 per 2 week | 2 per 2 week | 2 per 2 week | 2 per 2 week | yes | yes |  |
| 678 | 2 per 4 month | 2 per 4 month | 2 per 4 month | 2 per 4 month | yes | yes |  |
| 694 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes | segmentation_sectioning |
| 725 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 744 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 763 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | 1 per 12 month | 1 per 12 month | 1 per 12 month | 1 per year | yes | yes |  |
| 854 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 899 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | 5 per month | 5 per month | 5 per month | 3 to 5 per month | no | no |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | 3 to 5 per 1 week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes |  |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes |  |
| 1207 | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1281 | 5 to 7 per 1 year | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | yes | yes |  |
| 1317 | 1 cluster per 1 day, multiple per cluster | 1 cluster per day, multiple per cluster | 1 cluster per day, multiple per cluster | unknown, multiple per cluster | no | no |  |
| 1357 | 1 per 1 day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 1363 | 3 per 1 day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 1413 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes | segmentation_sectioning |
| 1454 | 1 per 7 day, 6 per 7 day | 1 per 7 day, 6 per 7 day | 1 per 7 day, 6 per 7 day | 7 per week |  |  | claim_extraction,scorer_format |
| 1486 | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1573 | 11 per 1 week | 11 per week | 11 per week | 11 per week | yes | yes | segmentation_sectioning |
| 1591 | 11 per 1 month | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 1596 | 12 per 1 week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1597 | 12 per 1 month | 12 per month | 12 per month | 12 per month | yes | yes |  |
| 1636 | 5 per 1 month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1640 | 5 per 1 week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 1687 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 1694 | 3 per 2 week | 3 per 2 week | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | yes | claim_extraction |
| 1695 | seizure free for 1 month | seizure free for 1 month | seizure free for 1 month | multiple per month | no | no |  |
| 1706 | unknown | unknown | unknown | multiple cluster per month, multiple per cluster | no | no |  |
| 1707 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | 11 per 6 month | 11 per 6 month | yes | yes |  |
| 1773 | 11 per 3 month | 11 per 3 month | 11 per 3 month | 11 per 3 month | yes | yes |  |
| 1790 | 8 per 4 month | 8 per 4 month | 8 per 4 month | 8 per 4 month | yes | yes | segmentation_sectioning |
| 1794 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1866 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1880 | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 8 per 2 month | yes | yes | temporality_conflict |
| 1887 | 4 per 3 month | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes |  |
| 1914 | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1922 | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1923 | 2 to 3 per 6 month | 2 to 3 per 6 month | 2 to 3 per 6 month | 7 per 6 month | no | no | claim_extraction |
| 1979 | 6 per 2 month | 6 per 2 month | 6 per 2 month | 6 per 2 month | yes | yes |  |
| 1980 | 6 per 3 month | 6 per 3 month | 6 per 3 month | 6 per 3 month | yes | yes |  |
| 2023 | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 2080 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2094 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2114 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2149 | unknown | unknown | unknown | unknown | yes | yes |  |
| 2166 | frequent | frequent | frequent | unknown |  |  | scorer_format |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | yes |  |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | yes |  |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2366 | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per year | yes | yes |  |
| 2369 | 3 to 4 per 1 month | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | yes | yes |  |
| 2425 | 6 to 8 per 1 month | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | yes | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | yes |  |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | yes |  |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | yes |  |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | yes |  |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | yes |  |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes |  |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | yes |  |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | yes |  |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | yes |  |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | yes |  |
| 2609 | 1 per night | 1 per day | 1 per day | 1 per day |  | yes | scorer_format |
| 2622 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2628 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2678 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2681 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 2731 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 2740 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2748 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2759 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2762 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2765 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2776 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2789 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2812 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2822 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2824 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2877 | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 2887 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 2932 | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | yes | yes |  |
| 2938 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 8 month | yes | yes |  |
| 2965 | seizure free for 1 year 4 month | seizure free for 1 year | seizure free for 1 year | seizure free for 16 month | yes | yes |  |
| 2992 | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 3015 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 12 month | yes | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 3095 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes | segmentation_sectioning |
| 3118 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for multiple month | yes | yes |  |
| 3137 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | yes |  |
| 3242 | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3261 | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | no | no |  |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3281 | 8 per 30 day | 8 per 30 day | 8 per 30 day | 8 per month | yes | yes |  |
| 3297 | 6 per 30 day | 6 per 30 day | 6 per 30 day | 6 per month | yes | yes |  |
| 3325 | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 3356 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3371 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3436 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3468 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3469 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3482 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3493 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3507 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3512 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3528 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3532 | unknown | unknown | unknown | unknown | yes | yes | claim_extraction,final_query |
| 3534 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | unknown | yes | yes |  |
| 3600 | unknown | unknown | unknown | unknown | yes | yes | segmentation_sectioning |
| 3623 | unknown | unknown | unknown | 7 per week | no | no | segmentation_sectioning |
| 3643 | 1 cluster per week, up to 7 per cluster | 1 cluster per week, up to 7 per cluster | 1 cluster per week, up to 7 per cluster | 7 per week | yes | yes |  |
| 3681 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3682 | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3710 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 3753 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 3766 | None | None | None | 8 per year |  |  | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event'; claim_extraction,final_query,parse_schema,scorer_format |
| 3774 | 9 per year | 9 per year | 9 per year | 9 per year | yes | yes | claim_extraction |
| 3791 | 10 per 12 month | 10 per 12 month | 10 per 12 month | 10 per year | yes | yes |  |
| 3801 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3806 | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3827 | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 3846 | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 3849 | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes | claim_extraction,final_query |
| 3889 | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3892 | 3 per year | 3 per year | 3 per year | 3 per year | yes | yes |  |
| 3940 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes | segmentation_sectioning |
| 3949 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3988 | 1 per week | 1 per week | 1 per week | multiple per week | no | no | claim_extraction |
| 3995 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 3999 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4022 | 8 per month | 8 per month | 8 per month | 8 per month | yes | yes |  |
| 4026 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4116 | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4173 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes | segmentation_sectioning |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes | segmentation_sectioning |
| 4258 | 4 per 7 day | 4 per 7 day | 4 per 7 day | 4 per week | yes | yes |  |
| 4337 | 3 per 4 month | 3 per 4 month | 3 per 4 month | 3 per 3 month | no | no |  |
| 4345 | 4 per month | 4 per month | 4 per month | 4 per month | yes | yes |  |
| 4368 | 5 per 2 month | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes |  |
| 4402 | 1 to 2 per month | 1 to 2 per month | 1 to 2 per month | 7 per 7 month | no | no |  |
| 4410 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 4 per 7 month | yes | yes | segmentation_sectioning |
| 4478 | 19 per week | 19 per week | 19 per week | 19 per week | yes | yes |  |
| 4480 | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | yes |  |
| 4562 | 1 per 6 week | 1 per 6 week | 1 per 6 week | 1 per 6 week | yes | yes |  |
| 4563 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 4574 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 4592 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 4597 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 4624 | 1 per 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | 1 per 3 to 4 day | yes | yes |  |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | yes |  |
| 4690 | seizure free interval | seizure free for multiple year | seizure free for multiple year | multiple per day | no | no |  |
| 4694 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4700 | unknown | unknown | unknown | multiple per day | yes | yes | segmentation_sectioning |
| 4709 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4731 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4732 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4771 | multiple per month | multiple per month | multiple per month | unknown | yes | yes |  |
| 4839 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes |  |
| 4842 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 4910 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes | segmentation_sectioning |
| 4919 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 4951 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 4956 | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 4992 | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | seizure free for 11 month | yes | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 months | yes | yes |  |
| 5082 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5092 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5110 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5121 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5136 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 5141 | seizure free for 1.5 month | seizure free for 1.5 month | seizure free for 1.5 month | seizure free for multiple month | yes | yes |  |
| 5197 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5210 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5221 | seizure free for 1 year 9 month | seizure free for 1 year | seizure free for 1 year | seizure free for multiple month | yes | yes |  |
| 5248 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 5331 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 5345 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5351 | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 5379 | None | None | None | seizure free for multiple month |  |  | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; claim_extraction,final_query,parse_schema,scorer_format |
| 5406 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | seizure free for multiple month | yes | yes |  |
| 5476 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5490 | unknown | unknown | unknown | unknown | yes | yes | segmentation_sectioning |
| 5491 | 2 per 6 week | 2 per 6 week | 2 per 6 week | unknown | no | no |  |
| 5504 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5507 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5528 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | 1 per month | no | no |  |
| 5534 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per multiple month | no | no |  |
| 5551 | several per day | several per day | multiple per day | multiple per day |  | yes | scorer_format |
| 5567 | Several per week | several per week | multiple per week | multiple per week |  | yes | scorer_format |
| 5584 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
