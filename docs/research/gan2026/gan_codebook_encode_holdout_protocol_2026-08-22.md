# Gan codebook-encode holdout protocol

Date: 2026-08-22
Status: completed 2026-08-22
Owner: this file
Result: [codebook-encode holdout](gan_codebook_encode_holdout_2026-08-22.md)

## Question

On locked `test450`, what are the Purist aggregates for the frozen
`llm_encode_codebook` candidate after `gan_llm_extract_label_forms`,
and what is the five-cell grid when cell 3 encode is that candidate
instead of the historical selected-evidence renderer?

## Why it matters

Development on `dev750` froze codebook encode as identity plus eight
named gap repairs. The locked five-cell grid still scores cell 3
encode with the historical renderer, which dropped holdout Purist
from 0.79 to 0.77. Holdout is required before that cell can change.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `test450` (`gan2026_split_v1` test) |
| Row policy | Aggregate only. Do not inspect rows. Do not dump failure ids. |
| Saved extract | `scratch/holdout/paper/gan_llm_extract_label_forms/gemini37flash/test450/rows.jsonl` |
| Model | Gemini 3.7 Flash |
| Prompt | Frozen `gan_llm_extract_label_forms` |
| Call mode | Saved-output deterministic replay; no model calls |
| Scorer | Gan Purist; secondary Pragmatic and scorable count |

Do not load development residuals to retune. Do not write holdout
`rows.jsonl`, `changes.jsonl`, or source-row identifiers.

## Candidate arms

All arms reuse the same frozen extract raw and gold labels.

1. **Identity / extract** — `raw_model`. Must match the locked extract
   cell (354/450).
2. **Historical encode** — `llm_encode`. Must match the locked cell 3
   encode (346/450).
3. **Codebook encode** — frozen `llm_encode_codebook`.
4. **Codebook then select** — `llm_select_after_codebook`: codebook
   encode, then the living select families. No selected-evidence
   re-derivation.
5. **Historical encode then select** — `llm_select`. Must match the
   locked cell 3 select (362/450).
6. **Select only** — `llm_select_only`. Must match locked cell 4
   select (368/450).

Cells 1, 2, 4, and 5 stay the locked published aggregates. This study
replaces only cell 3 encode and, if scored, cell 3 select.

## Fixed comparators

- Locked Gemini five-cell grid
- Do not overwrite `paper_experiments/gan/five_cell_grid/`
- Do not promote `claims.md` or `README.md` in this cut
- Do not run later-stage `gan_llm_encode` or new model calls

## Stop rule

Stop after the aggregate comparison and the candidate five-cell table
are written. A negative result is allowed: if codebook encode does
not beat historical encode on Purist, keep the locked cell 3 encode
and do not promote.

## Claim boundary

Frozen-candidate holdout aggregates. Not a paper column until
promoted. Not permission to inspect holdout rows or retune rules.
