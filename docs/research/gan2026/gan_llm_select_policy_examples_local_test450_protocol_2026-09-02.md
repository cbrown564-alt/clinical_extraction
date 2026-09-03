# Protocol: Local same-model policy-example select on Gan `test450`

Date: 2026-09-02
Status: complete
Report: [result](gan_llm_select_policy_examples_local_test450_2026-09-03.md)
Owner: this file
Guardrail: `gan2026-scoring-guardrail`;
[holdout is aggregate-only](../../paper/decisions/holdout-is-aggregate-only.md);
[later-stage select](../../paper/decisions/gan-later-stage-encode-select-prompts.md)

## Primary question

What are the Purist select-stop counts when Qwen 3.8 27B and Gemma 4
26B run the living policy-example select prompt on their own saved
codebook extract ledgers?

## Why this matters

Cited cell 5 is Gemini select on Gemini `gan_llm_extract`
(`gan_llm_select_policy_examples`, 383/450). The local models already
have sealed `gan_llm_extract` `test450` ledgers. This protocol measures
the same second call, same-model, without a later-stage encode and
without rereading the letter.

## Frozen candidate

- Find ledger: saved `gan_llm_extract` rows for the same slug
- Select: living `build_llm_select_prompt_input`
  (`gan_llm_select_policy_examples`)
- Method: `gan_llm_select_from_extract`
- No later-stage encode call
- No hybrid rule post-stack
- After the call: join and projection only
- Models: `qwen38_27b` then `gemma4_26b` (one resident model at a time)
- Work cells:
  `scratch/holdout/paper/gan_llm_select_from_extract/<slug>/gan_llm_extract/test450`
- Call transport: local sync (Ollama). Not OpenRouter batch.
- Do not write into the Gemini cited work tree
  `scratch/holdout/paper/gan_llm_select_policy_examples/gemini37flash/`
  or `paper_experiments/gan/gan_llm_select_from_extract/`

## Fixed comparators

| Cell | Purist |
| --- | ---: |
| Qwen codebook find (`gan_llm_extract` `test450`) | **315**/450 |
| Gemma codebook find (`gan_llm_extract` `test450`) | **299**/450 |
| Cited Gemini cell 5 | **383**/450 |

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

Aggregate Purist / Pragmatic / scorable versus each model's own find
stop and versus cited Gemini cell 5. Do not compute row-level rescue
or harm tables. Do not promote. Do not refresh Table 1.

## Stop rule

Stop after both isolated work cells are scored and the public
aggregates are written. Do not overwrite cited cell 5. Do not load
`dev750` in this protocol.

## Claim boundary

Holdout aggregate-only transfer measurement. Not Table 1. Not cited
cell 5. Not a six-model roster change. Not hybrid select. Gemini
remains the cited later-stage model.
