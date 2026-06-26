# Gan 2026 Fresh-Evidence Triage v0.10 — Cycle C5 validation750

Date: 2026-06-16

Cycle C5 GATE step. validation750 development split (NOT test450). Candidate: fresh_evidence_reasoner gan2026_fresh_evidence_reasoner_v0_10_triage (Cycle C5 confidence-gated triage scaffold) live, temp 0. Baseline: fresh_evidence_reasoner v0.4 from gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl.

Predeclaration: `experiments\gan2026_fresh_evidence_triage_v0_10_predeclaration_2026-06-16.md`

## Overall Purist (validation750)

- v0.10 triage Purist: 601 / 750
- v0.4 baseline Purist: 682 / 750
- Net vs v0.4: -81
- wrong->correct vs v0.4: 14
- correct->wrong vs v0.4: 95

## Held-out-family CV (leave-one-boundary-band-out)

**gap_robust: False**

Reasons (empty = clean): ['aggregate net Purist gain -81 <= 0', 'held-out bands regress (net Purist gain < 0): band_zero, band_unknown, band_submonthly, band_monthly, band_weekly, band_daily', 'held-out bands below changed-label precision 0.5: band_zero, band_unknown, band_submonthly, band_monthly, band_weekly, band_daily']
Aggregate: {'rows': 750, 'changed_labels': 160, 'wrong_to_correct': 14, 'correct_to_wrong': 95, 'net_purist_gain': -81, 'changed_label_precision': 0.0875}
Worst held-out fold: {'family': 'band_submonthly', 'net_purist_gain': -22}

| Band (held out) | rows | changed | w->c | c->w | net | changed-label prec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| band_zero | 112 | 29 | 0 | 20 | -20 | 0.0 |
| band_unknown | 170 | 48 | 10 | 22 | -12 | 0.2083 |
| band_submonthly | 87 | 30 | 1 | 23 | -22 | 0.0333 |
| band_monthly | 141 | 28 | 2 | 16 | -14 | 0.0714 |
| band_weekly | 177 | 18 | 1 | 10 | -9 | 0.0556 |
| band_daily | 63 | 7 | 0 | 4 | -4 | 0.0 |

## Per-band transition summary (v0.10 vs v0.4 baseline)

| Band | rows | changed | w->c | c->w |
| --- | ---: | ---: | ---: | ---: |
| band_zero | 112 | 29 | 0 | 20 |
| band_unknown | 170 | 48 | 10 | 22 |
| band_submonthly | 87 | 30 | 1 | 23 |
| band_monthly | 141 | 28 | 2 | 16 |
| band_weekly | 177 | 18 | 1 | 10 |
| band_daily | 63 | 7 | 0 | 4 |

## 11-Row Attribution Table (predeclared no-correct rows)

| Row | Gold | Baseline (v0.4) | New (v0.10) | Now Correct? | Triage Reason | Ambiguity Class | Action |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 5534 | `1 per multiple month` | `1 per 2 week` | `unknown` | True | `single_anchor_last_event` | `last_event_only_unknown` | `replace_with_fresh_evidence_final` |
| 6321 | `unknown` | `2 per 3 month` | `None` | False | `None` | `None` | `None` |
| 6368 | `unknown` | `3 per 6 week` | `3 per 6 week` | False | `usable_rate` | `explicit_count_window` | `keep_original_structured_event_final` |
| 6571 | `unknown` | `1 per 4 month` | `unknown` | True | `single_anchor_last_event` | `last_event_only_unknown` | `replace_with_fresh_evidence_final` |
| 9937 | `1 cluster per month, multiple per cluster` | `multiple per month` | `None` | False | `None` | `None` | `None` |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | `1 cluster per 4 to 5 week ( per cluster unknown)` | False | `cluster_retention` | `cluster_axis_incomplete` | `replace_with_fresh_evidence_final` |
| 11216 | `unknown` | `seizure free for 4 month` | `seizure free for 4 month` | False | `seizure_free_check` | `explicit_seizure_free_duration` | `keep_original_structured_event_final` |
| 11254 | `unknown` | `seizure free for 3 month` | `unknown` | True | `single_anchor_last_event` | `last_event_only_unknown` | `replace_with_fresh_evidence_final` |
| 11272 | `unknown` | `seizure free for 3 month` | `unknown` | True | `single_anchor_last_event` | `last_event_only_unknown` | `replace_with_fresh_evidence_final` |
| 13209 | `1 per 8 month` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | False | `cluster_retention` | `cluster_axis_complete` | `keep_original_structured_event_final` |
| 14025 | `unknown` | `2 per 6 week` | `2 per 6 week` | False | `no_triage_issue` | `explicit_count_window` | `keep_original_structured_event_final` |

