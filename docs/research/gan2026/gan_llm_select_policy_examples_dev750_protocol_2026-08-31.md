# Protocol: Policy-example LLM select on Gan `dev750`

Date: 2026-08-31
Status: complete
Owner: this file
Report: [result](gan_llm_select_policy_examples_dev750_2026-08-31.md)
Prior: [test450](gan_llm_select_policy_examples_test450_protocol_2026-08-31.md)
Guardrail: `gan2026-scoring-guardrail`

## Primary question

What is the Purist select-stop count when Gemini later-stage select
reads the saved codebook extract through the living policy-example
select prompt on `dev750`?

## Why this matters

Cited `test450` cell 5 is this prompt (383/450). Cited `dev750`
cell 5 was the earlier four-policy measurement (590/750). This run
measured the same living prompt on development and was then
promoted.

## Frozen candidate

- Find ledger: saved Gemini `gan_llm_extract` raw on `dev750`
- Select: living `build_llm_select_prompt_input` (same text as
  promoted `test450` cell 5)
- No later-stage encode call
- No hybrid rule post-stack
- After the call: join and projection only
- Model: Gemini 3.7 Flash
- Work cell:
  `experiments/paper/gan_llm_select_policy_examples/`
- Recorded prompt version: `gan_llm_select_policy_examples`
- Call transport: OpenRouter batch
- Do not write into cited `gan_llm_select_from_extract`

## Fixed comparators

| Cell | Purist |
| --- | ---: |
| Cited cell 5 (`gan_llm_select_from_extract`) | **590**/750 |
| Cited cell 3 (`llm_select_after_codebook`) | **656**/750 |
| Standalone rules | **691**/750 |

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `dev750` |
| Row policy | `development_review_permitted` |
| Scorer | Purist; secondary Pragmatic and scorable count |
| Public output | stop counts, rates, and flag-only changed-row totals versus cited cell 5 |

Row-level rescue or harm tables may use development letters. Do not
load `test450` for this protocol. Do not retune the prompt from this
run.

## Required analysis

Aggregate Purist / Pragmatic / scorable versus cited cell 5. Flag-only
rescue and harm counts versus the stored four-policy cell 5. Do not
promote. Do not refresh Table 1 from this cell.

## Stop rule

Stop after the isolated work cell is scored and the public artifact
is written. Promotion of cited `dev750` cell 5 is a separate
follow-on and is now complete.

## Claim boundary

Development measurement, then promotion, of the living select
prompt. Not holdout. Not a Table 1 change. Not hybrid select.
