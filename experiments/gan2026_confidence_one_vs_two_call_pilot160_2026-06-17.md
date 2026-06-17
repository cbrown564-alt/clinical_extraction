# Confidence Elicitation — One Call vs Two (pilot160)

Date: 2026-06-17 · Model openai/gpt-4.1-mini · n=160 paired (7 failures) · temp 0.0

**Question.** Does variant-D's failure-prediction discrimination come from the **decoupled second call** or simply from the **changed prompt wording**? Both signals are scored on the SAME answers / SAME error labels (the joint arm's answers), so the only difference is one call vs two.

Joint-arm Purist accuracy 0.956 (SE baseline 0.881; embedding the priming moves the answer if these differ).

| Arm | calls | top-bucket | mean p | ECE | Brier | failure AUROC |
|---|---:|---:|---:|---:|---:|---:|
| **Joint (1 call, wording only)** | 1 | 93.1% | 0.919 | 0.037 | 0.045 | **0.418** |
| **Decoupled reviewer (2 calls)** | 2 | 86.2% | 0.898 | 0.064 | 0.054 | **0.718** |

Comparators: decoupled-on-frozen-SE AUROC 0.684; intrinsic in-pass 0.497; external corroboration 0.781.

**Paired AUROC difference (decoupled − joint): +0.300, 95% CI [-0.013, +0.634]** (999 bootstrap reps).

## Residual sensitivity

- Joint: residual (n=33) mean p 0.900, acc 90.9%; non-residual mean p 0.924, acc 96.9%
- Decoupled: residual (n=33) mean p 0.838, acc 90.9%; non-residual mean p 0.913, acc 96.9%

## Verdict

**Neither.** Both arms collapse toward chance at this scale (joint 0.418); the paired test cannot separate them.
