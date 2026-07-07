# ExECTv2 Calibration Signal Probe (dev140)

- Generated: `2026-07-07` by `experiments/build_exectv2_calibration_signal_probe.py`
- Cells: `1719`
- Boundary: dev140 replay over saved same-core model-swap and multi-temperature artifacts; no model calls, no full-200 or holdout rows.

## Per-family AUROC (error vs correct)

| Family | Cells | Cross-model agreement | Self-consistency entropy |
| --- | ---: | ---: | ---: |
| Diagnosis | 520 | 0.6291 | 0.5879 |
| SeizureFrequency | 421 | 0.5479 | 0.5662 |
| Prescription | 463 | 0.5000 | 0.5000 |
| Investigations | 315 | 0.6067 | 0.6007 |
| **pooled** | 1719 | **0.5958** | **0.5776** |

## Predeclared verdicts

- **H1 (cross-model agreement generalizes):** `refuted_does_not_generalize`. AUROC > 0.7 on >=2 of the 3 non-SF families, or on the pooled population. Non-SF families above bar: `[]`.
- **H2 (self-consistency is orthogonal):** `adds_orthogonal_signal`. Spearman rho = `0.5676` (redundancy bar |rho| > 0.7).

## Signal distributions

- Cross-model agreement cluster sizes: `{'1': 123, '2': 284, '3': 1312}`
- Self-consistency entropy mean: `0.0626`

