> **Superseded for navigation —** canonical summary: [`GAN2026_RESEARCH_CANON.md`](../GAN2026_RESEARCH_CANON.md). Gan closeout, architecture arc, and The Wall. Full detail retained below.

# Gan 2026 — Research Closeout Synthesis

Date: 2026-06-17

This is the closeout document for the Gan 2026 seizure-frequency strand. It pulls
the full body of work into one accounting: every architecture and experiment family
that was attempted, what worked and what did not and why, the formal research
questions that were posed and the answers that emerged, and the distilled,
paper-facing insights. It supersedes no result; it indexes and interprets them.

The active recommendation is unchanged and frozen: the single GPT structured-event
pass is the go-forward simple labeler (`364/450 = 0.809` Purist on locked
`test450`, verified on `gpt-4.1-mini`); the V12 v0.4 fresh-evidence hybrid is the
high-complexity ceiling comparator (`379/450 = 0.842`); no further `0.90`
optimization on the current model family is planned. Forward implementation focus
moves to ExECTv2.

**Guardrail note.** This synthesis was assembled from validation-side artifacts,
aggregate `test450` numbers (already public in `PROJECT_STATUS.md`), and protocol /
answer documents. No `test450` row-level failures, rationales, selected events, or
transitions were inspected, and no new experiments or edits were proposed.

---

## Part I — Exhaustive Experiment Accounting

### 1. The architecture arc

The project walked a deliberate complexity ladder. Each rung was an honest attempt
to either (a) own the clinical interpretation more cleanly, or (b) buy back the
residual error of the previous rung.

