# Satellite 06 — Evaluation & Benchmark Protocol

Parent: [[00_overarching_implementation_plan]] · Phase 7 (+ governs all phases)
Status: planning. Contains the only holdout-facing procedure; **the full-200 and
`test` reads require explicit user authorization.**

## Purpose

Define exactly how we score, what counts as "beating the benchmark", how splits
are used, and the authorized procedure for the benchmark-comparable audit. This
is the document a reviewer would check to trust the headline number.

## 1. The target

Published ExECTv2 (Fonferko-Shadrach 2024), validation of the rule-based pipeline
against the consensus gold standard, **with all features**:

- **Overall: F1 0.87 per item, 0.90 per letter.**
- Per-entity per-item F1 (gold): Birth History 0.97, Diagnosis 0.85, Epilepsy
  Cause 0.90, Investigations 0.95, Onset 0.96, Patient History 0.78, Prescription
  0.87, **Seizure Frequency 0.66**, When Diagnosed 0.91.
- **Seizure Frequency per letter 0.68** (the SF lowest; 260 gold annotations) —
  the specific SF bar we track in [[02_rules_based_architecture]].
- Human IAA overall 0.73 (SF 0.47) — context, not the target.

"Beat the benchmark" = exceed **overall** 0.87 per item / 0.90 per letter on the
**same surface the benchmark used (all 200 letters)**, with our gates active.
Per-entity wins (especially SF) are reported but the headline is overall.

## 2. Match policy (pin it, then report sensitivity)

Scoring is label-based (offsets drift). The **benchmark-comparable policy** is
fixed as:

- entity + `normalize_phrase` + **all features** (the paper's "with all
  features"), via `MatchConfig(include_attributes=True)`.
- `CUIPhrase` ignored (redundant with phrase). **CUI**: the paper disregarded
  CUIs in IAA; the pinned headline policy therefore **excludes CUI** from the
  match key, and we **additionally report a CUI-strict variant** so the choice is
  transparent.
- Per-item = every mention (multiset, per-letter, micro-averaged). Per-letter =
  ≥1 correct mention. Both already implemented in `scoring.py`.

Report a small **sensitivity table**: phrase-only, phrase+features (headline),
phrase+features+CUI. This pre-empts "you picked the lenient policy" criticism.

## 3. Split usage

- **`dev`**: all development, iteration, ablation, prompt tuning. Unlimited reads.
- **`test`**: held out; a single confirmatory read per architecture once dev is
  locked. Authorized.
- **Full-200 frozen audit**: the benchmark-comparable headline. The benchmark
  scored on all 200, so this is the only directly comparable number. Run **once
  per architecture**, after dev is locked, **no tuning against it**, authorized.

The `dev` vs full-200 gap is itself reported (the validation-to-test-gap
discipline from Gan 2026) as evidence of generalization vs overfitting.

## 4. Authorized audit procedure (Phase 7)

Identical in spirit to the Gan 2026 frozen-aggregate audit:

1. Lock all rules/prompts/configs for the architecture under audit; record
   versions.
2. Obtain explicit user authorization for the holdout/full-200 read.
3. Run the locked pipeline over the frozen surface, no row inspection, no
   re-tuning, no repair beyond the standing semantically-neutral ladder.
4. Produce the aggregate report (overall + per-entity per-item/per-letter F1,
   gates, sensitivity table, dev→audit gap).
5. Register the audit run; it is immutable. Any later change requires a new
   authorized audit, not an edit.

## 5. What we report alongside the score

The reliability claim is the score **plus** the gates and trails:

- schema-validity rate, repair rate
- evidence-validity rate (per architecture)
- uncertainty calibration summary
- routed-row taxonomy (hybrid)
- the three-way comparison and the dev→audit gap

A score without these is a benchmark result; with these it is a reliability
result, which is the paper's contribution.

## 6. Statistical care

- Report per-item F1 with a bootstrap CI over letters (the benchmark reports
  point estimates; we add CIs to make the comparison honest).
- For the headline "beat" claim, state the margin and whether the CI clears
  0.87/0.90, not just the point estimate.

## 7. Deliverables & exit criteria

- This protocol, pinned match policy, and split manifest in place
- Sensitivity + dev→audit-gap reporting wired into the report builders
- Exit (Phase 7): authorized full-200 audit for each architecture that reaches
  the bar on dev, with the full reliability artifact set attached.
