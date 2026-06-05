# Gan 2026 Structural-Guard Full-Validation Audit

Validation-development full-validation audit for the frozen comparator-absent structural guard ranker. Selection uses only non-gold candidate features and the existing validation component matrix as the base assembly surface; gold labels are used only for post-selection W->C/C->W accounting. This does not change scorer policy, split policy, or locked-test behavior.

## Summary

Base full-row Purist proxy: 0.9040 (678 / 750).
Projected full-row Purist proxy with structural guard: 0.9320 (699 / 750).

## Selected Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 4 |
| `W_to_C` | 21 |
| `W_to_W` | 9 |

## Rule Counts

| Rule | Rows |
| --- | ---: |
| `projection_policy.acd_003.vague_count_without_denominator` | 2 |
| `projection_policy.acd_004.conditional_only_trigger` | 1 |
| `projection_policy.acd_005.relative_only_trend` | 2 |
| `rate.direct_count_per_period` | 2 |
| `rate.occurring_adjective` | 1 |
| `rate.period_first_recent_count` | 3 |
| `rate.seizure_adjective` | 1 |
| `rate.there_have_been_count` | 1 |
| `state_graph.no_reference_fallback` | 11 |
| `unknown` | 10 |

## Selected Rows

| Row | Base | Candidate | Gold | Transition | Rule |
| ---: | --- | --- | --- | --- | --- |
| 3371 | `` | `1 per month` | `unknown` | `W_to_W` | `unknown` |
| 3468 | `` | `unknown` | `unknown` | `W_to_C` | `projection_policy.acd_004.conditional_only_trigger` |
| 3469 | `` | `unknown` | `unknown` | `W_to_C` | `unknown` |
| 3482 | `` | `1 per 12 week` | `unknown` | `W_to_W` | `unknown` |
| 3493 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 3512 | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | `projection_policy.acd_005.relative_only_trend` |
| 3532 | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | `projection_policy.acd_005.relative_only_trend` |
| 4731 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 5490 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 5977 | `` | `multiple per 6 week` | `unknown` | `W_to_C` | `rate.there_have_been_count` |
| 5996 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 6087 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 6094 | `` | `3 per week` | `3 per month` | `W_to_W` | `rate.direct_count_per_period` |
| 6153 | `` | `1 per 1 to 2 week` | `9 per month` | `W_to_W` | `unknown` |
| 6319 | `` | `1 per week` | `1 per week` | `W_to_C` | `rate.occurring_adjective` |
| 6321 | `` | `1 per day` | `unknown` | `W_to_W` | `rate.seizure_adjective` |
| 6368 | `` | `1 per 1 to 2 week` | `unknown` | `W_to_W` | `rate.direct_count_per_period` |
| 6607 | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | `projection_policy.acd_003.vague_count_without_denominator` |
| 7093 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 7168 | `` | `2 per year` | `unknown` | `W_to_W` | `rate.period_first_recent_count` |
| 9103 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 9877 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 9879 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 10753 | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | `projection_policy.acd_003.vague_count_without_denominator` |
| 11216 | `` | `unknown` | `unknown` | `W_to_C` | `unknown` |
| 11254 | `` | `unknown` | `unknown` | `W_to_C` | `unknown` |
| 11259 | `` | `unknown` | `unknown` | `W_to_C` | `unknown` |
| 11262 | `` | `unknown` | `unknown` | `W_to_C` | `unknown` |
| 11272 | `` | `unknown` | `unknown` | `W_to_C` | `unknown` |
| 11282 | `` | `unknown` | `unknown` | `W_to_C` | `unknown` |
| 11337 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 14040 | `` | `no seizure frequency reference` | `unknown` | `W_to_C` | `state_graph.no_reference_fallback` |
| 14810 | `` | `12 per month` | `1 per month` | `W_to_W` | `rate.period_first_recent_count` |
| 14821 | `` | `17 per month` | `1 per month` | `W_to_W` | `rate.period_first_recent_count` |

## Interpretation

The structural guard is clean on full validation. Freeze this exact candidate policy and run an aggregate-only locked-test audit without test row-level inspection.

## Artifacts

- Structural-guard CSV: `experiments/gan2026_structural_guard_full_validation_audit_2026-06-05.csv`
- Structural-guard JSON: `experiments/gan2026_structural_guard_full_validation_audit_2026-06-05.json`
