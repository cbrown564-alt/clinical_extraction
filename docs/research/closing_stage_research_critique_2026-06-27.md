# Closing-Stage Research Critique: Gaps, Suspicions, and Decomposition-Enabled Ideas

Date: 2026-06-27

Status: analysis-only review of the draft research report and the body of work
behind it. Written at the request to ask, before close: *did we miss anything;
are any findings suspicious; were pointed-to threads left unfollowed; now that
the architecture is decomposed, is there a better way to report this; and does
the decomposition spark new ideas?* This document proposes no edits to results,
authorizes no holdout or full-200 row-level inspection, and reopens no Gan
accuracy-optimization freeze. It is a reviewer's read, grounded in the primary
artifacts cited at the end.

## Bottom Line

The Gan 2026 strand is genuinely rigorous and its central negative result (The
Wall, plus the P2.1 semantic-entropy falsification that returned a clean,
publishable null) is the strongest, most novel thing in the paper. The exposure
is on the **ExECTv2 side and the cross-task seam**, and it traces to one root:
**the project's stated success criterion changed mid-stream, and the manuscript
does not own that change.** `reliability_thesis.md` §7 sets the minimum bar as
"beat the ExECTv2 per-item/per-letter F1 benchmark" (`0.87/0.90`); the manuscript
headlines a different metric (`clinical_headline` recovery, `0.85`) on a
non-comparable surface and fences off the strict comparison. The like-for-like
number exists and is `0.3877` per item on dev140 — and the project's own analysis
says that gap is closeable fidelity engineering that was deprioritized, **not** a
broken benchmark. Closing the paper without reconciling this is the primary risk.

## What Is Solid (so the critique is calibrated)

- **Gan honest-ceiling analysis.** The `0.842` wall is well-characterized: the
  selector oracle is exhausted (739/750), the binding residual has no
  Purist-correct component, and the distinguishing signal is absent from every
  forward-observable feature.
- **P2.1 semantic entropy was run to conclusion**, not left dangling. Varying
  temperatures (0.3/0.5/0.7/1.0), degeneracy preflight, residual-enriched tier;
  result H0 (mean label entropy `0.012`, `band_unknown` `0.000`): the over-reading
  is *confident*, which is the mechanism behind the wall. This is a model
  falsification test, not a reframe.
- **Evaluation discipline.** Held-out-family CV that refused the validation
  winner, the predeclared adversarial battery, contamination canaries, frozen
  aggregate-only audits, decision-effect component attribution. The Gan closeout's
  Part III correctly identifies *this discipline* — not the score — as the durable
  contribution.

The points below are where the closing report is weaker than the work deserves.

---

## 1. Did We Miss Anything? — The Headline Claim Changed and the Paper Doesn't Say So

`reliability_thesis.md` §7: **minimum** = beat the ExECTv2 `0.87/0.90` benchmark
with at least one architecture; **target** = beat it with all three canonical
architectures and a clean three-way comparison. The manuscript delivers neither
and substitutes a different metric without narrating the substitution. Four
concrete gaps:

### 1a. The strict-benchmark number is absent from the manuscript
The ExECTv2 results draft contains no `0.87`, no `0.90`, no "per-item/per-letter,"
not even as the diagnostic it claims to retain. Yet the number exists:
`exectv2_benchmark_surface_overall_2026-06-18.md` reports the only like-for-like
read as **`0.3877` per item / `0.6972` per letter (dev140)** — ~45% of the paper's
per-item headline. A reader who reads the thesis then the results will notice the
target quietly disappeared.

### 1b. The "it's a target-construction artifact" defense is weaker than the project's own analysis
The metric pivot is justified internally by an oracle/artifact framing (scattered
across `exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md` — itself a
**60-row checkpoint explicitly labeled "not a frozen audit conclusion"** — and the
gold-representation principles). But the cleaner 06-18 like-for-like note
contradicts the "broken metric" story: *"The published `0.87` was a rule-based
pipeline tuned precisely to reproduce those bundles… the loss is concentrated in
the with-CUI and attribute-bundle strictness, not in concept recall… If the
benchmark headline is a goal, the lever is deterministic phrase/CUI and
attribute-bundle fidelity, not more LLM adjudication."* In other words, the gap is
**closeable engineering that was deprioritized**, not an artifact of a
mis-specified target. The honest reconciliation — and the more defensible claim —
is: *we evaluate on a label-based surface because spelling correction drifted the
gold offsets (thesis §5), so the published offset-tuned number is not reproducible
on our surface; on the comparable surface we reach `0.39`, and closing that gap is
deterministic-fidelity work we chose not to spend on.* That is a reviewer-proof
statement. "Their metric is an artifact," asserted by the team that couldn't hit
it, is not.

