# Retained experiment evidence

This directory contains only the saved outputs needed by the retained
two-task, three-family reference system and the paper's direct evidence
packages.

Start with:

- [`docs/experiments/retained_evidence_manifest.md`](../docs/experiments/retained_evidence_manifest.md)
  for the human-readable evidence map;
- [`docs/experiments/retained_evidence_manifest.json`](../docs/experiments/retained_evidence_manifest.json)
  for paths, hashes, replay inputs, and claim boundaries; and
- [`registry.jsonl`](registry.jsonl) for the retained run records.

The registry is intentionally selective. Rejected and superseded runs remain
recoverable from Git history instead of being maintained as a live catalog.
Large retained artifacts remain in Git until an immutable external store has
been chosen and its retrieval contract has been added to the manifest.

Gan `test450` evidence is aggregate-only. Do not add row-level locked-test
reports or use locked rows for tuning. ExECT `full200` is a
development-inclusive audit, not an independent holdout.
