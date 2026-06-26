# Confidence Elicitation — One Call vs Two on Frozen test450

## Aggregate-Only Holdout Readout

Date: 2026-06-17 · Split: test450 (frozen holdout) · arch: fresh joint gpt-4.1-mini SE+confidence pass (paired with decoupled reviewer)

_frozen aggregate-only holdout readout; no row-level test inspection._

n=446 paired (104 failures) · temp 0.0 · joint-arm Purist accuracy 0.767 (SE test baseline 0.809).

Frozen transforms (predeclared, hashed before touching test450): joint `bf053a2127911c0f…`, reviewer `c9198087ce03ffa0…`, readout `c6d66ca9956cbf0c…`.

**Both confidence signals scored on the SAME answers / SAME error labels (the fresh joint answers) — the only difference is one call vs two.**

| Arm | calls | top-bucket | mean p | ECE | Brier | failure AUROC |
|---|---:|---:|---:|---:|---:|---:|
| **Joint (1 call, wording embedded)** | 1 | 92.4% | 0.913 | 0.146 | 0.197 | **0.601** |
| **Decoupled reviewer (2 calls)** | 2 | 80.9% | 0.881 | 0.146 | 0.190 | **0.669** |

**Paired AUROC difference (decoupled − joint): +0.068, 95% CI [+0.014, +0.132]** (1000 bootstrap reps).

Comparators — validation750: joint 0.609, decoupled 0.641, paired-diff CI [-0.032, 0.098]; intrinsic in-pass 0.497; external corroboration 0.781.

## Verdict

**Does not replicate.** On the holdout the paired difference CI excludes 0 in favour of the decoupled reviewer (joint 0.601 vs decoupled 0.669); the extra call earns its cost on test.
