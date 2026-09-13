# Software architecture and reconstruction

Updated: 2026-09-13. This document owns software interfaces, worked
examples and the reconstruction boundaries. The
[programme and reconstruction plan](../plans/ACTIVE_ROADMAP.md) owns priorities,
sequencing and the DSPy/GEPA investigation. Source and tests own implemented
behaviour; the retained implementation reference below remains separately scoped.
The [11 September advisory review](architecture_review_2026-09-11.md) analyses an
earlier snapshot and remains historical advice, not an implementation claim.

Status: the selected Gan, ExECT and longitudinal reconstruction is implemented.
Shared immutable artifacts now have request-aware SQLite persistence and offline
replay. Required old package code has moved to the functional owners below;
L1–L7/L9/L10 removals are applied and L8 remains. R5 is research-paper tables,
with full implementation deferred. See the
[migration record](../research/maintenance/repository_migration_2026-09-08.md)
for verification, exact moves, preserved evidence and local-path exceptions.

## Reconstruction destinations after the legacy-support decision

Keep required behavior, move it to the owner of that behavior, and delete obsolete
code after callers migrate and verification passes. Do not preserve entire old
packages merely because some functions are still used. Retain one Python package
and one frontend. These are current owners within `src/clinical_extraction/`.

| Responsibility currently mixed into old packages | Destination and boundary |
| --- | --- |
| Source identity, evidence references, rendered requests, attempts, artifacts, persistence/resume and provider construction | `core/`: shared mechanics without Gan/ExECT categories or historical paper-phase enums. Research-paper tables must be able to extend evidence locations without adopting epilepsy types. |
| Gan saved-response hydration, benchmark evaluation/replay, result readers and Gan-specific comparisons from `paper/` and `trace_explorer/` | `tasks/seizure_frequency/gan2026/evaluation/`. Retain existing prompt/parser, deterministic and scoring owners where they are already correctly placed; move only the misplaced responsibilities. |
| ExECT saved-response hydration, benchmark evaluation/replay, result readers and ExECT-specific comparisons from those packages | `tasks/epilepsy_phenotyping/exectv2/evaluation/`, with the existing task-owned scorers and projections preserved. |
| Shared comparison records, metric reporting and saved-run comparison mechanics | `evaluation/`, restricted to behavior actually shared by both benchmarks. Historical five-cell meanings, rosters and method aliases remain benchmark-specific adapters or study configuration, not universal evaluation requirements. |
| HTTP API, artifact inspection, review persistence and frontend presentation adapters | `inspection/`, replacing the retained portion of `trace_explorer/`. It consumes evaluation/artifact records; evaluation must not import frontend serializers or API internals. Preserve existing user workflows and review data while rebinding callers. |
| Supported command dispatch | `operational/`: one `clinical-extract` command with distinct operations for extraction, evaluation, replay and inspection. Retain `run.py`, its flat-flag adapter and `requirements.txt` for the no-install workflow. Move implementation behind commands before retiring task-specific launchers. |
| Publication-specific figures and build entry points | `scripts/publications/`, reading reviewed results. Reusable benchmark calculations stay with evaluation; issued manuscript files remain in `publications/dissertation/`. |
| Closed-study launch presets and duplicate loops, classes, aliases and import facades | Remove from the supported runtime once the approved replacement works. Preserve historically necessary source in Git or its study archive; do not leave an executable duplicate in the active package. |

ExECT replay hydration now lives in task-owned `evaluation/review_records.py`.
Inspection consumes these records; evaluation no longer imports the inspection
package. Saved five-cell and historical registry meanings live explicitly under
`evaluation/letter_benchmarks/`, outside the task-neutral core.

Completion requires supported workflows to use these owners, old namespaces to
have no remaining runtime consumers, unchanged saved evidence, replay parity,
request-aware persistence/resume, and the roadmap's package, public-checkout,
backend, frontend and documentation checks. Existing guards and failure accounting
must move with each supported operation. Full research-paper table extraction
remains deferred. No further compatibility approval is required for the agreed
L1–L7/L9/L10 scope; L8 must remain supported.

