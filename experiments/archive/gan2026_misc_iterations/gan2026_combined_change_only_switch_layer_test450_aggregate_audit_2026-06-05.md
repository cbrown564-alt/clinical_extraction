# Gan 2026 Combined Change-Only Switch Layer

Frozen locked-test aggregate-only audit for the combined change-only switch layer. This summary intentionally omits row ids, clinical text, raw model outputs, and row-level failures.

## Decision

does_not_meet_goal

## Artifacts

- Summary JSON: `experiments/gan2026_combined_change_only_switch_layer_test450_aggregate_audit_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 450 |
| call ok rows | 446 |
| base correct rows | 342 |
| projected correct rows | 354 |
| base purist proxy | 0.7600 |
| projected purist proxy | 0.7867 |
| changed rows | 31 |
| changed label precision | 0.9286 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 341 |
| `C_to_W` | 1 |
| `W_to_C` | 13 |
| `W_to_W` | 95 |

## Selected Families

| Family | Rows |
| --- | ---: |
| `det_state_exact` | 10 |
| `keep_current` | 419 |
| `llm_selector_exact` | 21 |
