# Pipeline understandability and architecture recovery review

Date: 2026-07-30  
Status: review document; no implementation decision  
Repository state inspected: `main` through `5340ff5`  
Scope: the two-task, three-method clinical extraction research system

## Purpose

After nearly a month away from the project, the pipeline has become difficult
to reconstruct from memory. The immediate problem is not simply that the
repository is large. The project is now easier to verify than to understand:
it contains strong tests, retained evidence, explicit provenance, operational
packaging, and extensive experiment history, but it does not expose one
authoritative, teachable account of how a record moves through each selected
method.

This review assesses the current explanatory and architectural state. It
proposes a documentation-first recovery programme aligned to the following
priority order:

1. make the system easily understandable and explainable;
2. make it easy to write about accurately in the paper; and
3. preserve or improve results only after the first two conditions are met.

This document does not authorize model calls, locked-row inspection, scorer
changes, pipeline changes, or refactoring of frozen evidence paths.

## Executive conclusion

The project does not appear to have a fundamentally failed architecture. It
looks like a good research programme whose clinical core is obscured by three
systems living together:

1. the clinical extraction algorithms;
2. the research laboratory, including experiments, ablations, scorers,
   retained evidence, replay, and provenance; and
3. the operational product, including endpoint handling, retry, resume,
   handoff packaging, and the trace interface.

The main dissertation risk is now explanatory coherence. Several different
execution paths, historical and current variants, and neutral-sounding
abstractions make it difficult to state exactly who changes clinical meaning
at each stage. Some maintained explanatory material is materially shallower
than the selected implementation, and at least one handwritten teaching trace
misstates prediction ownership.

The recommended response is a short architecture-recovery sprint before broad
refactoring or further result optimization. It should establish an executable
stage model, two generated teaching cases, six method cards, and paper-facing
diagrams. Only then should the code be refactored where the explanation exposes
a genuine abstraction problem.

## The smallest truthful mental model

There are two tasks:

- **Gan 2026:** turn a letter into one current seizure-frequency answer.
- **ExECTv2:** turn a letter into multiple findings across four main clinical
  families: Diagnosis, Seizure Frequency, Prescription, and Investigations.

Each task has three research methods:

| Method | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Rules only | Rules find candidate events, normalize them, select one answer, and format it for scoring. | Nine deterministic entity extractors produce findings, followed by de-duplication and scoring. |
| LLM only | One model call directly produces the final label and evidence; code parses, adapts, checks, and scores it. | A GEPA-optimized program produces de-duplicated four-family facts; an adapter maps them into ExECT representations and applies evidence/schema checks. |
| LLM with rules | The model extracts an event history **and makes an initial selection**; deterministic code may normalize or correct the final label. | One model call proposes findings for four families; family-specific deterministic transforms may normalize, add, remove, project, or suppress findings before evidence checking and scoring. |

Two anchor explanations should govern all longer descriptions:

> **Gan hybrid:** the model extracts the event history and chooses an answer;
> deterministic rules then check and sometimes correct that answer.

> **ExECT hybrid:** the model proposes findings for four families;
> deterministic family transforms reconcile those findings into the final
> scored representation.

Every diagram, trace, paper paragraph, and code map should preserve these
ownership statements.

## Current method map

### Gan rules only

The retained runner calls explicit stages:

1. extract raw candidates and candidate events;
2. normalize candidate events;
3. select and render the final event;
4. validate the selected evidence and clinical trace; and
5. project the final value into Purist and Pragmatic scoring.

The clearest current entry point is
`src/clinical_extraction/tasks/seizure_frequency/gan2026/runners/deterministic_canonical.py`.

### Gan LLM only

The model receives a detailed rule taxonomy in the prompt and returns a final
label, evidence, answer kind, selected seizure type, time window, confidence,
and rationale. The downstream code then:

1. repairs JSON dialect or schema shape;
2. validates the structured decision;
3. calls `repair_prediction_label_with_evidence`;
4. validates that the label is scorable;
5. checks evidence containment; and
6. calculates Purist and Pragmatic results.

The selected implementation describes itself as LLM-only because the model
owns the clinical decision. However, the post-model evidence-based label repair
can change the final label. Its exact boundary must be demonstrated rather than
summarized as mere formatting.

