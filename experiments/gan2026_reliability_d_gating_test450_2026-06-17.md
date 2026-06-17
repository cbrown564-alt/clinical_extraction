# Variant-D Gating on Frozen test450

## Aggregate-Only Holdout Readout

Date: 2026-06-17 · Split: test450 (frozen holdout) · arch: single gpt-4.1-mini SE pass (primary)

_frozen aggregate-only holdout readout; no row-level test inspection._

**Asymmetry.** Single-model self-signal computed live identically on both splits — NO degradation (unlike P1.1's external score). Apples-to-apples holdout test.

Frozen transforms (predeclared, hashed before touching test450): reviewer `c3ea06caf2399c02…`, readout `45c96e36a5157d99…`.

- Base accuracy (no gate): **80.9%** (CI 77.0%–84.3%), error 19.1%.
- D failure-prediction AUROC: **0.649**.

## Gating operating points

| Coverage | Selective acc | 95% CI | Abstention precision | 95% CI | vs random | Errors shed |
|---:|---:|:--|---:|:--|---:|---:|
| 95% | 82.0% | 78.1%–85.4% | 40.9% | 23.3%–61.3% | +21.8% | 9 |
| 90% | 82.5% | 78.5%–85.9% | 33.3% | 21.4%–47.9% | +14.2% | 15 |
| 80% | 85.6% | 81.5%–88.8% | 37.8% | 28.5%–48.1% | +18.7% | 34 |
| 70% | 86.7% | 82.5%–90.0% | 32.6% | 25.3%–40.9% | +13.5% | 44 |
| 50% | 88.0% | 83.1%–91.6% | 26.2% | 20.9%–32.3% | +7.1% | 59 |

[comparator: validation750] base acc 0.884, AUROC 0.684; 90% cov selective acc 0.905, abstention precision 0.307 vs random 0.116.

---

**Reading.** On the locked holdout the single-model variant-D gate ranks errors at AUROC 0.649. Judge practical usefulness against the predeclared criterion: AUROC CI above chance, abstention precision at 90% coverage above the random bar (base error rate), and a positive monotone selective-accuracy lift. The val→test movement is itself the finding.
