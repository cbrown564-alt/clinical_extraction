# Holdout is aggregate-only

Date: 2026-08-17
Status: current
Owner: [paper methods](../methods.md)

## Decision

`test450` (Gan) and `test60` (ExECT) are locked. Cite aggregate
scores only. Do not inspect holdout identifiers, notes, predictions,
evidence, errors, or changed rows.

A holdout defect starts a new development candidate. It does not
permit holdout repair, prompt change, or scorer change from those
rows.

Development splits (`dev750`, `dev140`) may be reviewed.

Replay files for holdout cells keep only `source_row_index` or
`letter_id`, `prompt_version`, and `raw_output`.

## Why

Row inspection on a locked split turns a confirmation into tuning.

## Consequences

- Reports and paper sources show aggregates only for holdout.
- Runners may read locked notes only to make frozen calls and to
  rescore saved outputs. Those notes do not enter documents.
- Do not retune from sealed `test450`, Real(300), or ExECT `test60`.
