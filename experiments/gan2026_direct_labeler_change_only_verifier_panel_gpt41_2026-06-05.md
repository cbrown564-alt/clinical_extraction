# Gan 2026 Direct Labeler Change-Only Verifier Panel

Validation-development verifier panel over exact-evidence direct-labeler alternatives from hard failures and current-correct controls. Gold labels are used only for validation accounting.

## Decision

promote_to_full_validation_candidate

## Artifacts

- Row JSONL: `experiments/gan2026_direct_labeler_change_only_verifier_panel_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_direct_labeler_change_only_verifier_panel_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 28 |
| call ok rows | 27 |
| parse ok rows | 28 |
| all evidence quotes exact rows | 27 |
| panel base correct rows | 2 |
| panel projected correct rows | 8 |
| panel projected purist proxy | 0.2857 |
| base full correct rows | 708 |
| projected full correct rows | 714 |
| projected full purist proxy | 0.9520 |
| changed label precision | 1.0000 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 2 |
| `W_to_C` | 6 |
| `W_to_W` | 20 |

## Recommendations

| Recommendation | Rows |
| --- | ---: |
| `human_review` | 1 |
| `keep_current` | 11 |
| `parse_error` | 1 |
| `switch_to_proposed` | 15 |

## Changed Rows

| Row | Current | Proposed | Transition | Recommendation |
| ---: | --- | --- | --- | --- |
| 3528 | `seizure free for multiple year` | `unknown` | `W_to_C` | `switch_to_proposed` |
| 6153 | `None` | `9 per 4 week` | `W_to_C` | `switch_to_proposed` |
| 6501 | `seizure free for multiple year` | `unknown` | `W_to_C` | `switch_to_proposed` |
| 10996 | `1 to 2 cluster per month, multiple per cluster` | `1 to 2 cluster per month, 4 per cluster` | `W_to_C` | `switch_to_proposed` |
| 15593 | `2 per 6 month` | `1 cluster per 5 day, 2 to 4 per cluster` | `W_to_C` | `switch_to_proposed` |
| 15672 | `2 per 6 week` | `1 per day` | `W_to_C` | `switch_to_proposed` |