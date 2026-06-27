# Paper Manuscript — Capability-First Restructure

Date: 2026-06-27

Status: capability-first restructure. Section 4 reorganizes the two-task results by
what the system can do (shared architecture, LLM contribution, generalization,
reliability, component impact) rather than by which task ran first. Section 5 adds
Discussion (D.1–D.5) and Section 6 adds Contributions (C1–C5). Consensus/fresh
selector (v0.9) cut from all paper-facing promoted results per P5 CUT recommendation
(`docs/research/consensus_fresh_selector_fate_2026-06-27.md` C1–C5); the Gan
closeout headline stands alone.

Primary sources (P6 restructure):

- `docs/research/paper_drafts/capability_first_results_section_2026-06-27.md`
- `docs/research/paper_drafts/capability_first_discussion_contributions_2026-06-27.md`
- `docs/research/consensus_fresh_selector_fate_2026-06-27.md` (CUT C1–C5 applied)

Retained from 2026-06-26 draft:

- `docs/research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`
- `docs/research/exectv2_results_section_draft_2026-06-26.md`

## Claim Boundary (Both Tasks)

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
progressively higher test450 Purist accuracy (see Tables 1–2 below; not
reproduced here). The decisive LLM contribution is in resolving frequency-qualifier
ambiguity and in abstracting across orthographic and syntactic variation — exactly the
cases where pattern-matching rules are brittle.

**Table 1. Gan 2026 three-way comparison on validation750 (`gpt-4.1-mini`).**

| Architecture | Rendered | Purist of rendered | Pragmatic of rendered | Reading |
| --- | ---: | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | 741/750 | 673/741 (0.908) | 681/741 (0.919) | High validation score; large holdout drop. |
| `hybrid` | 597/750 | 526/597 (0.881) | 545/597 (0.913) | Strong rendered accuracy; too many null/routed rows. |
| `hybrid_structured_events` | 748/750 | 661/748 (0.884) | 679/748 (0.908) | Best LLM-using validation coverage/accuracy balance. |
| `llm_only_canonical_pipeline` | 750/750 | 582/750 (0.776) | 614/750 (0.819) | Comparator; below hybrid structured events. |

**Table 2. Gan 2026 frozen `test450` aggregate audit (`gpt-4.1-mini`).**

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
semantic-entropy probe (P2.1, n=150). ExECTv2 — frozen aggregate full-200 model-swap +
dev140 self-consistency artifact replay (wall-transfer probe). Probe verdict: **PARTIAL**
(3/6 checks passed; task-bound ceiling confirmed; Gan H0 mechanism partially differs).
Source: P3 `wall_transfer_cross_dataset_2026-06-27.md`.*

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

**Probe result (PARTIAL — 3/6 checks passed).** The wall-transfer probe
(`exectv2_sf_wall_transfer_probe_2026-06-27.md`) ran on dev140 self-consistency artifacts
and returned a partial verdict. The cross-dataset claim is:

> SeizureFrequency is the weakest ExECTv2 family under a frozen same-core architecture
> across all tested LLMs (GPT-4.1-mini 0.7525, DeepSeek chat 0.7602, full-200 aggregate;
> GPT 0.7645, DeepSeek 0.7658 on dev140). This weakness is task-bound: **43.6% of SF
> error cells are temperature-unanimous wrong** (4/4 same wrong answer), confirming a
> material confident-error component consistent with the Gan wall pattern. However, the
> Gan H0_confident_over_reading mechanism does **not** fully transfer: SF error entropy is
> elevated (0.287 vs 0.069 for correct cells) and cross-model agreement is lower on error
> cells (21.8%) than correct cells (69.4%) — the reverse of the Gan `band_unknown` pattern
> where every wrong answer was entropy-zero and stable across all temperatures. The ExECTv2
> SF floor is a **mixed** mechanism: some errors are as confidently wrong as Gan's
> over-reading; others are genuinely uncertain and heterogeneous across models. The
> **task-bound ceiling transfers; the mechanism partially differs.**

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
| Like-for-like dev140: 0.3877 per-item / 0.6972 per-letter | Published-benchmark, nine-entity | Validation-only, frozen aggregate | `exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json` |
| Rules > hybrid on SF benchmark (+0.34 per-item) | Published-benchmark | Validation-only, frozen aggregate | `exectv2_benchmark_surface_overall_2026-06-18.md` |
| Format-layer delta ~+0.04 stable across models | `clinical_headline` | Frozen aggregate full-200, component-off replay | `exectv2_component_off_replay_full200_20260626.json` |
| DeepSeek ≥ GPT full-200 (+0.021) | `clinical_headline` | Frozen aggregate full-200 | same |
| Gan wall: 0.842 ceiling, selector oracle 739/750 | Purist accuracy | Frozen test450 | orchestrator state; closeout synthesis |
| Gan P2.1: mean label entropy 0.012; band_unknown 0.000 | Purist label entropy | Validation-only probe (n=150) | `gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md` |
| ExECTv2 SF weakest across all models (0.75–0.76 full-200) | `clinical_headline` | Frozen aggregate full-200 | `exectv2_same_core_model_swap_full200_2026-06-25.md` |
| Calibration: Brier 0.2245 vs base-rate 0.2387 | `clinical_headline` | Aggregate full-200 validation | ExECTv2 reliability scorecard 2026-06-22/2026-06-25 |
| Cross-dataset wall-transfer mechanism | PARTIAL probe verdict (3/6 checks passed) | Dev140 self-consistency artifact replay | `exectv2_sf_wall_transfer_probe_2026-06-27.md`; task-bound ceiling confirmed; Gan H0 mechanism partially differs (error entropy 0.287 vs 0.069; cross-model agreement 21.8% on errors vs 69.4% correct; 43.6% error cells temperature-unanimous wrong) |

