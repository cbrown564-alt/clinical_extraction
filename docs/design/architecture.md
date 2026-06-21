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

Candidate-promotion and architecture-comparison work should also follow the
component evidence contract in
`docs/design/component_evidence_attribution_architecture.md`. That contract
defines how every candidate answers which component solved each clinical
subproblem, under which evidence gate, with what regression risk, and on which
distribution.

## ExECTv2 Clinical Finding Assembly

For ExECTv2 Plan 11, the implementation spine is a manifest-driven clinical
finding assembly:

- `ClinicalFinding`: an evidence-backed clinical assertion with entity, text,
  attributes, evidence, source metadata, and provenance.
- `ClinicalFindingStore`: a per-letter collection of raw and scored findings
  from all candidate producers.
- `CandidateProducer`: a component that proposes findings, currently including
  saved JSONL replay adapters for frozen LLM or hybrid artifacts.
- `EntityLens`: entity-specific reconciliation over the store, such as
  Diagnosis hierarchy/negation, SeizureFrequency state adjudication,
  Prescription regimen, or Investigations result lenses.
- `FindingView`: a scoring/rendering view over the final findings, including
  raw candidate, evidence-valid, clinical headline, fidelity companion, and
  benchmark/CUI views.
- `AttributionSidecar`: row-level `FindingSource` and `ProvenanceEvent` records
  that preserve producer ownership, deterministic actions, evidence status, and
  view-specific rendering.

The first implementation is behavior-preserving:
`exectv2_holistic_finding_assembly_v01_dev140` structurally replays frozen
dev140 artifacts through this object model. It is architecture cleanup and
component evidence only, not a full-200, holdout, or benchmark claim.

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
