# Gan 2026 — One-Call vs Two-Call Confidence (Paired Test) — test450 Port Predeclaration

Date: 2026-06-17
Driver: `experiments/build_gan2026_confidence_one_vs_two_call_test450.py`
Split: **test450 (frozen holdout)** · Model gpt-4.1-mini · Temperature 0.0
Freeze-warden gated · aggregate-only readout · run once.

## Why

The validation750 paired test
(``)
found that variant-D's failure-prediction discrimination is a **prompt-wording
effect, not a decoupling effect**: a single extraction call emitting a *primed*
`answer_probability_correct` matched the decoupled two-call reviewer (joint 0.609 vs
decoupled 0.641; paired difference +0.032, 95% CI [−0.032, +0.098] — includes 0),
with better ECE/Brier. This port confirms whether that conclusion holds on the locked
holdout.

## Protocol (identical transform, new split)

The joint-arm transform is **imported byte-identical** from the validation driver
(`build_gan2026_confidence_one_vs_two_call_paired`): same `JOINT_ELICITATION_INSTRUCTIONS`
(the verbatim variant-D priming), same `build_joint_prompt_input`, same
`parse_joint_probability`, same `arm_metrics` / `bootstrap_auroc_diff`. The decoupled
arm is the production `ConfidenceReviewer` (`variant_D_decoupled_v1`). All are
**hash-frozen before touching test450** and the SHA-256s are recorded in the readout.

**Asymmetry vs the d-gating test450 port.** Unlike the d-gating run (which reused the
frozen `v0_reference` answers, 0 SE calls), the joint arm here **necessarily generates
a fresh prediction set** on test450 — the one-call self-confidence cannot exist
without re-running extraction. Both confidence signals are then scored on **that same
joint answer set** (paired), so the comparison is internally valid; but the joint-arm
*accuracy* is a fresh-architecture number, not the certified v0_reference subject. It
is reported as context, not as a champion claim.

Gate sequence:
1. `--run` required (refuses to touch test450 otherwise).
2. `run_single_model_preflight` (split=test): manifest == `gan2026_split_v1`, 450/450
   locked unique row ids, subject artifact covers the locked set with `v0_reference`,
   and the candidate outputs are absent (no cross-run tuning).
3. Hash-freeze transforms, then the fresh joint pass (450 calls) + decoupled reviewer
   over the joint answers (450 calls). Resumable per `source_row_index`.
4. Aggregate-only readout — no `source_row_index` / `transition_vs_v0` / `score_layers`
   markers; only AUROCs, the paired-difference CI, ECE/Brier/top-bucket, accuracy.

## Predeclared metrics & decision rule

- Primary: **paired failure-prediction AUROC**, joint(1-call) vs decoupled(2-call),
  on the same answers/error labels; 1,000-sample row-bootstrap of the paired
  difference `AUROC_decoupled − AUROC_joint` with 95% percentile CI.
- Decision (mirrors validation): if the paired-difference 95% CI **includes 0** and
  `AUROC_joint` is clearly > 0.5 ⇒ **the validation H_wording conclusion replicates**
  (the second call is removable on the holdout). If the CI **excludes 0** favouring
  decoupled ⇒ the conclusion does not hold on test and the decoupled call earns its
  cost. If both collapse to ~0.5 ⇒ neither self-signal is useful on the holdout.
- Secondary: ECE, Brier, top-bucket share, distinct values per arm; joint-arm Purist
  accuracy vs the validation joint accuracy (0.863) and the SE test baseline (0.809).
- The val→test movement of each AUROC is itself a reported finding (self-signals are
  known to attenuate on test — d-gating saw 0.684→0.649).

Changes no production label; gates nothing on test450.

---

## Results (2026-06-17, frozen test450 — run once, freeze-gated)

Single-model preflight passed (10 checks, 0 failures); transforms hash-frozen before
the run (joint `bf053a21…`, reviewer `c9198087…`, readout `c6d66ca9…`). n=446 paired
(4 unscorable-gold dropped), **104 failures**, 0 parse failures either arm.

| Arm | calls | top-bucket | distinct | ECE | Brier | failure AUROC |
|---|---:|---:|---:|---:|---:|---:|
| **Joint (1 call, wording embedded)** | 1 | 92.4% | 4 | 0.146 | 0.197 | **0.601** |
| **Decoupled reviewer (2 calls)** | 2 | 80.9% | 11 | 0.146 | 0.190 | **0.669** |

**Paired AUROC difference (decoupled − joint) = +0.068, 95% CI [+0.014, +0.132]**
(1,000 reps). The CI **excludes 0** in favour of the decoupled reviewer.

Joint-arm Purist accuracy **0.767** — below the SE test baseline 0.809 (embedding the
priming *degrades* the extractor on the holdout, where on validation it was ~neutral,
0.863 vs 0.881).

### Verdict — the validation H_wording conclusion DOES NOT replicate

On the locked holdout the decoupled two-call reviewer ranks errors significantly better
than the one-call joint self-confidence (0.669 vs 0.601, paired difference CI excludes
0). The direction (decoupled ≥ joint) was the *same* on both splits — validation simply
lacked the gap/power to call it (val diff +0.032, CI included 0; test diff +0.068, CI
excludes 0). Pooling both splits, the weight of evidence is that **decoupling adds
modest but real discrimination**, and on test the in-pass folding *additionally* costs
~4 points of extraction accuracy (0.767 vs 0.809).

**Conclusion: keep the two-call decoupled `ConfidenceReviewer` stage.** The
validation-only "the second call is removable" reading was a false economy the holdout
caught — the extra call earns its cost on test, and folding the priming into the
extraction pass hurts the answer. Both self-signals remain modest (< external
corroboration 0.781) and gate nothing; this confirms the *current* production design.
