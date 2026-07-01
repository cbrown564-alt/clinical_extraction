# Clinical Extraction

This context covers the Gan 2026 seizure-frequency extraction work and its
evaluation surfaces.

## Repo layout / resumption

- Project control board: `PROJECT_STATUS.md`
- Active roadmap (what we are doing now): `docs/plans/ACTIVE_ROADMAP.md`
- Documentation map: `docs/NAVIGATION.md`
- Reading by narrative thread (five paths): `docs/THREAD_MAP.md`
- Active experiment surface: `experiments/README.md`
- Superseded notes archive: `experiments/archive/ARCHIVE_INDEX.md`
- Regenerating tracked artifacts: `docs/REGENERATION.md`
- Mapping the original supervisor brief's role names (Section/Timeline,
  Field Extractor, Verification, Aggregator Agent) onto the actual
  architecture: `docs/design/brief_role_crosswalk.md`

### Narrative threads (one-line pointers)

Full hop lists live in `docs/THREAD_MAP.md`. Terms for each thread are in the
sections below.

| Thread | One-line | Start doc |
| --- | --- | --- |
| **T1 Reliability / The Wall** | Confident over-reading; no forward-observable abstention signal on binding residuals | `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md` |
| **T2 Clinical recovery / capability-first** | `clinical_headline` primary; benchmark/CUI diagnostic; gold-quality ceiling on SF/Dx | `docs/research/exectv2_gold_representation_and_scoring_principles_2026-06-17.md` |
| **T3 Architecture / component evidence** | Three families (rules / LLM-only / hybrid); ablatable component homes | `docs/design/architecture.md` |
| **T4 Paper closeout / claims** | C1–C5 capability claims; frozen artifact index governs promotion | `docs/research/paper_claims_evidence_review_2026-07-01.md` |
| **T5 Engineering / experiment governance** | Two-tree rule; registry; predeclare → ladder → frozen index | `docs/runbooks/documentation_lifecycle.md` |

## Language

### Reliability

**Forward-Observable Feature**: Any signal computable at inference time —
single-sample (self-confidence, evidence-exactness, parse-repair count) or
multi-sample (cross-model agreement, self-consistency, semantic entropy) —
without access to the hidden gold label. The strand's central negative result is
that on the binding residual rows the signal separating withhold-to-unknown from
emit-rate is absent from *every* forward-observable feature; only the hidden gold
separates them. This is "[[The Wall]]".
_Avoid_: inference-time signal (unqualified), available feature

**The Wall**: The 0.842 honest accuracy ceiling for this architecture family on
mini, where the binding residual is fixed by a [[Forward-Observable Feature]]
absence rather than a selection or engineering gap. It is the *prior* for the
reliability work: P0.2 (risk–coverage) and P2.1 (semantic entropy) are
falsification tests of the wall, not foregone reframings, and their null
(signal is flat/absent at the residual) is itself the headline finding.
_Avoid_: 0.842 ceiling (as a tuning target), accuracy wall to be broken

**Irreducible Residual**: The portion of holdout error fixed by the wall — rows
with no Purist-correct component and no forward-observable signal to route them
(the 11 no-correct validation rows, 8/11 `band_unknown`). Distinct from
**recoverable error**, which external signals *can* shed on a risk–coverage
curve. Reporting the split between the two is the reframed P0.2 headline.
_Avoid_: hard residual (unqualified), unsolvable rows

**External Risk Score**: The single predeclared composite ordering signal for the
risk–coverage curve, built only from informative [[Forward-Observable Feature]]s:
[[Cross-Model Agreement Count]] (strongest leg), ambiguity-reason count, and the
`source_has_*` residual-shape flags (last_event, since_anchor, trigger,
drop_attack, unable_to_quantify). `selected_evidence_exact` is deliberately
excluded — it is 750/750 True on the routed layer and as degenerate as
self-confidence. Fully available only on validation750; on test450 the agreement
leg degrades to a two-agent consensus, so the holdout replay is weaker, not
identical.
_Avoid_: one of three interchangeable signals, evidence-exactness ordering

**Cross-Model Agreement Count**: Per-row count (3/2/1) of how many structured-event
agents (gpt-4.1-mini + qwen + deepseek) emit the same exact final label, derived
from `consensus_decision.votes` in the validation750 unanimous-exact consensus
artifact and joined to other per-row logs by `source_row_index`. The strongest
leg of the [[External Risk Score]] and the same signal that drove V12's only
positive lift. Lives in the consensus artifact, not the rq9 router file.
_Avoid_: model confidence, self-consistency (that is same-model, see [[The Wall]])

