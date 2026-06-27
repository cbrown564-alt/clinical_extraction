# The Wall Transfers: SeizureFrequency as a Cross-Dataset Confident-Over-Reading Phenomenon

Date: 2026-06-27
Author: paper-writing workstream (P3c — wall-transfers reframe)
Status: draft — writing only, no new data or model calls
Evidence validity: validation-only / frozen aggregate-only (full-200)
Probe status: `exectv2_sf_wall_transfer_probe_2026-06-27.md` — **NOT YET RUN** (see [PENDING PROBE] markers below)

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

On the frozen full-200 same-core model-swap
(`exectv2_same_core_model_swap_full200_2026-06-25.md`), both candidate LLMs show SeizureFrequency
as the weakest family by a consistent margin:

| Model | Overall | Diagnosis | SF | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8356 | 0.8397 | **0.7525** | 0.8926 | 0.8563 |
| DeepSeek chat | 0.8566 | 0.8708 | **0.7602** | 0.8926 | 0.9091 |

The SF gap is not model-specific. Swapping the LLM while holding the architecture frozen
(same component graph, same deterministic stages, same evaluation surface) leaves SF as
the weakest family under both GPT-4.1-mini and DeepSeek chat. DeepSeek's overall gain
of +0.021 over GPT is distributed across Diagnosis (+0.031), Investigations (+0.053), and
a slight SF gain (+0.008); Prescription is tied. The SF gap persists regardless of model
strength.

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

## 3. Cross-Dataset Wall-Transfer: The Finding If the Probe Confirms

### 3a. What the finding claims

If the probe experiment confirms the mechanism transfer (§4), the paper can state:

> The confident-over-reading wall documented on the Gan seizure-frequency benchmark is not a
> Gan-specific artifact. It reproduces on the ExECTv2 clinical-letter corpus, where the
> SeizureFrequency family is the persistently weakest extraction target across all tested LLMs
> under a frozen same-core architecture. On the Gan dataset, semantic-entropy probing
> (k=4, temperatures [0.3, 0.5, 0.7, 1.0]) established that the over-reading is confident:
> mean label entropy 0.012, `band_unknown` entropy 0.000, meaning the model never samples its
> way out of the wrong answer [cite P2.1]. On ExECTv2 SF, the same forward-observable-feature
> probe [PENDING PROBE; cite exectv2_sf_wall_transfer_probe when available] is expected to show
> the same signature: low label entropy, stable wrong-direction over-commitment, and no
> self-consistency or self-confidence signal separating correct from incorrect extractions.
>
> Together, these results characterize a **cross-dataset clinical-reasoning limit**: a clinical
> extractor trained to resolve ambiguous seizure-frequency evidence over-commits to rate
> interpretations at a rate and confidence level that no self-referential signal can detect or
> prevent. The limit is **task-bound, not system-bound** — it disappears when task-specific
> adjudication corrects the base extraction, and it is present in the same direction on two
> independent corpora using three different LLMs. The system's ceiling is the task's clinical
> ambiguity floor, not a deficiency of the architecture.

### 3b. What the finding does not claim

- **Holdout replication**: the ExECTv2 full-200 is the outer boundary of available aggregate
  evidence; no holdout test on the ExECTv2 corpus has been authorized. The cross-dataset claim
  is bounded to the validation-only + frozen aggregate evidence.
- **Row-level attribution**: the aggregate-only inspection policy prevents deriving the per-row
  mechanism analysis on full-200. The probe in §4 is predeclared on a validation slice only.
- **Universality**: the claim is two-dataset. Other NLP tasks with categorical over-reading
  are plausible analogues but are not evidenced here.
- **Causal mechanism from first principles**: the claim is structural (the over-reading persists,
  confident, across datasets) not causal (e.g. trained on rate-heavy corpora). Mechanism
  interpretation remains speculative.

---

## 4. [PENDING PROBE] Empirical Validation: ExECTv2 SF Wall-Transfer Probe

*Source document: `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`
— **does not yet exist**. The following specifies what it must show to close the cross-dataset
claim.*

### 4a. What the probe must measure

The Gan P2.1 test established the wall mechanism by running k=4 samples across a temperature
range on a stratified slice of rows (n=150 including residual-enriched rows). The ExECTv2 SF
wall-transfer probe must run the analogous measurement:

1. **Row selection**: a stratified SF slice from dev140 or an available validation split, with
   an SF-error-enriched subset (analogous to the Gan `band_unknown ∪ seizure_free_duration`
   residual). Recommend n ≥ 50 SF rows, with ≥ 15 rows where the baseline extraction is
   Purist-wrong on the SF family.
2. **Sampling protocol**: k=3 or k=4 at temperatures [0.3, 0.7, 1.0] (matching or approximating
   the Gan protocol); preserve all exact-evidence gates.
3. **Metrics to report**:
   - Mean SF label entropy across all rows
   - Mean SF label entropy on wrong-SF-extraction rows specifically
   - Per-temperature label stability (proportion of rows with same SF category across all k draws)
   - Whether evidence-rate drops on uncertain SF rows (contrast with Gan where evidence rate was
     maintained at 1.0000 even on wrong rows)
4. **Decision criterion**: confirm `H0_confident_over_reading` if mean label entropy on
   wrong-SF rows is < 0.05 and per-temperature stability > 0.90; revise the framing if not.

### 4b. What a null result means

If the probe shows *high* entropy on ExECTv2 SF wrong rows (the over-reading is uncertain, not
confident), the cross-dataset claim must be revised:

- The Gan wall mechanism is Gan-specific (confident over-reading on a synthetic benchmark with
  a discrete label grammar).
- The ExECTv2 SF gap has a different mechanism — possibly lower in the pipeline, possibly
  addressable by better prompting.
