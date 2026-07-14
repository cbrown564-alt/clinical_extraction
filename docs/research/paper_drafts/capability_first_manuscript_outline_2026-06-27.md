# Capability-First Manuscript Spine — Master Outline

Date: 2026-06-27
Workstream: Wave 4 · P6a (manuscript restructure — outline phase)
Status: outline only — no new data, no git, no model calls
Evidence boundary: synthesizes P1–P5 writing artifacts and M2–M3 measurement artifacts,
all at their declared validity levels (see per-section headers). Does not introduce new
claims; does not raise validity of any number beyond its source.
Parent task: `closing_campaign_orchestration_plan_2026-06-27.md` Wave 4 / P6.

---

## Spine Structure

Five capability-anchored sections replace the current task-parallel layout
(§4.1 Gan 2026 seizure-frequency labeling | §4.2 ExECTv2 multi-entity phenotyping).
Cross-references to the source drafts that supply
content are given per subsection; key numbers are quoted with their evidence
validity at point of citation.

---

## §1  Shared Decomposed Architecture

*One figure; one architectural narrative. This section replaces the separate
"Systems" subsections currently scattered under §4.1 and §4.2.*

### 1.1  The Common Stage Graph

**Content source:** orchestration plan §Verified load-bearing paths; decomposition
research impact review (decomp §1a); critique §4 spine proposal.

**Deliverable figure:** A single component-graph diagram showing the shared
spine — evidence extraction → normalization → adjudication/lens stack →
projection/headline assembly — with shared primitives (`core/evidence.py`,
`tasks.shared`, `tasks.seizure_frequency`) annotated, and both task-specific
branches (Gan SF label grammar; ExECTv2 four-family clinical-headline) as
variants off the same graph.

**Key architectural facts:**
- 49 ExECTv2 modules import `core/` or `tasks.shared` (confirmed by code structure;
  critique §1d). Structural reuse is real at the primitives level.
- `definitions.yaml` portability categories: `general`, `clinical_epilepsy`, `task`,
  `dataset`, `benchmark_format` — the taxonomy that makes the component ablation
  (§5) a direct read-out of the figure's annotations.
- Shared load-bearing paths (HEAD 2026-06-27): `core/evidence.py` (repair cascade);
  `exectv2/reports/component_ablation/definitions.yaml`; `catalog.yaml`.

**CUT from current draft:** Any language asserting that "the same SF clinical
machinery runs on both tasks." The ExECTv2 SF surface (`sf_state_projection.py`,
`rules/seizure_free.py`, `assembly/lenses/seizure_frequency.py`) re-implements
rather than imports the Gan SF normalizer. Correct claim: **structural reuse of
shared primitives**; the SF *clinical mechanisms* are independently implemented
per task. (Critique §1d; orchestration plan §Structural reuse caveat.)

### 1.2  Portability Taxonomy

**Content source:** P1 (`benchmark_surface_reconciliation_2026-06-27.md` §4.x.4);
M3 (`cross_task_shared_component_ablation_2026-06-27.md` §Mapping Notes).

**Subsection purpose:** Introduce the five portability categories so §5's
component-ladder figures are interpretable. Every component in the stage graph
carries exactly one category tag; the tag predicts whether toggling it moves
both tasks' scores (§5.1) or only one.

**Key table** (from P1 / `definitions.yaml`):

| Category | Meaning | Example component |
|----------|---------|-------------------|
| `general` | Task-neutral utility | `evidence_validation` |
| `clinical_epilepsy` | Epilepsy-domain but task-shared | `standard_dictionary` (normalization) |
| `task` | Single-task specific | ExECTv2 `headline_projection` |
| `dataset` | Corpus-specific calibration | Gan `benchmark_repair` |
| `benchmark_format` | Format-layer enrichment for scoring surface | `residual_semantic_lens` |

**Key numbers (validation-only replay):** `benchmark_format` layers add +0.0175
(`residual_semantic_lens`) + 0.0283 (`headline_projection`) = **+0.0458** on
GPT-4.1-mini dev140; ~+0.04 stable on full-200 across models (P1 §4.x.5).

### 1.3  SF Registry Caveat (Methods Integrity Note)

**Content source:** P1 §4.x.6; orchestration plan I1.

**Purpose:** Required methods-integrity paragraph for any rule-level ExECTv2 SF
benchmark claim. Do not suppress; place in Methods or Supplementary.