**Semantic Entropy (P2.1)**: A multi-sample [[Forward-Observable Feature]] from
sampling the structured-event extractor k=4–5× at temperature, scored at two
levels on the same samples: a *primary* entropy over the rendered Purist category
(the decision abstention acts on) and a *secondary* entropy over the selected
event kind (`frequency`/`seizure_free`/`unknown`, a more sensitive probe of
upstream wavering). It is the only unrefuted route at the residual because the
honest-ceiling analysis examined single-sample features only. Both H1 (entropy
high at the residual → wall cracks) and H0 (entropy flat → the over-reading is
*confident*, the wall is real and now has a mechanism) are predeclared and
publishable. Gated behind a 25-row degeneracy pre-flight: if exact-evidence gating
makes temperature sampling produce identical samples, entropy is degenerate
everywhere and the experiment is answered before the full run.
_Avoid_: same-model self-consistency (that is [[The Wall]]-confirmed at n=50),
confidence sampling, label-only entropy



**Validation250**: The first 250 rows of the `validation` split from
`gan2026_split_v1`, used as a stronger development signal after the validation
ladder gate is met. It is not a separate stratified panel.
_Avoid_: saved validation250 panel, stratified validation250 panel

**ExtractedCandidate**: A source-near seizure-frequency fact candidate emitted
by extraction before selection, normalization, projection, verification, or
rendering. It may be one of many candidates in a row-level candidate set.
_Avoid_: prediction label, scorer label, selected fact

**CandidateSet**: The collection of extracted candidates available for one row
before a selector chooses the clinically relevant fact or conflict.
_Avoid_: final answer, adjudicated label

**SelectedClinicalFact**: A selector output that chooses the clinically relevant
source-near fact from a `CandidateSet`, or explicitly abstains because the row
is ambiguous, conflicting, lacks reliable evidence, or needs verifier action. It
is upstream of normalization, projection, verification, rendering, and scoring.
_Avoid_: normalized fact, projected label, scorer answer

**Cluster Details**: The part of a cluster-frequency extracted candidate that
records cluster frequency, events per cluster, cluster count, and cluster
period.
_Avoid_: cluster schema, cluster label

**Time Period**: The source-near time basis attached to a seizure-frequency
candidate, such as day, week, month, year, or a range like 7 to 9 days.
_Avoid_: denominator

**Kind-Specific Detail Object**: The candidate detail object selected by
`candidate_kind`, such as `frequency`, `seizure_free`, `cluster_details`,
`unknown_frequency`, or `no_reference`.
_Avoid_: universal frequency details

**LLM Candidate Extraction Role**: The LLM should find source-near clinical
candidate statements, choose broad candidate kind/event type/temporality, and
mark simple certainty. It should not be responsible for parsing counts, ranges,
intervals, durations, ids, spans, source artifacts, or scorer-facing labels.
_Avoid_: LLM parser, LLM final labeler

**Deterministic Normalization Role**: Deterministic code expands source-near
candidate phrases into parsed counts, ranges, time periods, durations, canonical
states, and later projection inputs.
_Avoid_: hidden semantic repair

**Deterministic Candidate Extraction**: Rule-based extraction emits
source-near candidates into a `CandidateSet`. Any legacy deterministic label
carried with the raw candidate is extraction provenance for later normalization
or projection, not a selected clinical fact or final scorer answer.
_Avoid_: deterministic top answer, selected deterministic label

**Compatible-Kind Coverage**: An extract-stage diagnostic that asks whether a
candidate set contains at least one source-near candidate kind compatible with
the gold semantic kind. It is weaker than normalized-label recall and must not
be reported as scorer-facing performance.
_Avoid_: accuracy, label recall, benchmark score

**CandidateSet Union Coverage**: Compatible-kind coverage after combining
candidate sources, such as deterministic and LLM candidate sets, at the row
level. It measures whether any extraction source supplied a compatible
source-near candidate kind; it does not decide selection, normalization,
projection, or scorer-facing correctness.
_Avoid_: ensemble score, final hybrid accuracy

**Candidate Burden**: The number of source-near candidates emitted for one row
before selection. Higher burden can improve extraction coverage but increases
selector ambiguity and should be reported separately from coverage.
_Avoid_: coverage, recall

**High-Recall Extract Mode**: An extract-stage posture that deliberately emits
additional source-near candidates, including vague or uncertain candidates, so
selection and later pipeline stages can decide among them. It accepts higher
candidate burden and must be evaluated separately from selector accuracy.
_Avoid_: final assembly, tuned scoring policy

