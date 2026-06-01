# Clinical Extraction

Hybrid deterministic-LLM pipelines for extracting structured data from unstructured clinical notes.

The long-term goal is a Python package for modular clinical extraction tasks: data loading, clinical extraction/reasoning, normalization, structured schemas, scoring, evaluation, and error analysis. The short-term goal is narrower and sharper: beat the seizure-frequency benchmarks from Gan 2026, prioritizing purist F1.

This is also a research codebase. The intended paper contribution is not only higher benchmark performance, but a clearer account of how modular hybrid systems work: what deterministic rules contribute, what LLM reasoning contributes, where each fails, and how evidence/rationale trails can make clinical extraction less opaque.

## Current Focus

Immediate work is exclusively focused on:

- Dataset: `data/Gan (2026)/synthetic_data_subset_1500.json`
- Paper: `data/Gan (2026)/Synthetic Clinical Letters for Seizure Frequency.pdf`
- Author code: `data/Gan (2026)/previous implementation/`
- Primary metric: purist F1

The first pipeline hypothesis is:

```text
clinical note
  -> DSPy seizure-event extractor
  -> deterministic frequency/date normalization
  -> DSPy clinical reasoner for grouping, temporal selection, and final answer
  -> deterministic schema/evidence validation
  -> deterministic repair where interpretation is unchanged
  -> Gan-compatible evaluation
```

## Design Principles

- Build for Gan 2026 first, but keep task boundaries clean enough for later datasets.
- Prefer small, inspectable modules over an abstraction-heavy framework.
- Separate extraction from clinical selection so error analysis can localize failures.
- Keep deterministic label policy compatible with the author-provided evaluation code.
- Preserve auditable evidence spans and rationale in schemas, not just final labels.
- Make notebooks a forcing function for reproducible learning, not a side artifact.
- Treat deterministic rules as explicit, categorized, testable, and ablatable components.
- Separate general clinical/date rules from seizure-frequency rules, dataset-specific rules, and benchmark-formatting rules.
- Use GPT-4.1 mini for most early LLM experiments; reserve Qwen 3.6:35b for later local strong-reasoning comparisons once a pipeline exceeds 0.8 purist F1; keep DSPy GEPA with GPT-5.4 as a backlog optimizer option.

## Research Thesis

The project is designed around four paper-level claims:

- Previous epilepsy NLP systems tend to handle broad phenotyping or seizure-frequency extraction better than they handle both; a modular architecture should make both feasible.
- Generalisation should be engineered and measured, especially because both rules-based systems and LLM systems can overfit to local templates or datasets.
- Transparency requires intermediate schemas, evidence, rationale, error analysis, and ablation studies, not only final predictions.
- Deterministic preprocessing and post-processing rules should be described as controlled experimental variables rather than hidden implementation details.

See [docs/research/contribution_thesis.md](docs/research/contribution_thesis.md).

See [docs/design/model_strategy.md](docs/design/model_strategy.md) for LLM model policy and required run metadata.

## Repository Layout

```text
src/clinical_extraction/
  core/                         Shared pipeline, schema, evidence, validation primitives.
  tasks/seizure_frequency/
    gan2026/                    Gan-specific loader, labels, scoring, pipeline, and analysis.
docs/
  design/                       Architecture and pipeline design notes.
  decisions/                    Lightweight architecture decision records.
  runbooks/                     Repeatable development/evaluation workflows.
experiments/                    Run outputs and experiment records.
notebooks/                      Living notebooks for loading, extraction, evaluation, errors.
tests/                          Focused tests for data contracts and deterministic behavior.
```

## Getting Started

Create and activate an environment, then install the package in editable mode:

macOS/Linux:

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

The first implementation milestone is to reproduce Gan-compatible data loading, label normalization, and evaluation locally before optimizing the DSPy pipeline.

## Local Ollama Runs

Ollama setup is intentionally separate from the repo setup. Once Ollama is
running on a Windows laptop, use the LLM CLI's local endpoint flag so the run
metadata records the model route:

```powershell
gan2026-llm-experiment --pipeline llm_only_claim_table_selector --mode live --limit 1 --model ollama_chat/qwen3.6:35b --api-base http://localhost:11434 --disable-dspy-cache
```

Use Ollama's native LiteLLM route, `ollama_chat/...`, for Qwen reasoning models.
The shared LM builder sends `think=false`; do not use the OpenAI-compatible
`openai/...` plus `/v1` route for Qwen 3.6 because it can hide reasoning while
leaving DSPy with empty structured output. Keep early local runs tiny
(`--limit 1`, then `--limit 5`, then `--limit 25`) until latency, format
adherence, and endpoint behavior are known.