Primary implementation:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_canonical_pipeline.py`.

### Gan LLM with rules

The model returns two linked objects:

- an event ledger containing source-near seizure-frequency facts; and
- a selection containing `selected_event_ids`, `final_kind`, `final_label`,
  evidence, confidence, and rationale.

The selected code then performs:

1. JSON dialect repair;
2. structural/schema repair and validation;
3. normalization of every event;
4. resolution of an initial label from the model selection;
5. evidence-based label repair;
6. monthly-diary repair;
7. usual-interval repair;
8. breakthrough repair;
9. non-epileptic-event repair;
10. residual-jerk repair;
11. post-change-burst repair;
12. dated-sequence repair;
13. elapsed-anchor repair;
14. final scorable-label validation;
15. exact-evidence checking; and
16. Purist and Pragmatic scoring.

Primary implementation:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`.

The critical ownership point is that the model makes the initial event
selection. Deterministic code can subsequently change its rendered clinical
answer through named repair families.

### ExECT rules only

The deterministic all-nine baseline runs entity-specific extractors for
Diagnosis, Investigations, Onset, When Diagnosed, Birth History, Epilepsy
Cause, Patient History, Prescription, and Seizure Frequency. It combines and
de-duplicates the mentions before scoring.

Primary implementation:
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/orchestrator.py`.

This baseline covers nine entities, while the main model-led comparison focuses
on four. The difference must remain visible whenever scores are compared.

### ExECT LLM only

The retained GEPA program emits de-duplicated clinical facts for four families.
The adapter:

1. extracts and repairs the JSON payload;
2. coerces supported fact families;
3. drops malformed facts or facts without evidence;
4. maps each fact into an ExECT mention and attribute representation;
5. validates evidence and schema gates; and
6. passes the resulting predictions to scoring.

The adapter explicitly claims not to add or merge clinical facts, but it does
normalize representation fields such as negation, dose units, medication
frequency, modality, investigation state, and seizure-frequency state.

Primary implementation:
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py`.

### ExECT LLM with rules: current one-call architecture

The current selected model-comparison architecture makes one structured model
call per letter. The named model supplies candidates for Diagnosis, Seizure
Frequency, Prescription, and Investigations. The main stages are:

1. build the four-family prompt and call the model;
2. parse and, when eligible, perform format-only retry;
3. flatten model events into ExECT mentions;
4. project model-produced Seizure Frequency facts into the required state
   representation;
5. suppress narrowly defined unsupported unknown states;
6. register raw and scored findings in the finding store;
7. apply the family transform selected for each of the four entities;
8. preserve model origin and every deterministic action;
9. require exact evidence for every final finding; and
10. materialize the named score views for evaluation.

The family transforms have different behaviours:

- Diagnosis may rewrite, drop, or add concepts through heading recovery and the
  standard dictionary;
- Seizure Frequency uses projection and suppression before a thin assembly
  transform;
- Prescription applies dictionary-driven regimen processing and bounded
  correction;
- Investigations validates, normalizes, and de-duplicates findings.

Primary operational implementation:
`src/clinical_extraction/operational/exect.py`.

The public, readable wrapper is
the now-retired parallel handoff wrapper.

## Principal findings

### 1. There is no single canonical execution path

Gan hybrid has several closely related entry points:

- a research single-record runner;
- a research split runner;
- the operational/supervisor pipeline;
- saved-output replay paths; and
- trace-explorer projections.

These paths do not have identical retry, tracing, and failure behaviour.
Consequently, “where does the pipeline run?” has several defensible answers.
ExECT has the same division between experimental runners, saved-output
assembly, the operational wrapper, and the historical `v08` architecture.

A selected method needs one prediction-bearing core orchestrator. Research and
operational entry points should delegate to it rather than partially restating
its processing order.

### 2. Historical and current architectures share the same names

The paper-facing six-cell reference matrix retains historical ExECT `v08` as
its LLM-with-rules result. `v08` predates the adopted family-ownership rule:
Prescription is deterministic-only and Seizure Frequency includes an
independent extractor union.

