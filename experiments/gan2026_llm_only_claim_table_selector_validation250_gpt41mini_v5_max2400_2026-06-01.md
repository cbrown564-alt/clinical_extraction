# Gan 2026 LLM-Only Claim Table Selector V5

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 125 rows.
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

- Structured claim-table records: 125 / 125
- Call failures: 0
- Parse/schema/label issues: 0
- Exact claim evidence substrings: 270 / 273
- Exact selected final evidence substrings: 125 / 125
- raw final-query score: Purist 0.9200 (115 / 125), Pragmatic 0.9280 (116 / 125)
- Strict-format score: Purist 0.9280 (116 / 125), Pragmatic 0.9360 (117 / 125)
- Frozen clean scorer-facing score: Purist 0.9360 (117 / 125), Pragmatic 0.9440 (118 / 125)
- Rows changed by downstream repair layers: 15

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 5 |
| claim_extraction | 3 |
| temporality_conflict | 1 |
| final_query | 0 |
| parse_schema | 0 |
| scorer_format | 4 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 190 |  | unparsable_label: 1 cluster per 4 week (Unparsable cluster label: '1 cluster per 4 week') |  |
| 1454 | claim evidence not exact (c2: The shorter episodes often occur towards the end of longer, hotter shifts and tend to cluster on consecutive days when the weather is warmer.) | unparsable_label: 1 per 7 day, 6 per 7 day (Unparsable label (raw: '1 per 7 day, 6 per 7 day' / normalized: '1 per 7 day, 6 per 7 day')) |  |
| 1694 | claim evidence not exact (c2: She has been generally stable for several months prior to this cluster) |  |  |
| 1923 | claim evidence not exact (c2: Over the past six months he describes ... five epileptic spasms) |  |  |
| 2166 |  | unparsable_label: frequent (Unparsable label (raw: 'frequent' / normalized: 'frequent')) |  |
| 2609 |  | unparsable_label: 1 per night (Unparsable label (raw: '1 per night' / normalized: '1 per night')) |  |

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
