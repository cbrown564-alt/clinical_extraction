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
- Git commit: `e48945e`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_first_validation25_gpt41mini_v02_2026-05-31.jsonl`

## Summary

- Decision records: 24 / 25
- Call failures: 0
- Parse/schema/label issues: 7
- Exact evidence substrings: 23 / 25
- Purist validation accuracy/micro F1 proxy: 0.6800 (17 / 25)
- Pragmatic validation accuracy/micro F1 proxy: 0.7200 (18 / 25)

## Rows

| Row | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- |
| 10 | multiple per day | 4 per day | no |  |
| 40 | multiple per week | 4 per week | no | final_label_repaired: '≤ four per week' -> 'multiple per week' |
| 79 | 2 to 3 per month | 6 to 7 per year | no |  |
| 103 | 2 to 4 per year | 2 to 4 per year | yes |  |
| 128 | 2 to 3 per week | 17 per month | yes |  |
| 156 | 1 per week | 1 per 6 day | yes |  |
| 180 | 1 per week | 1 per 7 day | yes |  |
| 182 | 1 per 2 day | 1 per 2 day | yes | final_label_repaired: '1 every 2 days' -> '1 per 2 day' |
| 187 | unknown | 1 per 7 to 9 day | no | final_label_repaired: '1 cluster per week' -> 'unknown' |
| 190 | unknown | 1 per 4 week | no | final_label_repaired: '1 cluster per 4 weeks' -> 'unknown' |
| 198 | 1 per month | 1 per 4 week | yes |  |
| 212 | 2 to 3 per month | 1 per 3 to 4 week | yes |  |
| 218 | 2 to 3 per month | 1 per 3 week | yes |  |
| 243 | 2 to 3 per year | 1 per 4 month | yes | evidence_not_exact_substring |
| 278 | multiple per week | multiple per week | yes |  |
| 280 | multiple per day | multiple per day | yes |  |
| 338 | multiple per month | multiple per month | yes |  |
| 409 | multiple per month | 1 per month | no | final_label_repaired: '≤ once per month' -> 'multiple per month' |
| 419 | 2 per year | 2 per year | yes |  |
| 446 | 2 per week | 2 per week | yes |  |
| 466 | 2 to 3 per week | 21 to 28 per month | yes |  |
| 467 | 2 to 3 per week | 9 per month | yes |  |
| 531 | 2 to 3 per month | 12 to 30 per 3 month | no |  |
| 598 | 1 per 8 month | 1 per 8 month | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 |  | 2 per 4 day | no | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; evidence_not_exact_substring |
