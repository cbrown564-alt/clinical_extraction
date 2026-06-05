# Gan 2026 Change-Only Verifier Expanded Calibration

Validation-development expanded change-only verifier calibration panel. Gold labels were used only for panel construction and post-selection accounting, not in model input. No locked-test rows were inspected.

## Summary

Base proxy: 0.7500 (45 / 60).
Projected proxy: 0.9500 (57 / 60).
Decision: `promote_candidate`.
Reused raw-output rows: 24; new model-call rows: 35.

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 45 |
| `W_to_C` | 12 |
| `W_to_W` | 3 |

## Recommendations

| Recommendation | Rows |
| --- | ---: |
| `keep_current` | 40 |
| `parse_error` | 1 |
| `switch_to_proposed` | 19 |

## Artifacts

- Row JSONL: `experiments/gan2026_change_only_verifier_expanded_calibration_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_change_only_verifier_expanded_calibration_gpt41_2026-06-05.json`
