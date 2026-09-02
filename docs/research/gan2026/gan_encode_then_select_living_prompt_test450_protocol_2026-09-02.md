# Protocol: Living-prompt encode-then-select on Gan `test450`

Date: 2026-09-02
Status: complete
Owner: this file
Report: [aggregates](gan_encode_then_select_living_prompt_test450_2026-09-02.md)
Guardrail: `gan2026-scoring-guardrail`;
[holdout is aggregate-only](../../paper/decisions/holdout-is-aggregate-only.md)
Related: [later-stage encode/select](../../paper/decisions/gan-later-stage-encode-select-prompts.md),
[source-near vs bundled encode](../paper/gan_source_near_vs_bundled_encode_2026-08-23.md),
[policy-example select](gan_llm_select_policy_examples_test450_protocol_2026-08-31.md)

## Primary question

On locked `test450`, what are the Purist stops when Gemini:

1. encodes and then selects with the living select prompt, on codebook
   find and on the saved source-near encode ledger; and
2. does find, encode, and select in one request that adds the living
   select cases to the codebook extract prompt?

## Why this matters

Table 3a paired codebook find **354** with the Aug 21
`gan_llm_encode` cell **291**. That encode cell used
`gan_llm_with_rules` (`gan_llm_extract_raw`). Cited cell 5 is
select-from-extract with the living prompt (**383**), not
encode-then-select. The living prompt and a true codebook encode
have not been measured together on holdout.

## Frozen candidate

Four isolated Gemini 3.7 Flash live cells. Temperature 0. Living
low thinking. No hybrid rule post-stack. After each call: join and
projection only. Do not overwrite
`paper_experiments/gan/gan_llm_encode`,
`paper_experiments/gan/gan_llm_select`, or
`paper_experiments/gan/gan_llm_extract`.

1. **Codebook encode.** `gan_llm_encode` on saved
   `gan_llm_extract` raws.
   Work leaf: `gan_llm_encode_on_codebook`.
2. **Codebook encode-then-select.** `gan_llm_select` on cell 1,
   living `gan_llm_select_policy_examples`.
   Work leaf: `gan_llm_select_after_codebook_encode`.
3. **Source-near encode-then-select.** `gan_llm_select` on the
   promoted Aug 21 `gan_llm_encode` raws, scored against saved
   `gan_llm_extract_raw`. Living `gan_llm_select_policy_examples`.
   Work leaf: `gan_llm_select_after_source_near_encode`.
   No new encode calls.
4. **One-call find, encode, and select.**
   `gan_llm_extract_encode_select`: codebook extract plus the
   living select cases. Work leaf:
   `gan_llm_extract_encode_select`. Score the extract stop only
   (`raw_model`). Do not replay rule select.

Call transport: OpenRouter batch.

## Fixed comparators

| Cell | Purist |
| --- | ---: |
| Codebook find (`gan_llm_extract`) | **354**/450 |
| Source-near find (`gan_llm_extract_raw`) | **246**/450 |
| Aug 21 encode (source-near ledger) | **291**/450 |
| Aug 21 encode-then-select (old prompt) | **320**/450 |
| `dev750` codebook encode-then-select | 0.78 / **0.69** / 0.79 |
| Cited cell 5 (select from extract) | **383**/450 |
| Cited cell 3 (rule encode + rule select) | **387**/450 |

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

Aggregate Purist / Pragmatic / scorable / parse / call failures for
each cell. Compare codebook encode to find 354 and to dest750 0.69.
Compare each living-prompt select to encode, to old-prompt 320, and
to cited cell 5. Compare the one-call extract stop to codebook find
354 and to cited cell 5 383. Do not compute row-level rescue or harm
tables. Do not promote. Do not refresh Table 1.

## Stop rule

Stop after the four isolated work cells are scored and the public
aggregate is written. Do not load `dev750` in this protocol. Do not
overwrite cited later-stage cells.

## Claim boundary

Holdout aggregate-only measurement of encode-then-select with the
living select prompt. Ablation, not Table 1. Not cell 5. Not hybrid
select.
