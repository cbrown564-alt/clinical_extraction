# Gan 2026 Direct Labeler Targeted Switch Test450 Aggregate Audit

Frozen locked-test aggregate-only audit for the direct-labeler targeted switch over the combined switch-layer current label. This artifact omits test row ids, clinical text, raw model outputs, and row-level failures.

## Decision

does_not_meet_goal

## Artifacts

- Summary JSON: `experiments/gan2026_direct_labeler_targeted_switch_test450_aggregate_audit_2026-06-05.json`
- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 450 |
| raw base correct rows | 342 |
| combined current correct rows | 353 |
| final correct rows | 354 |
| raw base purist proxy | 0.7600 |
| combined current purist proxy | 0.7844 |
| final purist proxy | 0.7867 |
| combined changed rows | 34 |
| targeted selected rows | 4 |
| direct call ok rows | 450 |
| direct parse ok rows | 120 |
| direct exact evidence rows | 282 |
| targeted verifier call ok rows | 9 |
| targeted changed label precision | 1.0000 |

## Combined Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 340 |
| `C_to_W` | 2 |
| `W_to_C` | 13 |
| `W_to_W` | 95 |

## Targeted Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 353 |
| `W_to_C` | 1 |
| `W_to_W` | 96 |

## Combined Families

| Value | Rows |
| --- | ---: |
| `det_state_exact` | 10 |
| `keep_current` | 416 |
| `llm_selector_exact` | 24 |

## Targeted Families

| Value | Rows |
| --- | ---: |
| `direct_cluster_per_cluster_completion` | 2 |
| `direct_daily_upgrade_from_non_daily_current` | 1 |
| `direct_unknown_from_current_seizure_free` | 1 |
| `keep_current` | 446 |

## Targeted Verifier Actions

| Value | Rows |
| --- | ---: |
| `keep_current` | 5 |
| `not_run` | 441 |
| `switch_to_proposed` | 4 |

## Inspection Boundary

No test row ids, clinical text, raw model outputs, or row-level failures are stored in this report.