| # | Variant | Mechanism | Model(s) | Validation Purist | test450 Purist | Verdict |
|---|---------|-----------|----------|-------------------|----------------|---------|
| 1 | Deterministic floor (`rules_only`) | Pure rule extraction + normalization, no LLM | none | 688–697/750 (de-overfit stage dependent) | 343/450 = 0.762 | Floor / controlled variable |
| 2 | LLM-only **direct labeler** | One call renders the final Gan label directly | gpt-4.1-mini | 564/750 rendered | ~0.71–0.72 (mini) | Rejected (weakest) |
| 3 | Hybrid (rules candidates + LLM adjudicator) | Deterministic CandidateSet → LLM clinical assessment → deterministic render | gpt-4.1-mini | ~500–511/750 rendered | not run | Rejected |
| 4 | LLM-only **structured-event** (SE) | LLM lists source-near events w/ exact evidence + temporality, selects one; deterministic render/score | **gpt-4.1-mini** | **661/750 = 0.881** | **364/450 = 0.809** | **Promoted → chosen production arch** |
| 5 | Multi-component staged assembly + switch layers | Deterministic state machinery + narrow high-precision LLM change-only switches + few-shot candidates | gpt-4.1 / mini (mixed) | up to 708–726/750 (projected) | best 357/450 = 0.793 | Rejected (clean but low-coverage) |
| 6 | Three-agent exact consensus | Deterministic floor + exact-label unanimity across GPT/Qwen/DeepSeek SE | det. rules + gpt-4.1-mini + qwen3-235b + deepseek | 708/750 = 0.944 | 365/450 (constrained replay) | Rejected (didn't transfer) |
| 7 | V1–V11 agentic ladder | Second-pass reasoners / routers / verifiers / specialists over the GPT SE V0 | gpt-4.1-mini | best V9 val250 237/250 | none on test | Rejected (broad regresses, safe too weak) |
| 8 | **V12 fresh-evidence reasoner** (full hybrid) | 4th LLM pass reviews raw evidence over GPT/Qwen/DeepSeek SE scaffolds, keep-or-replace GPT final + ~6-rule guard | **full gpt-4.1** (reasoner) | **682/750 = 0.909** | **379/450 = 0.842** | **Best holdout; accepted ceiling** |
| 9 | A3 — GPT-only reasoner ablation | V12 reasoner sees only its own GPT trace | full gpt-4.1 | 610/750 = 0.813 | not run | Rejected (reasoner net −51) |
| 10 | A4 — 2-model reasoner ablation | V12 reasoner sees GPT + DeepSeek | full gpt-4.1 (+deepseek) | 631/750 = 0.841 | not run | Rejected (reasoner net −30) |

Five mechanism-level findings hold the arc together:

1. **Direct-label prediction is unsafe under Purist scoring.** Collapsing
   extraction, normalization, temporal reasoning, selection, and label grammar into
   one call produced, on full validation, 26 wrong→correct against **329
   correct→wrong**. The model saw the clinical signal but over-read historical
   mentions and was brittle on label syntax. Raw LLM finals are useful as
   *candidates*, never as predictions.

2. **Structured-event extraction was the breakthrough** precisely because it forced
   an inspectable, evidence-grounded intermediate state: the LLM stays *source-near*
   (events + exact substrings + temporality/certainty) and deterministic code owns
   only rendering and scoring. It posted the best LLM result (`0.881` val / `0.809`
   test on mini) **and** the smallest validation→test drop (7.2pp), because
   evidence-grounding suppressed the over-reading that sank the direct labeler.

3. **The hybrid/ensemble/guard apparatus buys little.** The full V12 stack reaches
   `0.842`, but the single GPT SE pass is only `+15` test rows behind. The
   layer decomposition (`gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16`)
   showed the deterministic guard layer is **near-inert** (fires on 8/750
   validation rows, +6) and the reasoner's lift is *entirely* the replace mechanism
   disciplined by cross-model agreement — not raw cleverness.

4. **Corroboration is non-linear in depth.** The reasoner's net effect vs simply
   keeping the GPT pass it reviews: GPT-only (A3) **−51**, GPT+DeepSeek (A4)
   **−30**, full 3-trace ensemble **+21**. With insufficient corroboration the
   free-to-replace agent over-replaces — the same unknown-over-reading failure. One
   peer does not suffice; it takes all three traces to flip the replace decision
   net-positive. Both ablations land *below* the bare one-model pass (`0.881`),
   i.e. simpler dominates until the full ensemble is present.

5. **Provenance caveat (load-bearing).** `build_dspy_lm` does no aliasing. The
   `0.842` hybrid and both reasoner ablations ran on **full `gpt-4.1`** (which
   exhausted the OpenAI budget mid-investigation). But the **chosen single SE pass
   is mini-verified** — its `test450` and `validation750` artifacts both record
   `openai/gpt-4.1-mini`, and the `v0_reference` layer inside the full-gpt-4.1
   reasoner artifact is byte-identical (0/750 mismatches). So `0.809` is a clean
   mini number with no full-gpt-4.1 dependency in the production path.

### 2. The formal research-question series (RQ1–RQ10)

Parallel to the architecture ladder, the project ran a disciplined five-stage
pipeline decomposition (candidate discovery → evidence selection → rich state →
projection → deterministic compilation) plus cross-cutting questions. All answers
were scoped as **validation-development component answers**, not benchmark claims;
only RQ6 carried a frozen aggregate-only `test450` audit.

- **RQ1 — Candidate discovery.** The useful LLM role is *selective boundary-state
  proposal*, not broad replacement. The raw LLM selector had 0.985 exact evidence
  but recall only 0.869 vs deterministic 0.967 (recovered 11, missed 94). Candidate
  discovery is not the broad bottleneck for ordinary rates.
- **RQ2 — Evidence selection.** LLMs are strong evidence *locators* but unsafe broad
  clinical *selectors*: 61/61 exact evidence yet 0 W→C / 8 C→W. Promote LLM evidence
  only behind exact-span + source-id gates; block unconstrained label changes.
- **RQ3 — Clinical state representation.** A rich typed selected state + exact
  evidence + deterministic renderer is the right bridge (hard panel: 75/75
  structured, 75/75 parseable projections). Trust the LLM as a **fact carrier, not a
  category chooser** — it overused `state_kind="frequency"` but parked corrective
  facts in boundary fields.
- **RQ4 — Projection.** The dominant remaining bottleneck. Broad graph/LLM label
  projection is a clean negative (`state_graph_projection`: 0 W→C / 84 C→W), but
  narrow gated policies recover named slices at high precision (18 W→C / 0 C→W).
- **RQ5 — Deterministic compilation/rendering.** Faithful: 0 parse failures, 0
  evidence loss, 0 semantic drift across a 2,295-row matrix. Remaining wrong labels
  are upstream state/projection failures, not rendering drift (ABL-off introduced 6
  drift rows, proving the policies are load-bearing).
- **RQ6 — Selective LLM value (only frozen-test RQ).** The project's strongest,
  most defensible claim: value comes only as a small, exact-evidence, no-regression
  selective intervention behind a deterministic safety floor. Validation750: 21
  changed, 11 W→C, **0 C→W**, precision 1.000. Frozen `test450`: 14 changed, 8 W→C,
  **0 C→W**, precision 0.889. This is a *hybrid safety-floor* result, not an
  LLM-first result.
- **RQ7 — Generalization by hidden family.** The governing meta-lesson:
  validation-prefix success does **not** imply hidden-family transfer (A2 went
  232/250 on validation250 → 337/500 on the later 500). Family must be the unit of
  generalization. Cluster/diary/denominator/convention families remain unsolved.
- **RQ8 — Efficiency & reliability.** Narrow extractive LLM + deterministic
  rendering wins operationally (0 parse failures, 1.000 source ids). Deep schemas
  and all-in-one prompts are operationally inferior. Cost/latency claims are
  *blocked* — 0/21 rows had complete cost telemetry.
- **RQ9 — Selective action / abstention.** v3 router covers 716/750, abstains 26,
  routes 8 to review, covered-row accuracy 0.9469. The win was *calibration*
  (over-review 154→8), not raw accuracy.
- **RQ10 — Gold/scorer ambiguity audit.** The residue is mixed, not one thing:
  0.641 ambiguity rate across the 53 validation Purist-wrong rows;
  `underdetermined_note` 23, `true_extraction_failure` 19,
  `benchmark_convention_dominated` 11; **0 likely gold defects**. The benchmark is
  not "wrong"; hard rows should be routed through review policy, not used as
  undifferentiated pressure to retune rules.

**RQ1, RQ2, and RQ4 were explicitly reset** during the project: their first-pass
(06-03) answers concluded the deterministic rule set was the best substrate; the
retrospective ruled that invalid (validation-tuned rules winning by default is not
a research answer) and re-derived all three as LLM-component-mechanics findings
under strict attribution.

### 3. The hard residual and clinical-reasoning limits

At the `0.842` ceiling, the selector-only **oracle** ceiling on validation is
739/750; of the 17 selected-wrong rows, 6 are selector-addressable and **11 have no
Purist-correct component at all** (8/11 in `band_unknown`). Selection is
exhausted; the binding constraint is *component generation*. The residual taxonomy:

- **Unknown-vs-rate over-inference (dominant).** Evidence that supports only an
  `unknown` state is converted into a quantified rate or seizure-free duration. Four
  illegitimate evidence shapes: last-event-only, open-ended "since", vague-count,
  relative-trend. Largest no-correct cluster.
- **Seizure-free over-inference from a last-event anchor.** A single dated last
  event + "none since" is converted into a quantified duration. Highly generalisable
  to real letters; the safe behavior is to leave it unresolved unless a source-backed
  event date exists.
- **Provoked / transient / underspecified count → habitual rate.** An explicit
  count+window describing provoked or transient events is read as a habitual
  frequency. This is the precise mechanism the robustness battery Panels A/B target.
- **Cluster / burden cadence flattening.** The cluster interval is encoded but the
  per-cluster burden axis ("multiple per cluster") is dropped — the *weakest battery
  axis*. The 18 null-rendered cluster rows are a missing owned semantic contract,
  not a parser gap.
- **Denominator / window errors, diary aggregation, benchmark-convention** make up
  the smaller, more idiosyncratic remainder.

These were localized by four diagnostics: the **hidden-family first-failure atlas**
(showed the residual is generation-bound), the **family-transition instrumentation**
(sharpened a useless uniform ~0.22 changed-label precision into a 0.11→1.00 spread
and pinned the consensus override's damage to `band_weekly`, net −3), the
**null-action taxonomy** (the null surface is ambiguity and contract debt, not clean
"unknown" statements), and the **selector saturation audit** (oracle 739/750).

Every attempt to close the unknown-over-reading residual failed in the same
direction: binding final label to the model's own triage (v0.7) passed the
robustness battery 100% but fell **−106** on validation; a confidence-gated reasoner
(v0.10) fell **−81** with 73 genuine-rate regressions; a narrow cluster-axis gate
(C6) was clean but `+0` on test; the knowledge-graph state-graph component (Stages
A–D) **could mint a Purist-correct competing component for 7/11 residual rows**, but
its only regression-safe selection posture (independent corroboration) recovered
**0/7** at selection time — because the no-correct residual is *defined* by every
other component being wrong, so nothing exists to corroborate it. The structural
verdict: on the binding rows, the signal distinguishing *withhold-to-unknown* from
*emit-rate* is **absent from every forward-observable feature**; only the hidden
gold separates them. No gate, model, or graph can exploit it gold-free. `0.842` is
the honest ceiling for this architecture family on mini. The one unrefuted route to
`>0.90` is a genuinely stronger model reading provoked/transient/adherence cues
directly from prose — which changes the stated mini constraint and was deliberately
not taken.

### 4. Methodology that survived, and the negative results

**Practices that proved more informative than metric chasing:**

- **Decision-effect component attribution** — owning each row by *which component
  changed the clinical fact*, not which module ran. This forced score-layer ladders
  so a deterministic-floor gain could never be silently credited to the LLM, and is
  why the frozen V12 audit had to be described as a *deterministic-safety-floor
  hybrid*.
- **Exact-evidence gating** — every changed row must cite an exact substring;
  evidence validity is reported separately from score (V12 validation750: 703/750
  exact). A hard rejection criterion.
- **Validation hard slices** — once validation750 saturated (oracle 739/750),
  targeted matched slices replaced aggregate F1 as the discriminator.
- **Synthetic/adversarial robustness battery (primary pre-test gate)** — three
  predeclared panels: minimal-pair hard-negatives (A), source-near perturbations
  (B), KCL-style OOD prose (C). A `transfers` verdict is *necessary but not
  sufficient* for a `test450` authorization. It scored the V12 v0.6 evidence variant
  **overfit** (A 3/6, B 5/7) despite perfect OOD — exactly the design intent.
- **Held-out-family cross-validation** — leave-one-band-out; promote only on
  cross-family stability. This operationalized the catch that the validation
  *winner* (unanimous-exact consensus, the only run to clear 700/750) was the
  *worst* generalizer because its gain was borrowed from validation-tuned
  deterministic components.
- **Frozen aggregate-only test audits** — predeclared slices, a deterministic
  preflight pinning hashes/versions and injecting contamination canaries, and a CLI
  guard forbidding row-level test inspection.
- **Controlled-variable treatment** of Gan-specific rules and benchmark-format
  repairs — isolated, ablatable, labeled. Ablation confirmed benchmark repair moved
  6 labels but *neither* aggregate Purist nor Pragmatic F1 — formatting support, not
  a performance driver.

**Headline negative results:**

- **V12 v0.6 + safety-v0.9 rejected on frozen `test450` at `351/450`** — below the
  383 pre-registration target *and* below the V0 deterministic comparator (364) and
  the v0.4 ceiling (379). The robustness battery had already flagged it overfit; the
  pre-test gate did its job before a contract-only improvement could be laundered
  into a benchmark claim.
- **Validation overstates holdout.** Deterministic V1 scored `0.9293` on
  validation750 but `0.7600` on locked test — a ~17-point gap on the same synthetic
  template data. This reframed the rule stack as "validation-saturated" and spawned
  the entire validation→test gap protocol.
- **Research-drift self-audit** flagged the biggest *metric* opportunity
  (deterministic semantic repair) as the biggest *research* risk, and ruled that
  metric gains were acceptable only with component labels, repair-rate reporting,
  evidence validity, and hybrid claim language.
- **Prompt-contamination audit** found internal vocabulary leaking into model-facing
  payloads; disposition was to demote interpretation and build clean successors, not
  discard evidence or burn validation budget.

---

## Part II — Central Research Questions and Answers

The strand asked six questions worth stating plainly, with the answers the evidence
actually supports.

1. **Can deterministic rules alone solve Gan seizure-frequency extraction?**
   No. They are a strong, transparent, controllable floor (`~0.76` test) and an
   indispensable controlled variable, but validation badly overstated their holdout
   generalisation (`0.929` → `0.760`). Rules learn validation-surface phrase
   families, not robust clinical reasoning.

2. **Can a single LLM own the clinical interpretation?**
   Only if it is forced to stay source-near. Direct final-label prediction was the
   weakest non-degenerate architecture (`~0.71–0.72` mini test) because it
   over-reads and is label-brittle. **Structured-event extraction** — same single
   model, but emitting evidence-grounded intermediate state — was the strongest LLM
   architecture (`0.809` test) and the best generaliser. The intermediate state, not
   the model, is what made the difference.

3. **Do hybrid / agentic components close the gap?**
   Modestly, and at steep cost. The full V12 stack reaches `0.842`, but that is only
   `+15` test rows over the single structured-event pass, the guard layer is
   near-inert, and the ensemble's value is non-linear: it materialises only when all
   three peer traces are present (one or two peers make it *worse* than no reasoner
   at all). The marginal complexity is not worth its marginal holdout gain.

4. **Where is the hard residual?**
   Unknown-vs-rate and cluster-burden clinical reasoning. The system over-infers
   habitual rates or seizure-free durations from last-event-only, provoked/transient,
   adherence-confounded, or underspecified evidence. On the binding rows the
   discriminating signal is not present in any forward-observable feature, so the
   residual is a *clinical-reasoning* limit, not a selection or engineering one.

5. **What methodology survived?**
   Component attribution, exact-evidence checks, validation hard slices,
   synthetic/adversarial panels, held-out-family CV, and frozen aggregate-only test
   audits — every one of which caught a failure that aggregate metric chasing would
   have shipped (the v0.6 overfit, the validation-winner-worst-generaliser, the
   17-point holdout gap).

6. **What is the paper-facing lesson?**
   The durable contribution is **auditable modular extraction and disciplined
   evaluation**, not a near-perfect Gan score. The defensible claims are: structured
   intermediate state beats direct labeling; selective gated action beats
   replacement (`0 C→W` on both validation and frozen test); and on a homogeneous
   synthetic benchmark, aggregate validation F1 is actively misleading.

---

## Part III — Distilled Insights

1. **State beats labeling.** The single highest-leverage decision in the entire
   strand was making the LLM emit source-near structured events instead of a final
   label. Same model, same data — a `~0.10` absolute jump and the best transfer,
   because evidence-grounding is what suppresses over-reading.

2. **The complexity/accuracy curve is non-monotone.** A one-model pass (`0.881`
   val) beats a one-model reasoner (`0.813`) and a two-model reasoner (`0.841`);
   only the full three-model hybrid clears it. Adding capability without sufficient
   corroboration actively hurts. "More models" is not a dial you can turn smoothly.

3. **The abstain/keep signal must be external.** Whenever the model was allowed to
   act on its own confidence (direct labels, triage-binding, confidence gates), it
   over-committed in the unknown-over-reading direction. Discipline has to come from
   an *independent* source — peer agreement, a deterministic safety floor, exact
   evidence — never the model's own certainty.

4. **Validation saturation is a trap, and family is the unit of generalization.**
   The architecture that won validation generalised worst; a 232/250 prefix result
   collapsed to 337/500 on hidden families. Held-out-family CV and a predeclared
   adversarial battery were the only honest promotion gates.

5. **Some residual is a clinical-reasoning wall, not an engineering gap.** A
   knowledge-graph component could *generate* a correct competing answer for 7/11
   no-correct rows but could never safely *select* it, because the distinguishing
   evidence is absent from every inference-time feature. Recognising this — rather
   than chasing it with more rules or more agents — is itself the result. `0.842` is
   honest; `>0.90` would require a stronger model reading the prose directly.

6. **Auditability was the product.** The decompositions that localized the residual,
   the attribution discipline, the contamination canaries, and the frozen protocols
   are what make every number above trustworthy. That regime — not the score — is the
   transferable contribution to ExECTv2 and to the paper.

---

## Core Artifacts

- ``
- ``
- `experiments/gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16.md`
- `experiments/gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16.md`
- ``
- `` (+ the RQ1–RQ10 `*_answer_*` docs)
- ``
- `` (state-graph Stages A–D)
- ``
- ``
- ``
- `experiments/RUN_INDEX.md` (canonical run registry)
