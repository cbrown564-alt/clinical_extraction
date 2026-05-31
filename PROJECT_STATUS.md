# Project Status

Last updated: 2026-05-31

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that exceeds 0.9 purist F1 while preserving enough structure to support future clinical extraction tasks.

## Research Objective

Produce a paper-quality hybrid deterministic-LLM system that demonstrates modular breadth/depth, improved generalisation discipline, transparent per-note reasoning/evidence trails, and rigorous component-level error analysis/ablation.

## Current Strategy

Start with a small package core and a Gan-specific task implementation. Reproduce data loading, label normalization, and scoring before optimizing any DSPy modules.

Treat deterministic rules as controlled variables. Categorize each rule by portability and clinical meaning so experiments can separate general date logic, seizure-frequency logic, Gan-specific synthetic patterns, and benchmark-formatting repairs.

## Active Milestones

1. Port author-provided label repair logic and clarify the remaining normalization policy under tests.
2. Build a simple deterministic baseline.
3. Implement DSPy event extraction and clinical reasoning modules.
4. Add row-level error analysis and a living notebook.
5. Add ablation toggles for deterministic rule categories and DSPy stages.
6. Produce paper-facing tables for component effects, rule effects, failure modes, and evidence validity.

## Current Repo State

- Python package skeleton exists under `src/clinical_extraction`.
- Gan 2026 task module exists under `tasks/seizure_frequency/gan2026`.
- Initial README, architecture notes, pipeline design notes, decision record, and runbook exist.
- Research contribution thesis exists under `docs/research`.
- Git repository has been initialized.
- Local `.venv` has been created with project dev dependencies.
- Gan-compatible data loading and evaluation reproduction is complete for the current JSON surface.
- Loader exposes full note text, gold label/reference, quality flags, raw rows, and parsed monthly gold frequency.
- Gold label parsing now covers all 1,500 local Gan rows under focused tests.
- Scoring policy prefers the author evaluation script when it conflicts with CSV-preparation behavior.
- `row_ok=False` rows are included in the development/evaluation surface and retained for stratified analysis.
- Step 1 inspection is documented in `docs/research/gan2026_step1_inspection.md`.
- `pytest` and `ruff` pass in the local `.venv`.

## Work Board

### Now

- Reconcile Gan normalization policy for raw semantics vs scoring sentinels.
- Port remaining author prediction repair behavior into `gan2026.normalize` under focused tests.
- Preserve Gan-compatible Purist scoring while cluster and sentinel behavior are made explicit.

### Next

- Produce a simple deterministic baseline once scoring parity is in place.
- Create the first evaluation/error-analysis table for development rows.
- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.

### Blocked

- Final benchmark-comparison language is blocked until local scoring policy is reconciled with the author implementation.

### Backlog

- Add split manifests for development, evaluation, and quarantine surfaces.
- Add run-record metadata templates under `experiments/`.
- Implement row-level error slicing for the expected Gan 2026 failure modes.
- Add DSPy event extraction and clinical reasoner modules after deterministic substrate parity.

### Done Recently

- 2026-05-31: Created initial package, docs, tests, and Gan 2026 task skeleton.
- 2026-05-31: Added project-specific Codex workflow skills for TDD, kanban/status, experiments, and scoring guardrails.
- 2026-05-31: Created local `.venv`, installed dev dependencies, and verified `pytest`/`ruff`.
- 2026-05-31: Reproduced Gan data loading/evaluation substrate with tested gold-label extraction, monthly frequency parsing, row quality flags, and evaluation helpers.
- 2026-05-31: Documented Step 1 inspection findings, including cluster-policy disagreement, sentinel collapse, misleading `clinic_date` field naming, and 30-day month conversion.
- 2026-05-31: Decided to include `row_ok=False` rows for development/evaluation while retaining the flag for stratified analysis, and to prefer author evaluation-script scoring.

## Immediate Next Step

Pause before baseline work to reconcile normalization policy: preserve raw semantic labels separately from scoring sentinels, then port the remaining author repair logic for model predictions.
