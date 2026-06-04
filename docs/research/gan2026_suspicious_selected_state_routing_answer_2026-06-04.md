# Gan 2026 Suspicious Selected-State Routing Answer

This is a no-call validation-development diagnostic over saved rich selected-state hard-panel replay artifacts.

## Answer

Deterministic suspicious-state routing is useful as a no-call safety and review layer, but it is not enough to replace a selective verifier for the remaining unresolved suspicious rows. The pass flagged 44/75 rows, routed 35 to `unknown` and 9 to review, with 1 W->C and 6 C->W changes among scorable rows.

## Verifier Decision

Predeclare a selective verifier only for the stable suspicious slices; deterministic routing caused C->W rows [190, 338, 1694, 9943, 10996, 15593], so the verifier must prove no-regression value before it can affect labels.

## Claim Boundary

Validation-development saved-artifact suspicious-state routing diagnostic only. No new live LLM calls, locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim.

## Artifacts

- Protocol: `docs/research/gan2026_ambiguity_ownership_protocol_2026-06-04.md`
- Routing JSONL: `experiments/gan2026_suspicious_selected_state_routing_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_suspicious_selected_state_routing_2026-06-04.json`
- Source replay: `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| suspicious state rows | 44 |
| non suspicious rows | 31 |
| route unknown rows | 35 |
| route review rows | 9 |
| render rows | 31 |
| comparator correct rows | 37 |
| final policy scorable rows | 66 |
| final policy correct rows | 29 |
| w to c against comparator rows | 1 |
| c to w against comparator rows | 6 |
| exact trace rate | 0.973 |
| suspicious no call resolution rows | 44 |

## Suspicious Flags

| Flag | Rows |
| --- | ---: |
| `denominator_window_mismatch` | 3 |
| `diary_log_date_list_without_defined_observation_window` | 4 |
| `frequency_with_count_blocking_ambiguity` | 30 |
| `frequency_with_exclusive_conditionality` | 5 |
| `seizure_free_non_all_type_scope_with_current_events` | 2 |
| `selected_evidence_missing_exact_trace` | 2 |
| `unresolved_cluster_cadence_with_per_cluster_burden` | 9 |
| `vague_trend_without_absolute_current_frequency` | 1 |

## Hidden-Family Readout

| Hidden family | Rows | Suspicious | Route unknown | Route review |
| --- | ---: | ---: | ---: | ---: |
| `benchmark_format_convention` | 24 | 14 | 10 | 4 |
| `candidate_absent_or_weak` | 4 | 3 | 3 | 0 |
| `cluster_burden` | 18 | 10 | 8 | 2 |
| `cluster_or_diary` | 12 | 8 | 4 | 4 |
| `competing_semiologies` | 37 | 23 | 19 | 4 |
| `current_vs_historical` | 39 | 21 | 18 | 3 |
| `deterministic_miss` | 4 | 3 | 3 | 0 |
| `diary_or_log_aggregation` | 8 | 4 | 1 | 3 |
| `rate_bucket_or_denominator` | 32 | 15 | 11 | 4 |
| `seizure_free_duration` | 27 | 18 | 15 | 3 |
| `seizure_free_overreach` | 11 | 8 | 5 | 3 |
| `shorthand_interval_range` | 1 | 0 | 0 | 0 |
| `temporal_conflict` | 10 | 6 | 3 | 3 |
| `uncertainty_or_ambiguity` | 26 | 15 | 13 | 2 |
| `unclassified` | 4 | 3 | 2 | 1 |
| `unknown_boundary` | 20 | 13 | 12 | 1 |
| `unknown_no_reference_boundary` | 14 | 9 | 5 | 4 |

## Routed Rows

| Row | Action | Flags | Comparator label | Final policy label | Gold | Delta |
| ---: | --- | --- | --- | --- | --- | --- |
| 190 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `1 per 4 week` | `unknown` | `1 per 4 week` | `C_to_W` |
| 338 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `multiple per month` | `unknown` | `multiple per month` | `C_to_W` |
| 743 | `route_review` | `denominator_window_mismatch` | `multiple per day` | `abstain` | `multiple per week` | `routed_to_review` |
| 744 | `route_review` | `denominator_window_mismatch` | `multiple per week` | `abstain` | `multiple per week` | `routed_to_review` |
| 869 | `route_review` | `diary_log_date_list_without_defined_observation_window`, `frequency_with_count_blocking_ambiguity` | `unknown` | `abstain` | `multiple per month` | `routed_to_review` |
| 959 | `route_unknown` | `frequency_with_count_blocking_ambiguity`, `unresolved_cluster_cadence_with_per_cluster_burden` | `unknown, 2 per cluster` | `unknown` | `1 per 2 month` | `W_to_W` |
| 1363 | `route_unknown` | `unresolved_cluster_cadence_with_per_cluster_burden` | `unknown, 3 per cluster` | `unknown` | `3 per day` | `W_to_W` |
| 1694 | `route_unknown` | `frequency_with_count_blocking_ambiguity`, `unresolved_cluster_cadence_with_per_cluster_burden` | `1 cluster per 2 week, 3 per cluster` | `unknown` | `1 cluster per 2 week, 3 per cluster` | `C_to_W` |
| 1695 | `route_review` | `selected_evidence_missing_exact_trace` | `3 to 5 per month` | `abstain` | `multiple per month` | `routed_to_review` |
| 2080 | `route_unknown` | `frequency_with_count_blocking_ambiguity`, `unresolved_cluster_cadence_with_per_cluster_burden` | `1 cluster per month, 2 per cluster` | `unknown` | `multiple per month` | `W_to_W` |
| 3356 | `route_unknown` | `frequency_with_exclusive_conditionality` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 3528 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 4368 | `route_review` | `diary_log_date_list_without_defined_observation_window` | `unknown` | `abstain` | `5 per 2 month` | `routed_to_review` |
| 5534 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `1 per 2 week` | `unknown` | `1 per multiple month` | `W_to_W` |
| 5921 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `1 cluster per 6 to 8 week, multiple per cluster` | `unknown` | `1 per 6 to 8 week` | `W_to_W` |
| 5974 | `route_unknown` | `frequency_with_exclusive_conditionality` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 6077 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 6094 | `route_review` | `frequency_with_count_blocking_ambiguity`, `selected_evidence_missing_exact_trace`, `unresolved_cluster_cadence_with_per_cluster_burden` | `unknown, 1 to 3 per cluster` | `abstain` | `3 per month` | `routed_to_review` |
| 6131 | `route_unknown` | `frequency_with_exclusive_conditionality` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 6153 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `9 per 4 week` | `unknown` | `9 per month` | `W_to_W` |
| 6209 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `2 to 3 per day` | `unknown` | `multiple per day` | `W_to_W` |
| 6321 | `route_unknown` | `frequency_with_exclusive_conditionality` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 6501 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 6571 | `route_unknown` | `frequency_with_exclusive_conditionality` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 6889 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `3 per 6 month` | `unknown` | `multiple per week` | `W_to_W` |
| 6987 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 7168 | `route_unknown` | `unresolved_cluster_cadence_with_per_cluster_burden` | `1 cluster per year, 2 per cluster` | `unknown` | `unknown` | `W_to_C` |
| 7615 | `route_unknown` | `frequency_with_count_blocking_ambiguity`, `unresolved_cluster_cadence_with_per_cluster_burden` | `1 cluster per month, 3 to 6 per cluster` | `unknown` | `3 to 7 per month` | `W_to_W` |
| 9888 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 9943 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `1 cluster per 4 to 5 week, multiple per cluster` | `unknown` | `1 cluster per 4 to 5 week, multiple per cluster` | `C_to_W` |
| 10618 | `route_review` | `denominator_window_mismatch`, `unresolved_cluster_cadence_with_per_cluster_burden` | `unknown, 4 to 6 per cluster` | `abstain` | `unknown, 4 to 6 per cluster` | `routed_to_review` |
| 10677 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `1 per month` | `unknown` | `1 cluster per month, multiple per cluster` | `W_to_W` |
| 10996 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `1 to 2 cluster per month, 4 per cluster` | `unknown` | `1 to 2 cluster per month, 4 per cluster` | `C_to_W` |
| 11259 | `route_review` | `diary_log_date_list_without_defined_observation_window`, `seizure_free_non_all_type_scope_with_current_events` | `unknown` | `abstain` | `unknown` | `routed_to_review` |
| 12438 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `2 to 3 per year` | `unknown` | `1 per day` | `W_to_W` |
| 12460 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `2 per year` | `unknown` | `1 per day` | `W_to_W` |
| 13209 | `route_review` | `diary_log_date_list_without_defined_observation_window`, `frequency_with_count_blocking_ambiguity` | `unknown` | `abstain` | `1 per 8 month` | `routed_to_review` |
| 13843 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `unknown` | `unknown` | `seizure free for multiple month` | `W_to_W` |
| 14076 | `route_unknown` | `frequency_with_count_blocking_ambiguity`, `vague_trend_without_absolute_current_frequency` | `unknown` | `unknown` | `unknown` | `C_to_C` |
| 14810 | `route_unknown` | `seizure_free_non_all_type_scope_with_current_events` | `unknown` | `unknown` | `1 per month` | `W_to_W` |
| 15168 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `unknown` | `unknown` | `multiple per 15 month` | `W_to_W` |
| 15193 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `0 per 9 to 10 month` | `unknown` | `multiple per 13 month` | `W_to_W` |
| 15593 | `route_unknown` | `frequency_with_count_blocking_ambiguity`, `unresolved_cluster_cadence_with_per_cluster_burden` | `1 cluster per 5 day, 2 to 4 per cluster` | `unknown` | `1 cluster per 5 day, 2 to 4 per cluster` | `C_to_W` |
| 15672 | `route_unknown` | `frequency_with_count_blocking_ambiguity` | `multiple per day` | `unknown` | `1 per day` | `W_to_W` |