**Unknown Frequency Candidate**: A source-near extracted candidate indicating
that the note discusses seizure frequency without a usable rate, duration, or
cluster cadence. It is only one possible representation of unknown frequency;
unknown may also be reconstructed downstream from absent reliable evidence,
uncertain candidates, contradictions, or verifier action.
_Avoid_: final unknown label, proof of unknown state

**Unknown By Absence**: A selector abstention that represents unknown frequency
because no reliable current seizure-frequency candidate is available. It is not
the same as selecting an `unknown_frequency` extracted candidate.
_Avoid_: extracted unknown candidate, final unknown label

**VerificationDecision**: A verifier-stage action over structurally valid
upstream clinical-assessment and projection/render objects. It may affirm,
reject, abstain, or require human review for risky clinical or projection
cases, but it does not repair missing drafts, malformed schema output, invalid
candidate references, parse failures, or model call failures.
_Avoid_: schema rescue, output repair, second selector

**Verification Route**: A predeclared issue or risk-family predicate that sends
a structurally valid clinical-assessment or projection/render object to
verification before score outcomes are used. Routes are defined by clinical or
projection risk, not by after-the-fact wrongness or null-label status alone.
_Avoid_: score triage, null-label bucket, post-hoc error filter

**Verifier Action**: The verifier output action for a routed object. `affirm`
accepts the current assessment, projection, or render action; `reject` blocks
an unsupported or unsafe current outcome; `abstain` leaves the row unresolved
because the automated pipeline has no reliable answer; and `human_review`
escalates a meaningful but high-risk, conflicting, or policy-sensitive case
that automation should not own.
_Avoid_: fallback label, repaired answer, hidden override

**Null Rendered Label**: A projection/render output with no scorer-facing label.
It is a symptom of the projection/render state, not a verifier route by itself.
Only null labels caused by a predeclared clinical or projection risk family
should enter verification.
_Avoid_: automatic verifier case, scored wrong row

**Seizure-Free Date Arithmetic**: A deterministic normalization or projection
policy that converts a source-near seizure-free anchor, such as "since January
2024", into a duration when the required dates are available and the anchor is
policy-approved. Date arithmetic is not a verifier job by itself.
_Avoid_: verifier repair, LLM duration inference

**Seizure-Free Conflict**: A verifier-route family where a seizure-free claim is
in tension with active-event evidence, scoped event types, breakthrough events,
or other current seizure-burden facts. Conflict handling belongs to
verification rather than silent projection arithmetic.
_Avoid_: date arithmetic, duration parsing

**Cluster-Axis Ambiguity**: A verifier-route family where it is unclear whether
a cluster statement describes cluster cadence, events per cluster, cluster
duration, or individual seizure frequency. Clear cluster operands belong to
deterministic projection; ambiguous cluster-axis meaning belongs to
verification.
_Avoid_: cluster parsing, deterministic cluster render

**Same-Window Additive Frequency**: A deterministic projection policy that may
sum multiple concrete `frequency_rate` primary facts only when they share the
same time window and compatible event scope. Mixed-window, vague-plus-concrete,
or event-scope-uncertain addition is a verifier or abstention case.
_Avoid_: mixed-window arithmetic, vague arithmetic, context aggregation

**Verifier Rejection**: A verifier action that blocks the current projected or
rendered outcome without inventing a replacement scorer-facing label. Any
replacement must come from a separately named deterministic fallback or action
policy.
_Avoid_: hidden render override, verifier fallback label

**Comparator Preservation Action**: A named fallback or action policy that may
preserve an existing comparator or baseline output after verification judges a
proposed projected outcome risky or unsupported. Comparator preservation is
benchmark/action policy, not clinical truth, verifier repair, or hidden
projection behavior.
_Avoid_: verifier label, projection guard, clinical assessment

**Verification Route Report**: A deterministic validation artifact that lists
structurally valid rows routed to verification by predeclared risk-family
predicates, such as seizure-free conflict, cluster-axis ambiguity,
mixed-window or vague addition, multiple current primary facts, comparator
preservation risk, or policy-sensitive rendered labels. It records route
reasons and trace ids but does not run a verifier model or emit verifier
actions.
_Avoid_: verifier decision report, score error report, Qwen schema report

**Route V0 Determinism Boundary**: The first verification-route artifact is
generated from deterministic predicates over existing validated pipeline
objects. Manual row annotations belong in a separate inspection layer or later
route refinement, not inside the V0 route-generation logic.
_Avoid_: human-coded route logic, mixed manual artifact

**Route Score Context Boundary**: A verification-route report may consume a
score-policy artifact when it already embeds projection/render objects, but
route predicates must be based on clinical-assessment, projection, render, and
predeclared risk fields. Score status and correctness fields are audit context,
not route triggers.
_Avoid_: score-triggered route, wrong-row routing

