# Plan — Close the five named manuscript evidence gaps

Status: **PROPOSED, not started.** Owner: paper/manuscript track. Date: 2026-07-01.

Follows from: `docs/research/paper_claims_evidence_review_2026-07-01.md` (the analysis
this plan implements — read it first for the full evidence trail behind each item).
Companion plan: `calibration_abstention_review_routing_strengthening_plan_2026-07-01.md`
covers item 5's underlying research gap in depth; this plan only closes item 5's
*manuscript framing*, to avoid the two plans duplicating experimental work.

## 1. Why this exists

The closing review found five concrete, ranked gaps between what the manuscript
(`docs/research/paper_manuscript_2026-06-26.md`) currently says and what the project's
own evidence base actually supports as of 2026-06-30:

1. The thesis's "Target" tier (ExECTv2 three-way architecture comparison) has been
   measured by the GEPA workstream but never written into the manuscript.
2. D.5/S1 calls the cross-task shared-component ablation "not yet executed"; it was run
   on 2026-06-27 and the manuscript has not caught up.
3. C1's gold-quality-ceiling argument rests on adjudication performed by the same
   pipeline being graded, with no independent check on inter-rater reliability.
4. The model-agnosticity claim's abstract framing soft-pedals Qwen's uniform
   underperformance across all three closed/open models.
5. The "no deployable knows-when-it's-wrong signal" finding is real and correctly
   reported as a negative result, but the manuscript does not state plainly that this
   leaves the transparency pillar without a working triage policy on the broad task.

None of these require new model calls or new holdout/full-200 access beyond what is
already authorized. Items 1 and 2 are propagation of already-completed work. Items 3 and
4 require small, bounded new analysis. Item 5 is a framing fix only.

## 2. Scope and inspection boundary

- All work reads dev140 and validation750 development-split artifacts already on disk,
  plus the already-frozen full-200/test450 aggregate summaries cited in the manuscript.
- **No new full-200 or test450 row-level inspection is authorized by this plan.** If any
  phase below appears to need it, stop and write a fresh predeclaration (the project's
  standing practice — see `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md`
  for the template) rather than read rows under this plan's authority.
- No GEPA optimization runs, no new prompt tuning, no new LLM calls anywhere in this
  plan. Where a phase needs a number that does not yet exist as a replay artifact, the
  phase is scoped to flag that and stop, not to generate it ad hoc.
- Output is manuscript-markdown edits (`docs/research/paper_manuscript_2026-06-26.md`
  and its `docs/research/paper_drafts/` sources) plus, where new analysis is run, a dated
  doc under `docs/experiments/exectv2/` in the existing house style (self-validation
  gate, evidence-validity boundary, source artifacts list).

## 3. Phases

Ordered cheapest/lowest-risk first.

### Phase 1 — Propagate the already-executed cross-task ablation (item 2)

**Why first:** zero new analysis. The result already exists and is unambiguous.

- Read `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`
  in full (already done for the review doc; re-verify the two tables before editing
  anything).
- Edit D.5 (S1) in the manuscript: replace "the shared-component ablation... is
  predeclared... but not yet executed at cross-task scope" with the measured result —
  `evidence_validation` inert on both tasks (Δ=0.0000 ExECTv2 dev140 / Δ=0.0000
  Gan2026 validation750), `standard_dictionary`/`normalize` positive on both
  (+0.0389 ExECTv2, +0.0293 Gan). Keep the existing caveat language about the SF
  clinical machinery being re-implemented, not literally shared — that finding is
  separate and still true.
- Edit Contribution 2 (§6): upgrade its evidence-validity row from "dev140 replay-only...
  cross-task ablation scope is future work (S1)" to cite the executed cross-task result
  directly. C2's claim becomes genuinely cross-task, not single-task-with-a-promise.
