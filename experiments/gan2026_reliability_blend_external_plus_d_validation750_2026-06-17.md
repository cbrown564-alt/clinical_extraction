# Blend: External Risk Score + Variant-D Self-Signal (validation750)

Date: 2026-06-17 · n=748 (87 errors) · model calls 0 · scored against `v0_reference.comparison.purist_correct`

Correctness-target cross-check: SE-pass vs v0_reference purist mismatch on **0/748** rows (confirms the shadow run scored the canonical subject). Dropped (no D signal): 2.

## Failure-prediction AUROC

| Signal | AUROC |
|---|---:|
| external composite alone | 0.783 |
| variant D alone | 0.684 |
| **rank-average blend (headline)** | **0.797** |
| CV-weighted blend (held-out) | 0.786 |
| whole-data best-weight (optimistic) | 0.795 |

Δ(rank-blend − external) = **+0.014**. Spearman(external-risk, D-risk) = **0.234**.

## Selective risk-coverage AUC (lower = better)

- external alone: 0.0392
- rank-average blend: 0.0382

## Reading

**H0 — D is largely redundant with the external score.** The blend does not materially beat corroboration alone. Given the Spearman correlation, the self-signal and the external composite are flagging substantially the *same* risky rows, so fusion adds little. External corroboration remains the single best forward-observable signal; D's value is as a cheaper standalone proxy where 3-model agreement is unavailable, not as an additive booster.