**Route V0 Predicate Boundary**: The first verification-route predicates map
existing structured contract fields and issue names to predeclared route
families. Candidate text and detail objects may be displayed for trace review,
but V0 route triggering does not parse evidence or discover new clinical facts.
_Avoid_: verifier discovery, second extraction pass, raw-text routing

**Concrete Frequency Precedence**: A deterministic clinical-assessment
normalization rule where a renderable frequency-rate candidate can override a
cluster-framed assessment when the cluster framing is contextual and the
frequency burden is concrete or policy-approved vague frequency from the shared
selected-evidence parser. It must not override already renderable
cluster-burden operands or medication-use cadence.
_Avoid_: cluster erasure, medication cadence as seizure frequency

**Projection Owner**: The named policy authority responsible for turning a
clinical state into a benchmark-facing label, such as rate projection, cluster
projection, boundary projection, or benchmark-only rendering. Projection
ownership must be explicit whenever a label change could be confused with a
clinical extraction decision.
_Avoid_: hidden renderer policy, unattributed final-label change

**Benchmark Renderer**: A projection owner that changes only the
benchmark-facing label convention while preserving the input clinical state.
It may emit scorer sentinels or Gan-specific cluster syntax, but it must not
choose a different clinical fact.
_Avoid_: clinical selector, semantic repair, final-label policy

**Meaning-Preserving Benchmark Projection**: A deterministic projection that
maps a model-selected clinical fact onto benchmark conventions without changing
concept identity, assertion, temporality, frequency state, negation, or
prescription status. It may canonicalize equivalent surfaces, fill
benchmark-required attributes entailed by the selected fact, and collapse
duplicates only within the same declared [[Headline Scoring Unit]].
_Avoid_: prediction-bearing rescue, semantic repair, hidden clinical selector

**Projection Boundary Violation**: A deterministic change that adds a missed
fact, drops an unsupported selected fact, promotes specificity, changes
clinical type, fills a clinically meaningful attribute, or derives
seizure-frequency state without explicit entailment from the selected phrase.
It belongs to a named hybrid rescue or verifier layer, not to
[[Meaning-Preserving Benchmark Projection]].
_Avoid_: aggressive projection, helpful normalization, silent benchmark fix

**Projection Attribution Tag**: A named audit label emitted by any
deterministic rule that changes the scored representation. Tags distinguish
[[Meaning-Preserving Benchmark Projection]] from hybrid rescue and verifier
rejection.
_Avoid_: unlogged repair, implicit rule, anonymous normalization

**Projection-Aware Score Line**: A reported score line that includes
[[Meaning-Preserving Benchmark Projection]] inside the LLM-only clinical
recovery headline while reporting hybrid rescue and verifier-filtered outputs
as separate lines.
_Avoid_: blended benchmark F1, single mixed scoreboard, hidden hybrid score

**Clinical-First Model Output**: An LLM output contract where the model selects
source-supported clinical facts before any benchmark-facing fields are rendered.
The model owns clinical fact selection; deterministic projection owns benchmark
rendering.
_Avoid_: benchmark-first extraction, scorer-shaped model output, direct label imitation

**Benchmark-Mimicry Guardrail**: A prompt and evaluation rule that rewards
source-supported clinical meaning rather than imitation of ExECT annotation
quirks. Benchmark-specific phrase boundaries, ontology surfaces, and guideline
defaults belong to tagged deterministic projection.
_Avoid_: optimize-to-annotation, gold-style guessing, scorer overfitting

**Deterministic Projection Eligibility**: The rule that projection eligibility
is decided by deterministic code from model-selected clinical facts and
attributes. The model supplies clinical structure; it does not self-certify that
a benchmark projection is allowed.
_Avoid_: model-approved projection, self-certified rendering, prompt-only eligibility

**Deterministic Projection Rule Taxonomy**: The named categories that classify
each deterministic rule as LLM-only-compatible projection, hybrid rescue, or
verifier rejection before it affects scored output. No projection rule should
ship without an attribution category.
_Avoid_: ad hoc projection rules, uncategorized normalization, helpful one-off fixes

**Cluster Cadence As Event Rate**: A narrow cluster projection policy where a
clear current cluster cadence may render as a simple seizure-frequency rate
when events-per-cluster burden is absent. It is owned by
`cluster_projection_policy`, must not apply to ambiguous cluster axes,
medication cadence, or contradictory per-cluster evidence, and should carry an
explicit rule id.
_Avoid_: benchmark renderer fallback, cluster erasure, medication cadence

