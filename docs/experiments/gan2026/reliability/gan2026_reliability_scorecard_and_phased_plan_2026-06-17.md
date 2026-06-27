# Gan 2026 — Reliability Scorecard and Phased Plan

Date: 2026-06-17

This document refocuses the Gan 2026 strand on **reliability**, the original central
research question that the accuracy-maximization arc drifted away from. It maps the
full body of work onto the ten core reliability dimensions from the internal
literature review (`docs/literature/llm_reliability_literature_review.pdf`, §3),
scores how well each is currently evidenced, and lays out a phased plan that begins
with everything achievable at **zero model budget**.

It builds on `gan2026_research_closeout_synthesis_2026-06-17.md`. The governing thesis:
**the project already measured most of these reliability properties — it reported them
as accuracy.** Nine of ten dimensions have substantial existing evidence; the dominant
work is re-expression of existing logs into reliability form, not new experiments. The
findings below come from a four-agent deep evidence audit (2026-06-17); every cited
artifact was read, and numbers were recomputed from logged JSONL where stated.

**Evidence validity metric (2026-06-27):** unified cross-task definition in
[`docs/reference/evidence_groundedness_metric.md`](../../reference/evidence_groundedness_metric.md).

---

## Scope, canonical subject, and the governing prior

*(Added 2026-06-17 after a design grilling against `CONTEXT.md`; see decision
`docs/decisions/0018-reliability-scorecard-canonical-subject-is-v0reference-single-se-mini.md`.)*

**Scope — bounded reopening.** This is not a clean reopening of the frozen strand.
All of Phase 0 (zero budget, re-analysis) is the paper spine and is run in full.
Phase 2's one new experiment (P2.1) is **conditional**: it is fired only if Phase 0
leaves the calibration/abstention story genuinely thin. The freeze on accuracy
optimization stands; this work re-expresses reliability, it does not chase 0.90.

**Canonical subject (decision 0018).** Every scorecard metric is computed on **one**
architecture — the frozen production single GPT structured-event pass on
`gpt-4.1-mini`, read per-row from the `v0_reference` layer of the V12 artifacts —
unless explicitly tagged `[comparator: V12-full-gpt4.1]` or
`[comparator: hybrid-adjudicator]`. The 703/750 and 423/450 exact-evidence figures,
the 0.842 task score, and the rq9 router's 0.929 base are all comparators, not
subject rows; the subject's faithfulness and task numbers are re-derived from
`v0_reference.evidence_valid` and `v0_reference.comparison.purist_correct`. A number
without a layer tag is not admissible.

**The governing prior — "The Wall."** The strand's central negative result (closeout
synthesis, Insight #5) is that on the binding residual rows the signal separating
*withhold-to-unknown* from *emit-rate* is absent from every forward-observable
feature. This is the **prior**, not a thing to be reframed away. P0.2 (risk–coverage)
and P2.1 (semantic entropy) are **falsification tests** of the wall; their null —
the external/entropy signal is flat or absent at the residual — is itself a headline
result (it proves the over-reading is *confident*, which is *why* no abstention
signal can catch it). Language that pre-judges these as foregone reframings has been
removed below.

---

## Part I — The Reliability Scorecard

Coverage score: 5 = fully evidenced already in proper reliability form; 1 = absent.
"Axis" notes whether the current evidence is on a reliability axis or an accuracy axis.

