# P0.3 — External-Signal Calibration (ECE / Brier / Failure-Prediction AUROC)

Date: 2026-06-17  ·  Split: validation750  ·  Model calls: 0

## Self-confidence is degenerate (and the subject has none)

Nearest logged self-confidence is `decision_record.uncertainty` ([comparator: V12-full-gpt4.1] reasoner self-report); the subject single-SE-mini layer emits none.

| Uncertainty bucket | n | Purist acc |
|---|---:|---:|
| low | 739 | 88.2% |
| medium | 10 | 90.0% |
| missing | 1 | 0.0% |

The dominant bucket holds **98.5%** of rows — self-report is near-constant and cannot rank correctness.

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

- Parse-repair count is a non-signal here: the production path logs 0 parse failures / 0 evidence loss across 2,295 rows (RQ5/RQ8), so it has no variance to calibrate against.

---

**Reading.** External signals rank the subject's correctness (agreement-share AUROC 0.750; risk-score failure AUROC 0.781); self-reported confidence does not (near-constant). The honest calibration story is that reliability must be read off external corroboration, not the model's own certainty — the same lesson the architecture arc reached (Insight #3).
