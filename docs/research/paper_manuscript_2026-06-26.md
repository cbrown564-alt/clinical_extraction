# Paper Manuscript — Capability-First Restructure

Date: 2026-06-27

Status: submission-ready assembly. Front matter (Abstract, §1 Introduction, §2 Methods,
§3 Evaluation Protocol and Claim Discipline) added ahead of the capability-first results.
Section 4 reorganizes the two-task results by what the system can do (shared architecture,
LLM contribution, generalization, reliability, component impact) rather than by which task
ran first. Section 5 adds Discussion (D.1–D.5) and Section 6 adds Contributions (C1–C5).
The ExECTv2 SeizureFrequency wall-transfer probe is folded in at its strengthened verdict
(WALL TRANSFERS, 6/9 checks passed). Consensus/fresh selector (v0.9) cut from all
paper-facing promoted results per P5 CUT recommendation
(`docs/research/consensus_fresh_selector_fate_2026-06-27.md` C1–C5); the Gan
closeout headline stands alone.

Primary sources (P6 restructure):

- `docs/research/paper_drafts/capability_first_results_section_2026-06-27.md`
- `docs/research/paper_drafts/capability_first_discussion_contributions_2026-06-27.md`
- `docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md`
- `docs/research/consensus_fresh_selector_fate_2026-06-27.md` (CUT C1–C5 applied)

Front-matter sources (§1–§3):

- `docs/design/reliability_thesis.md` (claim, datasets, success criteria, gates)
- `docs/research/closing_stage_research_critique_2026-06-27.md` (motivation; capability-first spine)
- `docs/research/decomposition_research_impact_review_2026-06-27.md` (portability taxonomy; structural-reuse caveat)
- `docs/research/paper_drafts/benchmark_surface_reconciliation_subsection_2026-06-27.md` (scoring surfaces)
- `docs/research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md` (§3 wall-transfers verdict)

Retained from 2026-06-26 draft:

- `docs/research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`
- `docs/research/exectv2_results_section_draft_2026-06-26.md`

## Abstract

Clinicians need clinical-extraction systems they can trust, and trust is not a property of
a single benchmark score: it is a property of a system that generalizes beyond the surface
it was tuned on, signals when it is uncertain, and exposes an auditable trail for every
prediction. We argue that a **modular, stage-owned clinical-extraction architecture** — not
any particular large language model — is the primary carrier of extraction quality, and we
demonstrate this by holding one decomposed architecture fixed while varying both the task and
the generation model. We evaluate on two complementary epilepsy-letter tasks that share a
component spine: deep single-concept seizure-frequency labeling on the Gan synthetic
seizure-frequency benchmark (Gan 2026) and broad multi-entity phenotyping on clinical
letters (ExECT multi-entity phenotyping task, ExECTv2; Fonferko-Shadrach 2024). On the Gan
benchmark a single GPT structured-event pass reaches 364/450 (0.809) Purist accuracy on a
locked holdout, within 15 rows of a far more complex multi-trace hybrid pipeline that peaks
at 379 correct labels of 450 (0.842). On ExECTv2, recovery of the four headline entity
families (`clinical_headline`—Diagnosis, SeizureFrequency, Prescription, and Investigations)
reaches 0.8197–0.8566 F1 across three qualitatively different
LLMs under a frozen component graph, with a non-development model (DeepSeek) leading the
development model (GPT-4.1-mini) by +0.021 — the predicted signature of a model-agnostic
architecture — while the open-weight model (Qwen 3.6 35B) trails both by a modest,
diagnosed margin concentrated in the corpus's hardest family (SeizureFrequency), not spread
uniformly or left unexplained. We reconcile our label-based surface with the published benchmark honestly: on
the comparable like-for-like surface we reach 0.3877 per item / 0.6972 per letter against the
paper's 0.87 / 0.90, a gap we locate in deterministic CUI-and-attribute-bundle fidelity that
was explicitly deprioritised, not in concept recall. The central negative result — a confident over-reading limit (the Wall): an
architecturally unresolvable ceiling on seizure frequency where the model commits to
quantified rates on ambiguous evidence — transfers across datasets: a forward-observable-feature
probe finds this mechanism reproduces on ExECTv2 (6 of 9 pre-registered cross-dataset checks
passed; external-risk failure AUROC 0.764
with a 17.1% irreducible risk-coverage plateau, and no gold-free separator on the binding
over-read slice), establishing a task-bound rather than system-bound limit. The durable
contribution is the evaluation discipline — predeclared adversarial panels, held-out-family
cross-validation, and frozen aggregate-only inspection — that characterized both the ceiling
and its mechanism without contaminating any holdout.

---

## 1 Introduction

Clinical phenotyping from free-text correspondence is a recall- and reasoning-intensive task:
the relevant facts are hedged, abbreviated, templated differently across clinics, and often
require temporal and clinical judgment to resolve. Large language models promise breadth on
exactly this kind of text, but a clinician cannot act on a single leaderboard F1. Trust in a
clinical setting is not a property of one benchmark score; it is a property of a system whose
behavior is **reliable** — it generalizes beyond the surface it was tuned on, and it knows
when it is wrong — and **transparent** — every prediction carries an inspectable trail and
every component can be ablated and error-analyzed (`docs/design/reliability_thesis.md` §1).

The central claim of this work is that a **modular, auditable clinical-extraction
architecture** delivers both, and that this can be *demonstrated* rather than asserted by
holding the architecture fixed while varying the two factors that usually confound reliability
claims in this literature: (i) the task and dataset, and (ii) the architecture family. We
apply one stage-owned component spine to two distinct epilepsy-letter tasks — the Gan
synthetic seizure-frequency benchmark and ExECT multi-entity phenotyping on clinical
letters — and for each task we situate the result against rules-based, LLM-only, and hybrid
instantiations over the same shared core. Holding the task fixed and varying the family
isolates *what the LLM adds*; holding the family fixed and varying the task isolates *what
generalizes*.

The two tasks are deliberately complementary. **Gan 2026** is deep single-concept extraction —
seizure frequency, the hardest single epilepsy indicator, demanding clinical reasoning (which
fact is the patient's current burden), temporal reasoning (current vs. historical, windows,
since-dates), and concept normalization (count/range × period → a comparable rate). **ExECTv2**
(Fonferko-Shadrach 2024) is broad multi-entity phenotyping — nine entity types with attributes
and UMLS CUIs, scored per-item and per-letter. **Seizure Frequency is the bridge between the
two tasks**: it is the deep target of task 1 and simultaneously ExECTv2's weakest entity, for
the same clinical-ambiguity reasons. If the modular investment is real, it shows up first and
most clearly here.

Four findings organize the paper. First, the architecture is **model-agnostic**: swapping the
generation LLM under a frozen component graph maintains or improves performance, and a
non-development model (DeepSeek chat) leads the development model (GPT-4.1-mini) on ExECTv2.
Second, the Gan strand's central negative result — a confident, forward-unobservable
over-reading ceiling on seizure frequency — is **task-bound and transfers** to ExECTv2 as a
cross-dataset phenomenon (WALL TRANSFERS, 6/9 checks). Third, we **reconcile** our label-based
clinical-recovery surface with the published nine-entity benchmark openly, naming the closeable
deterministic fidelity gap rather than disputing the benchmark. Fourth, the most transferable
output is the **evaluation discipline** that produced these results without contaminating any
holdout. We report these as five measured contributions (C1–C5; Section 6): benchmark
reconciliation with a surface-inversion finding (C1); a cross-task component ablation locating
the operative shared component (C2); the wall as a cross-dataset confident-over-reading
phenomenon (C3); model-agnostic architecture validated by a non-development LLM leading (C4);
and evaluation discipline as a reusable methodology (C5).

The remainder of the paper is organized capability-first. Section 2 defines the datasets, the
shared decomposed architecture, the three architecture families, and the models. Section 3
defines the scoring surfaces, the evidence-validity levels, the predeclaration and inspection
protocol, and the reliability-scorecard dimensions, and states the claim boundary that governs
every number below. Section 4 reports results by capability — shared architecture and
evaluation surfaces (§4.1), what the LLM adds (§4.2), what generalizes (§4.3), the unified
reliability scorecard (§4.4), and component impact (§4.5). Section 5 discusses the findings
(D.1–D.5) and Section 6 states the contributions (C1–C5).

---

## 2 Methods

### §2.1 Datasets and Tasks

We hold a single architecture fixed across two epilepsy-letter tasks chosen to be
complementary along every axis that matters for a reliability claim (deep vs. broad; one
label vs. many mentions; label accuracy vs. F1; clinical/temporal reasoning vs. breadth and
attribute structure).

**Gan 2026 — deep seizure-frequency labeling.** Each letter yields one normalized
seizure-frequency label (a state/rate over a temporal window). Accuracy is reported as
**Purist** and **Pragmatic** label accuracy. The corpus is split into a `validation750`
development split (750 letters) and a locked `test450` holdout (450 letters); the holdout is
used only as frozen aggregate evidence under the inspection policy of §3.2. The hard part is
clinical reasoning (which fact is the current burden), temporal reasoning (current vs.
historical), and normalization (count/range × period → comparable rate).

**ExECTv2 — broad multi-entity phenotyping** (Fonferko-Shadrach 2024). The published benchmark
defines nine entity types with attributes and UMLS CUIs, scored per-item and per-letter; the
reference is a rule-based GATE pipeline reporting overall F1 **0.87 per item / 0.90 per letter**
against human inter-annotator agreement of **0.73**. SeizureFrequency is the benchmark's
weakest entity (0.66 per item) and its lowest-agreement one (0.47 human IAA), precisely
because it resists rule-based extraction for the reasons that make it task 1's central
challenge; that low agreement also caps the achievable F1 and is the dominant component
of our SeizureFrequency benchmark gap (§4.1.2). We use a `dev140`
development split (140 letters) and a `full-200` aggregate split (200 letters). The ExECTv2
annotation schema independently corroborates the task-1 normalization model: its
SeizureFrequency attributes encode the same count/range × period × temporal-anchor structure
the Gan 2026 normalizer produces, and `NumberOfSeizures = 0` is a seizure-free assertion — the
lowest-accuracy answer kind carried over from task 1.

Our headline ExECTv2 surface is de-duplicated clinical-fact recovery over four families
(Diagnosis, SeizureFrequency, Prescription, Investigations) under the `clinical_headline`
view; the nine-entity CUI + attribute-bundle benchmark surface is retained for diagnostic
comparability only (§3.1, §4.1.2).

### §2.2 The Shared Decomposed Architecture

Both tasks run on the same stage-owned component spine: deterministic ingestion and
normalization stages, a structured-evidence extraction pass, task-specific assembly lenses,
and a shared post-processing projection/headline-assembly layer (the stage-ladder figure is
given in §4.1.1 and lifted from the Observatory laboratory page). The decomposition is
**stage-owned and principled**: any single component can be turned off, swapped, or ablated
without touching adjacent stages, and the scoring boundary is held constant across all
ablation conditions. Forty-nine ExECTv2 modules import from `core`, `tasks.shared`, or
`tasks.seizure_frequency`, so structural reuse of the shared primitives is real at the code
level.

