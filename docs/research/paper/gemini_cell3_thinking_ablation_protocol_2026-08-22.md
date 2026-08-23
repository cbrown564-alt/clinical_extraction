# Gemini cell-3 thinking ablation protocol

Date: 2026-08-22
Status: development extracts complete; holdout not started
Owner: this file
Related: [methods](../../paper/methods.md),
[six-model roster](../../paper/decisions/six-model-roster.md)

## Question

Does raising Gemini thinking from the living low setting to medium,
then high, change cell-3 extract on either task, once the output
budget is large enough for the extra thinking?

## Why it matters

Headline cells already use Gemini low. Thinking can change extract
only. Medium and high stay under `experiments/paper/` and are not a
results column.

## Data and inspection

| Item | Value |
| --- | --- |
| Tasks | Gan `gan_llm_extract_label_forms`; ExECT `exect_llm_only` |
| Splits | Development first (`dev750`, `dev140`). Holdout later, aggregate-only. |
| Model | Gemini 3.7 Flash |
| Comparator | Living low cells (5000 Gan / 16000 ExECT tokens) |
| Medium budget | 2x low (10000 Gan / 32000 ExECT) |
| High budget | same as medium (OpenRouter batch estimate rejected 5x) |
| Work cells | `experiments/paper/{method}/gemini37flash/reasoning_{effort}/{split}/` |

Do not run thinking on later-stage encode or select. Do not overlap
`OPENROUTER_API_KEY`. Do not inspect `test450` or `test60` rows.

## Stop rule

Run medium on both development extracts, then high. Stop after each
effort writes `comparison.json`. Do not retune from the misses.

## Claim boundary

Diagnostic ablation on development extracts. Not a roster row. Not a
headline replacement.