### 1c. The promoted architecture is *worse* than rules on the only comparable surface
Same 06-18 note: stacking the hybrid verifiers lowers the benchmark overall from
deterministic-only `0.3687` to all-hybrid `0.3100`; for SeizureFrequency the
hybrid collapses its benchmark cell from `0.692` (rules) to `0.347`. The LLM
clinical-recovery gains that drive the `0.85` `clinical_headline` story are
**orthogonal to, and for SF antagonistic with, the benchmark surface.** The paper
should state this directly — it is a real and interesting finding (two surfaces,
two owners) — rather than let the surface choice quietly hide it.

### 1d. No ExECTv2 three-way comparison; the shared-core "dividend" is asserted, not measured
- The Gan three-way table (rules / LLM-only / hybrid) exists (manuscript Tables
  1–2). The ExECTv2 equivalent does not exist in paper form — only the hybrid
  assembly plus a model swap. The §7 *target* criterion is therefore unmet on
  task 2. (The pieces exist in code: `exectv2/deterministic`,
  `exectv2/llm/llm_only_*`; they were never assembled into the comparison.)
- The §7 *thesis-complete* criterion — "a shared core demonstrably reused across
  tasks" — is asserted. It is real at the primitives level (49 ExECTv2 modules
  import `core`/`tasks.shared`/`tasks.seizure_frequency`), but the SF *clinical
  machinery* — the declared "bridge" — is **re-implemented** under
  `exectv2/deterministic/sf_state_projection.py` and `…/rules/seizure_free.py`;
  `assembly/lenses/seizure_frequency.py` does not import the Gan SF normalizer. So
  "the same SF machinery runs on both tasks" is not literally true. Structural
  reuse is a fine claim; the paper currently implies more.

---

## 2. Findings That Look Suspicious

- **DeepSeek beats GPT-4.1-mini on ExECTv2 and is sidelined on a one-row
  technicality.** Table 5: DeepSeek `0.8596` vs GPT `0.8396` (dev140); Table 6:
  `0.8566` vs `0.8356` (full-200). DeepSeek is relegated with "one parse/schema
  failure." This reads as motivated selection — and it is self-defeating: DeepSeek
  being best is *strong* evidence for the model-agnostic-architecture thesis, but
  the manuscript presents it apologetically instead of leveraging it.
- **The Gan consensus/fresh v0.9 pass/fail is fragile and late.** Constrained:
  changed-label precision `0.5909` → **FAIL**; exact-source: `0.6000` → **PASS** —
  clearing the `0.60` bar by `0.0001`, while the *failing* variant had the *higher*
  net gain (`+19` vs `+16`). Two variants run on 2026-06-26, after the clean 06-17
  closeout; the one that barely passes enters the manuscript. Even with the careful
  "frozen aggregate, no tuning" fence, a reviewer sees a barely-passing late
  add-on at `0.60` precision (40% of changed labels wrong). Recommend asking
  whether this selector belongs in the paper at all: the closeout already settled
  the headline (single-SE `0.809`) and the ceiling (V12 `0.842`); this adds
  fragile complexity for a bounded `+16`.
- **ExECTv2 calibration looks better than it is.** ECE `0.0432` reads well, but
  Brier `0.2245` vs base-rate `0.2387` is a `0.0142` improvement — barely above
  predicting the base rate. The Gan strand's own sharper finding is that
  self-confidence is degenerate and only *external* corroboration carries signal.
  The ExECTv2 calibration line is presented more favorably than the Gan evidence
  licenses; verify the "grouped scoring rule" is not a post-hoc construct that
  flatters ECE.
- **SF-is-weakest is spun as corroboration rather than examined.** SF
  (`0.7525`–`0.785`) is the weakest ExECTv2 family *and* the declared transfer
  bridge. The manuscript explains it as "consistent with deep-reasoning
  difficulty." That is a *good* story if stated plainly ("the wall transfers
  too"), but as written the weakest family doubles as evidence for the thesis
  without the reader noticing the asymmetry.

---

## 3. Underexplored Threads the Findings Pointed To

- **The wall as a cross-dataset phenomenon (highest value).** Gan proved the
  unknown-vs-rate over-reading is confident and only external signal crosses it
  (P2.1). ExECTv2 SF is the same wall on a second schema — but it was never
  instrumented with the same forward-observable-feature probe. This is the most
  valuable unfollowed thread (see §5).
- **Cross-model agreement as the working signal, never applied to ExECTv2.** On
  Gan it was the strongest leg of the External Risk Score (failure AUROC `0.781`).
  The ExECTv2 model swap already produced three models' outputs; the agreement
  signal is sitting there unused as a reliability/abstention probe.
- **Benchmark-surface fidelity engineering, explicitly deferred.** The 06-18 note
  names the exact lever to approach `0.87` (deterministic phrase/CUI/attribute
  bundles for Prescription, Investigations, PatientHistory) and then stops at
  "Next Work, If Any." Either close some of it, or cite it as the named,
  quantified reason the strict surface is not the headline.