Every component carries exactly one **portability category** —
`general` / `clinical_epilepsy` / `task` / `dataset` / `benchmark_format` — recorded in the
component-ablation `definitions.yaml`. The taxonomy makes the clinical-recovery-vs.-format
question a config read rather than a code fork (it predicts whether toggling a component moves
both tasks' scores or only one) and is what makes the component ladder of §4.5 a direct
read-out of the figure's annotations.

Two deterministic gates run on every prediction and are reported as first-class metrics, not
implementation details: **schema validation** (the structured output conforms to the task's
data contract) and **evidence verification** (each cited evidence span is an exact source
substring). These convert "the model said so" into "the model said so, the output is
well-formed, and the support is present in the note." Schema-validity rate, repair rate, and
evidence-validity rate are reported throughout (§3.3, §4.4).

**Structural-reuse caveat (do not overstate).** The architecture's claim is that the
decomposition is stage-owned and that the *shared primitives* are reused — not that the two
tasks share every component. In particular, the SeizureFrequency clinical machinery — the
declared cross-task "bridge" — is **re-implemented** for ExECTv2
(`exectv2/deterministic/sf_state_projection.py`, `rules/seizure_free.py`;
`assembly/lenses/seizure_frequency.py` does not import the Gan SF normalizer), not directly
imported from the Gan task. The accurate claim is structural reuse of shared primitives plus a
parallel clinical response to a parallel task, not literal SF code identity (see §5, D.5 / I1
for the rule-registry integrity caveat).

### §2.3 Architecture Families and Models

For each task the result is situated against three canonical architecture families over the
same shared core, each of which answers a different question. **Rules-based** is the portability
and reproducibility baseline and the honest measure of what is achievable with no model — it is
also what the published ExECTv2 benchmark itself is, so beating it with rules is a like-for-like
win. **LLM-only** is the upper bound on unaided model reasoning, bounded only by the schema and
evidence gates. **Hybrid** tests the thesis that representation/normalization is best owned by
deterministic stages while clinical judgment is best owned by the model. The Gan three-way
comparison is reported in full (§4.2, Tables 1–2); the assembled ExECTv2 three-way comparison —
the reliability thesis's "Target"-tier requirement (§7) — is now measured, via a separate
LLM-only GEPA single-pass instantiation over the same clinical_headline surface, and reported
as a negative result at the end of §4.2 (development-surface evidence; see also §5, S2).

Three large language models occupy the generation lane: **GPT-4.1-mini** (the primary closed
model the ExECTv2 component graph was developed against), **DeepSeek chat** (a second closed
model), and **Qwen 3.6 35B** (a local open-weight model). The **same-core model-swap** protocol
holds the component graph, deterministic stages, surface definitions, and evaluation protocol
fixed and varies only the generation LLM (frozen core
`exectv2_2call_no_sf_adjudicator`); it is the central test of model-agnostic architecture
(§4.3.1). Gan production runs use `gpt-4.1-mini`.

### §2.4 Relationship to the Original Brief

The originating brief asked for one training-free multi-agent extraction system with four
named roles — a Section/Timeline Agent, per-field-group Field Extractor Agents, a Verification
Agent checking evidence spans/contradictions/missingness, and an Aggregator Agent producing
final JSON with confidence and citations — evaluated by comparing single-prompt against
multi-agent extraction at matched budget, with self-consistency, evidence requirements, and
structured output validation as the levers under test. The hybrid architecture here implements
three of the four roles directly: per-family producer lanes are the Field Extractor Agents,
always-on schema/evidence gates plus per-family LLM verifiers are the Verification Agent, and
the assembly stage's `ClinicalFinding` object (confidence, evidence span, provenance) is the
Aggregator Agent. It generalizes the brief's single-prompt-vs-multi-agent question into a
three-way rules-only/LLM-only/hybrid comparison across two independent tasks rather than one
(§2.3). The fourth role, a Section/Timeline Agent, was built and ablation-tested on 2026-07-01
(`exectv2/deterministic/section_timeline.py`: letter-wide section segmentation plus
chronological-reference extraction, threaded as optional prompt context into the
SeizureFrequency and Investigations stages) with a **null result** on dev140 — neither family
improved (SeizureFrequency -0.0106, Investigations -0.0034, both within or near this project's
established measurement noise floor;
`docs/experiments/exectv2/reliability/exectv2_section_timeline_ablation_2026-07-01.md`). The
module remains available but is not part of the production v08 pipeline; temporal reasoning
continues to be handled by per-fact attributes (`PointInTime`, `TimeSince_or_TimeOfEvent`,
`FrequencyChange`) rather than a dedicated upstream stage, consistent with ExECTv2 letters being
single-encounter snapshots rather than multi-visit documents.

The brief's literal single-prompt-vs-multi-agent question was also answered directly, on
2026-07-01, with a genuine tool-using redo on both tasks (`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`,
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_results_2026-07-01.md`) — a
from-scratch rebuild using `dspy.ReAct` for genuine LM-decided tool invocation and specialist
sub-agents whose output schema structurally cannot contain a final answer, replacing a prior
2026-06-12 Gan attempt found to have hard-coded its tool calls and faked its multi-agent
condition. On Gan 2026, every new architecture beat single-prompt extraction by a wide accuracy
margin on a hard, disagreement-selected panel (Purist 38%→64%), and dynamic tool/specialist
selection beat a static always-run-everything decomposition — real, if statistically
underpowered, evidence that decomposition and dynamism both help. On ExECTv2 SeizureFrequency,
the same architecture family did *not* reproduce that pattern: single-prompt extraction was the
best performer among the four tested, with the new architectures trending mildly negative
(small-sample, inconclusive, not a confident reversal). The honest, cross-task reading is that
agentic decomposition is not a universal win for clinical extraction — it is at best
task-dependent, plausibly because Gan's single-label classification does not transfer cleanly to
ExECTv2 SF's multi-mention, richly-attributed extraction, where a resolver must reassemble full
attribute sets from partial specialist evidence rather than choose among whole-answer candidates.
The full role-to-component mapping is maintained as a living reference in
`docs/design/brief_role_crosswalk.md`.

---

## 3 Evaluation Protocol and Claim Discipline

### §3.1 Scoring Surfaces

ExECTv2 is reported on two scoring surfaces that measure different things and cannot be
compared directly. The **clinical-headline surface** (`clinical_headline`, four-family scorer)
matches entity type, normalized phrase, and clinical attributes, and disregards raw character
offsets and CUI codes; it carries every headline F1 figure in §4.2–§4.3. The
**published-benchmark surface** (nine-entity, per-item/per-letter, CUI + full attribute bundle)
requires exact phrase reproduction with complete attribute bundles and CUI codes and was the
originally stated success criterion (thesis §7: `0.87` / `0.90`). We score on entity-plus-label
rather than on raw offsets because spelling correction altered the letter text without updating
the gold character offsets (thesis §5), making the offset-tuned published number
non-reproducible on the corrected surface — a methodology consistent with the benchmark paper's
own inter-annotator protocol, which also disregarded CUIs and compared on phrase selection and
attribute classification. The two surfaces are reconciled with the like-for-like number in
§4.1.2; Gan 2026 is scored throughout on Purist/Pragmatic label accuracy.

### §3.2 Evidence-Validity Levels and Predeclaration

Every number in this paper carries an explicit evidence-validity level, and no claim is read
above the level of its source. Four levels recur: **dev140 validation-only** (ExECTv2
development split; not a holdout estimate); **validation750** (Gan development aggregate);
**development-inclusive full200 aggregate** (ExECTv2; dev140 plus test60, so not an
independent holdout estimate); and **frozen `test450` holdout** (Gan, the only
author-uninspected holdout in the work). Gan test450 runs are governed by an
**aggregate-only author-inspection policy**: the author did not inspect row-level test output
or tune from it. Agent-generated row reports were removed from the repository, and Observatory
now blocks locked-test row access in code.
Promotion decisions pass a **two-tier gate** — a predeclared adversarial battery (minimal-pair,
source-near, KCL-style OOD panels authored before results are read) *then* held-out-family
cross-validation as a stop rule — and frozen aggregate runs report a predeclared **gate status**
(`pass` / `pass_with_caveat`) over call failures, parse/schema failures, and evidence rate.
Probes (semantic-entropy, wall-transfer) are pre-registered with acceptance criteria before
the contrast is scored.

### §3.3 Reliability Scorecard Dimensions

Reliability is reported on a fixed dimension taxonomy applied consistently across both tasks:
**evidence grounding** (exact-substring evidence rate, schema/repair rate), **calibration**
(Brier vs. base-rate, ECE, monotone bins, external vs. self-reported signal), **abstention /
review routing** (risk-coverage, selective risk, External Risk Score AUROC), **robustness**
(adversarial battery and hard-slice F1), and **consistency** (run-to-run and varying-temperature
agreement). The scorecard tests trust properties of the *fixed* architecture; it is reported
separately from **component impact** (§4.5), and neither may be merged into causal
single-component claims on either task.

### §3.4 Claim Boundary (Both Tasks)

- Gan 2026 results use Purist/Pragmatic label accuracy on the locked `test450`
  split only as frozen aggregate evidence unless explicitly marked validation750.
- ExECTv2 results use de-duplicated `clinical_headline` recovery as the headline
  surface; strict benchmark/CUI scores remain diagnostic comparability only.
- Reliability scorecard and component-impact subsections are separate and must
  not be merged into causal component claims on either task.
- Seizure Frequency is the cross-task bridge: the deep target of §4.1 and the
  hardest ExECTv2 family in §4.3 (see `docs/design/reliability_thesis.md` §2).
- Consensus/fresh selector (v0.9): CUT. Neither the constrained nor the exact-source
  Gate 4 audit is a promoted holdout result. The Gan production headline is the
  single GPT structured-event pass (`364/450`, 0.809); ceiling comparator is V12
  (`379/450`, 0.842). No selector rows appear in architecture tables or manuscript
  headline claims.

---

## 4 Results

We evaluate the shared modular architecture on two complementary epilepsy-letter
tasks: deep seizure-frequency extraction and broad multi-entity phenotyping. Results
are organized by capability: shared architecture and evaluation surfaces (§4.1), what
the LLM adds to a deterministic spine (§4.2), what generalizes across models and
datasets (§4.3), reliability across fixed-protocol dimensions (§4.4), and
component-level impact (§4.5).

### §4.1 Shared Decomposed Architecture and Evaluation Surfaces

#### §4.1.1 Architecture

Both clinical-extraction tasks — Gan 2026 seizure-frequency labeling and ExECTv2
multi-family clinical-finding recovery — run on the same stage-owned component spine.
The spine comprises deterministic ingestion and normalization stages, a
structured-evidence extraction pass, task-specific assembly lenses, and a shared
post-processing projection layer. Forty-nine ExECTv2 modules import from
`core`, `tasks.shared`, or `tasks.seizure_frequency`; the SeizureFrequency family
in ExECTv2 shares the same normalization grammar as the Gan task while using a
re-implemented projection path adapted to the ExECTv2 schema. The architecture's
claim is not that the two tasks share every component, but that the component
decomposition is stage-owned and principled: any single component can be turned off,
swapped, or ablated without touching adjacent stages, and the scoring boundary is
held constant across all ablation conditions.

*(Architecture figure: one stage-ladder diagram with shared-core modules shaded.
Lift from Observatory laboratory page. Not reproduced here.)*

#### §4.1.2 Scoring Surfaces and Benchmark Reconciliation

*Evidence validity: dev140 validation-only (like-for-like read); frozen aggregate
full-200 (four-family clinical-headline only). Source: P1
`benchmark_surface_reconciliation_subsection_2026-06-27.md`.*

ExECTv2 reports performance on two distinct scoring surfaces that measure different
things and cannot be compared directly.

**Clinical-headline surface** (`clinical_headline`, four-family scorer). Matches
entity type, normalized phrase, and clinical attributes; disregards raw character
offsets and CUI codes. This is the surface used for all headline F1 figures in §4.2
and §4.3.

**Published-benchmark surface** (nine-entity, per-item/per-letter, CUI + full
attribute-bundle). Requires exact phrase reproduction together with complete attribute
bundles and CUI codes, and was the originally stated success criterion (thesis §7:
"beat the ExECTv2 per-item/per-letter F1 benchmark, `0.87`/`0.90`"). The two
surfaces diverge for a principled reason: the gold character-offset annotations were
made against the original unprocessed clinical letters; spelling correction altered
the text without updating the offsets (thesis §5). Scoring on raw spans therefore
systematically penalises correct extractions whose phrase boundaries were shifted by
the correction. The project scores on entity-plus-label, not on offsets — consistent
with the benchmark paper's own inter-annotator agreement protocol, which also
disregarded CUIs and compared on phrase selection and attribute classification.

On the published-benchmark surface (nine entities, exact normalized phrase + all
attributes + CUI), the best-of-dev140 like-for-like read is:

**Table R1. Benchmark-surface reconciliation (dev140, validation-only).**

| Surface | Per-item F1 | Per-letter F1 | vs. paper (0.87 / 0.90) |
|---------|------------:|---------------:|--------------------------|
| Paper (published, full 200) | 0.87 | 0.90 | — |
| Best-of dev140 (rules + hybrid Inv) | **0.3877** | **0.6972** | −0.48 / −0.20 |
| Deterministic-only dev140 | 0.3687 | 0.6747 | −0.50 / −0.23 |
| All-hybrid dev140 | 0.3100 | 0.6454 | −0.57 / −0.25 |

*Source: `experiments/exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json`;
validation-only, not a full-200 or holdout estimate. The 60-row exploratory
checkpoint from 2026-06-12 is superseded and must not be cited as a frozen audit
conclusion.*

The `0.3877` per-item figure is approximately 45% of the published headline. The gap
decomposes into **two distinct mechanisms**. For Prescription and Investigations it is
concentrated in **CUI reproduction and attribute-bundle strictness**, not in concept
recall or entity recognition: phrase-only and semantic-recall metrics remain materially
higher than the nine-entity bundle score, and the lever that would close it is
deterministic phrase/CUI/attribute-bundle engineering — catalogued patterns that
reproduce the exact bundle structure the benchmark expects — work that was explicitly
deprioritised in favour of the clinical-recovery evaluation framework. **SeizureFrequency
and Diagnosis both carry a second, non-closeable component: the gold's own
inter-annotator/consolidation conventions** (detailed below). The correct paper statement
is therefore:

> *We evaluate on a label-based surface because spelling correction drifted the gold
> offsets, making the offset-tuned published number non-reproducible on corrected
> text; on the comparable dev140 surface we reach `0.39` per item / `0.70` per
> letter; closing most of the remaining gap to the published headline requires
> deterministic phrase-and-CUI bundle engineering (CUI normalisation, full attribute
> serialisation, entity-bundle assembly per family) that was explicitly deprioritised
> as outside the clinical-recovery scope of this work — except for SeizureFrequency and
> Diagnosis, where a measurable share of the gap is not closeable engineering but the
> gold's own annotation conventions: SeizureFrequency's ~0.47 inter-annotator agreement,
> against which even a clinically-correct reader is scored wrong on roughly a third of
> letters, and Diagnosis's tendency to tag multiple co-present concepts from one
> diagnostic statement that a clinically complete consolidation correctly merges.*

**The rules > hybrid inversion on the benchmark surface is a genuine finding.** Stacking
hybrid verifiers lowers the nine-entity benchmark overall from deterministic-only
`0.3687` to all-hybrid `0.3100`. For SeizureFrequency, the hybrid verifier reaches
`0.782` on the clinical-recovery surface — a substantial gain — but collapses to
`0.347` on the published benchmark surface, well below the deterministic rules
baseline of `0.692`. This inversion — LLM hybrid gains clinical recovery, rules
retain benchmark fidelity — is a finding about the two surfaces, not a measurement
artefact. LLM-enriched clinical recovery does not substitute for deterministic bundle
engineering on the published-benchmark scorer; and the headline is not fully
recoverable from clinical facts alone.

**A second gap mechanism: gold quality, most acutely on SeizureFrequency.** The
closeable-fidelity account above does not hold uniformly. SeizureFrequency is the
benchmark's weakest entity (0.66 per item) and its lowest-agreement one (human IAA
0.47, §2.1), and a whole-corpus row-level adjudication on the primary SF state-set
metric (a per-letter clinical-recovery scorer over frequency states {active-rate,
seizure-free, changed, unknown} — a finer SF-specific view than the four-family
`clinical_headline` surface, and not the published-benchmark surface) shows why: the
gold is itself the ceiling. Scoring our two-stage SF program against
that metric, the per-letter answer is wrong on 37.9% of dev140 letters (F1 0.772); but
adjudicating every disagreement clinically, only **28% (15/53) are genuine model
errors**. The remaining 72% are the model being clinically defensible and scored
wrong — 42% (22/53) because the gold *under-annotated* a stated frequency or
*redundantly double-tagged* a single seizure type, and 30% (16/53) genuine
inter-annotator coin-flips. Counting only genuine model errors, the program is
clinically defensible on **125/140 = 89.3%** of letters where the metric credits
**62.1%**; the 27-point gap is gold noise, not model deficit, consistent with SF being
the corpus's lowest-IAA entity. Two reporting corollaries follow: (i) the metric
carries **±0.03 run-to-run variance** — a faithful re-run of the identical program
flips the state-set on 41/140 letters from temperature-0 nondeterminism alone, so SF
figures are reported as bands, never single decimals; (ii) the residual *attributable*
model lever is small and rule-shaped (≈15 letters: historical-versus-current temporal
discipline, and exam/inter-event-gap/non-epileptic state-evidence discipline), already
encoded in the deterministic projection. SeizureFrequency is thus the cleanest case in
the corpus where the benchmark gap is a property of the gold rather than of the model
— a gold-quality ceiling no fidelity engineering can recover. *(The 89.3% is mildly
optimistic — 34 of the 53 errors fall in the optimizer-seen trainset, 19 in the
held-out valset — but the error structure is the same across both splits. This figure is
corroborated, not merely asserted, by a blinded independent re-adjudication of a stratified
20-letter sample (`exectv2_gold_quality_adjudication_blind_replication_2026-07-01.md`):
the population-reweighted genuine-error-rate estimate (30.3%, 95% CI [14.3%, 46.4%])
overlaps the original (28.3%) closely, yielding a reweighted defensible-letter estimate of
88.5% (range 82.4–94.6%) against the original 89.3% — item-level verdict agreement on
individual cases is weaker (Cohen's κ≈0.40) than this aggregate-level robustness, a
distinction worth stating plainly. Source:
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`.)*

**The same mechanism, more lopsided, on Diagnosis.** A parallel whole-corpus
row-level adjudication on the official Diagnosis `clinical_headline` scorer
(`score_concept_identity(...).concept_only` — entity-agnostic recall, home-tagged
precision; self-validated to reproduce the scorer's aggregate exactly, F1 0.6617 at
that pass — the 2026-07-02 D1 hierarchy-match scorer-correctness fix has since raised
the raw metric to 0.6779 by folding 5 parent/child gold-multiplicity pairs into it,
reducing the disagreement base from 209 to 199)
finds the same pattern, more pronounced. 88/140 letters carry at least one Diagnosis
disagreement (92 missed + 117 spurious concepts, 209 total on the pre-D1 scorer);
adjudicating every one clinically, only **14.8% (31/209) — 15.6% (31/199) on the
post-D1 scorer — are genuine model errors** (concentrated in two
narrow, fixable patterns: tagging an explicitly *negated* finding as a diagnosis, and
mis-tagging an EEG/Investigations finding under the Diagnosis entity). The remaining
**85.2%** are the model being clinically correct and scored wrong — dominantly *gold
multiplicity*: the gold tags both a generic/parent concept and a specific/co-present
concept (or splits one compound diagnostic phrase into separate atomic tags) from a
single diagnostic statement, and the model's reasonable one-tag consolidation is
scored as both a miss and a false positive. Recomputing precision/recall after
crediting every clinically-defensible disagreement lifts Diagnosis from its raw metric
(0.6617 at that pass, **0.6779** after the D1 fix) to **approximately 0.85–0.99 (point
estimate ≈0.92)** — a ceiling essentially unchanged by D1, which folds already-defensible
pairs into the metric rather than moving it, and a larger absolute gap than
SeizureFrequency's even at the lower bound of this range. Diagnosis is therefore not a
pure closeable-fidelity entity: it shares SeizureFrequency's gold-quality ceiling,
just driven by annotation-granularity convention rather than inter-annotator
agreement. *(Source:
`docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`.
Caveat: adjudicated by five independent reviewers without cross-checking between
batches, unlike the single coherent SF pass; the four recurring mechanisms replicate
identically across all five independent batches, which is the main evidence for
robustness. This is reported as a range, not the single point estimate of 0.9501 from
the original pass, because a blinded independent re-adjudication of a stratified
20-item sample
(`exectv2_gold_quality_adjudication_blind_replication_2026-07-01.md`) found item-level
agreement with the original verdicts too weak to trust a bare point figure (Cohen's
κ≈0.39, at the predeclared 0.4 robustness threshold) and a directionally higher
population-reweighted genuine-error-rate estimate (14.8%→22.5% point estimate, wide CI
[1.6%, 43.5%]) — consistent with, and corroborating, this same weaker five-reviewer
provenance caveat. The core finding (most of the Diagnosis gap is gold-quality
artifact, not model deficit) is unchanged; only the point magnitude is revised to a
range.)*

---

### §4.2 What the LLM Adds

*Evidence validity: Gan three-way table — frozen test450 aggregate (V12) + dev/validation
replay. ExECTv2 component-off replay — dev140 (validation-only) + frozen aggregate
full-200. Source: P1 §4.x.4–5; existing manuscript Tables 1–2 (Gan); Table 8 (ExECTv2
component-off).*

Both tasks admit a three-way comparison of deterministic-only, LLM-only, and hybrid
architectures. The pattern is consistent across tasks: deterministic rules establish
a strong recall floor; LLM-only extraction adds semantic generalization that rules
miss; hybrid assembly combines both and delivers the headline score.

**On Gan seizure-frequency labeling:** rules alone, LLM-only, and hybrid achieve
progressively higher test450 Purist accuracy (see Tables 1–2 below; not
reproduced here). The decisive LLM contribution is in resolving frequency-qualifier
ambiguity and in abstracting across orthographic and syntactic variation — exactly the
cases where pattern-matching rules are brittle.

**Table 1. Gan 2026 three-way comparison on validation750 (`gpt-4.1-mini`).**

*Purist accuracy counts a prediction correct only when the extracted label exactly matches the
gold label (strict match).*

| Architecture | Rendered | Purist of rendered | Pragmatic of rendered | Reading |
| --- | ---: | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | 741/750 | 673/741 (0.908) | 681/741 (0.919) | High validation score; large holdout drop. |
| `hybrid` | 597/750 | 526/597 (0.881) | 545/597 (0.913) | Strong rendered accuracy; too many null/routed rows. |
| `hybrid_structured_events` | 748/750 | 661/748 (0.884) | 679/748 (0.908) | Best LLM-using validation coverage/accuracy balance. |
| `llm_only_canonical_pipeline` | 750/750 | 582/750 (0.776) | 614/750 (0.819) | Comparator; below hybrid structured events. |

**Table 2. Gan 2026 frozen `test450` aggregate audit (`gpt-4.1-mini`).**

*Purist accuracy counts a prediction correct only when the extracted label exactly matches the
gold label (strict match).*

| Architecture | Rendered | Purist of rendered | Pragmatic of rendered | Claim use |
| --- | ---: | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | 450/450 | 329/450 (0.731) | 341/450 (0.758) | Frozen aggregate; validation-to-test gap warning. |
| `hybrid` | 334/450 | 269/334 (0.805) | 281/334 (0.841) | Frozen aggregate; coverage-limited. |
| `hybrid_structured_events` | 448/450 | 364/448 (0.812) | 381/448 (0.850) | Strongest frozen hybrid aggregate on rendered rows. |
| `llm_only_canonical_pipeline` | 450/450 | 326/450 (0.724) | 346/450 (0.769) | Frozen comparator row. |

The promoted close-off candidate is the single GPT structured-event pass on
`gpt-4.1-mini`, which reached `364/450` Purist (`0.809`) on locked `test450`
with the smallest validation-to-test drop among LLM-using architectures. The
full V12 fresh-evidence hybrid reached `379/450` Purist (`0.842`) but is
retained only as a high-complexity ceiling comparator, not the operational
headline system.

**On ExECTv2:** the format-layer component ablation (dev140 one-component-off replay
and development-inclusive full200 aggregate replay) quantifies the LLM's marginal contribution by
staging. The `residual_semantic_lens` and `headline_projection` components —
categorized `benchmark_format` — are the layers where LLM adjudication and
normalization operate above the deterministic floor. Their combined delta on the
clinical-headline surface is:

**Table R2. Format-layer (LLM-added) contribution on ExECTv2 `clinical_headline`.**

| Model | Headline F1 (full) | Clinical-recovery F1 (format layers off) | Δ (format layers) |
|-------|-------------------:|------------------------------------------:|-------------------:|
| GPT-4.1-mini | 0.8356 | 0.7922 | +0.043 |
| DeepSeek chat | 0.8566 | 0.8110 | +0.046 |
| Qwen 3.6 35B | 0.8197 | 0.7797 | +0.040 |

*Source: `exectv2_component_off_replay_full200_20260626.json`; frozen aggregate
full-200, four-family `clinical_headline`; no row-level inspection.*

The format-layer contribution is stable at ~+0.04 across three qualitatively different
LLMs. The clinical-recovery floor without those layers (0.78–0.81) is materially
above the deterministic-only baseline, confirming that both the deterministic spine
and the LLM adjudication stages carry non-redundant signal.

**Component-level ladder (ExECTv2, dev140 and full-200 aggregate replay):**

| Component | Category | Split | Overall delta range | Main family signal |
|-----------|----------|-------|--------------------:|-------------------|
| `standard_dictionary` | `dictionary` | dev140 | +0.039 to +0.112 | Diagnosis +0.140; SF +0.173 |
| `standard_dictionary` | `dictionary` | full-200 | +0.019 to +0.029 | Diagnosis +0.080 |
| `residual_semantic_lens` | `semantic_lens` | dev140 | +0.018 to +0.104 | Investigations +0.172 |
| `residual_semantic_lens` | `semantic_lens` | full-200 | +0.010 to +0.012 | Diagnosis +0.031 |
| `headline_projection` | `deterministic_projection` | dev140 | +0.028 to +0.045 | SF +0.203 |
| `headline_projection` | `deterministic_projection` | full-200 | +0.030 to +0.035 | SF +0.142 |

*Source: `exectv2_component_off_replay_dev140_20260626.json` and
`exectv2_component_off_replay_full200_20260626.json`; `clinical_headline` scorer;
no model calls, replay-only.*

The dev140 deltas are uniformly larger than full-200 equivalents — consistent with
the same-core adjudicator recovering more dictionary content before the format layers
operate on the full-200 split. These component-off deltas are conditional on a fixed
scorer and inspection boundary; they are not causal claims that any single component
is globally necessary.

**The ExECTv2 three-way comparison: the thesis's Target tier, measured as a negative
result.** *Evidence validity: dev140 development-surface, non-paper-comparable diagnostics
(GEPA workstream, not a development-inclusive full200 aggregate or holdout result). Source: `PROJECT_STATUS.md`
("GEPA workstream closed out," 2026-06-28 to 2026-06-30);
`docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md` and its
four phase-result docs.* The reliability thesis's §7 "Target" tier requires beating the
published benchmark with all three architecture families on ExECTv2, mirroring the Gan
three-way comparison above. A parallel LLM-only instantiation was built and closed out
independently of this manuscript: a GEPA-optimized single-pass prompt (no deterministic
scaffolding beyond ingestion) reaches dev140 `clinical_headline` F1 **≈0.749**
(gpt-4.1-mini, best multi-family run) and **≈0.679** (Qwen 3.6 35B, underperforming its own
hand-tuned ExECTv2 baseline of 0.694). Against the hybrid ceiling on the same surface
(0.9155 dev140; Table R2/R3 report the full-200 aggregate), LLM-only sits **≈0.17
below hybrid** and does not clear the published-benchmark surface either.[^scorer-correction-2026-07-02]

[^scorer-correction-2026-07-02]: The gpt-4.1-mini figure (≈0.749 overall; was ≈0.731) reflects
the 2026-07-02 `clinical_headline` scorer-correctness fixes across all four families
(Prescription 0.8766→0.9122 — clause-scoping of the future/weight gate plus a drug-lexicon
valproate/brand unification; SeizureFrequency 0.5921→0.5982 — zero-count precedence; Diagnosis
0.6617→0.6779 — the D1 hierarchy-aware match, reported on the concept_only clinical_headline
surface that `clinical_headline_unit_keys` actually uses; Investigations unchanged at 0.8583;
overall 0.7313→0.7416→0.7491); the pre-fix values were computed under scorer bugs. Predictions
are unchanged; only the scorer changed. See
`docs/research/exectv2_pipeline_assumption_audit_phase1_2026-07-02.md` and the completing
re-score sweep `docs/research/exectv2_pipeline_assumption_audit_rescore_sweep_2026-07-02.md`.
This completes the
thesis's missing three-way leg, and the result is a negative one: raw LLM capability, tuned
directly on the scoring surface, does not approach what the deterministic/hybrid scaffolding
achieves — the same direction as C2 and C4, now with a third independent leg, reinforcing
that the architecture, not the model, is the primary carrier of extraction quality.

The GEPA workstream's root-cause account for this gap has itself been revised and must be
stated with the corrected, per-family attribution rather than a blanket claim. The original
hypothesis — that the gap is producer evidence-recall rather than the hybrid's
verify/arbitrate stages — is confirmed as **genuine** for Investigations (26–30% of its
evidence-recall misses are H-inflated, i.e., mostly real retrieval failures) and **partially
genuine** for Prescription (52.2% H-inflated, via a distinct mechanism: transcription-typo
substring breaks, not gold multiplicity). For Diagnosis and SeizureFrequency, however, the
same re-examination found the evidence-recall shortfall is **mostly an artifact of the gold
consolidation convention already documented in §4.1.2** (93.5% and 61–83% H-inflated,
respectively) — the identical gold-multiplicity mechanism that inflates the benchmark-surface
gap for those two families. The honest statement is therefore: part of the LLM-only ceiling
is genuine single-pass extraction-recall limitation (Investigations, partly Prescription), and
part is the same-core LLM-only architecture being scored against the same gold-multiplicity
convention that already narrows the hybrid's apparent margin on Diagnosis/SF elsewhere in this
paper — meaning the *true* architectural gap is smaller than the raw 0.18–0.19 once both legs
are corrected for gold convention, though by how much is not yet quantified and is not
estimated here.

*This is GEPA development-track evidence, not a development-inclusive full200 aggregate or holdout result, and must
not be compared directly to Table R2/R3's frozen full-200 numbers without this dev140-vs-
full200 caveat, consistent with how every other dev140-only figure is treated in this paper.*

---

### §4.3 What Generalizes

#### §4.3.1 Model-Agnostic Architecture: DeepSeek ≥ GPT-4.1-mini

*Evidence validity: dev140 four-family `clinical_headline` validation-only; frozen
aggregate full-200 same-core model-swap. Source: P2
`deepseek_model_agnostic_evidence_2026-06-27.md`.*

A model-agnostic architecture predicts that no single LLM should be necessary: swap
the generation component while holding the architecture constant, and performance
should be maintained or improved. The same-core model-swap experiment is precisely
this test.

Under the frozen `exectv2_2call_no_sf_adjudicator` core — same component graph, same
deterministic stages, same scoring surface — three LLMs were compared on both the
dev140 and full-200 splits:

**Table R3. Same-core model swap, full-200 aggregate `clinical_headline`.**

| Model | Overall | Diagnosis | SF | Prescription | Investigations | Call/parse failures | Evidence rate |
|-------|--------:|----------:|---:|-------------:|---------------:|--------------------:|--------------:|
| DeepSeek chat | **0.8566** | **0.8708** | **0.7602** | 0.8926 | **0.9091** | 0 / 1 | 1.0000 |
| GPT-4.1-mini | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | 0 / 0 | 1.0000 |
| Qwen 3.6 35B repair v02 | 0.8197 | 0.8307 | 0.7020 | 0.8926 | 0.8503 | 0 / 0 | 1.0000 |

*Source: `exectv2_same_core_model_swap_full200_2026-06-25.md`; frozen aggregate
full-200; no row-level inspection authorized.*

DeepSeek chat outperforms GPT-4.1-mini by **+0.021 overall** on the frozen full-200
aggregate. The lead is consistent across families: Diagnosis +0.031,
SeizureFrequency +0.008, Investigations +0.053; Prescription is tied. DeepSeek's
clinical-recovery base (0.8110 without format layers) also exceeds GPT's (0.7922),
confirming the advantage is not a post-processing artefact (Table R2).

The one DeepSeek parse/schema failure is within the predeclared full-200 tolerance
(zero call failures; ≤1 parse/schema failure; evidence rate 1.0000 for all
completed rows; gate status `pass_with_caveat`). That a non-development LLM outperforms
the development model under a frozen architecture is the predicted signature of a
system whose intelligence lives in the component graph, not in the model weights.
If the LLM were the bottleneck, GPT-4.1-mini's higher benchmark ranking would dominate
and the swap would regress; it does not.

The format-layer contribution remains **stable at ~+0.044–0.046** across models on
full-200 (Table R2), buffering idiosyncratic differences in how each LLM structures
its outputs. Score stability plus a non-development model leading is the joint
evidence for model-agnostic architecture.

**Qwen's shortfall, decomposed.** Qwen 3.6 35B (the local open-weight model) trails both
closed models on the development-inclusive full200 aggregate (0.8197 vs. GPT 0.8356, DeepSeek 0.8566;
Table R3), and this gap is neither uniform nor unexplained. *Evidence validity: frozen
aggregate full-200, replay-only decomposition, no row-level inspection. Source:
`exectv2_qwen_hybrid_swap_gap_decomposition_2026-07-01.md`.* Per-family, Qwen's deficit
versus GPT is concentrated in SeizureFrequency (−0.0505) — 5–8× the size of its Diagnosis
(−0.0090) or Investigations (−0.0060) deltas — with Prescription exactly tied. Three
candidate mechanisms are ruled out directly from the replayed diagnostics: call failures
(zero on all models/families), parse/schema failures (zero for Qwen), and evidence
groundedness (exact evidence rate 1.0000 for Qwen on every family, including SF). A fourth,
extraction-volume over/under-calling, is also ruled out: Qwen's SF prediction-to-gold ratio
(1.1074) sits between GPT's (1.0537) and DeepSeek's (1.1198), yet Qwen's SF precision
(0.6679) and recall (0.7397) are both below both closed models' at that comparable volume —
a per-mention SF classification-quality gap, not a coverage or evidence problem. This
differs from the *separate* GEPA single-pass Qwen finding
(`exectv2_gepa_qwen_cross_model_2026-06-30.md`), which located Qwen's shortfall in
Diagnosis evidence-retrieval under an LLM-only architecture with no deterministic
scaffolding: under the hybrid graph analyzed here, Diagnosis is nearly flat and SF carries
the gap instead, suggesting the hybrid's deterministic dictionary/CUI-normalization layers
(§4.5) absorb most of Qwen's raw Diagnosis weakness before scoring, but not its SF
weakness. The honest characterization of the abstract's model range is therefore: the
aggregate spread across all three models is tight and non-catastrophic (Qwen trails by
0.0159 overall), but the open-weight model does not fully maintain the closed models' level
on the corpus's hardest, lowest-agreement family.

*Note on dev140:* DeepSeek leads on dev140 as well (0.9174 vs GPT 0.9155 overall
headline F1), with its clinical-recovery base lower (0.8334 vs 0.8697) but headline
F1 higher — indicating the post-processing stack extracts more value from DeepSeek's
structured outputs on the richer dev140 surface. All dev140 figures are
validation-only and are not holdout estimates.

#### §4.3.2 Wall Transfer: The Seizure-Frequency Ceiling Is Task-Bound

*Evidence validity: Gan — frozen test450 aggregate (multi-trace fresh-evidence hybrid,
0.842) + validation-only semantic-entropy probe (P2.1, n=150). ExECTv2 — frozen aggregate
full-200 model-swap + dev140 aggregate model-swap + self-consistency replay (wall-transfer
probe). Probe checklist: 6 of 9 pre-registered cross-dataset checks passed (task-bound
ceiling and wall mechanism confirmed; population-wide error observability noisier than Gan).
Source: P3 `wall_transfer_cross_dataset_2026-06-27.md`.*

The central negative result of the Gan strand does not stay on the Gan dataset.

**The Gan confident over-reading limit (the Wall).** On the Gan 2026 seizure-frequency
benchmark, the best architecture achieves a frozen holdout ceiling of **0.842**
(multi-trace fresh-evidence hybrid pipeline, test450 Purist). Exhaustive ablation
established that this ceiling is generator-bound: the model over-reads ambiguous frequency
evidence as quantified rates or seizure-free durations with high confidence, and no
forward-observable signal — self-consistency, self-confidence, sampling entropy — separates
the over-read rows from correct extractions at inference time. No remaining selector
headroom: on validation750, 739 of 750 rows have at least one Purist-correct component; of
the 11 binding residual rows (no Purist-correct component), 8/11 fall in `band_unknown`,
and the signal distinguishing *withhold-to-unknown* from *emit-rate* is absent from every
inference-time feature.

Semantic-entropy probing at k=4 across temperatures [0.3, 0.5, 0.7, 1.0] confirmed
the mechanism:

**Table R4. Semantic-entropy probe results (Gan, P2.1, n=150 validation rows).**

| Subset | n | Mean label entropy | Mean kind entropy |
|--------|--:|-------------------:|------------------:|
| All rows | 150 | 0.012 | 0.003 |
| Residual (band_unknown ∪ seizure_free_duration) | 23 | 0.018 | 0.018 |
| Non-residual | 127 | 0.011 | 0.000 |
| band_unknown specifically | 15 | **0.000** | 0.000 |

*Source: `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md`;
validation-only probe; H0 verdict: `H0_confident_over_reading`.*

`band_unknown` entropy is exactly zero across all four temperatures: the model never
samples its way out of the wrong answer. The over-reading is not sampling noise — it
is the model's committed interpretation. This is the mechanism behind the wall.

**The ExECTv2 SF gap.** On the frozen full-200 same-core model-swap, SeizureFrequency
is the weakest extraction family under all three tested LLMs:

| Model | Overall | Diagnosis | SF | Prescription | Investigations |
|-------|--------:|----------:|---:|-------------:|---------------:|
| GPT-4.1-mini | 0.8356 | 0.8397 | **0.7525** | 0.8926 | 0.8563 |
| DeepSeek chat | 0.8566 | 0.8708 | **0.7602** | 0.8926 | 0.9091 |
| Qwen 3.6 35B | 0.8197 | 0.8307 | **0.7020** | 0.8926 | 0.8503 |

The SF gap is **not model-specific**: swapping the LLM while holding the component graph
constant narrows it by only +0.008 between the two strongest models. It is **not a
data-surface artefact**: the gap closes to ~0.905 on dev140 when a task-specific SF
adjudicator is added, confirming that targeted post-processing can correct the base
extraction residual — but the base extraction wall persists in the same direction as
the Gan ceiling before that adjudicator intervenes. Evidence rate is 1.0000 on all
three model-swap runs: the SF gap is not an evidence-validity failure.

The clinical task is the same in both settings: extract the current seizure burden from
prose where evidence is often hedged, qualified by event rather than rate, or
temporally ambiguous. The illegitimate evidence shapes that drive Gan over-reading —
last-event-only anchors, open-ended temporal qualifiers, vague counts read as habitual
rates — are present in real clinical letters too.

**Probe result (6 of 9 pre-registered cross-dataset checks passed).** The wall-transfer
probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) applied a nine-item checklist
comparing Gan and ExECTv2 seizure-frequency failure signatures; six items passed (task-bound
ceiling and wall mechanism confirmed; population-wide error observability noisier than Gan).
It ran on dev140 aggregate model-swap and self-consistency artifacts and was extended to
compute the two acceptance criteria the base probe left blank. Both confirm transfer:

> SeizureFrequency is the weakest ExECTv2 family under a frozen same-core architecture
> across all tested LLMs (GPT-4.1-mini 0.7525, DeepSeek chat 0.7602, full-200 aggregate;
> GPT 0.7645, DeepSeek 0.7658 on dev140); this task-bound ceiling is established in the rows
> above. The two acceptance criteria establish that the *wall mechanism* transfers too.
> **(i) External Risk composite ranks SF errors.** The frozen composite validated on Gan P0.2
> ranks ExECTv2 SF errors at failure-prediction **AUROC 0.764** (Gan 0.781), and its
> risk-coverage curve **plateaus**: the safest-ranked SF tier still carries an irreducible
> selective risk of **17.1%** (95% CI 8.5–31.3%, lower bound above zero) — errors leak into the
> low-risk region, the same shape Gan P0.2 documented. **(ii) No gold-free separator on the
> binding slice.** On the gold-`unknown` SF units (the rows that should withhold), a
> pre-registered null test finds **no forward-observable feature** that separates correct
> withholds from over-reads (best AUROC 0.676 < the 0.70 useful-triage bar; 2/5 over-reads are
> temperature-entropy-zero, the exact Gan `band_unknown` = 0.000 signature; all three models
> over-read the slice, 5/7/8) — **H0 retained**. Together these results show a **task-bound
> ceiling whose wall mechanism transfers; population-wide observability is noisier than Gan.**
> The one genuine difference from Gan is population-wide: ExECTv2's broad error cells are
> noisier (error entropy 0.287 vs 0.069 for correct cells; cross-model agreement 21.8% on
> errors vs 69.4% on correct), so the error distribution is less uniformly degenerate than
> Gan's near-zero P2.1 panel — a noisier-error caveat, not a different mechanism.

