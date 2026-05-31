# Project Kanban

Last updated: 2026-05-31

## Now

- Reconcile Gan normalization policy for raw semantics vs scoring sentinels.
- Port remaining author prediction repair behavior into `gan2026.normalize` under focused tests.
- Preserve Gan-compatible Purist scoring while cluster and sentinel behavior are made explicit.

## Next

- Produce a simple deterministic baseline once scoring parity is in place.
- Create the first evaluation/error-analysis table for development rows.
- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.

## Blocked

- Final benchmark-comparison language is blocked until local scoring policy is reconciled with the author implementation.

## Backlog

- Add split manifests for development, evaluation, and quarantine surfaces.
- Add run-record metadata templates under `experiments/`.
- Implement row-level error slicing for the expected Gan 2026 failure modes.
- Add DSPy event extraction and clinical reasoner modules after deterministic substrate parity.

## Done Recently

- 2026-05-31: Created initial package, docs, tests, and Gan 2026 task skeleton.
- 2026-05-31: Added project-specific Codex workflow skills for TDD, kanban/status, experiments, and scoring guardrails.
- 2026-05-31: Created local `.venv`, installed dev dependencies, and verified `pytest`/`ruff`.
- 2026-05-31: Reproduced Gan data loading/evaluation substrate with tested gold-label extraction, monthly frequency parsing, row quality flags, and evaluation helpers.
- 2026-05-31: Documented Step 1 inspection findings, including cluster-policy disagreement, sentinel collapse, misleading `clinic_date` field naming, and 30-day month conversion.
- 2026-05-31: Decided to include `row_ok=False` rows for development/evaluation while retaining the flag for stratified analysis, and to prefer author evaluation-script scoring.