**Medication Cadence Ambiguity**: A verification-route family where cadence
evidence may describe medication use, rescue dosing, or another non-event
schedule rather than seizure or seizure-cluster occurrence. Projection must not
convert this cadence into seizure frequency without reliable event evidence.
_Avoid_: cluster-axis ambiguity, frequency-rate projection, medication cadence as seizure frequency

**Unknown-Cadence Cluster Burden**: A cluster projection state where
events-per-cluster burden is supported, but cluster recurrence cadence is not
known. It may render to an explicit unknown-cadence cluster sentinel only under
a named `cluster_projection_policy` rule; it is not benchmark-renderer
formatting.
_Avoid_: cluster cadence fallback, simple rate projection, hidden sentinel rendering

**Cyclic Vulnerability Window**: A clinical statement that events occur within
a recurring biological or contextual window, such as a perimenstrual interval,
without specifying the number of events in that window. It is not itself a
seizure-frequency count or cluster-burden operand.
_Avoid_: cluster frequency, unknown-cadence cluster burden, inferred event count

**Dominant Vague Current Burden**: A rate projection policy where a vague but
current high-frequency burden, such as events on most weekdays, may be selected
over lower-frequency contextual burden when both labels are derivable and the
vague burden mechanically dominates. It is a named projection policy, not
additive arithmetic.
_Avoid_: mixed-window addition, hidden selector preference, score-only rescue

**Gan2026PipelineRunner (`runner.py`)**: The unified, parameterized runner built
by the Phase F consolidation that executes the deterministic, hybrid, and
fully-LLM architectures as named `PipelineArchitecture` configurations
(`deterministic`, `hybrid`, `llm_only_direct_labeler`,
`hybrid_structured_events`) inside one class, producing the shared
projection/render/score/route/decision artifact contract. New architecture
variants are added as new `PipelineArchitecture` values and `run()` branches
within this framework, not as standalone forked modules.
_Avoid_: separate canonical runner per architecture, bespoke pipeline module

