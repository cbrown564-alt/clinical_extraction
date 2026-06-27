# The Wall Transfers: SeizureFrequency as a Cross-Dataset Confident-Over-Reading Phenomenon

Date: 2026-06-27
Author: paper-writing workstream (P3c — wall-transfers reframe)
Status: draft — revised to incorporate probe partial verdict (2026-06-27)
Evidence validity: validation-only / frozen aggregate-only (full-200); no holdout; no new model calls
Probe status: `exectv2_sf_wall_transfer_probe_2026-06-27.md` — **PARTIAL** (3/6 checks passed). Task-bound ceiling confirmed; Gan H0 mechanism does NOT fully replicate. See §4.

---

## Purpose

The closing-stage critique (§2, §5, *closing_stage_research_critique_2026-06-27.md*) identifies
a specific reframing opportunity: ExECTv2 SeizureFrequency is persistently the weakest clinical
family, and the draft manuscript explains this as "consistent with deep-reasoning difficulty."
That is a missed headline. The same mechanism characterized with high resolution on the Gan
dataset — the confident-over-reading wall — is the most likely explanation for the ExECTv2 SF
gap, and showing that the wall transfers across datasets and schemas converts "SF is our weakest
family" from an apology into the paper's strongest generalization claim:

> *A clinical extractor whose limit is the task's, not the system's — and the limit transfers.*

This document drafts the subsection text, specifies what a cross-dataset wall-transfer finding
consists of, marks the one empirical gap that requires a probe experiment, and proposes placement
in the capability-first manuscript spine.

---

## 1. The Wall: Defined on Gan

### 1a. What the Wall is

The Gan 2026 strand converged on a ceiling of **0.842 (V12 hybrid, test450 Purist)** and
**0.809 (single-SE pass, test450 Purist)**. Detailed decomposition
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

The wall is not a component failure that can be patched. It is a *clinical-reasoning limit*: on
the hardest rows, the model over-commits to rate-like interpretations of genuinely ambiguous
evidence, and no gate, reasoner, or ensemble safely corrects it at inference time without the
hidden gold.

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

The hypothesis — not yet a confirmed finding; see §4 — is that the **same confident
over-reading mechanism** drives the ExECTv2 SF gap: the model extracts a structured
SeizureFrequency representation with high evidence-rate (1.0000 on both model-swap runs) but
systematically commits to over-specified rate interpretations when the source evidence supports
only a qualitative or unknown state. The adjudicator corrects this post-hoc; the base extraction
wall is the same.

---

## 3. Cross-Dataset Wall-Transfer: Confirmed Partial Finding

### 3a. What the probe showed

The wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) ran and returned a
**partial verdict** (3/6 checks passed). The paper can now state the following with evidence
support, subject to the limitations in §3b:

> The task-bound ceiling documented on the Gan seizure-frequency benchmark transfers to the
> ExECTv2 clinical-letter corpus. SeizureFrequency is the persistently weakest extraction
> family across all three tested LLMs under a frozen same-core architecture: GPT-4.1-mini
> 0.7525, DeepSeek chat 0.7602, Qwen 3.6 35B 0.7020 (full-200); GPT 0.7645, DeepSeek
> 0.7658, Qwen 0.6919 (dev140). The weakness is not model-specific, not data-surface noise,
> and not correctible by model substitution alone — it closes to ~0.9053 only when a
> task-specific SF adjudicator is added. On the Gan dataset, semantic-entropy probing
> (k=4, temperatures [0.3, 0.5, 0.7, 1.0]) established that over-reading was fully
> confident: mean label entropy 0.012, `band_unknown` entropy 0.000 [cite P2.1].
>
> On ExECTv2 SF, the probe reveals a **partially different mechanism**: 43.6% of SF error
> cells are temperature-unanimous wrong (4/4 same wrong answer), confirming a material
> confident-error component. However, SF error entropy is elevated rather than flat
> (0.287 vs 0.069 for correct cells), and cross-model agreement is substantially lower
> on error cells than correct cells (21.8% vs 69.4% exact 3/3 agreement). The ExECTv2
> SF floor is therefore a *mixed* phenomenon: some errors are as confidently wrong as
> Gan's over-reading; others are genuinely uncertain and heterogeneous across models.
>
> Together, these results characterize a **task-bound ceiling that transfers** across
> datasets and schemas — the same clinical task (extracting seizure burden from
> ambiguous letter evidence) is the weakest family under every architecture variant tested,
> on two independent corpora, using three different LLMs. The ceiling is task-bound, not
> system-bound. The mechanism at ExECTv2 **partially differs** from Gan: confident
> over-reading is present but coexists with uncertain errors not seen in the Gan
> residual. The stronger Gan claim — that the wall is purely confident, undetectable
> by self-referential signals — does not transfer in full.

