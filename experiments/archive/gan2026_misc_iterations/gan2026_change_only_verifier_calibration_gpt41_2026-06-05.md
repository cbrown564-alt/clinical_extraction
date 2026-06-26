# Gan 2026 Change-Only Verifier Calibration

Validation-development change-only verifier calibration panel. Gold labels were used only for panel construction and post-selection accounting, not in model input. No locked-test rows were inspected.

## Summary

Base proxy: 0.5000 (12 / 24).
Projected proxy: 0.8333 (20 / 24).
Decision: `diagnostic_positive_but_not_promotable`.

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 10 |
| `C_to_W` | 2 |
| `W_to_C` | 10 |
| `W_to_W` | 2 |

## Recommendations

| Recommendation | Rows |
| --- | ---: |
| `keep_current` | 11 |
| `switch_to_proposed` | 13 |

## Changed Rows

| Row | Role | Current | Proposed | Decision | Transition |
| ---: | --- | --- | --- | --- | --- |
| 4690 | `positive_recoverable_miss` | `seizure free for multiple year` | `unknown` | `switch_to_proposed` | `W_to_C` |
| 5921 | `positive_recoverable_miss` | `1 per day` | `1 per 6 to 8 week` | `switch_to_proposed` | `W_to_C` |
| 6244 | `positive_recoverable_miss` | `seizure free for multiple year` | `unknown` | `switch_to_proposed` | `W_to_C` |
| 6889 | `positive_recoverable_miss` | `1 per 2 to 3 week` | `multiple per week` | `switch_to_proposed` | `W_to_C` |
| 6987 | `positive_recoverable_miss` | `seizure free for multiple year` | `unknown` | `switch_to_proposed` | `W_to_C` |
| 9496 | `positive_recoverable_miss` | `2 per week` | `2 per 5 month` | `switch_to_proposed` | `W_to_C` |
| 10266 | `positive_recoverable_miss` | `1 per 5 day` | `unknown` | `switch_to_proposed` | `W_to_C` |
| 10386 | `positive_recoverable_miss` | `1 per day` | `1 cluster per week, 2 to 3 per cluster` | `switch_to_proposed` | `W_to_C` |
| 10618 | `positive_recoverable_miss` | `seizure free for multiple year` | `unknown` | `switch_to_proposed` | `W_to_C` |
| 13209 | `positive_recoverable_miss` | `1 per 4 to 5 week` | `1 per 8 month` | `switch_to_proposed` | `W_to_C` |
| 14076 | `positive_recoverable_miss` | `seizure free for multiple year` | `unknown` | `switch_to_proposed` | `W_to_W` |
| 156 | `negative_correct_control` | `1 per 6 day` | `every 6 days` | `switch_to_proposed` | `C_to_W` |
| 182 | `negative_correct_control` | `1 per 2 day` | `every 2 days` | `switch_to_proposed` | `C_to_W` |

## Artifacts

- Row JSONL: `experiments/gan2026_change_only_verifier_calibration_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_change_only_verifier_calibration_gpt41_2026-06-05.json`
