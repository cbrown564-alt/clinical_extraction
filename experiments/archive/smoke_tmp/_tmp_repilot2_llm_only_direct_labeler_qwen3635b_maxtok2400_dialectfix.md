# Gan 2026 LLM-First Validation Run

Date: 2026-06-08

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 50 rows.
Rare full-validation reason: not applicable for this run size.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `ollama_chat/qwen3.6:35b`
- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: `http://localhost:11434`
- Model role: LLM-only direct-labeler note-to-label extractor
- Prompt/program version: `gan2026_llm_only_direct_labeler_v0.1`
- Temperature: `0.0`
- Max tokens: `2400`
- Mode: `live`
- DSPy cache enabled: `False`
- Ollama Qwen thinking mode: `disabled` (`think=false`)
- Reused raw model outputs: `0`
- Reuse source: `none`
- Run started UTC: `2026-06-08T05:55:11.181299+00:00`
- Run finished UTC: `2026-06-08T06:06:57.447442+00:00`
- Wall-clock elapsed: `706.266` seconds (`11.771` minutes)
- Throughput: `0.070795` rows/sec (`14.125` sec/row)
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `f9845eb`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/_tmp_repilot2_llm_only_direct_labeler_qwen3635b_maxtok2400_dialectfix.jsonl`

## Summary

- Decision records: 47 / 50
- Call failures: 0
- Parse/schema/label issues: 3
- Deterministic repair notes: 25
- Exact evidence substrings: 43 / 50
- Purist validation accuracy/micro F1 proxy: 0.8600 (43 / 50)
- Pragmatic validation accuracy/micro F1 proxy: 0.8800 (44 / 50)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | yes | final_label_repaired: 'multiple per day' -> '4 per day' |
| 40 | 4 per week | 4 per week | yes |  |
| 79 | 6 to 7 per year | 6 to 7 per year | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 17 per month | 17 per month | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per 7 day | 1 per 7 day | yes | final_label_repaired: '1 per week' -> '1 per 7 day' |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '0.5 per day' -> '1 per 2 day' |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | final_label_repaired: 'multiple per week' -> '1 per 7 to 9 day'; evidence_not_exact_substring |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: 'unknown' -> '1 per 4 week' |
| 198 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 per month' -> '1 per 4 week' |
| 212 | 2 to 3 per month | 1 per 3 to 4 week | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 month | 1 per 4 month | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 |  | multiple per month | no | invalid_json: Invalid control character at; evidence_not_exact_substring |
| 409 | 1 per month | 1 per month | yes |  |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes | final_label_repaired: '2 to 3 per week' -> '2 per week' |
| 466 | 21 to 28 per month | 21 to 28 per month | yes |  |
| 467 | 9 per month | 9 per month | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | final_label_repaired: '4 to 10 per month' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 day | 2 per 4 day | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per 2 week | 2 per 2 week | yes | final_label_repaired: '1 per week' -> '2 per 2 week' |
| 678 | 2 per 4 month | 2 per 4 month | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 | multiple per day | 1 per day | no | evidence_not_exact_substring |
| 731 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 743 | multiple per day | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> 'multiple per week' |
| 763 | 1 per week | 1 per week | yes |  |
| 790 | 1 to 2 per week | 1 per 7 to 10 day | no |  |
| 816 | 1 per month | 1 per month | yes | final_label_repaired: 'monthly' -> '1 per month' |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per day | multiple per month | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 |  | 1 per 2 month | no | invalid_json: Expecting ',' delimiter; evidence_not_exact_substring |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 |  | 1 per 2 month | no | invalid_json: Invalid control character at; evidence_not_exact_substring |
| 1030 | 1 per month | 1 to 3 per month | no | final_label_repaired: 'unknown' -> '1 per month'; evidence_not_exact_substring |
| 1046 | unknown | 3 to 5 per month | no |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 5 to 7 per 6 week | 5 to 7 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '5 to 7 per 6 week'; evidence_not_exact_substring |
