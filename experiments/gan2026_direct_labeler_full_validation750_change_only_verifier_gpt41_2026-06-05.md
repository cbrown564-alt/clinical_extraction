# Gan 2026 Direct Labeler Change-Only Verifier Panel

Validation-development verifier panel over exact-evidence direct-labeler alternatives from hard failures and current-correct controls. Gold labels are used only for validation accounting.

## Decision

reject_or_revise_verifier_gate

## Artifacts

- Row JSONL: `experiments/gan2026_direct_labeler_full_validation750_change_only_verifier_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_direct_labeler_full_validation750_change_only_verifier_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 225 |
| call ok rows | 222 |
| parse ok rows | 225 |
| all evidence quotes exact rows | 220 |
| panel base correct rows | 195 |
| panel projected correct rows | 181 |
| panel projected purist proxy | 0.8044 |
| base full correct rows | 708 |
| projected full correct rows | 694 |
| projected full purist proxy | 0.9253 |
| changed label precision | 0.3056 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 170 |
| `C_to_W` | 25 |
| `W_to_C` | 11 |
| `W_to_W` | 19 |

## Recommendations

| Recommendation | Rows |
| --- | ---: |
| `human_review` | 5 |
| `keep_current` | 106 |
| `parse_error` | 3 |
| `switch_to_proposed` | 111 |

## Changed Rows

| Row | Current | Proposed | Transition | Recommendation |
| ---: | --- | --- | --- | --- |
| 3356 | `seizure free for multiple year` | `unknown` | `W_to_C` | `switch_to_proposed` |
| 3528 | `seizure free for multiple year` | `unknown` | `W_to_C` | `switch_to_proposed` |
| 3534 | `unknown` | `seizure free for 7 month` | `C_to_W` | `switch_to_proposed` |
| 6065 | `5 per month` | `3 to 5 per month` | `C_to_W` | `switch_to_proposed` |
| 6131 | `seizure free for 6 month` | `unknown` | `W_to_C` | `switch_to_proposed` |
| 6153 | `1 per 1 to 2 week` | `9 per 4 week` | `W_to_C` | `switch_to_proposed` |
| 6244 | `unknown` | `2 per week` | `C_to_W` | `switch_to_proposed` |
| 9496 | `2 per week` | `4 per 7 month` | `W_to_C` | `switch_to_proposed` |
| 9955 | `1 per month` | `1 cluster per month, multiple per cluster` | `W_to_C` | `switch_to_proposed` |
| 10996 | `1 to 2 cluster per month, multiple per cluster` | `1 to 2 cluster per month, 4 per cluster` | `W_to_C` | `switch_to_proposed` |
| 11282 | `unknown` | `seizure free for 3 month` | `C_to_W` | `switch_to_proposed` |
| 11389 | `no seizure frequency reference` | `1 per 2 month` | `C_to_W` | `switch_to_proposed` |
| 12835 | `4 per month` | `4 per year` | `C_to_W` | `switch_to_proposed` |
| 13008 | `4 per month` | `4 per year` | `C_to_W` | `switch_to_proposed` |
| 14076 | `seizure free for multiple year` | `unknown` | `W_to_C` | `switch_to_proposed` |
| 14282 | `multiple per 6 week` | `seizure free for 1 month` | `C_to_W` | `switch_to_proposed` |
| 14284 | `2 to 3 per month` | `seizure free for 1 month` | `C_to_W` | `switch_to_proposed` |
| 14332 | `5 per 2 month` | `seizure free for 2 month` | `C_to_W` | `switch_to_proposed` |
| 14383 | `3 to 4 per 3 month` | `seizure free for 3 month` | `C_to_W` | `switch_to_proposed` |
| 14454 | `2 per 2 month` | `seizure free for 2 month` | `C_to_W` | `switch_to_proposed` |
| 14524 | `2 per 6 month` | `unknown` | `C_to_W` | `switch_to_proposed` |
| 14581 | `2 per 3 month` | `seizure free for multiple year` | `C_to_W` | `switch_to_proposed` |
| 14611 | `2 per 4 month` | `seizure free for multiple year` | `C_to_W` | `switch_to_proposed` |
| 14672 | `3 per 8 month` | `seizure free for multiple year` | `C_to_W` | `switch_to_proposed` |
| 14765 | `1 per month` | `seizure free for 1 month` | `C_to_W` | `switch_to_proposed` |
| 14806 | `1 per 2 month` | `seizure free for 1 month` | `C_to_W` | `switch_to_proposed` |
| 15168 | `seizure free for multiple year` | `unknown` | `W_to_C` | `switch_to_proposed` |
| 15306 | `2 to 3 per 15 month` | `2 to 3 per month` | `C_to_W` | `switch_to_proposed` |
| 15317 | `2 to 3 per 15 month` | `2 to 3 per month` | `C_to_W` | `switch_to_proposed` |
| 15593 | `2 per 6 month` | `1 cluster per 5 day, 2 to 4 per cluster` | `W_to_C` | `switch_to_proposed` |
| 15672 | `2 per 6 week` | `1 per day` | `W_to_C` | `switch_to_proposed` |
| 15964 | `11 per 3 month` | `11 per 2 month` | `C_to_W` | `switch_to_proposed` |
| 15997 | `10 per 3 month` | `10 per 2 month` | `C_to_W` | `switch_to_proposed` |
| 16021 | `9 per 3 month` | `9 per 2 month` | `C_to_W` | `switch_to_proposed` |
| 16041 | `9 per 3 month` | `9 per 2 month` | `C_to_W` | `switch_to_proposed` |
| 16719 | `7 per 6 month` | `1 per week` | `C_to_W` | `switch_to_proposed` |