**Canonical Deterministic Pipeline (`deterministic_canonical_pipeline`)**: A
`PipelineArchitecture` configuration on `Gan2026PipelineRunner` that
restructures the existing deterministic logic into four named, stage-owned,
ablatable stages — Extract (raw note text through evidence-anchored
`CandidateEvent`/`CandidateSet` construction), Normalize (label repair and
frequency-record parsing), [[Select & Render]] (selection scoring and
final-label construction), and [[Evidence Trace Check]] — while preserving its
current rules unchanged — a pure staging pass, so a later family-by-family
de-overfitting rewrite (the three-way comparison plan's Section 4) has a
legible, measurable starting point. Each stage is a thin named wrapper
function in `deterministic_canonical_stages.py` over the existing internals
(no new wrapper schemas; existing typed objects already carry rule-id/group/
portability/error trace fields), and its diagnostics dict is kept
key-identical to the existing `deterministic` configuration's — proven
byte-identical by `tests/test_gan2026_deterministic_canonical_pipeline.py`,
the directly assertable "rules unchanged" equivalence guard. It is a
configuration on the consolidated runner substrate, not a fork of a
standalone module.
_Avoid_: Gan2026PipelineV1 (as canonical), staged pipeline_v1, refactored v1,
new diagnostics key shape, per-stage wrapper schemas

**Select & Render**: The combined selection-and-rendering stage name used by
the canonical deterministic pipeline for what `_select_final_event` already
does in one pass — scoring and picking among normalized candidate events, then
constructing the final rendered label and rationale together. It is named
distinctly from the hybrid pipeline's separately-staged `Project`/`Render` seam
(`projection_render.project_and_render`, which produces a `ProjectionDecision`
and a `FinalRenderedLabel` as separate typed objects) because the deterministic
selection logic has no corresponding internal seam between "decide the
projected fact" and "render it" — splitting it to mirror hybrid naming would be
a behavior-risking refactor, not a staging pass.
_Avoid_: Project & Render (for the deterministic canonical pipeline), separate
Project/Render stages here, projection_render.project_and_render (as the model
for this stage)

**Evidence Trace Check**: The canonical deterministic pipeline's new verify-
adjacent stage, wrapping the existing `evidence_is_substring` check (does the
selected evidence string appear verbatim in the source note) plus its
diagnostic-only `AssessmentDraft`/`clinical_assessment` probe as a named,
ablatable stage output — same behavior as today, new seam. It is deliberately
*not* named `Verify` and does not reuse `VerificationDecision`/`Verifier
Action` vocabulary or its `affirm`/`reject`/`abstain`/`human_review` action set:
those are reserved for the hybrid pipeline's verifier stage, which acts on
structurally valid `ClinicalAssessment` and projection/render objects that the
deterministic pipeline does not produce. Naming this stage `Verify` would
silently expand what the deterministic pipeline does (introducing routing/
affirm/reject decisions where none exist), which would make the staging pass a
behavior change wearing a staging-pass costume.
_Avoid_: Verify (for this stage), VerificationDecision (for this stage),
verifier action, affirm/reject/route semantics (here)

**Canonical Fully-LLM Pipeline (`llm_only_canonical_pipeline`)**: A
single-shot `PipelineArchitecture` configuration on `Gan2026PipelineRunner`
(implemented in `llm/llm_only_canonical_pipeline.py`, 2026-06-07 — the
remaining Phase 0 item from the three-way architecture comparison plan) that
collapses extract/select/normalize/project/render into one LLM call, with the
now-mature deterministic rule taxonomy (cluster-axis ambiguity, seizure-free
conflict, same-window additive frequency, and similar named families)
embedded as prompt instructions — under `guidance_for_tricky_cases` in the
prompt payload, written in plain clinical language rather than this
project's internal stage/architecture vocabulary, since the model has no
context for that vocabulary — rather than pre/post processing. It sits alongside, not in place of, the existing
`llm_only_direct_labeler` and `hybrid_structured_events` configurations; it
reports a distinct evidence text-containment metric (`evidence_text_contained`
/ `evidence_text_containment_rate` — does the LLM's free-text evidence string
appear in the source note) rather than the formal `CandidateSet` source-id
validity rate the deterministic/hybrid configurations support, since forcing
it through that machinery would misrepresent what a single-shot LLM
architecture actually produces.
_Avoid_: llm_only_direct_labeler (as the canonical fully-LLM target), fully-LLM
runner, source-id validity rate (for this architecture)

**Model-Facing Prompt Language**: Text an LLM will actually read as part of a
prompt — `Signature` docstrings, `InputField`/`OutputField` descriptions, and
the keys/values/instruction strings inside JSON prompt payloads such as
`build_prompt_input()` — must be a plain, task-oriented brief written for a
reader with no other context about this project, and must not lean on this
project's internal architecture/process vocabulary (extraction, selection,
normalization, projection, rendering, deterministic/hybrid Gan 2026 pipelines,
stage-owned/ablatable rules, rule taxonomy, scored, scorer-facing, downstream,
benchmark, and similar terms from this glossary). Where such a term names a
real constraint, restate the constraint itself in plain language instead of
naming the internal concept. This applies only to model-facing strings —
human-facing text (this glossary, experiment reports, docstrings for humans,
ADRs) should keep using this project's vocabulary precisely. Enforced by
`tests/test_gan2026_llm_prompt_hygiene.py`'s `INTERNAL_MODEL_FACING_PHRASES`;
see
`docs/decisions/0015-model-facing-prompt-language-must-drop-internal-architecture-vocabulary.md`.
_Avoid_: internal-architecture phrasing in prompts, "collapse extract/select/
normalize/project/render", rule-taxonomy framing in model-facing text

**Seizure-Free Proxy Evidence Overreach**: A boundary projection block where
the selected evidence supports only proxy improvement, such as no rescue
medication, no injury, no admission, better control, or conditional future
breakthrough-event planning, rather than explicit no-seizure or no-event
evidence. It must not render a seizure-free duration.
_Avoid_: seizure-free state, duration projection, rescue-medication absence as seizure freedom

### ExECTv2 Scoring

**Prescription Regimen**: The clinical medication fact for an active
anti-seizure prescription, consisting of medication identity, dose, dose unit,
and frequency when stated or guideline-defaulted. Its evidence phrase may be a
source-near medication span, but the regimen is the clinical object being
recovered.
_Avoid_: medication mention, raw prescription phrase, drug name only

**Future Medication Diagnostic**: A diagnostic layer for planned, titration,
target-dose, or future anti-seizure medication statements that contain regimen
facts but are not current prescriptions. It is a *one-way, non-penalizing* route:
a model-flagged future medication is recorded here instead of as a
[[Prescription Clinical Headline]] false positive, but it never earns headline
credit. Because the gold has no temporality column, the Prescription headline is
scored against the as-annotated (temporality-blind) gold and this route exists so
correct temporality reasoning is not punished by it.
_Avoid_: current prescription, false positive prescription, discarded plan evidence

**Weight-Based Dosing Diagnostic**: A diagnostic layer for Prescription evidence
that states dose by body-weight basis, such as `mg/kg/day`, rather than as an
absolute administered `mg` or `g` dose. It is clinically meaningful dosing
evidence, but it is not the same component object as an absolute current regimen
dose.
_Avoid_: absolute DrugDose, current regimen tuple dose, discarded dosing evidence