- **ExECTv2 component-impact evidence validation was "structurally inert" and not
  escalated to full-200.** The manuscript flags this and stops — an acknowledged
  hole in the component story.

---

## 4. A Better Final-Reporting Structure Now That It Is Decomposed

The manuscript is **task-first** (4.1 Gan, 4.2 ExECTv2) with reliability and
component subsections *duplicated* under each. Now that both tasks sit on one
decomposed, stage-owned spine, a **capability-first** spine is stronger and
matches what the contribution actually is:

1. The shared decomposed architecture (one figure, one spine).
2. *What the LLM adds* — the three-way comparison, both tasks side by side.
3. *What generalizes* — transfer + the wall, both tasks.
4. Reliability scorecard — unified dimensions across both tasks.
5. Component impact — one **unified stage-ladder figure** (already built for the
   Observatory laboratory page; lift it in instead of two separate tables).

This foregrounds the architecture and the evaluation discipline — the durable
contribution the Gan closeout itself identifies — rather than reading as two
parallel benchmark write-ups, one of which has no benchmark number.

---

## 5. New Ideas the Decomposition Sparks

- **Cross-task shared-component ablation — the modular dividend, finally
  measurable.** Turn *one shared component off* (the evidence-substring gate, the
  date-arithmetic policy, the SF normalization structure) and report the delta on
  **both tasks at once**. This is the concrete artifact behind the weakest-
  evidenced §7 criterion ("shared core demonstrably reused"). Today it is an
  assertion; the decomposition makes it a measurement. Highest-value new artifact;
  validation-side, within current protocols.
- **A task-neutral-vs-task-specific component map.** Every component ×
  {Gan, ExECTv2, shared-core} × portability category (general / clinical_epilepsy
  / task / dataset / benchmark_format). Now derivable from the code structure
  itself — it *is* Contributions 2 and 4 made concrete instead of narrated.
- **Reframe the wall as the cross-dataset headline.** Probe ExECTv2 SF with the
  same forward-observable features used on Gan and show the confident-over-reading
  wall reproduces on a second dataset and schema. This converts "SF is our weakest
  family" from an apology into the paper's strongest, most novel finding: *a
  clinical extractor whose limit is the task's, not the system's — and the limit
  transfers.* It also gives §2's SF-spin a real backbone.

---

## Recommended Priority Order

1. **(Submission blocker) Consolidate the benchmark-surface reconciliation** into
   one first-class subsection: report `0.3877`/`0.6972`, state the offset-drift
   non-reproducibility reason (thesis §5), name the closeable fidelity lever, and
   report the rules > hybrid benchmark inversion as a finding. Compute the
   like-for-like number on full-200 if a frozen aggregate read is authorized;
   otherwise label it dev140 throughout. Replace the dependence on the 60-row
   checkpoint.
2. **Build the cross-task shared-component ablation** (the §7 thesis-complete
   evidence). Validation-side, aggregate, no new freeze needed.
3. **Decide the consensus/fresh selector's fate** — keep it only if it survives a
   pre-registration check; otherwise cut it and let the closeout headline stand.
4. **Promote the model-swap finding** (DeepSeek ≥ GPT supports modularity) and the
   **wall-transfers** framing to first-class results.
5. **Tighten the calibration claim** to what the evidence supports (near-base-rate
   Brier; external signal, not self-confidence).

## Guardrail Compliance

Nothing recommended here requires holdout or full-200 row-level inspection, and
nothing reopens Gan accuracy optimization. The shared-component ablation and the
wall-transfer probe are validation-side/aggregate and aligned with the standing
ExECTv2 reliability-audit and Gan frozen protocols. The benchmark-surface
reconciliation is a reporting/consolidation task over already-produced aggregate
numbers; a full-200 like-for-like read remains gated under the existing standing
policy and is offered only as an option, not assumed.

## Source Artifacts (verified for this review)

- `docs/research/paper_manuscript_2026-06-26.md` (the draft report)
- `docs/research/exectv2_results_section_draft_2026-06-26.md`
- `docs/research/exectv2_benchmark_surface_overall_2026-06-18.md` (the `0.3877`
  like-for-like read; rules > hybrid inversion)
- `docs/research/exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md`
  (the 60-row checkpoint underpinning the artifact framing)
- `docs/design/reliability_thesis.md` (§5 offset drift; §7 success criteria)
- `docs/research/contribution_thesis.md` (experimental ontology; three families)
- `docs/research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`
- `docs/experiments/gan2026/reliability/gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md`
  (P2.1 result; External Risk Score; failure AUROC `0.781`)
- Code structure: `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/`
  (shared-core imports present; SF clinical machinery re-implemented, not imported
  from the Gan task)
- `PROJECT_STATUS.md`, `CONTEXT.md`