**Claim ceiling (from audit I1):** ExECTv2 consolidates SeizureFrequency rules
into a YAML-indexed registry (133 rule IDs: extraction, convention repair,
projection) but behavior remains split — `convention_residual` delegates to
`_legacy_residual.py` (~905 LOC); five `convention_rewrite` rules execute in
`_legacy_rewrite`; `projection_sf` uses no catalog-driven dispatch. Parity gate
(`test_shadow_diff_zero_mismatches`) covers convention rewrite only. Rule-level
benchmark scores are aggregate replay read-outs, not cleanly catalog-attributable.

---

## §2  What the LLM Adds — Three-Way, Both Tasks

*Pairs the Gan three-way table (rules / LLM-only / hybrid) with the ExECTv2
two-surface comparison. The ExECTv2 full three-way (deterministic arm assembled)
is an acknowledged gap.*

### 2.1  Gan Strand: Rules / LLM-Only / Hybrid (Three-Way Table)

**Content source:** Existing manuscript Tables 1–2 (Gan 2026 seizure-frequency three-way
comparison, validation750 and `test450` held-out aggregate). No new material required.

**Key numbers** (validation750 / `test450`; no-call replay / frozen aggregate):
- Deterministic floor: validation ~0.636 (Purist); `test450` 0.343/0.450 (det floor)
- LLM-only (single SE, gpt-4.1-mini): validation 0.9093 Purist; `test450` 0.809
- Multi-trace fresh-evidence hybrid pipeline holdout ceiling: validation 0.9787 (oracle
  selector 739/750 = 0.9853 ceiling); `test450` **0.842**
- Finding: LLM adds ~+0.17 over deterministic on validation; hybrid adds ~+0.03
  over LLM-only on test (holdout ceiling-limited; critique §What Is Solid)

**Evidence validity:** `test450` = frozen holdout; validation = frozen aggregate.

### 2.2  ExECTv2 Strand: The Two Surfaces and the Like-for-Like Number

**Content source:** P1 (`benchmark_surface_reconciliation_2026-06-27.md`), all
subsections.

#### 2.2.1  The Stated Benchmark vs. the Evaluation Surface

**Key facts:**
- Thesis §7 minimum bar: beat ExECTv2 per-item / per-letter F1 benchmark
  `0.87` / `0.90`.
- Manuscript delivers `clinical_headline` F1 (Diagnosis, SeizureFrequency,
  Prescription, and Investigations; label-based) — a *different surface*.
- Non-reproducibility reason: gold character-offset annotations were made
  on unprocessed text; subsequent spelling correction shifted offsets without
  updating them (thesis §5). Offset-tuned published pipeline score is not
  reproducible on corrected text. This is the honest reconciliation; the
  "metric-is-an-artifact" defense is weaker and reviewer-visible.

#### 2.2.2  The Like-for-Like Number (`dev140`, frozen aggregate)

*Evidence validity: validation-only, frozen aggregate. Source:
`exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json`.*

| Surface | Per-item F1 | Per-letter F1 | vs. paper |
|---------|------------:|---------------:|-----------|
| Published benchmark (paper) | 0.87 | 0.90 | — |
| Best-of dev140 (rules + hybrid Inv) | **0.3877** | **0.6972** | −0.48 / −0.20 |
| Deterministic-only dev140 | 0.3687 | 0.6747 | −0.50 / −0.23 |
| All-hybrid dev140 | 0.3100 | 0.6454 | −0.57 / −0.25 |

The gap is closeable fidelity engineering (CUI normalization, full attribute
serialization, entity-bundle assembly per family) that was explicitly
deprioritized. Name the lever and name the choice; do not assert the benchmark
is broken. (P1 §4.x.3)

#### 2.2.3  Clinical-Headline F1 (Primary Evaluation Surface)

*Evidence validity: frozen aggregate full-200 (no row-level inspection). Source:
`exectv2_same_core_model_swap_full200_2026-06-25.md`; P1 Table 2.*

| Model | Headline F1 | Clinical-recovery F1 | Format-layer Δ |
|-------|------------:|---------------------:|---------------:|
| GPT-4.1-mini | 0.8356 | 0.7922 | +0.043 |
| DeepSeek chat | **0.8566** | **0.8110** | +0.046 |
| Qwen 3.6 35B | 0.8197 | 0.7797 | +0.040 |

Format-layer delta ~+0.04 is **stable across models** — the deterministic
post-processing spine contributes a model-independent increment.

#### 2.2.4  The Rules > Hybrid Inversion (Two-Surface Finding)

