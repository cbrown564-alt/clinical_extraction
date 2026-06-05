# Gan 2026 Direct Labeler Targeted Switch Validation750

Validation-development targeted policy over direct-labeler alternatives and change-only verifier decisions. Gold labels are used only for validation accounting; no locked-test row-level inspection is involved.

## Decision

freeze_candidate_for_aggregate_audit

## Metrics

| Metric | Value |
| --- | ---: |
| selected rows | 20 |
| base correct rows | 708 |
| projected correct rows | 717 |
| base purist proxy | 0.9440 |
| projected purist proxy | 0.9560 |
| changed label precision | 1.0000 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 4 |
| `W_to_C` | 9 |
| `W_to_W` | 7 |

## Families

| Family | Rows |
| --- | ---: |
| `direct_cluster_per_cluster_completion` | 7 |
| `direct_daily_upgrade_from_non_daily_current` | 7 |
| `direct_unknown_from_current_seizure_free` | 6 |

## Changed Rows

| Row | Family | Current | Proposed | Gold | Transition |
| ---: | --- | --- | --- | --- | --- |
| 3356 | `direct_unknown_from_current_seizure_free` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` |
| 3528 | `direct_unknown_from_current_seizure_free` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` |
| 3532 | `direct_daily_upgrade_from_non_daily_current` | `no seizure frequency reference` | `1 per day` | `unknown` | `C_to_C` |
| 6131 | `direct_unknown_from_current_seizure_free` | `seizure free for 6 month` | `unknown` | `unknown` | `W_to_C` |
| 6501 | `direct_unknown_from_current_seizure_free` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_W` |
| 9955 | `direct_cluster_per_cluster_completion` | `1 per month` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `W_to_C` |
| 10677 | `direct_cluster_per_cluster_completion` | `1 per month` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `W_to_W` |
| 10933 | `direct_cluster_per_cluster_completion` | `2 to 3 cluster per month, multiple per cluster` | `2 to 3 cluster per month, 5 per cluster` | `2 to 3 cluster per month, 5 per cluster` | `C_to_C` |
| 10942 | `direct_cluster_per_cluster_completion` | `5 per month` | `2 cluster per month, 5 per cluster` | `2 cluster per month, 5 per cluster` | `C_to_C` |
| 10996 | `direct_cluster_per_cluster_completion` | `1 to 2 cluster per month, multiple per cluster` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `W_to_C` |
| 11002 | `direct_cluster_per_cluster_completion` | `2 to 4 cluster per month, multiple per cluster` | `2 to 4 cluster per month, 5 per cluster` | `2 to 4 cluster per month, 5 per cluster` | `C_to_C` |
| 12422 | `direct_daily_upgrade_from_non_daily_current` | `4 per year` | `1 per day` | `1 per day` | `W_to_W` |
| 12438 | `direct_daily_upgrade_from_non_daily_current` | `2 to 3 per year` | `1 per day` | `1 per day` | `W_to_W` |
| 12456 | `direct_daily_upgrade_from_non_daily_current` | `3 per year` | `1 per day` | `1 per day` | `W_to_W` |
| 12460 | `direct_daily_upgrade_from_non_daily_current` | `2 per year` | `1 per day` | `1 per day` | `W_to_W` |
| 12468 | `direct_daily_upgrade_from_non_daily_current` | `4 per year` | `1 per day` | `1 per day` | `W_to_W` |
| 14076 | `direct_unknown_from_current_seizure_free` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` |
| 15168 | `direct_unknown_from_current_seizure_free` | `seizure free for multiple year` | `unknown` | `multiple per 15 month` | `W_to_C` |
| 15593 | `direct_cluster_per_cluster_completion` | `2 per 6 month` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `W_to_C` |
| 15672 | `direct_daily_upgrade_from_non_daily_current` | `2 per 6 week` | `1 per day` | `1 per day` | `W_to_C` |
