# Architecture

This project should grow from a concrete benchmark implementation into a reusable clinical extraction package without becoming over-engineered early.

## Package Layers

`clinical_extraction.core` contains task-neutral primitives:

- pipeline protocols and result containers
- evidence-span utilities
- validation and repair result types
- shared schema base models

`clinical_extraction.tasks` contains task-specific implementations. A task can define its own data contract, schemas, label policy, deterministic components, DSPy modules, evaluators, and error-analysis views.

The first task is `seizure_frequency.gan2026`.

## Boundary Choices

The project intentionally separates:

- Loading from scoring
- Event extraction from final clinical reasoning
- Label normalization from metric mapping
- Evidence validation from correctness evaluation
- Model selection from prompt/program behavior
- Experiment output from package source
- General rules from task-specific, dataset-specific, and benchmark-specific rules

These boundaries are useful now because they expose failure modes. They are also the minimum reusable shape needed later for other clinical extraction tasks.

LLM model policy is documented in `docs/design/model_strategy.md`. Model choice
should be recorded as run metadata so experiments can distinguish schema,
prompt, deterministic-rule, optimizer, and runtime-model effects.

## Rule Taxonomy

Deterministic behavior should not collapse into an unstructured regex pile. Rules should be grouped by clinical meaning and expected portability:

- `general`: dates, durations, intervals, section boundaries, evidence substring checks
- `clinical_epilepsy`: seizure terminology and epilepsy-note conventions
- `seizure_frequency`: rates, clusters, seizure-free durations, current-versus-historical selection helpers
- `gan2026_specific`: synthetic-letter patterns or data quirks specific to Gan 2026
- `benchmark_format`: transformations needed to produce accepted Gan label strings without changing clinical interpretation

Each category should be separately testable and, where practical, ablatable.

## Non-Goals For The First Pass

- A generic workflow engine
- A fully pluggable registry system
- Dataset-agnostic prompt abstractions
- Broad support for every epilepsy dataset

Those can come later if repeated code proves they are needed.
