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
- Experiment output from package source

These boundaries are useful now because they expose failure modes. They are also the minimum reusable shape needed later for other clinical extraction tasks.

## Non-Goals For The First Pass

- A generic workflow engine
- A fully pluggable registry system
- Dataset-agnostic prompt abstractions
- Broad support for every epilepsy dataset

Those can come later if repeated code proves they are needed.

