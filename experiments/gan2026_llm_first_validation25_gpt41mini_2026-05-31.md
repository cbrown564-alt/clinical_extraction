# Gan 2026 LLM-First Validation Run

Date: 2026-05-31

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan seizure-frequency interpretation, while deterministic code is limited to label repair, evidence validation, and scoring.

Minimal change: add an LLM-first direct extraction runner. No deterministic V1 candidate diagnostics are provided to the model.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
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
- Git commit: `1c55aa5`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_first_validation25_gpt41mini_2026-05-31.jsonl`

## Summary

- Decision records: 3 / 25
- Call failures: 0
- Parse/schema/label issues: 24
- Exact evidence substrings: 3 / 25
- Purist validation accuracy/micro F1 proxy: 0.0400 (1 / 25)
- Pragmatic validation accuracy/micro F1 proxy: 0.0400 (1 / 25)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 |  | 4 per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 40 | multiple per week | 4 per week | no | final_label_repaired: '≤ four per week' -> 'multiple per week' |
| 79 |  | 6 to 7 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 103 |  | 2 to 4 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 128 |  | 17 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 156 |  | 1 per 6 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 180 |  | 1 per 7 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 182 | 1 per month | 1 per 2 day | no | final_label_repaired: '1 every 2 days' -> '1 per month' |
| 187 |  | 1 per 7 to 9 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 190 |  | 1 per 4 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 198 |  | 1 per 4 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 212 | 2 to 3 per month | 1 per 3 to 4 week | yes |  |
| 218 |  | 1 per 3 week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 243 |  | 1 per 4 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 278 |  | multiple per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 280 |  | multiple per day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 338 |  | multiple per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 409 |  | 1 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 419 |  | 2 per year | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 446 |  | 2 per week | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 466 |  | 21 to 28 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 467 |  | 9 per month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 531 |  | 12 to 30 per 3 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 598 |  | 1 per 8 month | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
| 659 |  | 2 per 4 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
