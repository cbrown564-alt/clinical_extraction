# Gan five-cell prefix grid protocol

Date: 2026-08-22
Status: completed 2026-08-22; cited in claims
Result: [five-cell grid](gan_five_cell_grid_2026-08-22.md)
Owner: this file

## Question

What is the `dev750` score for cell 4 — codebook extract as encode,
then rule select without rule encode — and what are the locked
`test450` aggregates for cells 2, 4, and 5?

## Why it matters

The Gemini row is now a prefix chain from all-rules to all-LLM.
Cell 4 is the missing step: the model already wrote the form, and
only select rules run.

## Cells

| # | Extract | Encode | Select |
| --- | --- | --- | --- |
| 1 | Rules | Rules | Rules |
| 2 | Rules then LLM | Rules | Rules |
| 3 | LLM | Rules | Rules |
| 4 | LLM | LLM (= extract) | Rules, no encode repair |
| 5 | LLM | LLM (= extract) | LLM |

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Development | `dev750` review permitted |
| Holdout | `test450` aggregate only. No row inspection. |
| Model | Gemini 3.7 Flash |
| Extract | `gan_llm_extract` |
| Cell 2 extract | `gan_llm_and_rules_extract` |
| Cell 4 repair | new `llm_select_only` (select families on, encode off) |
| Scorer | Purist |

## Stop rule

Stop after `dev750` cell 4 and holdout aggregates for 2, 4, and 5.
Reuse the frozen extract holdout cell. Do not retune `label_forms`.
Do not promote `claims.md`.

## Claim boundary

Development plus frozen holdout aggregates. Not a paper column
until promoted.
