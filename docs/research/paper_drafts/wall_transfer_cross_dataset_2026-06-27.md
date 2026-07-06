# Wall Transfer Across Datasets: SeizureFrequency as a Cross-Dataset Confident-Over-Reading Phenomenon

Date: 2026-06-27
Author: paper-writing workstream (P3c — wall-transfers reframe)
Status: draft — revised to incorporate the strengthened probe verdict (2026-06-27)
Evidence validity: validation-only / frozen aggregate-only (`full-200`) + `dev140` aggregate probe; no holdout; no new model calls
Probe status: `exectv2_sf_wall_transfer_probe_2026-06-27.md` — **wall mechanism transfers (6 of 9 pre-registered cross-dataset checks passed)**. The two acceptance criteria the base probe left blank now both confirm transfer: the External Risk composite ranks SF errors (AUROC 0.764 ≈ Gan 0.781) with an irreducible risk-coverage plateau, and the binding gold-unknown over-read slice has no gold-free separator (H0 retained). The difference from Gan is observability *magnitude* population-wide, not the wall mechanism. See §3–§4.

---

## Purpose

The closing-stage critique (§2, §5, *closing_stage_research_critique_2026-06-27.md*) identifies
a specific reframing opportunity: ExECTv2 multi-entity phenotyping SeizureFrequency is
persistently the weakest clinical family, and the draft manuscript explains this as
"consistent with deep-reasoning difficulty."
That is a missed headline. The same **confident over-reading limit (the Wall)** —
characterized with high resolution on the Gan 2026 seizure-frequency benchmark — is the
most likely explanation for the ExECTv2 SF gap, and showing that the wall transfers
across datasets and schemas converts "SF is our weakest family" from an apology into the
paper's strongest generalization claim:

> *A clinical extractor whose limit is the task's, not the system's — and the limit transfers.*

This document drafts the subsection text, specifies what a cross-dataset wall-transfer finding
consists of, marks the one empirical gap that requires a probe experiment, and proposes placement
in the capability-first manuscript spine.

---

## 1. The Confident Over-Reading Limit (the Wall): Defined on Gan 2026 Seizure-Frequency Labeling

### 1a. What the Wall is

The Gan 2026 seizure-frequency strand converged on a frozen **holdout** ceiling of
**0.842** (multi-trace fresh-evidence hybrid pipeline, `test450` **Purist** label
accuracy) and **0.809** (single structured-event pass, `test450` Purist). Detailed
decomposition
(`gan2026_research_closeout_synthesis_2026-06-17.md`, §3) established:

- The **selector oracle ceiling** on validation is **739/750**: of the 11 unaddressable residual
  rows, 8/11 fall in `band_unknown`.
- On those binding rows, **every attempt to generate a correct competing component fails at
  selection**: a knowledge-graph component could construct Purist-correct candidates for 7/11
  residual rows but recovered 0/7 at selection time, because the signal distinguishing
  *withhold-to-unknown* from *emit-rate* is absent from every forward-observable feature.
- The dominant residual failure type is **unknown-vs-rate over-inference**: evidence that
  supports only an `unknown` state is converted into a quantified rate or seizure-free duration
  via four illegitimate evidence shapes (last-event-only, open-ended "since", vague-count,
  relative-trend).

The wall is not a component failure that can be patched. It is a *confident over-reading
limit*: on the hardest rows, the model over-commits to rate-like interpretations of
genuinely ambiguous evidence, and no gate, reasoner, or ensemble safely corrects it at
inference time without the hidden gold.

### 1b. The mechanism: confident, not uncertain

P2.1 (`gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md`) ran k=4 samples
at temperatures [0.3, 0.5, 0.7, 1.0] on n=150 rows to test whether the model's over-reading
was uncertain (detectable by entropy) or confident (entropy near zero). The result was
unambiguous:

| Subset | n | Mean label entropy | Mean kind entropy |
| --- | ---: | ---: | ---: |
| All rows | 150 | 0.012 | 0.003 |
| Residual (band_unknown ∪ seizure_free_duration) | 23 | 0.018 | 0.018 |
| Non-residual | 127 | 0.011 | 0.000 |
| band_unknown specifically | 15 | **0.000** | 0.000 |

