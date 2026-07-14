# Research contribution

The literature review is in
`literature/hybrid_seizure_phenotype_literature_review.pdf`.

The project studies clinical extraction as a sequence of inspectable decisions.
Deterministic rules and model reasoning are both explicit, testable components.

## Methods compared

- **Rules only:** deterministic rules determine the clinical facts.
- **LLM only:** the model determines the clinical facts; deterministic code may
  validate or format them.
- **LLM with rules:** model and deterministic code can both change clinical meaning.

Saved filenames retain older long identifiers. Current commands and prose use
the plain names above; see the [naming guide](../reference/plain_language_glossary.md).

## Contribution 1: one package for narrow and broad extraction

Gan 2026 tests one difficult concept, current seizure frequency. ExECTv2 tests
several epilepsy phenotypes. The package keeps shared code in `core` and task
logic in `tasks` so the same extraction, evidence, scoring, and analysis tools
can support both.

## Contribution 2: test transfer rather than assume it

Rules and models can both fit a local template or benchmark. The project labels
rules by expected portability, separates clinical logic from benchmark
formatting, records models as experimental conditions, and removes components
in saved-output comparisons. Results must state the dataset and split to which
they apply.

## Contribution 3: make decisions inspectable

Per-letter outputs retain extracted events, evidence spans, assertion status,
time, uncertainty, normalized values, and rationale. Corpus analyses count
clinically meaningful failure types and identify the first component that made
an error unrecoverable.

## Contribution 4: treat rules as experimental variables

Deterministic behavior is grouped as general, clinical epilepsy,
seizure-frequency, Gan-specific, or benchmark-format logic. Tests and ablations
show which group helps or hurts. This prevents preprocessing and repair rules
from disappearing into an undifferentiated method description.

## Paper outputs

The final evidence must include method comparisons for both tasks, component
and rule-group ablations, error counts and examples, task-appropriate scores,
evidence and schema validity, repair rates, confidence results, and worked
examples of successful and failed temporal reasoning.