- Edit the Claim Boundary Summary table (§4, end) and the Evidence Validity Summary
  (§6, end) to add a row for the cross-task ablation with its correct evidence-validity
  level (`validation-side, aggregate-only, no model calls, no new freeze` — copy
  verbatim from the source doc's claim-boundary line).
- **Self-check before committing:** confirm the two contribution-delta numbers quoted in
  the manuscript edit exactly match the source doc's tables (no rounding drift), the same
  discipline every other manuscript number follows.

**Output:** manuscript diff only; no new experiment doc needed (the source artifact
already exists in full house style).

### Phase 2 — Write up the ExECTv2 three-way comparison the thesis's Target tier requires (item 1)

**Why this is propagation, not new research:** the GEPA workstream already closed this
out (`PROJECT_STATUS.md`: "GEPA workstream closed out (06-28 to 06-30)"). This phase
synthesizes existing, closed GEPA results into manuscript language; it runs no new GEPA
cycles.

- Draft a new manuscript subsection — placement: end of §4.2 ("What the LLM Adds"), since
  it completes that section's three-way-comparison framing for ExECTv2 the way Tables 1-2
  already do for Gan. Alternatively, fold into §5 D.5 as a *resolved* (not open) item,
  replacing the current framing of S1's missing comparison.
- State the headline numbers precisely, with evidence-validity labels:
  - LLM-only (GEPA single-pass, gpt-4.1-mini): dev140 `clinical_headline` F1 ≈ 0.731
    (best multi-family run, `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`).
  - LLM-only (GEPA single-pass, Qwen 3.6 35B): dev140 F1 ≈ 0.654, underperforming its own
    hand-tuned ExECTv2 baseline (0.694) — cite
    `docs/research/exectv2_gepa_qwen_cross_model_2026-06-30.md`.
  - Hybrid ceiling (existing manuscript number): 0.9155 dev140 / 0.8356-0.8566 full-200
    (Table R2/R3).
  - Deterministic-only floor: already in Table R2 row context (~0.78-0.81 without format
    layers) — cite for the third leg of the three-way comparison if a clean
    deterministic-only ExECTv2 dev140 number exists in the component-off replay; if not,
    state plainly that the deterministic-only leg is the one true gap remaining (do not
    backfill with an approximate number).
- State the result as what it is: **the thesis's Target tier is now measured and is a
  negative result** — LLM-only does not approach the hybrid ceiling (~0.18-0.19 gap) and
  does not clear the published benchmark either. Frame this as consistent with, and
  reinforcing, C1's "architecture, not model, carries the gain" thesis: the LLM-only
  leg's shortfall is itself evidence that the deterministic/hybrid scaffolding (not raw
  LLM capability) is doing the load-bearing work — the same direction as C2 and C4, now
  with a third independent leg.
- **Critical accuracy requirement — do not import the stale root-cause claim.** The GEPA
  workstream's original explanation ("producer evidence-recall, not verify/arbitrate
  stages") has been partially revised by the 2026-06-30 EV-recall consolidation
  re-examination. State the corrected, per-family attribution: genuine evidence-retrieval
  shortfall is confirmed for Investigations (26-30% H-inflated, i.e., mostly real),
  partially genuine for Prescription (52.2% H-inflated, mechanism = transcription
  divergence not gold multiplicity), and mostly an artifact of gold consolidation
  convention for Diagnosis (93.5% H-inflated) and SeizureFrequency (61-83% H-inflated) —
  the same mechanism C1 already documents for those two families' benchmark gap. Cite
  `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md` and
  its four phase-result docs. This means the *honest* root-cause statement is: part of
  the LLM-only ceiling is genuine single-pass extraction-recall limitation (Investigations,
  partly Prescription), and part is the LLM-only architecture being scored against the
  same gold-multiplicity convention that already inflates the hybrid's apparent margin on
  Diagnosis/SF — i.e., the true architectural gap is *smaller* than 0.18-0.19 once both
  legs are corrected for gold convention, though by how much is not yet quantified (flag
  this precisely as unquantified, do not estimate a number that hasn't been computed).
- Add a new row to the Claim Boundary Summary and Evidence Validity Summary tables:
  evidence level = "dev140 development-surface, non-paper-comparable diagnostics" per
  `PROJECT_STATUS.md`'s existing framing — this is GEPA development-track evidence, not a
  frozen full-200/holdout result, and must be labeled as such, matching how the rest of
  the manuscript treats dev140-only numbers.
- Add to "Do Not Use As Claims": GEPA single-pass numbers are not promoted full-200 or
  holdout results; do not compare them directly to Table R2/R3's frozen full-200 numbers
  without the dev140-vs-full200 caveat already used elsewhere in the manuscript.

**Output:** manuscript diff (new subsection + two table rows + one new "do not use"
line). No new experiment artifacts — pure synthesis of existing, closed-out GEPA docs.

### Phase 3 — Root-cause the Qwen asymmetry in the same-core hybrid swap (item 4)

This is the one phase that does new (but small, replay-only) analysis.

- **Goal:** determine whether Qwen's full-200 shortfall (0.8197 vs GPT 0.8356, DeepSeek
  0.8566 — Table R3) is uniform across families/mechanisms or concentrated, so the
  manuscript can either explain it mechanistically or state precisely how it bounds the
  model-agnosticity claim.
