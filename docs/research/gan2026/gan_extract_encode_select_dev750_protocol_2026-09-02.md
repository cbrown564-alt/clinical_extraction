# Protocol: One-call find, encode, and select on Gan `dev750`

Date: 2026-09-02
Status: complete
Owner: this file
Report: [aggregates](gan_extract_encode_select_dev750_2026-09-02.md)
Guardrail: `gan2026-scoring-guardrail`
Related: [holdout encode-then-select protocol](gan_encode_then_select_living_prompt_test450_protocol_2026-09-02.md),
[policy-example select on `dev750`](gan_llm_select_policy_examples_dev750_protocol_2026-08-31.md)

## Primary question

On permitted `dev750`, what is the Purist stop when Gemini does
codebook find, encode, and living-prompt select in one request?

## Why this matters

The same frozen prompt on locked `test450` scored **392**/450
Purist (0.87), above cited cell 5 (0.85) and at cited cell 3
(0.86). That holdout number is aggregate-only. It does not
authorize retuning. It does require the matching development
measurement before any paper language.

## Frozen candidate

One isolated Gemini 3.7 Flash live cell. Temperature 0. Living
low thinking. Method `gan_llm_extract_encode_select`. Same prompt
as the `test450` one-call cell. Score the extract stop only
(`raw_model`). No rule select after. No hybrid post-stack.

Work leaf: `experiments/paper/gan_llm_extract_encode_select/gemini37flash/dev750/`.
Do not overwrite `paper_experiments/`. Do not overwrite the
`test450` scratch cell.

Call transport: OpenRouter batch.

## Fixed comparators

| Cell | Purist |
| --- | ---: |
| Codebook extract (`gan_llm_extract`) | **585**/750 (0.78) |
| Cited cell 5 (select from extract, living prompt) | **640**/750 (0.85) |
| Cited cell 3 (rule encode + rule select) | **656**/750 (0.87) |
| Same prompt on `test450` (aggregate only) | **392**/450 (0.87) |

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `dev750` (`gan2026_split_v1` validation) |
| Row policy | `development_review_permitted` |
| Scorer | Purist; secondary Pragmatic, scorable, parse, call failures |
| Public output | stop counts, rates, and permitted row examples |

Do not inspect `test450` rows. Do not change the prompt from the
holdout result.

## Required analysis

Aggregate Purist / Pragmatic / scorable / parse / call failures.
Compare to codebook extract 585, cell 5 640, and cell 3 656.
If the score moves those interpretation lines, inspect permitted
rescue and harm versus extract and versus cell 5. Do not promote.
Do not refresh Table 1.

## Stop rule

Stop after the `dev750` work cell is scored and the public
artifact is written. A lower development score than holdout is a
valid negative result, not a reason to edit the prompt.

## Claim boundary

Development measurement of the frozen one-call prompt. Ablation,
not Table 1. Not a holdout claim. Not cell 5.
