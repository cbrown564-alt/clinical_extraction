# Software architecture

Updated: 2026-09-13. This document owns interface responsibilities. Source and tests
own exact behaviour; the [migration record](../research/maintenance/repository_migration_2026-09-08.md)
owns completed reconstruction and checks. The [roadmap](../plans/ACTIVE_ROADMAP.md)
and [paper protocol](../research/gan2026/one_shot_paper_protocol.md) own current work.
Longitudinal extensions and research-paper tables are postponed.

## Implemented owners

All Python paths below are under `src/clinical_extraction/`.

| Responsibility | Owner |
| --- | --- |
| Source/request identity, evidence locations, typed artifacts, attempts and persistence | `core/` |
| Model construction | `core/dspy_runtime.py`; clinical policy stays outside it |
| Ordinary extraction and evaluation commands | `operational/` |
| Shared evaluation and saved-result infrastructure | `evaluation/` |
| Gan and ExECT prompts, parsers, projection and native scoring | Their task packages, including task-owned `evaluation/` |
| Existing demo/workbench API and inspection | `inspection/` |
| Saved longitudinal linking, history and queries, currently paused | `longitudinal/` |
| Browser UI | `frontend/` |

One Python package and one frontend remain. Old `paper/` and `trace_explorer/`
Python namespaces were removed after moving consumers. Saved identifiers and
historical artifact paths remain interpretable through explicit reader mappings.
The no-install `run.py` HPC workflow is retained.

## Records and evidence

| Object | Minimum responsibility | Boundary |
| --- | --- | --- |
| `SourceDocument` | Stable source ID, immutable version/content hash, exact text view and its hash | No gold labels. Visit/event/availability times remain explicitly supplied domain metadata. No silent whitespace or Unicode rewriting. |
| `EvidenceRef` | Source version and text-view hash, exact quote and zero-based character range with exclusive end, location status | Implemented support is text only. Table locators are deferred. Multiple references can jointly support one assertion. |
| `ExtractionArtifact[T]` | Artifact ID, schema/profile/request identity, input source references, original response reference, typed domain output and separate diagnostics | No mandatory selected answer; `T` is domain-owned. |
| `Assertion[T]` | Artifact-scoped assertion ID, typed content, evidence references and production provenance | Domain records can retain certainty, reporter and event time. An assertion ID is not a real-world event ID. Existing IDs survive adapters. |
| `Relationship` | Typed domain relation between assertion IDs, supporting evidence and derivation/version | Recency or equal names alone do not establish correction or identity. Unresolved relations remain explicit. |
| `DecisionRecord[T]` | Policy/version, request parameters/cutoff, input artifact IDs, result and supporting/unresolved predicates | Does not mutate assertions. Clinical indeterminacy is distinct from execution failure or unsupported input schema. |
| `CoverageRecord` | Declared capture families, processed/failed source parts and known unsupported fields | Processing success is not exhaustive recall. Clinical absence and complete-history claims require their own source-supported assertions. |

Source text and its model-visible view have explicit hashes. Evidence offsets
refer to that view; an assertion ID is not a patient event ID. Equal response text
does not establish identical input or execution settings. Changed source text
invalidates saved-request matching.

Preserve supplied evidence even when invalid. A unique exact match can support a
recorded location correction; repeated matches remain ambiguous unless offsets
disambiguate them. Exact location does not establish clinical support. Missing,
negated and uncertain findings remain distinct from parser or provider failure.

## Prompt and execution boundary

A task profile declares capture scope, domain types, schema and prompt components.
Keep instructions, label presentation, evidence obligations, schema descriptions
and examples individually inspectable. Preserve their versions/hashes and the
exact ordered rendered messages; moving strings alone does not prove equivalent
requests.

Execution configuration owns model, revision, decoding and retry limits. Evaluation
configuration owns data, reference, scorer and split permissions. Do not infer
these from a mutable global setting or a historical method alias.

DSPy is an execution adapter; typed domain records and offline scoring must remain
usable without a live model. Request-aware persistence records each attempt,
response and failure. Offline replay requires the same declared request identity.
A timeout, invalid JSON or unsupported schema is not a valid empty clinical record.

For the paper, the model returns findings and the final answer in one call.
Parsing and format handling must not silently change the selected clinical answer.
Historical task adapters can contain semantic rules: audit the chosen route before
calling it the paper's primary condition. A clinical meaning change is attributed
separately, regardless of which module contains it.

## Boundaries to preserve

- Separate extraction, evidence location, clinical interpretation and native scoring.
- Keep Gan single-label and ExECT inventory reference semantics task-specific.
- Keep raw responses, format recovery and semantic transformations distinguishable.
- Retain original source accounts when interpreting saved longitudinal outputs;
  query-conditioned historical captures are not query-independent extractions.
- Add no new serving, optimizer, universal clinical schema or table parser without
  a current task that requires it.

The [generated stage reference](../architecture/README.md) documents retained
benchmark implementations. Those historical pipelines do not establish the new
paper condition's behaviour. The next paper-specific engineering check is the
protocol's no-call rich/simple prompt and adapter proof.
