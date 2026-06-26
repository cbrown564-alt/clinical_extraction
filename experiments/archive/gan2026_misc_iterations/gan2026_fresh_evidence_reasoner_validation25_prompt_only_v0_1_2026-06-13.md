# Gan 2026 Fresh-Evidence Reasoner

Date: 2026-06-13

This is a validation-development V12 fresh-evidence reasoning artifact.
The model may replace the GPT structured-event final only from exact raw-note evidence.

## Experiment Unit

- Work class: V12 fresh-evidence reasoner over saved structured events.
- Rows: 25
- Split: `validation`, manifest `gan2026_split_v1`.
- Mode: `prompt-only`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_1`
- JSONL artifact: `experiments\gan2026_fresh_evidence_reasoner_validation25_prompt_only_v0_1_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 0
- Model calls attempted: 0
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 0
- Evidence-gate fallbacks: 0
- Exact evidence substrings: 0
- V0 Purist: 25/25
- Raw model Purist: 0/25
- Final Purist: 0/25
- Net Purist gain vs V0: 0
- Changed-label precision vs V0: None
- Actions: `{}`
- Profiles: `{}`

## Gate

- Status: `prompt_only_no_prediction`
- Interpretation: Prompt-only scaffold generated without model calls; run live validation25 before applying contract promotion gates.

## Claim Boundary

validation-development V12 fresh-evidence reasoner; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Action | Profiles | V0 | Raw | Final | Transition | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | `None` | `None` | `4 per day` | `None` | `None` | `unscored` | no | not_run |
| 40 | `None` | `None` | `4 per week` | `None` | `None` | `unscored` | no | not_run |
| 79 | `None` | `None` | `6 to 7 per year` | `None` | `None` | `unscored` | no | not_run |
| 103 | `None` | `None` | `2 to 4 per year` | `None` | `None` | `unscored` | no | not_run |
| 128 | `None` | `None` | `17 per month` | `None` | `None` | `unscored` | no | not_run |
| 156 | `None` | `None` | `1 per 6 day` | `None` | `None` | `unscored` | no | not_run |
| 180 | `None` | `None` | `1 per 7 day` | `None` | `None` | `unscored` | no | not_run |
| 182 | `None` | `None` | `1 per 2 day` | `None` | `None` | `unscored` | no | not_run |
| 187 | `None` | `None` | `1 per 7 to 9 day` | `None` | `None` | `unscored` | no | not_run |
| 190 | `None` | `None` | `1 per 4 week` | `None` | `None` | `unscored` | no | not_run |
| 198 | `None` | `None` | `1 per 4 week` | `None` | `None` | `unscored` | no | not_run |
| 212 | `None` | `None` | `2 to 3 per month` | `None` | `None` | `unscored` | no | not_run |
| 218 | `None` | `None` | `1 per 3 week` | `None` | `None` | `unscored` | no | not_run |
| 243 | `None` | `None` | `1 per 4 month` | `None` | `None` | `unscored` | no | not_run |
| 278 | `None` | `None` | `multiple per week` | `None` | `None` | `unscored` | no | not_run |
| 280 | `None` | `None` | `multiple per day` | `None` | `None` | `unscored` | no | not_run |
| 338 | `None` | `None` | `multiple per month` | `None` | `None` | `unscored` | no | not_run |
| 409 | `None` | `None` | `1 per month` | `None` | `None` | `unscored` | no | not_run |
| 419 | `None` | `None` | `2 per year` | `None` | `None` | `unscored` | no | not_run |
| 446 | `None` | `None` | `15 per 3 month` | `None` | `None` | `unscored` | no | not_run |
| 466 | `None` | `None` | `21 to 28 per month` | `None` | `None` | `unscored` | no | not_run |
| 467 | `None` | `None` | `9 per month` | `None` | `None` | `unscored` | no | not_run |
| 531 | `None` | `None` | `12 to 30 per 3 month` | `None` | `None` | `unscored` | no | not_run |
| 598 | `None` | `None` | `1 per 8 month` | `None` | `None` | `unscored` | no | not_run |
| 659 | `None` | `None` | `2 per 4 day` | `None` | `None` | `unscored` | no | not_run |
