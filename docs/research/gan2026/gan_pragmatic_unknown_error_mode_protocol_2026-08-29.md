# Protocol: Pragmatic gold → unknown error modes

Date: 2026-08-29
Status: completed
Owner: this file
Prior:
[rate → unknown / no-seizure](gan_pragmatic_infrequent_error_mode_protocol_2026-08-29.md),
[last-event well-since](gan_last_event_well_since_protocol_2026-08-29.md)
Report:
[unknown-error report](gan_pragmatic_unknown_error_mode_2026-08-29.md)

## Primary question

On living Gemini cell 3 (select stop, after `last_event_well_since`),
how much of the remaining pragmatic error is gold → unknown, and what
letter types produce gold seizure-free → unknown on `dev750`?

Infrequent → unknown and frequent → unknown are already typed in the
prior study. This study adds the missing gold-seizure-free → unknown
slice and treats the three golds as one unknown-column family.

## Why this study

Last-event well-since removed almost all infrequent → seizure-free
errors. The remaining large pragmatic leak is collapse into Unknown.
The published `test450` matrix already shows frequent → unknown (13)
and infrequent → unknown (16). Seizure-free → unknown (8 before
promotion; recompute on the living stack) is the third gold that
feeds that column and has not been typed.

## Scope

- Dataset: Gan 2026. Manifest: `gan2026_split_v1`.
- Candidate: living Gemini 3.7 Flash cell 3 select
  (`gan_llm_extract` → `gan_rules_encode` →
  `llm_select_after_codebook` with `last_event_well_since` on).
- Comparators (secondary, `dev750` only): extract, encode,
  rules-only three-stage select.
- Scorer: living `map_pragmatic` / `map_purist`.
- Replay: no-call. Zero new model calls.
- `test450`: aggregate confusion counts only. No row ids, no letter
  text, no failure inspection.
- `dev750`: row-level qualitative analysis permitted for gold
  seizure-free → unknown. Reuse prior-study types for infrequent →
  unknown and frequent → unknown; recompute counts on the living
  stack. Mark
  `data_text_policy: synthetic_development_raw_text_diagnostic`.

## Required analysis

1. Quantitative: full 4×4 pragmatic confusion for living cell-3
   select on `test450` (counts only) and `dev750`. Report gold →
   unknown as a share of all pragmatic errors, plus the three
   source cells (frequent, infrequent, seizure-free).
2. Same unknown-column counts on `dev750` for extract, encode, and
   rules-only.
3. Qualitative, `dev750` only, gold seizure-free predicted unknown
   at select. Assign mutually readable letter types. Quote short
   synthetic spans when needed. Do not retype the prior infrequent
   and frequent unknown slices unless the living stack changes their
   membership.

## Artifact

`docs/research/gan2026/gan_pragmatic_unknown_error_mode_2026-08-29.json`

`test450` object: counts only. `dev750` object: matrices, unknown-
column counts, and a row table for gold seizure-free → unknown.
Letter text stays in the report.

## Stop rule

Answer from saved artifacts. Do not retune. Do not inspect holdout
rows. Do not treat this as a repair surface for the holdout matrix.

## Claim boundary

Development answer for seizure-free → unknown types on `dev750`.
Holdout remains aggregate-only. Not a new cited score. Infrequent
and frequent unknown types remain owned by the prior report unless
this living-stack recount changes them.
