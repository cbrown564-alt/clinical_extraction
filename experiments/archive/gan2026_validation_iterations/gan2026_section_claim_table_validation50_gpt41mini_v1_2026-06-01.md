# Gan 2026 Section Claim Table V1

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 50 rows.
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
- Reused raw model outputs: `25`
- Reuse source: `experiments/gan2026_section_claim_table_validation25_gpt41mini_v1_2026-06-01.jsonl`
- Optimizer: none
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `7db354c`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_section_claim_table_validation50_gpt41mini_v1_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 50 / 50
- Call failures: 0
- Parse/schema/label issues: 0
- Exact claim evidence substrings: 151 / 153
- Exact selected final evidence substrings: 50 / 50
- raw final-query score: Purist 0.9400 (47 / 50), Pragmatic 0.9400 (47 / 50)
- Strict-format score: Purist 0.9400 (47 / 50), Pragmatic 0.9400 (47 / 50)
- Frozen clean scorer-facing score: Purist 0.9400 (47 / 50), Pragmatic 0.9400 (47 / 50)
- Rows changed by downstream repair layers: 2

## Interpretation

`gan2026_section_claim_table_v1` fixed the main v0 raw-label failure family:
all 50 raw final labels were scorable, and raw/strict/clean scores were
identical. Evidence behavior was also reviewable, with exact selected final
evidence on 50/50 rows.

Do not escalate this artifact to 250 rows yet. The three Purist misses are
localized final-query behaviors that should be addressed in a small prompt/schema
revision first:

- Row 187: cluster-cadence evidence was treated as `unknown` instead of the
  ordinary frequency label `1 per 7 to 9 day`.
- Row 704: `twice a month` was incorrectly converted to `2 per 2 month` instead
  of `2 per month`.
- Row 1165: `5 or 7 focal onset seizures in three weeks` was softened to
  `multiple per 3 week` instead of preserving `5 to 7 per 3 week`.

The next comparison should be a v2 prompt/schema smoke focused on these
final-query conversions before any 250-row escalation decision.

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 0 |
| claim_extraction | 2 |
| temporality_conflict | 0 |
| final_query | 0 |
| parse_schema | 0 |
| scorer_format | 0 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 182 | claim evidence not exact (c2: No use of rescue medication since the last appointment) |  |  |
| 891 | claim evidence not exact (c4: No witnessed generalised tonic–clonic seizures) |  |  |

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
| 665 | 2 per 2 week | 2 per 2 week | 2 per 2 week | 2 per 2 week | yes | yes |  |
| 678 | 2 per 4 month | 2 per 4 month | 2 per 4 month | 2 per 4 month | yes | yes |  |
| 694 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | 2 per 2 month | 2 per 2 month | 2 per 2 month | 2 per month | no | no |  |
| 725 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 744 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 763 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | 1 per 12 month | 1 per 12 month | 1 per 12 month | 1 per year | yes | yes |  |
| 854 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes | claim_extraction |
| 899 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | 1 to 3 per 1 month | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | multiple per 3 week | multiple per 3 week | multiple per 3 week | 5 to 7 per 3 week | no | no |  |
