# Research Contribution Thesis

This project sits in a long line of epilepsy NLP work, summarized for this repo in:

```text
literature/hybrid_seizure_phenotype_literature_review.pdf
```

The engineering design should support a research paper, not only a benchmark run. The core claim is that seizure-frequency extraction should be treated as a modular, auditable clinical extraction problem where deterministic rules and LLM reasoning are both explicit, testable components.

## Contribution 1: Modular Breadth And Depth

Prior epilepsy NLP systems often do one of two things well:

- broad epilepsy phenotyping
- narrow seizure-frequency extraction

The project aims to show that a modular clinical extraction architecture can support both. Gan 2026 seizure frequency is the first high-pressure task, but the package should keep enough structure to later support broader phenotyping and other extraction targets.

Implication for the repo:

- Keep task-specific code under `tasks/`.
- Keep reusable primitives in `core/` only when they genuinely apply across tasks.
- Treat seizure frequency as the first task module, not the identity of the whole package.

## Contribution 2: Generalisation By Design

Rules-based systems are often precise but brittle: they can work well on a particular note template, institution, or clinician style, then lose recall elsewhere. LLM systems can also overfit to a dataset, prompt, or benchmark surface.

The project aims to build and evaluate a hybrid system that is:

- transparent about which behavior is deterministic and which behavior is model-mediated
- efficient enough to run practical experiments
- modular enough to test general versus dataset-specific components
- designed for cross-template and cross-dataset evaluation rather than only local benchmark fit

Implication for the repo:

- Label rules by portability: general, task-specific, dataset-specific, or benchmark-specific.
- Separate clinical logic from benchmark formatting.
- Preserve ablation switches so each component can be removed or replaced.
- Treat model choice as an experimental variable. Early hosted GPT-4.1 mini runs,
  later local Qwen 3.6:35b comparisons, and possible GPT-5.4 GEPA-teacher runs
  should be reported as distinct conditions rather than blended together.

## Contribution 3: Transparency Through Evidence, Reasoning, And Error Analysis

Many systems are black boxes in practice. Rules are inspectable in principle, but complex regex stacks can become difficult to reason about. LLMs add another layer of opacity.

The project aims to make system behavior inspectable at two levels:

- per-note transparency: extracted events, evidence spans, assertions, temporality, uncertainty, normalized values, final rationale
- corpus-level transparency: rigorous error analysis, failure-mode taxonomies, and ablation studies showing which components help or hurt

Implication for the repo:

- Store intermediate events, not just final predictions.
- Validate evidence as source substrings where possible.
- Maintain row-level error-analysis outputs as first-class experiment artifacts.
- Track failure modes in clinically meaningful categories.

## Contribution 4: Deterministic Rules As A Controlled Variable

LLM clinical extraction papers often include preprocessing and post-processing rules, but these rules may be underdescribed, hard to reproduce, or treated as implementation detail. Here, deterministic rules are part of the scientific object.

The project should make rules explicit, categorized, testable, and ablatable.

Rule categories should distinguish:

- general date and duration patterns likely to transfer across clinical settings
- seizure-frequency expressions likely to transfer across epilepsy notes
- task-specific temporal-selection rules for seizure frequency
- Gan-specific synthetic-letter patterns, such as diary phrasing or benchmark label quirks
- benchmark-formatting rules needed only to score against Gan-style labels

The expected pattern is itself a research question: highly specific rules may fit local training data exceptionally well but generalize poorly. The repo should make that visible instead of hiding it inside regex soup.

## Paper-Relevant Outputs

The implementation should produce artifacts that can become paper tables and figures:

- component ablation table
- deterministic-rule category ablation table
- error taxonomy with counts and examples
- per-label purist and pragmatic performance
- evidence-validity rate
- schema-validity and repair-rate summaries
- examples showing successful and failed temporal reasoning
