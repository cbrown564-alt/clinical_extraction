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

1. Reproduce Gan-compatible data loading and evaluation.
2. Port author-provided label parsing, repair, and category mapping under tests.
3. Build a simple deterministic baseline.
4. Implement DSPy event extraction and clinical reasoning modules.
5. Add row-level error analysis and a living notebook.
6. Add ablation toggles for deterministic rule categories and DSPy stages.
7. Produce paper-facing tables for component effects, rule effects, failure modes, and evidence validity.

## Current Repo State

- Python package skeleton exists under `src/clinical_extraction`.
- Gan 2026 task module exists under `tasks/seizure_frequency/gan2026`.
- Initial README, architecture notes, pipeline design notes, decision record, and runbook exist.
- Research contribution thesis exists under `docs/research`.
- Git repository has been initialized.
- Dependency-free compile/import smoke checks pass.
- `pytest` has not been run because it is not installed in the current system Python.

## Immediate Next Step

Port the author-provided Gan label parser and repair logic into `gan2026.normalize` with focused tests.