## Design question and decisions

Can a declared extraction task retain source-supported information so that a
different question can reuse it without inheriting a benchmark's final answer
format? The first software test is smaller: can one existing extraction request
be prepared and consumed through explicit interfaces without changing its prompt,
raw response or compatibility output?

Working design decisions:

1. Retain assertions within a declared capture scope. Do not promise extraction
   of all clinical facts or assume a new question's required fields were captured.
2. Keep original sources, model responses and assertions separate from later
   normalisation, linking, review and answers. Each interpretation records its
   inputs and owner; it does not overwrite the source account.
3. Use ordinary Python composition and domain-owned payload types. Shared code
   handles identity, provenance, evidence locations and execution status. It must
   not contain a universal epilepsy/study enum or benchmark selection policy.
4. A logical responsibility need not be a separate model call. The paper's
   one-shot condition remains one inference attempt; any retry is explicit.
5. Keep evidence location, semantic support, completeness and decision correctness
   separately assessable. An exact quote can support the wrong assertion.
6. Add new interfaces beside existing routes. Preserve legacy outputs and scores
   through named adapters; changing capture semantics requires a new experiment.

These decisions govern the proposed slices. The exact clinical schema, primary
paper endpoint and different-domain pilot are not frozen by choosing interfaces.

## Prompt components and implementation order

Agreed on 2026-09-13: controlled prompt composition is the organising principle
for reconstruction. Use a small set of meaningful, versioned components rather
than an abstraction for every text fragment.

| Responsibility | Owner and boundary |
| --- | --- |
| Task definition | Input unit, clinical semantics, output schema, permitted values and task-specific scorer |
| Prompt composition | Instructions, examples, allowed-label presentation, evidence requirements and schema presentation; retain the final rendered request |
| Shared execution | Model invocation, raw-output capture, parsing, validation, provenance and evaluation orchestration |
| Optional processing | Rules, semantic repair, linking, history assembly and query selection; consume saved outputs and record their own changes and failures |

Task requirements and prompt presentation are distinct. Removing label text need
not change permitted answers or scoring. Removing an evidence instruction while
retaining a required evidence field is not removal of the entire evidence
requirement. Changing one selected frequency to seizure-type-specific frequencies
changes the task. Record component dependencies and reject or explicitly describe
incoherent combinations; schema experiments need a declared representation and
comparison procedure. Shared execution must not require a universal clinical
schema or scorer.

1. Prove Gan composition first: inventory the existing single-label request,
   reproduce its rendered bytes and saved-output evaluation, then demonstrate
   controlled substitutions with task and scorer fixed. Record component versions,
   rendered input, model/runtime settings, raw output and any repair separately.
2. Test reuse with ExECT's diagnoses, medications, investigations and
   seizure-type-specific frequencies. Keep domain types and scoring adapters
   task-owned; the shared runner must not accumulate ExECT-specific branches.
3. Connect longitudinal extraction to explicit temporal/linking/query stages.
   Preserve input cutoffs and query conditioning. Existing saved outputs do not
   prove query-independent per-letter extraction.
4. Migrate other methods incrementally after these consumers establish the
   boundaries. Preserve saved bytes, identifiers and replay behaviour.

The Gan dependency inventory selected `gan_llm_extract` as the only supported
profile for the first slice. The ExECT artifact design below is implemented as
the second slice. New experiments, clinical schema changes and broad migrations
remain separately scoped.

## Three worked examples

### A. One letter, several supported facts

Use this fictional sentence-level fixture for the ExECT reuse slice:

> Diagnosis: focal epilepsy. MRI brain normal. Levetiracetam 500 mg twice daily.
> She has two seizures per month.

The current `exect_llm_extract` request captures diagnosis, investigation,
medication and seizure-frequency events. Preserve each event's own text,
attributes and quote; do not flatten it into a single patient phenotype. An
existing benchmark adapter can create ExECT mentions for its scorer. A later
consumer can display medication evidence without requiring a benchmark score.
Neither consumer should edit the retained event record.

