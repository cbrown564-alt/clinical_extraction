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

**H0 — D does not materially boost the external score.** The unsupervised rank-average edges external alone by only +0.014 (within CI on this error count), and crucially the **honest CV-weighted blend (0.786) collapses back to external alone (0.783)** — when the weight is chosen without peeking, fusion buys nothing. Note this is NOT because the signals are redundant: Spearman is only 0.23, so D and the external composite make partly *independent* errors. The problem is that D is simply the weaker, noisier ranker (0.684 vs 0.783), so averaging it in mostly adds noise. External corroboration stays the single best forward-observable signal; D's value is as a cheaper standalone proxy where 3-model agreement is unavailable, not as an additive booster.
