# Gan 2026 Combined Change-Only Switch Layer

Validation-development composition of already validation-clean change-only switch families over the staged reasoner scorer-facing label. This does not authorize benchmark-comparable claims.

## Decision

freeze_candidate_for_aggregate_audit

## Artifacts

- Summary JSON: `experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 750 |
| base correct rows | 697 |
| projected correct rows | 708 |
| base purist proxy | 0.9293 |
| projected purist proxy | 0.9440 |
| changed rows | 34 |
| changed label precision | 1.0000 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 697 |
| `W_to_C` | 11 |
| `W_to_W` | 42 |

## Selected Families

| Family | Rows |
| --- | ---: |
| `det_state_exact` | 9 |
| `keep_current` | 716 |
| `llm_selector_exact` | 25 |