**Clinical Medication Identity**: The clinically equivalent medication concept
used for Prescription component scoring, where brand names, generic names, and
common spelling variants may resolve to the same anti-seizure medication.
_Avoid_: literal DrugName string, CUI identity, brand-only identity

**Clinical Component Score**: A diagnostic score for a decomposable clinical
fact component, such as Prescription medication identity, dose, frequency, or
complete regimen tuple, evaluated apart from exact ExECT mention phrase and CUI
projection.
_Avoid_: benchmark score, headline F1, exact mention match

**Prescription Clinical Headline**: The primary clinical Prescription score,
combining accepted current-regimen component shapes such as ordinary
[[Complete Regimen Tuple]]s and [[Rescue Medication Regimen]]s. Supporting
component scores remain diagnostics rather than parallel headline claims.
_Avoid_: every component as headline, benchmark Prescription F1, name-only success

**Decomposable Clinical Object**: An ExECTv2 entity target whose clinical fact
naturally breaks into meaningful bound components, such as a medication regimen
or an investigation with performed/result/type fields. Component scoring should
be used for these objects, not forced onto entities where only phrase,
assertion, time, or projection diagnostics are clinically meaningful.
_Avoid_: symmetry-driven component score, fake component layer, component score for every entity

**Complete Regimen Tuple**: A bound Prescription component key containing
clinical medication identity, dose, dose unit, and frequency from the same
regimen mention. It is the component score that supports "regimen recovered"
language; isolated name, dose, or frequency scores diagnose partial recovery
only.
_Avoid_: unbound component match, letter-level ingredient match, any-component recovery

**Split-Dose Regimen**: A Prescription regimen where one medication has multiple
source-stated dose slots, such as different morning and evening doses. In the
clinical component layer each slot is a separate [[Complete Regimen Tuple]],
while benchmark projection may still merge or split the surface mention.
_Avoid_: combined dose blob, single averaged dose, benchmark split/merge convention

**Rescue Medication Regimen**: A Prescription component shape for rescue or PRN
anti-seizure medication where medication identity plus `As_Required` frequency
can be a valid regimen even when no dose is stated. Dose may be recorded when
present, but absence of dose should not turn the rescue fact into an ordinary
complete-tuple failure.
_Avoid_: ordinary complete regimen tuple, missing-dose failure, non-prescription PRN mention

**Guideline-Defaulted Frequency**: A Prescription frequency value supplied by
the ExECT annotation guideline when the source does not state a schedule, such
as once daily by default or `As_Required` for rescue medication conventions. It
is benchmark projection, not source-stated schedule extraction.
_Avoid_: recovered frequency, stated schedule, clinical schedule evidence

**ExECT Mention Projection**: The benchmark-facing representation that turns a
clinical fact into an ExECT mention key: entity, normalized phrase text, and the
non-ignored attribute bundle, including CUI for the benchmark surface. It is a
projection policy, not the same thing as clinical fact recovery.
_Avoid_: clinical extraction, raw gold text, scorer normalization

**Phrase-Scope Mismatch**: A projection gap where the predicted and gold ExECT
mentions refer to the same clinical fact but choose different phrase boundaries,
such as a medication regimen span versus a section-prefixed span.
_Avoid_: clinical miss, evidence miss, fuzzy match

**Prescription Phrase Projection**: The ExECT mention projection policy for
Prescription that uses the clinically bounded medication regimen span as mention
text and excludes section headings, list labels, and surrounding sentence
context.
_Avoid_: full section phrase, heading-inclusive prescription text, raw-gold imitation

**CUI Projection**: The benchmark-format step that attaches the CUI expected by
the ExECT mention surface. It should be reported separately from clinical
component recovery because ontology convention can change benchmark F1 without
changing the recovered clinical fact.
_Avoid_: medication extraction, semantic correctness, clinical understanding

**Prescription Benchmark Projection**: The ExECT mention projection layer that
turns a recovered Prescription regimen into the benchmark-facing `DrugName` and
CUI convention. It is separate from [[Clinical Medication Identity]] because
brand/generic equivalence can be clinically correct while still differing from
the benchmark ontology surface.
_Avoid_: clinical medication identity, component recovery, raw ontology lookup

**Clinical Recovery Headline**: The primary ExECTv2 score for an entity,
measuring recovery of the clinical fact, with [[ExECT Mention Projection]] and
[[CUI Projection]] demoted to a separately-credited artifact layer beneath it.
Decomposable entities take a [[Clinical Component Score]] headline; atomic-concept
entities take a [[Concept-Identity Headline]]. This is the deliberate move away
from all-entity exact-phrase F1 as the scoreboard, made because that metric is
largely a target-construction artifact (oracle ceiling ~0.42).
_Avoid_: all-entity exact-phrase F1 as headline, benchmark item F1 as the scoreboard

