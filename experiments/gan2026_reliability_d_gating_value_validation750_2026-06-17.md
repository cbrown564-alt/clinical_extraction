# Variant-D as a Gate on the Single-Model Architecture (validation750)

Date: 2026-06-17 · arch: single gpt-4.1-mini SE pass (primary) · n=748 · model calls 0

Base accuracy (no gate): **88.4%** (error 11.6%). D failure-prediction AUROC: **0.684**.

**The bar:** random abstention sheds errors in proportion to the abstained fraction and leaves selective accuracy unchanged in expectation. A gate is useful only if it beats that — higher selective accuracy and abstention precision above the base error rate.

## D gate (the signal the single-model arch actually has)

| Coverage | Selective acc | 95% CI | Abstention precision | vs random | Errors shed | vs random shed |
|---:|---:|:--|---:|---:|---:|---:|
| 100% | 88.4% | 85.9%–90.5% | nan% | +nan% | 0 | 0% vs 0% |
| 95% | 89.0% | 86.5%–91.1% | 24.3% | +12.7% | 9 | 10% vs 5% |
| 90% | 90.5% | 88.0%–92.5% | 30.7% | +19.0% | 23 | 26% vs 10% |
| 80% | 92.1% | 89.7%–94.0% | 26.7% | +15.0% | 40 | 46% vs 20% |
| 70% | 93.1% | 90.6%–95.0% | 22.8% | +11.1% | 51 | 59% vs 30% |
| 50% | 95.2% | 92.5%–96.9% | 18.4% | +6.8% | 69 | 79% vs 50% |

## External composite gate (context only — needs 3 models, unavailable single-model)

| Coverage | Selective acc | Abstention precision | vs random |
|---:|---:|---:|---:|
| 100% | 88.4% | nan% | +nan% |
| 95% | 89.6% | 35.1% | +23.5% |
| 90% | 90.6% | 32.0% | +20.4% |
| 80% | 93.1% | 30.7% | +19.0% |
| 70% | 94.5% | 25.9% | +14.3% |
| 50% | 97.9% | 21.1% | +9.5% |

_External composite needs 3 models and is NOT available to the single-model architecture; shown only as the ceiling a multi-model gate would reach._

## Reading

At 90% coverage the D gate lifts accuracy from 88.4% to 90.5% and its abstention precision is 30.7% vs the random bar 11.6% (+19.0%). Judge practical usefulness by how far selective accuracy and abstention precision sit above the random bar, and whether the lift justifies one extra mini call per row plus the discarded coverage.