For compatibility, use the existing Compact domain type initially. This does
not establish that its flat attributes are the right clinical schema for the
new paper. For example, a medication mention without supported initiation or
exposure dates cannot answer a treatment-start question; emit an explicit
coverage limitation rather than inventing dates or returning a negative.

The software acceptance result is unchanged request/response and traceable
projection. Scientific success would additionally require reference annotations
for the extracted facts and evidence. A correct final Gan category or ExECT
inventory score cannot establish all of that. The paper protocol will decide
the precise extraction scope and its primary endpoint independently.

### B. The same patient, different information cutoffs and questions

Use [authored patient 001](../../examples/longitudinal/authored_patient_001/README.md),
an existing fictional development case. L1 describes daytime staring spells and
morning jerks as epileptic, proposes lamotrigine and requests an EEG. L2 later
reinterprets those same staring spells as non-epileptic and confirms lamotrigine
was never taken. Its consultation date is 20 June; availability is 10 July.

At T1 (15 January), the visit account admits L1 only. Q2 supports at least two
overlapping epileptic patterns; Q3 is indeterminate about actual lamotrigine
initiation. With the retrospective cutoff of 14 July, L2 is admitted: Q2 becomes
ineligible and Q3 becomes ineligible. Preserve the original assertions, L2's
new assertions and the supported correction link. The June decision itself
does not become a January decision. The
[task definition](../longitudinal/task_definition.md) owns the exact predicates.

This example distinguishes two reuse tests. Q2 and Q3 at one permitted input
set can consume the same frozen assertion batch. Moving from visit to
retrospective view admits additional evidence and can require a different
extraction batch; it is not merely a filter over a batch produced with future
knowledge. Persist each batch's actual input documents and query conditioning.
The current saved extractions saw query context, so they do not prove independent
per-letter extraction. A future inference or replay must exclude unavailable
documents before the model runs.

The current longitudinal schema has richer identity and time fields than Compact.
Do not convert legacy Compact output to that schema by filling missing values
from the reference annotations. Reuse requires an explicit partial mapping, with
missing capabilities reported, or a separately evaluated new extraction profile.

### C. Research-paper tables with alternative time-point policies

Conor selected research-paper tables for R5 on 2026-09-13. Full implementation is
deferred while reconstruction prepares the source and evidence foundations. This
example remains a fictional design fixture, not a real study result or a selected
source corpus. A fictional trial report states that 12 of 100 intervention
participants and 20 of 100 comparator participants had the defined outcome at
six months. A companion report gives twelve-month counts for only 80 and 85
participants, with a table footnote explaining its analysis population.

Retain each result with study/report identity, arm, population, outcome, time
point, numerator, denominator and evidence for the table cell, headers and
footnote. A six-month policy selects the first result; a twelve-month policy
selects the second and exposes its population. Neither substitutes the first
denominator into the second estimate. An uncertain same-study link remains
uncertain rather than deduplicating by similar title.

The shared responsibilities are document versions, assertion identity, multiple
evidence references and recorded policy choices. Study population identity,
outcome definitions and analysis time belong to the study domain. Whether a
source entails the result is separate from study quality and evidence certainty;
neither establishes a clinical recommendation.

The user-supplied NICE/SIGN discussion brief motivates this candidate, especially
its evidence-workbench example. It is an independent discussion brief, not
organisational authorisation. Its local PDF remains outside the repository.
The selection does not commit to a guideline workflow or an evidence-quality
assessment product. Exact source documents, reference and reviewer remain open.

Foundation requirements for the next reconstruction steps:

- Preserve original document bytes by identity and distinguish each derived text
  or table view by version and ingestion provenance.
- Keep current text-span evidence working. Permit a later explicitly typed table
  locator with table/cell identity and links to supporting headers and footnotes;
  do not pretend a flattened text offset establishes a cell's structural meaning.