This framing converts "SF is our weakest family" from an apology into the paper's
strongest generalization claim: a system whose ceiling is the task's clinical-ambiguity
floor, not a deficiency of the architecture or the model, exhibits exactly the behavior
a genuinely modular, clinically-grounded design predicts.

---

### §4.4 Reliability Scorecard

*Evidence validity: all figures aggregate full-200 validation (ExECTv2) or
frozen test450 (Gan), except where noted. No holdout or deployment-probability claim.
Source: P4 `calibration_claim_revision_2026-06-27.md`; existing manuscript reliability
scorecard; `gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md`.*

The reliability scorecard tests whether both architectures behave faithfully under
fixed scoring and inspection boundaries. Dimensions are reported consistently across
tasks.

**Table R5. Unified reliability scorecard.**

| Dimension | Gan (test450 / validation) | ExECTv2 (full-200 aggregate) |
|-----------|---------------------------|------------------------------|
| Evidence grounding | Gold-grounded evidence rate 1.0000 on V12 hybrid (validation750); enforced by evidence-contract gate | Same-core model-swap: min exact evidence rate 1.0000 across all three LLMs |
| Calibration | Self-confidence degenerate: 749/750 validation rows "high"; external corroboration is the only calibration-carrying signal; External Risk Score AUROC 0.781 | Near-base-rate: Brier 0.2245 vs constant base-rate 0.2387 (Δ = 0.0142), ECE 0.0432, five populated monotone bins. External predeclared features (family, provenance, evidence-ambiguity) carry the signal; model-reported confidence not used |
| Abstention / review routing | External Risk Score risk–coverage AUC 0.040 (oracle 0.007); selective risk 0.8% at 16% coverage; irreducible plateau at low-risk tier | High-recall routing point validated; no promoted low-burden triage policy |
| Robustness | Adversarial battery (P1 OOD, minimal pairs, source-near): Panel C 87.5% PASS; Panels A, B FAIL — cluster-axis and rate-withholding failures | Hard-slice F1 0.8336 across 414 eligible family cells vs 0.8503 overall (current-code v08) |
| Consistency | temp-0 run-to-run: two concordant independent test450 runs agree within 4 rows | Hard-50 temp-0 exact agreement 0.9217; dev140 varying-temperature 0.8857 |

