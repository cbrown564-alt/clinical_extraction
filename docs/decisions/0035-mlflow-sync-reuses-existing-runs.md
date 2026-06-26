# ADR 0035: MLflow Sync Reuses Existing Runs Before Backfill

Date: 2026-06-26

## Status

Accepted and implemented.

## Decision

Broader MLflow registry backfill must not create duplicate runs for the same
registry row or comparison group. Before any wider sync, mirror helpers must look
up an existing MLflow run and reuse it when possible.

Lookup keys:

- child or single runs: `registry_run_id` tag, with `params.registry_run_id`
  fallback for earlier mirrors;
- parent comparison runs: `comparison_id` tag.

On reuse, refresh tags, metrics, and selected artifacts only. MLflow params are
immutable, so they are logged on first create and left unchanged afterward.

Broader backfill beyond the first same-core dev140 group remains deferred. That
group stays local observability, not claim-of-record.

## Context

Phase 2 sync already mirrors registry rows and one parent/child comparison group,
but re-running `--sync` created duplicate MLflow runs. That is acceptable for a
one-off local mirror, but it would make a broader backfill hard to navigate and
could let stale duplicate runs look like competing evidence.

The registry remains canonical. MLflow is only an index. Even so, duplicate
mirror rows would waste local storage and make comparison UI misleading.

## Consequences

- `mirror_payload_to_mlflow` searches for an existing run before creating a new
  one.
- Registry-derived payloads now tag `registry_run_id` in addition to logging it
  as a param.
- Re-sync updates metrics/tags/artifacts on the existing run id.
- Historical duplicate runs created before this ADR are not auto-merged; manual
  `mlruns/` cleanup remains optional.
- Broader registry backfill can proceed once an operator confirms doctor/sync
  health, but still requires explicit scope selection and remains non-canonical.

## Verification

`tests/test_core_mlflow_tracking.py` covers lookup-key selection, param fallback
search, and reuse of an existing mirrored run without creating a duplicate.
