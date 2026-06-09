# Gan 2026 Architecture Lineage And Retired Approaches

Date: 2026-06-07

Author: Claude

Status: Phase D deliverable for
[[gan2026_repo_consolidation_and_cleanup_plan]] Section 6 — the consolidated
lineage summary that makes Phase E removal defensible. Per the user's framing,
prior architectures "served the purpose of providing evidence and shaping our
path"; this document compresses that contribution into one durable record so
the dozens of scattered, dated research docs describing these architectures'
internals can later be removed without losing anything load-bearing. Each
section below answers: what the line tried, what it taught the project, and
what (if anything) of it survives in the canonical lines —
`pipeline_v1.py` (deterministic), `hybrid/reset_clinical_assessment_pipeline.py`
(hybrid), and `llm_only_direct_labeler.py` / `hybrid_structured_events.py`
(fully-LLM one-shot and multi-step variants), per
[[gan2026_canonical_runner_selection_2026-06-07]].

---

## 1. `hybrid/staged_hybrid_assembly.py` (v0)

**What it tried**: `staged_hybrid_assembly_v0` assembled a long chain of
bespoke validation-era components — abstention-policy predeclaration,
component-evidence matrices, exact-label-selector ablation, last-event-date
instrumentation, residual-nonprediction audits, selective-abstention pressure,
a "selective verifier," and a `staged_decision_policy` — into one runnable
candidate, wired together with ad hoc per-component artifact paths
(`DEFAULT_*_JSONL_PATH`/`JSON_PATH`/`REPORT_PATH` for each sub-stage). It was
the first attempt to compose many narrow validation-development findings into
one end-to-end "staged hybrid" candidate rather than studying them in
isolation.

**What it taught the project**: that bolting many narrow, independently-tuned
components together produces an assembly that is hard to audit and easy to
overfit to validation — the component list itself (abstention pressure,
"selective verifier," exact-label-selector ablation, etc.) reads as a
catalog of validation-attuned micro-policies rather than a principled stage
model. It pushed the project toward asking "what is the right *stage*
taxonomy" instead of "what is the next component to bolt on," which is the
question the reset architecture answers directly.

**What survived**: nothing of the v0 component catalog survives by name —
it is the cleanest dead end of the four lineages (zero live code dependents
besides its own `needs-decision`-tagged analyzers). What *did* survive is the
negative lesson: the reset pipeline's named-stage-ownership model
(`Extract -> Select / Clinical Assessment -> Normalize -> Project -> Verify ->
Render / Score`) exists precisely to replace this kind of ungoverned
component accretion with stages that have one clear owner and one clear
contract each.

---

## 2. `hybrid/staged_assembly_v1.py` (v1)

**What it tried**: `hybrid_multi_component_staged_assembly_v1` was a
"saved-replay final assembly" that composed a fixed set of named, versioned
policies — `h5_repair_policy_v1` (bounded repair), `seizure_free_boundary_event_v0`
(boundary detection), `benchmark_convention_renderer_v0` (rendering),
`selective_safety_floor_gate_v0` (a verify-stage safety gate), plus H6/H9/H10
"sidecars" (control replay, action-summary, raw-identity provenance audits) —
and froze the result behind a locked-test holdout protocol
(`gan2026_hybrid_multi_component_staged_assembly_v1_frozen_holdout_protocol_2026-06-05.md`).
It was the project's most disciplined staged-assembly attempt: each component
was named, versioned, and audited with W->C/C->W transition tables before
being allowed into the assembly.

