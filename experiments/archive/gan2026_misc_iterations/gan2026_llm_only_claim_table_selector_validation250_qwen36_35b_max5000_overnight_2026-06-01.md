# Gan 2026 LLM-Only Claim Table Selector V5

Date: 2026-06-02

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Pipeline: `gan2026_llm_only_claim_table_selector_v5`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only direct-labeler claim extractor and final query selector
- Prompt/program version: `gan2026_llm_only_claim_table_selector_v5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `False`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Prompt policy taxonomy: `sct_v5.schema.scalar_enum_output`, `sct_v5.schema.strict_json_object`, `sct_v5.evidence.exact_substring`, `sct_v5.gan_label.parser_ready_surface`, `sct_v5.gan_label.interval_preservation`, `sct_v5.gan_label.cluster_dual_axis`, `sct_v5.schema.cluster_axis_state`, `sct_v5.selection.current_burden_precedence`, `sct_v5.selection.add_same_window_counts`, `sct_v5.boundary.unknown_no_reference_seizure_free`, `sct_v5.schema.boundary_state`, `sct_v5.exclusion.proxy_or_conditional_frequency`, `sct_v5.gan_label.compact_interval_notation`, `sct_v5.gan_label.maximum_burden`, `sct_v5.selection.constrained_selector`
- Required ablations before 25/50/250 ladder runs: `raw_model_claim_table`, `strict_schema_repair`, `constrained_selector_state`, `clean_scorer_facing_policy`
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `a11bedc`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_claim_table_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 0 / 250
- Call failures: 0
- Parse/schema/label issues: 250
- Exact claim evidence substrings: 0 / 0
- Exact selected final evidence substrings: 0 / 250
- raw final-query score: Purist 0.0000 (0 / 250), Pragmatic 0.0000 (0 / 250)
- Strict-format score: Purist 0.0000 (0 / 250), Pragmatic 0.0000 (0 / 250)
- Frozen clean scorer-facing score: Purist 0.0000 (0 / 250), Pragmatic 0.0000 (0 / 250)
- Rows changed by downstream repair layers: 0

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 0 |
| claim_extraction | 250 |
| temporality_conflict | 0 |
| final_query | 250 |
| parse_schema | 250 |
| scorer_format | 250 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 10 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 40 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 79 |  | missing_final_label | schema_validation_error: Field required |
| 103 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 128 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 156 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 180 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 182 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 187 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 190 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 198 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 212 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 218 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 243 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 278 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 280 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 338 |  | missing_final_label | schema_validation_error: Field required |
| 409 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 419 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 446 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 466 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 467 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 531 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 598 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 659 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 665 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 678 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 694 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 704 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 725 |  | missing_final_label | schema_validation_error: Field required |
| 731 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 743 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 744 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 763 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 790 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 816 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 849 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 854 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 869 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 891 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 899 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 959 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 960 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 978 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 987 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1030 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1046 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1070 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1094 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1165 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1171 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1207 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1223 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1249 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1281 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1317 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1357 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1363 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1413 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1454 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1486 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1573 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1591 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1596 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1597 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1636 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1640 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1687 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1694 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1695 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1706 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1707 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1772 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1773 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1790 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1794 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1866 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1880 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1887 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1914 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1922 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1923 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 1979 |  | missing_final_label | invalid_json: Expecting ',' delimiter |
| 1980 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2023 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2080 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2094 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2114 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2149 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2166 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2228 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2233 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2245 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2259 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2354 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2366 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2369 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2374 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2425 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2427 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2435 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2437 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2440 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2456 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2459 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2487 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2513 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2541 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2548 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2554 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2558 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2609 |  | missing_final_label | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event' |
| 2622 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2628 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2678 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2681 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2698 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2731 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2740 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2748 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2759 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2762 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2765 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2776 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2789 |  | missing_final_label | schema_validation_error: Field required |
| 2812 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2822 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2824 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2877 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2887 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2907 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2932 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2938 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2965 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 2992 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3015 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3048 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3058 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3082 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3095 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3113 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3118 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3137 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3224 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3242 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3261 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3262 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3281 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3297 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3325 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3356 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3371 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3436 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3468 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3469 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3482 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3493 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3507 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3512 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3528 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3532 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3534 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3600 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3623 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3643 |  | missing_final_label | schema_validation_error: Field required |
| 3681 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3682 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3710 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3753 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3766 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3774 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3791 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3801 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3806 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3827 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3846 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3849 |  | missing_final_label | schema_validation_error: Field required |
| 3889 |  | missing_final_label | schema_validation_error: Field required |
| 3892 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3940 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3949 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3988 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3995 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 3999 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4022 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4026 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4092 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4100 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4110 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4116 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4173 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4243 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4258 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4337 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4345 |  | missing_final_label | schema_validation_error: Field required |
| 4368 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4402 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4410 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4478 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4480 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4496 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4562 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4563 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4574 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4592 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4597 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4624 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4631 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4690 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4694 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4700 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4709 |  | missing_final_label | schema_validation_error: Field required |
| 4731 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4732 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4771 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4839 |  | missing_final_label | schema_validation_error: Field required |
| 4842 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4910 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4919 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4926 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4951 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4956 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4992 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 4994 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5040 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5082 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5092 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5110 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5121 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5136 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5141 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5197 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5210 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5221 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5248 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5331 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5345 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5351 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5379 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5406 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5476 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5490 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5491 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5504 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5507 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5528 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5534 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5551 |  | missing_final_label | schema_validation_error: Field required |
| 5567 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |
| 5584 |  | missing_final_label | invalid_json: Expecting property name enclosed in double quotes |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | None | None | None | 4 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 40 | None | None | None | 4 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 79 | None | None | None | 6 to 7 per year |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 103 | None | None | None | 2 to 4 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 128 | None | None | None | 17 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 156 | None | None | None | 1 per 6 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 180 | None | None | None | 1 per 7 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 182 | None | None | None | 1 per 2 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 187 | None | None | None | 1 per 7 to 9 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 190 | None | None | None | 1 per 4 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 198 | None | None | None | 1 per 4 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 212 | None | None | None | 1 per 3 to 4 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 218 | None | None | None | 1 per 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 243 | None | None | None | 1 per 4 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 278 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 280 | None | None | None | multiple per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 338 | None | None | None | multiple per month |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 409 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 419 | None | None | None | 2 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 446 | None | None | None | 2 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 466 | None | None | None | 21 to 28 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 467 | None | None | None | 9 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 531 | None | None | None | 12 to 30 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 598 | None | None | None | 1 per 8 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 659 | None | None | None | 2 per 4 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 665 | None | None | None | 2 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 678 | None | None | None | 2 per 4 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 694 | None | None | None | 1 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 704 | None | None | None | 2 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 725 | None | None | None | 1 per day |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 731 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 743 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 744 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 763 | None | None | None | 1 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 790 | None | None | None | 1 per 7 to 10 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 816 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 849 | None | None | None | 1 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 854 | None | None | None | 1 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 869 | None | None | None | multiple per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 891 | None | None | None | 1 per 2 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 899 | None | None | None | 1 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 959 | None | None | None | 1 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 960 | None | None | None | 1 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 978 | None | None | None | 1 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 987 | None | None | None | 1 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1030 | None | None | None | 1 to 3 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1046 | None | None | None | 3 to 5 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1070 | None | None | None | 3 to 4 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1094 | None | None | None | 3 to 5 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1165 | None | None | None | 5 to 7 per 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1171 | None | None | None | 7 to 9 per 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1207 | None | None | None | 21 to 28 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1223 | None | None | None | 3 to 4 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1249 | None | None | None | 2 to 4 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1281 | None | None | None | 5 to 7 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1317 | None | None | None | unknown, multiple per cluster |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1357 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1363 | None | None | None | 3 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1413 | None | None | None | 9 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1454 | None | None | None | 7 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1486 | None | None | None | 3 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1573 | None | None | None | 11 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1591 | None | None | None | 11 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1596 | None | None | None | 12 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1597 | None | None | None | 12 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1636 | None | None | None | 5 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1640 | None | None | None | 5 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1687 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1694 | None | None | None | 1 cluster per 2 week, 3 per cluster |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1695 | None | None | None | multiple per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1706 | None | None | None | multiple cluster per month, multiple per cluster |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1707 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1772 | None | None | None | 11 per 6 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1773 | None | None | None | 11 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1790 | None | None | None | 8 per 4 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1794 | None | None | None | 8 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1866 | None | None | None | 8 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1880 | None | None | None | 8 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1887 | None | None | None | 4 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1914 | None | None | None | 7 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1922 | None | None | None | 7 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1923 | None | None | None | 7 per 6 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 1979 | None | None | None | 6 per 2 month |  |  | invalid_json: Expecting ',' delimiter; claim_extraction,final_query,parse_schema,scorer_format |
| 1980 | None | None | None | 6 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2023 | None | None | None | 5 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2080 | None | None | None | multiple per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2094 | None | None | None | multiple per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2114 | None | None | None | multiple per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2149 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2166 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2228 | None | None | None | 3 to 5 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2233 | None | None | None | 6 to 7 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2245 | None | None | None | 7 to 8 per 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2259 | None | None | None | 6 to 8 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2354 | None | None | None | 6 to 7 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2366 | None | None | None | 2 to 4 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2369 | None | None | None | 3 to 4 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2374 | None | None | None | 7 to 9 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2425 | None | None | None | 6 to 8 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2427 | None | None | None | 3 to 5 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2435 | None | None | None | 5 to 7 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2437 | None | None | None | 2 to 3 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2440 | None | None | None | 5 to 7 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2456 | None | None | None | 6 to 7 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2459 | None | None | None | 7 to 9 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2487 | None | None | None | 2 to 3 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2513 | None | None | None | 2 to 3 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2541 | None | None | None | 8 to 9 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2548 | None | None | None | 5 to 6 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2554 | None | None | None | 1 to 10 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2558 | None | None | None | 3 to 4 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2609 | None | None | None | 1 per day |  |  | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event'; claim_extraction,final_query,parse_schema,scorer_format |
| 2622 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2628 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2678 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2681 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2698 | None | None | None | 1 per 2 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2731 | None | None | None | 1 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2740 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2748 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2759 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2762 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2765 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2776 | None | None | None | 1 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2789 | None | None | None | 1 per week |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 2812 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2822 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2824 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2877 | None | None | None | 2 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2887 | None | None | None | 2 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2907 | None | None | None | seizure free for 6 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2932 | None | None | None | seizure free for 9 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2938 | None | None | None | seizure free for 8 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2965 | None | None | None | seizure free for 16 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 2992 | None | None | None | seizure free for 7 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3015 | None | None | None | seizure free for 12 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3048 | None | None | None | seizure free for 16 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3058 | None | None | None | seizure free for 12 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3082 | None | None | None | seizure free for 10 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3095 | None | None | None | seizure free for 12 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3113 | None | None | None | seizure free for 14 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3118 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3137 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3224 | None | None | None | 1 cluster per month, 6 to 7 per cluster |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3242 | None | None | None | 2 cluster per month, 5 per cluster |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3261 | None | None | None | 2 cluster per month, 4 per cluster |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3262 | None | None | None | 2 cluster per month, 5 per cluster |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3281 | None | None | None | 8 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3297 | None | None | None | 6 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3325 | None | None | None | 3 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3356 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3371 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3436 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3468 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3469 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3482 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3493 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3507 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3512 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3528 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3532 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3534 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3600 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3623 | None | None | None | 7 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3643 | None | None | None | 7 per week |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 3681 | None | None | None | 9 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3682 | None | None | None | 6 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3710 | None | None | None | 5 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3753 | None | None | None | 1 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3766 | None | None | None | 8 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3774 | None | None | None | 9 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3791 | None | None | None | 10 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3801 | None | None | None | 9 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3806 | None | None | None | 6 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3827 | None | None | None | 7 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3846 | None | None | None | 2 per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3849 | None | None | None | 3 per day |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 3889 | None | None | None | 8 per year |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 3892 | None | None | None | 3 per year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3940 | None | None | None | 4 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3949 | None | None | None | 4 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3988 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3995 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 3999 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4022 | None | None | None | 8 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4026 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4092 | None | None | None | 1 per 2 to 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4100 | None | None | None | 1 per 2 to 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4110 | None | None | None | 1 per 1 to 2 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4116 | None | None | None | 1 per 1 to 2 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4173 | None | None | None | 1 per 2 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4243 | None | None | None | 1 per 2 to 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4258 | None | None | None | 4 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4337 | None | None | None | 3 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4345 | None | None | None | 4 per month |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 4368 | None | None | None | 5 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4402 | None | None | None | 7 per 7 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4410 | None | None | None | 4 per 7 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4478 | None | None | None | 19 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4480 | None | None | None | 3 to 5 per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4496 | None | None | None | 7 to 8 per 3 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4562 | None | None | None | 1 per 6 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4563 | None | None | None | 1 per 4 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4574 | None | None | None | 1 per 4 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4592 | None | None | None | 1 per 2 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4597 | None | None | None | 1 per 3 week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4624 | None | None | None | 1 per 3 to 4 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4631 | None | None | None | 1 per 14 to 21 day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4690 | None | None | None | multiple per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4694 | None | None | None | multiple per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4700 | None | None | None | multiple per day |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4709 | None | None | None | multiple per day |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 4731 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4732 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4771 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4839 | None | None | None | seizure free for multiple month |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 4842 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4910 | None | None | None | seizure free for 2 year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4919 | None | None | None | seizure free for 2 year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4926 | None | None | None | seizure free for 1 year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4951 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4956 | None | None | None | seizure free for 7 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4992 | None | None | None | seizure free for 11 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 4994 | None | None | None | seizure free for 6 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5040 | None | None | None | seizure free for 6 months |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5082 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5092 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5110 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5121 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5136 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5141 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5197 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5210 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5221 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5248 | None | None | None | seizure free for multiple year |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5331 | None | None | None | seizure free for 12 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5345 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5351 | None | None | None | seizure free for 18 month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5379 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5406 | None | None | None | seizure free for multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5476 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5490 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5491 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5504 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5507 | None | None | None | unknown |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5528 | None | None | None | 1 per month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5534 | None | None | None | 1 per multiple month |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5551 | None | None | None | multiple per day |  |  | schema_validation_error: Field required; claim_extraction,final_query,parse_schema,scorer_format |
| 5567 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
| 5584 | None | None | None | multiple per week |  |  | invalid_json: Expecting property name enclosed in double quotes; claim_extraction,final_query,parse_schema,scorer_format |