## Genuine-Rate Regression Check (stop-rule)

Genuine-rate rows that regressed correct->wrong: 73

| Row | Band | Gold | Baseline | New | Triage Reason |
| ---: | --- | --- | --- | --- | --- |
| 694 | band_weekly | `1 per week` | `1 per week` | `None` | `usable_rate` |
| 1094 | band_weekly | `3 to 5 per week` | `3 to 5 per week` | `unknown` | `explicitly_provoked_or_transient` |
| 1357 | band_daily | `1 per day` | `1 per day` | `None` | `None` |
| 1880 | band_weekly | `8 per 2 month` | `8 per 2 month` | `7 per 2 month` | `usable_rate` |
| 3118 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 3137 | band_zero | `seizure free for multiple month` | `seizure free for 6 month` | `unknown` | `single_anchor_last_event` |
| 3623 | band_daily | `7 per week` | `7 per week` | `None` | `None` |
| 4842 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 4951 | band_zero | `seizure free for multiple month` | `seizure free for 8 month` | `unknown` | `single_anchor_last_event` |
| 5121 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 5141 | band_zero | `seizure free for multiple month` | `seizure free for 1.5 month` | `unknown` | `single_anchor_last_event` |
| 5528 | band_monthly | `1 per month` | `1 per month` | `unknown` | `explicitly_provoked_or_transient` |
| 5995 | band_submonthly | `1 per 3 months` | `3 per 8 month` | `unknown` | `explicitly_provoked_or_transient` |
| 6251 | band_submonthly | `1 per 1 to 2 month` | `1 per 2 month` | `None` | `None` |
| 6509 | band_weekly | `1 per week` | `2 per 2 week` | `None` | `None` |
| 7401 | band_monthly | `2 cluster per 6 week, 1 to 2 per cluster` | `1 to 3 per month` | `unknown` | `cluster_retention` |
| 7615 | band_weekly | `3 to 7 per month` | `3 to 6 per month` | `2 per 10 month` | `cluster_retention` |
| 7818 | band_zero | `seizure free for 2 years` | `seizure free for 2 year` | `unknown` | `single_anchor_last_event` |
| 7834 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 7911 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 8160 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `1 per month` | `no_triage_issue` |
| 8180 | band_zero | `seizure free for multiple month` | `seizure free for 6 month` | `unknown` | `single_anchor_last_event` |
| 8188 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 8203 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 8730 | band_zero | `seizure free for 6 month` | `seizure free for 6 month` | `unknown` | `single_anchor_last_event` |
| 8820 | band_zero | `seizure free for 7 month` | `seizure free for 7 month` | `unknown` | `single_anchor_last_event` |
| 8924 | band_zero | `seizure free for multiple month` | `seizure free for 5 month` | `unknown` | `single_anchor_last_event` |
| 9063 | band_zero | `seizure free for 8 month` | `seizure free for 8 month` | `unknown` | `single_anchor_last_event` |
| 10371 | band_zero | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | `single_anchor_last_event` |
| 10967 | band_weekly | `3 cluster per month, 4 to 5 per cluster` | `12 to 15 per month` | `unknown` | `cluster_retention` |
| 12537 | band_daily | `1 per day` | `1 per day` | `multiple per week` | `usable_rate` |
| 12823 | band_weekly | `9 per month` | `9 per month` | `9 per year` | `usable_rate` |
| 13008 | band_weekly | `4 per month` | `4 per month` | `unknown` | `explicitly_provoked_or_transient` |
| 13058 | band_submonthly | `2 per 7 month` | `2 per 7 month` | `unknown` | `single_anchor_last_event` |
| 13122 | band_submonthly | `3 per year` | `3 per 1 year` | `unknown` | `explicitly_provoked_or_transient` |
| 13149 | band_submonthly | `3 per year` | `3 per 1 year` | `unknown` | `single_anchor_last_event` |
| 13290 | band_submonthly | `4 per 6 month` | `2 per 6 month` | `unknown` | `single_anchor_last_event` |
| 13858 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `no_triage_issue` |
| 13889 | band_zero | `seizure free for multiple month` | `seizure free for multiple year` | `unknown` | `no_triage_issue` |
| 14530 | band_monthly | `2 per 2 month` | `2 per 2 month` | `unknown` | `single_anchor_last_event` |
| 14540 | band_submonthly | `2 per 8 month` | `2 per 8 month` | `unknown` | `single_anchor_last_event` |
| 14562 | band_submonthly | `3 per 6 month` | `3 per 6 month` | `unknown` | `single_anchor_last_event` |
| 14581 | band_submonthly | `2 per 3 month` | `2 per 3 month` | `unknown` | `single_anchor_last_event` |
| 14592 | band_submonthly | `3 per 5 month` | `3 per 5 month` | `None` | `None` |
| 14611 | band_submonthly | `2 per 4 month` | `2 per 4 month` | `unknown` | `single_anchor_last_event` |
| 14628 | band_monthly | `2 per 2 month` | `2 per 2 month` | `unknown` | `single_anchor_last_event` |
| 14645 | band_submonthly | `2 per 6 month` | `2 per 6 month` | `unknown` | `single_anchor_last_event` |
| 14662 | band_submonthly | `3 per 4 month` | `3 per 4 month` | `unknown` | `explicitly_provoked_or_transient` |
| 14672 | band_submonthly | `3 per 8 month` | `3 per 8 month` | `None` | `None` |
| 14810 | band_monthly | `1 per month` | `1 per month` | `seizure free for 1 month` | `seizure_free_check` |
| 14821 | band_monthly | `1 per month` | `1 per month` | `seizure free for multiple year` | `seizure_free_check` |
| 14872 | band_monthly | `1 per month` | `1 per 1 month` | `seizure free for multiple year` | `seizure_free_check` |
| 14943 | band_submonthly | `1 per 3 month` | `1 per 3 month` | `unknown` | `single_anchor_last_event` |
| 14965 | band_submonthly | `1 per 3 month` | `1 per 3 month` | `unknown` | `single_anchor_last_event` |
| 14973 | band_monthly | `1 per month` | `1 per 1 month` | `unknown` | `single_anchor_last_event` |
| 15267 | band_submonthly | `3 per 14 month` | `3 per 14 month` | `unknown` | `explicitly_provoked_or_transient` |
| 16021 | band_monthly | `9 per 3 month` | `9 per 3 month` | `8 per 2 month` | `usable_rate` |
| 16394 | band_weekly | `1 per 2 to 4 day` | `1 per 2 to 4 day` | `3 per 2 month` | `cluster_retention` |
| 16574 | band_weekly | `1 per 4 day` | `1 per 4 day` | `unknown` | `cluster_retention` |
| 16645 | band_submonthly | `5 per 7 month` | `5 per 7 month` | `unknown` | `single_anchor_last_event` |
| 16674 | band_monthly | `7 per 6 month` | `6 per 4 month` | `None` | `None` |
| 16697 | band_submonthly | `3 per 6 month` | `3 per 4 month` | `unknown` | `single_anchor_last_event` |
| 16714 | band_submonthly | `5 per 6 month` | `5 per 6 month` | `unknown` | `single_anchor_last_event` |
| 16728 | band_submonthly | `4 per 6 month` | `4 per 6 month` | `unknown` | `single_anchor_last_event` |
| 16750 | band_submonthly | `6 per 7 month` | `6 per 7 month` | `unknown` | `single_anchor_last_event` |
| 16757 | band_monthly | `13 per 6 month` | `13 per 6 month` | `None` | `None` |
| 16758 | band_monthly | `9 per 5 month` | `9 per 5 month` | `unknown` | `single_anchor_last_event` |
| 16772 | band_monthly | `9 per 5 month` | `9 per 5 month` | `unknown` | `explicitly_provoked_or_transient` |
| 16774 | band_monthly | `19 per 7 month` | `3 per month` | `1 cluster per 2 month, multiple per cluster` | `cluster_retention` |
| 16780 | band_submonthly | `3 per 7 month` | `3 per 7 month` | `unknown` | `single_anchor_last_event` |
| 16824 | band_monthly | `11 per 5 month` | `11 per 5 month` | `1 per month` | `no_triage_issue` |
| 16839 | band_monthly | `9 per 4 month` | `5 per 2 month` | `None` | `None` |
| 17146 | band_daily | `1 per day` | `1 per day` | `multiple per week` | `usable_rate` |

## Decision

**reject**

Stop rule: reject if net Purist < 0 OR family-CV not gap_robust OR any genuine-rate band regresses. Confidence gate is too loose if regressions > 0.