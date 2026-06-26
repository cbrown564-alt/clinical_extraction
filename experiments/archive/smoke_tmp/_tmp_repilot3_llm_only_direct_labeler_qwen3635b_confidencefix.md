# Gan 2026 LLM-First Validation Run

Date: 2026-06-08

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 120 rows.
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
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `f9845eb`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/_tmp_repilot3_llm_only_direct_labeler_qwen3635b_confidencefix.jsonl`

## Summary

- Decision records: 114 / 120
- Call failures: 0
- Parse/schema/label issues: 6
- Deterministic repair notes: 55
- Exact evidence substrings: 102 / 120
- Purist validation accuracy/micro F1 proxy: 0.8917 (107 / 120)
- Pragmatic validation accuracy/micro F1 proxy: 0.9083 (109 / 120)

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
| 816 | 1 per month | 1 per month | yes | evidence_not_exact_substring |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 | multiple per day | multiple per month | yes | final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 891 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 per day' -> '1 per 2 day' |
| 899 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '2 per month' -> '1 per 2 month' |
| 960 |  | 1 per 2 month | no | invalid_json: Expecting ',' delimiter; evidence_not_exact_substring |
| 978 | 1 per 2 month | 1 per 2 month | yes | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 987 |  | 1 per 2 month | no | invalid_json: Invalid control character at; evidence_not_exact_substring |
| 1030 | 1 per month | 1 to 3 per month | no | final_label_repaired: 'unknown' -> '1 per month' |
| 1046 | unknown | 3 to 5 per month | no |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | yes |  |
| 1165 | 5 to 7 per 6 week | 5 to 7 per 3 week | yes | json_dialect_repaired: python_literal; final_label_repaired: 'unknown' -> '5 to 7 per 6 week'; evidence_not_exact_substring |
| 1171 | 2 to 3 per week | 7 to 9 per 3 week | yes |  |
| 1207 | 7 to 9 per week | 21 to 28 per 3 month | no |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | yes |  |
| 1281 | 5 to 7 per year | 5 to 7 per year | yes | final_label_repaired: 'unknown' -> '5 to 7 per year' |
| 1317 | multiple per day | unknown, multiple per cluster | yes |  |
| 1357 | 1 per day | 1 per day | yes |  |
| 1363 | 1 per day | 3 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 1413 | 9 per month | 9 per month | yes |  |
| 1454 | 7 per week | 7 per week | yes | json_dialect_repaired: python_literal |
| 1486 | 2 per month | 3 per month | yes | final_label_repaired: '3 per month' -> '2 per month' |
| 1573 | 11 per week | 11 per week | yes |  |
| 1591 | 5 per month | 11 per month | yes | final_label_repaired: '11 per month' -> '5 per month' |
| 1596 | 12 per week | 12 per week | yes |  |
| 1597 | 12 per month | 12 per month | yes |  |
| 1636 | 5 per month | 5 per month | yes |  |
| 1640 | 5 per week | 5 per week | yes |  |
| 1687 | multiple per day | multiple per week | yes | final_label_repaired: 'multiple per week' -> 'multiple per day'; evidence_not_exact_substring |
| 1694 | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | final_label_repaired: '3 per fortnight' -> '3 per 2 week' |
| 1695 | unknown | multiple per month | yes | evidence_not_exact_substring |
| 1706 | multiple cluster per month, multiple per cluster | multiple cluster per month, multiple per cluster | yes | final_label_repaired: 'multiple per day' -> 'multiple cluster per month, multiple per cluster' |
| 1707 | multiple per week | multiple per week | yes | final_label_repaired: 'multiple per day' -> 'multiple per week' |
| 1772 | 11 per 6 month | 11 per 6 month | yes | final_label_repaired: '2 to 3 per month' -> '11 per 6 month' |
| 1773 | 11 per 3 month | 11 per 3 month | yes | final_label_repaired: '11 per 3 months' -> '11 per 3 month' |
| 1790 | 8 per 4 month | 8 per 4 month | yes | final_label_repaired: '1.5 per month' -> '8 per 4 month' |
| 1794 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 per 2 months' -> '8 per 2 month' |
| 1866 | 8 per 2 month | 8 per 2 month | yes | final_label_repaired: '8 in 2 months' -> '8 per 2 month' |
| 1880 | multiple per week | 8 per 2 month | no | json_dialect_repaired: python_literal; evidence_not_exact_substring |
| 1887 | 4 per 3 month | 4 per 3 month | yes | final_label_repaired: '1 to 2 per month' -> '4 per 3 month' |
| 1914 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '7 in 3 months' -> '7 per 3 month' |
| 1922 | 7 per 3 month | 7 per 3 month | yes | final_label_repaired: '2 to 3 per month' -> '7 per 3 month' |
| 1923 | 7 per 6 month | 7 per 6 month | yes | final_label_repaired: '7 per 6 months' -> '7 per 6 month' |
| 1979 | 3 per 2 month | 6 per 2 month | yes | final_label_repaired: '3 per month' -> '3 per 2 month' |
| 1980 | 6 per 3 month | 6 per 3 month | yes | final_label_repaired: '2 per month' -> '6 per 3 month' |
| 2023 | 5 per month | 5 per month | yes |  |
| 2080 | multiple per day | multiple per month | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 2094 | multiple per month | multiple per month | yes | json_dialect_repaired: python_literal; final_label_repaired: 'multiple per day' -> 'multiple per month'; evidence_not_exact_substring |
| 2114 | multiple per day | multiple per month | yes | evidence_not_exact_substring |
| 2149 | unknown | unknown | yes | evidence_not_exact_substring |
| 2166 | multiple per day | unknown | yes | evidence_not_exact_substring |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | final_label_repaired: '3 to 5 per week' -> '3 to 5 per 2 week' |
| 2233 | 3 to 4 per month | 6 to 7 per 2 month | yes |  |
| 2245 | 2 to 3 per week | 7 to 8 per 3 week | yes |  |
| 2259 | 2 to 3 per month | 6 to 8 per 3 month | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | yes |  |
| 2366 | 2 to 4 per year | 2 to 4 per year | yes | final_label_repaired: 'unknown' -> '2 to 4 per year' |
| 2369 | 3 to 4 per month | 3 to 4 per month | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | yes |  |
| 2425 | 6 to 8 per month | 6 to 8 per month | yes | evidence_not_exact_substring |
| 2427 | 3 to 5 per month | 3 to 5 per month | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | final_label_repaired: '5 to 7 per 2 weeks' -> '5 to 7 per 2 week' |
| 2437 | 1 to 2 per month | 2 to 3 per 2 month | yes |  |
| 2440 | 2 to 3 per month | 5 to 7 per 2 month | yes |  |
| 2456 | 3 to 4 per week | 6 to 7 per 2 week | yes |  |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | final_label_repaired: '7 to 9 per 2 weeks' -> '7 to 9 per 2 week' |
| 2487 | 2 to 3 per month | 2 to 3 per 3 month | no |  |
| 2513 | 4 to 6 per week | 2 to 3 per 2 week | yes |  |
| 2541 | 4 to 5 per week | 8 to 9 per 2 week | yes |  |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | final_label_repaired: '5 to 6 per 2 months' -> '5 to 6 per 2 month' |
| 2554 |  | 1 to 10 per 2 month | no | invalid_json: Invalid control character at; evidence_not_exact_substring |
| 2558 |  | 3 to 4 per 2 month | no | invalid_json: Expecting ',' delimiter; evidence_not_exact_substring |
| 2609 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | 1 per day | 1 per day | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 2628 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2678 |  | 1 per day | no | invalid_json: Invalid control character at; evidence_not_exact_substring |
| 2681 | 1 per day | 1 per day | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: 'multiple per day' -> '1 per 2 day' |
| 2731 | 1 per 2 week | 1 per 2 week | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 | 1 per month | 1 per month | yes |  |
