# ADR 0034: MLflow Is Optional Observability

Date: 2026-06-26

## Status

Accepted for Phase 0-1 implementation.

## Decision

Add MLflow as an optional local observability layer, not as a source of research
truth. The canonical record for claims remains:

- predeclarations and report Markdown;
- raw JSON/JSONL artifacts selected by protocol;
- `experiments/registry.jsonl`;
- `experiments/RUN_INDEX.md`;
- `PROJECT_STATUS.md` when a durable project decision changes.

MLflow support starts as a disabled-safe helper behind the optional `mlops`
dependency. Normal package imports and experiment runners must continue to work
when MLflow is not installed.

## Context

The project now has many comparable ExECTv2 and Gan 2026 runs, including model
swaps, replay analyses, reliability scorecards, and component-impact ladders.
Those artifacts are scientifically useful, but hard to search and compare in a
local working session. MLflow can provide a standard tracking UI and searchable
metadata without changing the evidence spine.

The risk is that a convenient tracking UI becomes a shadow claim system, or that
raw row-level traces leak across split and inspection boundaries. This ADR keeps
MLflow behind the registry and starts with aggregate-safe metadata only.

## Consequences

- `mlflow` lives in the optional `mlops` dependency group.
- Local MLflow state such as `mlruns/` and `mlflow.db` is ignored by git.
- `src/clinical_extraction/core/mlflow_tracking.py` owns MLflow imports,
  environment configuration, payload normalization, artifact safety checks, and
  non-strict failure handling.
- When the helper uses the default repo-local `file:<repo>/mlruns` backend it
  sets `MLFLOW_ALLOW_FILE_STORE=true`, which MLflow 3 requires for filesystem
  tracking. Explicit `MLFLOW_TRACKING_URI` values are left untouched.
- `experiments/registry.jsonl`, `RUN_INDEX.md`, and source reports remain the
  claim-of-record even when a run is mirrored to MLflow.
- Restricted surfaces such as Gan test450, ExECTv2 full-200 aggregate audits,
  and holdout-like readouts must not log raw row text, prompts, model outputs,
  evidence snippets, or row-level failure ledgers through this helper.
- The default trace policy is disabled. Raw tracing requires a later explicit
  decision and must preserve split discipline.

## Verification

Phase 0-1 is covered by focused tests for optional import behavior, environment
configuration, payload conversion, metric/tag normalization, artifact path
safety, and non-strict MLflow failure handling.