*Evidence validity: validation-only, frozen aggregate dev140.*

On the published-benchmark surface, stacking hybrid verifiers *lowers* the
overall benchmark score (deterministic 0.3687 → all-hybrid 0.3100). For
SeizureFrequency specifically: rules reach 0.692 benchmark item F1; hybrid
collapses to 0.347. Yet on the clinical-headline surface, hybrid gains are
real (+0.0458 format layers on dev140). The surfaces have different owners:
hybrid verifiers promote clinical recovery; deterministic rules retain
benchmark fidelity. State this directly — it is a finding, not a problem to
hide. (P1 §4.x.4)

**CUT from current draft:**
- Any dependence on the 60-row checkpoint
  (`exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md`) as evidence
  for benchmark-gap claims. That document is explicitly labeled "not a frozen audit
  conclusion" and is superseded by the 2026-06-18 frozen aggregate read. (P1 §4.x.2)

### 2.3  ExECTv2 Three-Way Comparison (Acknowledged Gap)

**Content source:** Critique §1d; orchestration plan §P-track note on three-way.

The ExECTv2 equivalent of the Gan three-way table (deterministic / LLM-only /
hybrid, head-to-head) has not been assembled in paper form. The constituent
architectures exist in code (`exectv2/deterministic`, `exectv2/llm/llm_only_*`).

**Manuscript handling:** Acknowledge explicitly as deferred work. State what is
available — the model-swap comparison (hybrid across three LLMs) — and what is
not. Do not assert the three-way §7 target criterion as met on ExECTv2.

---

## §3  What Generalizes — Wall + Model Swap

*The two strongest generalization results, each establishing a different dimension
of architecture-independence: model-agnostic score stability (§3.1); task-bound
ceiling that transfers across datasets (§3.2).*

### 3.1  Architecture Transfer: Model-Agnostic Performance (DeepSeek ≥ GPT)

**Content source:** P2 (`deepseek_model_agnostic_evidence_2026-06-27.md`),
all sections.

#### 3.1.1  Reframe: the Model-Swap Experiment Tests Modularity

The same-core architecture holds the component graph, surface definitions, and
evaluation protocol constant while varying only the LLM. A model-agnostic
architecture predicts that no single LLM is necessary: the architecture, not the
model weights, drives performance. The model-swap result confirms this — and
DeepSeek *beating* GPT makes it stronger: the deterministic post-processing spine
normalizes structurally different LLM outputs into consistent clinical-headline
recovery. (P2 §2a)

#### 3.1.2  Key Numbers (full-200 frozen aggregate)

*Evidence validity: frozen aggregate full-200. Source:
`exectv2_same_core_model_swap_full200_2026-06-25.md`.*

| Candidate | Model | Overall F1 | Dx | SF | Presc | Inv |
|-----------|-------|----------:|---:|---:|------:|----:|
| Same-core GPT | GPT-4.1-mini | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 |
| Same-core DeepSeek | DeepSeek chat | **0.8566** | **0.8708** | **0.7602** | 0.8926 | **0.9091** |
| Same-core Qwen | Qwen 3.6 35B | 0.8197 | — | — | — | — |

DeepSeek leads overall by **+0.021**; leads on three of four families. Format-layer
contribution is stable at ~+0.044–0.046 across models (DeepSeek clinical-recovery
base 0.8110 > GPT 0.7922, confirming the advantage is not a post-processing
artifact). (P2 §1, §3 reframed language)

#### 3.1.3  Gate Status for Reliability Section Cross-Reference

One parse/schema failure on DeepSeek run was within predeclared full-200
tolerance (call failures = 0; evidence rate 1.0000). Gate: `pass_with_caveat`.
This belongs in §4 apparatus language, not in the headline framing. (P2 §4)

**CUT from current draft:**
- DeepSeek relegated to caveat footnote on the basis of one tolerated failure.
  The `pass_with_caveat` gate was designed for this outcome; it is not a
  relegation warrant. Reframe from apology to positive modularity evidence.
  (P2 §2b–§2c)
- Any language implying GPT-4.1-mini is the "primary" model on grounds of score
  alone. The model-agnostic thesis requires no single LLM to be privileged.

### 3.2  Wall Transfer: Task-Bound Ceiling (Cross-Dataset Confident Over-Reading)