| # | Dimension | Cov. | Current state (verified) | Gap to close |
|---|-----------|:----:|--------------------------|--------------|
| 1 | **Task correctness** | 4/5 | Frozen holdout task score (0.809 single SE / 0.842 hybrid), render success 0/2295 parse fails, abstention-aware covered-row acc 0.9469 (RQ9). | Risk–coverage curve on test450; per-family frozen breakdown. Both no-budget. |
| 2 | **Factuality** (closed-extraction: value true to letter; failure = over-inference) | 3/5 | Dominant failure named & ranked (unknown→rate / last-event→seizure-free over-inference); purpose-built adversarial battery; RQ10 found **0 gold defects** (misses are model fabrications). | Reported as panel pass/fail + W→C/C→W deltas, not a **fabrication / over-inference rate**. Re-aggregation, no-budget. |
| 3 | **Faithfulness** | **5/5** | Project centerpiece. Exact-span evidence + source-id gating enforced in code (`fresh_evidence_reasoner.py`, `structured_event_verifier.py`); `[comparator: V12-full-gpt4.1]` validation750 703/750 exact, **frozen test450 423/450 exact**, reported separately from score; RQ2 61/61 exact yet 0 W→C / 8 C→W (grounding ≠ selection). | **Subject metric re-derived from `v0_reference.evidence_valid`** (single-SE-mini), not the 703/423 full-gpt-4.1 figures (now comparators per decision 0018). Relabel counts as a faithfulness rate; build the faithful×correct 2×2. No-budget. |
| 4 | **Calibration** | **2/5** | Per-row `confidence` IS logged across architectures/models — but **degenerate**: 749/750 rows "high" on validation, 443/450 "high" on test450; buckets statistically indistinguishable. `explore_uncertainty_signals.py` builds an accuracy-by-confidence table but **never ECE/Brier/reliability diagram**. | Self-confidence is uninformative → must derive a score from **external** signals (cross-model agreement, evidence-exactness) and compute ECE/Brier/failure-prediction AUROC over existing logs. No-budget. |
| 5 | **Abstention** | 4/5 | Richest of the uncertainty cluster. RQ9 v3 router logs per row `selective_action {predict 716 / abstain 26 / review 8}` **and** `purist_correct`; RQ6 selective gated action 0 C→W on both validation and frozen test; 53-row ambiguity gold set (RQ10). Honest-ceiling reframe: the 11 no-correct rows (8/11 band_unknown) are **abstention targets, not failures**. | Only three discrete operating points exist — **no risk–coverage curve drawn**, though the data supports it. No-budget. |
| 6 | **Robustness** | 4/5 | Crown jewel. Predeclared 3-panel battery (minimal-pair / source-near / OOD) gating test450; four scored candidates; the v0.6 **overfit** verdict (A 3/6, B 5/7) was vindicated when v0.6 scored 351/450 on frozen test. Key finding: v0.7 passed battery 100% yet **−106 on validation** (battery is necessary, not sufficient). | Reported as panel pass/fail, not a continuous robustness index / flip-rate. No-budget to re-express. Paraphrase-invariance on real test rows needs budget + freeze-warden. |
| 7 | **Consistency** | 3/5 | Real same-model self-consistency exists (`tool_self_consistency.py`, hard50, k=4 + temperature reference) — but n=50, reported as a reject gate; agreement does **not** separate correct from wrong (4/4 unanimous = 0.69 acc). Panel B is invariance testing. | n=50 only; population-scale semantic entropy missing. Re-tabulate hard50 no-budget; population run needs budget. |
| 8 | **Safety & compliance** (reframed: fail-closed + research-integrity) | 4/5 | Strong & code-enforced. 0 C→W no-regression safety floor; abstain-to-unknown policy (`SAFETY_GATE_VERSION v0_9`); working contamination canaries (`frozen_test_preflight.py`); CLI guard forbidding row-level test inspection; hash/version pinning. | Demographic/jailbreak/PII safety unmeasured — correctly **out of scope on synthetic data** (state as finding). Assemble safety-property table. No-budget. |
| 9 | **Fairness** (subgroup = clinical family/band) | 3/5 | Excellent substrate: per-family transition stats (`family_transitions.py`), leave-one-band-out CV gate (`family_cv_promotion.py`, refused the validation winner because band_weekly regressed −3), precision-gated selector. Drove the "validation winner = worst generalizer" decision. | Never expressed as a **parity/disparity metric**; no per-family parity on frozen test; demographic fairness structurally unmeasurable here. No-budget to re-express. |
| 10 | **Operational reliability** | 3/5 | Integrity is 5/5: 0 parse failures / 0 evidence loss / 0 drift across 2,295 rows; source ids 1.000; resumable runners (`run_resume.py`); full provenance stamping; run-level latency captured. Honest observability gate (`rq8_telemetry_guard.py`) **blocks** the cost claim at 0/21 rows. | Per-call cost/token/retry telemetry genuinely missing. Latency (aggregate) + token estimates **reconstructable offline** (tiktoken over saved prompts) with no spend; retry needs a re-run. |

