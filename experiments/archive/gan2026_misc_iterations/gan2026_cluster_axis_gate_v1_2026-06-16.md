# Gan 2026 C6: Cluster-Axis RETENTION Gate v1 (No-Call Replay)

Date: 2026-06-16

No-call post-hoc replay over v0.4 fresh-evidence outputs. No model calls. No test450 rows were read until step 3 authorization was confirmed.

## Gate Definition

Fires when ALL hold:
- (a) v0.4 final label is a PLAIN rate (numeric, no cluster/unknown/seizure-free/no-reference/multiple-per)
- (b) note contains explicit recurring-cluster language: "in clusters", "group together", "runs of", "bursts of", "several over consecutive", "clusters of seizures"
- (c) the rewrite changes the Purist bucket

Rewrite: 'N per X' -> 'N cluster per X, multiple per cluster'

## Validation750 Results

- Baseline Purist: 682/750
- Gated Purist: 677/750
- Rows touched by gate: 7
- Wrong->Correct (W->C): 1
- Correct->Wrong (C->W): 6
- Net Purist: -5

### Touched Rows

| idx | gold | v0.4 pred | cluster rewrite | gold_purist | gated_purist | transition |
| --- | --- | --- | --- | --- | --- | --- |
| 40 | `4 per week` | `4 per week` | `4 cluster per week, multiple per cluster` | `seizure_freq_more1week_less1day` | `seizure_freq_1ormore_daily` | correct_to_wrong |
| 5682 | `2 to 4 per month` | `2 to 4 per month` | `2 to 4 cluster per month, multiple per cluster` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1week_less1day` | correct_to_wrong |
| 7275 | `1 per month` | `3 per 12 week` | `3 cluster per 12 week, multiple per cluster` | `seizure_freq_1_per_mon` | `seizure_freq_more1mon_less1week` | correct_to_wrong |
| 9365 | `1 per 2 day` | `1 per 2 day` | `1 cluster per 2 day, multiple per cluster` | `seizure_freq_more1week_less1day` | `seizure_freq_1ormore_daily` | correct_to_wrong |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | `1 cluster per 4 to 5 week, multiple per cluster` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1mon_less1week` | wrong_to_correct |
| 16757 | `13 per 6 month` | `13 per 6 month` | `13 cluster per 6 month, multiple per cluster` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1week_less1day` | correct_to_wrong |
| 16839 | `9 per 4 month` | `5 per 2 month` | `5 cluster per 2 month, multiple per cluster` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1week_less1day` | correct_to_wrong |

## Precision Check (Genuine-Rate Regressions)

- Genuine-rate regressions (C->W where gold is plain rate): 6
- Row indices: [40, 5682, 7275, 9365, 16757, 16839]
- FAIL: genuine-rate regressions detected; gate is too leaky

## Held-Out-Family CV

- gap_robust: **False**
- Aggregate net Purist gain: -5
- Worst held-out fold: {'family': 'band_monthly', 'net_purist_gain': -3}
- Regressing held-out families: ['band_monthly', 'band_weekly']
- Low-precision held-out families: ['band_monthly', 'band_weekly']
- Reasons for non-robust: ['aggregate net Purist gain -5 <= 0', 'held-out bands regress (net Purist gain < 0): band_monthly, band_weekly', 'held-out bands below changed-label precision 0.5: band_monthly, band_weekly']

### Per-Band Transition Summary

| Band | rows | W->C | C->W | net | precision |
| --- | ---: | ---: | ---: | ---: | --- |
| band_zero | 112 | 0 | 0 | +0 | n/a |
| band_unknown | 170 | 0 | 0 | +0 | n/a |
| band_submonthly | 87 | 0 | 0 | +0 | n/a |
| band_monthly | 141 | 1 | 4 | -3 | 0.2 |
| band_weekly | 177 | 0 | 2 | -2 | 0.0 |
| band_daily | 63 | 0 | 0 | +0 | n/a |

## Test450 Results

GATE DID NOT REACH TEST: See stop-rule evaluation in summary.

## Decision

STOP RULE triggered: gate did not reach test. Reasons: 6 genuine-rate regressions; net Purist -5 < 0; gap_robust=False (['aggregate net Purist gain -5 <= 0', 'held-out bands regress (net Purist gain < 0): band_monthly, band_weekly', 'held-out bands below changed-label precision 0.5: band_monthly, band_weekly']). Gate needs tightening before test application.
