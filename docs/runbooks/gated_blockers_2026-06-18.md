# Split-Authorization Runbook

Last updated: 2026-07-14

This runbook states what must exist before holdout-facing work. It does not
authorize a run.

## Gan 2026

Gan `test450` is a locked holdout. Development may not inspect its row-level
predictions, errors, evidence, or slice membership.

Before any new aggregate holdout run, create a dated frozen protocol that names:

- explicit user authorization for the run;
- split manifest `gan2026_split_v1` and distribution `test450`;
- frozen candidate code, prompt or program, model, scorer, gates, and repair
  policy;
- output paths and hashes where practical;
- predeclared aggregate readouts, stop rule, and claim language;
- a no-row-inspection policy during development.

A holdout defect starts a new validation candidate. It never licenses tuning on
the holdout. The governing split rules are in
`docs/design/gan2026_split_protocol.md`.

## ExECTv2

`dev140` is the row-inspectable development surface. `test60` is held out from
row-level development. `full200` combines the two and is therefore a
development-inclusive aggregate audit, not an independent holdout.

Before a new `full200` run, create a dated protocol that freezes the candidate,
prompt or program, model, scorer, projection, repair policy, output paths,
aggregate readouts, failure handling, and stop rule. The run must not expose or
use `test60` rows for tuning.

## Permitted Work Without New Authorization

- Gan train or validation work within the split protocol;
- ExECT `dev140` experiments and row-level analysis;
- no-call replay and hash verification of selected evidence;
- aggregate reproduction of already selected frozen evidence.

## Verification

Use the repository environment:

```sh
source .venv/bin/activate
python -m pytest
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
```

Current verified results belong in `PROJECT_STATUS.md`, not in this runbook.