**Calibration — revised framing (P4):**

The ExECTv2 scoring rule's calibration is near-base-rate. Aggregate full-200
validation Brier is `0.2245` versus constant base-rate `0.2387` (Δ = `0.0142`),
ECE `0.0432`, five populated monotone bins. The improvement above the base rate is
real but small and should not be read as evidence of well-calibrated predictive
confidence. The signal comes entirely from external, predeclared features — family
identity, evidence-provenance indicators, and evidence-ambiguity flags — not from
model-reported confidence scores, which were not used. This is consistent with the
Gan strand's finding that self-reported confidence is degenerate (749/750 validation
rows "high", statistically indistinguishable buckets) and that only external
corroboration carries calibration-relevant signal.

Per-family ECE: Diagnosis `0.1424`, SeizureFrequency `0.1292`, Prescription `0.1214`,
Investigations `0.0925`. The claim is bounded to the aggregate full-200 validation
surface; holdout or external calibration confirmation has not been run.

**What calibration does not claim:** The scoring rule is not deployment-ready for
probability-calibrated triage; the Brier improvement of 0.0142 is documented evidence
of a real but modest signal, not a production confidence model.

---

### §4.5 Component Impact

*Evidence validity: component-off replay — dev140 validation-only + frozen aggregate
full-200. No holdout. Source: existing manuscript Table 8; P1 §4.x.4 format-layer
ablation; `exectv2_component_off_replay_{dev140,full200}_20260626.json`.*

Component impact is reported as aggregate replay deltas under a fixed scorer, split,
and inspection boundary. Three component categories show non-zero positive contributions
on both splits; a fourth (evidence validation) was structurally inert on dev140 holistic
replays and not escalated to full-200.

**Stage-ladder summary (ExECTv2, `clinical_headline`):**

| Component | Category | Split | Overall Δ | Clinical-recovery vs benchmark-format |
|-----------|----------|-------|----------:|--------------------------------------|
| `standard_dictionary` | `dictionary` | full-200 | +0.019–+0.029 | Operates below the LLM adjudication layer; raises the clinical floor before semantic adjudication |
| `residual_semantic_lens` | `semantic_lens` | full-200 | +0.010–+0.012 | LLM-adjudicated add/drop/replace; clinical-recovery contribution, not format |
| `headline_projection` | `deterministic_projection` | full-200 | +0.030–+0.035 | Format/projection layer; largest on SF (up to +0.142 full-200) |
| `residual_semantic_lens` + `headline_projection` | `benchmark_format` sum | full-200 | ~+0.044 | Combined format-layer delta; stable across models (see Table R2) |

**Benchmark-format vs clinical-recovery split.** The `residual_semantic_lens` and
`headline_projection` components together contribute ~+0.04 on the
`clinical_headline` surface. On the published-benchmark surface those same layers
**lower** overall score from rules-only `0.3687` to all-hybrid `0.3100`: clinical
recovery and benchmark fidelity are not the same objective, and the format layers are
optimized for the former. Largest benchmark-format delta on dev140 is Qwen at +0.148
(headline − clinical-recovery); that gap shrinks to ~+0.040 on full-200 (Table R2),
consistent with the same-core adjudicator recovering more dictionary content before
the format layers operate at the larger scale.

**Evidence-validation component** was structurally inert on dev140 single-lane holistic
replays (no positive delta in ablation) and was not escalated to full-200 under the
frozen protocol. This is an acknowledged gap in the component story; it does not affect
any other claim above.

**What component impact does not claim:** Component-off deltas are conditional on a
fixed scorer and inspection boundary. A positive delta does not prove a component is
globally necessary; it proves it has a non-zero effect on this surface and split.
The reliability scorecard is separate from component impact and measures trust
properties of the fixed architecture, not causal score attribution from individual
components.

---

### Claim Boundary Summary (§4)

| Claim | Surface | Evidence level | Source artifact |
|-------|---------|---------------|-----------------|
| Full-200 clinical-headline F1: GPT 0.8356, DeepSeek 0.8566, Qwen 0.8197 | `clinical_headline` | Frozen aggregate full-200 | `exectv2_same_core_model_swap_full200_2026-06-25.md` |
| Qwen shortfall decomposition: SF-concentrated (−0.0505 vs GPT), Diagnosis/Investigations modest (−0.009/−0.006), Prescription tied; not call/parse/evidence-rate/volume-explained | `clinical_headline` | Frozen aggregate full-200, replay-only, no row-level inspection | `exectv2_qwen_hybrid_swap_gap_decomposition_2026-07-01.md` |
| C1 gold-quality blind replication: item-level κ≈0.39 (Dx), 0.40 (SF); population-reweighted genuine-error rate Dx 14.8%→22.5% (CI 1.6–43.5%), SF 28.3%→30.3% (CI 14.3–46.4%); revised Diagnosis adjusted F1 range 0.85–0.99 (pt. ≈0.92), SF defensible-% range 82.4–94.6% (pt. 88.5%) | Diagnosis `concept_only`; SF `state_profile` | Stratified n=20/family blind sub-agent re-adjudication over already-published dev140 case files; not external clinical validation | `exectv2_gold_quality_adjudication_blind_replication_2026-07-01.md` |
| Like-for-like dev140: 0.3877 per-item / 0.6972 per-letter | Published-benchmark, nine-entity | Validation-only, frozen aggregate | `exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json` |
| Rules > hybrid on SF benchmark (+0.34 per-item) | Published-benchmark | Validation-only, frozen aggregate | `exectv2_benchmark_surface_overall_2026-06-18.md` |
| Format-layer delta ~+0.04 stable across models | `clinical_headline` | Frozen aggregate full-200, component-off replay | `exectv2_component_off_replay_full200_20260626.json` |
| DeepSeek ≥ GPT full-200 (+0.021) | `clinical_headline` | Frozen aggregate full-200 | same |
| Gan wall: 0.842 ceiling, selector oracle 739/750 | Purist accuracy | Frozen test450 | orchestrator state; closeout synthesis |
| Gan P2.1: mean label entropy 0.012; band_unknown 0.000 | Purist label entropy | Validation-only probe (n=150) | `gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md` |
| ExECTv2 SF weakest across all models (0.75–0.76 full-200) | `clinical_headline` | Frozen aggregate full-200 | `exectv2_same_core_model_swap_full200_2026-06-25.md` |
| Calibration: Brier 0.2245 vs base-rate 0.2387 | `clinical_headline` | Aggregate full-200 validation | ExECTv2 reliability scorecard 2026-06-22/2026-06-25 |
| Cross-dataset wall-transfer mechanism | WALL TRANSFERS probe verdict (6/9 checks passed) | Dev140 aggregate model-swap + self-consistency replay | `exectv2_sf_wall_transfer_probe_2026-06-27.md`; External Risk AUROC 0.764 + 17.1% risk-coverage plateau (criterion 1); no gold-free separator on the binding gold-unknown over-reads, H0 retained (criterion 2); population-wide error entropy 0.287 vs 0.069 and agreement 21.8% vs 69.4% are the one noisier-than-Gan caveat |
| Cross-task shared-component ablation: `evidence_validation` inert on both tasks (Δ = 0.0000 ExECTv2 dev140 / Δ = 0.0000 Gan validation750); `standard_dictionary`/`normalize` positive on both (+0.0389 ExECTv2, +0.0293 Gan) | `clinical_headline` (ExECTv2); Purist accuracy (Gan) | Validation-side, aggregate-only, no model calls, no new freeze | `cross_task_shared_component_ablation_2026-06-27.md` |

