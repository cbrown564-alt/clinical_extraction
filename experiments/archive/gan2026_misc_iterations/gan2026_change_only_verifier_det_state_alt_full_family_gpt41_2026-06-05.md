# Gan 2026 Change-Only Verifier Deterministic/State Full Family

Validation-development row-level full-family audit over deterministic/state exact frequency or cluster alternatives. The proposal ranker does not use gold labels; gold labels are used only for validation accounting. This artifact does not authorize locked-test row-level inspection or benchmark claims.

## Decision

Promote to a frozen aggregate-only holdout audit: validation full-family accounting has positive W->C movement and zero C->W regressions.

## Artifacts

- Row JSONL: `experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.json`
- Source matrix: `experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 149 |
| call ok rows | 149 |
| model call rows | 1 |
| raw output reused rows | 148 |
| parse ok rows | 149 |
| parse error rows | 0 |
| all evidence quotes exact rows | 141 |
| base correct rows | 138 |
| projected correct rows | 142 |
| base purist proxy | 0.9262 |
| projected purist proxy | 0.9530 |
| whole validation base correct rows | 697 |
| whole validation projected correct rows | 701 |
| whole validation base purist proxy | 0.9293 |
| whole validation projected purist proxy | 0.9347 |
| changed label precision | 1.0000 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 138 |
| `W_to_C` | 4 |
| `W_to_W` | 7 |

## Recommendations

| Recommendation | Rows |
| --- | ---: |
| `keep_current` | 119 |
| `switch_to_proposed` | 30 |

## Changed Validation Rows

| Row | Current | Proposed | Source | Kind | Transition | Quotes exact |
| ---: | --- | --- | --- | --- | --- | --- |
| 5921 | `1 per day` | `1 per 6 to 8 week` | `deterministic_candidates_all` | `frequency_rate` | `W_to_C` | True |
| 10386 | `1 per day` | `1 cluster per week, 2 to 3 per cluster` | `deterministic_candidates_all` | `cluster_frequency` | `W_to_C` | True |
| 13209 | `1 per 4 to 5 week` | `1 per 8 month` | `deterministic_candidates_all` | `frequency_rate` | `W_to_C` | True |
| 15986 | `1 per 5 to 7 day` | `11 per 3 month` | `deterministic_candidates_all` | `frequency_rate` | `W_to_C` | True |

## Promotion Boundary

Promotion requires zero C->W regressions on this validation family and a positive W->C count. Any follow-up locked-test use must be frozen and aggregate-only.
