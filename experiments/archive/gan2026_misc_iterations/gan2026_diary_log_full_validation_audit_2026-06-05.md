# Gan 2026 Diary/Log Full-Validation Audit

Validation-development full-validation diary/log audit. The selected policy uses fixed diary rule ids from prior hard-panel ablation and reports rejected diary rules for negative evidence. It does not inspect locked-test row-level failures, change scorer policy, or make a benchmark-comparable claim.

## Summary

Base full-row Purist proxy: 0.9040 (678 / 750).
Projected full-row Purist proxy with selected diary rules: 0.9067 (680 / 750).

| Candidate set | Rows |
| --- | ---: |
| selected | 2 |
| rejected | 3 |

## Selected Transitions

| Transition | Rows |
| --- | ---: |
| `W_to_C` | 2 |

## Rule Counts

| Rule | Selected | Rejected |
| --- | ---: | ---: |
| `diary.increasing_monthly_count` | 0 | 2 |
| `diary.monthly_count_log` | 1 | 0 |
| `diary.seizure_day_log` | 0 | 1 |
| `diary.sleep_awake_month_summary` | 1 | 0 |

## Selected Rows

| Row | Base | Candidate | Gold | Transition | Rule |
| ---: | --- | --- | --- | --- | --- |
| 9496 | `2 per week` | `2 per 5 month` | `6 per 12 month` | `W_to_C` | `diary.monthly_count_log` |
| 15986 | `1 per 5 to 7 day` | `11 per 3 month` | `11 per 3 month` | `W_to_C` | `diary.sleep_awake_month_summary` |

## Interpretation

The selected diary/log rule set is clean on full validation. Freeze the rule ids and run an aggregate-only locked-test audit; keep rejected diary rules excluded (diary.increasing_monthly_count:2, diary.seizure_day_log:1).

## Artifacts

- Diary/log CSV: `experiments/gan2026_diary_log_full_validation_audit_2026-06-05.csv`
- Diary/log JSON: `experiments/gan2026_diary_log_full_validation_audit_2026-06-05.json`