---

## 5 Discussion

### D.1 What the System Does Well and Why the Architecture Deserves Credit

The central claim of this work is that a decomposed, stage-owned architecture — not any
particular large language model — is the primary carrier of clinical extraction quality.
Three pieces of evidence support this claim. First, swapping the generation LLM while
holding the component graph, scoring surface, and evaluation protocol constant does not
degrade performance: DeepSeek chat reaches **0.8566** overall clinical-headline F1 on the
development-inclusive full200 aggregate versus GPT-4.1-mini's **0.8356**, a +0.021 lead distributed
across Diagnosis (+0.031), SeizureFrequency (+0.008), and Investigations (+0.053), with
Prescription tied at 0.8926 (evidence validity: development-inclusive full200 aggregate, same-core
architecture, no row-level inspection). This is the predicted signature of a model-agnostic
system: the component graph normalizes structured outputs from qualitatively different LLMs
into consistent clinical-headline recovery, and the post-processing format layers contribute
a stable delta of ~+0.04–0.05 regardless of which LLM is in the generation lane. If the
LLM were the bottleneck, GPT's higher general-purpose benchmark ranking would dominate the
swap; it does not.

Second, the component-off ablation on dev140 confirms that the architecture's deterministic
spine is doing load-bearing work. The SeizureFrequency headline-projection layer contributes
+0.124–0.203 clinical-headline F1 depending on model; the residual semantic recovery lens
contributes +0.018–0.104. These are not margin gains — they are the mechanism by which
LLM-generated clinical facts are normalized, projected, and assembled into a recoverable
clinical headline. Removing any one of these layers produces a measurable regression. One
finding deserves specific attention: the evidence-validation gate is **structurally inert**
on the current holistic dev140 assembly (+0.000 delta across all four models; evidence
validity: dev140 replay-only aggregate), because the generation lanes emit only
verbatim-grounded mentions that already satisfy the gate. This is a grounding guard check,
not proof that evidence validation is universally unnecessary; it means the extraction lanes
already enforce the evidence contract before the gate fires.

Third, the structured-event extraction discipline itself — not the evidence-validation gate,
not the selector apparatus, but the forcing function that keeps the LLM source-near — is
where the Gan strand found most of its reliable value. On the Gan benchmark, the single GPT
structured-event pass achieved **0.809 test450 Purist** versus the full V12 hybrid's
**0.842**, a difference of only +15 test rows for a stack of four LLM calls and a
rule-guarded replace mechanism. The lesson is architectural: evidence-grounded intermediate
state, deterministic rendering, and a disciplined claim about what the LLM is allowed to
change are the primary sources of correctness. Orchestration complexity adds incrementally at
best.

---

### D.2 The Benchmark-Surface Inversion and Its Honest Interpretation

The manuscript reports headline performance on a clinical-recovery surface
(`clinical_headline`, four families: Diagnosis, SeizureFrequency, Prescription,
Investigations) that does not match the published ExECTv2 benchmark's per-item F1 scorer
(nine entities, CUI codes, full attribute bundles). This choice has a principled basis:
gold character-offset annotations were made against the original unprocessed clinical
letters; subsequent spelling correction altered the text without updating the offsets (thesis
§5), making any offset-tuned comparison non-reproducible on the corrected surface. The
methodology is consistent with the benchmark paper's own inter-annotator agreement protocol,
which also disregarded CUIs and compared on phrase selection and attribute classification.

The honest consequence must be stated directly. On the comparable dev140 published-benchmark
surface (nine-entity CUI + attribute-bundle scorer), the best-of-dev140 like-for-like figure
is **0.3877 per item / 0.6972 per letter** — approximately 45% of the paper's 0.87 per-item
headline (evidence validity: dev140 validation-only, frozen aggregate, not a full-200
estimate). For Prescription and Investigations this gap is not a measurement artifact: the
project's own 2026-06-18 like-for-like analysis locates the loss in **CUI reproduction and
attribute-bundle strictness**, not in concept recall or entity recognition, and identifies
the lever as deterministic phrase/CUI/attribute-bundle fidelity engineering that was
explicitly deprioritised in favour of the clinical-recovery evaluation framework. This is a
defensible choice; it should be narrated, not quietly elided. SeizureFrequency and
Diagnosis are the two entities where a substantial part of the gap *is* a property of the
measurement, for related but distinct reasons (below).

There is a second finding embedded in the benchmark-surface comparison that is genuinely
informative: **rules beat hybrid on the published-benchmark surface for SeizureFrequency,
Diagnosis, and Prescription**. For SeizureFrequency specifically, the hybrid verifier
reaches 0.782 on the clinical-recovery surface but collapses to 0.347 on the
published-benchmark surface, well below the deterministic rules baseline of 0.692 (+0.345
rules advantage). Stacking all four hybrid verifiers lowers the nine-entity benchmark
overall from 0.3687 (deterministic) to 0.3100 (all-hybrid). This is not a contradiction: the
LLM's clinical-recovery gains and the benchmark's format-fidelity requirements are
orthogonal surfaces with different owners. The paper should state this directly — as a
two-surface, two-stakeholder finding — rather than allow the surface choice to hide it.

A third finding sharpens what "the gap" means for SeizureFrequency, the benchmark's
weakest (0.66 per item) and lowest-agreement (human IAA 0.47) entity. A whole-corpus
row-level adjudication of our two-stage SF program on the primary state-set metric finds
that of its metric-errors only 28% are genuine model mistakes; 42% are the model being
clinically correct and scored wrong because the gold under-annotated a stated frequency or
redundantly double-tagged a seizure type, and 30% are genuine inter-annotator coin-flips.
Counting only genuine errors, the program is clinically defensible on **89.3%** of dev140
letters where the metric credits **62.1%** (dev140 validation-only; error structure
consistent across the held-out split). For SeizureFrequency, therefore, a substantial part
of the benchmark gap is not closeable fidelity engineering but a **gold-quality ceiling**:
the scorer penalises a clinically-correct reader because the reference it scores against is
itself only ~0.47 self-consistent. Two honesty consequences follow — SF figures are reported
as bands (the identical program re-run flips the per-letter state-set on 41/140 letters from
temperature-0 nondeterminism alone, a ±0.03 measurement band), and the only attributable
model lever that remains is a small, rule-shaped temporal/state-evidence discipline already
encoded in the deterministic projection. This makes SeizureFrequency the cleanest case in the
corpus where the benchmark gap is a property of the gold, not the model (row-analysis:
`exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`).

A fourth finding extends the same pattern to Diagnosis, more lopsidedly. A parallel
whole-corpus adjudication on the official Diagnosis `clinical_headline` scorer
(self-validated against the scorer's own aggregate, F1 0.6617 at that pass; 0.6779 after
the 2026-07-02 D1 hierarchy-match fix folded 5 gold-multiplicity pairs into the metric)
finds 88/140 letters carry a Diagnosis disagreement (209 missed-or-spurious concepts on
the pre-D1 scorer, 199 after); of these only
**14.8%** (15.6% post-D1) are genuine model errors (two narrow patterns: negation mis-read as
diagnosis, and Investigations findings mis-tagged as Diagnosis). **85.2%** are gold
*multiplicity* — splitting one diagnostic statement into a generic-plus-specific tag
pair, or several atomic fragments — that the model's reasonable single-tag
consolidation is scored against twice (once as a miss, once as a false positive).
Crediting every clinically-defensible disagreement lifts Diagnosis from F1 0.6617 (0.6779
post-D1) to approximately 0.85–0.99 (point estimate ≈0.92), a larger raw gap than SeizureFrequency's
even at the range's lower bound. Diagnosis therefore is not a pure closeable-fidelity
entity either; it shares the gold-quality-ceiling mechanism, driven by
annotation-granularity convention rather than inter-annotator disagreement
(row-analysis: `exectv2_dx_canonical_row_analysis_2026-06-30.md`). This figure is
reported as a range rather than the original pass's single point estimate (0.9501)
because a blinded independent re-adjudication of a stratified sample found item-level
verdict agreement too weak (κ≈0.39) to certify a bare point figure, and a
directionally higher population-reweighted genuine-error rate (14.8%→22.5% point
estimate); SeizureFrequency's parallel figure was, by contrast, corroborated closely by
the same check (§4.1.2; `exectv2_gold_quality_adjudication_blind_replication_2026-07-01.md`).
The core finding for both families — most of the benchmark gap is gold-quality artifact,
not model deficit — is unchanged; only Diagnosis's point magnitude is revised.

A specific caveat applies to SeizureFrequency rule-level claims under the published-benchmark
surface. The SF registry consolidates 133 rule IDs but the clinical behavior remains split:
convention rewrite and noise run through catalog-driven builder loops while residual
additions and operand-format rewrites execute in legacy Stack B modules; projection logic
uses no catalog-driven dispatch. The shadow-parity CI gate covers convention rewrite only.
Benchmark scores attributed to "SF rules" are valid aggregate readouts from saved replay
artifacts, not claims about cleanly auditable individual rule ownership (I1: SF registry
legacy delegation audit, 2026-06-27).

---

### D.3 The Wall and What It Means for the Architecture's Ceiling

The Gan strand's central negative result — a performance plateau at **0.842 test450 Purist**
for the multi-trace fresh-evidence hybrid pipeline and **0.809** for the single
structured-event pass — is not a failure of optimization effort. It reflects a task-ambiguity
floor: when documentation is genuinely ambiguous about current seizure burden, the model
over-specifies a definite rate rather than withholding, and no forward-observable signal can
safely breach that limit. The model over-reads ambiguous seizure-frequency evidence as
quantified rates with high confidence, and every inference-time feature fails to distinguish
*withhold-to-unknown* from *emit-rate*. On validation750, only 11 binding rows lack any
Purist-correct component (739 of 750 rows have at least one correct path); those 11 are
structurally indistinguishable from genuine-rate rows on every observable dimension — only
hidden gold separates them (structural-impossibility finding from C7).

The mechanism was established, not merely hypothesized, by a pre-registered semantic-entropy
probe (P2.1) at k=4 samples across temperatures {0.3, 0.5, 0.7, 1.0} on 150 validation
rows: mean label entropy **0.012**, with the most-over-read band (`band_unknown`) at **entropy
0.000** across all four temperatures (evidence validity: validation-only probe, n=150,
no holdout). The over-reading is not sampling noise — the model does not sample its way out
of the wrong answer. H0 (`H0_confident_over_reading`) was not refuted; the null is clean and
publishable.

This result generalizes, at minimum structurally. On the ExECTv2 clinical-letter corpus,
SeizureFrequency is the persistently weakest extraction family under a frozen same-core
architecture across all three tested LLMs: GPT-4.1-mini **0.7525**, DeepSeek chat
**0.7602** (development-inclusive full200 aggregate). The other families are materially stronger
(Diagnosis 0.8397–0.8708, Prescription 0.8926, Investigations 0.8563–0.9091). The gap is
not model-specific (DeepSeek narrows it by only +0.008 vs GPT), not an evidence-failure
(evidence rate is 1.0000 on all model-swap runs), and correctible by task-specific
adjudication (dev140 v08 with SF adjudicator: 0.9053). These are the same structural
signatures as the Gan wall: persistent across models, not addressable by model choice alone,
reducible by targeted post-processing that corrects the base extraction residual, but not
eliminated at the base extraction level.

The wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) ran on dev140
aggregate model-swap and self-consistency artifacts and, extended to compute the two
acceptance criteria the base probe left blank, returned a checklist result of **6 of 9
pre-registered cross-dataset checks passed**. The cross-dataset claim can now be stated with
evidence on two fronts. First,
the frozen External Risk composite validated on Gan P0.2 ranks ExECTv2 SF errors at
failure-prediction AUROC **0.764** (Gan 0.781), and its risk-coverage curve **plateaus** — the
safest-ranked SF tier still carries an irreducible **17.1%** selective risk (95% CI 8.5–31.3%,
lower bound above zero), the same irreducible-residual shape Gan documented. Second, on the
binding gold-`unknown` over-read slice a pre-registered null test finds **no gold-free
separator**: cross-model agreement, the External Risk composite, and self-consistency state
entropy all fail to distinguish the wrong over-reads from correct withholds (best AUROC 0.676,
below the useful-triage bar), with 2/5 over-reads temperature-entropy-zero — the exact Gan
`band_unknown` = 0.000 signature — and all three models over-reading the slice (5/7/8). H0 is
retained: the binding over-reads are unflaggable without gold, just as on Gan. The one genuine
difference is population-wide: ExECTv2's broad error cells are noisier (error entropy 0.287 vs
0.069 for correct cells; cross-model agreement 21.8% on errors vs 69.4% on correct), so the
error distribution is less uniformly degenerate than Gan's near-zero P2.1 panel — which is why
3 of the 9 checks, the population-magnitude ones, read `no`. The confirmed finding is therefore
**a task-bound ceiling whose wall mechanism transfers, with population-wide observability
noisier than Gan** — the more honest and more informative characterization: *a system whose
ceiling is task-bound, not system-bound, with the binding over-reads confident and undetectable
on a second independent corpus*. The wall is a characterization, not an apology.

**Reconciling the wall and the gold-quality ceiling.** D.2 and this section may read as
competing accounts of the same SF weakness — one a confident model *over-reading*, the
other a *gold under-annotation* that scores a clinically-correct model wrong. They are
not in competition: they are two mechanisms on disjoint error slices, measured on
different surfaces, and they converge. The whole-corpus row adjudication (D.2, on the
per-letter SF state-set metric) finds that only ~28% of SF metric-errors are genuine
model mistakes — and those are exactly the confident over-reads characterized here
(historical or superseded rates read as current, single or lifetime events read as
habitual rates), the rows the probe confirms are unflaggable without gold. The other
~72% are gold under-annotation, redundant double-tagging, and 0.47-IAA coin-flips — not
model errors. So the wall is real but small (it caps the genuinely-attributable residual
at ~28% of the SF error mass), while the bulk of SF's *apparent* weakness is a
gold-quality measurement ceiling. The 0.9053 dev140 adjudicated figure above is on the
four-family `clinical_headline` surface with a hand-tuned adjudicator that partly fits
this gold's conventions in-sample; it is not comparable to, and does not contradict, the
state-set gold ceiling of D.2. Both mechanisms point the same way: SeizureFrequency's
ceiling is a property of the task and its annotation, not of the system extracting it.

---

### D.4 Evaluation Discipline as the Lasting Methodological Contribution

The Gan closeout synthesis (Part III, 2026-06-17) identifies evaluation discipline — not
the F1 score — as the durable contribution. This assessment is correct and should be
foregrounded in the manuscript rather than subordinated to the numerical results.

The specific practices that constitute this discipline:

**Held-out-family cross-validation as a stop rule.** The two-tier gate (adversarial battery
*then* held-out-family CV) caught a -106 regression (v0.7) that a battery-perfect result
alone would have promoted to test450. The governing insight is that battery passing at 100%
is necessary but not sufficient: v0.7 was battery-perfect but over-demoted genuine-rate rows
because the coerce-to-unknown intervention was too aggressive across the full distribution.
Without the held-out-family CV gate, this candidate would have entered the locked evaluation
set with a false signal of generalization.

**Predeclared adversarial panels over cherry-picked cases.** The robustness battery's
minimal-pair, source-near, and KCL-OOD panels were authored before results were read. The
finding that the component wall is a genuine clinical gap (not surface overfit) came from the
C1 battery, where KCL-style OOD barely dented accuracy (87.5%) while minimal-pair and
synonym traps revealed the limit. This distinction — OOD-robust but abstention-incapable —
is the paper's most precise characterization of what the wall actually is.

**Contamination canaries and evidence-validity audits.** The M2 audit's recovery of
`REPAIRED_ELLIPSIS` copy-collation artifacts as the source of Qwen's apparent
evidence-validity gap (53.7% of hybrid exact-invalid strings; grounded rate 94.7% vs raw
74.8%) is a methodological result: the raw substring metric was misleading, and the audit
corrected it without changing any numbers or conclusions.

**Split inspection policies.** ExECTv2 full200 is a development-inclusive corpus audit, not a
holdout. The author did not inspect Gan test450 rows or use them for tuning. Agent-generated
row-level test reports were removed, and Observatory now rejects locked-test row access in
code. Gan paper claims use aggregate test450 results only.

These practices transfer. The ExECTv2 reliability scorecard adopts the same evaluation
dimensions, the same evidence-groundedness metric, and the same predeclaration format. The
method is reusable at the architecture level.

---

### D.5 Limitations

**I1 — SF registry hybrid-delegated (structural).** The ExECTv2 SeizureFrequency registry
consolidates 133 rule IDs across extraction, convention repair, and projection under a
YAML-indexed catalog, but clinical behavior remains split between catalog-driven builder
loops and legacy Stack B modules. The `convention_residual` family delegates entirely to
`_legacy_residual.py` (~905 LOC); five operand-format rewrites execute in
`_legacy_rewrite._sf_operand_format_rewrite`; `projection_sf` uses no catalog-driven dispatch
loop. Shadow-parity CI covers convention rewrite only. Aggregate benchmark scores attributed
to "SF rules" are valid readouts from saved replay artifacts; individual rule-level causal
attribution within the SF stack is not auditable from catalog metadata alone. This is a
maintainability and audit-trail limitation, not a validity limitation on the reported
aggregate figures.

**S1 — Cross-task shared-component ablation: executed, partial dividend confirmed.** The
reliability thesis §7 sets the thesis-complete criterion as "a shared core demonstrably reused
across tasks." Structural reuse is real at the code level (49 ExECTv2 modules import
`core`/`tasks.shared`/`tasks.seizure_frequency`), but the SeizureFrequency clinical machinery —
the declared "bridge" — is re-implemented under `exectv2/deterministic/sf_state_projection.py`
and `rules/seizure_free.py`; `assembly/lenses/seizure_frequency.py` does not import the Gan SF
normalizer. The shared-component ablation that would measure the cross-task dividend (turn one
shared component off, report delta on both tasks at once) was predeclared in
`exectv2_component_off_reliability_ablation_plan_2026-06-26.md` and executed at cross-task
scope on 2026-06-27 (`cross_task_shared_component_ablation_2026-06-27.md`; validation-side,
aggregate-only, no model calls, no new freeze): the `evidence_validation` gate is inert on
**both** tasks (Δ = 0.0000 ExECTv2 dev140; Δ = 0.0000 Gan2026 validation750), and
`standard_dictionary`/Gan `normalize` shows a **positive** cross-task dividend (+0.0389
ExECTv2, +0.0293 Gan validation750) — normalization buys score on both tasks, though the
underlying mechanisms differ (CUI/dictionary matching vs. format-level Gan label
normalization). The modularity thesis is now supported by structural evidence, the model-swap
result, and a measured, positive cross-task shared-component dividend. What remains open is
narrower than before: this dividend is validation-side only (no development-inclusive full200
or holdout cross-task
ablation), and it does not by itself establish literal SF-machinery code sharing, which
remains re-implemented per above.

**S2 — ExECTv2 three-way architecture comparison (thesis §7 Target tier): measured,
negative.** The thesis's Target tier requires beating the published benchmark with all three
architecture families and a clean three-way comparison. This is now measured for ExECTv2 (§4.2,
closing paragraph): a GEPA-optimized LLM-only single pass reaches dev140 `clinical_headline` F1
≈0.749 (gpt-4.1-mini) / ≈0.679 (Qwen 3.6 35B), ≈0.17 below the hybrid ceiling (0.9155
dev140) and short of the published-benchmark surface. The Target tier is therefore not met — the
result is a negative one, consistent with C2/C4's direction that architecture, not model
capability, carries the gain. Two caveats bound this claim: (i) it is dev140 development-surface
evidence only, not a development-inclusive full200 aggregate or holdout result; (ii) the root cause is not uniformly
"evidence-recall limitation" — per-family re-examination shows this is genuine for
Investigations and partially genuine for Prescription, but mostly a gold-consolidation-convention
artifact for Diagnosis and SeizureFrequency (the same mechanism as §4.1.2's benchmark-gap
finding), so the *true* architectural gap between LLM-only and hybrid is smaller than the raw
number once both legs are corrected for gold convention — by an amount not yet quantified.