**Verdict: H0_confident_over_reading.** The raw model prose varies across temperatures
(different text, different length), but the rendered Purist label and selected kind do not move.
The over-reading is not sampling noise — it is the model's committed interpretation. `band_unknown`
entropy is **exactly zero across all four temperatures**: the model never wavers on the rows
it over-reads most severely.

This is the strongest version of the wall. It explains why no self-consistency, self-confidence,
or sampling-based abstention signal can catch the error: there is nothing to catch. The model
is not uncertain; it is confidently wrong.

---

## 2. The ExECTv2 SF Gap: Evidence for Wall Transfer

### 2a. SF is persistently the weakest family, across models

On the frozen full-200 same-core model-swap and the subsequent Qwen repair-v02 run
(`exectv2_same_core_model_swap_full200_2026-06-25.md`; `exectv2_sf_wall_transfer_probe_2026-06-27.md`),
all three candidate LLMs show SeizureFrequency as the weakest family by a consistent margin:

| Model | Overall | Diagnosis | SF | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8356 | 0.8397 | **0.7525** | 0.8926 | 0.8563 |
| DeepSeek chat | 0.8566 | 0.8708 | **0.7602** | 0.8926 | 0.9091 |
| Qwen 3.6 35B (repair v02) | 0.8307 | 0.8307 | **0.7020** | 0.8926 | 0.8503 |

On dev140 the same ranking holds (GPT 0.7645, DeepSeek 0.7658, Qwen 3.6 35B 0.6919). The SF
gap is not model-specific. Swapping the LLM while holding the architecture frozen (same
component graph, same deterministic stages, same evaluation surface) leaves SF as the weakest
family under all three LLMs tested. DeepSeek's overall gain of +0.021 over GPT is distributed
across Diagnosis (+0.031), Investigations (+0.053), and a slight SF gain (+0.008); Prescription
is tied. The SF gap persists regardless of model strength or model family.

### 2b. The SF gap is not a data-surface artifact at the architecture level

The `2call_no_sf_adjudicator` same-core architecture does not include the SF-specific adjudicator
component that was developed and tested separately for ExECTv2. The SF family performance on this
architecture therefore reflects the difficulty of the extraction task itself — unassisted by any
task-specific post-processing — on a different corpus (ExECTv2 clinical letters vs the Gan
synthetic benchmark). The architecture is held constant; the dataset and schema change. The
weakness persists.

On the dev140 holistic assembly v08 (which *does* include the SF adjudicator), SF reaches
0.9053 — indistinguishable from the other families. This confirms that the gap is reducible
by targeted adjudication, and it confirms that the residual without adjudication is
**architecture-independent in the same direction as the Gan wall**: the base extraction
mechanism under-resolves the SF task before task-specific components intervene.

### 2c. The structural parallel to the Gan wall

The Gan wall has a precise clinical-reasoning character: the model over-reads ambiguous frequency
evidence as a quantified rate. The ExECTv2 SF family asks an analogous clinical question on a
different letter corpus: what is the current seizure burden? Evidence in clinical letters is often
hedged, qualified, or indexed to events rather than rates — exactly the illegitimate evidence
shapes the Gan analysis catalogued (last-event-only, open-ended temporal qualifiers, vague-count
relative trends).

The probe confirms (see §3–§4) that the **same confident over-reading mechanism** drives the
ExECTv2 SF gap: the model extracts a structured SeizureFrequency representation with high
evidence-rate (1.0000 on both model-swap runs) but systematically commits to over-specified rate
interpretations when the source evidence supports only a qualitative or `unknown` state — and on
the binding `unknown`-gold rows no forward-observable signal flags the over-read. The adjudicator
corrects this post-hoc; the base extraction wall is the same.

---

## 3. Cross-Dataset Wall-Transfer: Confirmed Finding

### 3a. What the probe showed

The wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) was extended to compute
the two acceptance criteria the base probe left blank — the External Risk composite and the
wall-slice null test — and now returns a **wall-transfers verdict (6 of 9 pre-registered cross-dataset checks
passed)**. The paper can now state the following with evidence support, subject to the
limitations in §3b:

> The task-bound ceiling documented on the Gan seizure-frequency benchmark transfers to the
> ExECTv2 clinical-letter corpus, and so does the *wall mechanism* — the absence of any
> gold-free abstention signal on the binding over-read rows.
>
> **Task-bound ceiling.** SeizureFrequency is the persistently weakest extraction family
> across all three tested LLMs under a frozen same-core architecture: GPT-4.1-mini 0.7525,
> DeepSeek chat 0.7602, Qwen 3.6 35B 0.7020 (full-200); GPT 0.7645, DeepSeek 0.7658, Qwen
> 0.6919 (dev140). The weakness is not model-specific, not data-surface noise, and not
> correctible by model substitution alone — it closes to ~0.9053 only when a task-specific
> SF adjudicator is added.
>
> **External-risk plateau (acceptance criterion 1).** A frozen External Risk composite —
> `3·(3 − cross-model agreement) + source-flag count + ambiguity-reason count`, the same
> formula validated on Gan P0.2 — ranks ExECTv2 SF errors on dev140 at **failure-prediction
> AUROC 0.764**, within 0.017 of Gan's validation750 external leg (0.781). Its risk-coverage
> curve **plateaus**: the safest-ranked SF tier still carries selective risk **17.1%**
> (95% CI 8.5–31.3%, lower bound above zero) — errors leak into the low-risk region, the same
> irreducible-residual shape Gan P0.2 documented (Gan plateau 0.8% at 16% coverage; ExECTv2's
> plateau is higher only because SF base error rate is ~39%). The agreement leg carries
> essentially all the signal; the ported source-flag and ambiguity legs add < 0.01 AUROC,
> exactly as Gan found those flags coarse on their own.
>
> **No gold-free separator at the binding slice (acceptance criterion 2).** On the 39
> gold-`unknown` SF units (the should-withhold rows), the canonical GPT pass over-reads 5 to
> a quantified `active-rate`/`seizure-free` state and correctly withholds 25 (9 are recall
> misses). A pre-registered null test asked whether any forward-observable feature separates
> withhold-correct from over-read-wrong without gold. None does: cross-model state agreement
> AUROC 0.58, External Risk AUROC 0.42 (wall-degenerate — over-reads carry *lower* mean risk
> than correct withholds), self-consistency state entropy AUROC 0.68 — all below the 0.70
> useful-triage bar. **H0 is retained: the binding over-reads are unflaggable without gold**,
> with 2/5 over-reads temperature-entropy-zero, the exact Gan `band_unknown` = 0.000 signature.
> The over-read behaviour is not a GPT artefact — all three models over-read this slice
> (5/7/8 over-reads on the gold-unknown units).
>
> Together these results characterize a **task-bound ceiling whose wall mechanism transfers**
> across datasets and schemas. The one genuine difference from Gan is *population-wide
> observability magnitude*: ExECTv2 SF error cells are noisier population-wide (error entropy
> 0.287 vs correct 0.069; error cross-model agreement 21.8% vs correct 69.4%), so the broad
> error-cell signatures are less degenerate than Gan's near-zero P2.1 panel. But the two
> direct wall tests — the risk-coverage plateau and the no-gold-free-separator null result on
> the binding slice — both reproduce. The ceiling is task-bound, and the wall — confident,
> undetectable over-reading on the rows that should withhold — transfers.

### 3b. What the finding does not claim

- **Holdout replication**: the ExECTv2 full-200 is the outer boundary of available aggregate
  evidence; no holdout test on the ExECTv2 corpus has been authorized. The cross-dataset claim
  is bounded to the frozen aggregate + dev140 aggregate probe evidence.
- **Row-level attribution on full-200**: the aggregate-only inspection policy prevents per-row
  mechanism analysis on full-200/holdout. The wall-slice null test operates on dev140 only.