- Keep multiple evidence references per assertion. Study/report identity, arm,
  population, outcome, unit, numerator, denominator and time point remain task-owned.
- Reuse immutable extraction, attempt and lifecycle records for downstream policies.
  Missing fields or ambiguous header/footnote associations remain explicit.

These are design requirements, not implemented table support. Current
`SourceDocument` and `EvidenceRef` use a text view and character offsets. A concrete
table adapter, parser/OCR, dataset and complete extraction workflow are deferred;
the current reconstruction should not introduce an untested universal table schema.

## Proposed interfaces and ownership

These names now identify the implemented records in `core/artifacts.py`. Only the
subset exercised by the current slices exists; add further locator or domain
types with a working consumer.

| Object | Minimum responsibility | Boundary |
| --- | --- | --- |
| `SourceDocument` | Stable source ID, immutable version/content hash, exact text view and its hash | No gold labels. Visit/event/availability times remain explicitly supplied domain metadata. No silent whitespace or Unicode rewriting. |
| `EvidenceRef` | Source version and text-view hash, exact quote and zero-based character range with exclusive end, location status | Implemented support is text only. Research-paper tables are the selected next locator requirement; its concrete adapter is deferred. Multiple references can jointly support one assertion. |
| `ExtractionArtifact[T]` | Artifact ID, schema/profile/request identity, input source references, original response reference, typed domain output and separate diagnostics | No mandatory selected answer; `T` is initially the retained Compact record, not an arbitrary universal fact dictionary. |
| `Assertion[T]` | Artifact-scoped assertion ID, typed content, evidence references and production provenance | Future domain records can retain certainty, reporter and event time. An assertion ID is not a real-world event ID. Existing IDs survive adapters. |
| `Relationship` | Typed domain relation between assertion IDs, supporting evidence and derivation/version | Recency or equal names alone do not establish correction or identity. Unresolved relations remain explicit. |
| `DecisionRecord[T]` | Policy/version, request parameters/cutoff, input artifact IDs, result and supporting/unresolved predicates | Does not mutate assertions. Clinical indeterminacy is distinct from execution failure or unsupported input schema. |
| `CoverageRecord` | Declared capture families, processed/failed source parts and known unsupported fields | Processing success is not exhaustive recall. Clinical absence and complete-history claims require their own source-supported assertions. |

Use a small sequence of callable operations: prepare a request; execute one
attempt; decode the response; apply named compatibility normalisation; validate
evidence; link where needed; evaluate a policy; score against a separate reference.
Each operation returns an inspectable result. Domain selection and scoring must
be callable from saved artifacts without a live model or global DSPy settings.

An extraction profile owns capture scope, payload schema, prompt components and
their versions. A policy declares which fields, relation types and source coverage
it requires. An execution configuration owns the provider, model revision,
generation settings and retry limits. An evaluation configuration owns datasets,
references, metrics and split permissions. A profile may reference the others;
it must not silently infer them from a method name or a mutable global variable.

### Prompt components and DSPy

Keep capture instructions, domain vocabulary, schema descriptions and examples
individually named in the extraction profile. Final benchmark label forms and
selection policies belong to their adapters/decision profiles when they constrain
the requested answer. Legacy prompts that combine these remain versioned legacy
profiles; structural refactoring must not silently change their meaning.

Record the final ordered messages as well as component hashes. Preserve rendering
order, whitespace and adapter formatting during the compatibility slice. Merely
moving strings into separate files is insufficient: tests must show which parts
enter the model request and that changing a downstream policy does not change
the extraction request. A new simplified prompt is a later experiment.

DSPy implements the existing model-call adapter. Its signatures should expose the
real module responsibility; clinical facts and downstream decisions remain typed
Python data outside DSPy. The first slice retains the existing signature because
changing it changes the rendered request. Provider routing now lives in
`core/dspy_runtime.py`; the historical Gan import is a compatibility wrapper and
provider payload tests pin the move. GEPA, multi-agent extraction and additional
verification calls are excluded from this slice.

