# Gan 2026 C6: Cluster-Axis RETENTION Gate v1 (No-Call Replay)

Date: 2026-06-16

No-call post-hoc replay over v0.4 fresh-evidence outputs. No model calls. No test450 rows were read until step 3 authorization was confirmed.

## Gate Definition (v1-tightened)

Original v1 pattern fired too broadly (7 rows, 6 genuine-rate regressions, net=-5). Tightened to two high-precision triggers only.

Fires when ALL hold:
- (a) v0.4 final label is a PLAIN rate (numeric, no cluster/unknown/seizure-free/no-reference/multiple-per)
- (b) note contains TIGHT recurring-cluster language: "group(s/ed/ing) together" (cadence-defining grouping) OR "in clusters...every N" (cadence-explicit interval)
  - Excluded from original v1: 'runs of', 'bursts of', 'in clusters' in isolation (too many false positives)
- (c) the rewrite changes the Purist bucket

Rewrite: 'N per X' -> 'N cluster per X, multiple per cluster'

## Validation750 Results

- Baseline Purist: 682/750
- Gated Purist: 683/750
- Rows touched by gate: 1
- Wrong->Correct (W->C): 1
- Correct->Wrong (C->W): 0
- Net Purist: +1

### Touched Rows

| idx | gold | v0.4 pred | cluster rewrite | gold_purist | gated_purist | transition |
| --- | --- | --- | --- | --- | --- | --- |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | `1 cluster per 4 to 5 week, multiple per cluster` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1mon_less1week` | wrong_to_correct |

## Precision Check (Genuine-Rate Regressions)

- Genuine-rate regressions (C->W where gold is plain rate): 0
- PASS: zero genuine-rate regressions (gate is precision-safe)

## Held-Out-Family CV

- gap_robust: **True**
- Aggregate net Purist gain: 1
- Worst held-out fold: {'family': 'band_zero', 'net_purist_gain': 0}
- Regressing held-out families: []
- Low-precision held-out families: []
- Reasons for non-robust: []

### Per-Band Transition Summary

| Band | rows | W->C | C->W | net | precision |
| --- | ---: | ---: | ---: | ---: | --- |
| band_zero | 112 | 0 | 0 | +0 | n/a |
| band_unknown | 170 | 0 | 0 | +0 | n/a |
| band_submonthly | 87 | 0 | 0 | +0 | n/a |
| band_monthly | 141 | 1 | 0 | +1 | 1.0 |
| band_weekly | 177 | 0 | 0 | +0 | n/a |
| band_daily | 63 | 0 | 0 | +0 | n/a |

## Test450 Results (Authorised Gate Applied)

- Baseline Purist (v0.4): 379/450
- Gated Purist: 379/450
- Rows touched by gate: 0
- Wrong->Correct (W->C): 0
- Correct->Wrong (C->W): 0
- Net Purist: +0
- Delta vs 379 baseline: +0

### Test Touched Rows

| idx | gold | v0.4 pred | cluster rewrite | gold_purist | gated_purist | transition |
| --- | --- | --- | --- | --- | --- | --- |

## Decision

Gate cleared precision check but test delta is +0. Cluster-axis gate is precision-safe but the lift is limited.