**What it taught the project**: the `gan2026_final_assembly_findings_and_holdout_plan_2026-06-05.md`
retrospective is explicit and numeric. The control candidate
(`untagged_nonprediction_release_candidate_v0`) scored 697/750 correct with
37/37 H6 controls preserved and 0 release-wrong rows — strong enough to be
the "denominator," not a final result. `selective_safety_floor_gate_v0`
transferred best across surfaces (validation750: 11 W->C/0 C->W; frozen test450
aggregate: 8 W->C/0 C->W) — "selective fallback is useful when narrow and
predeclared." `h5_repair_policy_v1` taught that repair must be reported as a
score layer and that label-changing semantic repair must never hide inside
"normalization" language. The boundary/renderer typed-event layer was promoted
only as a *rare-family* component (36/36 synthetic match, 6 W->C/0 C->W on the
validation typed panel) — not a broad-coverage solution. Most importantly,
**broad structured projection was rejected**: `structured_projection_port_promoted_v0`
*reduced* the frozen test450 Purist proxy from 342/450 to 337/450 (7 W->C, 12
C->W), closing off "broad projection rewrite" as a goal-achieving path. And
the H6/H9/H10 sidecars were reframed as "useful instrumentation, not
conceptual pipeline stages" — report/audit roles, not pipeline roles.

**What survived**: this is the lineage that most directly generated the
canonical reset model. As the cleanup plan's own example states:
*"`staged_assembly_v1` introduced the h5/h6/h9/h10 policy-marker pattern; this
was superseded by the reset pipeline's named-stage-ownership model, which
generalizes the same idea without bespoke marker codes."* Concretely: the
discipline of "name the policy, version it, audit its W->C/C->W transitions
before promoting it" generalized into the reset pipeline's named, owned stages
(Normalize/Project/Render/Score/Route/Decision each with one explicit owner
and an audited contract); the safety-floor-as-narrow-verify-gate idea
generalized into the reset pipeline's Verify/Route stages; and the rejection
of broad structured projection directly shaped the reset pipeline's choice to
keep projection bounded and stage-scoped rather than a single sweeping
rewrite.

---

## 3. `hybrid/hybrid_parallel_state_candidate_reasoner.py`

**What it tried**: this runner generated several *independent* candidate
representations in parallel for the same note — a deterministic top candidate,
a state-graph projection, a raw LLM candidate selector, and a hybrid-adjudicator
selection (with and without "adapters") — then compared them as named score
layers (`SCORE_LAYER_NAMES`) plus oracle analysis layers
(`oracle_candidate_presence`, `oracle_graph_representability`). The thesis was
that running multiple reasoning strategies "in parallel" and studying where
each one wins or loses would surface the hidden failure families that a single
strategy could not.

**What it taught the project**: per
`gan2026_multi_component_assembly_research_report_2026-06-05.md`'s
cross-experiment findings (drawn substantially from this lineage's
validation750/test450 runs): **(1) validation is saturated** — once the
validation baseline reaches ~0.94-0.97, further validation gains mostly measure
fit to known validation families rather than real generalization; **(2) high
precision gates are too low-coverage** — the best test movement (13 W->C, 1
C->W, 354/450) was a good component result but roughly 51-63 correct rows
short of the ~405/450 needed for 0.9; **(3) raw LLM replacement is unsafe** —
the direct labeler full-validation run produced 26 W->C but 329 C->W; **(4)
evidence exactness is necessary but not sufficient** — exact quoted spans were
often the wrong span for the current Gan label (recurring traps: historical
seizure-free statements wrongly becoming `unknown`, partial windows overriding
correct broader labels, per-semiology counts overriding overall state); and
**(5) schema repair matters operationally** but must stay separate from
semantic repair. The `gan2026_hidden_family_first_failure_atlas_2026-06-03.md`
mined this lineage's `..._deterministic_safety_floor_v2_replay` artifacts to
catalog dozens of named hidden failure families (`unknown_boundary`,
`seizure_free_duration`, `rate_bucket_or_denominator`, `cluster_burden`,
`competing_semiologies`, etc.) — the project's first systematic
failure-family taxonomy.

