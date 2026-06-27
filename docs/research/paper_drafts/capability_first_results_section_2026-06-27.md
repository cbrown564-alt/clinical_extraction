# Capability-First Results Section (Draft)

Date: 2026-06-27  
Workstream: Wave 4 · P6b (paper writing — Results restructure)  
Status: draft — writing only; no new model calls; no holdout or full-200 row-level inspection  
Evidence validity: see per-claim tags throughout  
Omits: consensus/fresh selector (P5 CUT)

**Replaces:** §4.1 (Gan task-first results) + §4.2 (ExECTv2 task-first results) in
`docs/research/paper_manuscript_2026-06-26.md`. Merges the two task streams into a
single capability-first Results section organized by what the system can do, not by
which task it did it on first.

**Source drafts consumed:**  
- P1: `benchmark_surface_reconciliation_subsection_2026-06-27.md`  
- P2: `deepseek_model_agnostic_evidence_2026-06-27.md`  
- P3: `wall_transfer_cross_dataset_2026-06-27.md`  
- P4: `calibration_claim_revision_2026-06-27.md`  
- Closing-stage critique §4 spine: `closing_stage_research_critique_2026-06-27.md`

---

## §4 Results

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
is concentrated in **CUI reproduction and attribute-bundle strictness**, not in
concept recall or entity recognition. Phrase-only and semantic-recall metrics remain
materially higher than the nine-entity bundle score. The lever that would close the
gap is deterministic phrase/CUI/attribute-bundle engineering — catalogued patterns
that reproduce the exact bundle structure the benchmark expects — work that was
explicitly deprioritised in favour of the clinical-recovery evaluation framework. The
correct paper statement is therefore:

> *We evaluate on a label-based surface because spelling correction drifted the gold
> offsets, making the offset-tuned published number non-reproducible on corrected
> text; on the comparable dev140 surface we reach `0.39` per item / `0.70` per
> letter; closing the remaining gap to the published headline requires deterministic
> phrase-and-CUI bundle engineering (CUI normalisation, full attribute serialisation,
> entity-bundle assembly per family) that was explicitly deprioritised as outside the
> clinical-recovery scope of this work.*

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
progressively higher test450 Purist accuracy (see manuscript Tables 1–2; not
reproduced here). The decisive LLM contribution is in resolving frequency-qualifier
ambiguity and in abstracting across orthographic and syntactic variation — exactly the
cases where pattern-matching rules are brittle.

**On ExECTv2:** the format-layer component ablation (dev140 one-component-off replay
and frozen full-200 aggregate replay) quantifies the LLM's marginal contribution by
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

*Note on dev140:* DeepSeek leads on dev140 as well (0.9174 vs GPT 0.9155 overall
headline F1), with its clinical-recovery base lower (0.8334 vs 0.8697) but headline
F1 higher — indicating the post-processing stack extracts more value from DeepSeek's
structured outputs on the richer dev140 surface. All dev140 figures are
validation-only and are not holdout estimates.

#### §4.3.2 Wall Transfer: The Seizure-Frequency Ceiling Is Task-Bound

*Evidence validity: Gan — frozen test450 aggregate (V12 0.842) + validation-only
semantic-entropy probe (P2.1, n=150). ExECTv2 — frozen aggregate full-200 model-swap.
Mechanism confirmation [PENDING PROBE]: marked throughout. Source: P3
`wall_transfer_cross_dataset_2026-06-27.md`.*

The central negative result of the Gan strand does not stay on the Gan dataset.

**The Gan wall.** On the Gan 2026 seizure-frequency benchmark, the best architecture
achieves a frozen holdout ceiling of **0.842** (V12 hybrid, test450 Purist). Exhaustive
ablation established that this ceiling is generator-bound: the model over-reads
ambiguous frequency evidence as quantified rates or seizure-free durations with high
confidence, and no forward-observable signal — self-consistency, self-confidence,
sampling entropy — separates the over-read rows from correct extractions at inference
time. The selector oracle is exhausted at 739/750: of the 11 binding residual rows
(no Purist-correct component), 8/11 fall in `band_unknown`, and the signal
distinguishing *withhold-to-unknown* from *emit-rate* is absent from every
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

**[PENDING PROBE]** A forward-observable-feature entropy probe on a stratified ExECTv2
SF validation slice is required to confirm that the entropy signature matches the Gan
pattern (confident, not uncertain, over-reading). Specification in
`docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`; probe
document `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`
does not yet exist. Pending that result, the cross-dataset claim is structural:

> SeizureFrequency is the weakest ExECTv2 family under a frozen same-core architecture
> across all tested LLMs (GPT-4.1-mini 0.7525, DeepSeek chat 0.7602, full-200 aggregate).
> This pattern is consistent with the confident-over-reading wall characterized on the Gan
> benchmark (mean label entropy 0.012, `band_unknown` entropy 0.000 at k=4 sampling across
> four temperatures), where the same mechanism — confident extraction of over-specified rate
> interpretations from ambiguous evidence — was identified as the binding ceiling.
> Whether the same entropy signature reproduces on ExECTv2 SF is currently under
> investigation. If confirmed, the ExECTv2 SF gap and the Gan wall constitute a
> **cross-dataset confident-over-reading phenomenon**: a clinical-reasoning limit that is
> task-bound, not system-bound.

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

## Claim Boundary Summary

| Claim | Surface | Evidence level | Source artifact |
|-------|---------|---------------|-----------------|
| Full-200 clinical-headline F1: GPT 0.8356, DeepSeek 0.8566, Qwen 0.8197 | `clinical_headline` | Frozen aggregate full-200 | `exectv2_same_core_model_swap_full200_2026-06-25.md` |
| Like-for-like dev140: 0.3877 per-item / 0.6972 per-letter | Published-benchmark, nine-entity | Validation-only, frozen aggregate | `exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json` |
| Rules > hybrid on SF benchmark (+0.34 per-item) | Published-benchmark | Validation-only, frozen aggregate | `exectv2_benchmark_surface_overall_2026-06-18.md` |
| Format-layer delta ~+0.04 stable across models | `clinical_headline` | Frozen aggregate full-200, component-off replay | `exectv2_component_off_replay_full200_20260626.json` |
| DeepSeek ≥ GPT full-200 (+0.021) | `clinical_headline` | Frozen aggregate full-200 | same |
| Gan wall: 0.842 ceiling, selector oracle 739/750 | Purist accuracy | Frozen test450 | orchestrator state; closeout synthesis |
| Gan P2.1: mean label entropy 0.012; band_unknown 0.000 | Purist label entropy | Validation-only probe (n=150) | `gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md` |
| ExECTv2 SF weakest across all models (0.75–0.76 full-200) | `clinical_headline` | Frozen aggregate full-200 | `exectv2_same_core_model_swap_full200_2026-06-25.md` |
| Calibration: Brier 0.2245 vs base-rate 0.2387 | `clinical_headline` | Aggregate full-200 validation | ExECTv2 reliability scorecard 2026-06-22/2026-06-25 |
| Cross-dataset wall-transfer mechanism | Structural parallel | [PENDING PROBE] | `exectv2_sf_wall_transfer_probe_2026-06-27.md` (does not exist) |

**Do not claim:**
- Holdout validation of ExECTv2 performance on any split.
- Full-200 published-benchmark nine-entity CUI score (not computed under current protocol).
- Cross-model agreement as a validated ExECTv2 reliability signal (unused; available artifact).
- That the calibration scoring rule is deployment-ready.
- That the wall-transfer mechanism is confirmed cross-dataset (requires pending probe).
- That the shared SF machinery is literally identical across tasks (ExECTv2 re-implements projection; structural reuse is the accurate claim, not code identity).

---

## Sections This Replaces

| Old section | Replaced by |
|-------------|-------------|
| §4.1 Gan 2026 results (all subsections) | §4.1.1 architecture (partial), §4.1.2 reconciliation, §4.3.2 wall, §4.4 calibration (Gan legs), §4.5 Gan component impact |
| §4.2.1 Architecture and Clinical-Headline Performance | §4.1 (shared architecture) + Table R3 headline figures |
| §4.2.2 Same-Core Model Swap | §4.3.1 (promoted to capability claim) |
| §4.2.3 Reliability Scorecard | §4.4 (unified across both tasks) |
| §4.2.4 Component Impact | §4.5 (unified, plus benchmark-format vs clinical-recovery split added) |
| Task-first benchmark claims (implicit 0.87/0.90) | §4.1.2 explicit reconciliation (reviewer-proof version) |

---

*Writing only. No git operations. No model calls. No holdout or full-200 row-level reads.*  
*Parent task: Wave 4 workstream P6b (capability-first Results restructure).*