**Aggregate read.** Mean coverage ≈ 3.5/5. The two genuine weak points are **Calibration
(2/5)** — driven by degenerate self-confidence, which is itself the project's headline
calibration finding — and the cost-telemetry leg of **Operational reliability**. Both the
strongest dimension (Faithfulness, 5/5) and the most decision-relevant one (Abstention,
4/5) need only re-expression, not new data.

**The unifying discovery.** The single most repeated audit conclusion, across all four
clusters independently, was: *the data to populate this dimension already exists in logged
artifacts; what is missing is the reliability-form metric and the driver to compute it.*
This is why the plan front-loads a no-budget phase that can populate the entire scorecard.

---

## Part II — Phased Plan

Three phases, ordered by cost. **Phase 0 requires no model calls and produces the entire
scorecard.** Phase 1 requires no new model calls but needs freeze-warden governance.
Phase 2 is the small, targeted fresh-model-budget work, with one genuine research swing.

Every incremental runner below must be resumable via `core/run_resume.py` (foundational
project requirement) even when replaying, and every new artifact registers in
`experiments/RUN_INDEX.md`.

### Phase 0 — Zero model budget (re-analysis of existing logs)

Each task is a deterministic driver over already-saved JSONL/JSON. No LLM calls.

- **P0.1 — Faithfulness × correctness 2×2 + over-inference rate** *(Faithfulness, Factuality, Task correctness).*
  Join, **per row on the `v0_reference` layer** (the canonical single-SE-mini subject, decision
  0018), `v0_reference.evidence_valid` with `v0_reference.comparison.purist_correct` in the
  saved frozen artifacts (`gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl`
  and the validation750 sibling). Yields: holdout faithfulness rate as a proper metric on the
  *production* path, the **faithful-but-clinically-wrong** cell (the project's whole thesis,
  never tabulated), and the directional over-inference/fabrication rate on unknown-gold rows.
  The full-gpt-4.1 V12 `final`-layer rate (703/423) is reported alongside only as a tagged
  comparator.

