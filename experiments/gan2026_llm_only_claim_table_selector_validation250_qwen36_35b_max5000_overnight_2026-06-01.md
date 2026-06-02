# Gan 2026 LLM-Only Claim Table Selector V5

Date: 2026-06-02

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 10 rows.
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

- Structured claim-table records: 0 / 10
- Call failures: 0
- Parse/schema/label issues: 10
- Exact claim evidence substrings: 0 / 0
- Exact selected final evidence substrings: 0 / 10
- raw final-query score: Purist 0.0000 (0 / 10), Pragmatic 0.0000 (0 / 10)
- Strict-format score: Purist 0.0000 (0 / 10), Pragmatic 0.0000 (0 / 10)
- Frozen clean scorer-facing score: Purist 0.0000 (0 / 10), Pragmatic 0.0000 (0 / 10)
- Rows changed by downstream repair layers: 0

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 0 |
| claim_extraction | 10 |
| temporality_conflict | 0 |
| final_query | 10 |
| parse_schema | 10 |
| scorer_format | 10 |

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
