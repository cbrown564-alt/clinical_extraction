# Gan 2026 — One-Call vs Two-Call Confidence Elicitation (Paired Test) — Predeclaration

Date: 2026-06-17
Driver: `experiments/build_gan2026_confidence_one_vs_two_call_paired.py`
Split: validation750 · Model: gpt-4.1-mini · Temperature 0.0 (single-shot point
calibration, per [[project_gan2026_confidence_elicitation]] — varying-temperature
rule scopes only to consistency/semantic entropy).

## Question

Variant D (failure-mode-primed confidence) recovers real failure-prediction
discrimination — validation750 AUROC **0.684** vs the intrinsic in-pass
`selection.confidence` AUROC **0.497** (chance) — but it costs **one extra LLM
call** per row (`confidence_reviewer.py`, a decoupled second pass that is
label-blind to the model's own rationale).

The production decision (decoupled shadow stage) rests on the *belief* that the
gain comes from **decoupling** — a separate, dedicated, rationale-blind call —
and that folding the same priming back into the joint extraction pass would
"re-degenerate" (`confidence_reviewer.py` docstring). **That belief was never
tested.** The alternative hypothesis is that the gain comes simply from the
**changed prompt wording** (naming the unknown↔rate over-read), in which case the
second call is wasteful and the priming can ride along in the single extraction
call for free.

## Design — paired, same wording, one prompt vs two

A clean paired test that removes the answer-set confound: **both** confidence
signals are scored against the **same answers and the same error labels**.

- **Joint arm (1 call/row).** A single SE extraction pass whose prompt embeds the
  *verbatim* variant-D failure-mode-priming sentence and emits an extra
  `selection.answer_probability_correct` (integer 0-100) **in the same JSON** as
  the answer. The model sees its own events/rationale when it self-rates (this is
  the absence of decoupling). Wording held ≈constant with `VARIANT_D_INSTRUCTIONS`.
- **Decoupled arm (1 extra call/row).** The existing `ConfidenceReviewer`
  (`variant_D_decoupled_v1`) run over the **joint arm's own answers** — note +
  stated answer only, blind to the joint rationale.

Both signals predict the **same** `purist_correct` computed from the joint arm's
answers. Difference in AUROC is therefore attributable to *one call vs two*
(decoupling + rationale-blindness + dedicated focus), with the priming wording
held constant.

Reported alongside as context: existing decoupled-on-frozen-SE-answers AUROC
**0.684** (`gan2026_confidence_reviewer_shadow_validation750_2026-06-17`), and the
joint arm's Purist accuracy vs the frozen SE baseline (0.881) — does embedding the
priming move the answer?

## Predeclared hypotheses

- **H_wording** (the thing being tested): the wording alone explains the gain. The
  joint-arm self-confidence ranks errors about as well as the decoupled reviewer —
  `AUROC_joint` within the bootstrap CI of `AUROC_decoupled`, and clearly above
  0.5. ⇒ the second call is removable; fold priming into the extraction pass.
- **H_decoupling** (the production prior): discrimination requires the separate
  rationale-blind call. The joint self-confidence re-degenerates toward the
  intrinsic field — `AUROC_joint` significantly below `AUROC_decoupled` and near
  0.5. ⇒ keep the two-call decoupled stage.

## Primary metric & decision rule

- Primary: **paired failure-prediction AUROC**, joint vs decoupled, on the same
  rows/answers/error labels (validation750). 1,000-sample row bootstrap of the
  **paired AUROC difference** (`AUROC_decoupled − AUROC_joint`); report the 95%
  percentile CI.
- Decision: if the paired-difference 95% CI **excludes 0** in favour of decoupled
  ⇒ H_decoupling (decoupling does real work; keep two calls). If it **includes 0**
  and `AUROC_joint` is clearly > 0.5 ⇒ H_wording (the call is removable). If both
  collapse to ~0.5 ⇒ neither is useful at this scale.
- Secondary: ECE, Brier, top-bucket share, distinct values, residual sensitivity
  for each arm; joint-arm Purist accuracy vs SE 0.881.

This gates nothing on test450 and changes no production label; it is a validation
diagnostic about whether the extra call earns its cost.

---

## Results (2026-06-17, validation750)

Run: `experiments/build_gan2026_confidence_one_vs_two_call_paired.py --full`.
n=737 paired (13 unscorable-gold rows dropped), **101 failures**. 0 parse failures
on either arm. Joint-arm Purist accuracy **0.863** (vs SE baseline 0.881 — embedding
the priming does *not* meaningfully move the answer at scale; the pilot's 0.956 was a
160-row / 7-failure fluke).

| Arm | calls | top-bucket | distinct | ECE | Brier | failure AUROC |
|---|---:|---:|---:|---:|---:|---:|
| **Joint (1 call, wording embedded)** | 1 | 91.0% | 5 | **0.050** | **0.119** | **0.609** |
| **Decoupled reviewer (2 calls)** | 2 | 79.8% | 12 | 0.080 | 0.139 | **0.641** |

**Paired AUROC difference (decoupled − joint) = +0.032, 95% CI [−0.032, +0.098]**
(1,000 row-bootstrap reps). The CI **includes 0**.

Comparators: decoupled-on-frozen-SE 0.684; intrinsic in-pass `selection.confidence`
**0.497** (chance); external corroboration 0.781.

### Verdict — H_wording (the production prior was wrong)

The discrimination is a **prompt-wording effect, not a decoupling effect.** Folding
the verbatim failure-mode priming into the single extraction call recovers
essentially the same failure-prediction discrimination (**0.609 vs 0.641**, paired
difference CI straddles 0) at **one call instead of two** — and with *better*
calibration error (ECE 0.050 vs 0.080, Brier 0.119 vs 0.139). The separate,
rationale-blind second call is **not** the active ingredient; the priming wording is.

This **falsifies** the belief recorded in `confidence_reviewer.py` ("folding the
priming back into the joint pass … is expected to re-degenerate — hence a decoupled
stage"). It does not re-degenerate. The earlier evidence for "decoupling matters" was
the comparison against the *intrinsic* low/med/high `selection.confidence` field
(0.497) — but that field is degenerate because it is unprimed/categorical, not because
it is in-pass. A primed integer-probability question works whether posed in-call or
out-of-call.

### Caveats

- Both signals are **modest** (~0.61–0.64) and well below external corroboration
  (0.781); neither replaces it. This changes *how cheaply* the self-signal is
  obtained (one call, free-riding on extraction), not the conclusion that external
  corroboration is the stronger forward-observable signal.
- The decoupled arm scored 0.641 here vs 0.684 on the frozen-SE answers — expected,
  since it ran over the joint pass's (slightly different) answer set; the paired
  comparison is internally valid because both arms share those answers.
- Residual rows are no less accurate than the rest (88.7% vs 85.0%) and neither
  signal drops its confidence there — consistent with The Wall: the over-reading is
  confident, so no self-signal (in-call or decoupled) flags it well.

### Implication (validation-only — SUPERSEDED by the test450 holdout)

> **The provisional read below did NOT survive the holdout.** On frozen test450
> (``,
> run 2026-06-17) the decoupled reviewer ranks errors *significantly* better than the
> one-call joint signal (0.669 vs 0.601, paired difference +0.068, 95% CI
> [+0.014, +0.132] — **excludes 0**), and the in-pass folding additionally *degrades*
> extraction accuracy (0.767 vs SE 0.809). The direction (decoupled ≥ joint) was the
> same on both splits; validation merely lacked the gap/power to call it. **Corrected
> conclusion: keep the two-call decoupled `ConfidenceReviewer` stage** — the extra call
> earns its cost on the holdout. The validation-only text below is retained for the
> record.

~~If a cheap self-confidence triage knob is wanted, **emit the primed
`answer_probability_correct` inside the extraction call** — it matches the decoupled
reviewer's discrimination at zero extra calls and better calibration. The decoupled
`ConfidenceReviewer` stage can be retired in favour of the in-pass field (still a
shadow signal; still secondary to external corroboration). Not promoted to gating.~~
