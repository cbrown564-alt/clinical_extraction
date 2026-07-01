> **Status: ACTIVE** — open work tracked in [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md).

# Plan — Strengthen ExECTv2 calibration and abstention/review-routing

Status: **PROPOSED, not started.** Owner: ExECTv2 reliability track. Date: 2026-07-01.

Follows from: `docs/research/paper_claims_evidence_review_2026-07-01.md` §"Why
Calibration and Abstention/Review-Routing Get Their Own Plan." Companion plan:
`manuscript_evidence_gaps_closure_plan_2026-07-01.md` (its Phase 5 owns only the
manuscript-framing fix for this gap; this plan owns the actual research).

## 1. Why this exists

The manuscript's reliability scorecard (§4.4) reports the weakest evidence in the paper
on exactly the dimension the reliability thesis treats as one of its two pillars
("knows when it is wrong," `reliability_thesis.md` §1):

- Calibration: Brier `0.2245` vs. constant-base-rate `0.2387` — a real but tiny
  improvement (Δ = `0.0142`), ECE `0.0432`.
- Abstention/review-routing: current triggers fire on **96.6%** of cells to catch
  **90.4%** of errors (`PROJECT_STATUS.md`) — a "review nearly everything" policy, not a
  usable low-burden one. The manuscript states plainly: "no promoted low-burden triage
  policy."
- On the single slice where a working signal would matter most (the binding
  gold-`unknown` over-read cases), the best AUROC across every forward-observable
  feature tried is `0.676`, below the paper's own `0.70` usefulness bar (H0 retained).

This is not for lack of data. Verified directly against the code and artifacts on disk,
three signal sources already exist, are already computed, and are **not** in the current
calibration feature set or review-routing trigger set:

1. **Cross-model agreement** (GPT-4.1-mini / DeepSeek chat / Qwen 3.6 35B, same-core
   architecture, same dev140 letters — `exectv2_same_core_model_swap_dev140_20260625.*`).
   This signal is used *once*, narrowly, inside the SF-only wall-transfer probe, where
   the agreement leg alone reaches AUROC **0.7613** for ranking SF errors — already
   higher than what the whole-corpus calibration rule's Brier improvement implies is
   achievable. It has never been computed for Diagnosis, Prescription, or Investigations,
   and is not a feature in `_CALIBRATION_FEATURES`. The manuscript's own "Do Not Use As
   Claims" list states this outright: "Cross-model agreement is a validated ExECTv2
   reliability signal (unused; available artifact)."
2. **Self-consistency / sampling entropy** at four temperatures on dev140
   (`exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_{r1..r4}_*_2026-06-25.*`)
   plus a temp-0 reproducibility check on a hard-50 slice. Currently folded only into a
   single aggregate "Consistency" scorecard number (`0.8857` dev140, `0.9217` hard-50);
   never used as a per-letter or per-cell feature.
3. **Evidence support-quality** (does the cited evidence actually support the *specific*
   claimed value/status/temporality, not merely that the quoted text is locatable in the
   note) — `experiments/exectv2_evidence_support_audit.py`, built 2026-06-30, closing the
   FM1 guardrail that was previously "Partial." This has never been tested as a
   calibration or routing feature at all; it is brand new.