### Identity, uncertainty and failures

Hash the actual model-visible text separately from original source bytes when
ingestion transforms them. Evidence offsets refer to that specific text view.
Changing source text invalidates a saved-request match; re-extraction or an
explicit mapping creates a new artifact. A matching response-text hash alone is
not proof that the model saw the same input or used the same runtime settings.

Keep original evidence even if it is wrong. If supplied offsets select the exact
quote in the correct version, accept that location; otherwise a unique exact
match may propose a recorded location correction. Repeated matches without
disambiguating evidence are ambiguous, not silently the first occurrence.
Location validity and clinical support have separate statuses; no automatic
clinical-support verdict is introduced here.

Retain each failed inference attempt, original response and retry separately.
Provider failure, invalid JSON, unsupported schema and unresolved evidence are
not a valid empty clinical record. Conversely, a valid empty result does not
mean a documented negative. Policy consumers must distinguish insufficient
capture capability from clinical uncertainty and execution failure. A review
correction creates a revision with reviewer identity and reason.

## Second implementation slice: explicit ExECT extraction artifact

### Why this route

Use `exect_llm_extract` explicitly, not an alias or the default operational method.
It returns four-family events without requiring Gan's `selection.final_label`.
`build_prompt_input(letter, prompt_version=...)` already permits explicit prompt
selection and `DspyKeyEntitiesStructuredExtractor.render_messages` already renders
without a call. `ExectLetter` accepts text with no annotations; the new source
adapter must construct it only at the legacy boundary, never load a benchmark.

Gan's preceding `run_gan_artifact_notes` path accepts ordinary source documents
without constructing benchmark gold. This ExECT slice tests whether the same
source/request/artifact lifecycle also supports four task-owned clinical families.

### Dependency findings that determine the slice

| Inspected code | Present behaviour | Required treatment |
| --- | --- | --- |
| `operational/exect.py::run_exect_notes` | Default is `llm_with_rules`; creates a runner and configures DSPy | Preserve the public default. Add an explicitly selected extraction-artifact entry point only after its library path works. |
| `orchestration/structured_one_call.py::produce_structured_letter` | Builds prompt, calls/replays, parses/retries, maps mentions and projects evidence/attributes | Do not reuse the whole function as a supposedly raw extractor. Isolate request/attempt/parsed-event steps and leave clinical projection in the existing wrapper. |
| `key_entities_structured/constants.py` | Mutable `PROMPT_VERSION` selected through `set_active_prompt_version` | New path takes an explicit immutable profile. Legacy wrappers may preserve their current default; test that interleaving explicit profiles cannot contaminate requests. |
| `key_entities_structured/parsing.py` | Repairs JSON, coerces values/aliases, drops unknown event families and normalises attributes | Retain raw JSON tree and original event positions before this transformation. Treat the parsed record as a derived compatibility output; record dropped/changed fields rather than calling it raw model output. |
| `key_entities_structured/records.py` | Compact fields and an attribute dictionary; extra fields ignored | Keep for compatibility. Preserve ignored fields in the raw response/tree. Do not claim a complete, lossless typed clinical record. |
| `key_entities_structured/projection.py` | Evidence replacement/checking, attribute repair, safety filtering and CUI projection | Keep outside the extraction artifact's original assertions; attach derived results with existing provenance. No clinical projection becomes an unreported one-shot repair. |
| `core/evidence.py` and `longitudinal/evidence.py` | Different matching/repair policies, with longitudinal unique-exact-offset handling | Preserve old routes. New evidence locations use explicit versioned text and ambiguity handling, not a global change to existing match rules. |

These names are relative to the current ExECT package unless prefixed otherwise.
The compatibility producer and its public runners remain responsible for their
current historical outputs. The new path must be independently useful without
calling scoring, clinical projection or a corpus loader.

### Concrete change boundary

Implemented files and boundaries:

- `core/artifacts.py`: source identity, text evidence locations and a minimal
  generic extraction-artifact envelope, including immutable nested records and
  lifecycle manifests. No clinical enums, scorer imports, provider credentials
  or source-loading side effects.
- `core/dspy_runtime.py`: shared provider construction and inspectable non-secret
  environment controls. Gan's `llm_config.py` delegates through a compatibility
  wrapper; ExECT no longer imports a Gan package.
- `tasks/seizure_frequency/gan2026/llm/extraction.py`: the selected
  `gan_llm_extract` profile, controlled prompt composition, exact rendering,
  one-attempt execution, strict replay and a named legacy projection.
- `tasks/epilepsy_phenotyping/exectv2/llm/extraction.py`: explicit profile/request
  preparation and response consumption using the retained builder, signature and
  Compact parser through a named legacy adapter. Distinguish raw decode from
  compatibility normalisation. An injected completion callable returns the
  original response/attempt metadata; replay requires the matching request identity.
- Existing `orchestration/structured_one_call.py`: retains its clinical projection,
  legacy stage IDs and outputs. The additive path records its own raw-to-
  compatibility-to-projected-mention positions and projection warnings.
- `longitudinal/artifacts.py`: adapts existing per-letter assertions and links to
  immutable artifacts and decision records. Source date metadata is identity-bound
  and rechecked before a policy runs.
- Existing focused ExECT tests plus `tests/test_extraction_artifacts.py`: extend
  and narrow the checks that already own
  no-call replay, prompt identity and projection ownership. Add only new
  source-version/ambiguity obligations that lack existing coverage, following
  always-on test admission. Do not create a mirror suite for every helper.

First prove the library path with fictional fixtures and saved development output.
A CLI addition is a second change within this slice only if the library result is
complete and a distinct output format is useful; never replace the existing
`prediction.mentions` response with an artifact silently. No frontend, package-wide
benchmark scorer, longitudinal schema or artifact relocation was needed. No new
schema was sent to a model in the compatibility slice.

Execution order: baseline the permitted request and response; introduce the
source/request interface; retain and consume the original response; add separate
evidence diagnostics; verify the compatibility wrapper; only then expose the new
artifact to another caller. Each step can be reverted by removing the new caller
and restoring the old delegation, with source/raw bytes untouched.

### Acceptance checks and completion boundary

| Obligation | Concrete check |
| --- | --- |
| Request parity | Same explicit `exect_llm_extract` profile and text produce byte-identical payload and rendered messages before/after. Different IDs do not inject research metadata into model text. |
| Task isolation | Alternate extract and extract-and-select request preparation; results equal independently prepared baselines, with no global profile mutation required. |
| No hidden runtime dependency | Preparing/consuming an ordinary source requires no gold fields, corpus files, credentials or network. Replay completion callable fails the check if invoked. |
| Provenance and failure | Exact source/request mismatch refuses replay. Invalid JSON and failed capture remain failed attempts; they never become an empty successful record. |
| No loss disguised as parsing | A two-event response with an unknown family preserves both raw events and their positions; the retained compatibility parser may still yield one, with that drop explicitly recorded. Attribute coercion and ignored fields remain traceable. |
| Evidence identity | Repeated quotes without offsets remain ambiguous; exact disambiguating offsets work; changed text versions do not inherit previous locations. No model event disappears merely because its evidence check fails. |
| Compatibility | Existing selected development replay and public runner/projection tests retain their outputs, stage ownership and denominators. Compare a baseline captured from this working tree, not an assumed clean historical state. |
| Independent downstream consumption | Read the extraction artifact without invoking CUI projection, scoring or another model. A read-only family display must leave original artifact hashes unchanged. This is a software reuse check, not clinical eligibility validation. |

During implementation run focused ExECT and operational tests, then repository
always-on pytest, Ruff and mypy before claiming the slice complete. Reuse the
existing replay/identity checks in `tests/test_exectv2_llm_vertical_slice.py`,
`tests/test_exectv2_llm_pre_post_vertical_slice.py`,
`tests/test_exectv2_llm_only_prompt_contract.py` and
`tests/test_operational_cli.py`. Any required historical fixture that is missing
must be reported; do not fabricate a replacement oracle. Capture known unrelated
failures separately. Full-suite completion is not implied by this specification.

