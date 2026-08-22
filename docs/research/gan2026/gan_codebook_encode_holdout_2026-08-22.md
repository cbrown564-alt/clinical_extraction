# Gan codebook-encode holdout

Date: 2026-08-22
Status: holdout aggregates written; not promoted
Owner: [protocol](gan_codebook_encode_holdout_protocol_2026-08-22.md)
Artifact: `experiments/gan_codebook_encode_holdout_20260822/summary.json`

## Answer

On locked `test450`, frozen `llm_encode_codebook` is **359/450 (0.80)**.
That is above identity extract **354/450 (0.79)** and the historical
selected-evidence encode **346/450 (0.77)**. Codebook encode then the
living select families is **373/450 (0.83)**, above historical encode
then select **362/450 (0.80)** and select-without-encode **368/450
(0.82)**.

The replay reproduced every locked stop used as a comparator. No
holdout rows were inspected. `claims.md` and the cited five-cell
artifact were not overwritten.

## Protocol

Gemini 3.7 Flash, Purist, saved `gan_llm_extract_label_forms` raw,
zero model calls. Arms: identity, historical `llm_encode`, frozen
`llm_encode_codebook`, `llm_select_after_codebook`, historical
`llm_select`, and `llm_select_only`.

## Component result

| Encode / select policy | Purist | Pragmatic | Scorable |
| --- | ---: | ---: | ---: |
| Identity (`raw_model`) | 354/450 (0.79) | 366/450 (0.81) | 448 |
| Historical rule encode | 346/450 (0.77) | 359/450 (0.80) | 449 |
| Codebook encode | **359/450 (0.80)** | **371/450 (0.82)** | 449 |
| Historical encode then select | 362/450 (0.80) | 372/450 (0.83) | 449 |
| Select only | 368/450 (0.82) | 377/450 (0.84) | 448 |
| Codebook then select | **373/450 (0.83)** | **382/450 (0.85)** | 449 |

Identity, historical encode, historical select, and select-only match
the locked cell-3/4 stops.

## Candidate five-cell Purist

Cell 3 encode is `llm_encode_codebook`. Cell 3 select is
`llm_select_after_codebook`. Cells 1, 2, 4, and 5 are the locked
published aggregates.

| # | LLM | Rules | Extract | Encode | Select |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | | extract, encode and select | 0.73 | 0.73 | 0.73 |
| 2 | extract | extract, encode and select | 0.82 | 0.80 | 0.82 |
| 3 | extract | encode, select | 0.79 | **0.80** | **0.83** |
| 4 | extract, encode | select | 0.79 | 0.79 | 0.82 |
| 5 | extract, encode and select | | 0.79 | 0.79 | 0.79 |

Locked cell 3 was 0.79 / 0.77 / 0.80. The historical renderer still
drops the extract score. The codebook candidate does not.

## Attribution

The study scores frozen policies only. It does not say which holdout
letters moved. Development already showed that the historical renderer
re-derives a label after a codebook extract, and that the candidate
preserves the parsed label except for eight named gap repairs. The
holdout direction matches that mechanism: encode no longer costs
letters, and select after codebook encode is higher than select after
the historical rewrite.

This is still a hybrid development artifact plus one frozen-prompt
holdout replay. It is not a second-model result and not a paper
column.

## Claim boundary

Holdout evidence for the frozen codebook-encode candidate. Aggregate
only. Do not inspect `test450` rows. Do not retune rules from this
total. Do not treat this table as the cited Gemini grid until
promoted.

## Next

Decide whether to replace the cited cell-3 encode/select with
`llm_encode_codebook` / `llm_select_after_codebook`. If yes, update
`claims.md`, `README.md`, and
`paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json`
in a separate promotion cut.