The current calibration rule's feature set (verified in
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/reliability/constants.py`,
`_CALIBRATION_FEATURES`) is: family one-hots, `evidence_invalid`, `low_confidence`,
`source_final_delta`, `active_rate`, `plan_language`, `result_state`,
`deterministic_action_count`, `prediction_count`. None of the three signals above appear.
The review-routing trigger set (`review_routing.py`'s `review_triggers`) is a hand-built
OR-of-boolean-conditions gate; `review_operating_points` already has risk-coverage-sweep
scaffolding, it has simply never been fed a better-ranked composite risk score. This plan
closes that gap directly: add the three signals to the calibration feature set, re-fit,
re-measure Brier/ECE, then re-rank `review_operating_points` on the improved score and
look for an actual low-burden operating point.

## 2. Predeclared hypotheses and what would falsify them

Stated before any new analysis is run, per the project's standing discipline.

- **H1 (cross-model agreement generalizes).** A per-letter/per-cell cross-model agreement
  feature, computed the same way as the wall-transfer probe's leg #1
  (`3 - cross_model_agreement_count`, or the raw agreement count itself) but extended to
  all four families on dev140, improves calibration (lower Brier, lower ECE) and/or error
  ranking (higher AUROC) versus the current feature set, on at least two of the three
  non-SF families. **Falsified if:** adding the feature does not move Brier/ECE outside
  the existing cross-validation fold variance, or the AUROC gain is concentrated in SF
  only (i.e., the wall-transfer probe's result does not generalize and this was a
  family-specific artifact, not a transferable signal).
- **H2 (self-consistency entropy adds orthogonal signal).** A per-cell self-consistency
  entropy feature (computed from the existing 4-temperature dev140 reruns, joined back to
  the base-temperature cell) is not redundant with cross-model agreement — i.e., it
  catches a different subset of errors (low cross-model agreement does not imply high
  self-consistency entropy and vice versa) and improves the combined model over either
  alone. **Falsified if:** the two features are highly correlated (e.g., Spearman ρ >
  0.7) and the combined model's improvement over the better single-feature model is
  within noise.
- **H3 (evidence support-quality adds signal beyond groundedness).** The new
  support-quality score (distinct from the existing `evidence_invalid` groundedness flag,
  which is already in the feature set) improves calibration/ranking beyond what
  groundedness alone captures — i.e., the FM1 distinction (grounded-but-wrong vs.
  grounded-and-right) is itself predictive. **Falsified if:** support-quality is highly
  correlated with the existing `evidence_invalid`/`low_confidence` features and adds no
  measurable lift.
- **H4 (a usable low-burden operating point exists once the score is better-ranked).**
  Re-ranking `review_operating_points` on the improved composite score (H1+H2+H3
  combined, whichever survive) yields at least one operating point materially better than
  the current rule-based router's (burden 0.9661, catch 0.9037) — concretely, the kill
  bar is **catch ≥ 0.75 at burden ≤ 0.50** (catch three-quarters of errors while reviewing
  half the cells or fewer), chosen because it would be a genuinely different and useful
  policy shape, not because it is guaranteed achievable. **Falsified if:** no operating
  point on the new risk-coverage curve clears this bar — report the best achievable
  point honestly as a negative/bounded result, the same way the wall-transfer probe
  reported its binding-slice null.
- **The irreducible plateau is not a target for this plan.** The wall-transfer probe
  already established that the binding gold-`unknown` over-reads have no gold-free
  separator (best AUROC 0.676, H0 retained, pre-registered). This plan does **not**
  re-attempt to crack that specific slice — relitigating an already-clean, already
  pre-registered null would violate the project's evaluation discipline (the same
  discipline C5 in the manuscript credits as the durable contribution). This plan's H4
  targets the *recoverable majority* of risk outside that slice; if H4 succeeds, the
  manuscript should explicitly report both numbers side by side: "a working triage
  policy now exists for N% of error mass; the remaining irreducible M% (the binding
  gold-unknown slice) still has no gold-free separator and is reported as a structural
  limit, not a triage failure."

## 3. Scope and inspection boundary

- **Development surface: dev140 only**, for all feature construction, fitting, and
  the H1-H4 decision points. This matches every other row-level analysis already done in
  this project (Dx/SF canonical row analyses, EV-recall consolidation checks) and avoids
  any full-200/holdout row-level inspection question.
- **Confirmatory step: full-200 aggregate-only**, mirroring how Table R2/R3 numbers are
  always dev140-developed then full-200-aggregate-confirmed. The final phase recomputes
  the *aggregate* Brier/ECE/risk-coverage AUC on full-200 using the dev140-fitted scoring
  rule (no re-fitting on full-200, no row-level full-200 inspection) — the same protocol
  the existing `calibration_proxy` function already uses for its dev140-vs-full200
  separation.
- **Zero new LLM calls.** Every feature in H1-H3 is computable from artifacts already on
  disk (`exectv2_same_core_model_swap_dev140_20260625.*` and its underlying per-model
  prediction caches keyed by `candidate_id`; the four self-consistency temperature runs;
  the 2026-06-30 evidence support audit). If any feature turns out to require data not
  actually present in these artifacts (e.g., per-letter raw predictions are not
  separately cached for one of the three same-core models), stop and report that as a
  scope finding rather than triggering a new model run under this plan.
- **No changes to the production scoring path** (`reliability_scorecard.py`'s
  callers, or any non-reliability scoring code) — this plan only touches the
  `reports/reliability/{calibration,review_routing,scoring,constants}.py` module group
  and adds new feature-construction code alongside it.

## 4. Phases

### Phase 0 — Locate and validate the three raw signal sources

Before building anything, confirm each signal is actually joinable to the existing
dev140 reliability cells at the per-letter/per-family granularity `calibration_proxy`
operates on.

- **Cross-model agreement:** locate the per-letter prediction caches for each of the
  three `candidate_id`s in `exectv2_same_core_model_swap_dev140_20260625.jsonl`
  (`exectv2_2call_no_sf_adjudicator_{gpt41mini,deepseek,qwen36}_dev140`). Confirm a
  shared letter-id join key exists across all three (the same letters, same order or
  joinable by id) and that the join recovers a non-trivial agreement distribution
  (not degenerate at agreement=3 for every cell, which would make the feature useless by
  construction — the wall-transfer probe's SF-only read already showed a real spread, so
  this is a sanity check, not expected to fail).
- **Self-consistency entropy:** confirm the four temperature-run JSONs
  (`exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r{1..4}_*_assembly.json`)
  carry a stable per-letter id joinable back to the base dev140 cell set, and that a
  per-letter entropy statistic (e.g., label/state agreement fraction across the 4 runs,
  analogous to the Gan P2.1 semantic-entropy construction) is computable per family, not
  just in aggregate.
- **Evidence support-quality:** confirm `exectv2_evidence_support_audit_2026-06-30.json`
  is keyed at a granularity (mention/cell level) that can be aggregated up to the same
  cell unit `calibration_proxy` scores on.
- **Gate:** write a short validation note (can be a code comment plus a printed summary,
  not necessarily a full house-style doc) confirming all three joins work and reporting
  the raw distributional sanity checks (e.g., agreement-count histogram, entropy
  histogram, support-quality score histogram) before any feature is added to the
  calibration rule. If any one signal fails to join cleanly, scope that signal out and
  proceed with the other two — do not block the whole plan on one signal's data-shape
  surprise.

### Phase 1 — Extend cross-model agreement to all four families (H1)

- Compute, per dev140 cell, an agreement feature analogous to the wall-transfer probe's
  leg #1: size of the largest identical-output cluster among the three models for that
  letter/family (or, if outputs are not directly comparable across models'
  `clinical_headline` representations, a normalized concept-overlap agreement score —
  use whichever the wall-transfer probe's existing code
  (`build_exectv2_sf_wall_transfer_probe_extended.py`) already implements for SF, ported
  to the other three families rather than reinvented).
- Add the feature to `_CALIBRATION_FEATURES` (or a parallel candidate-feature list, to
  keep the change reviewable/revertible) and re-run `calibration_proxy`'s grouped 5-fold
  CV on dev140 with the feature included.
- Report, per family and pooled: Brier with vs. without the feature, ECE with vs.
  without, and a standalone AUROC for the feature alone (ranking error vs. correct),
  matching the wall-transfer probe's existing reporting format for direct comparability
  to its SF-only 0.7613 figure.
- **Apply H1's falsification test** as written in §2 before proceeding to Phase 2.

### Phase 2 — Add self-consistency entropy and test orthogonality (H2)

- Compute a per-cell self-consistency feature from the four-temperature dev140 reruns:
  the simplest defensible construction is the same state/label-agreement-fraction-across-runs
  metric Gan's P2.1 probe used, applied per ExECTv2 cell rather than per Gan label.
- Before adding to the calibration rule, compute the correlation between this feature and
  Phase 1's cross-model agreement feature (Spearman ρ, or simple cross-tab if both are
  effectively discrete/low-cardinality). Report this number explicitly — it is the
  falsification test for H2, not an incidental diagnostic.
- If not disqualified by the correlation check, add to the feature set alongside Phase
  1's surviving feature(s), re-run the grouped CV, and report the combined model's
  Brier/ECE/AUROC versus Phase 1's single-feature model.

### Phase 3 — Add evidence support-quality and test against the groundedness baseline (H3)

- Compute a per-cell support-quality score from `exectv2_evidence_support_audit_2026-06-30.json`,
  aggregated to match the cell unit.
- Check correlation against the existing `evidence_invalid` feature already in
  `_CALIBRATION_FEATURES` (the falsification test for H3).
- If not disqualified, add to the cumulative feature set from Phases 1-2 (whichever
  survived), re-run, report cumulative Brier/ECE/AUROC.

### Phase 4 — Re-rank review-routing on the improved composite and search for a usable operating point (H4)

- Replace (or run alongside, for comparison) the current rule-based `review_triggers`
  OR-gate with a ranked threshold on the cumulative calibrated-confidence/risk score from
  Phases 1-3, feeding `review_operating_points`' existing coverage-sweep mechanism.
- Plot/report the full risk-coverage curve (burden vs. catch-rate) on dev140, and
  identify the best operating point, with explicit comparison to the current rule-based
  router's single point (burden 0.9661, catch 0.9037).
- **Apply H4's kill bar** (catch ≥ 0.75 at burden ≤ 0.50) exactly as predeclared in §2.
  Report the actual best point regardless of whether it clears the bar — a near-miss
  (e.g., catch 0.70 at burden 0.50) is still a materially more useful finding than the
  current degenerate router and should be reported as a real improvement even if it
  doesn't clear the predeclared bar; only the *headline framing* ("a usable low-burden
  policy now exists" vs. "burden was reduced but no policy clears the usefulness bar")
  depends on the bar.
- Explicitly separate this curve's reading from the binding gold-`unknown` slice: report
  what fraction of total error mass that slice represents (the wall-transfer probe gives
  this: 5 over-reads out of dev140's error population) and confirm the new operating
  point's catch-rate accounting either includes or excludes that irreducible slice
  transparently, so the H4 result cannot be read as having "solved" the slice the
  wall-transfer probe correctly left open.

### Phase 5 — Full-200 aggregate confirmatory read

- Using the dev140-fitted scoring rule (features and any logistic weights) from whichever
  of Phases 1-3 survived, recompute aggregate-only Brier/ECE on full-200 (no row-level
  full-200 access — only the aggregate calibration statistics, exactly as
  `calibration_proxy`'s existing `validation_status` field already documents for the
  current rule).
- Recompute the full-200 aggregate risk-coverage AUC for the new composite, compared to
  the current full-200 reliability scorecard's reported AUC (`0.040`, oracle `0.007`).
- **This is a confirmation, not a re-fit.** If the full-200 aggregate numbers diverge
  substantially from the dev140 read (e.g., Brier improvement collapses), report that
  divergence honestly as a generalization-gap finding — do not re-fit on full-200 to
  chase agreement, which would violate the aggregate-only inspection policy's spirit even
  if not its letter.

### Phase 6 — Write-up and manuscript propagation

- One house-style doc,
  `docs/experiments/exectv2/reliability/exectv2_calibration_abstention_strengthening_<date>.md`,
  reporting all four hypotheses' verdicts (H1-H4), the Phase 0 data-validation notes, and
  the Phase 5 full-200 confirmatory numbers.
- Manuscript edit to §4.4 (Reliability Scorecard) and D.5 (Limitations): replace the
  current "Calibration is near-base-rate, not deployment-ready" framing with whatever the
  actual outcome supports — either a genuinely improved calibration story (if H1-H3
  deliver material Brier/ECE gains) or an honestly-reported negative result (if they
  don't), and likewise for review-routing's "no promoted low-burden triage policy" line.
  Do not pre-write this edit; it depends entirely on which hypotheses survive.
- Cross-link to `manuscript_evidence_gaps_closure_plan_2026-07-01.md` Phase 5, which
  should be re-checked once this plan concludes — if H4 succeeds, that plan's framing
  sentence (no working triage policy) becomes stale and needs a follow-up correction
  banner, the same pattern used throughout this project's research docs.

## 5. Non-goals

- No attempt to close the binding gold-`unknown` slice's pre-registered null (§2, "the
  irreducible plateau is not a target for this plan").
- No new LLM calls, no new GEPA work, no new model-swap runs — this plan is entirely
  replay/re-analysis over existing artifacts.
- No changes to the underlying extraction architecture, prompts, or assembly lenses —
  this plan only touches the reliability-reporting layer (calibration and routing code),
  not the system being measured.
- No full-200 or holdout row-level inspection.
- No re-opening of the Gan2026 calibration/abstention work (External Risk Score,
  P0.2/P0.3) — that strand is closed and out of scope; this plan only extends signals
  *within* ExECTv2.

## 6. Output summary

- Extended `_CALIBRATION_FEATURES` (or a clearly-separated candidate set) in
  `constants.py`, conditional on which of H1-H3 survive.
- A re-ranked review-routing operating-point report using the improved score.
- One new house-style experiment doc covering Phases 0-5.
- Manuscript edits to §4.4 and D.5, written only after Phase 5 concludes.
- A forward-link to `manuscript_evidence_gaps_closure_plan_2026-07-01.md` for the
  framing-correction this plan's outcome may require there.
