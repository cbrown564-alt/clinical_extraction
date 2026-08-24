# Cell 2 uses the living extract plus suggested candidates

Date: 2026-08-23
Status: answered
Owner: this file

## Primary question

If both-extract (`exect_llm_pre_post`) starts from the living
`exect_llm_extract` prompt and only adds the rules-suggested
candidates, what is the Gemini select stop on 4-family micro F1?

## Why it matters

Cell 2 was the Compact filtered extract with suggested candidates.
Cells 3–5 already use the living extract. Both-extract should be
that same extract plus the candidate list.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Model | Gemini 3.7 Flash, living low |
| Method | `exect_llm_pre_post` |
| Prompt | `exect_llm_extract` plus suggested evidence |
| Select | inventory Select |
| Development | `dev140`, review permitted |
| Holdout | `test60`, aggregate only. Do not inspect rows. |
| Scorer | 4-family micro F1 (`clinical_inventory_unit_keys`) |
| Batches | `batch-1787519113-cqUTTcC7jIRcee44vuyR` (`dev140`); `batch-1787519464-Dh4Ndp9NpOsWLRIQvwUU` (`test60`) |

An earlier `--overwrite` resume reused Compact OpenRouter batches.
Those scores were discarded. `--overwrite` now drops `batch.json`
before submit.

## Answer

Gemini both-extract select is **0.8884** on `dev140` and
**0.8592** on `test60`. Stage stops: extract **0.8321 / 0.8319**,
encode **0.8754 / 0.8511**. Cell 3 remains the holdout peak
(**0.8674**). All five cited rows now use 4-family micro F1.

## Claim boundary

Aggregate-only `test60`. Do not inspect holdout rows. Other-model
`exect_llm_pre_post` cells remain historical Compact both-extract.
Not a six-model cell-2 roster.

## Next action

Write the five-cell table from the Gemini select stops. Do not
retune on `test60`.
