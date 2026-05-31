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
- Loader now preserves normalized gold labels, semantic label kind, yearly bounds, and monthly scorer values separately.
- Prediction-label repair behavior has been ported into `gan2026.normalize` for common author-script repairs.
- Scoring policy prefers the author evaluation script when it conflicts with CSV-preparation behavior.
- `row_ok=False` rows are included in the development/evaluation surface and retained for stratified analysis.
- Step 1 inspection is documented in `docs/research/gan2026_step1_inspection.md`.
- Ten-letter schema exploration is documented in `docs/research/gan2026_schema_exploration_10_examples.md`.
- Pipeline V1 now specifies richer candidate-event, deterministic-normalization, and final-selection schemas.
- LLM model strategy is documented in `docs/design/model_strategy.md`: GPT-4.1 mini for rapid baseline experiments, Qwen 3.6:35b later for local strong-reasoning tests after a pipeline exceeds 0.8 purist F1, and GPT-5.4 only as a possible DSPy GEPA teacher.
- First schema-shaped deterministic V1 baseline is implemented in `gan2026.pipeline_v1`.
- V1 run record exists at `experiments/gan2026_v1_deterministic_baseline_2026-05-31.md`.
- V1 development result on all 1,500 local rows is 0.3120 Purist micro F1/accuracy; this is not benchmark-comparable and mostly reflects low recall plus unknown/no-reference scorer collapse.
- V1 selected-evidence validity is 1,500/1,500 exact source substrings.
- `pytest` and `ruff` pass in the local `.venv` after baseline implementation.

## Work Board

### Now

- Improve deterministic candidate recall for ordinary frequency evidence before adding LLM reasoning.
- Create a row-level error-analysis table for the V1 baseline, prioritizing missed `frequency` and `seizure_free` gold kinds.
- Add patterns for distributed month lists, interval language such as `every 4 days`, and no-event/seizure-free phrasing with breakthrough-event guards.

### Next

- Start a living notebook for loading, gold-label distribution, scoring, and failure slices.
- Add split manifests for development/evaluation/quarantine surfaces before stronger benchmark language.
- Use GPT-4.1 mini as the default LLM runtime model for early DSPy experiments and record exact model metadata in run artifacts after deterministic recall is less brittle.

### Blocked

- Final benchmark-comparison language is blocked until split policy and replication surface are explicit.

### Backlog

- Add split manifests for development, evaluation, and quarantine surfaces.
- Add run-record metadata templates under `experiments/`.
- Implement row-level error slicing for the expected Gan 2026 failure modes.
- Add DSPy event extraction and clinical reasoner modules after deterministic substrate parity.
- After at least one pipeline exceeds 0.8 purist F1, run controlled Qwen 3.6:35b local-model comparisons on the Windows laptop.
- Consider DSPy GEPA with GPT-5.4 as teacher after the hand-built pipeline has stable artifacts and failure slices.

### Done Recently

- 2026-05-31: Created initial package, docs, tests, and Gan 2026 task skeleton.
- 2026-05-31: Added project-specific Codex workflow skills for TDD, kanban/status, experiments, and scoring guardrails.
- 2026-05-31: Created local `.venv`, installed dev dependencies, and verified `pytest`/`ruff`.
- 2026-05-31: Reproduced Gan data loading/evaluation substrate with tested gold-label extraction, monthly frequency parsing, row quality flags, and evaluation helpers.
- 2026-05-31: Documented Step 1 inspection findings, including cluster-policy disagreement, sentinel collapse, misleading `clinic_date` field naming, and 30-day month conversion.
- 2026-05-31: Decided to include `row_ok=False` rows for development/evaluation while retaining the flag for stratified analysis, and to prefer author evaluation-script scoring.
- 2026-05-31: Reconciled normalization sentinels by adding semantic label records and loader fields while preserving Gan scorer collapse to `1000`.
- 2026-05-31: Ported tested author prediction-label repair behavior into `gan2026.normalize`; `pytest` and `ruff` pass.
- 2026-05-31: Worked through 10 Gan letters and updated the V1 pipeline schema toward source-near candidate events, deterministic normalization, and traceable final selection.
- 2026-05-31: Documented LLM model strategy and experiment-metadata requirements.
- 2026-05-31: Implemented the first schema-shaped deterministic V1 baseline with candidate events, normalized events, final selection diagnostics, and exact evidence validation.
- 2026-05-31: Evaluated V1 on all 1,500 local Gan rows: Purist micro F1/accuracy 0.3120, evidence validity 1,500/1,500, with failures dominated by missed frequency/seizure-free evidence.

## Immediate Next Step

Build the V1 row-level error-analysis table, then improve deterministic recall for distributed event counts, interval-derived rates, and seizure-free/no-event phrasing while preserving exact evidence validation.