**Content source:** P3 (`wall_transfer_cross_dataset_2026-06-27.md`), all
sections. Probe returned **3 of 6 pre-registered cross-dataset checks passed**
(task-bound ceiling confirmed; Gan H0 mechanism partially differs — see §3.2.3).

#### 3.2.1  The Confident Over-Reading Limit (the Wall) on Gan (Confirmed Finding)

*Evidence validity: Gan `test450` frozen holdout (score); validation-only probe (entropy).*

- Holdout ceiling: **0.842** (multi-trace fresh-evidence hybrid pipeline, `test450`
  Purist); single structured-event pass: **0.809**.
- Selector oracle ceiling: 739/750 validation rows; 11 structurally unresolvable
  residual rows.
- Mechanism (P2.1 semantic entropy probe, n=150, k=4 at temps [0.3, 0.5, 0.7, 1.0]):
  mean label entropy **0.012**; `band_unknown` entropy **0.000** across all four
  temperatures. The over-reading is confident, not uncertain — the model never
  samples its way out of the wrong answer. Dominant failure type:
  unknown-vs-rate over-inference (last-event-only, open-ended "since",
  vague-count, relative-trend evidence shapes). (P3 §1)

#### 3.2.2  ExECTv2 SF Gap: Structural Parallel

*Evidence validity: frozen aggregate full-200 (score); probe pending (mechanism).*

- SF is the weakest ExECTv2 family under a frozen same-core architecture across
  all three LLMs: GPT 0.7525, DeepSeek **0.7602** (gap narrows only +0.008 under
  DeepSeek — model-independent).
- Other families: Dx 0.8397–0.8708, Presc 0.8926, Inv 0.8563–0.9091.
- Evidence rate 1.0000 on all model-swap runs — the SF gap is not an evidence
  failure; it is a clinical-interpretation residual. (P3 §2a–§2b)
- With task-specific SF adjudicator (dev140 v08): SF 0.9053, indistinguishable
  from other families — gap is targeted-adjudication-correctable. (P3 §2b)
- Clinical task is analogous to Gan: extract seizure burden from hedged,
  event-indexed, or temporally-ambiguous prose — precisely the illegitimate
  evidence shapes the Gan wall analysis catalogued.

#### 3.2.3  Cross-Dataset Claim — Probe Complete (3 of 6 Checks Passed)

*Source: `exectv2_sf_wall_transfer_probe_2026-06-27.md` — **3 of 6 pre-registered
cross-dataset checks passed**. `dev140` self-consistency artifact replay; no new model
calls; no holdout.*

**Task-bound ceiling confirmed.** SF is the weakest family on every evaluation surface
and every LLM tested. The gap is structural, not model-specific, and not addressable by
model substitution alone. This part of the Gan → ExECTv2 transfer holds cleanly.

**Mechanism partially differs.** The Gan wall was characterized by zero-entropy,
zero-disagreement confident over-reading. ExECTv2 SF presents a mixed picture:
- **43.6%** of SF error cells are temperature-unanimous wrong (4/4 same wrong answer)
  — a genuine confident-error component present and material.
- SF error entropy is **elevated** (0.287 vs 0.069 for correct cells) — errors are
  detectably more uncertain, unlike Gan where residual entropy was flat at ~0.018.
- Cross-model agreement is **lower on errors** (21.8%) than correct cells (69.4%) —
  the opposite direction to Gan's `band_unknown` pattern.
- The elevated-error-entropy pattern is SF-specific; other families do not show it
  uniformly.

**Manuscript framing (use P3 §3a language):** "task-bound ceiling transfers; mechanism
partially differs." State 43.6% unanimous-wrong as confirming a confident-error
component; state the elevated entropy and lower cross-model agreement as establishing
the mechanism divergence from Gan. Do not assert full H0_confident_over_reading
replication — probe fails checks on that claim.

**CUT / reframe from current draft:**
- "SF is consistent with deep-reasoning difficulty" — replace with the wall-transfer
  framing or the pending-probe hedge. The current language makes SF sound like an
  apology. (Critique §2 SF-spin)

### 3.3  Evaluation Discipline Transfers

**Content source:** Critique §What Is Solid; orchestration plan §Acceptance gates.

Brief subsection establishing that the *protocol*  — held-out-family CV, predeclared
adversarial battery, frozen aggregate-only audits, decision-effect component
attribution — is the durable transferable artifact, applied consistently across both
tasks. No new numbers; draws on the Gan closeout's Part III (the discipline, not the
score, is the durable contribution) and the ExECTv2 predeclaration/gate discipline
demonstrated through the model-swap and component ablation runs.

