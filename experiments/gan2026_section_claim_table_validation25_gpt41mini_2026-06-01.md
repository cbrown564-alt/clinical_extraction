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
- Git commit: `76f90fb`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_section_claim_table_validation25_gpt41mini_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 25 / 25
- Call failures: 0
- Parse/schema/label issues: 0
- Exact claim evidence substrings: 87 / 89
- Exact selected final evidence substrings: 23 / 25
- raw final-query score: Purist 0.4800 (12 / 25), Pragmatic 0.4800 (12 / 25)
- Strict-format score: Purist 0.8000 (20 / 25), Pragmatic 0.8000 (20 / 25)
- Frozen clean scorer-facing score: Purist 0.8800 (22 / 25), Pragmatic 0.9200 (23 / 25)
- Rows changed by downstream repair layers: 16

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 0 |
| claim_extraction | 2 |
| temporality_conflict | 0 |
| final_query | 2 |
| parse_schema | 0 |
| scorer_format | 12 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 10 |  | unparsable_label: ≤ four per day (Unparsable label (raw: '≤ four per day' / normalized: '≤ four per day')) |  |
| 40 |  | unparsable_label: ≤ 4 per week (Unparsable label (raw: '≤ 4 per week' / normalized: '≤ 4 per week')) |  |
| 79 |  | unparsable_label: ≤ 6 to 7 per year (Unparsable label (raw: '≤ 6 to 7 per year' / normalized: '≤ 6 to 7 per year')) |  |
| 103 | claim evidence not exact (c2: over the past year, however, the patient and family report that events have become markedly infrequent, such that the current pattern is ≤ two or four per year); selected evidence not exact (over the past year, however, the patient and family report that events have become markedly infrequent, such that the current pattern is ≤ two or four per year) | unparsable_label: ≤ 2 to 4 per year (Unparsable label (raw: '≤ 2 to 4 per year' / normalized: '≤ 2 to 4 per year')) |  |
| 182 |  | unparsable_label: 1 seizure every 2 days (Unparsable label (raw: '1 seizure every 2 days' / normalized: '1 seizure every 2 days')) |  |
| 187 |  | unparsable_label: 1 cluster per week (Unparsable cluster label: '1 cluster per week') |  |
| 190 |  | unparsable_label: 1 cluster per 4 weeks (Unparsable cluster label: '1 cluster per 4 weeks') |  |
| 243 | claim evidence not exact (c1: he and his partner report that the seizures occur every four months); selected evidence not exact (he and his partner report that the seizures occur every four months) |  |  |
| 338 |  | unparsable_label: many per month (Unparsable label (raw: 'many per month' / normalized: 'many per month')) |  |
| 409 |  | unparsable_label: ≤ once per month (Unparsable label (raw: '≤ once per month' / normalized: '≤ once per month')) |  |
| 446 |  | unparsable_label: ≤ 2 per week (Unparsable label (raw: '≤ 2 per week' / normalized: '≤ 2 per week')) |  |
| 531 |  | unparsable_label: 12 to 30 per quarter (Unparsable label (raw: '12 to 30 per quarter' / normalized: '12 to 30 per quarter')) |  |
| 598 |  | unparsable_label: 1 per eight months (Unparsable label (raw: '1 per eight months' / normalized: '1 per eight months')) |  |

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | ≤ four per day | 4 per day | 4 per day | 4 per day |  | yes | scorer_format |
| 40 | ≤ 4 per week | 4 per week | 4 per week | 4 per week |  | yes | scorer_format |
| 79 | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year |  | yes | scorer_format |
| 103 | ≤ 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year |  | yes | claim_extraction,final_query,scorer_format |
| 128 | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | 1 per 6 days | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | 1 per week | 1 per week | 1 per week | 1 per 7 day | yes | yes |  |
| 182 | 1 seizure every 2 days | 1 1 per 2 day | 1 1 per 2 day | 1 per 2 day |  |  | scorer_format |
| 187 | 1 cluster per week | 1 cluster per week | 1 per week | 1 per 7 to 9 day |  | no | scorer_format |
| 190 | 1 cluster per 4 weeks | 1 cluster per 4 week | 1 per 4 week | 1 per 4 week |  | yes | scorer_format |
| 198 | 1 per month | 1 per month | 1 per month | 1 per 4 week | yes | yes |  |
| 212 | 1 per month | 1 per month | 1 per month | 1 per 3 to 4 week | no | no |  |
| 218 | 1 per 3 weeks | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | 1 per 4 months | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes | claim_extraction,final_query |
| 278 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | many per month | many per month | multiple per month | multiple per month |  | yes | scorer_format |
| 409 | ≤ once per month | 1 per month | 1 per month | 1 per month |  | yes | scorer_format |
| 419 | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | ≤ 2 per week | 2 per week | 2 per week | 2 per week |  | yes | scorer_format |
| 466 | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month |  | yes | scorer_format |
| 598 | 1 per eight months | 1 per 8 month | 1 per 8 month | 1 per 8 month |  | yes | scorer_format |
| 659 | 2 per 4 days | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
