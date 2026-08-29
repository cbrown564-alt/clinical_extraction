# Protocol: Pragmatic rate → unknown / no-seizure error modes

Date: 2026-08-29
Status: completed
Revised: 2026-08-29 (add frequent → unknown)
Owner: this file
Report: [error-mode report](gan_pragmatic_infrequent_error_mode_2026-08-29.md)

## Primary question

On living Gemini cell 3 (select stop), is the largest pragmatic error
the gold-infrequent row predicted as unknown or no seizure frequency
reference, as the published `test450` pragmatic confusion matrix
shows? Is that also the largest pragmatic error on `dev750`? Within
that cell on `dev750`, what letter-level types produce it?

The same study then types the second-largest off-diagonal: gold
frequent predicted as unknown. Frequent → no seizure is counted but
is not a qualitative target (3 rows on `dev750`, 1 on `test450`).

## Why this study

The paper figure `paper/draft/confusion_matrix_pragmatic.pdf` is the
Gemini cell-3 `test450` pragmatic matrix. Infrequent recall is the
weakest diagonal (49/80 = 0.61). The two largest off-diagonals in that
row are unknown (16) and no seizure (13). The study asks whether that
is a holdout-only pattern and what mechanisms sit inside it on the
permitted development split.

## Scope

- Dataset: Gan 2026. Manifest: `gan2026_split_v1`.
- Candidate: living Gemini 3.7 Flash cell 3 select
  (`gan_llm_extract` → `gan_rules_encode` →
  `llm_select_after_codebook`).
- Comparators (secondary, same rows): encode stop, extract stop,
  rules-only three-stage select. Used only to locate the first stop
  that leaves the gold pragmatic band.
- Scorer: living `map_pragmatic` / `map_purist` on
  `gold_monthly_frequency` and the parsed predicted label.
- Replay: no-call. Zero new model calls.
- `test450`: aggregate confusion counts only. No row ids, no letter
  text, no failure inspection. Published figure counts are the owner
  if they match a no-text replay of saved labels.
- `dev750`: row-level qualitative analysis permitted. Synthetic
  development text may be quoted. Mark
  `data_text_policy: synthetic_development_raw_text_diagnostic`.

## Required analysis

1. Quantitative: full 4×4 pragmatic confusion for cell-3 select on
   `test450` (counts only) and `dev750`. Rank off-diagonal cells by
   count. Report infrequent→{unknown, no-seizure} as a share of all
   pragmatic errors and of gold-infrequent support.
2. Same ranking on `dev750` for extract, encode, and rules-only.
3. Qualitative, `dev750` only, two focal slices at select:
   gold-infrequent predicted unknown or no-seizure, and gold-frequent
   predicted unknown. Assign mutually readable buckets from gold
   Purist band, predicted kind/label, stage where the rate was lost,
   and letter pattern (dated isolated event, seizure-free competitor,
   uncertainty language, sparse diary, qualitative
   “occasional/infrequent”, competing semiologies, historical vs
   current, cluster). Quote short synthetic spans when needed.

## Artifact

`docs/research/gan2026/gan_pragmatic_infrequent_error_mode_2026-08-29.json`

`test450` object: counts only. `dev750` object: matrices, bucket
counts, and a row table with ids, labels, buckets. Letter text stays
in the report, not the JSON, unless a one-line span is required to
reproduce a bucket.

## Stop rule

Answer from saved artifacts. Do not retune. Do not inspect holdout
rows. If `dev750` ranking disagrees with `test450`, report the
disagreement; do not treat development as a repair surface for the
holdout matrix.

## Claim boundary

Diagnostic plus development answer for infrequent→sentinel and
frequent→unknown on `dev750`. The `test450` matrix remains an
aggregate-only holdout description. This study does not support a new
cited score or a holdout row-level claim.