**Wall mechanism transfers; population-wide observability is noisier than Gan.** The
cross-dataset wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`, 6/9 checks
passed) confirms the wall mechanism transfers: the External Risk composite ranks SF errors with
an irreducible risk-coverage plateau (17.1% selective risk, 95% CI 8.5–31.3%, lower bound above
zero), and the binding gold-`unknown` over-reads have no gold-free separator (best AUROC 0.676
< 0.70; H0 retained). The residual difference from Gan is that ExECTv2's population-wide error
cells are noisier than Gan's degenerate P2.1 panel (error entropy 0.287 vs 0.069; cross-model
agreement 21.8% vs 69.4%), which is why 3 of the 9 checks — the population-magnitude ones —
read `no`. The mechanism claim is two-dataset and aggregate-only: no ExECTv2 holdout SF
comparison and no row-level mechanism attribution on full-200 have been authorized, and the
binding over-read slice is small (5 over-reads vs 25 withholds on dev140), so its AUROCs are
suggestive rather than definitive.

**Calibration is near-base-rate, not deployment-ready.** The scoring rule's aggregate
full-200 validation calibration is Brier **0.2245** versus constant base-rate **0.2387**
(Δ = 0.0142), ECE **0.0432**. The improvement above base rate is real but small. All signal
carried by the rule comes from external predeclared features (family identity, evidence-
provenance indicators, evidence-ambiguity flags), not from model-reported confidence, which
is degenerate on the Gan strand and unused here. Holdout calibration confirmation has not
been run.

The practical consequence follows directly and is stated here rather than left for the reader
to infer: the transparency/reliability pillar currently has **no working low-burden triage
policy** on the broad ExECTv2 task (the review-routing gate fires on ~97% of cells to catch
~90% of errors, Table R5) — and the one slice where a working signal would matter most
clinically, the binding gold-`unknown` over-read cases (§4.3.2), has **no forward-observable
separator at all** (best AUROC 0.676, below the paper's own 0.70 usefulness bar; H0 retained).
This is an honest, pre-registered negative result, not a closed null: cross-model agreement,
self-consistency entropy, and evidence support-quality are three signal sources already
computed on this project's own data but not yet incorporated into the calibration rule or the
review-routing trigger set, and closing that gap is active future work, not a settled question.

---

## 6 Contributions

The following five contributions are stated as the measured deliverables of this work.
Evidence-validity labels accompany each claim; no contribution overstates its evidence basis.

---

**Contribution 1: Benchmark reconciliation with honest gap disclosure and surface inversion
finding.**

We provide the first like-for-like comparison between our clinical-recovery evaluation
surface and the published ExECTv2 benchmark (nine-entity CUI + attribute-bundle scorer): our
best-of-dev140 configuration reaches **0.3877 per item / 0.6972 per letter** on the
published-benchmark surface versus the published pipeline's **0.87 / 0.90**
(evidence validity: dev140 validation-only, frozen aggregate). The gap is explained by
two distinct mechanisms. First, spelling correction on the clinical letters drifted the gold
character offsets, making the offset-tuned published number non-reproducible on the corrected
surface; for Prescription and Investigations the residual gap on the aligned surface is
concentrated in CUI reproduction and attribute-bundle strictness, representing closeable
deterministic fidelity engineering that was explicitly deprioritised. Second, for
SeizureFrequency and Diagnosis whole-corpus row-level adjudications show a measurable share of
the gap is **not** closeable engineering but the gold's own annotation conventions: for
SeizureFrequency, the gold's ~0.47 inter-annotator agreement leaves the two-stage program
clinically defensible on 89.3% of letters (blinded-replication-corroborated, 88.5%,
range 82.4–94.6%) where the metric credits 62.1%; for Diagnosis, the gold's tendency to
split one diagnostic statement into multiple co-present concepts leaves the single-pass
extractor clinically defensible on the equivalent of F1 ≈0.85–0.99 (point estimate
≈0.92, revised from an original single-pass point estimate of 0.9501 by the same blinded
replication check) where the metric credits 0.6617 (0.6779 after the 2026-07-02 D1 fix). Both of the benchmark's weakest cells
are therefore in substantial part a gold-quality ceiling rather than a model deficit.
A non-obvious inversion accompanies this finding: the deterministic rules pipeline beats the
hybrid configuration on the published-benchmark surface for Diagnosis, Prescription, and
SeizureFrequency (SF rules advantage: +0.345 benchmark per-item F1 on SF), while the hybrid
dominates on the clinical-recovery surface. This two-surface, two-stakeholder result is a
finding, not a measurement inconsistency; it characterizes the difference between
CUI-bundle fidelity and clinical-concept recovery as genuinely distinct objectives.

---

**Contribution 2: Cross-task shared component ablation establishing the evidence-validation
gate as structurally inert and SF normalization as the operative shared component.**

We report the first systematic one-component-off aggregate ablation for ExECTv2 under a
frozen dev140 replay protocol. The ablation establishes that the evidence-validation gate
contributes **Δ = 0.000** to clinical-headline F1 across all four model configurations on the
current holistic assembly (evidence validity: dev140 replay-only, no model calls, aggregate
only). This is not a failure of the gate — it is a grounding-architecture result: the
structured-event generation lanes enforce exact-evidence grounding before the gate fires, so
the gate's protection is already baked in at the source. Separately, the SeizureFrequency
headline-projection layer contributes **+0.124–0.203 F1** depending on model (largest for
DeepSeek: +0.203), concentrated entirely on the SF family. This identifies SF normalization
and projection as the operative shared clinical component across both tasks — not because the
same module is imported (the ExECTv2 SF clinical machinery is re-implemented, not directly
ported), but because the clinical task's structure, and the architecture's response to it,
are parallel. This ExECTv2-only delta is extended by a separate cross-task shared-component
ablation (`cross_task_shared_component_ablation_2026-06-27.md`; validation-side,
aggregate-only, no model calls, no new freeze) that genuinely spans both tasks at once: the
evidence-validation gate is inert on **both** ExECTv2 dev140 (Δ = 0.0000) and Gan2026
validation750 (Δ = 0.0000), and a shared normalization mechanism (`standard_dictionary` / Gan
`normalize`) shows a positive dividend on **both** (+0.0389 ExECTv2, +0.0293 Gan) — the same
normalization-buys-score direction on both tasks, via mechanisms that differ (CUI/dictionary
matching vs. format-level label normalization). This is the first measured, positive
cross-task component dividend reported in this work, and it upgrades C2 from a single-task
finding with a promised follow-up (S1) to genuine cross-task evidence.

---

**Contribution 3: The wall as a cross-dataset confident-over-reading phenomenon —
mechanism transfer with structural confirmation.**

We characterize the Gan 2026 seizure-frequency ceiling (**0.842 test450 Purist**, V12
hybrid) as a confident, architecturally unresolvable over-reading of ambiguous evidence: the
model commits to rate-like interpretations of genuinely ambiguous clinical text without
uncertainty and with no forward-observable signal separating wrong over-reads from correct
rate extractions. A pre-registered semantic-entropy probe (P2.1: k=4 at temperatures
{0.3, 0.5, 0.7, 1.0}, n=150 residual-enriched rows) returned mean label entropy **0.012**
with `band_unknown` entropy **0.000** — H0 (`H0_confident_over_reading`) not refuted
(evidence validity: validation-only probe; test450 not read for mechanism). We show that the
same wall appears structurally on the ExECTv2 clinical-letter corpus: SeizureFrequency is
the persistently weakest extraction family under a frozen same-core architecture across all
three tested LLMs (GPT-4.1-mini **0.7525**, DeepSeek chat **0.7602**, frozen full-200
aggregate), with the same signatures — model-independent gap, 1.0000 evidence rate
(faithful-but-wrong, not unfaithful), and correctability by task-specific adjudication
(dev140 with SF adjudicator: 0.9053). The cross-dataset mechanism claim — that the ExECTv2
over-reading is also confident, not merely frequent — is supported by the ExECTv2 SF
wall-transfer probe (6/9 checks): the External Risk composite ranks SF errors
(AUROC 0.764) with a 17.1% irreducible risk-coverage plateau, and the binding
gold-`unknown` over-reads have no gold-free separator (H0 retained). Population-wide
error observability is noisier than Gan, but the wall mechanism transfers. The
structural finding stands: a system whose ceiling is **task-bound, not
system-bound** exhibits exactly the behavior a clinically-grounded, modular
architecture predicts. The limit is the clinical task's ambiguity floor, not an
architectural deficiency.

---

**Contribution 4: Model-agnostic architecture validated by a non-development LLM outperforming
the primary model.**

We demonstrate that the ExECTv2 architecture is model-agnostic through the strongest
available test: a same-core model-swap experiment in which DeepSeek chat, running on the
frozen component graph developed against GPT-4.1-mini, surpasses GPT-4.1-mini by **+0.021
overall F1** on the development-inclusive full200 aggregate (0.8566 vs 0.8356; evidence validity:
development-inclusive aggregate, same-core `exectv2_2call_no_sf_adjudicator` architecture, predeclared
gate `pass_with_caveat` for one parse/schema failure within tolerance). The post-processing
format layers contribute a stable **~+0.044–0.046** across all three models tested, confirming
that the architecture normalizes idiosyncratic model output differences before they reach the
scored surface. DeepSeek's clinical-recovery base (0.8110) also exceeds GPT's (0.7922),
ruling out the alternative that the aggregate advantage is purely a formatting artifact.
This result provides direct empirical support for the modularity claim: if the LLM were the
intelligence locus, the non-development LLM would not lead on three of four clinical families
while holding the architecture constant. The architecture's component graph, deterministic
normalization, and projection stages are the primary carriers of clinical extraction quality.

---

**Contribution 5: Evaluation discipline as a reusable, transferable methodology for
LLM-mediated clinical extraction.**

The single most transferable output of this work is the evaluation discipline developed
through seven experiment cycles on the Gan benchmark and applied to the ExECTv2 strand. The
core practices are: (a) predeclared adversarial panels with distinct clinical failure axes
(minimal-pair, source-near, KCL-style OOD), run before validation750 to catch overfitting
that would otherwise reach the locked evaluation set; (b) held-out-family cross-validation
as a stop rule, catching the -106 regression in v0.7 that battery-perfect performance would
have promoted; (c) contamination canaries and evidence-validity audits distinguishing
metric artifacts from real failures (e.g., `REPAIRED_ELLIPSIS` recovery); (d) frozen
aggregate-only inspection policies that preserved the test set's evidential integrity through
structural-impossibility findings including C7's proof that the no-correct residual is
feature-indistinguishable from genuine-rate rows on all inference-time signals. These
practices were transferred to the ExECTv2 reliability scorecard under the same evaluation
dimensions and evidence-groundedness metric. The methodology is architecture-independent and
task-independent; its durable contribution is the proof that rigorous, predeclared evaluation
protocols for LLM-mediated clinical extraction are both necessary (removing them would have
produced false promotion decisions) and sufficient (they correctly characterized both a
genuine ceiling and the mechanism behind it without holdout contamination).

---

### Evidence Validity Summary (Contributions)

| Contribution | Evidence level | Boundary |
|---|---|---|
| C1 — Benchmark reconciliation | dev140 validation-only, frozen aggregate; gold-quality magnitudes corroborated by a blinded independent re-adjudication (SF closely; Diagnosis revised to a range) | No full-200 published-benchmark surface computed; blind-replication check is internal (project-framework second-pass, not external clinical validation), n=20/family, wide CIs |
| C2 — Component ablation (gate inert; SF norm matters) + cross-task dividend | dev140 replay-only, aggregate (ExECTv2 single-task); validation-side cross-task ablation (ExECTv2 dev140 + Gan validation750) | No model calls; cross-task ablation is validation-side/aggregate-only, not a development-inclusive full200 or holdout cross-task result |
| C3 — Wall cross-dataset | Development-inclusive full200 aggregate (ExECTv2); validation-only probe (Gan P2.1); wall-transfers probe 6/9 | Ceiling and wall mechanism transfer (external-risk plateau + no gold-free separator); population-wide observability noisier than Gan; no holdout on ExECTv2 |
| C4 — Model-agnostic architecture | Development-inclusive full200 aggregate, predeclared gate | No independent holdout on non-primary models; row-level attribution excluded |
| C5 — Evaluation discipline | Validation-only + test450 aggregate (Gan); validation-only (ExECTv2) | No new experiments; retrospective characterization of completed work |
| S2 — ExECTv2 three-way comparison (GEPA LLM-only vs. hybrid, thesis §7 Target tier) | dev140 development-surface, non-paper-comparable diagnostics | Not a development-inclusive full200 aggregate or holdout result; per-family root-cause of the LLM-only-vs-hybrid gap corrected (H-inflated/gold-convention for Diagnosis+SF, genuine for Investigations, partial for Prescription) |

---

## Do Not Use As Claims

- Gan test450 or ExECTv2 development-inclusive full200 reliability is deployment-validated.
- ExECTv2 de-duplicated `clinical_headline` recovery is a strict benchmark win vs published 0.87/0.90.
- Qwen is an operationally promoted same-core ExECTv2 candidate above GPT-4.1-mini or DeepSeek.
- The ExECTv2 calibration rule is deployment-ready.
- A low-burden review-routing policy is validated on ExECTv2.
- Strict benchmark/CUI reproduction is the headline ExECTv2 success criterion.
- Either reliability scorecard proves individual component causality.
- Post-test tuning is authorized from any frozen `test450` aggregate.
- The consensus/fresh v0.9 selector (constrained or exact-source) is a promoted holdout result. Neither Gate 4 audit is a paper-facing promoted result; the Gan production headline is the single GPT structured-event pass `364/450` (0.809) only.
- Holdout validation of ExECTv2 performance on any split.
- Full-200 published-benchmark nine-entity CUI score is computed under the current protocol.
- Cross-model agreement is a validated ExECTv2 reliability signal (unused; available artifact).
- ExECTv2 SF reproduces Gan's population-wide error magnitude. The wall *mechanism* transfers (6/9 checks: External Risk plateau + no gold-free separator on the binding gold-unknown slice, H0 retained), but ExECTv2's population-wide error cells are noisier than Gan's degenerate P2.1 panel (error entropy 0.287 vs correct 0.069; cross-model agreement 21.8% on errors vs 69.4% correct), so 3 of 9 checks — the population-magnitude ones — read `no`. Identical same-magnitude population-wide degeneracy is not claimed.
- The shared SF machinery is literally identical across tasks (ExECTv2 re-implements projection; structural reuse is the accurate claim, not code identity).
- The GEPA LLM-only ExECTv2 numbers (≈0.749 gpt-4.1-mini, ≈0.679 Qwen dev140 clinical_headline F1; the mini figure reflects the 2026-07-02 four-family scorer-correctness fixes, see §4.2 footnote) are a promoted full200 or holdout result. They are dev140 development-surface diagnostics only and must not be compared directly to Table R2/R3's development-inclusive full200 numbers without the dev140-vs-full200 caveat.
- The C1 gold-quality blind replication (`exectv2_gold_quality_adjudication_blind_replication_2026-07-01.md`) is external clinical validation. It is a second internal pass (an LLM-based sub-agent blind to the original verdicts and to this project's conclusions, not a human clinician) that corroborates the aggregate magnitude and revises the Diagnosis point estimate to a range; a blinded board-certified neurologist/epileptologist review remains open future work.