---

## §4  Unified Reliability Scorecard

*Replaces the two separate reliability subsections currently under §4.1 (Gan) and
§4.2 (ExECTv2). Unified across ten dimensions; sourced from the Gan reliability
scorecard and ExECTv2 scorecard under the same dimension taxonomy.*

### 4.1  Calibration (Revised Framing)

**Content source:** P4 (`calibration_claim_revision_2026-06-27.md`), §Before/After.

**After (revised) language:**
> The scoring rule is near-base-rate calibrated: aggregate full-200 validation Brier
> **0.2245** versus constant base-rate **0.2387** (Δ = **0.0142**), ECE **0.0432**,
> five populated monotone bins. The improvement is real but small; it should not be
> read as evidence of well-calibrated predictive confidence. All signal comes from
> external, predeclared features — family identity, evidence-provenance indicators,
> evidence-ambiguity flags — not from model-reported confidence, which is degenerate
> on the Gan strand (749/750 validation rows rated "high"; statistically
> indistinguishable buckets) and unused here.

*Evidence validity: aggregate full-200 validation; no holdout calibration run.*

Per-family ECE: Diagnosis **0.1424**, SeizureFrequency **0.1292**, Prescription
**0.1214**, Investigations **0.0925**.

**CUT from current draft:**
- ECE `0.0432` presented without the paired Brier improvement of `0.0142` (suppressing
  Brier makes the claim look better than the evidence supports). Both figures required.
- Any language implying the scoring rule uses self-reported model confidence. It does not.
- Qwen apologetic footnote presenting 74.8% exact evidence rate as a model-quality
  limitation. Correct statement if Qwen must be mentioned: M2 audit shows 53.7% (hybrid)
  and 61.4% (LLM-only) of exact-invalid strings are recoverable `REPAIRED_ELLIPSIS`
  copy-collation artifacts; grounded rates 94.7% and 90.9% respectively. If the Qwen
  arm does not need to appear in the calibration paragraph, remove the footnote entirely.
  (P4 §Qwen Footnote; see §4.2 below)

### 4.2  Evidence Groundedness (Unified Metric M2)

**Content source:** M2 (`evidence_groundedness_metric.md`), all sections.

**Subsection purpose:** Define the unified `evidence_grounded_rate` metric and explain
why `REPAIRED_*` grades count as grounded (semantically neutral formatting repair;
every repaired span is source-exact by construction). This is the canonical cross-task
shared component whose ablation (§5.1) shows structural inertness on the representative
validation surfaces — the guard is present but producers already emit grounded evidence.

**Key fact:** Three call sites previously computed the same raw `in` test under two
names (`evidence_valid` vs `evidence_text_contained`). The divergence was accidental.
Collapsing to `evidence_grounded_rate` removes cross-architecture footnotes that
blocked fair comparison.

**Qwen resolution (from M2 audit):**

| Model arm | Exact rate | Grounded rate | Gap explanation |
|-----------|----------:|---------------:|----------------|
| Qwen hybrid | 74.8% | **94.7%** | 53.7% of exact-invalid = `REPAIRED_ELLIPSIS` |
| Qwen LLM-only | 76.5% | **90.9%** | 61.4% of exact-invalid = `REPAIRED_ELLIPSIS` |

The gap is a metric artifact of ellipsis-formatting collation, not evidence absence.

### 4.3  Abstention / Risk Coverage

**Content source:** Gan reliability scorecard P0.2 (risk coverage); P1.1 (test450
port); reliability_d_gating_value_validation750 (AUROC 0.684 on single-model gate).

**Key numbers:**
- Gan External Risk Score failure AUROC: **0.781** (cross-model agreement leg;
  validation750, external features only)
- Holdout port (test450): agree-only coverage 65.8%; selective risk 12.2% vs base
  error 19.1%; AUROC 0.648
- Single-model abstention (variant-D confidence): AUROC 0.684; peak abstention
  precision 2.6× random at 90% coverage; modest absolute lift (88.4% → 90.5%
  costs 10% coverage)

**ExECTv2 cross-model agreement:** Three model-swap outputs exist (GPT, DeepSeek,
Qwen); agreement signal has not been computed as an abstention gate — the strongest
Gan signal unused on ExECTv2. Flag as a concrete future direction.

### 4.4  Operational Reliability (Gate Status, Cross-Model)

**Content source:** P2 §4 (gate-status language); P1 §4.x.6 (SF registry caveat).

