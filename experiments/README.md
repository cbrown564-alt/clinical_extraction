# Selected experiment evidence

This directory contains the saved outputs and run records needed by the paper.

Start with:

- the [retained evidence index](../docs/experiments/retained_evidence_manifest.md)
  for a readable map;
- its [JSON source](../docs/experiments/retained_evidence_manifest.json) for
  paths, hashes, replay inputs, and evidence limits;
- [registry.jsonl](registry.jsonl) for selected run records.

Rejected and superseded runs remain in Git history instead of a live catalogue.
Five large ExECT replay files are immutable Git LFS objects; run `git lfs pull`
when a checkout contains pointer files.

Gan test450 permits aggregate results only. Do not add or inspect row-level
holdout reports. ExECT full200 includes development rows and is not an
independent holdout.
