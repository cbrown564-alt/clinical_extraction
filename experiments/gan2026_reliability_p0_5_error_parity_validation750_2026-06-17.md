# P0.5 — Error-Parity Gap Across Families / Bands (Fairness)

Date: 2026-06-17  ·  Split: validation750  ·  Model calls: 0

Subject overall Purist accuracy: 661/750 = 88.1%. Subgroups from `labels.classify_boundary_families (frozen validation taxonomy)`.

## Boundary bands (partition every row exactly once)

| Band | n | Purist acc | Error rate |
|---|---:|---:|---:|
| band_daily | 63 | 84.1% | 15.9% |
| band_weekly | 177 | 84.7% | 15.3% |
| band_submonthly | 87 | 87.4% | 12.6% |
| band_monthly | 141 | 88.7% | 11.3% |
| band_unknown | 170 | 90.6% | 9.4% |
| band_zero | 112 | 92.0% | 8.0% |

- **Error-rate spread (max−min): 7.8%**
- **Accuracy coefficient of variation: 0.032**
- Worst band: **band_daily** at 84.1% (n=63)
- Parity flag: none beyond the 10% margin

## Qualitative families (overlapping)

| Family | n | Purist acc | Error rate |
|---|---:|---:|---:|
| seizure_free_duration | 115 | 82.6% | 17.4% |
| band_daily | 63 | 84.1% | 15.9% |
| band_weekly | 177 | 84.7% | 15.3% |
| cluster_burden | 323 | 85.4% | 14.6% |
| band_submonthly | 87 | 87.4% | 12.6% |
| band_monthly | 141 | 88.7% | 11.3% |
| band_unknown | 170 | 90.6% | 9.4% |
| band_zero | 112 | 92.0% | 8.0% |

_The transition-based promotion gate is family_cv_promotion.gap_robust (no held-out band regresses); here the subject's own per-band disparity is the standalone fairness flag._

---

**Reading.** Per-band parity is fairly tight (error-rate spread 7.8%, CV 0.032, no band beyond the 10% margin). The disparity lives less in the partitioning bands than in the qualitative over-reading families: **seizure_free_duration** (82.6%) and `cluster_burden` are the weakest subgroups, and among bands the rate bands (`band_daily`, `band_weekly`) trail — not `band_unknown`, which sits above the mean because most unknown rows are handled correctly and the over-reading is a minority within it. The cluster-burden and seizure-free-duration cadence families are the fairness face of the residual the accuracy work localized. On synthetic templated letters demographic fairness is structurally unmeasurable (P0.6); clinical-family parity is the available axis.