**Key table** (full-200 predeclared readiness gates):

| Model | Overall F1 | Call failures | Parse/schema failures | Gate status |
|-------|----------:|---------------:|----------------------:|-------------|
| GPT-4.1-mini | 0.8356 | 0 | 0 | pass |
| DeepSeek chat | 0.8566 | 0 | 1 | **pass_with_caveat** |
| Qwen 3.6 35B | 0.8197 | — | — | (per respective predeclaration) |

DeepSeek `pass_with_caveat` language belongs here, in the apparatus, not in the
headline (see §3.1.3). Evidence rate 1.0000 for all completed rows across models.

### 4.5  Consistency (Semantic Entropy, Gan)

**Content source:** Gan reliability P2.1; RUN_INDEX §`gan2026_reliability_p2_1_semantic_entropy`.

**Key numbers (validation-only, live gpt-4.1-mini, n=150, k=4):**
- Mean label entropy: **0.012**; mean kind entropy: **0.003**
- `band_unknown` label entropy: **0.000** across all four temperatures
- Verdict: **H0_confirmed (confident over-reading)** — raw prose varies across
  temperatures; rendered label/kind does not. Consistency rating restores to 4/5.

ExECTv2 equivalent: probe returned **3 of 6 pre-registered checks passed**
(task-bound ceiling confirmed; error entropy elevated 0.287 vs correct 0.069; cross-model agreement lower on
errors 21.8% than correct 69.4% — mechanism partially differs from Gan H0). See §3.2.3.

---

## §5  Unified Component Impact / Stage Ladder

*Replaces the two separate component-impact tables under §4.1 and §4.2. One cross-task
figure + two task-specific ladder panels, unified under the portability taxonomy of §1.2.*

### 5.1  Cross-Task Shared-Component Ablation (M3 Primary Result)

**Content source:** M3 (`cross_task_shared_component_ablation_2026-06-27.md`),
primary and secondary tables.

*Evidence validity: validation-side aggregate-only replay; no model calls; no new freeze.
Source: `experiments/cross_task_shared_component_ablation_2026-06-27.json`.*

#### Primary Table — `evidence_validation` (category: `general`)

| Component | Task | Split | Baseline | Component-off | Δ |
|-----------|------|-------|----------:|--------------:|--:|
| `evidence_validation` | ExECTv2 | dev140 | 0.8308 | 0.8308 | **0.0000** |
| `evidence_validation` | Gan2026 | validation | 0.9093 | 0.9093 | **0.0000** |

**Interpretation:** The evidence gate is structurally inert on both tasks' representative
validation surfaces. Producers already emit verbatim-grounded mentions / rule outputs
already pass the gate. The guard is present but does not move the declared score on
these splits. This is not a reason to remove the gate — it is a sign the gate is
working as designed (it filters at evidence ingestion, not at score-time).

Do not overstate: these rows do not prove the component is globally unnecessary, and
must not be blended into reliability-scorecard or holdout claims. (M3 §Interpretation
Boundary)

#### Secondary Table — `standard_dictionary` (category: `clinical_epilepsy`)

| Component | Task | Split | Baseline | Component-off | Δ |
|-----------|------|-------|----------:|--------------:|--:|
| `standard_dictionary` | ExECTv2 | dev140 | 0.8697 | 0.8308 | **+0.0389** |
| `standard_dictionary` | Gan2026 | validation | 0.6360 | 0.6067 | **+0.0293** |

Normalization buys score on both tasks. Mechanisms differ (ExECTv2: CUI/dictionary
normalization; Gan: format-level SF label normalization — closest SF-normalization rung
on the Gan hybrid ladder). The portability category `clinical_epilepsy` captures this
correctly: shared clinical domain, different task-level implementations.

#### Deferred: Date-Arithmetic Policy

No clean cross-task ladder rung available from the current harness — would require
Gan one-family-off replays (`seizure_free_duration_date_instrumentation`) outside
this harness. Flag as deferred. (M3 §Mapping Notes)

### 5.2  ExECTv2 Format-Layer Contribution (Benchmark-Format Category)

**Content source:** P1 §4.x.4–§4.x.5; benchmark surface reconciliation Tables 1–2.

*Evidence validity: dev140 validation-only replay (Δ); frozen aggregate full-200 (full-200 Δ).*

#### dev140 component-off (four-family `clinical_headline`)

