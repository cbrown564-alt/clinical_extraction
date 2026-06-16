# Gan 2026 v0.7 Label-Binding — validation750 + family CV

Date: 2026-06-15

Cycle-3 GATE step. validation750 development split (NOT test450). Candidate: llm_only_direct_labeler prompt v0.7 (label binding) live, temp 0. Baseline: llm_only_direct_labeler prompt v0.5 re-parsed from gan2026_llm_only_direct_labeler_v05_validation750_gpt41mini_2026-06-09.jsonl (no new calls).

Predeclaration: `experiments\gan2026_label_binding_v0_7_predeclaration_2026-06-15.md`

## Overall Purist (validation750)

- v0.7 Purist: 469 / 750
- v0.5 baseline Purist: 575 / 750
- Net vs v0.5: -106
- wrong->correct vs v0.5: 43
- correct->wrong vs v0.5: 149

## Held-out-family CV (leave-one-boundary-band-out)

**gap_robust: False**

Reasons (empty = clean): ['aggregate net Purist gain -106 <= 0', 'held-out bands regress (net Purist gain < 0): band_zero, band_submonthly, band_monthly, band_weekly, band_daily', 'held-out bands below changed-label precision 0.5: band_zero, band_unknown, band_submonthly, band_monthly, band_weekly, band_daily']
Aggregate: {'rows': 750, 'changed_labels': 365, 'wrong_to_correct': 43, 'correct_to_wrong': 149, 'net_purist_gain': -106, 'changed_label_precision': 0.1178}
Worst held-out fold: {'family': 'band_weekly', 'net_purist_gain': -45}

| Band (held out) | rows | changed | w->c | c->w | net | changed-label prec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| band_zero | 112 | 41 | 1 | 4 | -3 | 0.0244 |
| band_unknown | 170 | 66 | 19 | 8 | +11 | 0.2879 |
| band_submonthly | 87 | 43 | 0 | 20 | -20 | 0.0 |
| band_monthly | 141 | 84 | 4 | 40 | -36 | 0.0476 |
| band_weekly | 177 | 108 | 16 | 61 | -45 | 0.1481 |
| band_daily | 63 | 23 | 3 | 16 | -13 | 0.1304 |

## Per-band transition summary (candidate vs baseline)

| Band | rows | changed | w->c | c->w |
| --- | ---: | ---: | ---: | ---: |
| band_zero | 112 | 41 | 1 | 4 |
| band_unknown | 170 | 66 | 19 | 8 |
| band_submonthly | 87 | 43 | 0 | 20 |
| band_monthly | 141 | 84 | 4 | 40 |
| band_weekly | 177 | 108 | 16 | 61 |
| band_daily | 63 | 23 | 3 | 16 |

## Interpretation

A gap_robust verdict means no held-out boundary band silently regresses and every changed band clears the changed-label precision bar. This is within-validation stability, necessary but NOT sufficient for test450: it is not a holdout result.
