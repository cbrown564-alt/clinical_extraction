# P0.3 — External-Signal Calibration (ECE / Brier / Failure-Prediction AUROC)

Date: 2026-06-17  ·  Split: validation750  ·  Model calls: 0

## Self-confidence is degenerate

Subject self-confidence is `structured_record.selection.confidence (subject SE pass)` (subject single-SE-mini); the v0_reference scoring layer drops confidence, but the SE source emits it.

| Confidence bucket | n | Purist acc |
|---|---:|---:|
| high | 744 | 88.3% |
| medium | 4 | 100.0% |
| missing | 2 | 0.0% |

The dominant bucket holds **99.2%** of rows — the subject's own confidence is near-constant and cannot rank correctness. (The V12 reasoner self-report is equally degenerate; see JSON `comparator_reasoner_uncertainty`.)

## External confidence (cross-model agreement share) — calibration

- Definition: `cross_model_agreement_count / 3  (predeclared, not fitted)`
- **ECE (10-bin): 0.0804**, **Brier: 0.1024**, **AUROC for correctness: 0.7499**

| Bin | n | Mean score | Empirical acc | Gap |
|---|---:|---:|---:|---:|
| [0.3,0.4) | 48 | 0.333 | 0.583 | +0.250 |
| [0.6,0.7) | 238 | 0.667 | 0.790 | +0.123 |
| [0.9,1.0) | 464 | 1.000 | 0.959 | -0.041 |

## Failure prediction

- **External risk score AUROC for failure: 0.7806**
- Evidence-valid vs correctness:
  - evidence_valid=False: 50/59 = 84.7%
  - evidence_valid=True: 611/691 = 88.4%
- **Parse-repair count AUROC for failure: 0.6003** (528/750 rows took a deterministic repair — repairs are common, not constant, so the signal is real):
  - no_repair: 207/222 = 93.2%
  - any_repair: 454/528 = 86.0%
---

**Reading.** External signals rank the subject's correctness (agreement-share AUROC 0.750; risk-score failure AUROC 0.781); self-reported confidence does not (near-constant). The honest calibration story is that reliability must be read off external corroboration, not the model's own certainty — the same lesson the architecture arc reached (Insight #3).