| Component | Category | Δ (GPT-4.1-mini dev140) |
|-----------|----------|------------------------:|
| `residual_semantic_lens` | `benchmark_format` | +0.0175 |
| `headline_projection` | `benchmark_format` | +0.0283 |
| **Sum** | | **+0.0458** |

*Source: `exectv2_component_off_replay_dev140_20260626.json`; replay-only.*

#### full-200 format-layer delta (frozen aggregate)

| Model | Headline F1 | Clinical-recovery F1 | Δ (format layers) |
|-------|------------:|---------------------:|------------------:|
| GPT-4.1-mini | 0.8356 | 0.7922 | +0.043 |
| DeepSeek chat | 0.8566 | 0.8110 | +0.046 |
| Qwen 3.6 35B | 0.8197 | 0.7797 | +0.040 |

Format-layer delta is **smaller and tighter on full-200 (~+0.04)** than dev140,
consistent with the same-core adjudicator baking in more dictionary recovery before
the format layers operate.

### 5.3  Benchmark Surface Inversion — Rules vs. Hybrid (Two-Surface Result)

**Content source:** P1 §4.x.4; dev140 validation-only, nine-entity scorer.

The rules > hybrid inversion is a unified stage-ladder finding: on the published-benchmark
surface the `benchmark_format` layers are harmful (they improve clinical recovery but
not CUI/attribute-bundle fidelity). The stage-ladder figure should show this as a
branching point: one path optimizes clinical-recovery (hybrid), the other benchmark
fidelity (rules + deterministic bundle engineering).

**Key numbers** (dev140, nine-entity benchmark scorer):

| Verifier | Benchmark item F1 | Clinical-recovery |
|----------|------------------:|------------------:|
| Rules only (deterministic) | **0.3687** | lower |
| All-hybrid | 0.3100 | higher |
| Rules + hybrid Inv (best-of) | 0.3877 | — |
| SF rules | **0.6921** | — |
| SF hybrid | 0.3472 | 0.782 |

Inversion is largest on SeizureFrequency: hybrid gains +0.18 clinical-recovery
but loses −0.34 benchmark item F1 relative to rules. Direct consequence of the
wall-transfer story (§3.2): hybrid promotes extraction confidence; the benchmark
scorer penalizes over-specified bundles; the same over-reading mechanism drives both.

### 5.4  Gan Stage-Ladder Reference

**Content source:** existing `experiments/gan2026_component_stage_ladder_validation_20260624.json`.

Present as a companion panel to §5.1–§5.3 — the Gan deterministic → hybrid ladder
(det floor → normalize → llm_selection → benchmark_repair → fresh_evidence). Lift the
existing Observatory/laboratory-page figure rather than redrafting. Note the M3
cross-task read-out (§5.1) lands at the `normalize` rung for Gan (+0.0293).

---

## CUT List — Items Removed from P5 (Consensus/Fresh Selector)

The consensus/fresh selector (`gan2026_consensus_fresh_agreement_selector_v0_9`)
**fails the closing-campaign pre-registration bar** on seven of eight criteria (P5
evidence table). It does not beat the promoted production headline (selected 359/450 =
0.7978 vs single-SE 364/450 = 0.809); passes its own Gate 4 bar by 0.0001 on the
exact-source path while the higher-gain variant fails; holds changed-label precision
at the floor (40% of holdout label changes wrong); and adds no novel paper claim beyond
the closeout. The closeout headline stands alone.

**Manuscript deletions:**

| # | Item to remove | Location in paper_manuscript_2026-06-26.md |
|---|---------------|---------------------------------------------|
| C1 | §4.1.2 subsection (consensus/fresh Gate 4 audits) | §4.1.2 |
| C2 | Table 3 (consensus/fresh Gate 4 result table) | Table 3 |
| C3 | Exact-source "frozen exact v0.9 selector holdout" from promoted-result prose | §4.1 promoted results |
| C4 | Selector rows in architecture comparison tables (alongside single SE and multi-trace hybrid) | Any comparison table listing selector as a promoted row |
| C5 | Reference to selector as a headline or promoted result in the abstract/conclusions | Abstract, §7 conclusions |

**Permitted retention (one sentence maximum, appendix only):**
> Validation-side component-ladder evidence shows corroboration-gated switching over
> a deterministic floor can yield validation gains (733/750, 0 C→W) but does not
> transfer to a holdout score above the simpler promoted architecture — consistent with
> closeout finding #3 ("hybrid/ensemble/guard apparatus buys little").

