# P1.2 — Per-Family Error-Parity on Frozen test450 (Fairness)

## Aggregate-Only Holdout Readout

Date: 2026-06-17  ·  Split: test450 (frozen holdout)  ·  Model calls: 0

_frozen aggregate-only holdout readout; no row-level test inspection._  Frozen classifier `labels.classify_boundary_families (validation classifier)` sha256 `2fe000d4c3c1735d…`.

Subject overall Purist accuracy: 364/448 = 81.2%.

### Boundary bands (partition)

| Band | n | Purist acc | Error rate |
|---|---:|---:|---:|
| band_submonthly | 59 | 69.5% | 30.5% |
| band_weekly | 104 | 76.9% | 23.1% |
| band_monthly | 81 | 80.2% | 19.8% |
| band_daily | 36 | 83.3% | 16.7% |
| band_unknown | 102 | 87.3% | 12.7% |
| band_zero | 66 | 89.4% | 10.6% |

- **Error-rate spread (max−min): 19.9%**, accuracy CV 0.082
- Worst band: **band_submonthly** 69.5% (n=59); worst qualitative family: **band_submonthly** 69.5% (n=59)
- Parity flag (> 10% below overall): band_submonthly

### Qualitative families (overlapping)

| Family | n | Purist acc | Error rate |
|---|---:|---:|---:|
| band_submonthly | 59 | 69.5% | 30.5% |
| cluster_burden | 213 | 76.1% | 23.9% |
| band_weekly | 104 | 76.9% | 23.1% |
| seizure_free_duration | 65 | 78.5% | 21.5% |
| band_monthly | 81 | 80.2% | 19.8% |
| band_daily | 36 | 83.3% | 16.7% |
| band_unknown | 102 | 87.3% | 12.7% |
| band_zero | 66 | 89.4% | 10.6% |

---

**Reading.** The holdout confirms the validation parity picture on the same frozen taxonomy: the disparity concentrates in the over-reading qualitative families and the rate bands rather than in `band_unknown`. Family is a real reliability slice on the locked split, not just a validation artifact.
