# Clinical Extraction: architecture review

Prepared for Conor Brown · 11 September 2026

Status: advisory architecture review of the pinned revision below. Recommendations are proposals; the [active roadmap](../plans/ACTIVE_ROADMAP.md) remains the project plan.

**Recommendation:** build a small shared evidence layer, keep clinical and research-study semantics explicit, and make benchmark labels, cohort answers and evidence tables projections over retained assertions. Validate the boundaries through two working slices before consolidating the existing pipelines.

## Scope and strength of evidence

This is a static architecture and documentation review of [clinical_extraction at commit fa8917f21b5fdebde516369fe97292e4db673ebb](https://github.com/cbrown564-alt/clinical_extraction/tree/fa8917f21b5fdebde516369fe97292e4db673ebb). The complete GitHub tree contains 399 Python files under `src/`, 103 Python files under `tests/`, and 485 Markdown files under `docs/`. These are file counts, not complexity scores. I retrieved 73 selected code, test, schema and design files for detailed inspection, plus the root instructions and navigation documents. I followed the operational paths, Gan structured extraction, ExECT finding assembly, evidence utilities, prompt composition and longitudinal Q5 prototype. I did not exhaustively inspect every method, run the test suite, call extraction models, inspect locked patient rows or reproduce benchmark scores.

`PROJECT_STATUS.md` and `CONTEXT.md` are ignored local files according to the tracked roadmap and are absent from this public snapshot. Consequently, current local work may be ahead of this review. No repository changes were made. This document is an advisory review; the existing `docs/plans/ACTIVE_ROADMAP.md` remains the project plan.

The active direction is already longitudinal. The repo contains 12 authored patients, annotation contracts and a bounded executable Q5 evaluator. The most recent appended review describes pilot v0.6, whereas several document introductions still describe earlier revisions. I use the later, explicitly scoped entries where they differ. Their reported test results are historical author reports, not checks performed here.

Background research used primary technical documentation, published research and the earlier NICE discussion brief. NICE methodology and AI-policy pages returned access errors, and SIGN material could not be retrieved reliably. Accordingly, this review does not claim a complete or current NICE/SIGN methods audit. The earlier brief describes the guideline workbench as a proposal. Searches of the connected repository list and GitHub issues did not identify the specific assigned guideline project mentioned in the request; its exact implementation and remit remain unresolved.

## 1. The fundamental design decision

The reusable product should be **a supported account of what sources assert**, together with the means to derive a particular answer. A document, an assertion, a real-world event and an analytical answer are different objects.

For example, two letters can describe the same event differently. The later letter may correct the interpretation without changing when the event happened. Two papers can describe the same trial, with different outcomes, denominators or corrections. In both cases, collapsing the material into one final answer during extraction destroys information needed by another question.

Your direction is sound, with two qualifications:

1. **“Extract all clinical facts” still needs a declared scope.** No finite schema captures every useful clinical statement. Define a reusable domain scope such as epilepsy diagnosis, seizure patterns, medication actions and investigations. A new question can reuse that record only if its required information was captured. Persist source documents and extraction coverage so that missing capabilities can trigger a targeted new extraction.
2. **Interpretation cannot be deferred entirely.** Recognising a seizure pattern, assigning a statement to a patient rather than a relative, and linking a count to a subtype already require interpretation. The useful separation is between source-supported interpretation and the policy that chooses an answer for a particular purpose.

The aim is therefore: preserve evidence and competing interpretations; make information-reducing decisions explicit, versioned and replaceable. “Extract, then decide” describes that principle, but should not prescribe exactly two model calls or one universal pipeline.

## 2. What is coupled today

The following findings refer to inspected code. Paths are relative to `src/clinical_extraction/` unless otherwise indicated.

| Finding | Concrete evidence | Architectural consequence | Recommended boundary |
|---|---|---|---|
| Extraction requires an answer | Gan `llm/prompt_llm_extract.py` includes `selection_schema`, allowed label forms and highest-current-burden instructions. `StructuredExtractionRecord` in `hybrid_structured_events.py` requires both `events` and `selection`. | Changing the downstream question changes an ostensibly upstream extraction contract. | A source assertion batch without a required final selection; keep the current contract as a frozen benchmark adapter. |
| Operational inference requires benchmark-shaped input | `operational/gan.py::_note_record` constructs `GanFrequencyRecord` with dummy gold labels and gold-normalized fields. | A caller supplying an ordinary note inherits evaluation concepts. This is interface coupling; it is not evidence that gold is sent to the model. | Runtime consumes a source document; a benchmark example separately pairs it with a reference answer. |
| Rich evidence is secondary to the answer | `core/schemas.py::FinalExtraction` is a final value, rationale and evidence string. Operational Gan returns the richer record alongside parse information and score projections. | The output model makes a single answer primary even when reuse needs the candidate record. | Return typed extraction artifacts as first-class outputs; task projections produce final answers. |
| The best reusable concept belongs to ExECT | `assembly/clinical_finding.py` has findings and provenance, but imports `PredictedMention`, stores ExECT attribute dictionaries, and converts back to scorer mentions. | Moving the file into `core` would preserve its benchmark assumptions. | A small evidence envelope with typed domain payloads; ExECT conversion lives outside that envelope. |
| Producer abstraction assumes replay files | `assembly/producers.py::CandidateProducer` requires `artifact_path` and `rows_by_id()`. `SavedJsonlProducer` indexes rows by `letter_id`. | It is a useful replay-source interface, but not yet a shared live extractor interface. | Separate artifact readers from extractors; both can yield the same typed assertion batch. |
| Views combine output and evaluation | `assembly/views.py::build_scoring_views` takes gold letters, invokes score reports and CUI projection, and emits benchmark/fidelity summaries. | A cohort view cannot reuse this interface without inheriting evaluation. | Pure view construction; scoring is a separate consumer of a projected answer. |
| Evidence has no shared document identity | `core/schemas.py::EvidenceSpan` holds text and optional offsets. `core/evidence.py::locate_evidence` uses the first matching substring, with repair fallback. | Repeated text, multiple versions and PDF tables require more precise references. | Versioned source reference, disambiguated locator and recorded match/repair result. |
| “Inventory” has a policy-specific scope | ExECT `prompt_inventory.py` excludes non-epileptic events from the diagnosis family unless explicitly asserted as epileptic, and prescribes family-specific output wording. | That is defensible for ExECT, but insufficient for a history that must preserve later reinterpretation and competing events. | Explicit domain capture scope, followed by ExECT inclusion and encoding policy. |
| Orchestrators still depend on legacy bundles | Gan `orchestration/llm_with_rules.py::run_record` imports `hybrid_structured_events` for prompt dispatch, parsing, repair configuration and the extractor. | Introducing an orchestrator has not separated all of its implementation responsibilities. | Pull out small contracts at call boundaries; preserve current stage order in the old route. |
| Longitudinal semantics live mainly in research scripts | `scripts/longitudinal/evaluate_q5_slice.py` evaluates authored annotations and imports the annotation checker. No `src/clinical_extraction/longitudinal/` package exists in this snapshot. | There is a concrete semantic prototype, not a completed shared longitudinal runtime. | Promote the tested query kernel separately from fixture loading and replay reporting. |

Source anchors: [Gan prompt][gan-prompt], [Gan structured contract][gan-structured], [operational Gan][op-gan], [shared schemas][core-schema], [ExECT finding][finding], [producers][producers], [scoring views][views], [evidence utilities][evidence], [ExECT inventory prompt][inventory-prompt], [Gan orchestrator][gan-orchestrator], [Q5 prototype][q5].

These findings do not imply that the work should be discarded. Several boundaries are already valuable: exact-source checks, retained raw outputs, format-only retry machinery, explicit semantic-repair ownership, source candidate IDs, component ablations and replay contracts. The Gan `CandidateSet` and `ClinicalAssessment` models already separate source-near candidates from a later synthesis. However, their types remain explicitly Gan- and seizure-frequency-specific. They provide migration examples, not a ready-made universal schema.

## 3. The shared model should be small

Use a **shared evidence envelope plus domain-specific payloads**. Avoid both a universal dictionary of arbitrary facts and a giant clinical schema full of optional fields.

| Object | Shared responsibility | Keep outside it |
|---|---|---|
| SourceDocument | Stable document/version ID, content hash, source type, availability, derived text and mapping to the original | Patient matching, clinical conclusions, benchmark gold |
| EvidenceRef | Document version, exact quote or table cell, text offsets/page/block location, matching status | Clinical correctness or study quality |
| Assertion | What a source states; subject reference; typed payload; source/reporter; supporting references | A mandatory final answer |
| Relationship | Assertion endpoints, typed relation, evidence and derivation | A universal rule that latest statements always win |
| Activity | Model/rule/reviewer identity, inputs, outputs, versions and changes | Clinical truth inferred from successful execution |
| DecisionRecord | Policy ID/version, input artifact IDs, selected/rejected/undetermined items and reasons | Mutations to the original assertions |
| CoverageRecord | Extraction scope, processed/missing sections, failures and explicit source completeness claims | Treating an empty output as evidence of absence |

There are two identities to preserve: the identity of an assertion in an extraction artifact, and the identity of the clinical event or study entity it describes. Do not make a text hash serve both roles. A rerun can produce different assertion boundaries; cross-run identity then requires an explicit mapping. Corrections and reviewer edits should create a new version or recorded action rather than silently overwriting old output.

The shared envelope need not require every assertion to have clinical time, certainty and an experiencer with universal enum values. Put valid-time structures in a reusable primitive library; clinical assertions can require them where appropriate. Study results need follow-up duration and analysis time points, which should not be forced into “current/recent/historical”. Domain schema versions define the relevant meanings.

Use ordinary Python composition and typed models. A small number of functions/interfaces is sufficient: extract, validate, normalize, link, evaluate policy and export. A generic workflow engine, microservices, dynamically loaded plugins and a graph database have not yet earned their complexity. Relationships can initially be stored as tables or JSON records with stable IDs.

## 4. Separate domain, question and execution choices

Today “task” often means a mixture of clinical topic, dataset, answer schema and pipeline. Split those axes explicitly.

| Configuration | Example |
|---|---|
| Domain definition | Epilepsy patterns, medication actions, diagnosis assertions and investigation events |
| Extraction specification | Capture those families, all documented temporal states, evidence and relationships; specify what is out of scope |
| Normalization policy | Preserve ranges; resolve dates only from supported anchors; distinguish clusters from seizures |
| Link policy | Same-pattern identity, later reinterpretation, repeated mention, conflict |
| Decision policy | Gan current-frequency choice; current ASMs; tonic-clonic-only history; Q1–Q5 |
| Output contract | Benchmark string, patient timeline, cohort membership or evidence table |
| Execution profile | Model/provider, local/cloud route, deterministic versus model stage, retry budget |
| Evaluation protocol | Dataset/split, references, metrics, allowed development and comparison rules |

These components are independently versioned, but not arbitrarily interchangeable. A policy declares its required fields and relationship types. If the extraction record lacks them, report insufficient coverage or request a targeted extraction; do not return a misleading negative.

Keep physical stage boundaries flexible. Recognition and encoding may share a model call. Temporal linking may use a second call. Deterministic rules can supply some assertions and model extraction others. What matters is recording who supplied each assertion or changed its meaning, and permitting a policy-only replay without rerunning extraction.

## 5. Prompt components: modularity without hidden coupling

The repo already has useful component work. Gan separates label forms, variants and selection prompts, and `tests/test_gan_extract_prompt_component_ablations.py` checks several component-removal variants. ExECT has prompt builders and worked-example loading. Preserve that evidence while making components represent semantic responsibilities.

| Component | Extract stage | Decide stage |
|---|---|---|
| Scope and definitions | Families, inclusions, exclusions, what counts as a source assertion | Which captured families can answer the question |
| Evidence instructions | Quote/cell support; no unsupported completion | Cite assertion IDs and policy clauses |
| Representation | Typed fields, allowed domain concepts, temporal uncertainty | Decision status and output schema |
| Examples | Source-to-assertion examples, including competing facts | Record-to-decision examples |
| Normalization | Explicitly permitted encoding, with raw value retained | Additional analytical conversion if the policy requires it |
| Selection policy | Omitted for reusable extraction | Eligibility, subtype filters, aggregation and tie handling |

“Allowed labels” therefore has two meanings: domain concepts permitted in an assertion, and final benchmark answer forms. Only the former belongs in general extraction. Worked examples can also leak selection policy: an example that omits historical or non-epileptic events teaches their exclusion even if the general instructions say to retain them.

A prompt compiler should emit the exact rendered request and a manifest containing component IDs, content hashes, schema version and example IDs. Preserve order as part of the rendered prompt. Keep bulky provenance outside model-facing payloads when it does not help extraction. Validate component compatibility before a call. Do not add a sprawling conditional template language.

For a new reusable extractor, change only the downstream selection policy and verify that the extraction prompt and stored assertions remain unchanged. Separately evaluate whether explicitly telling the extractor the question improves recall. That is a legitimate alternative execution strategy, but it must be named and measured; it is not equivalent to question-independent extraction.

## 6. Longitudinal epilepsy: the next implementation should start here

The existing [task definition][long-task] already gets several difficult issues right: physical cutoff filtering, separate visit and retrospective accounts, supplied patient IDs, concurrent patterns, partial dates, plan versus use, and three-way cohort answers. Preserve those semantics.

The pipeline should distinguish four temporal notions: the clinical event/state interval, the consultation date, when a document became available, and when a clinical reinterpretation occurred. Extraction processing time is another provenance field; it must not substitute for any of these. The FHIR Observation specification similarly distinguishes clinically relevant time from when a resource version was made available, although mapping your full model to FHIR requires more than those two fields. [FHIR R5 Observation](https://www.hl7.org/fhir/R5/observation.html).

**Illustrative example, not a case from the dataset:** a January letter describes weekly blank spells as epileptic and proposes medication. A March letter reports that the drug was never started and explicitly reinterprets those same spells as non-epileptic following review. The January visit account retains the initial interpretation and proposed treatment. A retrospective account of January can attach the later reinterpretation, with its source and decision date. Neither account should record medication exposure merely because it was proposed.

Store each assertion separately, link the same pattern with evidence, and derive the account for a declared index date and information cutoff. A timeline is therefore a view over assertions and relationships, not an accumulating paragraph or one mutable patient record.

Three-valued logic is necessary. Failure to find an event is not proof that none occurred. A tonic-clonic-free interval does not establish freedom from every epileptic seizure. A current medication list does not establish when treatment started. Missing follow-up remains missing observation.

The Q5 slice is especially informative. Its `first_reinterpretation_evidence` field was introduced because a correction after the index date does not prove that no earlier correction occurred. The latest review reports a four-request, one-patient ablation showing why the field matters to that evaluator. It explicitly does not claim general Q5 accuracy. [Prototype][q5]; [review history][pilot-review].

**Candidate abstraction to test:** a supported coverage assertion with subject, event family, scope, interval and evidence. This could represent “first ever”, “all episodes in this interval” or “no other patterns”. It might eventually replace task-specific completeness fields, but do not replace the existing field until several independent examples establish equivalent behavior. Source completeness, extraction coverage and clinical absence must remain distinct.

A further hard issue is evaluation coverage: Q1–Q5 do not directly reward accurate seizure-burden rates, ranges and clusters. If the intended output includes disease progression, add a separately scored burden-history endpoint. Otherwise the new benchmark risks reproducing the old problem: a rich-looking schema whose important fields are invisible to its primary metric.

## 7. Cohorts and predictive models belong downstream

A cohort query should specify patient group, index time, observation window, information cutoff, required concepts, inclusion/exclusion predicates and unknown handling. Its output should contain membership plus supporting witnesses and unresolved predicates. A UI filter such as “tonic-clonic seizures only” becomes a parameterized view, not a new extraction prompt when the existing capture scope is sufficient.

For combinations of medication and epilepsy type, distinguish co-documentation from actual exposure and temporal overlap. A medication mention and diagnosis in the same letter do not establish that treatment caused a later change.

Predictive modelling needs an additional contract: prediction time, feature window, outcome definition, outcome horizon, censoring and missingness policy. Features must use only information available at prediction time. Later evidence can be used to ascertain an outcome under a declared label protocol, but cannot leak into earlier features. If a cross-document model saw later letters while interpreting an earlier note, filtering its finished output afterwards does not remove that leakage. Cutoff isolation must happen before inference or through a replay that demonstrably excludes later inputs.

Split patients and any synthetic source ancestry together; do not place related visits or near-duplicate seed families in different splits. Evaluate extraction error propagation into cohort membership and model features. Predictive discrimination, calibration and external validity would be new studies, not consequences of benchmark F1. The active roadmap correctly leaves prediction outside the first longitudinal release.

Use a flat feature table as an export, retaining links back to assertions. OMOP offers useful interoperability targets: `NOTE_NLP` records extracted terms, note links, offsets, lexical variants and processing metadata. Its row semantics do not by themselves replace a rich assertion-and-revision model. [OMOP CDM 5.4](https://ohdsi.github.io/CommonDataModel/cdm54.html#NOTE_NLP).

## 8. Guideline evidence: a different domain, a shared evidence problem

Clarify the work item as **research evidence extraction and review-question matching**. Asking questions of a published guideline, checking a patient's care against a recommendation, and helping develop recommendations from studies are different tasks. This review develops the third interpretation, consistent with the request's emphasis on experimental results and evidence review.

The unit of analysis is usually a study and its comparisons, not one PDF. Cochrane explicitly requires linking reports of the same study; it also emphasizes structured collection, preserving sources and planning how to handle inconsistencies. This supports a report-to-study linking layer alongside your letter-to-patient linking layer, while keeping their identity rules separate. [Cochrane Handbook, chapter 5](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-05).

Recommended study payloads include study identity, population/subgroup, arm, intervention/comparator, outcome definition, follow-up, analysis population, denominator, effect measure, estimate and uncertainty. Keep adjusted versus unadjusted analyses and intention-to-treat versus other populations explicit. An outcome estimate should be keyed by that context; “the study result” is too coarse.

PDF ingestion must preserve tables, headers, footnotes and page locations. A number in a table cell can require several evidence references: the cell, row/column headers and a footnote defining the analysis. Exact text spans over a flattened PDF are not always sufficient. Keep parser/OCR versions and mappings to the original document so that a changed parser does not silently invalidate old evidence locations.

Separate these judgments:

| Judgment | Question | Proposed output |
|---|---|---|
| Source validity | Does the cited material exist at that version/location? | Located, ambiguous, missing or transformed |
| Semantic support | Does it support the extracted assertion and its attributes? | Supported, contradicted or insufficient evidence |
| Review eligibility | Does the study/result meet a declared review question and protocol? | Include, exclude or unclear, with criterion-level reasons |
| Critical appraisal | What study limitations affect credibility? | Reviewer-adjudicated domain judgments with evidence |
| Evidence certainty | How much confidence is justified across a body of evidence? | Outcome-level appraisal across studies |
| Recommendation | What policy follows, considering benefits, harms and other decision factors? | A distinct, governed synthesis/decision process |

GRADE's certainty assessment addresses a body of evidence and includes concerns such as risk of bias, inconsistency, indirectness, imprecision and publication bias. It must not be inferred from the extractor's confidence score or citation presence. [Cochrane Handbook, chapter 14](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-14).

Established work offers useful comparators:

| Work | Relevant contribution | What it does not establish for this repo |
|---|---|---|
| [Evidence Inference, Lehman et al. 2019](https://aclanthology.org/N19-1371/) | Full-text trial findings conditioned on intervention, comparator and outcome; demonstrates why a question-to-evidence relation matters | Complete numerical extraction, multi-report reconciliation or guideline recommendation quality |
| [RobotReviewer](https://github.com/ijmarshall/robotreviewer) | PDF trial annotation, PICO information and automated risk-of-bias assistance with highlighted text | That its judgments are reliable enough for every review or that it is your assigned project |
| [Schmidt et al. feasibility study, 2024](https://arxiv.org/abs/2405.14445) | Examines LLM extraction across review domains and reports variable performance; study design and causal-method fields were difficult | A universal accuracy threshold or current-model performance estimate |

For a transfer pilot, use one completed guideline review question and a small set of openly accessible study reports, including a multi-report study and table-based results. Preserve several candidate time points and subgroups, then apply two predeclared eligibility/time-point policies to the same extracted record. Compare with expert-reviewed evidence tables. Review disagreement is a result to investigate, not something a second model automatically resolves.

The shared opportunity is evidence handling, typed assertions, provenance, relationships and policy replay. Clinical temporal linking and study-population/result linking should share contracts where their meanings match, not one domain algorithm.

## 9. Recommended migration order

Integrate this sequence into the existing roadmap rather than adding another plan. Prefer a sequence of bounded changes with explicit exit criteria.

| Slice | Work | Exit criterion |
|---|---|---|
| A. Preserve existing behavior | Pin current prompt/schema/repair/scorer versions and a permitted replay sample; record hashes and commands | Old routes remain reproducible; structural changes can be separated from new model behavior |
| B. Introduce source and artifact contracts | Add versioned source documents, evidence references and assertion batches alongside old outputs | A note can be represented without gold fields; old output can be read through an adapter |
| C. Promote longitudinal Q5 | Move reusable predicate evaluation out of the script; inject documents/assertions/query; retain script as a replay wrapper | Existing authored Q5 cases and boundary/conflict behavior remain intact; patient 011 and partial-date cases extend coverage |
| D. Demonstrate policy reuse | Use one frozen assertion batch for a subtype history and an existing cohort query | Policy changes do not change extraction artifacts; missing required fields are explicit |
| E. Build the study-evidence slice | Add study-specific payloads, table-aware evidence and result eligibility | Two review policies reuse one extraction; no epilepsy-specific fields are needed in shared core |
| F. Consolidate proven overlap | Extract common execution, validation and provenance utilities; compose prompts; retain benchmark adapters | New domain additions avoid edits to shared clinical enums or benchmark modules |

Do not begin with a global move of every file or a merger of the Gan and ExECT runners. The legacy paths encode research provenance and repair ownership, and their commonality is only partial. New adapters may be lossy: an old output that discarded a historical event cannot reconstruct it. Declare that loss; do not present legacy conversion as equivalent to a new broad extraction.

Suggested ownership within the existing single package: `core` for source/evidence/artifact contracts; `longitudinal` for clinical assertions, links and query evaluation; a study-evidence module when its first executable slice exists; existing `tasks/.../gan2026` and `tasks/.../exectv2` for retained benchmark rules and adapters. Move files only when behavior and callers justify it.

## 10. Verification that would demonstrate the abstractions work

The central architectural test is not fewer files. It is **a materially different task implemented without changing shared-core semantics**.

Preserve existing evidence, prompt snapshot, repair-attribution and replay checks. The inspected tests already protect component omissions, ledger-only behavior and operational boundaries. Add focused behavior checks at the new seams rather than duplicating old implementation tests.

| Area | Decisive check |
|---|---|
| Policy independence | Change subtype or time-point policy; retained extraction and its hash stay unchanged |
| Provenance | Every changed assertion records an owner and supporting source or derivation |
| Evidence identity | Repeated quotes and different document versions cannot silently resolve to the wrong location |
| Temporal isolation | Adding a later letter cannot change a visit-account answer computed from the earlier permitted inputs |
| Missingness | Empty extraction, explicit absence, unknown source statement and unprocessed text remain distinguishable |
| Identity | Repeated mention of one pattern or repeated report of one trial is not double-counted |
| Repair separation | Format retry cannot silently introduce a new clinical or study assertion |
| Domain transfer | Study payloads use shared evidence handling without seizure enums or Gan label parsing |

Evaluate extraction, linking and policy execution separately and end to end. For longitudinal work, report assertion/relationship correctness, temporal boundary errors, burden-history accuracy, per-query membership results and indeterminate rates. Compare linked extraction with independent-letter aggregation and direct history-to-answer baselines under the same permitted context. For study work, assess estimates, denominators, population/time-point linkage, evidence support, selection errors and measured reviewer correction time. Group evaluation by patient or study rather than treating correlated records as independent.

Use controlled field removals through an executable evaluator. The Q5 work already demonstrates why unchanged stored answers are not evidence that a field is unnecessary. Likewise, measure correction time directly; model latency and AI agreement are not substitutes for reviewer effort or expert accuracy.

## 11. Documentation changes that support the architecture

The documentation contains useful design knowledge, but authority and currentness are hard to infer. The [software design page][design] says dataset-independent prompt abstractions are deliberately excluded; your present request reopens that decision. Update the scoped design rationale once the new boundaries are demonstrated, rather than treating the old exclusion as an enduring prohibition.

The active roadmap's header says the executable field-utility comparison is outstanding, while the later pilot review documents a bounded Q5 experiment. The task definition's introduction says it is not an implemented annotation schema, despite the separate schema and checker now existing. These are synchronization problems, not evidence that the underlying research is invalid.

Keep the current owner map and one roadmap. Give living design pages a short current statement, applicable scope and source revision. Keep detailed historical experiments in their existing records, with a clear pointer from the current summary. Publish enough status in a tracked entry point that a public contributor does not need ignored local files to know what is implemented.

Separate four kinds of explanation: the shared software contract, each domain's semantics, each benchmark's scoring/annotation policy, and the experiment record. Generated architecture diagrams should remain explicitly diagrams of implemented legacy paths, not diagrams of the proposed general system. Update their generators alongside any code change that affects them.

## 12. Decisions worth settling before expanding the framework

1. **What is the first reusable record?** Recommend source assertions with typed payloads and evidence, not a single finalized patient phenotype.
2. **Which information must every epilepsy extraction retain?** Start with the existing four families and supported temporal states. Add fields because history or a named query uses them; do not declare capture of all clinical knowledge.
3. **What proves an absence or complete history?** Require scoped source support. Distinguish that from the extractor reporting it processed every section.
4. **Which links may change an interpretation?** Explicitly supported corrections may; recency or majority vote alone may not.
5. **What belongs in shared code?** Evidence, provenance, execution contracts and reusable primitives. Keep clinical/study identity rules and policy semantics domain-owned until both slices demonstrate common behavior.
6. **What is the guideline project's concrete job?** The proposal here assumes evidence-table preparation and review-question matching. A named project brief could materially change its source types and acceptance tests.
7. **What would count as success?** Two policies reuse one retained record; a study task runs without clinical special cases in core; preserved benchmark routes reproduce their old behavior; the new tasks receive independent evaluations.

The strongest next step is to implement those boundaries on the existing longitudinal prototype and one narrow study-evidence example. That would turn the original modular-framework ambition into a testable software claim, while preserving the research work that made the necessary distinctions visible.

[gan-prompt]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/prompt_llm_extract.py
[gan-structured]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py
[op-gan]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/operational/gan.py
[core-schema]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/core/schemas.py
[finding]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/clinical_finding.py
[producers]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/producers.py
[views]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/views.py
[evidence]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/core/evidence.py
[inventory-prompt]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/prompt_inventory.py
[gan-orchestrator]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/llm_with_rules.py
[q5]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/scripts/longitudinal/evaluate_q5_slice.py
[long-task]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/docs/longitudinal/task_definition.md
[pilot-review]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/docs/longitudinal/pilot_disagreement_report.md
[design]: https://github.com/cbrown564-alt/clinical_extraction/blob/fa8917f21b5fdebde516369fe97292e4db673ebb/docs/design/architecture.md
