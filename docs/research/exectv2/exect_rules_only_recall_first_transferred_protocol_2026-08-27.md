# Protocol: ExECT rules-only recall-first transferred keep set

Date: 2026-08-27
Status: complete — gates met on dev140
([results](exect_rules_only_recall_first_transferred_2026-08-27.md))
Prior evidence:
[Phase A–C results](exect_rules_only_recall_first_restructure_2026-08-27.md),
[Phase D aggregate-only replay](exect_rules_only_recall_first_test60_aggregate_2026-08-27.md).
Comparator: `run_letter` = `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)`,
dev140 select stop **0.9167**. Cited `test60` row stays **0.8018**.
`test60` is sealed. No holdout load, inspection, or retune in this study.

## Primary question

After Phase D classified the four Phase C keeps as transfer versus
development-only, can a new development candidate that **keeps only the
transferring mechanisms** (Prescription recall expansion and SF state
variant) and **drops the holdout-losing keeps** (Diagnosis heading
decomposition and Investigations result variant) still beat **0.9167**
on `dev140` with zero comparator-exact regressions?

## Why this is a new candidate

Phase D forbade changing `RECALL_FIRST_THREE_STAGE_CONFIG` and forbade
holdout retune. This protocol does not mutate that freeze. It names a
new config, `TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG`, built only
from mechanisms the aggregate-only family bands already classified.

## Fixed measurement frame

- Dataset: ExECTv2 `dev140` only.
- Scorer: `clinical_inventory_unit_keys`, four-family micro F1.
- Zero model calls.
- Changed-pair accounting as in the recall-first measurement script.

## Candidate

Base: `ACCEPTED_THREE_STAGE_CONFIG` recognise flags (no result-less
Investigations emission, no unassociated SF-anchor widening).

Recognise emits only:

- `rx_recall_expansion` (external lexicon, typo, parse)
- `sf_state_variant`

Select: `selection.recall_first_unsupported_drop` plus
`selection.keep_rx_recall_expansion` and
`selection.keep_sf_state_variant` (existing conditions unchanged).

Not emitted, not kept: heading decomposition, Investigations result
variants, and every Phase C rejected class. Those producers remain in
the repo so the frozen Phase C config can still replay.

## Gates (dev140)

- Select F1 >= **0.9167**.
- Zero comparator-exact letter/family regressions versus `run_letter`.
- Diagnosis and Investigations select F1 not below the comparator
  (those families must match the accepted program).
- Prescription and SeizureFrequency select F1 each >= comparator.

If any gate fails, report a negative result and leave `run_letter` on
`ACCEPTED_THREE_STAGE_CONFIG`.

## Stop rules

- Do not promote cited rows from this study.
- Do not load `test60`.
- Do not change `RECALL_FIRST_THREE_STAGE_CONFIG` or
  `ACCEPTED_THREE_STAGE_CONFIG`.

## Claim boundary

Development mechanism evidence. Transfer was already measured for the
superset stack; this study only asks whether the pruned keep set still
wins on `dev140`.
