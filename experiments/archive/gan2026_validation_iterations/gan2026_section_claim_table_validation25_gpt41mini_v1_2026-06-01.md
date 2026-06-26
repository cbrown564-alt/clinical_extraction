# Gan 2026 Section Claim Table V1

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Pipeline: `gan2026_section_claim_table_v1`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first claim extractor and final query selector
- Prompt/program version: `gan2026_section_claim_table_v1`
- Temperature: `0.0`
- Max tokens: `1400`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `7db354c`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_section_claim_table_validation25_gpt41mini_v1_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 25 / 25
- Call failures: 0
- Parse/schema/label issues: 0
- Exact claim evidence substrings: 71 / 72
- Exact selected final evidence substrings: 25 / 25
- raw final-query score: Purist 0.9600 (24 / 25), Pragmatic 0.9600 (24 / 25)
- Strict-format score: Purist 0.9600 (24 / 25), Pragmatic 0.9600 (24 / 25)
- Frozen clean scorer-facing score: Purist 0.9600 (24 / 25), Pragmatic 0.9600 (24 / 25)
- Rows changed by downstream repair layers: 1

## Interpretation

This v1 smoke passes the prompt/schema gate for a 50-row validation comparison.
The main v0 failure family improved: raw final labels were scorable on 25/25
rows, with no raw-to-clean metric gain. Selected final evidence was exact on
25/25 rows. The remaining score miss is row 187, where the model became too
conservative about a cluster-cadence statement and answered `unknown` instead of
preserving `1 per 7 to 9 day`. Watch for this cluster-cadence conservatism in
the 50-row comparison before any 250-row escalation.

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 0 |
| claim_extraction | 1 |
| temporality_conflict | 0 |
| final_query | 0 |
| parse_schema | 0 |
| scorer_format | 0 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 182 | claim evidence not exact (c2: No use of rescue medication since the last appointment) |  |  |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 6 to 7 per year | yes | yes |  |
| 103 | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 128 | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes | claim_extraction |
| 187 | unknown | unknown | unknown | 1 per 7 to 9 day | no | no |  |
| 190 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 278 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 409 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | 2 per 12 month | 2 per 12 month | 2 per 12 month | 2 per year | yes | yes |  |
| 446 | 2 per 1 week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | 1 per 8 month | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | 2 per 4 day | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