- **P0.2 — Risk–coverage / selective-prediction curve** *(Abstention, Calibration, Task correctness). HEADLINE.*
  Order all 750 rows by **one predeclared composite External Risk Score** — *not* the three
  interchangeable signals first drafted here. The evidence audit found that of those three,
  `selected_evidence_exact` is **degenerate (750/750 True** in the router file, as uninformative
  as self-confidence), and **cross-model agreement is not in the rq9 file at all** — it must be
  joined from `consensus_decision.votes` in
  `gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.jsonl`
  (per-row gpt-4.1-mini + qwen + deepseek labels → agreement 3/2/1) by `source_row_index`. The
  composite therefore combines: **cross-model agreement count** (strongest leg, the same signal
  that drove V12's only positive lift), **ambiguity-reason count** (coarse, 5 buckets), and the
  **`source_has_*` residual-shape flags** (`last_event`, `since_anchor`, `trigger`,
  `drop_attack`, `unable_to_quantify`). Score against **`v0_reference.comparison.purist_correct`**
  (the canonical subject), *not* the rq9 `hybrid_adjudicator_with_adapters` purist. Sweep the
  abstention threshold; plot selective-risk vs coverage as a **step function with explicit
  operating points and CIs** (the curve rests on only ~53 error events), and report AUC and
  risk-at-fixed-coverage. This converts RQ9's three operating points into the full curve. **It
  is a falsification test of The Wall, not a reframing of it:** the headline is the
  decomposition of the gap into *recoverable error* (shed by the external score) vs *irreducible
  residual* (the plateau fixed at the no-correct rows). A hard plateau at the residual is the
  expected, publishable result — it is the empirical proof of the wall drawn as a curve.

- **P0.3 — External-signal calibration (ECE / Brier / failure-prediction AUROC)** *(Calibration).*
  Self-confidence is degenerate, so define the calibration score from external features
  (cross-model agreement, `evidence_valid`, parse-repair count) over existing per-row logs;
  produce a real reliability diagram + numeric ECE/Brier/AUROC. Extends
  `explore_uncertainty_signals.py` Section 5. The honest calibration story: external signals
  rank correctness; self-reported confidence does not.

- **P0.4 — Robustness index + invariance flip-rate** *(Robustness).*
  Re-aggregate the four saved battery JSONs into a continuous robustness index (mean panel
  pass-fraction + minimal-pair both-sides-correct consistency rate + the overfit-gap between
  rate-side and unknown-side accuracy), and compute a Panel-B paraphrase flip-rate from the
  original↔perturbed pairs in `cases.json`.

- **P0.5 — Error-parity gap across families/bands** *(Fairness).*
  From the per-band transition tables (`family_transitions` / `family_cv_promotion` outputs,
  the v0.9 selector replay JSONL): compute cross-family error-rate spread (max−min per-band
  Purist accuracy, coefficient of variation) and lift the `gap_robust` "any held-out band
  regresses" boolean into a standalone fairness flag reported on every candidate.

- **P0.6 — Safety-property table** *(Safety & compliance).*
  Collate into one table: the 0 C→W floor (with numbers), the abstain-to-unknown policy
  (file + version), the contamination-canary results, and the CLI/readout governance guards.
  Add the explicit out-of-scope finding: synthetic templated letters ⇒ PHI-leakage and
  demographic-bias evals are N/A and would require real-letter validation before any
  deployment claim.

- **P0.7 — Operational-integrity scorecard + offline cost/latency reconstruction** *(Operational reliability).*
  Assemble the integrity row (0/2295 parse fails, source ids 1.000, resumability, provenance
  fields). Then reconstruct an **offline-estimated** cost/token/latency band: harvest
  `elapsed_seconds`/`seconds_per_row` already in run metadata, and re-tokenize saved
  `prompt_input_json` + `raw_output` with `tiktoken` (no API call) → per-row token/cost
  estimates. Feed both as explicitly *estimated* fields into `rq8_telemetry_guard.py`,
  converting RQ8 from "fully blocked" to "partially reconstructed, offline-estimated."
  (Retry count remains genuinely un-reconstructable.)

- **P0.8 — Hard50 self-consistency re-tabulation** *(Consistency, partial).*
  From the existing `tool_self_consistency` hard50 JSONL, compute per-row agreement entropy /
  majority fraction and the agreement↔accuracy curve. **Temperature caveat (2026-06-17):** the
  saved hard50 samples are all temperature 0.0, so this artifact measures *reproducibility /
  determinism*, **not** genuine self-consistency — it cannot draw a "self-consistency is
  uninformative" conclusion. What survives: even fully-reproducible (temp-0 unanimous) hard rows
  are wrong ~31%, and 5/50 rows disagree despite identical temperature. Genuine self-consistency
  **requires varying temperatures** and is deferred to P2.1; this leg is therefore scored **2/5**,
  not 3/5, until P2.1 runs.

- **P0.9 — Assemble the master reliability scorecard.**
  Merge P0.1–P0.8 into the single ten-dimension scorecard with proper metrics. This is the
  paper-facing spine and is achievable entirely within Phase 0.

### Phase 1 — No new model calls, but freeze-warden governance required

These replay existing test450 prediction artifacts through new analysis; they read the
locked split. The Phase-1 gate is stated as **two concrete invariants** (not a vague
"freeze-warden required"), because the existing guard only checks the readout text:

1. **Output-aggregate invariant** *(already mechanically enforced)* — every artifact passes
   `frozen_test_readout`'s aggregate-only check: no per-row tables, no `source_row_index`,
   `transition_vs_v0`, or `score_layers` markers; only subgroup/curve aggregates.
2. **Pre-frozen-transform invariant** *(the new thing the Freeze Warden must certify)* — the
   external-score function (P1.1) and the family-tagging function (P1.2) are predeclared,
   deterministic, and **frozen by hash before they touch test450**. P1.2 must reuse the
   *existing validation* family classifier (`family_transitions` / `family_cv_promotion`),
   never a test-tuned one. This closes the one backdoor the report-text guard cannot catch:
   iterating a tagger against test outcomes to smuggle in row-level inspection.

No model budget.

- **P1.1 — Frozen test450 risk–coverage replay.** Predeclared, aggregate-only port of P0.2
  to the holdout. Note the asymmetry: on test450 the cross-model-agreement leg degrades to a
  **two-agent** consensus (`..._two_agent_exact_test450_...`), so this is a *weaker* replay of
  the validation composite, not an identical one — state this wherever the test curve appears.
- **P1.2 — Per-family error-parity on frozen test450.** No-call re-score producing a
  per-family parity slice on the holdout, family-tagging the 450 rows with the *frozen
  validation classifier* per invariant 2 above.

### Phase 2 — Fresh model budget (gpt-4.1-mini; small, targeted)

Full gpt-4.1 budget is exhausted; all Phase 2 work is on mini and is cheap. One item is the
genuine research swing.

- **P2.1 — Semantic entropy over multi-sampled structured events** *(Consistency, Calibration, Abstention). THE RESEARCH SWING. NOW FIRING — Phase 0 left Consistency at 2/5 and the user directed that self-consistency use varying temperatures.*
  Sample the structured-event extractor k=4–5× over validation750 at **varying temperatures**
  (e.g. 0.3 / 0.5 / 0.7 / 1.0 — **not** a single fixed temperature, and never temp-0, which only
  re-measures the P0.8 reproducibility result) (≈3,000–3,750 short mini calls; a few dollars; one
  resumable overnight run via `run_resume.py`). Compute
  semantic entropy per row at **two levels on the same samples**: *primary* over the rendered
  Purist category (what abstention acts on), and *secondary* over the selected event kind
  (`frequency`/`seizure_free`/`unknown`, a more sensitive probe of upstream wavering that
  rendering can mask). **Both hypotheses are predeclared and publishable:** H1 — entropy is high
  precisely on the unknown-vs-rate residual (last-event / provoked / "since" rows) → it is a
  forward-observable abstention signal the honest-ceiling analysis declared absent (it examined
  *single*-sample features only) → the wall cracks; H0 — entropy is flat/low at the residual →
  the documented over-reading is **confident, not uncertain**, which is *why* no abstention
  signal can catch it → the wall is real and now has a mechanism. The two-level design keeps the
  null informative: flat label-entropy but live kind-entropy localizes the wavering; both flat
  is the strongest version of the wall. **Hard gate before the full run: a 25-row degeneracy
  pre-flight** — if exact-evidence gating makes temperature sampling return identical samples,
  entropy is degenerate everywhere and the experiment is answered cheaply before the validation750
  spend. Must also pass a predeclared hard-negative + OOD panel (rule-designer /
  generalization-adversary discipline) before any holdout consideration. Feeds the external
  score in P0.3.

- **P2.2 — Telemetry-instrumented re-pass** *(Operational reliability).*
  Enable DSPy/LiteLLM usage tracking + per-call `perf_counter` over the surviving primitives
  (~125–450 rows). Replaces the offline estimates from P0.7 with measured per-call
  cost/token/latency/retry. ≈$0.50–2 on mini.

- **P2.3 — (Optional) Paraphrase-invariance on real test rows** *(Robustness).* Freeze-warden
  gated; ~450 rows × 3–5 paraphrase prompts; measures label-flip rate on the actual benchmark.

- **P2.4 — (Optional) Entailment judge / verbalized-confidence re-elicitation.** Sampled NLI
  pass (cited span → label) and/or 0–100 confidence re-elicitation; only if P0.3 leaves the
  calibration story thin.

---

## Part III — Phase 0 Execution Results (2026-06-17)

Phase 0 ran in full at zero model budget. Each task is a deterministic driver
(`experiments/build_gan2026_reliability_p0_*.py`) over the frozen artifacts,
reading the canonical `v0_reference` subject layer; outputs are paired `.json` +
`.md` in `experiments/`. Shared loaders/metrics live in
`artifact_analysis/reliability_common.py`. The consolidated result is
`experiments/gan2026_reliability_master_scorecard_2026-06-17.md`.

| # | Dimension | Cov. (was→now) | Computed metric |
|---|-----------|:--:|-----------------|
| 1 | Task correctness | 4/5 | Subject Purist 0.881 val / 0.809 test; risk–coverage AUC 0.040 |
| 2 | Factuality | 3/5 | Unknown-gold over-read 9.4% val / 12.7% test |
| 3 | Faithfulness | 5/5 | Subject faithfulness 92.1% val / 92.9% test; faithful-but-wrong 80/80 `[comparator: 703/750, 423/450]` |
| 4 | Calibration | 2/5→3/5 | Self-confidence degenerate (98.5% one bucket); external ECE 0.080, Brier 0.102, failure AUROC 0.781 |
| 5 | Abstention | 4/5→5/5 | Full curve, AUC 0.040 (oracle 0.007); selective risk 3.0%@50% cov, 7.8%@80% |
| 6 | Robustness | 4/5 | Index 0.547 / 0.694 / 1.000 (v0.5 / v0.6 / v0.7); overfit gap the diagnostic leg |
| 7 | Consistency | 3/5→2/5→**4/5** | P0.8 temp-0 reproducibility (unanimous acc 0.689) + **P2.1 varying-temperature semantic entropy** (mean label entropy 0.012; residual 0.018; band_unknown 0.000) |
| 8 | Safety & compliance | 4/5 | 0 C→W selective floor; gate v0_9; canaries + hash pin + readout guard |
| 9 | Fairness | 3/5 | Per-band error spread 7.8%, CV 0.032; worst subgroup `seizure_free_duration` |
| 10 | Operational | 3/5→4/5 | 0 model render failures / 5,483 recoverable repairs / 1,950 rows; ~$1.16/1000 notes (est); latency+retry still blocked |

**Findings worth flagging.**
- The **P0.2 risk–coverage curve** is the headline: the predeclared External Risk
  Score (cross-model agreement + residual-shape flags + ambiguity count) ranks
  errors with **AUROC 0.781** and yields a smooth, monotone selective-risk curve.
  The wall reading is nuanced: external features *do* shed recoverable error, while
  the irreducible core is the confident-agreement over-reading (1 error even among
  the 121 safest risk-0 rows).
- **Subject faithfulness (92.1% / 92.9%)** is genuinely lower than the full-gpt-4.1
  V12 `final` comparator (703/750, 423/450) — decision 0018's re-derivation matters.
  Evidence-validity barely predicts correctness (84.7% vs 88.4%), reinforcing the
  faithful-but-wrong thesis.
- **Two corrections were applied during execution.** (a) `parse_errors` logs
  *recoverable* deterministic repairs, not failures — true model render failures are
  0; the 6 un-rendered rows are unscorable-gold exclusions. Parse-repair count is a
  weak-but-real error signal (AUROC 0.60), not the "non-signal" first drafted.
  (b) Per user direction, **self-consistency must use varying temperatures**; the
  temp-0 hard50 only measures reproducibility, so Consistency is honestly scored
  **2/5** and P2.1 fires (now run; restores Consistency to 4/5).

## Part IV — Phase 1 & Phase 2 Execution Results (2026-06-17)

**Phase 1 (freeze-warden-gated, no new model calls).** Both holdout ports are
aggregate-only (0 forbidden markers) with hash-frozen transforms predeclared
before touching test450.
- **P1.1 risk–coverage (two-agent leg only — weaker port, decision 0018):** test450
  base error 19.1%; abstaining the agent-disagreement set lifts the covered majority,
  cutting selective risk to **12.2%** at 65.8% coverage; two-agent failure AUROC
  **0.648** (< validation 0.781, by construction).
- **P1.2 per-family parity (frozen validation classifier):** overall 0.812, band error
  spread **19.9%** (sharper than validation's 7.8%); worst band `band_submonthly` 69.5%
  (flagged). Confirms the validation picture — disparity in rate bands + over-reading
  families, not `band_unknown`.

**Phase 2 — P2.1 semantic entropy (THE RESEARCH SWING; varying temperatures
0.3/0.5/0.7/1.0 on gpt-4.1-mini).** The 25-row degeneracy preflight, then a 150-row
residual-enriched tier (23 residual rows), were run resumably. **Result: H0 — the
over-reading is confident, not uncertain.**
- Raw model prose genuinely varies across temperatures (different text/length per
  sample — sampling is real, not cached), but the **rendered Purist label and selected
  kind do not move**: mean label entropy **0.012**, only 4/150 rows show any label
  variation, and the residual is *no more uncertain than the rest* (residual label
  entropy 0.018 vs non-residual 0.011; **`band_unknown` = 0.000**, perfectly stable).
- This is a publishable null that **converts the closeout's negative result into a
  mechanism**: self-confidence is degenerate (P0.3), self-consistency is chance-level
  (P0.8), and sampling entropy is flat at the residual (P2.1) — three independent
  self-signals all fail to flag the unknown-vs-rate over-reading because the model
  *confidently commits* to the same category regardless of temperature. The wall is
  real, and the only signal that crosses it is **external** corroboration (P0.2/P0.3).
- The full validation750 × 4-temperature run (~3,000 calls, ~5 h sequential) was
  **not** spent: the degeneracy gate exists precisely to avoid a confirmation-only
  spend once decisions are shown temperature-stable on a residual-enriched sample.

## Recommended sequencing

Do **all of Phase 0 first** — it populates the entire ten-dimension scorecard, costs nothing,
and likely is the paper's backbone on its own. Within Phase 0, **P0.2 (risk–coverage curve)**
is the single highest-leverage artifact: it simultaneously upgrades Abstention to a full
curve and gives Calibration its first real failure-prediction number. Then, **only if Phase 0
leaves the calibration/abstention story thin**, run **P2.1 (semantic entropy)** as the one
fresh experiment with genuine upside — it is the only unrefuted, reliability-native route at
the residual and is a genuine *falsification test* of the project's central negative result
(its null is as publishable as its hit). Phase 1 and the remaining Phase 2 items are
completeness work that can follow as needed.

The narrative this produces: *a clinical extractor that knows what it cannot extract* —
the literature review's thesis (reliability is engineered through grounding, verification,
calibrated abstention, and governance) instantiated on a real benchmark.

---

## Source

- Four-agent deep evidence audit, 2026-06-17 (Grounding / Uncertainty / Robustness+Fairness /
  Systems clusters). All artifact paths and numbers verified against logged JSONL.
- ``
- `docs/literature/llm_reliability_literature_review.pdf` (§3 core dimensions)
- Key artifacts: `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl`,
  `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl`,
  `experiments/gan2026_robustness_battery_v1*_gpt41mini_2026-06-15.json`,
  `experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl`,
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/{fresh_evidence_reasoner,family_transitions,family_cv_promotion}.py`,
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/{frozen_test_preflight,frozen_test_readout,llm_pipeline_cli}.py`,
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/rq8_telemetry_guard.py`.