Completion means one usable extraction-artifact path with preserved legacy
behaviour. It does not mean a new reusable clinical schema, validated extraction,
query-independent model behaviour, a hospital-ready service or a completed paper.
After Gan composition and ExECT reuse, the longitudinal slice tests two clinically
meaningful policies once capture coverage is adequate; the different-domain slice
follows candidate selection.

Implementation acceptance on 2026-09-13 covers this bounded path. Default Gan and
ExECT prompt payloads and rendered messages match their legacy builders. Controlled
Gan component substitution changes the request, while inconsistent overlapping
evidence components are rejected. Replay requires the exact request; unsupported
ExECT shapes fail while an explicit empty event list succeeds. Raw unknown events,
ignored fields and event positions remain inspectable, and projected mentions
carry ambiguity-safe raw origins and warnings. The task-owned ExECT scorer runs
from the artifact without entering `core/`.

The longitudinal adapter identity includes source text and availability/visit
metadata. It rejects changed documents, excludes later sources in cutoff-limited
captures, and serves Q2 and Q3 visit/retrospective decisions from one frozen,
query-independent authored artifact without changing its hash. It refuses the
existing query-conditioned outputs as general reusable captures. This is software
reuse over provisional synthetic/reference records, not clinical validation.

## Decisions now resolved and questions left open

Resolved for implementation planning: Gan composition is first; ExECT inventory
is the second route. For the retained ExECT design, its
profile is explicit; raw response precedes compatibility normalisation; original
assertions survive evidence failure; source identity is versioned; DSPy remains
the existing call adapter; the first change is additive and library-first.

Questions that do not block this compatibility slice:

- Conor must choose the paper's scored unit and primary endpoint: benchmark
  answer agreement, fact inventory, or independently annotated evidence-supported
  assertions. These require different references and cannot be one hidden metric.
- Conor and reviewers must define the useful local-model capability threshold
  and acceptable error/cost tradeoffs before model selection or new comparisons.
- The broader epilepsy profile must decide which burden, time, medication and
  uncertainty fields are necessary for named downstream questions. Preserve the
  current schema until a separately versioned replacement is justified.
- Research-paper tables are selected for the different-domain pilot. Its concrete
  question, accessible sources and review/reference ownership remain deferred.
  The fictional study example is only a design test.
- Historical GEPA score/replay provenance must be reconciled before citing that
  experiment as a comparative result, but it does not block source/artifact design.

## Evidence for this specification

Read-only feasibility check on 2026-09-11, in the repository `.venv`, used the
fictional text in Example A. Explicit `exect_llm_extract` preparation produced
identical payloads for source IDs `design-a` and `design-b`, rendered system/user
messages without a model call, and had 17,747 payload characters. Its UTF-8 payload
SHA-256 was `97ddce91662f85b438684ede1540688d88efe631a92de58a29f287fac0058662`.
This pins the inspected builder's output, not a future profile's acceptance hash.

A second read-only probe passed two hand-written events (diagnosis and an
`outside_scope` family) to the retained parser. It returned one event with
`dropped_unknown_event_family` diagnostics. This substantiates the need to retain
raw events separately; it is not model accuracy evidence. No prompt, schema,
source record, saved prediction or runtime code changed during these checks.

The plain-language prompt audit applies to any future prompt revision. This
specification inspected the current rendered request's structure and retained
its wording; it does not certify a new prompt or claim that all inherited
instructions have been simplified.

The initial additive slice had two known test failures. The completed migration
repairs both: generated teaching documentation is current, and the inventory
expectation includes the six already-present encode-select cells. No saved result
was changed to satisfy a test. Final commands and outcomes belong to the migration
record, including installed-wheel/public-checkout and browser checks.

