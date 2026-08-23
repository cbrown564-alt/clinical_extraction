# Gan codebook-extract grid protocol

Date: 2026-08-22
Status: completed 2026-08-22
Result: [codebook-extract grid](gan_codebook_extract_grid_2026-08-22.md)
Owner: this file

## Question

If Gemini extract uses the closed `label_forms` list, what are the
`dev750` extract / encode / select scores for (1) later-stage LLM
encode and select on that ledger, (2) rule encode and select on that
same raw, and (3) a new `gan_llm_pre_post` request that also carries
`label_forms`, then rule encode and select?

## Why it matters

The codebook extract is the intended Gemini extract. The old
`gan_llm_extract_raw` request stays as a source-near ablation. The
four-method grid has to sit on the new extract, or encode/select
would still describe the old ledger.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `dev750` only |
| Row policy | Development review permitted |
| Holdout | Do not load or inspect `test450` |
| Model | Gemini 3.7 Flash |
| Scorer | Purist; secondary Pragmatic and scorable count |
| Extract source | Saved `gan_llm_extract` raw |

## Candidate arms

1. **LLM** — later-stage Gemini encode, then select, on the codebook
   extract ledger. Fresh calls. No hybrid post-stack after those calls.
2. **LLM then rules** — no new extract call. Replay `raw_model`,
   `llm_encode`, and `llm_select` on the same codebook extract raw.
3. **Rules then LLM** — new `gan_llm_and_rules_extract` extract
   (suggested quotes plus `label_forms`). Then the same rule
   encode/select replay on that new raw.

## Fixed comparators (not overwritten)

- Promoted `gan_llm_extract_raw` extract and its later-stage encode/select
- Promoted `gan_llm_pre_post` without `label_forms`
- Standalone rules `0.89`

## Stop rule

Stop after the three `dev750` arms are scored. Do not retune
`label_forms`. Do not overwrite `gan_llm_extract_raw` or living
`gan_llm_pre_post`. Do not run holdout in this cut. Do not promote
into the claims table until the `dev750` grid is written.

## Claim boundary

Development candidate grid. Not holdout. Old `gan_llm_extract_raw`
remains the source-near ablation.
