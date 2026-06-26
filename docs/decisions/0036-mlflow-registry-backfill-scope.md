# ADR 0036: MLflow Registry Backfill Scope

Date: 2026-06-26

## Status

Accepted.

## Decision

Broader MLflow registry backfill is explicitly scoped, operator-selected, and
non-canonical. It must never replace or compete with `experiments/registry.jsonl`,
report Markdown, or `PROJECT_STATUS.md` as claim-of-record.

Default broader backfill scope is `paper_facing`, not the full registry:

- include rows on or after `2026-06-24`;
- include rows whose `registry_roles` intersect
  `architecture_comparator`, `reliability_scorecard`, `component_ladder`, or
  `holdout_anchor`;
- exclude untagged historical rows, `model_family_variant`-only diagnostics,
  `negative_attribution`, and `historical_lineage` unless an operator chooses a
  wider scope.

Supported operator scopes:

| Scope | Meaning |
| --- | --- |
| `same_core_dev140` | Existing parent/child comparison group only. |
| `paper_facing` | Default broader backfill. Paper-facing reliability, architecture, component, and holdout-anchor rows since 2026-06-24. |
| `reliability_slice` | Reliability scorecards and architecture comparators since 2026-06-24. |
| `all_since_2026_06_24` | Every registry row on or after 2026-06-24, regardless of role. |
| `full_registry` | Entire `experiments/registry.jsonl`. Explicit opt-in only. |

Additional rules:

- Reuse existing MLflow runs per ADR 0035 before creating new ones.
- Pointer artifacts remain the default for row-level JSONL and large files.
  `--include-large-artifacts` is explicit per invocation and must not become the
  default backfill policy.
- Restricted surfaces (`test`, `holdout`, `full200`) stay aggregate-only in
  MLflow metadata and artifact policy.
- Registry entries stay MLflow-agnostic. MLflow tags point back via
  `registry_run_id`; MLflow run ids are not written into the registry.
- Operators should run `clinical-extraction-mlflow-doctor` before any backfill.

## Context

ADR 0035 made re-sync idempotent, and the same-core dev140 comparison group is
already mirrored. The implementation plan left broader backfill unscoped: whether
to mirror all `240` registry rows, only recent reliability work, and whether raw
JSONL should ever be copied by default.

Without an explicit scope, a local backfill would either bloat `mlruns/` with
historical exploratory rows or create a misleading "complete registry mirror"
that looks like competing evidence.

## Consequences

- `clinical-extraction-mlflow-sync` exposes `--backfill-scope` and optional
  `--registry-role` overrides.
- The default broader backfill command is:

```powershell
clinical-extraction-mlflow-sync --backfill-scope paper_facing --sync
```

- Wider scopes require explicit operator choice; `full_registry` is documented
  as local observability only.
- The runbook records scope tiers, artifact policy, and preflight checks.
- Open question 1 in the MLflow observability plan is resolved by this ADR.
- Automatic post-registration mirroring (Phase 3) remains deferred until an
  operator confirms the scoped backfill policy in practice.

## Verification

`tests/test_mlflow_registry_sync.py` covers scope resolution, role filtering,
and dry-run selection for `paper_facing` and `full_registry`.
