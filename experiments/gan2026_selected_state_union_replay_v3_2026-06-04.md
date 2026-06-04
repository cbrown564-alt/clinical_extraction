# Gan 2026 Selected-State Union Replay V3

This is a no-call validation-development replay over the saved 75-row rich selected-state hard panel and the controlled v3 boundary-candidate output.

## Outcome

The gated v3 union is coherent as a downstream selected-state input artifact, but the primary v3 candidate-state projection is not a final label policy. It is scorable on 22 rows and correct on 16 of them; a deterministic safety-floor replay preserves the prior comparator score with 0 W->C and 0 C->W changes.

## Claim Boundary

Validation-development no-call selected-state replay over saved rich selected states plus the controlled v3 boundary-candidate artifact. No locked-test inspection, live model call, scorer-policy change, whole-pipeline promotion, or benchmark-comparable claim is authorized.

## Artifacts

- JSONL: `experiments/gan2026_selected_state_union_replay_v3_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selected_state_union_replay_v3_2026-06-04.json`
- Saved selected-state replay: `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.jsonl`
- V3 boundary candidates: `experiments/gan2026_selective_boundary_candidate_experiment_v3_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| rows with v3 boundary candidates | 22 |
| rows with union verified candidates | 75 |
| comparator correct rows | 37 |
| primary v3 projection scorable rows | 22 |
| primary v3 projection correct rows | 16 |
| safety floor correct rows | 37 |
| safety w to c against comparator rows | 0 |
| safety c to w against comparator rows | 0 |
| primary v3 c to w against comparator rows | 6 |
| known real model error rows carried | 1 |

## V3 Boundary Rows

| Row | Gold | Comparator | Primary v3 projection | Safety-floor label | Delta | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 338 | `multiple per month` | `multiple per month` | `1 cluster per 4 week, multiple per cluster` | `multiple per month` | `C->C` |  |
| 1707 | `multiple per week` | `multiple per week` | `1 per week` | `multiple per week` | `C->C` |  |
| 3356 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 5974 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 6077 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 6131 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 6244 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 6321 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 6501 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 6571 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 6987 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 9888 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 cluster per 4 to 5 week, multiple per cluster` | `1 cluster per 4 to 5 week, multiple per cluster` | `1 cluster per 4 to 5 week, multiple per cluster` | `C->C` |  |
| 9955 | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `C->C` |  |
| 10266 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 10618 | `unknown, 4 to 6 per cluster` | `unknown, 4 to 6 per cluster` | `1 cluster per day, 4 to 6 per cluster` | `unknown, 4 to 6 per cluster` | `C->C` |  |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `C->C` |  |
| 12456 | `1 per day` | `1 per day` | `unknown` | `1 per day` | `C->C` |  |
| 14025 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 14076 | `unknown` | `unknown` | `unknown` | `unknown` | `C->C` |  |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `C->C` | known real model cluster-cadence error |
| 15834 | `5 per week` | `5 per week` | `unknown` | `5 per week` | `C->C` |  |

## Interpretation

- Keep v3 boundary candidates as a useful selected-state input surface, not as final labels.
- Keep row 15593 visible as a real v3 model error before any broader replay.
- The safety-floor result is diagnostic because it preserves deterministic-correct rows by policy.
