# Gan 2026 LLM-First Validation Run

Date: 2026-05-31

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-first direct extraction runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first note-to-label extractor
- Prompt/program version: `gan2026_llm_first_direct_extractor_v0.1`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only repairs labels, validates evidence, and scores.
- Git commit: `e48945e`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.jsonl`

## Summary

- Decision records: 90 / 250
- Call failures: 0
- Parse/schema/label issues: 160
- Deterministic repair notes: 41
- Exact evidence substrings: 86 / 250
- Purist validation accuracy/micro F1 proxy: 0.3080 (77 / 250)
- Pragmatic validation accuracy/micro F1 proxy: 0.3120 (78 / 250)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 |  | 4 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 40 |  | 4 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 79 |  | 6 to 7 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 103 |  | 2 to 4 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 128 |  | 17 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 156 |  | 1 per 6 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 180 |  | 1 per 7 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 182 |  | 1 per 2 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 187 |  | 1 per 7 to 9 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 190 | 1 per 4 week | 1 per 4 week | yes | final_label_repaired: '1 cluster per 4 weeks' -> '1 per 4 week' |
| 198 |  | 1 per 4 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 212 |  | 1 per 3 to 4 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 218 |  | 1 per 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 243 |  | 1 per 4 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 |  | multiple per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 409 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 419 | 2 per year | 2 per year | yes |  |
| 446 |  | 2 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 466 |  | 21 to 28 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 467 |  | 9 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 531 |  | 12 to 30 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per eight months' -> '1 per 8 month' |
| 659 |  | 2 per 4 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 665 |  | 2 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 678 |  | 2 per 4 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 694 | 1 per week | 1 per week | yes |  |
| 704 | 2 per month | 2 per month | yes |  |
| 725 |  | 1 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 731 |  | 1 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 743 | multiple per week | multiple per week | yes |  |
| 744 | multiple per week | multiple per week | yes |  |
| 763 | 1 per week | 1 per week | yes |  |
| 790 |  | 1 per 7 to 10 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 816 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 849 | 1 per year | 1 per year | yes |  |
| 854 | 1 per year | 1 per year | yes |  |
| 869 |  | multiple per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 891 |  | 1 per 2 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 899 |  | 1 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 959 | 2 per month | 1 per 2 month | no |  |
| 960 | 2 per month | 1 per 2 month | no |  |
| 978 |  | 1 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 987 | 2 per month | 1 per 2 month | no |  |
| 1030 |  | 1 to 3 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1046 |  | 3 to 5 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1070 |  | 3 to 4 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1094 |  | 3 to 5 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1165 |  | 5 to 7 per 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1171 |  | 7 to 9 per 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1207 |  | 21 to 28 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1223 |  | 3 to 4 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1249 |  | 2 to 4 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1281 |  | 5 to 7 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1317 |  | unknown, multiple per cluster | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1357 |  | 1 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1363 |  | 3 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1413 |  | 9 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1454 |  | 7 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1486 |  | 3 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1573 |  | 11 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1591 |  | 11 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1596 |  | 12 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1597 |  | 12 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1636 |  | 5 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1640 |  | 5 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1687 |  | multiple per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1694 |  | 1 cluster per 2 week, 3 per cluster | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1695 |  | multiple per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1706 | unknown | multiple cluster per month, multiple per cluster | no | final_label_repaired: 'cluster of short events on multiple days' -> 'unknown' |
| 1707 |  | multiple per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1772 |  | 11 per 6 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1773 |  | 11 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1790 |  | 8 per 4 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1794 |  | 8 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1866 |  | 8 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1880 |  | 8 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1887 |  | 4 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1914 |  | 7 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1922 |  | 7 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1923 |  | 7 per 6 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1979 |  | 6 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 1980 |  | 6 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2023 |  | 5 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2080 |  | multiple per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2094 | multiple per month | multiple per month | yes | final_label_repaired: 'several per month' -> 'multiple per month' |
| 2114 |  | multiple per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2149 | no seizure frequency reference | unknown | yes | final_label_repaired: 'occasional tonic-clonic over last year' -> 'no seizure frequency reference' |
| 2166 | no seizure frequency reference | unknown | yes | final_label_repaired: 'frequent' -> 'no seizure frequency reference' |
| 2228 |  | 3 to 5 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2233 |  | 6 to 7 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2245 |  | 7 to 8 per 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2259 |  | 6 to 8 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2354 |  | 6 to 7 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2366 |  | 2 to 4 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2369 |  | 3 to 4 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2374 |  | 7 to 9 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2425 |  | 6 to 8 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2427 |  | 3 to 5 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2435 |  | 5 to 7 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2437 |  | 2 to 3 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2440 |  | 5 to 7 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2456 |  | 6 to 7 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2459 |  | 7 to 9 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2487 |  | 2 to 3 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2513 |  | 2 to 3 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2541 |  | 8 to 9 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2548 |  | 5 to 6 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2554 |  | 1 to 10 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2558 |  | 3 to 4 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2609 | 1 per day | 1 per day | yes | final_label_repaired: '1 per night' -> '1 per day' |
| 2622 | no seizure frequency reference | 1 per day | no | final_label_repaired: 'every night' -> 'no seizure frequency reference' |
| 2628 | multiple per day | 1 per day | no |  |
| 2678 | multiple per day | 1 per day | no |  |
| 2681 |  | 1 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2698 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 2731 |  | 1 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2740 | 1 per month | 1 per month | yes |  |
| 2748 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2759 | 1 per month | 1 per month | yes |  |
| 2762 | 1 per month | 1 per month | yes |  |
| 2765 | 1 per month | 1 per month | yes |  |
| 2776 | 1 per week | 1 per week | yes |  |
| 2789 |  | 1 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2812 |  | 1 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2822 | multiple per day | 1 per day | no |  |
| 2824 |  | 1 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2877 |  | 2 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2887 |  | 2 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2907 | seizure free for multiple year | seizure free for 6 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 2932 |  | seizure free for 9 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2938 | seizure free for multiple year | seizure free for 8 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 2965 |  | seizure free for 16 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 2992 | seizure free for multiple year | seizure free for 7 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year'; evidence_not_exact_substring |
| 3015 | seizure free for multiple year | seizure free for 12 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3048 | seizure free for 16 month | seizure free for 16 month | yes |  |
| 3058 | seizure free for multiple year | seizure free for 12 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3082 |  | seizure free for 10 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3095 | seizure free for multiple year | seizure free for 12 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3113 | seizure free for multiple year | seizure free for 14 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3118 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3137 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3224 |  | 1 cluster per month, 6 to 7 per cluster | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3242 |  | 2 cluster per month, 5 per cluster | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3261 |  | 2 cluster per month, 4 per cluster | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3262 |  | 2 cluster per month, 5 per cluster | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3281 |  | 8 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3297 |  | 6 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3325 |  | 3 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3356 |  | unknown | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3371 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3436 | unknown | unknown | yes |  |
| 3468 | seizure free for multiple year | unknown | no | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 3469 | multiple per month | unknown | yes |  |
| 3482 |  | unknown | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3493 | unknown | unknown | yes |  |
| 3507 | unknown | unknown | yes |  |
| 3512 |  | unknown | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3528 | multiple per day | unknown | yes |  |
| 3532 |  | unknown | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3534 | seizure free for 7 month | unknown | no |  |
| 3600 | unknown | unknown | yes |  |
| 3623 | multiple per week | 7 per week | no |  |
| 3643 |  | 7 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3681 |  | 9 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3682 |  | 6 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3710 |  | 5 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3753 |  | 1 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3766 |  | 8 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3774 |  | 9 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3791 |  | 10 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3801 |  | 9 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3806 |  | 6 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3827 |  | 7 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3846 | 2 per day | 2 per day | yes |  |
| 3849 | 3 per day | 3 per day | yes |  |
| 3889 | 8 per year | 8 per year | yes |  |
| 3892 |  | 3 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 3940 | 4 per week | 4 per week | yes |  |
| 3949 | 4 per week | 4 per week | yes |  |
| 3988 | multiple per week | multiple per week | yes | final_label_repaired: 'several times per week' -> 'multiple per week' |
| 3995 | 1 per month | 1 per month | yes | final_label_repaired: 'abs monthly' -> '1 per month' |
| 3999 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4022 |  | 8 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4026 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4092 | 2 to 3 per week | 1 per 2 to 3 week | no |  |
| 4100 |  | 1 per 2 to 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4110 |  | 1 per 1 to 2 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4116 |  | 1 per 1 to 2 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4173 |  | 1 per 2 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4243 |  | 1 per 2 to 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4258 |  | 4 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4337 |  | 3 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4345 |  | 4 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4368 |  | 5 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4402 |  | 7 per 7 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4410 |  | 4 per 7 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4478 |  | 19 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4480 |  | 3 to 5 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4496 |  | 7 to 8 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4562 |  | 1 per 6 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4563 |  | 1 per 4 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4574 |  | 1 per 4 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4592 |  | 1 per 2 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4597 |  | 1 per 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4624 |  | 1 per 3 to 4 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4631 | 2 to 3 per month | 1 per 14 to 21 day | yes |  |
| 4690 |  | multiple per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4694 |  | multiple per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4700 |  | multiple per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4709 | unknown | multiple per day | yes | evidence_not_exact_substring |
| 4731 | no seizure frequency reference | unknown | yes | final_label_repaired: 'rare' -> 'no seizure frequency reference' |
| 4732 | unknown | unknown | yes |  |
| 4771 |  | unknown | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4839 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4842 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4910 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4919 | seizure free for 2 year | seizure free for 2 year | yes |  |
| 4926 | seizure free for multiple year | seizure free for 1 year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4951 |  | seizure free for multiple month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 4956 | seizure free for 7 month | seizure free for 7 month | yes |  |
| 4992 | seizure free for multiple year | seizure free for 11 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 4994 |  | seizure free for 6 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 5040 | seizure free for 6 month | seizure free for 6 months | yes |  |
| 5082 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5092 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5110 | seizure free for 3 month | seizure free for multiple month | yes |  |
| 5121 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5136 | seizure free for 3 month | seizure free for multiple month | yes | evidence_not_exact_substring |
| 5141 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5197 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5210 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5221 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5248 | seizure free for multiple year | seizure free for multiple year | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5331 | seizure free for 12 month | seizure free for 12 month | yes |  |
| 5345 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5351 | seizure free for multiple year | seizure free for 18 month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5379 | seizure free for multiple year | seizure free for multiple month | yes | final_label_repaired: 'seizure free for multiple month' -> 'seizure free for multiple year' |
| 5406 |  | seizure free for multiple month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 5476 | no seizure frequency reference | unknown | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 5490 | unknown | unknown | yes | evidence_not_exact_substring |
| 5491 |  | unknown | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 5504 | unknown | unknown | yes |  |
| 5507 |  | unknown | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 5528 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 5534 |  | 1 per multiple month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 5551 | multiple per day | multiple per day | yes |  |
| 5567 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 5584 | multiple per week | multiple per week | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