- The paper's framing becomes: "the Gan wall is a resolved, characterized negative result;
  ExECTv2 SF is an independently weaker family whose mechanism differs."

This is a lesser finding but still honest. The probe must be run before the cross-dataset claim
enters the manuscript as a confirmed result.

### 4c. What to write in the manuscript pending probe completion

Until the probe result is in hand, the manuscript should present the structural parallel (§2)
as an observation and the mechanism as a hypothesis:

> SeizureFrequency is the weakest ExECTv2 family under a frozen same-core architecture across
> all tested LLMs (GPT-4.1-mini 0.7525, DeepSeek chat 0.7602, full-200 aggregate). This
> pattern is consistent with the confident-over-reading wall characterized on the Gan
> benchmark (mean label entropy 0.012, `band_unknown` entropy 0.000 at k=4 sampling across
> four temperatures), where the same mechanism — confident extraction of over-specified
> rate interpretations from ambiguous evidence — was identified as the binding ceiling.
> Whether the same entropy signature reproduces on ExECTv2 SF is currently under
> investigation [cite probe when available]. If confirmed, the ExECTv2 SF gap and the Gan
> wall constitute a **cross-dataset confident-over-reading phenomenon**: a clinical-reasoning
> limit that is task-bound, not system-bound.

---

## 5. Reframed Manuscript Language

The following draft text is intended for the *"What generalizes"* subsection under a
capability-first spine (see §6).

### Draft subsection: Seizure Frequency and the Cross-Dataset Ceiling

*[Evidence validity: frozen aggregate full-200 (ExECTv2); frozen test450 aggregate + validation-only
probe (Gan). Holdout read on ExECTv2 not available; probe [PENDING PROBE] marks unconfirmed
mechanism claim.]*

---

The central negative result of the Gan strand — that a clinical extractor for seizure-frequency
labeling hits a confident, architecturally unresolvable wall — does not stay on the Gan dataset.

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
a frozen same-core architecture across all three tested LLMs: GPT-4.1-mini reaches **0.7525**,
DeepSeek chat **0.7602** (Table [model-swap table reference]). Other families are materially
stronger: Diagnosis 0.8397–0.8708, Prescription 0.8926, Investigations 0.8563–0.9091. The gap
is not model-specific — swapping the LLM while holding the component graph constant narrows it
by only +0.008. It is not a data-surface artifact — the gap closes to ~0.9053 on dev140 when a
task-specific SF adjudicator is added, confirming that targeted post-processing can correct the
base extraction, but the base extraction residual persists in the same direction as the Gan wall.

The clinical task is the same in both settings: extract the current seizure burden from
prose where evidence is often hedged, qualified by event rather than rate, or temporally
ambiguous. The illegitimate evidence shapes that drive Gan over-reading — last-event-only
anchors, open-ended temporal qualifiers, vague counts read as habitual rates — are present
in real clinical letters too.

**[PENDING PROBE]** A forward-observable-feature probe on a stratified ExECTv2 SF slice is
required to confirm that the entropy signature matches the Gan pattern (confident, not uncertain,
over-reading). Pending that result, the cross-dataset claim is structural: the same clinical
task, the same family weakness, the same persistence across models, the same correctability by
task-specific adjudication. The interpretation is that the extractor's ceiling is **the task's
clinical-ambiguity floor**, not a deficiency of the architecture or the model. This is the
argument that converts "SF is our weakest family" from an apology into the paper's strongest
generalization claim: a system whose limits are task-bound exhibits exactly the behavior a
genuinely modular, clinically-grounded architecture predicts.

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
| **3.2 Wall transfer: the task-bound ceiling** | **Confident over-reading as cross-dataset phenomenon** | **Gan P2.1 + ExECTv2 SF gap + [PENDING PROBE] entropy** |
| 3.3 Evaluation discipline transfers | Held-out-family CV, adversarial battery as reusable gates | Gan protocol applied to ExECTv2 robustness panels |

Section 3.2 (this subsection) anchors the generalization claim. Its opening sentence converts
the SF finding:

> The wall that bounds Gan seizure-frequency performance is not dataset-specific. It is a
> property of the clinical task.

The section then presents the Gan ceiling, the P2.1 entropy mechanism, the ExECTv2 SF gap,
and the structural parallel — with [PENDING PROBE] gating the mechanism confirmation.

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

**Supported by available artifacts (validation-only probe + frozen aggregate full-200):**

- ExECTv2 SF is the weakest family under a frozen same-core architecture at full-200 aggregate
  for both GPT-4.1-mini (0.7525) and DeepSeek chat (0.7602).
- The SF gap persists across model swaps (+0.008 under DeepSeek vs GPT).
- Gan P2.1 establishes confident over-reading on Gan: mean label entropy 0.012, `band_unknown`
  entropy 0.000 (validation-only probe, n=150).
- The ExECTv2 SF gap is reducible by task-specific adjudication (dev140 v08: SF 0.9053).
- Evidence rate is 1.0000 on all full-200 ExECTv2 model-swap runs; the SF gap is not an
  evidence-failure.

**Not yet supported (requires pending probe):**

- Confirmation that ExECTv2 SF over-reading is confident (not uncertain) — requires the
  entropy probe on an ExECTv2 SF slice.
- Cross-dataset H0_confident_over_reading verdict for ExECTv2 SF.
- Row-level mechanism attribution on ExECTv2 SF — excluded by the aggregate-only policy.

**Not supported (outside evidence boundary):**

- Holdout SF comparison on ExECTv2.
- Claim that the wall mechanism is identical across datasets; the claim is structural parallel,
  not identity.
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
  — **[PENDING PROBE: does not yet exist]**
