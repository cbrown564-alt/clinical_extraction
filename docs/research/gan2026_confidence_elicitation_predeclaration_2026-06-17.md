# Gan 2026 — Confidence-Elicitation Predeclaration (Calibration probe)

Date: 2026-06-17

Predeclared design for a small, validation-only experiment that asks whether the
**degeneracy** of the model's self-reported confidence is a property of *how we ask*
or a property of the model. It extends the Calibration dimension of
`gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md` (Part I, dim. 4 — the
weakest leg, 2/5→3/5) and the P0.3 finding that self-confidence is uninformative
while external signals rank correctness.

This is **predeclared before any run** so a flat/null result is as reportable as a
hit, consistent with how the strand treats "The Wall."

---

## 1. The mechanism we are testing against

The logged `confidence` field (`Literal["low","medium","high"]`) is emitted by the
LLM-only labelers (`llm_only_direct_labeler.py:149`, `llm_only_canonical_pipeline.py:88`)
and is **degenerate**: 749/750 rows "high" on validation, 443/450 on test450; the
buckets are statistically indistinguishable (P0.3). The current anchor
(`llm_only_direct_labeler.py:275-285`) defines:

> `'high'` when there is exactly one unambiguous current fact, no competing claims,
> and the evidence can be quoted directly from the note.

Three structural causes, each of which a new elicitation can attack:

1. **The "high" anchor matches the common case.** Most letters contain one quotable
   current fact; the dominant over-reading failures (last-event→rate, "since X"→rate,
   provoked→rate) are precisely the rows where the model has *already decided* there
   is one clean fact — so by its own definition they read "high." The confidence
   definition keys on the same surface feature the answer over-trusts; it cannot
   dissent from the answer.
2. **Joint emission = post-hoc rationalization.** Confidence is produced in the same
   pass as the label, so it justifies the chosen answer rather than probing it.
3. **Coarse 3-bucket scale, no consider-the-alternative step.**

## 2. Subject and what this does / does not touch

- **Answers under test = the canonical production answers**: the `v0_reference`
  single-SE-mini layer per row (decision 0018), read via
  `reliability_common.subject_final_label/subject_final_kind/subject_purist_correct`
  from `gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`.
- **Elicitation is a *decoupled second pass*** on `gpt-4.1-mini`: given the note plus
  the already-assigned answer, a separate call returns only a probability. This
  realizes cause #2 (decoupling) and **does not alter the production path** — the V0
  pipeline is unchanged; we are measuring a candidate *self-signal*, not shipping it.
- **Validation only.** test450 is untouched; holdout consideration (freeze-warden
  gated) is out of scope until a variant earns it on validation.

## 3. Variants (per user selection: C + D)

Both elicit an integer `probability` ∈ [0,100] → `p_correct ∈ [0,1]`, directly
comparable to `purist_correct`. The contrast between them isolates whether **naming
the dominant failure mode** beats a generic decoupled framing.

- **C — Second-reader agreement.** "A second, independent epileptologist reads the
  same letter from scratch. Probability they assign the *same* purist category as the
  stated answer." Decouples confidence from self-justification; forces the model to
  reason about how a careful independent reader could disagree.
- **D — Failure-mode-primed correctness.** "Probability the stated answer is the
  *correct* purist category," with the prompt explicitly naming the dominant error:
  a non-quantifiable description (single last-event date, event "since" an anchor,
  provoked/transient, one isolated seizure) mis-read as an ongoing **rate** when the
  truth is `unknown`; or, conversely, a genuine rate wrongly called `unknown`.

**Elicitation temperature = 0.0 (deterministic).** This is a single-shot calibration
probe, *not* a consistency/semantic-entropy probe; the varying-temperature requirement
(`feedback_self_consistency_varying_temperature`) scopes to sampling-based consistency
(P0.8/P2.1), not to point confidence elicitation. Stated here to preempt the confusion.

## 4. Sample (stratified, deterministic)

~160 validation rows, **residual-enriched** to guarantee enough error events for a
stable AUROC (the curve rests on ~50 errors, per P0.2). Residual = `band_unknown` ∪
`seizure_free_duration` family, using the frozen `boundary_band` /
`classify_boundary_families` classifiers (identical to P2.1). Selection: up to 80
residual rows + fill to 160 with non-residual, ordered by `source_row_index`
(deterministic, resumable). Call budget ≈ 160 × 2 variants = ~320 mini calls (~$0.50).

## 5. Metrics

Per variant, over rows with a parsed probability:

- **Spread (the headline):** mean, std, count of distinct values, and **top-bucket
  share** (fraction with `p_correct ≥ 0.9`). Baseline degeneracy = 98.5% one bucket.
- **Calibration:** ECE (10-bin) + reliability table, Brier
  (`reliability_common.expected_calibration_error/brier_score`).
- **Discrimination (failure prediction):** AUROC of `risk = 1 − p_correct` against
  `not purist_correct` (`reliability_common.auroc`). Chance = 0.5; the external-signal
  comparator from P0.3 = **0.781**.
- **Residual sensitivity:** mean `p_correct` and accuracy on residual vs non-residual
  (does confidence actually drop where the model is wrong?).

**Comparator** `[comparator: direct-labeler joint self-confidence]`: the documented
degenerate `confidence` high/med/low from
`..._llm_only_direct_labeler_gpt41mini_2026-06-07.jsonl`, mapped high=1.0/med=0.5/low=0.0,
scored against *its own* `purist_correct`. Different architecture and joint elicitation,
so labeled a comparator, not a like-for-like.

## 6. Predeclared hypotheses

- **H1 — elicitation recovers a usable self-signal.** At least one variant yields a
  **non-degenerate** distribution (top-bucket share materially below baseline, set at
  **< 70%**) **and** failure-prediction **AUROC ≥ 0.65**. A variant reaching toward the
  external 0.781 would mean a forward-observable self-signal exists once asked correctly.
- **H0 — verbalized self-confidence is irrecoverable.** Both variants stay degenerate
  (top-bucket share ≥ 70%) **or** non-discriminative (AUROC ≤ 0.60). Reading: the
  over-reading is *confident regardless of elicitation framing* — this triangulates with
  P0.3 (self-confidence degenerate), P0.8 (self-consistency chance-level), and P2.1
  (sampling entropy flat at the residual): every *self*-signal fails, and only **external**
  corroboration crosses the wall. A publishable null.
- **Secondary:** does failure-mode priming (D) beat generic decoupling (C) on AUROC /
  residual sensitivity? Isolates whether the lever is *decoupling* or *failure naming*.

## 7. Decision rule

- If a variant meets **H1** on the pilot → scale that variant to validation750 (same
  driver, `--full`), then and only then consider a freeze-warden-gated holdout port.
- If **H0** → stop; the null is the result and feeds the Calibration narrative (the
  external score in P0.3 stays the only calibrated signal).

## 8. Artifacts

- Driver: `experiments/build_gan2026_reliability_confidence_elicitation.py`
  (`--pilot` / `--full`; resumable per-variant sample JSONL).
- Outputs: `gan2026_reliability_confidence_elicitation_{tag}_2026-06-17.{json,md}` +
  per-variant `..._samples_{tag}_{variant}_2026-06-17.jsonl`. Registers in
  `experiments/RUN_INDEX.md`.
