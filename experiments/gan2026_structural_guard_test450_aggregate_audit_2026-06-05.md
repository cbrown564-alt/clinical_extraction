# Gan 2026 Structural-Guard Test450 Aggregate Audit

Final-holdout aggregate-only local audit of the validation-frozen comparator-absent structural guard ranker. No test row-level failures were inspected or written, and no scorer/gold/split policy was changed.

## Summary

Base Purist proxy: 0.7600 (342 / 450).
Projected Purist proxy: 0.7622 (343 / 450).
Selected rows: 9.

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 7 |
| `W_to_C` | 1 |
| `W_to_W` | 1 |

## Interpretation

This frozen aggregate audit satisfies the user target if and only if the projected Purist proxy is at least 0.9000. The policy was frozen from validation before this holdout run; no row-level holdout output is emitted.

## Artifacts

- Summary JSON: `experiments/gan2026_structural_guard_test450_aggregate_audit_2026-06-05.json`