**Source/code deletion list** (future cleanup pass; no action in this outline task):
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/consensus_fresh_agreement_selector.py`
- `tests/test_gan2026_consensus_fresh_agreement_selector.py`
- Build drivers: `build_gan2026_v05_*`, `build_gan2026_v06_*`, `build_gan2026_v08_*`,
  `build_gan2026_v09_*` (frozen gate series), `build_gan2026_v10_*`
- Protocol doc: `docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`
- Experiment artifacts: `experiments/gan2026_consensus_fresh_*` and frozen gate reports
  `2026-06-26` (retain archived copies under `experiments/archive/` per repo policy)
- Cross-references: `paper_manuscript_2026-06-26.md` §4.1.2, Table 3, source list;
  `src/.../gan2026/agentic/README.md`; `docs/experiments/retained_evidence_manifest.md`;
  `docs/design/gan2026_rule_register.md` (selector policy entries)

---

## Section Count and Evidence Validity Summary

**Total sections: 5 top-level (§1–§5)**
**Total subsections: 20**

| § | Subsections | Primary sources | Evidence validity of key numbers |
|---|------------|-----------------|----------------------------------|
| 1 Shared architecture | 1.1–1.3 | Decomp review; P1 §4.x.6; definitions.yaml | Code audit; dev140 replay |
| 2 What LLM adds | 2.1–2.3 | Existing Gan tables; P1 full | Frozen holdout (Gan test450); frozen aggregate full-200 (ExECTv2); dev140 validation-only (like-for-like) |
| 3 What generalizes | 3.1–3.3 | P2; P3; P2.1 | Frozen aggregate `full-200`; validation-only probe (entropy); wall-transfer probe 3 of 6 pre-registered checks passed — task-bound ceiling confirmed; mechanism partially differs |
| 4 Unified reliability | 4.1–4.5 | P4; M2; Gan scorecard; RUN_INDEX | Aggregate full-200 validation; validation750; test450 frozen holdout (Gan only) |
| 5 Component impact | 5.1–5.4 | M3; P1 §4.x.4–5; gan2026 ladder | Dev140 replay; frozen aggregate full-200; validation750 replay |

---

## Relationship Map: Source Draft → Spine Section

| Source artifact | Primary spine placement | Secondary |
|-----------------|------------------------|-----------|
| P1 benchmark reconciliation | §2.2 (like-for-like + two-surface finding) | §1.3 (SF registry caveat); §5.2–5.3 |
| P2 DeepSeek model-agnostic | §3.1 (What generalizes) | §2.2.3 (format-layer table) |
| P3 wall transfer | §3.2 (What generalizes) | §4.5 (consistency cross-ref) |
| P4 calibration revision | §4.1 (Unified reliability) | — |
| P5 selector fate (CUT) | Appendix one-sentence only | No headline placement |
| M2 evidence groundedness | §4.2 (Unified reliability) | §5.1 (why evidence_validation Δ=0) |
| M3 cross-task ablation | §5.1 (Component impact) | §1.2 (portability taxonomy) |

---

## Open Actions Before P6b (Full Draft)

1. **[PROBE COMPLETE — 3 of 6 checks passed]** `exectv2_sf_wall_transfer_probe_2026-06-27.md` returned
   3 of 6 pre-registered cross-dataset checks passed. Task-bound ceiling confirmed; Gan H0_confident_over_reading does not
   fully transfer (error entropy 0.287 vs correct 0.069; cross-model agreement 21.8% on
   errors vs 69.4% correct; 43.6% error cells unanimous wrong). §3.2.3 updated to reflect
   partial verdict; use P3 §3a "task-bound ceiling transfers; mechanism partially differs"
   framing throughout.
2. **ExECTv2 three-way comparison** (§2.3): assemble deterministic / LLM-only / hybrid
   comparison in paper form to close the §7 target criterion on task 2; or explicitly
   acknowledge as deferred with named reason (not assembled, not that it would fail).
3. **Cross-model agreement abstention gate** (§4.3): compute the cross-model agreement
   signal on ExECTv2 model-swap outputs as an abstention probe — the strongest Gan
   reliability signal has not been applied to ExECTv2.
4. **P5 manuscript cuts** (§CUT list items C1–C5): execute removals from
   `paper_manuscript_2026-06-26.md` before circulating the revised draft.

---

*Writing only. No git operations. No row-level reads. No model calls.*
*Wave 4 workstream P6a; consumes P1–P5, M2–M3.*