The current one-call ExECT architecture is what produced the fixed six-model
panel. Both can appear under “LLM with rules,” despite having materially
different ownership. Therefore the reader is not really learning only six
architectures. They are learning six comparison cells plus current replacements
and historical controls.

Current and historical methods need visibly different roles:

- current selected method;
- historical performance control;
- rejected candidate or ablation; and
- operational wrapper.

A version identifier alone is insufficient explanation.

### 3. Maintained explanations are too compressed

`docs/canon/02_pipeline_steps.md` describes each task in approximately four
arrows. That is useful as an abstract, but it skips most of the stages a reader
must understand to explain ownership, improvement, regression, or evidence.

For example, the selected Gan hybrid implementation expands the phrase
“deterministic selection and normalization” into schema repair, event
normalization, label resolution, and nine ordered repair families. The current
canonical page therefore does not bridge the gap between a one-sentence summary
and the source code.

### 4. Neutral-sounding abstractions can conceal clinical changes

The terms `lens`, `normalization`, `projection`, `repair`, and `adapter` do not
reliably communicate their effect:

- a Diagnosis lens can rewrite, drop, and add findings;
- Seizure Frequency projection can create the scored state representation;
- unknown suppression removes model-produced findings;
- Gan repair can change the final clinical label; and
- Gan LLM-only still applies evidence-based label repair after the model call.

Every stage should explicitly declare whether it may change:

1. transport or schema only;
2. representation without changing clinical meaning;
3. clinical selection or meaning; or
4. benchmark/scorer projection only.

The declared category should be testable from traces.

### 5. The handwritten teaching fixture is not an authoritative trace

`src/clinical_extraction/trace_explorer/fixtures/syn_014.json` attributes Gan
current-event selection to a deterministic `gan-current-event-selector`. The
selected Gan hybrid contract actually asks the model to return
`selected_event_ids`, `final_kind`, and `final_label`. Deterministic code then
normalizes and may repair that initial selection.

This is a material prediction-ownership mismatch. It demonstrates why a rich
handwritten trace can be more misleading than a short generated trace.
Pedagogical examples should be produced by real stage hooks or validated
against them. A fixture may simplify payloads, but it must not invent ownership
or stage behaviour.

### 6. The active roadmap no longer matches the immediate project need

`docs/plans/ACTIVE_ROADMAP.md` is organized around closing evidence gaps while
keeping the verified pipeline fixed. That was an appropriate earlier goal. It
does not reflect the new primary objective of recovering understanding before
paper writing.

The roadmap also describes the frontend as outside retained deliverables while
the repository now includes substantial trace and review interfaces. The
current roadmap should not be treated as a sufficient guide to the next phase.

### 7. The main paper comparison needs conceptual review

The current manuscript juxtaposes:

- ExECT rules-only results covering all nine entities and paper-derived metric
  views;
- a four-family GEPA LLM-only development comparison; and
- historical `v08` LLM-with-rules results under an ownership pattern that is no
  longer selected.

The caveats are disclosed, but the comparison is difficult to explain as one
clean experiment. The project’s revised priorities suggest favouring current,
matched, scientifically coherent architectures even if this lowers a headline
number.

The paper should consider moving `v08` out of the main three-method row and
using the current one-call model-led architecture as the primary ExECT hybrid.
`v08` would then become historical evidence demonstrating why explicit
component ownership matters. The rules-only, LLM-only, and current hybrid
methods should be compared on the most closely matched four-family and scorer
view that can be reproduced without violating the data policy.

## Recommended architecture-recovery sprint

### Phase 1: Establish an authoritative stage manifest

Create one machine-readable stage manifest for each selected task-method pair.
Every stage must record:

- plain name;
- stable stage ID;
- input type and example;
- output type and example;
- operation summary;
- model, deterministic, or scorer owner;
- whether clinical meaning may change;
- exact implementation path and callable;
- governing test or characterization fixture;
- trace fields proving execution; and
- paper-facing wording.

The manifest should generate or validate diagrams and teaching traces. It
should not become a generic workflow engine.

### Phase 2: Build two executable teaching cases

Choose one synthetic or permitted development letter per task and run it
through all three methods. For every stage retain:

- source text;
- input object;
- plain-English operation;
- output object;
- before/after difference;
- selected and supporting evidence;
- prediction owner;
- code link;
- relevant test; and
- whether the stage changed correctness.