**Concept-Identity Headline**: The [[Clinical Recovery Headline]] for
atomic-concept entities (Diagnosis, Onset, WhenDiagnosed, EpilepsyCause,
BirthHistory). Credit = clinical concept recovered + assertion attributes
(Negation, surviving Certainty), scored *source-entity-agnostically* — any pass
that surfaced the concept counts — with phrase boundary demoted to projection.
DiagCategory is supplied by [[Deterministic Normalization Role]] (named seizure
type → category), not demanded from the model's own entity tag.
_Avoid_: per-entity exact-mention match, entity-tagged recall, model-must-tag-the-entity credit

**Concept Recovery Unit**: The unit a [[Concept-Identity Headline]] scores.
Split coordinated same-kind concepts into atomic facts — a compound "X with Y"
is two required facts — but collapse a specificity hierarchy to the most-specific
concept — `epilepsy` vs `focal epilepsy` is one fact; generic-only is a clean
miss, not partial credit. The rule: split = different facts, collapse = same fact
at different granularity; split fires only on coordinated *same-kind* clinical
concepts, never on a qualified single concept.
_Avoid_: phrase-level unit, generic+specific both required, partial-credit on specificity

**Frequency State Recovery**: The state-level [[Clinical Recovery Headline]] for
SeizureFrequency: per-current-seizure-type recovery over {active-rate,
seizure-free, unknown}, matched on seizure-type/CUI (EA0011's two types are two
facts), with `unknown` a first-class TP-able state rather than a scoring void.
Exact counts, ranges, and time periods are separate [[Clinical Component Score]]
diagnostics where the quantification wall lives openly — never the headline.
_Avoid_: per-letter single state, exact-count headline, unknown as scoring void

**Coverage-Diagnostic Entity**: An ExECTv2 entity reported only as
[[CandidateSet Union Coverage]], not as a [[Clinical Recovery Headline]], because
it is a heterogeneous catch-all whose "recovery" would measure generation breadth
rather than recovery of a defined clinical object. PatientHistory is the case in
point: recall-bound (most golds absent from the candidate pool) and open-ended
(any past clinical concept with a time anchor).
_Avoid_: PatientHistory headline F1, scored grab-bag entity

**Headline Scoring Unit**: The de-duplicated, entity-specific unit the
[[Clinical Recovery Headline]] actually scores, distinct from the raw ExECT
mention. SeizureFrequency reduces every mention to `(seizure_type, state)` and
de-duplicates (`scoring._frequency_state_keys`), so two mentions of the same
seizure-free type are one unit; Diagnosis reduces to the [[Concept Recovery
Unit]]. Any per-letter exploration surface must report match status and family
counts against this unit, never the raw mention multiset — the two disagree on
exactly the letters that carry duplicates, which is what makes a raw-mention
drill-down contradict the headline chips above it.
_Avoid_: raw ExECT mention as the scored unit, per-mention multiset counts as the
exploration-surface truth

**Redundant-Convention Duplicate**: Two or more raw gold mentions that reduce to
the *same* [[Headline Scoring Unit]] because they differ only in a
headline-demoted attribute — e.g. EA0044's two `seizures` SeizureFrequency
mentions at the *same offset* differing only in `PointInTime` (LastClinic vs
DrugChange) on one seizure-free state. The headline de-duplicates them, so a model
that emits one is fully correct and is *not* charged for the second. The
exploration surface keeps the extra raw copies visible but badges them "removed
from headline scoring - deduplicated". It carries no additional clinical fact.
_Avoid_: required duplicate target, missed gold, [[Distinct-Assertion Duplicate]]

**Distinct-Assertion Duplicate**: Two or more raw gold mentions of one concept at
*distinct offsets* — genuine repeat textual assertions (e.g. EEG in the
Investigations heading and again later in the letter body). Per the duplicate-FN
analysis (gold-representation principles P5 / all-9 Finding 3) the published
offset-based benchmark counts each, so the [[Clinical Recovery Headline]]
*preserves* them rather than collapsing — Investigations is not de-duplicated
(corpus 136 = 136). They are therefore NOT badged "removed from headline scoring".
The contrast with [[Redundant-Convention Duplicate]] — same scoring unit vs. same
concept at distinct offsets — is the load-bearing distinction the exploration
surface must keep legible.
_Avoid_: [[Redundant-Convention Duplicate]], headline-collapsible duplicate,
cheap recall ceiling