- **Method (replay-only, no new model calls):** pull the per-family breakdown already
  reported in Table R3 (Diagnosis 0.8307, SF 0.7020, Prescription 0.8926-tied,
  Investigations 0.8503) plus the diagnostic fields already present in
  `exectv2_same_core_model_swap_full200_20260625.json` (`diagnostics.by_family`:
  `call_failures`, `parse_schema_failures`, `exact_evidence_rate`, `raw_mentions` vs
  `scored_mentions` — already inspected during the review and confirmed present per
  model). Compute, per family: Qwen's delta vs the GPT/DeepSeek mean, and whether the
  delta correlates with `raw_mentions/scored_mentions` ratio (over/under-extraction) or
  with the structured/exact evidence rate gap (already known: Qwen repair v02 has
  evidence rate 1.0000 per `PROJECT_STATUS.md`, so this leg is likely a clean null —
  confirm rather than assume).
- **Cross-reference, do not conflate:** the GEPA Qwen cross-model closeout
  (`docs/research/exectv2_gepa_qwen_cross_model_2026-06-30.md`) found Qwen's GEPA
  single-pass gap "localized to Diagnosis evidence-retrieval, not format" — but that is a
  *different architecture* (single-pass LLM-only) from Table R3's *hybrid* same-core swap.
  Check explicitly whether the same Diagnosis-concentration pattern holds in the hybrid
  setting or whether the hybrid's deterministic/format layers already absorb it (Table R3's
  Diagnosis delta, 0.8307 vs GPT 0.8397, is modest — only -0.009 — versus SF's -0.0505 and
  Investigations' -0.006, which would argue the hybrid gap is *not* Diagnosis-concentrated
  the way the GEPA gap is; verify this rather than assume it transfers).
- **Write-up:** a short dated doc,
  `docs/experiments/exectv2/reliability/exectv2_qwen_hybrid_swap_gap_decomposition_<date>.md`,
  in house style (self-validation reproducing Table R3's aggregate numbers from the same
  source JSON before trusting any decomposition, evidence-validity boundary, source
  artifacts list).
- **Manuscript edit:** in §4.3.1, add one or two sentences after the DeepSeek-vs-GPT
  discussion characterizing Qwen's shortfall precisely (uniform-and-modest vs.
  concentrated; mechanism if found) rather than leaving it as an unexplained number in a
  table. Revise the abstract's "0.8356–0.8566 F1 across three qualitatively different
  LLMs" framing to either (a) widen the stated range to include Qwen's 0.8197 if the
  finding supports calling the spread tight-and-non-catastrophic, or (b) add a clause
  acknowledging the open-weight model does not fully maintain the closed models' level,
  whichever the Phase 3 finding actually supports — do not pre-decide the wording before
  running the decomposition.

**Kill-criterion / scope limit:** this is a one-pass diagnostic over already-replayed
data. If the per-family/diagnostics fields in the existing JSON do not support a clean
mechanistic read (e.g., the signal is genuinely diffuse with no discriminating feature),
report that as the finding ("Qwen's shortfall is uniform and not attributable to any
single diagnosed mechanism in the available replay fields") and stop — do not escalate to
a new Qwen run or a fresh model-swap experiment under this plan.

### Phase 4 — Independent robustness check on the C1 gold-quality adjudications (item 3)

This is the highest-effort, highest-value phase, because C1 is the manuscript's most
load-bearing soft claim.

- **Goal:** produce an inter-rater reliability statistic between the existing
  adjudication verdicts (SF Phase 7, Dx canonical row analysis) and a *fresh, blinded*
  re-adjudication of a sample, to give the manuscript a robustness number instead of an
  unverified single-pass (SF) or five-uncross-checked-batches (Dx) provenance.
- **Sampling:** stratified random sample across both families and all three verdict
  buckets (`GOLD_RIGHT` / `MODEL_DEFENSIBLE` / `BOTH_DEFENSIBLE`), large enough for a
  meaningful kappa but bounded — target ~40 cases (20 SF from
  `_sf_canonical/_adjudication.csv`, 20 Diagnosis from `_dx_canonical/_adjudication.csv`),
  oversampling the minority verdict buckets if the base distribution is skewed (it is:
  per the manuscript, genuine-error verdicts are the minority class in both families, and
  a kappa computed on an all-majority-class sample is uninformative).
- **Blinding protocol:** the re-adjudicator (a fresh agent invocation or a separate
  reviewer with no access to this conversation's context) sees only the letter text, the
  gold annotation(s), and the model's prediction for each sampled case — **not** the
  original verdict label, **not** which family's "narrative" (gold-multiplicity vs
  IAA-ambiguity) the case was drawn to illustrate. Use the exact same three-way verdict
  taxonomy already defined in `experiments/exectv2_sf_canonical_adjudication.py`'s
  docstring, unchanged, so the comparison is apples-to-apples.
- **Statistic:** Cohen's kappa (or weighted kappa, since the three verdict categories
  have a natural ordering from "genuine model error" to "fully gold-side") between
  original and blind-fresh verdicts, plus simple raw agreement rate, reported per family
  and pooled.
