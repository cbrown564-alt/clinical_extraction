> **Superseded for navigation —** canonical summary: [`PAPER_CANON.md`](PAPER_CANON.md). Claims register and provenance index; this file remains the detailed gap analysis. Full detail retained below.

# Paper Claims and Evidence Review (2026-07-01)

Status: analysis-only review of `docs/research/paper_manuscript_2026-06-26.md` (as it
stands after the 2026-06-30 Diagnosis gold-quality revision). Written to answer three
questions before further paper work: what is the manuscript actually claiming, how well
is each claim evidenced, and which gaps are load-bearing enough to need more robust or
more authoritative evidence before submission. This document proposes no edits to
results, authorizes no new holdout/full-200 row-level inspection, and reopens no frozen
gate. It is a reviewer's read, grounded in the primary artifacts cited throughout and
verified to exist on disk as of this writing. Two follow-up plans implement its
findings: `manuscript_evidence_gaps_closure_plan_2026-07-01.md` (items 1-5) and
`calibration_abstention_review_routing_strengthening_plan_2026-07-01.md` (the
calibration/abstention deep dive).

## Bottom Line

The manuscript is unusually self-disciplined for a paper at this stage: it already
carries explicit evidence-validity labels on every number, a claim-boundary table, and
a "Do Not Use As Claims" list that pre-empts most of the overclaiming a reviewer would
normally have to find themselves. That changes the nature of this review — most of the
soft spots below are things the manuscript itself names as bounded or as future work; my
contribution is ranking which of those self-flagged gaps are most consequential, plus
surfacing a few things the manuscript has not yet caught up to (a stale "future work"
claim that has since been executed, and an asymmetry in the model-agnosticity claim that
the abstract's framing soft-pedals).

The single biggest fact shaping how to read this paper: the original `reliability_thesis.md`
§7 success criteria (**minimum** = beat the published 0.87/0.90 benchmark with at least
one architecture; **target** = beat it with all three architecture families and a clean
three-way comparison; **thesis-complete** = both, plus a demonstrably shared cross-task
core) are **not met by the current manuscript on any tier**, and the manuscript has been
restructured around that fact rather than around hitting the original bar. That is a
defensible, well-evidenced pivot — but it is a pivot, and the paper's credibility now
rests heavily on the quality of the reconciliation argument (C1) rather than on a clean
benchmark win.

## What Is Solid

- **C2 (component ablation) and C4 (model-agnostic architecture)** rest on frozen
  full-200 aggregate reads with predeclared gates. I confirmed the underlying artifacts
  exist and match the numbers cited: `exectv2_same_core_model_swap_full200_20260625.json`,
  `exectv2_component_off_replay_full200_20260626.json`. These are the manuscript's
  cleanest claims.
- **C3 (the wall transfers)** is a genuinely pre-registered probe with a stated decision
  rule (AUROC ≥ 0.70 bar) decided before the result was read, and it returns an honest
  mixed verdict (6/9 checks, H0 retained on the binding slice) rather than being massaged
  into a clean positive. `exectv2_sf_wall_transfer_probe_2026-06-27.md` is more careful
  about its own limits (small-n caveat, "suggestive not definitive") than most papers'
  headline results are.
- **The evaluation discipline itself (C5)** — predeclared adversarial panels, held-out-family
  CV as a stop rule, frozen aggregate-only inspection — is real and demonstrated, not
  asserted; the v0.7 -106 regression catch is a concrete instance of the discipline doing
  work, not a hypothetical benefit.
- **The self-critique apparatus** (evidence-validity labels, claim-boundary table,
  "Do Not Use As Claims") is itself unusual rigor and should be preserved, not trimmed,
  in any future revision.

## The Claims, Ranked by Evidence Strength

1. **Strong:** C2 — evidence-validation gate inert (Δ=0.000 both tasks, confirmed
   2026-06-27 per item 2 below), and the post-processing format layers contribute a
   stable ~+0.04 across three qualitatively different LLMs.
2. **Strong:** C4 — DeepSeek (non-dev model) leads GPT-4.1-mini (dev model) by +0.021
   full-200, with the clinical-recovery base (pre-format-layer) advantage ruling out a
   pure formatting artifact.
3. **Strong but explicitly bounded:** C3 — wall mechanism transfers (External Risk AUROC
   0.764, 17.1% irreducible plateau, no gold-free separator on the binding slice), but
   the manuscript itself flags the binding-slice n as small (5 over-reads vs 25
   withholds on dev140) and calls the AUROCs suggestive, not definitive.
4. **Soft, highly load-bearing:** C1 — the gold-quality-ceiling argument that rescues the
   paper's headline ("we evaluate on a different surface because the benchmark gap is
   substantially gold noise, not model deficit") rests on row-by-row clinical
   adjudication performed by the same research pipeline whose output is being judged.
   This is the manuscript's most important single argument and its weakest-sourced one.
5. **Honestly weak and labeled as such:** calibration (Δ Brier 0.0142 over base rate,
   "not deployment-ready") and abstention/review-routing on ExECTv2 ("no promoted
   low-burden triage policy"). The thesis's reliability pillar is "generalizes" +
   "knows when it's wrong"; the first half is well evidenced, the second is thin on the
   broad task.

## Open Gaps, Ranked by Consequence

### 1. The thesis's "Target" tier (ExECTv2 three-way comparison) is measured now, but not written up

`docs/design/reliability_thesis.md` §7 requires beating the benchmark with all three
architecture families and a clean three-way comparison. The manuscript marks the
ExECTv2 three-way comparison an "acknowledged gap" (§2.3, S1). Independently of the
paper-writing track, the GEPA workstream (2026-06-27 → 2026-06-30, see
`PROJECT_STATUS.md` "GEPA workstream closed out") has since built and closed out exactly
this missing leg: single-pass LLM-only ExECTv2 plateaus at **~0.731** (gpt-4.1-mini) /
**~0.654** (Qwen 3.6 35B) `clinical_headline` F1 on dev140, **~0.18-0.19 below** the
hybrid ceiling (0.9155), and does not clear the published-benchmark surface either. This
*is* the thesis's missing three-way comparison — it is just a negative result, and it
lives entirely in `docs/research/` GEPA documents, not in the manuscript. The completion
of the measurement is good news for the paper's honesty; the absence of the write-up is
the gap.

A real subtlety the closure plan must get right: the GEPA workstream's own root-cause
story for the 0.731→0.9155 gap ("producer evidence-recall, not verify/arbitrate stages,"
per `exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`) has itself been
partially revised by the 2026-06-30 EV-recall consolidation re-examination
(`docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md`):
of the families checked, Diagnosis's evidence-recall shortfall is 93.5% H-inflated
(consolidation/gold-multiplicity artifact, not genuine retrieval failure), SeizureFrequency
is 61-83% H-inflated, Prescription barely crosses the inflation threshold (52.2%) via a
different mechanism (transcription-typo substring breaks), and Investigations is a clean
genuine-retrieval negative (26-30% H-inflated only). So "producer evidence-recall" is
real for Investigations and substantially genuine for Prescription, but mostly an
artifact of the same gold-multiplicity convention as C1 for Diagnosis and SF. Any
manuscript propagation of the GEPA ceiling must carry this corrected, per-family
attribution rather than the workstream's earlier blanket "evidence-recall" framing —
otherwise the paper would import a root-cause claim its own later analysis already
revised.

*Source: `PROJECT_STATUS.md`; `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`
(status-corrected); `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md`.*

### 2. The manuscript's own "future work" claim for S1 is stale

D.5 (S1) states: "the shared-component ablation that would measure the cross-task
dividend... is predeclared... but not yet executed at cross-task scope." This is no
longer true. `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`
(generated the day after the manuscript outline, 2026-06-27) already ran it: the
`evidence_validation` gate is inert on **both** tasks (Δ=0.0000 ExECTv2 dev140, Δ=0.0000
Gan2026 validation750), and `standard_dictionary`/Gan `normalize` shows positive
cross-task contribution (+0.0389 ExECTv2, +0.0293 Gan). This is a real, measured,
*positive* cross-task dividend result sitting unused — exactly the kind of evidence S1
says doesn't exist yet. Folding it in upgrades C2 from a single-task finding to genuine
cross-task evidence and removes a true-when-written-but-now-false sentence from the
Limitations section. This is the cheapest, lowest-risk item in either plan: no new
analysis, just propagation, and I verified the source artifact exists and the numbers
are internally consistent with Table R2/R3.

*Source: `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`.*

### 3. C1's gold-quality-ceiling argument has a circularity exposure

The Diagnosis (F1 0.6617→0.9501) and SeizureFrequency (62.1%→89.3%) gold-quality
adjudications are the manuscript's single most important rescue of its "didn't beat the
benchmark" headline. Both were performed by the project's own research pipeline: the SF
pass was "one coherent pass," the Diagnosis pass was "five independent reviewers without
cross-checking between batches" (manuscript's own caveat, §4.1.2). Neither involved a
blinded external clinician, and the same team that built the system being graded is also
the arbiter of which disagreements are "genuine" versus "gold artifact." The manuscript
is honest about this caveat in passing but does not address it structurally. Given how
much weight this argument carries (it is the difference between "didn't beat the
benchmark" and "beats it net of gold noise"), it is the gap most likely to draw hard
reviewer pushback, and the one most worth strengthening with an actual robustness check
(a blinded re-adjudication and inter-rater agreement statistic) even short of true
external clinical validation.

### 4. Model-agnosticity is asymmetric in a way the abstract underemphasizes

Table R3: GPT 0.8356, DeepSeek 0.8566, **Qwen 0.8197** — full-200 `clinical_headline`.
The abstract foregrounds "a non-development model (DeepSeek) leading the development
model" and the range "0.8356–0.8566," which quietly excludes Qwen's score from the
headline range even though Qwen ran under the identical frozen core and is one of the
three models the abstract says were tested. Qwen is explicitly excluded from any "leads"
claim in the "Do Not Use As Claims" list, but the manuscript never explains *why* the
open-weight model underperforms both closed models, nor whether the gap is uniform
across families or concentrated (which would change how alarming it is for the
model-agnostic thesis). Per-family numbers (Diagnosis 0.8307, SF 0.7020 — the family
floor of all nine cells in Table R3, Investigations 0.8503) suggest a roughly uniform,
modest shortfall rather than a collapse, but this has not been verified or written up.

### 5. No deployable "knows when it's wrong" signal for the hardest, most clinically important cases

On the binding gold-`unknown` slice (the cases where the model should withhold), the
best forward-observable AUROC is 0.676, below the paper's own 0.70 usefulness bar; H0 is
retained honestly. That is a correct, well-evidenced *negative* result and should stay
in the paper as such — but it means the transparency/reliability pillar currently has no
working triage policy for exactly the cases a clinician would most want flagged. This
item is scoped narrowly in the closure plan (tighten the manuscript's framing and make
the deployment-readiness gap explicit rather than implied) and handed off in full to the
calibration/abstention plan for any actual attempt to move the needle, to avoid the two
plans duplicating experimental work.

### 6. Logistics: the IEEE camera-ready draft is stale relative to markdown (not part of either plan below)

`PROJECT_STATUS.md` states the LaTeX draft under `literature/IEEE/` reflects only the
2026-06-26 manuscript state and has not been re-synced with the SF (06-29) or Diagnosis
(06-30) gold-quality revisions. This is a submission-readiness risk, not an evidence
gap, and is not included in either follow-up plan; flagging it here so it is not lost
before any camera-ready pass.

## Why Calibration and Abstention/Review-Routing Get Their Own Plan

Item 5 above is a symptom; the underlying cause is that the current calibration scoring
rule and the current review-routing trigger set are both shallow relative to data the
project has already paid for and is not using:

- **Cross-model agreement** (GPT/DeepSeek/Qwen on the same dev140 letters, same-core
  architecture) is used as a risk feature *only* inside the SF-specific wall-transfer
  probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`, AUROC 0.7613 for the agreement
  leg alone — already better than the whole-corpus calibration rule's Brier improvement
  suggests is possible) and is explicitly listed in the manuscript's own "Do Not Use As
  Claims" as "validated... (unused; available artifact)" for the other three families
  and the main scorecard.
- **Self-consistency / sampling entropy** across four temperatures already exists for
  dev140 (`exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_*_2026-06-25.*`)
  and a temp-0 reproducibility check exists for a hard-50 slice, but both are folded only
  into a single aggregate "Consistency" scorecard number (0.8857 / 0.9217); no per-letter
  entropy feature has been tried in the calibration rule.
- **Evidence support-quality** (does the cited evidence actually support the *specific*
  claimed value, not just that it is locatable in the note) was just built
  (`experiments/exectv2_evidence_support_audit.py`, 2026-06-30, closing the FM1
  guardrail) and has never been tested as a calibration feature at all.

I verified the current calibration feature set directly in
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/reliability/constants.py`
(`_CALIBRATION_FEATURES`): family one-hots, `evidence_invalid`, `low_confidence`,
`source_final_delta`, `active_rate`, `plan_language`, `result_state`,
`deterministic_action_count`, `prediction_count`. None of the three signals above are in
it. Similarly, `review_routing.py`'s `review_triggers` is an OR-of-rules gate (fires on
~97% of cells to catch ~90% of errors — a "review nearly everything" policy, not a
ranked, low-burden one); `review_operating_points` already has the scaffolding for a
risk-coverage sweep, it just has not been fed a better-ranked risk score. This is a
concrete, code-grounded opportunity, not a speculative one, which is why it gets its own
plan rather than being folded into the broader closure plan.

## Sources Consulted

- `docs/research/paper_manuscript_2026-06-26.md` (full read)
- `docs/design/reliability_thesis.md` (§§1, 2, 7)
- `PROJECT_STATUS.md` (2026-06-30 state)
- `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`
- `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_{full200,dev140}_2026-06-25.md`
  and underlying `.json`/`.jsonl`
- `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`
- `docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`
- `docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`
- `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md` and
  its four phase-result docs under `docs/experiments/exectv2/`
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/reliability/{calibration,review_routing,scoring,constants}.py`
- `experiments/exectv2_evidence_support_audit.py` and
  `docs/experiments/exectv2/reliability/exectv2_evidence_support_audit_2026-06-30.md`
