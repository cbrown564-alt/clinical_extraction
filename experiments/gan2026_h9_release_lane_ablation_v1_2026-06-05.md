# Gan 2026 H9 Release Lane Ablation v1

Validation-development release-lane ablation. Each lane replays an already saved deterministic fallback release independently; no semantic repair, boundary/renderer, prompt, model, parser, scorer, or locked-test policy changes are made.

## Decision

h9_release_lane_ablation_v1_passed_guardrail

## Lanes

| Lane | Released | W->C | C->W | Precision | H6 controls | H6 regressions | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `abstain` | 17 | 17 | 0 | 1.0000 | 0 | 0 | `passed_no_c_to_w_no_h6_regression` |
| `human_review` | 2 | 2 | 0 | 1.0000 | 0 | 0 | `passed_no_c_to_w_no_h6_regression` |

## Surface

validation_hard_control_rows_from_current_assembled_control