---

## 5 Discussion

### D.1 What the System Does Well and Why the Architecture Deserves Credit

The central claim of this work is that a decomposed, stage-owned architecture — not any
particular large language model — is the primary carrier of clinical extraction quality.
Three pieces of evidence support this claim. First, swapping the generation LLM while
holding the component graph, scoring surface, and evaluation protocol constant does not
degrade performance: DeepSeek chat reaches **0.8566** overall clinical-headline F1 on the
frozen full-200 aggregate versus GPT-4.1-mini's **0.8356**, a +0.021 lead distributed
across Diagnosis (+0.031), SeizureFrequency (+0.008), and Investigations (+0.053), with
Prescription tied at 0.8926 (evidence validity: frozen aggregate full-200, same-core
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
estimate). The gap is not a measurement artifact. The project's own 2026-06-18
like-for-like analysis locates the loss in **CUI reproduction and attribute-bundle
strictness**, not in concept recall or entity recognition, and identifies the lever as
deterministic phrase/CUI/attribute-bundle fidelity engineering that was explicitly
deprioritised in favour of the clinical-recovery evaluation framework. This is a defensible
choice; it should be narrated, not quietly elided.

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

The Gan strand's central negative result — the honest ceiling of **0.842 test450 Purist**
for the V12 hybrid and **0.809** for the single structured-event pass — is not a failure of
optimization effort. It is a characterization of a clinical-reasoning limit that no
forward-observable signal can safely breach: the model over-reads ambiguous
seizure-frequency evidence as quantified rates with high confidence, and the signal
distinguishing *withhold-to-unknown* from *emit-rate* is absent from every inference-time
feature (selector oracle 739/750; 11 rows with no Purist-correct component;
structural-impossibility finding from C7, which showed the no-correct residual rows are
feature-identical to genuine-rate rows on every observable dimension — only hidden gold
separates them).

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
**0.7602** (frozen full-200 aggregate). The other families are materially stronger
(Diagnosis 0.8397–0.8708, Prescription 0.8926, Investigations 0.8563–0.9091). The gap is
not model-specific (DeepSeek narrows it by only +0.008 vs GPT), not an evidence-failure
(evidence rate is 1.0000 on all model-swap runs), and correctible by task-specific
adjudication (dev140 v08 with SF adjudicator: 0.9053). These are the same structural
signatures as the Gan wall: persistent across models, not addressable by model choice alone,
reducible by targeted post-processing that corrects the base extraction residual, but not
eliminated at the base extraction level.

The wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) ran on dev140
self-consistency artifacts and returned a **partial verdict** (3/6 checks passed). The
cross-dataset claim can now be stated with evidence: **43.6% of SF error cells are
temperature-unanimous wrong** (4/4 same wrong answer), confirming that a material
confident-error component is present — consistent with the Gan pattern. However, the full
Gan H0_confident_over_reading mechanism does not transfer: SF error entropy is elevated
(0.287 vs 0.069 for correct cells) and cross-model agreement is lower on error cells
(21.8%) than correct cells (69.4%) — the reverse of the Gan `band_unknown` pattern where
every wrong answer was entropy-zero and stable across all temperatures. The ExECTv2 SF
floor is a *mixed* mechanism: some errors are as confidently wrong as Gan's over-reading;
others are genuinely uncertain and heterogeneous across models. The confirmed finding is
**task-bound ceiling that transfers; mechanism that partially differs** — and this is the
more honest, more informative characterization: *a system whose ceiling is task-bound — not
system-bound — with an error composition that reveals both the clinical-reasoning limit and
its mixed character on a second independent corpus*. The wall is a characterization, not an
apology.

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

**Frozen aggregate-only inspection policies.** The standing protocol (no full-200 or holdout
row-level inspection without a fresh predeclaration) protected the test set from
contamination through seven experiment cycles, including structural-impossibility findings
that would have been tempting to probe at row level. That the C7 finding (feature
indistinguishability of no-correct residual from genuine-rate rows) was established without
reading any test row is itself a protocol achievement.

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