Each case should include one ordinary path. A second failure or repair case can
be added later. The first goal is a complete, trustworthy story rather than
coverage of every edge case.

### Phase 3: Produce layered explanations

For each of the six selected methods, create:

1. a one-sentence explanation;
2. a 60-second explanation;
3. a one-page method card;
4. a detailed stage walkthrough;
5. an executable trace; and
6. a direct code map.

A method should count as understood only when the author can explain it from
memory and reach every prediction-changing stage within two links.

The method card should answer five recall questions:

1. What enters?
2. Who first proposes the clinical answer?
3. Which later stages may change clinical meaning?
4. What final representation is scored?
5. What evidence shows whether each component helped or harmed?

### Phase 4: Create the paper-facing diagrams

Prefer several small diagrams to one complete repository diagram:

- one two-task × three-method overview;
- one detailed Gan hybrid stage diagram;
- one detailed ExECT hybrid stage diagram;
- one ownership matrix showing model, deterministic, validation, and scoring
  stages;
- one worked-example diagram per task; and
- one result-attribution view showing rescues and regressions.

Diagram nodes should be generated from or checked against the stage manifest.
No manually authored diagram should be allowed to disagree with runtime
ownership.

### Phase 5: Refactor only after characterization

Likely high-value refactoring targets are:

- one thin authoritative orchestrator per selected pipeline;
- explicit stage functions with typed inputs and outputs;
- research runners that delegate to the orchestrator;
- operational wrappers limited to endpoint and runtime concerns;
- historical and experimental variants outside the primary reading path;
- explicit naming of semantic versus format-only transformations; and
- removal of tracked temporary or generated noise from active source-search
  paths.

For Gan hybrid, the selected orchestrator should visibly read as:

```text
request
  -> parse
  -> validate schema
  -> normalize events
  -> retain model selection
  -> apply named deterministic corrections
  -> verify evidence
  -> score
```

For ExECT hybrid:

```text
request
  -> parse
  -> map model events
  -> apply seizure-frequency transform
  -> apply four family transforms
  -> require exact evidence
  -> materialize score views
  -> score
```

The existing internals may remain behind these stages initially. A façade that
truthfully exposes the selected flow can provide substantial explanatory value
without immediately rewriting validated logic.

## Refactoring safety requirements

Before moving prediction-bearing code:

1. freeze representative input/output characterization fixtures for every
   selected method;
2. retain raw model boundaries separately from deterministic outputs;
3. replay all six reference cells without model calls;
4. prove identical final predictions, evidence, component actions, and scores;
5. preserve split and locked-data restrictions;
6. produce a new recorded version only if a semantic output changes; and
7. avoid optimizing against locked holdout rows.

Refactoring is justified when it reduces the number of places that own pipeline
order or makes semantic ownership explicit. It is not justified merely to
reduce file count.

## Proposed definition of understandable

A selected method is sufficiently understandable when:

- its one-sentence and 60-second explanations are accurate;
- its stages fit on one readable page;
- every stage has one stable name across prose, diagrams, traces, and code;
- every prediction-changing stage has one declared owner;
- an executable teaching case shows before and after values;
- the implementation is reachable from the method card within two links;
- historical alternatives are visibly separate from the selected path;
- the paper can describe the method without relying on internal version codes;
  and
- the author can explain where a rescue or regression originated without
  reopening the entire repository.

## Recommended priority order

1. Correct mental model and executable teaching cases.
2. Paper-facing architecture, comparison boundary, and terminology.
3. Thin canonical orchestrators and removal of duplicate execution ownership.
4. Repository navigation and historical separation.
5. Further result improvement only when it does not compromise the first four.

## Suggested next decision

The next review should decide whether to authorize a documentation-only
architecture-recovery branch containing:

- the six method cards;
- the authoritative stage manifests;
- generated teaching traces for one Gan and one ExECT letter;
- corrected diagrams;
- a proposed current-versus-historical comparison boundary; and
- a refactoring candidate list with parity-test requirements.

That branch should not initially change prediction-bearing code. Its purpose is
to make the system explainable enough that any later refactor is deliberate,
bounded, and easy to evaluate.
