# Clinical Extraction

Hybrid deterministic-LLM pipelines for extracting structured data from unstructured clinical notes.

The long-term goal is a Python package for modular clinical extraction tasks: data loading, clinical extraction/reasoning, normalization, structured schemas, scoring, evaluation, and error analysis. The active phase is deletion-led repository surgery and evidence repair before the final paper experiments; Gan 2026 holdout evidence remains frozen. See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) for the live objective and evidence stack.

This is also a research codebase. The intended paper contribution combines
benchmark performance with an account of how modular hybrid systems work: what
deterministic rules contribute, what LLM reasoning contributes, where each
fails, and how evidence and rationale records can make clinical extraction
easier to inspect.

## Current Focus

**Authoritative steering:** [`PROJECT_STATUS.md`](PROJECT_STATUS.md) and
[`docs/plans/ACTIVE_ROADMAP.md`](docs/plans/ACTIVE_ROADMAP.md).

The repo runs two parallel extraction tracks. **Track 1 (Gan 2026)** asks a single
question per letter: what is the patient's current seizure frequency? Its held-out
test set (`test450`) is frozen — cite aggregate scores only, not row-level tuning.
**Track 2 (ExECTv2)** extracts several epilepsy phenotypes (diagnosis, seizure
frequency, prescriptions, investigations) from de-identified letters; this track is
still active. Primary scoreboards: **Purist** on Gan `test450`; **`clinical_headline`**
composite on ExECT.

Active work (2026-07-14):

- **Surgery:** source, document, and artifact reduction are complete. The
  retained manifest selects the six no-call reference cells; the five largest
  replay artifacts are content-addressed Git LFS objects.
- **Quality:** pytest and mypy pass on the reduced backend. Ruff has 120
  line-length and two import-order findings; fresh-checkout verification is
  still outstanding.
- **Follow-up evidence:** deterministic phrase/CUI/full-attribute-bundle
  reproduction, broad-phenotyping confidence calibration, annotation-evidence
  consolidation, and the frozen six-model comparison follow the cleanup.
- **Split boundary:** Gan test450 remains aggregate-only; ExECT full200 is a
  development-inclusive aggregate audit, not an independent holdout.

The surgery assessment, completed batches, inspection findings, and deletion
pitfalls are recorded in
[`docs/research/maintenance/repository_surgery_assessment_2026-07-14.md`](docs/research/maintenance/repository_surgery_assessment_2026-07-14.md).

**Reading by thread:** [`docs/THREAD_MAP.md`](docs/THREAD_MAP.md) (five paths, ≤8
hops each).

Both tasks share modular hybrid architecture (rules / LLM-only / hybrid families).
Gan seizure-frequency remains the focused single-label benchmark; ExECTv2
covers broad epilepsy phenotyping on de-identified letters.

## Design Principles

- Build for Gan 2026 first, but keep task boundaries clean enough for later datasets.
- Prefer small, inspectable modules over an abstraction-heavy framework.
- Separate extraction from clinical selection so error analysis can localize failures.
- Keep deterministic label policy compatible with the author-provided evaluation code.
- Preserve auditable evidence spans and rationale in schemas alongside final labels.
- Keep reproducible analysis in tested scripts and manifest-selected artifacts.
- Treat deterministic rules as explicit, categorized, testable, and ablatable components.
- Separate general clinical/date rules from seizure-frequency rules, dataset-specific rules, and benchmark-formatting rules.
- Use GPT-4.1 mini for most early LLM experiments; reserve Qwen 3.6:35b for later local strong-reasoning comparisons once a pipeline exceeds 0.8 Purist (strict Gan scorer) F1; keep DSPy GEPA with GPT-5.4 as a backlog optimizer option.

## Research Thesis

The project is designed around four paper-level claims:

- Previous epilepsy NLP systems tend to handle broad phenotyping or seizure-frequency extraction better than they handle both. This project tests whether a modular architecture can support both.
- The project must measure generalisation because rules-based and LLM systems can both overfit to local templates or datasets.
- Transparency requires intermediate schemas, evidence, rationale, error analysis, and ablation studies, not only final predictions.
- Reports must describe deterministic preprocessing and post-processing rules as controlled experimental variables, not hide them as implementation details.

See [docs/research/contribution_thesis.md](docs/research/contribution_thesis.md).

See [docs/design/model_strategy.md](docs/design/model_strategy.md) for LLM model policy and required run metadata.

See
[docs/design/component_evidence_attribution_architecture.md](docs/design/component_evidence_attribution_architecture.md)
and
[docs/runbooks/gan2026_component_evidence_audit.md](docs/runbooks/gan2026_component_evidence_audit.md)
for the audit method used to decide which component solved each
clinical subproblem, whether LLM changes to deterministic answers are correct,
and whether a candidate has the required evidence and regression results.

## Repository Layout

```text
src/clinical_extraction/
  core/                         Shared pipeline, schema, evidence, validation primitives.
  tasks/seizure_frequency/
    gan2026/                    Gan-specific loader, labels, scoring, pipeline, and analysis.
docs/
  design/                       Architecture and pipeline design notes.
  decisions/                    Lightweight architecture decision records.
  experiments/                  Human-readable experiment reports and predeclarations.
  NAVIGATION.md                 Short guide to current documents and retained evidence.
  plans/                        The active roadmap.
  research/                     Thesis, manuscript, annotation source, and surgery owner.
  runbooks/                     Repeatable development/evaluation workflows.
  literature/                   Literature reviews and source PDFs.
experiments/                    Manifest-selected outputs and the retained registry.
tests/                          Focused tests for data contracts and deterministic behavior.
```

## Resuming Work

- **Plain-language glossary:** [docs/reference/plain_language_glossary.md](docs/reference/plain_language_glossary.md)
- **Documentation map:** [docs/NAVIGATION.md](docs/NAVIGATION.md)
- **Short reading paths:** [docs/THREAD_MAP.md](docs/THREAD_MAP.md)
- **Active roadmap:** [docs/plans/ACTIVE_ROADMAP.md](docs/plans/ACTIVE_ROADMAP.md)
- **Live control board:** [PROJECT_STATUS.md](PROJECT_STATUS.md)
- Active experiments index: [experiments/README.md](experiments/README.md)
- Regenerating tracked artifacts: [docs/REGENERATION.md](docs/REGENERATION.md)

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