**S1 — Cross-task thesis-complete criterion unmeasured.** The reliability thesis §7 sets
the thesis-complete criterion as "a shared core demonstrably reused across tasks." Structural
reuse is real at the code level (49 ExECTv2 modules import `core`/`tasks.shared`/
`tasks.seizure_frequency`), but the SeizureFrequency clinical machinery — the declared
"bridge" — is re-implemented under `exectv2/deterministic/sf_state_projection.py` and
`rules/seizure_free.py`; `assembly/lenses/seizure_frequency.py` does not import the Gan SF
normalizer. The shared-component ablation that would measure the cross-task dividend (turn one
shared component off, report delta on both tasks at once) is predeclared in the
`exectv2_component_off_reliability_ablation_plan_2026-06-26.md` but not yet executed at
cross-task scope. The modularity thesis is supported by structural evidence and the model-swap
result; the quantified cross-task component dividend remains future work.

**Partial wall mechanism — ExECTv2 entropy probe not yet run.** The cross-dataset
claim that the confident-over-reading mechanism transfers to ExECTv2 SF requires a
pre-registered forward-observable-feature entropy probe on a stratified SF slice. The probe
specification is complete (acceptance criteria predeclared: mean label entropy on
wrong-SF-extraction rows < 0.05 for H0 confirmation; per-temperature stability > 0.90). The
structural parallel is confirmed; the mechanism claim is pending. If the probe returns high
entropy on ExECTv2 SF wrong rows, the cross-dataset claim must be revised: the Gan wall
mechanism is Gan-specific, and the ExECTv2 SF gap has a different, potentially addressable
origin.

**Calibration is near-base-rate, not deployment-ready.** The scoring rule's aggregate
full-200 validation calibration is Brier **0.2245** versus constant base-rate **0.2387**
(Δ = 0.0142), ECE **0.0432**. The improvement above base rate is real but small. All signal
carried by the rule comes from external predeclared features (family identity, evidence-
provenance indicators, evidence-ambiguity flags), not from model-reported confidence, which
is degenerate on the Gan strand and unused here. Holdout calibration confirmation has not
been run.

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
(evidence validity: dev140 validation-only, frozen aggregate). The gap is explained:
spelling correction on the clinical letters drifted the gold character offsets, making the
offset-tuned published number non-reproducible on the corrected surface; the residual gap
on the aligned surface is concentrated in CUI reproduction and attribute-bundle strictness,
representing closeable deterministic fidelity engineering that was explicitly deprioritised.
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
are parallel. The delta is a component-impact finding; the full cross-task shared-component
dividend requires the predeclared cross-task ablation (S1; future work).

---

**Contribution 3: The wall as a cross-dataset confident-over-reading phenomenon — partial
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
over-reading is also confident, not merely frequent — is supported by the partial
ExECTv2 SF wall-transfer probe (3/6 checks: 43.6% temperature-unanimous wrong;
error entropy 0.287 vs 0.069 correct; cross-model agreement 21.8% on errors vs
69.4% on correct). The mechanism partially differs from Gan H0, but the
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
overall F1** on the frozen full-200 aggregate (0.8566 vs 0.8356; evidence validity: frozen
aggregate full-200, same-core `exectv2_2call_no_sf_adjudicator` architecture, predeclared
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
| C1 — Benchmark reconciliation | dev140 validation-only, frozen aggregate | No full-200 published-benchmark surface computed |
| C2 — Component ablation (gate inert; SF norm matters) | dev140 replay-only, aggregate | No model calls; cross-task ablation scope is future work (S1) |
| C3 — Wall cross-dataset (partial) | Frozen aggregate full-200 (ExECTv2); validation-only probe (Gan P2.1); partial probe 3/6 | Ceiling transfers; mechanism partially differs; no holdout on ExECTv2 |
| C4 — Model-agnostic architecture | Frozen aggregate full-200, predeclared gate | No holdout on non-primary models; row-level attribution excluded |
| C5 — Evaluation discipline | Validation-only + test450 aggregate (Gan); validation-only (ExECTv2) | No new experiments; retrospective characterization of completed work |

---

## Do Not Use As Claims

- Gan or ExECTv2 holdout/full-200 reliability is deployment-validated.
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
- The full Gan H0_confident_over_reading mechanism transfers cross-dataset: probe fails 3 of 6 checks (error entropy elevated 0.287 vs correct 0.069; cross-model agreement lower on errors 21.8% vs correct 69.4%; elevated-error-entropy pattern is SF-specific). The task-bound ceiling transfers; the mechanism is mixed, not purely confident.
- The shared SF machinery is literally identical across tasks (ExECTv2 re-implements projection; structural reuse is the accurate claim, not code identity).
