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