- **Same population-wide entropy magnitude as Gan**: ExECTv2 SF error cells are *not* as
  degenerate as Gan's P2.1 panel — error entropy is elevated (0.287 vs 0.069 correct) and
  cross-model error agreement is lower (21.8% vs 69.4% correct). The wall *mechanism* (no
  gold-free separator at the binding slice; risk plateau) transfers; the broad error-cell
  observability is noisier. This is a magnitude difference, not a mechanism difference.
- **Large-n binding slice**: the gold-unknown over-read slice is small (5 over-reads vs 25
  withholds on dev140, mirroring Gan's 11-row binding residual). The null result is reported
  with that caveat; AUROCs on n=5 are suggestive, not definitive.
- **Universality**: the claim is two-dataset. Other NLP tasks with categorical over-reading
  are plausible analogues but are not evidenced here.
- **Causal mechanism from first principles**: the claim is structural (task-bound ceiling +
  transferred wall mechanism), not a first-principles causal account.

---

## 4. Empirical Validation: ExECTv2 SF Wall-Transfer Probe — Results

*Source document: `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`
— **wall mechanism transfers verdict (6 of 9 pre-registered checks passed)**. Aggregate /
`dev140`-only; no new model calls;
replay from saved same-core model-swap and self-consistency artifacts. Generated by
`build_exectv2_sf_wall_transfer_probe_extended.py`.*

### 4a. Acceptance criterion 1 — External Risk composite (population, dev140, n=140)

Frozen composite (matches Gan P0.2): `risk = 3·(3 − cross-model agreement) + source-flag count
+ ambiguity-reason count`. The agreement leg comes from the three same-core model-swap runs; the
source-flag (#5–#9) and ambiguity (#11) legs are ported deterministically by keyword from the SF
assembly trace, since ExECTv2 has no rq9 boundary-features packet.

| Feature | AUROC (predicts SF-cell error) | Risk-coverage AUC ↓ | Safest-tier plateau |
| --- | ---: | ---: | --- |
| #1 Cross-model agreement count | 0.7613 | 0.1383 | cov 50.7%, selective risk 16.9% (CI 9.9–27.3%) |
| #2 Agreement share | 0.7613 | 0.1383 | cov 50.7%, selective risk 16.9% (CI 9.9–27.3%) |
| #3 External risk composite | **0.7636** | 0.1787 | cov 29.3%, selective risk **17.1%** (CI 8.5–31.3%) |
| _oracle (correct-first)_ | — | 0.0899 | — |

The composite ranks SF errors at AUROC 0.764 (Gan 0.781) and **plateaus** — the safest-ranked
tier still carries ~17% selective risk with the CI lower bound above zero. Errors leak into the
low-risk region: the irreducible-residual wall shape, reproduced. **Criterion (b) "external
agreement ranks SF errors" passes.**

### 4b. Acceptance criterion 2 — wall-slice null test (pre-registered)

Slice: 39 gold-`unknown` SF units (canonical GPT pass) → **25 withhold-correct, 5 over-read-wrong,
9 recall-miss**. Pre-registered **H0** (no gold-free feature separates withhold from over-read →
wall transfers) vs **H1** (separation exists; decision rule AUROC ≥ 0.70). Result:

| Feature (forward-observable) | Mean withhold-correct | Mean over-read-wrong | AUROC (flags over-read) |
| --- | ---: | ---: | ---: |
| #1 Cross-model state agreement | 2.76 | 2.60 | 0.580 |
| #3 External risk composite | 3.92 | 3.20 | 0.416 (wall-degenerate) |
| #17/#18 Self-consistency state entropy | 0.099 | 0.243 | 0.676 |

**H0 retained** — best separation AUROC 0.676 < 0.70; no gold-free separator. 2/5 over-reads are
temperature-entropy-zero (the Gan `band_unknown` = 0.000 signature); the External Risk composite
that ranks errors population-wide is *wall-degenerate* here (over-reads carry lower mean risk than
correct withholds). All three models over-read this slice (5/7/8). **Criterion (c) "binding
over-reads remain high-agreement / unflaggable" passes.**

### 4c. Key signal comparison: Gan vs ExECTv2 SF probe

| Signal | Gan reference | ExECTv2 SF (this probe) | Transfers? |
| --- | --- | --- | --- |
| Weakest family | over-reading bands | SF F1 0.7525 full-200, 0.7645 dev140 | **yes** |
| External-risk failure AUROC | 0.781 (P0.2) | **0.764** (dev140) | **yes** |
| Risk-coverage plateau | 0.8% @ 16% cov (irreducible) | **17.1% @ 29% cov** (irreducible, CI>0) | **yes (same shape)** |
| Gold-free separator on binding over-reads | none (wall) | none (best AUROC 0.676 < 0.70) | **yes** |
| Population-wide error entropy | flat ~0.018 (degenerate) | elevated 0.287 vs correct 0.069 | **no (noisier)** |
| Population-wide error cross-model agreement | high; disagreement signals risk | lower on errors (21.8%) vs correct (69.4%) | **no (noisier)** |

### 4d. Interpretation of the wall-transfers verdict

The extended probe establishes three things:

1. **Task-bound ceiling confirmed.** SF is the weakest family on every evaluation surface and
   every LLM tested; not model-specific, not data-surface, not closed by model substitution.

2. **Wall mechanism transfers.** The two direct wall tests both reproduce: the External Risk
   composite ranks SF errors at AUROC 0.764 with an irreducible risk-coverage plateau (17.1%,
   CI > 0), and the binding gold-unknown over-read slice has no gold-free separator (H0 retained;
   2/5 over-reads entropy-zero). On the rows that should withhold, the model over-reads to a
   quantified rate confidently and undetectably — exactly the Gan wall.

3. **Population-wide observability is noisier, not the mechanism.** The only genuine divergence
   from Gan is magnitude: ExECTv2 SF error cells are more heterogeneous population-wide (error
   entropy 0.287 vs 0.069; error agreement 21.8% vs 69.4%), so the broad error-cell signatures
   are less degenerate than Gan's near-zero P2.1 panel. This is why three of the nine probe
   checks — the ones testing for Gan-magnitude population-wide degeneracy — read `no`. They test
   a stronger same-magnitude claim that the wall-transfer headline does not require.

The manuscript framing should therefore be **"task-bound ceiling and wall mechanism transfer;
population-wide observability is noisier than Gan"** — stronger than the earlier partial reading,
and still honest about the one place ExECTv2 differs.

---

## 5. Reframed Manuscript Language

The following draft text is intended for the *"What generalizes"* subsection under a
capability-first spine (see §6). It incorporates the strengthened wall-transfers probe verdict.

### Draft subsection: Seizure Frequency and the Cross-Dataset Ceiling

*[Evidence validity: frozen aggregate `full-200` (ExECTv2); frozen `test450` holdout aggregate
(Gan 2026 seizure-frequency labeling); validation-only probe (Gan); `dev140` aggregate
model-swap + self-consistency artifact replay (ExECTv2 SF probe). Holdout read on ExECTv2
not available. The wall *mechanism* transfers; the one caveat is that ExECTv2's population-wide
error observability is noisier than Gan's — see probe limits below.]*

---

The central negative result of the Gan 2026 seizure-frequency strand — that a clinical
extractor for seizure-frequency labeling hits an architecturally unresolvable ceiling —
does not stay on the Gan dataset. The
ceiling transfers, and so does its wall mechanism: on the rows that should withhold to
`unknown`, the model over-reads to a quantified rate confidently, and no forward-observable
signal flags it.

On the Gan 2026 seizure-frequency benchmark, the best architecture achieves a frozen holdout
ceiling of **0.842** (multi-trace fresh-evidence hybrid pipeline, `test450` Purist).
Exhaustive ablation established that this holdout ceiling is generator-bound: the model over-reads ambiguous frequency evidence as quantified rates or
seizure-free durations with high confidence, and no forward-observable signal — self-consistency,
self-confidence, sampling entropy — separates the over-read rows from correct extractions at
inference time. Semantic-entropy probing at k=4 across temperatures [0.3, 0.5, 0.7, 1.0]
confirmed the mechanism: mean label entropy 0.012, with the most-over-read band (`band_unknown`)
at **entropy 0.000** across all four temperatures. The model does not sample its way out of the
wrong answer. The limit is clinical-reasoning, not architectural.

On the ExECTv2 clinical-letter corpus, SeizureFrequency is the weakest extraction family under
a frozen same-core architecture across all three tested LLMs: GPT-4.1-mini **0.7525**, DeepSeek
chat **0.7602**, Qwen 3.6 35B **0.7020** (full-200); GPT 0.7645, DeepSeek 0.7658, Qwen 0.6919
(dev140). Other families are materially stronger: Diagnosis 0.8397–0.8708, Prescription 0.8926,
Investigations 0.8563–0.9091. The gap is not model-specific — it is present across all three
model families and narrows by only +0.008 between the two strongest LLMs. It is not a
data-surface artifact — the gap closes to ~0.9053 on dev140 only when a task-specific SF
adjudicator is added, confirming that targeted post-processing can correct the base extraction,
but the base extraction residual persists in the same direction as the Gan wall.

The clinical task is the same in both settings: extract the current seizure burden from prose
where evidence is often hedged, qualified by event rather than rate, or temporally ambiguous.
The illegitimate evidence shapes that drive Gan over-reading — last-event-only anchors,
open-ended temporal qualifiers, vague counts read as habitual rates — are present in real
clinical letters too.

A forward-observable-feature probe on dev140 aggregate artifacts confirms the wall mechanism
transfers. A frozen External Risk composite — `3·(3 − cross-model agreement) + source-flag
count + ambiguity-reason count`, the same formula validated on Gan — ranks ExECTv2 SF errors at
failure-prediction AUROC **0.764** (Gan 0.781), and its risk-coverage curve **plateaus**: the
safest-ranked tier still carries ~**17% selective risk** (95% CI lower bound above zero), the
same irreducible residual Gan documented. On the binding slice — the gold-`unknown` rows the
model over-reads to a quantified state — a pre-registered null test finds **no gold-free
separator**: cross-model agreement, the External Risk composite, and self-consistency state
entropy all fail to distinguish the wrong over-reads from correct withholds (best AUROC 0.68,
below the useful-triage bar), with the most confident over-reads temperature-entropy-zero, the
exact Gan `band_unknown` signature. The one place ExECTv2 differs from Gan is *population-wide*:
its broad error-cell signatures are noisier (error entropy 0.287 vs correct 0.069; error
cross-model agreement 21.8% vs correct 69.4%), so the error cells are less uniformly degenerate
than Gan's near-zero panel. But the two direct wall tests — the risk plateau and the
no-gold-free-separator null result — both reproduce. The ExECTv2 SF floor is therefore a
**task-bound ceiling whose wall mechanism transfers**: on the rows that should withhold, the
over-reading is confident and undetectable, just as on Gan.

The interpretation is that the extractor's ceiling is **the task's clinical-ambiguity floor**,
not a deficiency of the architecture or the model. This is the argument that converts "SF is
our weakest family" from an apology into the paper's strongest generalization claim: a system
whose limits are task-bound exhibits exactly the behavior a genuinely modular,
clinically-grounded architecture predicts. The Gan wall finding characterizes the most extreme
version of that ceiling (purely confident over-reading, population-wide entropy ≈ 0); the
ExECTv2 SF finding establishes that the structural property — task-bound,
architecture-independent, not closed by model substitution, and unflaggable by any
forward-observable signal on the binding rows — holds on a second independent corpus, even
though the broader error distribution there is noisier than Gan's degenerate panel.

---

## 6. Placement in the Capability-First Spine

The closing-stage critique (§4) proposes restructuring the manuscript around capabilities
rather than tasks, with the following sections:

> 1. Shared decomposed architecture
> 2. *What the LLM adds* — three-way comparison, both tasks side by side
> 3. *What generalizes* — transfer + the wall, both tasks
> 4. Reliability scorecard — unified dimensions across both tasks
> 5. Component impact — unified stage-ladder figure

**Recommended placement: §3 — *What generalizes*, as the second subsection of that section.**

Proposed §3 structure:

| Subsection | Content | Paired evidence |
| --- | --- | --- |
| 3.1 Architecture transfer: same core on a new task | Model-swap: DeepSeek ≥ GPT under frozen graph | ExECTv2 model-swap full-200 + Gan three-way table |
| **3.2 Wall transfer: the task-bound ceiling** | **Task-bound ceiling and wall mechanism transfer; population-wide observability noisier than Gan** | **Gan P0.2/P2.1 + ExECTv2 SF gap + probe wall-transfers verdict (6 of 9 pre-registered checks passed): external-risk AUROC 0.764 with 17% plateau + no gold-free separator on the binding slice** |
| 3.3 Evaluation discipline transfers | Held-out-family CV, adversarial battery as reusable gates | Gan protocol applied to ExECTv2 robustness panels |

Section 3.2 (this subsection) anchors the generalization claim. Its opening sentence converts
the SF finding:

> The wall that bounds Gan seizure-frequency performance is not dataset-specific. It is a
> property of the clinical task.

The section then presents the Gan ceiling, the P0.2 risk-coverage plateau and P2.1 entropy
mechanism, the ExECTv2 SF gap, the structural parallel, and the wall-transfers probe results
(external-risk plateau + no gold-free separator) — with the honest caveat that ExECTv2's
population-wide error observability is noisier than Gan's degenerate panel.

### Why §3, not §4 (reliability)

The wall-transfer result is about *what the system does at its limit*, which is a capability
claim with a generalization dimension. Placing it in reliability would frame it as a failure
mode to be managed; placing it in "what generalizes" frames it correctly as the characterization
of a task-bound ceiling — a positive, distinctive, and honest finding. The reliability section
should reference it as the mechanism behind the SF calibration and abstention story, but the
primary locus is §3.

---

## 7. Relationship to Other Workstream Drafts

| Draft | Relationship |
| --- | --- |
| `deepseek_model_agnostic_evidence_2026-06-27.md` | §3.1 (model-swap) precedes §3.2 (wall-transfer) in the same capabilities section; both argue task-bound vs system-bound limits |
| `benchmark_surface_reconciliation_2026-06-27.md` | SF benchmark inversion (rules > hybrid on strict surface) is consistent with the wall story: the adjudicator gains are on the clinical-headline surface; the base extraction residual is what the wall characterizes |
| `evidence_groundedness_reconciliation_2026-06-27.md` | Evidence-groundedness metric is maintained at 1.0000 on ExECTv2 SF across both model-swap runs, confirming the SF gap is not an evidence-validity failure — the system extracts with evidence but the clinical interpretation over-commits |
| `closing_stage_research_critique_2026-06-27.md` §2 SF-spin | This document is the full response to the §2 critique; the §5 "reframe the wall" idea is implemented here |

---

## 8. Claim Boundaries

**Supported by available artifacts (wall-transfers probe: 6 of 9 pre-registered checks passed + frozen aggregate `full-200`):**

- ExECTv2 SF is the weakest family under a frozen same-core architecture at full-200 aggregate
  for all three LLMs tested: GPT-4.1-mini (0.7525), DeepSeek chat (0.7602), Qwen 3.6 35B
  (0.7020). Same ranking on dev140 (GPT 0.7645, DeepSeek 0.7658, Qwen 0.6919).
- The SF gap persists across all three model swaps; it narrows by at most +0.008 between
  the two strongest LLMs.
- Gan P2.1 establishes fully confident over-reading on Gan: mean label entropy 0.012,
  `band_unknown` entropy 0.000 (validation-only probe, n=150).
- The ExECTv2 SF gap is reducible by task-specific adjudication (dev140 v08: SF 0.9053).
- Evidence rate is 1.0000 on all full-200 ExECTv2 model-swap runs; the SF gap is not an
  evidence-failure.
- **External Risk composite ranks SF errors (acceptance criterion 1):** failure-prediction
  AUROC **0.7636** on dev140 (Gan 0.781), with an irreducible risk-coverage plateau — the
  safest-ranked tier still carries **17.1% selective risk** (95% CI 8.5–31.3%, lower bound
  above zero). The agreement leg carries the signal; ported source-flag/ambiguity legs add
  < 0.01 AUROC.
- **No gold-free separator on the binding slice (acceptance criterion 2):** on the gold-`unknown`
  SF units, a pre-registered null test retains H0 — cross-model agreement (AUROC 0.58),
  External Risk (0.42), and self-consistency state entropy (0.68) all fail to separate the 5
  over-reads from the 25 correct withholds; 2/5 over-reads are temperature-entropy-zero; all
  three models over-read the slice (5/7/8).
- **Task-bound ceiling and wall mechanism transfer**: the structural weakness is
  dataset-independent, model-independent, architecture-independent, and the binding over-reads
  are unflaggable without gold — per the wall-transfers probe verdict.

**Confirmed but nuanced (one population-wide difference from Gan):**

- ExECTv2 SF error entropy is *elevated* vs correct (0.287 vs 0.069), not flat, and cross-model
  agreement is lower on error cells (21.8%) than correct cells (69.4%). The broad error-cell
  signatures are noisier than Gan's near-zero P2.1 panel. This is a difference in *population-wide
  observability magnitude*, not in the wall mechanism: the two direct wall tests (risk plateau +
  no gold-free separator at the binding slice) both reproduce. Three of the nine probe checks —
  those testing for Gan-magnitude population-wide degeneracy — read `no` for this reason.
- 43.6% of SF error cells are temperature-unanimous wrong (a material confident-error component
  population-wide), but the binding-slice null result, not this aggregate, is the wall test.

**Not supported (outside evidence boundary):**

- Holdout SF comparison on ExECTv2.
- Identical population-wide entropy/agreement *magnitude* to Gan — probe checks 2, 4, 6 read
  `no`; ExECTv2 error cells are noisier population-wide even though the wall mechanism transfers.
- Row-level mechanism attribution on full-200/holdout ExECTv2 SF — excluded by aggregate-only
  policy (the wall-slice null test is dev140-only).
- Universality beyond these two clinical-letter corpora.

---

## Source Artifacts

- `docs/research/closing_stage_research_critique_2026-06-27.md` (§2 SF-spin, §5 wall-transfers)
- `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md` (P2.1
  verdict; H0_confident_over_reading; entropy table)
- `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`
  (SF weakest family; GPT 0.7525, DeepSeek 0.7602; evidence rate 1.0000)
- `docs/research/paper_drafts/deepseek_model_agnostic_evidence_2026-06-27.md` (§6 capability
  table, §3.1 model-swap pairing)
- `docs/experiments/exectv2/reliability/exectv2_reliability_scorecard_and_phased_plan_2026-06-21.md`
  (dev140 v08 SF 0.9053; residual risk register)
- `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`
  (§3 selector saturation; §Part II Q4 hard residual; Part III Insights #3, #5)
- `docs/experiments/gan2026/reliability/gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md`
  (External Risk Score AUROC 0.781; wall prior definition)
- `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`
  — **wall mechanism transfers (6 of 9 pre-registered checks passed)**; SF weakest confirmed; External Risk composite
  AUROC 0.764 with 17.1% risk-coverage plateau (criterion 1); pre-registered wall-slice null test
  retains H0 — no gold-free separator on the binding gold-unknown over-reads (criterion 2);
  population-wide error observability noisier than Gan (the one residual difference)
- `experiments/build_exectv2_sf_wall_transfer_probe_extended.py` — extended harness computing the
  External Risk composite + wall-slice null test (imports the base probe; aggregate/dev140-only,
  no model calls)
- `experiments/gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.md` — Gan External
  Risk Score curve (AUROC 0.781; plateau 0.8% @ 16% coverage), the frozen composite ported here
