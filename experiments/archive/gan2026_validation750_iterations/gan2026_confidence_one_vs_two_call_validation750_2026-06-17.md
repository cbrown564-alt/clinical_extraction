# Confidence Elicitation — One Call vs Two (validation750)

Date: 2026-06-17 · Model openai/gpt-4.1-mini · n=737 paired (101 failures) · temp 0.0

**Question.** Does variant-D's failure-prediction discrimination come from the **decoupled second call** or simply from the **changed prompt wording**? Both signals are scored on the SAME answers / SAME error labels (the joint arm's answers), so the only difference is one call vs two.

Joint-arm Purist accuracy 0.863 (SE baseline 0.881; embedding the priming moves the answer if these differ).

| Arm | calls | top-bucket | mean p | ECE | Brier | failure AUROC |
|---|---:|---:|---:|---:|---:|---:|
| **Joint (1 call, wording only)** | 1 | 91.0% | 0.912 | 0.050 | 0.119 | **0.609** |
| **Decoupled reviewer (2 calls)** | 2 | 79.8% | 0.865 | 0.080 | 0.139 | **0.641** |

Comparators: decoupled-on-frozen-SE AUROC 0.684; intrinsic in-pass 0.497; external corroboration 0.781.

**Paired AUROC difference (decoupled − joint): +0.032, 95% CI [-0.032, +0.098]** (1000 bootstrap reps).

## Residual sensitivity

- Joint: residual (n=257) mean p 0.907, acc 88.7%; non-residual mean p 0.915, acc 85.0%
- Decoupled: residual (n=257) mean p 0.853, acc 88.7%; non-residual mean p 0.872, acc 85.0%

## Verdict

**H_wording.** The joint one-call self-confidence ranks errors at AUROC 0.609, within the bootstrap CI of the decoupled reviewer (difference CI includes 0). The discrimination comes from the changed wording, not the decoupling — the second call is removable and the priming can ride along in the extraction pass for free.
