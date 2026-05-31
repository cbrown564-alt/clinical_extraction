# Project Kanban

Last updated: 2026-05-31

## Now

- Set up the local development environment and verify `pytest` and `ruff`.
- Port Gan 2026 label repair/parsing behavior into `gan2026.normalize` under focused tests.
- Preserve Gan-compatible Purist scoring while author behavior is reconciled.

## Next

- Add tests for allowed label formats, sentinels, ranges, clusters, and `multiple`.
- Produce a simple deterministic baseline once scoring parity is in place.
- Create the first evaluation/error-analysis table for development rows.
- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.

## Blocked

- Final benchmark-comparison language is blocked until local scoring policy is reconciled with the author implementation.
- Row inclusion policy for the 65 `row_ok=False` rows is blocked until the benchmark protocol is explicit.

## Backlog

- Add split manifests for development, evaluation, and quarantine surfaces.
- Add run-record metadata templates under `experiments/`.
- Implement row-level error slicing for the expected Gan 2026 failure modes.
- Add DSPy event extraction and clinical reasoner modules after deterministic substrate parity.

## Done Recently

- 2026-05-31: Created initial package, docs, tests, and Gan 2026 task skeleton.
- 2026-05-31: Added project-specific Codex workflow skills for TDD, kanban/status, experiments, and scoring guardrails.
