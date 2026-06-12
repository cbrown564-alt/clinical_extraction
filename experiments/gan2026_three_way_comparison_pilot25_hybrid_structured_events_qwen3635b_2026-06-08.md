# Gan 2026 LLM-Structured Validation Run

Date: 2026-06-08

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce direct note-to-label schema burden while keeping deterministic code limited to Gan normalization, evidence validation, and scoring.

Minimal change: add an LLM-only structured-events extractor and selector. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only structured-events extractor and clinical selector
- Prompt/program version: `gan2026_hybrid_structured_events_v0.5`
- Temperature: `0.0`
- Max tokens: `5000`
- Mode: `live`
- DSPy cache enabled: `True`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-08T03:15:18.570215+00:00`
- Run finished UTC: `2026-06-08T03:38:54.312200+00:00`
- Wall-clock elapsed: `1415.742` seconds (`23.596` minutes)
- Throughput: `0.017659` rows/sec (`56.63` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels selected by the LLM, validates evidence, and scores.
- Repair mode: `hybrid_full_stack`
- Repair policy: hybrid full deterministic repair stack after structured model selection.
- Repair config: `basic_label_repair=True`, `basic_label_repair_format_only=False`, `breakthrough_repair=True`, `clean_scorer_facing_gold_policy=False`, `dated_sequence_repair=True`, `elapsed_anchor_repair=True`, `json_dialect_repair=True`, `monthly_diary_repair=True`, `non_epileptic_repair=True`, `post_change_burst_repair=True`, `repair_mode=None`, `residual_jerk_repair=True`, `selected_evidence_repair=True`, `usual_interval_repair=True`
- Git commit: `f9845eb`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_three_way_comparison_pilot25_hybrid_structured_events_qwen3635b_2026-06-08.jsonl`

## Summary

- Structured records: 25 / 25
- Call failures: 0
- Parse/schema/label issues: 0
- JSON dialect repairs: 25
- Deterministic repair notes: 18
- Exact selection evidence substrings: 23 / 25
- Purist validation accuracy/micro F1 proxy: 1.0000 (25 / 25)
- Pragmatic validation accuracy/micro F1 proxy: 1.0000 (25 / 25)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 4 per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | 6 to 7 per year | 6 to 7 per year | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 2 to 4 per year' -> '2 to 4 per year' |
| 128 | 17 per month | 17 per month | yes | json_dialect_repaired: python_literal |
| 156 | 1 per 6 day | 1 per 6 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'every 2 days' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per week' -> '1 per 7 to 9 day'; evidence_not_exact_substring |
| 190 | 1 per 4 week | 1 per 4 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 cluster per month' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per month' -> '1 per 4 week' |
| 212 | 1 to 2 per month | 1 per 3 to 4 week | yes | json_dialect_repaired: python_literal |
| 218 | 1 per 3 week | 1 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal |
| 280 | multiple per day | multiple per day | yes | json_dialect_repaired: python_literal |
| 338 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'many per month' -> 'multiple per month' |
| 409 | 1 per month | 1 per month | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 1 per month' -> '1 per month' |
| 419 | 2 per year | 2 per year | yes | json_dialect_repaired: python_literal |
| 446 | 15 per 3 month | 2 per week | yes | json_dialect_repaired: python_literal; final_label_repaired: '≤ 2 per week' -> '2 per week'; final_label_repaired: '2 per week' -> '15 per 3 month' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes | json_dialect_repaired: python_literal |
| 467 | 9 per month | 9 per month | yes | json_dialect_repaired: python_literal |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 2 per 16 month | 1 per 8 month | yes | json_dialect_repaired: python_literal; final_label_repaired: '1 per eight months' -> '2 per 16 month'; evidence_not_exact_substring |
| 659 | 2 per 4 day | 2 per 4 day | yes | json_dialect_repaired: python_literal; final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
