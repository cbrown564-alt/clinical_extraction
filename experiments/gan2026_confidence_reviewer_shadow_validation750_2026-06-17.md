# Confidence-Reviewer Shadow Run (validation750)

Date: 2026-06-17 · Host: hybrid_structured_events.run_split (SE selection pass, reused SE outputs) · reviewer `variant_D_decoupled_v1` · SE calls 0 (reused), reviewer live · n=750 (748 scored, 87 failures)

**Shadow stage — gates nothing; SE label/score path untouched.** `calibrated_confidence` scored against the SE pass's own `purist_correct`.

| Signal | top-bucket | mean p | ECE | Brier | failure AUROC |
|---|---:|---:|---:|---:|---:|
| **variant D (decoupled reviewer)** | 76.5% | 0.863 | 0.052 | 0.118 | **0.684** |
| intrinsic in-pass `selection.confidence` | 99.5% | — | — | — | 0.497 |

External-corroboration comparator AUROC (P0.3) = 0.781.

## Residual sensitivity

- Residual (n=269): mean p 0.843, acc 88.8%
- Non-residual: mean p 0.874, acc 88.1%

## Reading

In production shape (hosted in the SE pass, scored on SE answers), the decoupled variant-D reviewer ranks errors at AUROC **0.684** vs the in-pass joint field's 0.497 on the same rows — the discrimination survives integration. Still shadow: it complements external corroboration (0.781) and is not yet a gate.