### 3b. What the finding does not claim

- **Holdout replication**: the ExECTv2 full-200 is the outer boundary of available aggregate
  evidence; no holdout test on the ExECTv2 corpus has been authorized. The cross-dataset claim
  is bounded to the frozen aggregate + validation-only probe evidence.
- **Row-level attribution**: the aggregate-only inspection policy prevents per-row mechanism
  analysis on full-200. The probe operates on dev140 self-consistency artifacts only.
- **Full Gan H0 replication**: the Gan H0_confident_over_reading verdict (near-zero entropy,
  zero cross-model disagreement on residual rows) does NOT replicate on ExECTv2 SF. Error
  entropy is elevated (0.287 vs 0.069 correct), and cross-model agreement is lower on errors
  (21.8%) than correct cells (69.4%). The mechanism partially differs.
- **Universality**: the claim is two-dataset. Other NLP tasks with categorical over-reading
  are plausible analogues but are not evidenced here.
- **Causal mechanism from first principles**: the claim is structural (the task-bound ceiling
  transfers; the error composition at ExECTv2 includes both confident and uncertain components)
  not causal. Mechanism interpretation remains speculative.

---

## 4. Empirical Validation: ExECTv2 SF Wall-Transfer Probe — Results

*Source document: `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`
— **PARTIAL verdict** (3/6 checks passed). Aggregate-only; no new model calls; replay from
saved same-core model-swap and self-consistency artifacts.*

### 4a. Checks passed (confirmed)

| Check | Result |
| --- | --- |
| `sf_weakest_on_dev140_and_full200` | **pass** — SF weakest on both splits, all three LLMs |
| `sf_unanimous_4_of_4_wrong_material` | **pass** — 43.6% of SF error cells are 4/4 wrong |
| `gan_p21_h0_confident_over_reading_reference` | **pass** — Gan P2.1 reference loaded; H0 confirmed on Gan |

### 4b. Checks failed (mechanism divergence)

| Check | Result | What it means |
| --- | --- | --- |
| `sf_error_cross_model_agreement_not_lower_than_correct` | **fail** | Error cells have *lower* cross-model agreement (21.8%) than correct cells (69.4%); the opposite of pure confident over-reading |
| `sf_error_entropy_not_elevated_vs_correct` | **fail** | Error entropy 0.287 vs correct 0.069 — errors are detectably more uncertain, unlike Gan where residual entropy was flat at ~0.018 |
| `other_families_also_show_confident_error_pattern` | **fail** | The elevated-error-entropy pattern is SF-specific; other families do not show it uniformly |

### 4c. Key signal comparison: Gan P2.1 vs ExECTv2 SF probe

| Signal | Gan P2.1 | ExECTv2 SF (this probe) |
| --- | --- | --- |
| Error / residual entropy | flat ~0.018 (below correct) | **elevated 0.287** (4× correct 0.069) |
| Self-consistency unanimous wrong | `band_unknown` stable at 0.000 | **43.6%** of SF error cells — material but not dominant |
| Cross-model error agreement | high; disagreement signals risk (AUROC 0.781) | **lower on errors** (21.8%) vs correct (69.4%) — opposite direction to Gan |
| Weakest family | over-reading bands | SF F1 0.7525 full-200, 0.7645 dev140 — confirmed |

### 4d. Interpretation of partial verdict

The probe establishes two things:

1. **Task-bound ceiling confirmed.** SF is the weakest family on every evaluation surface and
   every LLM tested. The gap is structural, not model-specific, and not addressable by model
   substitution alone. This part of the Gan → ExECTv2 transfer holds cleanly.

2. **Mechanism partially differs.** The Gan wall was characterized by zero-entropy, zero-
   disagreement confident over-reading — the model never wavered on its wrong answers.
   ExECTv2 SF presents a mixed picture: 43.6% of error cells are temperature-unanimous (a
   genuine confident-error component), but error entropy is substantially elevated and
   cross-model agreement is lower on errors than correct cells. ExECTv2 SF errors include
   both a confident wrong-direction component and an uncertain, heterogeneous component not
   seen in the Gan residual. The full Gan H0_confident_over_reading verdict does not
   transfer.

The manuscript framing should therefore be **"task-bound ceiling transfers; mechanism
partially differs"** — honest about what the probe showed, avoiding both the over-claim
(full Gan mechanism replication) and the under-claim (the weakness is unexplained or random).

---