- **Decision framing (not a kill-criterion that erases the original finding — a
  robustness report):**
  - Kappa ≥ 0.6 (substantial agreement, standard threshold): report this as
    independent corroboration; state it explicitly in D.2 and strengthen C1's framing
    from "self-adjudicated" to "self-adjudicated, independently corroborated on a
    blinded sample (κ=X)."
  - Kappa 0.4-0.6 (moderate): report honestly as partial corroboration; note which
    verdict boundary drives the disagreement (most likely `MODEL_DEFENSIBLE` vs
    `BOTH_DEFENSIBLE`, the softest distinction in the taxonomy) and whether collapsing
    those two categories raises agreement — this would itself be a useful finding about
    where the taxonomy's real discriminating power lies.
  - Kappa < 0.4: this is a genuine problem for C1 and must be reported as a limitation,
    not smoothed over — it would mean the gold-quality-ceiling argument's magnitude
    (F1 0.66→0.95, 62.1%→89.3%) is not robust to who is doing the judging, and the
    manuscript's C1 claim should be revised to report a *range* bounded by the
    re-adjudication's lower estimate rather than the original single point estimate.
- **Explicit limitation regardless of outcome:** state plainly, in whatever framing
  results, that this strengthens internal robustness (agreement across two
  *independent passes within the project's own evaluation framework*) but is **not**
  external clinical validation. A blinded board-certified neurologist/epileptologist
  reviewing the same sample remains the gold-standard check this plan cannot fully
  substitute for, and should be named as residual future work in D.5 regardless of how
  the kappa comes out.
- **Output:** `docs/experiments/exectv2/reliability/exectv2_gold_quality_adjudication_blind_replication_<date>.md`,
  house style, reporting the sample, the blinding protocol, the raw and weighted kappa,
  per-family breakdown, and the manuscript-language consequence under each of the three
  bands above. Manuscript edit to §4.1.2/D.2/C1 follows directly from whichever band the
  result lands in — do not pre-write the edit before the kappa is computed.

### Phase 5 — Tighten the manuscript's framing of the no-deployable-signal finding (item 5)

Framing-only; no new analysis (the calibration/abstention plan owns any attempt to
improve the underlying numbers).

- In D.5 (Limitations) and/or §4.4, add one direct sentence stating the practical
  consequence the manuscript currently only implies: *the transparency/reliability
  pillar has no working low-burden triage policy on the broad ExECTv2 task, and the one
  slice where it matters most clinically (the binding gold-unknown over-read cases) has
  no forward-observable separator at all (best AUROC 0.676 < the paper's own 0.70 bar).*
  State this is an open research question, not a closed null — and forward-reference the
  calibration/abstention strengthening plan as the active next step, so a reader does not
  mistake the honest negative result for the project considering the question settled.
- Do not weaken or hedge the existing H0-retained framing in §4.3.2/D.3 — that result is
  solid and pre-registered; this phase only adds the deployment-consequence sentence
  that is currently left for the reader to infer.

**Output:** manuscript diff, two sentences, no new artifacts.

## 4. Non-goals

- No new GEPA optimization runs (Phase 2 is write-up of already-closed work only).
- No new full-200 or test450/holdout row-level inspection under this plan's authority.
- No attempt to fix or improve calibration/abstention numbers — that is the companion
  plan's job; this plan only tightens the manuscript's framing of the existing finding
  (Phase 5).
- No re-litigation of the original SF/Dx adjudication verdicts as "wrong" — Phase 4
  produces a *robustness statistic alongside* them, not a replacement judgment.
- No IEEE LaTeX resync (named in the research report as a separate logistics item, not
  in scope here).

## 5. Output summary

- Manuscript diff across Phases 1, 2, 3 (partial), 5, and 3/4 conditionally on findings.
- Two new dated experiment docs: Qwen hybrid-swap gap decomposition (Phase 3), gold-quality
  adjudication blind replication (Phase 4).
- Updated Claim Boundary Summary, Evidence Validity Summary, and "Do Not Use As Claims"
  list reflecting all five closures.
