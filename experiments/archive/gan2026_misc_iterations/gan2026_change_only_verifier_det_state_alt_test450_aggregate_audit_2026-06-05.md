# Gan 2026 Change-Only Verifier Test450 Aggregate Audit

Frozen locked-test aggregate-only audit over deterministic/state exact frequency or cluster alternatives. This summary intentionally omits row ids, clinical text, raw model outputs, and row-level errors.

## Decision

Aggregate-only holdout result does not approach the requested Purist F1 >= 0.9 threshold.

## Artifacts

- Summary JSON: `experiments/gan2026_change_only_verifier_det_state_alt_test450_aggregate_audit_2026-06-05.json`
- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 450 |
| eligible rows | 92 |
| call ok rows | 92 |
| parse ok rows | 92 |
| parse error rows | 0 |
| all evidence quotes exact rows | 88 |
| base correct rows | 342 |
| projected correct rows | 350 |
| base purist proxy | 0.7600 |
| projected purist proxy | 0.7778 |
| changed label precision | 0.9000 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 75 |
| `C_to_W` | 1 |
| `W_to_C` | 9 |
| `W_to_W` | 7 |

## Recommendations

| Recommendation | Rows |
| --- | ---: |
| `human_review` | 1 |
| `keep_current` | 72 |
| `switch_to_proposed` | 19 |

## Inspection Boundary

No test row ids, clinical text, raw model outputs, or row-level failures are stored in this report.