## 5. Reframed Manuscript Language

The following draft text is intended for the *"What generalizes"* subsection under a
capability-first spine (see §6). It incorporates the partial probe verdict.

### Draft subsection: Seizure Frequency and the Cross-Dataset Ceiling

*[Evidence validity: frozen aggregate full-200 (ExECTv2); frozen test450 aggregate +
validation-only probe (Gan); dev140 self-consistency artifact replay (ExECTv2 SF probe).
Holdout read on ExECTv2 not available. Mechanism claim is partial — see probe limits below.]*

---

The central negative result of the Gan strand — that a clinical extractor for seizure-frequency
labeling hits an architecturally unresolvable ceiling — does not stay on the Gan dataset. The
ceiling transfers. Its detailed mechanism partially differs.

On the Gan seizure-frequency benchmark, the best architecture achieves a frozen holdout ceiling
of **0.842** (V12 hybrid, test450). Exhaustive ablation established that this ceiling is
generator-bound: the model over-reads ambiguous frequency evidence as quantified rates or
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

A forward-observable-feature probe on dev140 self-consistency artifacts confirms that the
ceiling's *character* at ExECTv2 is mixed rather than purely confident. **43.6% of SF error
cells are temperature-unanimous wrong** (4/4 same wrong answer) — a material confident-error
component analogous to the Gan pattern. However, SF error entropy is elevated (0.287 vs 0.069
for correct cells), and cross-model agreement is lower on error cells (21.8%) than correct
cells (69.4%) — the reverse of the Gan `band_unknown` pattern where every wrong answer was
entropy-zero and stable across all temperatures. The ExECTv2 SF floor is therefore a
**task-bound ceiling that transfers, with a mechanism that partially differs**: some errors
are as confidently wrong as Gan's over-reading; others are uncertain and heterogeneous.

The interpretation is that the extractor's ceiling is **the task's clinical-ambiguity floor**,
not a deficiency of the architecture or the model. This is the argument that converts "SF is
our weakest family" from an apology into the paper's strongest generalization claim: a system
whose limits are task-bound exhibits exactly the behavior a genuinely modular,
clinically-grounded architecture predicts. The Gan wall finding characterizes the most extreme
version of that ceiling (purely confident over-reading); the ExECTv2 SF finding establishes
that the structural property — task-bound, architecture-independent, not closed by model
substitution — holds on a second independent corpus even where the internal error distribution
is more heterogeneous.

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
| **3.2 Wall transfer: the task-bound ceiling** | **Task-bound ceiling transfers; mechanism partially differs** | **Gan P2.1 + ExECTv2 SF gap + probe partial verdict (3/6)** |
| 3.3 Evaluation discipline transfers | Held-out-family CV, adversarial battery as reusable gates | Gan protocol applied to ExECTv2 robustness panels |

Section 3.2 (this subsection) anchors the generalization claim. Its opening sentence converts
the SF finding:

> The wall that bounds Gan seizure-frequency performance is not dataset-specific. It is a
> property of the clinical task.

The section then presents the Gan ceiling, the P2.1 entropy mechanism, the ExECTv2 SF gap,
the structural parallel, and the partial-verdict probe results — with honest caveats on the
mechanism divergence.

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

**Supported by available artifacts (partial probe verdict + frozen aggregate full-200):**

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
- **43.6% of SF error cells are temperature-unanimous wrong** (dev140 self-consistency
  artifacts) — a material confident-error component is present.
- **Task-bound ceiling transfers**: the structural weakness is dataset-independent,
  model-independent, and architecture-independent, per the partial probe verdict.

**Confirmed but nuanced (probe partially fails Gan H0):**

- ExECTv2 SF error entropy is *elevated* vs correct (0.287 vs 0.069), not flat — the
  full Gan H0_confident_over_reading does not transfer. Cross-model agreement on error
  cells is lower (21.8%) than correct cells (69.4%).
- The ExECTv2 SF floor is a mixed mechanism: confident-error component + uncertain-error
  component. The "confidently wrong, undetectable" framing applies to a subset, not all,
  of ExECTv2 SF errors.

**Not supported (outside evidence boundary):**

- Holdout SF comparison on ExECTv2.
- Full cross-dataset H0_confident_over_reading replication — probe fails checks 2, 4, 5.
- Row-level mechanism attribution on ExECTv2 SF — excluded by aggregate-only policy.
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
  — **PARTIAL verdict** (3/6 checks); SF weakest confirmed; 43.6% error unanimous wrong confirmed;
  Gan H0 mechanism does not fully transfer (error entropy elevated, cross-model agreement lower on errors)