**What survived**: the failure-family taxonomy this lineage's replay artifacts
made visible (boundary/duration/denominator/cluster/competing-semiology
families) directly informs the reset pipeline's Normalize/Project family
handling and the verification/routing analyzers
(`suspicious_selected_state_routing.py` and friends) that remain canonical.
The "compare strategies as named, oracle-annotated score layers" instinct also
generalized into the reset pipeline's explicit per-stage scoring/audit
artifacts. The runner itself, however, is a dead end: zero live Python imports,
and its CLI/observatory/frontend wiring (`FAMILY_SHORT_LABELS["hybrid_parallel_state_candidate_reasoner"]`,
the `traceAdapter` switch arm) is confirmed **dead** — it references a
`pipeline_family` with zero backing rows in `experiments/registry.jsonl`.

---

## 4. `hybrid/hybrid_rules_candidates_llm_adjudicator.py` (+ `hybrid_adjudicator_parser.py`)

**What it tried**: a "pragmatic hybrid thesis" — deterministic rules generate
a high-recall candidate set (`Candidate events`), an LLM "adjudicator"
(`Gan2026FinalSelectionAdjudicatorSignature`) accepts/rejects/selects among
them, and conservative overreach gates (candidate membership, accepted subset,
label support, evidence substring, boundary demotion) fall back to the
deterministic top candidate whenever the LLM's choice looks unsupported. The
parser/schema-repair companion (`hybrid_adjudicator_parser.py`,
`AdjudicatorDecisionRecord`) gave this lineage an unusually clean, fully
attributed output contract.

**What it taught the project**: the numbers are unambiguous and repeatedly
cited across the retrospective docs. v0.1 *underperformed* deterministic top
(680/750 = 0.9067 adjudicated vs. 697/750 = 0.9293 deterministic — the LLM
corrected 7 deterministic misses but regressed 24 deterministic-correct rows).
v0.2's conservative gates didn't fix this either (gated 244/250 vs.
deterministic top 246/250 Purist on validation250; 0 deterministic-wrong to
gated-correct, 2 deterministic-correct to gated-wrong). A targeted
`cluster_diary_candidate_recall` revision improved a 56-row synthetic panel
(42/56 -> 50/56) but **did not generalize**: validation750 gated final dropped
to 677/750 vs. deterministic top's 697/750 (45 changed labels, 5 W->C, 25
C->W), and test450 gated final matched deterministic top's raw count (343/450)
only by Pragmatic luck (353 vs 354). The project-defining lesson, stated
plainly in `gan2026_intermediate_schema_report_2026-06-01.md` and the full
retrospective: **"an adjudicator constrained to a candidate set cannot recover
rows where the correct category is absent"** — and candidate-Purist recall was
itself capped at 707/750 (validation) and a much weaker 359/450 (test),
meaning no amount of better adjudication could close that gap. Its future
value was reframed from "general selector" to, at best, "a narrow
overreach-family adjudicator with abstention and fallback."

**What survived**: the attribution discipline — scoring deterministic-top,
raw-LLM, and gated-final as three separately named, separately measured
layers — generalized into the reset pipeline's explicit stage-by-stage
scoring/audit model (and into the comparison plan's "apples-to-apples by
shared back-half" methodology). The schema-repair separation this lineage
forced (`hybrid_adjudicator_parser.repair_decision_payload` /
`_repair_adjudicator_required_fields`, keeping format repair distinct from
semantic repair) generalized into the shared `contract.schema_repair` module
that the canonical hybrid and fully-LLM lines both import directly. But the
core thesis — "LLM adjudicates over deterministic candidates as the final
selection mechanism" — is a confirmed dead end: candidate-recall, not
adjudication quality, is the ceiling, and the canonical hybrid line (reset
pipeline) instead routes the LLM's contribution earlier (Select /
ClinicalAssessment) where deterministic stages still own representation and
arithmetic.

---

## 5. The 8 non-canonical `llm_only_*` modules (7 reasoners + repair-ablation companion)

These were a family of "fully-LLM" experiments, each testing a different
*output schema / reasoning-contract* hypothesis for what a model-owned final
answer should look like. Per the canonical-runner-selection doc, none had a
`shared-keep` Python dependent; each is summarized here by the distinct idea
it tested:

- **`llm_only_minimal_evidence_selector`**: minimal model-boundary schema (extract only the raw answer text + exact evidence), with deterministic sidecars doing everything else (label derivation, diagnostics, scoring). It represented the opposite end of the spectrum where the model owns almost no reasoning logic, shifting the burden entirely to deterministic post-processors.
- **`llm_only_claim_table_selector`** (+ `claim_table_parser`,
  `reports/claim_table_report.py`): a richer "source-near claim table" schema
  — extract section-local claims, then select the final answer from the table.
  It taught that source-near claim tables aid human-review transparency but
  that "the final [selection step] is the lesson" — a richer schema alone
  doesn't solve selection.
- **`llm_only_rich_selected_state_reasoner`**: an RQ3 schema experiment that
  asked the model to select one fully-typed clinical state (with boundary
  fields and graph-projection-shaped output) directly — the "maximal typed
  selection" end of the spectrum.
- **`llm_only_simplified_selected_state_reasoner`** ("A1", selection-only):
  the minimal-schema counterpoint to the rich reasoner — select one
  source-grounded state with *no* graph projection, testing whether stripping
  the schema down to bare selection improved reliability.
- **`llm_only_sparse_operands_selected_state_reasoner`** ("A2"): a middle
  point between rich and simplified — selection plus *nullable* numeric
  operand detail, testing whether partial numeric structure helped without the
  full graph-projection burden.
- **`llm_only_typed_adapter_reasoner`**: tested DSPy's typed `JSONAdapter`
  machinery itself — multi-field typed output (`events` /
  `selection` / `final_answer`) as an "adapter smoke" experiment, i.e.
  whether the adapter layer's structured-output guarantees were worth their
  complexity cost (the reset-era finding that "adapter layer changed 0 rows in
  the latest run; role unclear" applies directly to this lineage's premise).
- **`llm_only_typed_operations_reasoner`**: tested a *typed-operations*
  intermediate (extract typed `operations`, select among them, derive a final
  answer with model-derived graph projection) — i.e., pushing the
  candidate/selection idea one level more structured than claim tables, with
  the model owning the projection step rather than a deterministic stage.
- **`hybrid_structured_events_repair_ablation`**: a no-call companion
  ablation harness for the *canonical* `hybrid_structured_events`, meant to
  isolate which repair-family policies affect the canonical module's labels.
  Confirmed **not the active ablation mechanism** (zero run history, zero
  wiring) — its contribution is the *methodology* (ablate repair families
  against a frozen no-call replay), not the file.

**What it taught the project, in aggregate**: across this whole family and its
siblings, the recurring cross-architecture finding (full retrospective,
intermediate-schema report) is that **a single final Gan label is too lossy a
target to optimize directly** — every schema that tried to jump straight from
note to label (direct labeler, raw claim selection, raw typed selection)
either underperformed or was unsafe, while every schema that decomposed into
richer intermediates (events, claims, typed operations, selected states)
"improved on direct label prediction" but each exposed its own new attribution
or selection problem rather than solving the underlying one. This is precisely
the finding that makes `llm_only_direct_labeler` (the simplest direct baseline) the
right choice for the one-shot LLM-only version, and `hybrid_structured_events`
(structured event extraction coupled with multi-step reasoning) the right choice
for the two- and three-step variants.

**What survived**: no individual non-canonical module survives as a runner.
What survives is the *schema taxonomy itself* — "how much should the model
structure vs. select vs. project" is now a named axis (the comparison plan's
Option A/B framing), and the shared `contract.label_parser` /
`contract.schema_repair` modules these reasoners forced into existence are
imported by both canonical fully-LLM runners and the canonical hybrid line.

---

## 6. The `components/*` staged-assembly-era validation scripts (47 files)

