# Gan five-cell prefix grid

Date: 2026-08-22
Status: locked aggregates written
Owner: [protocol](gan_five_cell_grid_protocol_2026-08-22.md)
Paper artifact: `paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`

## Answer

On locked `test450`, codebook extract is the Gemini LLM extract and
encode column (**0.79**). Rule select without encode (**0.82**) matches
Rules then LLM select and beats full rule encode-then-select (**0.80**)
and LLM select (**0.79**). Rule encode on that extract **drops** the
score (0.79 → 0.77).

## `dev750` Purist

| # | LLM | Rules | Extract | Encode | Select |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | | extract, encode and select | 0.89 | 0.89 | 0.89 |
| 2 | extract | extract, encode and select | 0.86 | 0.86 | 0.89 |
| 3 | extract | encode, select | 0.78 | 0.80 | 0.86 |
| 4 | extract, encode | select | 0.78 | 0.78 | 0.85 |
| 5 | extract, encode and select | | 0.78 | 0.78 | 0.79 |

## Locked `test450` Purist (aggregate only)

| # | LLM | Rules | Extract | Encode | Select |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | | extract, encode and select | 0.73 | 0.73 | 0.73 |
| 2 | extract | extract, encode and select | 0.82 | 0.80 | 0.82 |
| 3 | extract | encode, select | 0.79 | 0.77 | 0.80 |
| 4 | extract, encode | select | 0.79 | 0.79 | 0.82 |
| 5 | extract, encode and select | | 0.79 | 0.79 | 0.79 |

Holdout rows were not inspected. The old `gan_llm_with_rules` grid
is the source-near ablation.

## Post-grid development diagnosis

The rule-encode drop prompted a `dev750` changed-row audit. The existing
renderer re-derives an answer from evidence after the LLM has already attempted
a codebook label. A codebook-preserving candidate raises development Purist
accuracy from 0.8027 to 0.8093 against that renderer, changes 27 rows with 22
Purist rescues and no observed Purist or exact-label harms, and keeps semantic
select/revision separate. See the
[protocol](gan_codebook_encode_rule_development_protocol_2026-08-22.md) and
[development result](gan_codebook_encode_rule_development_2026-08-22.md).

This is inspected development evidence only. It does not replace any locked
`test450` aggregate above.

A later frozen holdout of that candidate is
[codebook-encode holdout](gan_codebook_encode_holdout_2026-08-22.md).
On `test450` codebook encode is 359/450 (0.80) and codebook then
select is 373/450 (0.83). That candidate grid is not the cited table
in this file.

## Claim boundary

Frozen-prompt holdout aggregates. Promoted into `claims.md` and
`README.md` as the cited Gemini frequency grid. Do not retune
`label_forms`. Do not inspect holdout rows.
