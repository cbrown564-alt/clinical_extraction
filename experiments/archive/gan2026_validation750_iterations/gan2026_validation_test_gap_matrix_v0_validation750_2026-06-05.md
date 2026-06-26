# Gan 2026 Validation-Test Gap Matrix v0

Split manifest: `gan2026_split_v1`

This artifact is validation row-level only. Locked-test row-level artifacts are skipped by construction; locked-test evidence remains aggregate-only unless a future frozen slice protocol authorizes more.

## Summary

- Matrix rows: 1534
- Unique validation source rows: 750
- Source artifacts used: 1
- Locked-test row-level artifacts used: 0

## Score Layers

| Score layer | Rows |
| --- | ---: |
| deterministic_comparator | 750 |
| final_policy | 750 |
| abstain_review_monitor | 34 |

## Component Owners

| Component owner | Rows |
| --- | ---: |
| deterministic_rule | 750 |
| deterministic_adapter | 701 |
| safety_floor | 83 |

## Final-Policy Transitions

| Transition | Rows |
| --- | ---: |
| C_to_C | 678 |
| W_to_W | 38 |
| C_to_abstain | 17 |
| W_to_abstain | 9 |
| W_to_review | 6 |
| C_to_review | 2 |

## Hidden Families

| Hidden family | Layer rows |
| --- | ---: |
| seizure_free_duration | 64 |
| competing_semiologies | 59 |
| uncertainty_or_ambiguity | 59 |
| current_vs_historical | 58 |
| unknown_boundary | 51 |
| rate_bucket_or_denominator | 42 |
| cluster_burden | 22 |
| benchmark_format_convention | 20 |
| diary_or_log_aggregation | 8 |
| unclassified | 5 |

## Skipped Artifacts

| Artifact | Reason |
| --- | --- |
| rules_only_v1_baseline | not_validation_row_level_allowed |
| staged_assembly_validation750_no_call | unsupported_row_source_role |
| hidden_family_first_failure_atlas | unsupported_row_source_role |
| rq7_family_component_matrix | not_validation_row_level_allowed |
| selective_safety_floor_validation750 | unsupported_row_source_role |
| selective_safety_floor_test450_frozen_readout | locked_test_row_level_blocked |
| staged_assembly_test450_nonprediction_selector | locked_test_row_level_blocked |
| direct_labeler_targeted_switch_validation750 | unsupported_row_source_role |
| direct_labeler_targeted_switch_test450 | locked_test_row_level_blocked |
| structured_candidate_direct_labeler_validation750 | unsupported_row_source_role |
| fewshot_train_exemplar_validation750 | unsupported_row_source_role |
| fewshot_train_exemplar_test450 | locked_test_row_level_blocked |
| structural_guard_validation750 | unsupported_row_source_role |
| structural_guard_test450 | locked_test_row_level_blocked |
| llm_structured_validation750_repair_ladders | not_validation_row_level_allowed |