This directory is exploratory scaffolding from the two staged-assembly eras,
not a distinct architecture: 45 of its 47 files are confirmed (Phase C
dependency-audit Section 4) to be islands — imported by nothing outside
`components/` — split roughly along filename-prefix lines into a v0 set
(`staged_decision_policy`, `trigger_*`, `selective_*`, `change_only_*`,
`boundary_state_graph`-adjacent) and a v1 set (`structured_*`, `boundary_*`).
Each was a narrow, single-question validation probe (abstention pressure,
exact-label-selector ablation, last-event-date instrumentation, residual
nonprediction audits, structured-projection ports, boundary typed-event
layers, and similar) written to answer one mechanics question about a staged
candidate before — or instead of — promoting it into an assembly. Their
collective lesson is procedural rather than architectural: this is what
*disciplined, narrow, falsifiable component probing* looks like, and the
reset pipeline's stage model is what made most of that probing unnecessary —
once a stage has one named owner and one audited contract, there is no need
for dozens of standalone scripts each re-deriving a narrow slice of the same
question. Two files — `source_trace.py` and `suspicious_state_policy.py` —
are *not* part of this batch: the audit found they are actually live,
imported dependencies of the canonical-line analyzer
`suspicious_selected_state_routing.py`, mis-classified by directory location
rather than by actual role; they should be relocated to shared infrastructure,
not retired with the rest of the group.

---

## What this means for Phase E

- **`staged_hybrid_assembly` (v0)**: this doc's Section 1 captures its
  contribution (and confirms it as a true dead end). Combined with its already
  modest doc footprint, the `needs-doc-archival-first` blocker is now clear —
  Phase E can proceed for this lineage as soon as its test is retired.
- **`staged_assembly_v1`**: this doc's Section 2 — including the explicit
  h5/h6/h9/h10-to-named-stage-ownership mapping the cleanup plan called for —
  captures the heavily-documented "frozen holdout protocol" cluster's
  load-bearing content. The `needs-doc-archival-first` blocker (the heaviest
  of the four lineages, per the audit) is now cleared; the underlying dated
  docs may be archived/removed once this doc is reviewed.
- **`hybrid_parallel_state_candidate_reasoner`** (+ its 13 string-coupled
  analyzers and `validation_surface_inventory.py`): this doc's Section 3
  captures both its parallel-strategy methodology and the hidden-family
  taxonomy its replay artifacts generated — the load-bearing content `PROJECT_STATUS.md`
  currently frames as an active "comparison baseline." The
  `needs-doc-archival-first` blocker is cleared; the registry/CLI/frontend
  unwiring (Section 5.3 of the audit) remains a separate, mechanical
  `needs-registry-update-first` step.
- **`hybrid_rules_candidates_llm_adjudicator`** (+ `hybrid_adjudicator_parser`,
  `reports/hybrid_adjudicator_report.py`, `saturated_surface_evaluation`,
  `architecture_component_ablation`): this doc's Section 4 captures the
  candidate-recall-ceiling finding that is this lineage's central, oft-cited
  contribution. The `needs-doc-archival-first` blocker is cleared; the
  remaining pre-step is the `synthetic_hard_case_component_stress.py`
  loader-porting (audit Section 5.2), which is independent of documentation.
- **The 8 non-canonical `llm_only_*` modules**: this doc's Section 5 names the
  distinct schema/reasoning idea each one tested and the aggregate
  "single-final-label is too lossy" finding that shaped the Option A/B
  selection. No further doc-archival prep is needed beyond what's compressed
  here (most of these carried no currency-framed doc references to begin
  with, per the audit's Section 2.7 table).
- **The `components/*` group (45 of 47 files)**: this doc's Section 6 gives
  the one batch summary the plan asked for. The `needs-doc-archival-first`
  blocker is cleared for the 45-file batch. `source_trace.py` and
  `suspicious_state_policy.py` remain explicitly excluded — they need
  reclassification and relocation (audit Section 5.1), not archival or
  removal.
