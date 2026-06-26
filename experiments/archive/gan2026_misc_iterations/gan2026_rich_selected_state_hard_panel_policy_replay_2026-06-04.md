# Gan 2026 Rich Selected-State Hard-Panel Deterministic Policy Replay

Date: 2026-06-04

Mode: deterministic projection-only replay over saved rich selected-state JSONL; no live model calls.

- Source JSONL: `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.jsonl`
- Replay JSONL: `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.jsonl`
- Claim boundary: validation-development component replay, not holdout or benchmark-comparable.

## Summary

- Rows replayed: 75
- Revised parseable labels: 75/75
- Orientation exact label matches before policy replay: 26/75
- Orientation exact label matches after policy replay: 37/75
- Changed projected labels: 26
- Wrong to right: 11
- Right to wrong: 0

## Policy Changes Exercised

- Render explicit cluster cadence before falling back to unknown per-cluster burden.
- Render cluster cadence plus per-cluster burden as Gan cluster syntax when both axes are present.
- Infer one cluster per saved observation window only when the selected state ties the whole window to one cluster and exposes per-cluster burden.
- Use a seizure-free gap followed by clustering as cluster cadence when the saved state exposes that boundary.
- Treat trigger/context language as non-blocking, while keeping exclusive/conditional event states and ambiguous single-breakthrough windows as unknown.
- Abstain on vague increase language when exact numeric frequency is explicitly missing.

## Changed Rows

| Row | Gold | Previous projection | Revised projection | Orientation exact |
| ---: | --- | --- | --- | --- |
| 190 | `1 per 4 week` | `unknown, 1 per cluster` | `1 per 4 week` | `False -> True` |
| 338 | `multiple per month` | `unknown` | `multiple per month` | `False -> True` |
| 743 | `multiple per week` | `unknown` | `multiple per day` | `False -> False` |
| 744 | `multiple per week` | `unknown` | `multiple per week` | `False -> True` |
| 987 | `1 per 2 month` | `unknown` | `2 per 1 to 2 month` | `False -> False` |
| 1317 | `unknown, multiple per cluster` | `unknown` | `multiple per day` | `False -> False` |
| 1694 | `1 cluster per 2 week, 3 per cluster` | `unknown, 3 per cluster` | `1 cluster per 2 week, 3 per cluster` | `False -> True` |
| 1695 | `multiple per month` | `unknown` | `3 to 5 per month` | `False -> False` |
| 1707 | `multiple per week` | `unknown` | `multiple per week` | `False -> True` |
| 2080 | `multiple per month` | `unknown, 2 per cluster` | `1 cluster per month, 2 per cluster` | `False -> False` |
| 3528 | `unknown` | `multiple per day` | `unknown` | `False -> True` |
| 5534 | `1 per multiple month` | `1 per 14 day` | `1 per 2 week` | `False -> False` |
| 5921 | `1 per 6 to 8 week` | `unknown` | `1 cluster per 6 to 8 week, multiple per cluster` | `False -> False` |
| 6153 | `9 per month` | `unknown` | `9 per 4 week` | `False -> False` |
| 6368 | `unknown` | `unknown, 1 per cluster` | `3 per 6 week` | `False -> False` |
| 6889 | `multiple per week` | `unknown` | `3 per 6 month` | `False -> False` |
| 7168 | `unknown` | `unknown, 2 per cluster` | `1 cluster per year, 2 per cluster` | `False -> False` |
| 7615 | `3 to 7 per month` | `unknown, 3 to 6 per cluster` | `1 cluster per month, 3 to 6 per cluster` | `False -> False` |
| 9937 | `1 cluster per month, multiple per cluster` | `multiple per week` | `1 per 3 to 4 week` | `False -> False` |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `unknown` | `1 cluster per 4 to 5 week, multiple per cluster` | `False -> True` |
| 9955 | `1 cluster per month, multiple per cluster` | `multiple per month` | `1 cluster per month, multiple per cluster` | `False -> True` |
| 10386 | `1 cluster per week, 2 to 3 per cluster` | `2 to 3 per week` | `1 cluster per week, 2 to 3 per cluster` | `False -> True` |
| 10677 | `1 cluster per month, multiple per cluster` | `unknown` | `1 per month` | `False -> False` |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | `False -> True` |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `unknown, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `False -> True` |
| 15672 | `1 per day` | `unknown` | `multiple per day` | `False -> False` |
