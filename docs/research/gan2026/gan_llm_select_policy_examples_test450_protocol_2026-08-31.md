# Protocol: Policy-example LLM select on Gan `test450`

Date: 2026-08-31
Status: complete
Owner: this file
Report: [result](gan_llm_select_policy_examples_test450_2026-08-31.md)
Guardrail: `gan2026-scoring-guardrail`;
[holdout is aggregate-only](../../paper/decisions/holdout-is-aggregate-only.md)

## Primary question

What is the Purist select-stop count when Gemini later-stage select
reads the saved codebook extract through the living policy-example
select prompt?

## Why this matters

Cited cell 5 used a four-policy select prompt (357/450). The living
prompt now states the same current-state policies as living rule
select, with ledger-shaped examples. This run measures that prompt
on the sealed holdout. After the measurement, the result was
promoted as cited cell 5.

## Frozen candidate

- Find ledger: saved Gemini `gan_llm_extract` raw on `test450`
- Select: living `build_llm_select_prompt_input` (cases with
  first_choice / events / answer examples)
- No later-stage encode call
- No hybrid rule post-stack
- After the call: join and projection only
- Model: Gemini 3.7 Flash
- Work cell:
  `scratch/holdout/paper/gan_llm_select_policy_examples/`
- Recorded prompt version: `gan_llm_select_policy_examples`
- Call transport: live sync (OpenRouter batch returned 402)
- Do not write into `gan_llm_select_from_extract`

## Fixed comparators

| Cell | Purist |
| --- | ---: |
| Cited cell 5 (`gan_llm_select_from_extract`) | **357**/450 |
| Cited cell 4 (`llm_select_only`) | **382**/450 |
| Cited cell 3 (`llm_select_after_codebook`) | **387**/450 |

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `test450` |
| Row policy | `aggregate_only` |
| Scorer | Purist; secondary Pragmatic and scorable count |
| Public output | stop counts and rates only |

Do not inspect, quote, or tune on holdout identifiers, notes,
predictions, evidence, errors, or changed rows. The public artifact
must not contain those keys. A holdout defect starts a new
development candidate; it does not permit holdout repair.

## Required analysis

Aggregate Purist / Pragmatic / scorable versus cited cell 5. Do not
compute row-level rescue or harm tables. Do not promote. Do not
refresh Table 1.

## Stop rule

Stop after the isolated work cell is scored and the public aggregate
is written. Do not overwrite cited cell 5. Do not load `dev750` in
this protocol.

## Claim boundary

Holdout aggregate-only measurement of a living select-prompt
candidate. Not Table 1. Not a promotion. Not hybrid select.
