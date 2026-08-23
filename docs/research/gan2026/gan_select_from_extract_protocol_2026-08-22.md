# Gan select-from-extract protocol

Date: 2026-08-22
Status: completed 2026-08-22
Result: [select-from-extract](gan_select_from_extract_2026-08-22.md)
Owner: this file

## Question

If later-stage Gemini select reads the codebook extract ledger
directly, skipping LLM encode, what is the `dev750` Purist score
versus extract (0.78) and versus select after encode (0.79)?

## Why it matters

Later-stage encode on the codebook extract drops 68 letters
(0.78 → 0.69). If select can do its job from extract labels, encode
may be skippable on the LLM row.

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

## Candidate

Fresh later-stage select call. Same select prompt. Event labels come
from extract: the extract pick uses `final_label`; other events use
`raw_value`. No encode work cell. No hybrid post-stack.

## Fixed comparators

- Codebook extract stop: 0.78
- Later-stage encode then select on that ledger: 0.69 / 0.79
- Rule encode/select on that raw: 0.80 / 0.86
- Do not overwrite `gan_llm_select` or `gan_llm_encode` work cells

## Required analysis (same cut)

On `dev750`, why later-stage encode harms extract, and why rule
encode helps the same raw. Same-pick versus form change. Rescue and
harm counts. Do not retune `label_forms`.

## Stop rule

Stop after the `dev750` select-from-extract cell is scored and the
encode comparison is written. Do not run holdout. Do not promote.

## Claim boundary

Development candidate. Not holdout. Not a paper column until
promoted.