`core/artifact_store.py` validates serialized request, response and artifact hashes,
stores immutable captures and append-only execution revisions, and refuses replay
under changed request/runtime/program identity. Failed attempts remain visible;
retry is explicit. It is a local sequential batch store, not a distributed job
scheduler or a guarantee of exactly-once provider execution across concurrent jobs.
`operational/extraction.py` uses task-owned prepare/execute/projection adapters;
longitudinal loading restores typed domain content through a decoder callback.

## Retained implementation reference

The package separates shared extraction code from task-specific clinical logic.

## Package ownership

`clinical_extraction.core` contains code shared across tasks:

- pipeline interfaces and result objects;
- evidence-span utilities;
- validation and repair results;
- shared schema base models.

`clinical_extraction.tasks` contains dataset and task implementations. Each task
owns its loader, schemas, label rules, deterministic components, model programs,
scorers, and error analysis.

The implementation keeps these decisions separate:

- loading and scoring;
- extracting events and selecting the final clinical answer;
- normalizing labels and mapping them to metrics;
- checking evidence and judging clinical correctness;
- choosing a model and choosing a prompt;
- saved outputs and package source;
- general, clinical, dataset-specific, and benchmark-format rules.

Record the model and route in every run. Use
[component attribution](component_evidence_attribution_architecture.md) when a
study compares methods or changes a selected result.

## ExECT clinical findings

Current ExECT code combines extracted findings before scoring them:

- `ClinicalFinding` stores one clinical assertion, its attributes, evidence,
  source, and change history.
- `ClinicalFindingStore` collects findings for one letter.
- `CandidateProducer` proposes findings, including adapters that replay saved
  JSONL outputs.
- `EntityLens` is the retained code name for entity-specific reconciliation.
  In prose, call it a diagnosis, seizure-frequency, prescription, or
  investigation transform.
- `FindingView` formats the final findings for each score.
- `AttributionSidecar` is the retained code name for records that identify the
  producer, deterministic changes, evidence status, and score-specific output.

The first saved implementation,
`exectv2_holistic_finding_assembly_v01_dev140`, replays development outputs
through these objects without changing behavior. Its identifier remains only
for saved-evidence compatibility.

## Final ExECT LLM-with-rules ownership

The final model comparison is model-led at the input to each main family:

| Family | Model supplies | Deterministic code may do | Deterministic code must not do |
| --- | --- | --- | --- |
| Diagnosis | Concepts, assertions, and evidence | Normalize and apply recorded heading, boundary, and residual recovery | Substitute a rules-only diagnosis result |
| Seizure Frequency | Structured frequency facts and evidence | Project model-selected operands and suppress unsupported states | Union an independent deterministic extractor into the answer |
| Prescription | Medication regimen facts and evidence | Normalize, split supported regimens, remove unsupported facts, and apply bounded repair | Substitute the deterministic all-entity or Prescription extractor |
| Investigations | Findings and evidence | Validate, normalize, and deduplicate | Substitute an independent deterministic extractor |

Rules that change a clinical fact remain prediction owners and make that fact
hybrid. The attribution record must preserve those changes instead of crediting
the final result entirely to the model. See
[decision 0040](../history/decisions/0040-final-exect-llm-with-rules-family-ownership.md).

## Deterministic rule groups

- `general`: dates, durations, intervals, sections, and evidence checks;
- `clinical_epilepsy`: seizure terminology and epilepsy-note conventions;
- `seizure_frequency`: rates, clusters, seizure-free duration, and temporal selection;
- `gan2026_specific`: Gan synthetic-letter patterns and data quirks;
- `benchmark_format`: Gan label formatting that does not change clinical meaning.

Each group must be testable and, where practical, removable for comparison.

## Deliberate exclusions

The retained benchmark implementation did not require dataset-independent prompt
abstractions. The current programme tests reusable task and prompt boundaries on
bounded slices before consolidating them. A generic workflow engine, fully
pluggable registry or support for every epilepsy dataset remains unjustified
unless demonstrated needs require it.
