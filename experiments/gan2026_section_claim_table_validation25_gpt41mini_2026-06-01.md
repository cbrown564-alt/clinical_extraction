# Gan 2026 Section Claim Table V0

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Pipeline: `gan2026_section_claim_table_v0`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first claim extractor and final query selector
- Prompt/program version: `gan2026_section_claim_table_v0`
- Temperature: `0.0`
- Max tokens: `1400`
- Mode: `prompt-only`
- DSPy cache enabled: `True`
- Reused raw model outputs: `25`
- Reuse source: `experiments/gan2026_section_claim_table_validation25_gpt41mini_2026-06-01.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `fd4262e`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_section_claim_table_validation25_gpt41mini_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 21 / 25
- Call failures: 0
- Parse/schema/label issues: 4
- Exact claim evidence substrings: 73 / 75
- Exact selected final evidence substrings: 19 / 25
- raw final-query score: Purist 0.3600 (9 / 25), Pragmatic 0.3600 (9 / 25)
- Strict-format score: Purist 0.6400 (16 / 25), Pragmatic 0.6400 (16 / 25)
- Frozen clean scorer-facing score: Purist 0.7200 (18 / 25), Pragmatic 0.7600 (19 / 25)
- Rows changed by downstream repair layers: 13

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 0 |
| claim_extraction | 6 |
| temporality_conflict | 0 |
| final_query | 6 |
| parse_schema | 4 |
| scorer_format | 15 |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | ≤ four per day | 4 per day | 4 per day | 4 per day |  | yes | scorer_format |
| 40 | ≤ 4 per week | 4 per week | 4 per week | 4 per week |  | yes | scorer_format |
| 79 | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year |  | yes | scorer_format |
| 103 | ≤ 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year |  | yes | claim_extraction,final_query,scorer_format |
| 128 | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | None | None | None | 1 per 6 day |  |  | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event'; claim_extraction,final_query,parse_schema,scorer_format |
| 180 | None | None | None | 1 per 7 day |  |  | schema_validation_error: Input should be 'frequency', 'cluster_frequency', 'seizure_free', 'last_event_only', 'unknown_frequency', 'no_reference' or 'non_seizure_event'; claim_extraction,final_query,parse_schema,scorer_format |
| 182 | 1 seizure every 2 days | 1 1 per 2 day | 1 1 per 2 day | 1 per 2 day |  |  | scorer_format |
| 187 | 1 cluster per week | 1 cluster per week | 1 per week | 1 per 7 to 9 day |  | no | scorer_format |
| 190 | 1 cluster per 4 weeks | 1 cluster per 4 week | 1 per 4 week | 1 per 4 week |  | yes | scorer_format |
| 198 | 1 per month | 1 per month | 1 per month | 1 per 4 week | yes | yes |  |
| 212 | 1 per month | 1 per month | 1 per month | 1 per 3 to 4 week | no | no |  |
| 218 | None | None | None | 1 per 3 week |  |  | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; claim_extraction,final_query,parse_schema,scorer_format |
| 243 | 1 per 4 months | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes | claim_extraction,final_query |
| 278 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | many per month | many per month | multiple per month | multiple per month |  | yes | scorer_format |
| 409 | None | None | None | 1 per month |  |  | schema_validation_error: Input should be 'current', 'recent', 'historical', 'future' or 'unclear'; claim_extraction,final_query,parse_schema,scorer_format |
| 419 | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | ≤ 2 per week | 2 per week | 2 per week | 2 per week |  | yes | scorer_format |
| 466 | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month |  | yes | scorer_format |
| 598 | 1 per eight months | 1 per 8 month | 1 per 8 month | 1 per 8 month |  | yes | scorer_format |
| 659 | 2 per 4 days | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
