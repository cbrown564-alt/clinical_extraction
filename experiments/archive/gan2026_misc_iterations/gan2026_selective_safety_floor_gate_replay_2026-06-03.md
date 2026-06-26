# Gan 2026 Selective Safety-Floor Gate Replay (No-Call)

Validation-cycle fixed-slice replay over saved artifacts only. This is diagnostic accounting and does not imply production promotion.

- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Slice manifest: `experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json`
- Predeclaration/input manifest: `experiments/gan2026_selective_safety_floor_gate_predeclaration_2026-06-03.json`
- Split manifest: `gan2026_split_v1`
- Rows (slice memberships): 87
- JSONL artifact: `experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.jsonl`
- Summary JSON: `experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.json`

## Slice-level Summary

| Slice | Variant | Rows | Purist correct | Pragmatic correct | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions | Evidence-exact changed | Source-id valid changed | Fallback |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| candidate_generation_rescue | baseline_safety_floor_v2 | 44 | 0 | 4 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| candidate_generation_rescue | projection_boundary_state_priority_gate_v0 | 44 | 0 | 4 | 1 | 0 | 0 |  | 0 | 1 | 1 | 41 |
| candidate_generation_rescue | competing_frequency_uncertainty | 44 | 2 | 4 | 5 | 2 | 0 | 0.5000 | 0 | 5 | 5 | 0 |
| candidate_generation_rescue | lowest_current_frequency | 44 | 1 | 4 | 5 | 1 | 0 | 0.5000 | 0 | 5 | 5 | 0 |
| candidate_generation_rescue | llm_candidate_sidecar_rescue_gate_v0 | 44 | 6 | 10 | 8 | 6 | 0 | 1.0000 | 0 | 8 | 8 | 36 |
| candidate_generation_rescue | combined_selective_gate_v0 | 44 | 6 | 10 | 9 | 6 | 0 | 1.0000 | 0 | 9 | 9 | 35 |
| candidate_generation_unknown_seizure_free_boundary | baseline_safety_floor_v2 | 26 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| candidate_generation_unknown_seizure_free_boundary | projection_boundary_state_priority_gate_v0 | 26 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 0 | 26 |
| candidate_generation_unknown_seizure_free_boundary | competing_frequency_uncertainty | 26 | 1 | 1 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 | 0 |
| candidate_generation_unknown_seizure_free_boundary | lowest_current_frequency | 26 | 0 | 0 | 1 | 0 | 0 |  | 0 | 1 | 1 | 0 |
| candidate_generation_unknown_seizure_free_boundary | llm_candidate_sidecar_rescue_gate_v0 | 26 | 6 | 6 | 8 | 6 | 0 | 1.0000 | 0 | 8 | 8 | 18 |
| candidate_generation_unknown_seizure_free_boundary | combined_selective_gate_v0 | 26 | 6 | 6 | 8 | 6 | 0 | 1.0000 | 0 | 8 | 8 | 18 |
| projection_arbitration | baseline_safety_floor_v2 | 11 | 0 | 3 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| projection_arbitration | projection_boundary_state_priority_gate_v0 | 11 | 5 | 8 | 5 | 5 | 0 | 1.0000 | 0 | 5 | 5 | 6 |
| projection_arbitration | competing_frequency_uncertainty | 11 | 2 | 2 | 6 | 2 | 0 | 0.4000 | 0 | 6 | 6 | 2 |
| projection_arbitration | lowest_current_frequency | 11 | 4 | 4 | 5 | 4 | 0 | 1.0000 | 0 | 5 | 5 | 2 |
| projection_arbitration | llm_candidate_sidecar_rescue_gate_v0 | 11 | 1 | 4 | 2 | 1 | 0 | 1.0000 | 0 | 2 | 2 | 9 |
| projection_arbitration | combined_selective_gate_v0 | 11 | 5 | 8 | 5 | 5 | 0 | 1.0000 | 0 | 5 | 5 | 6 |
| projection_unknown_seizure_free_arbitration | baseline_safety_floor_v2 | 6 | 0 | 2 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| projection_unknown_seizure_free_arbitration | projection_boundary_state_priority_gate_v0 | 6 | 4 | 6 | 4 | 4 | 0 | 1.0000 | 0 | 4 | 4 | 2 |
| projection_unknown_seizure_free_arbitration | competing_frequency_uncertainty | 6 | 1 | 1 | 3 | 1 | 0 | 0.3333 | 0 | 3 | 3 | 0 |
| projection_unknown_seizure_free_arbitration | lowest_current_frequency | 6 | 2 | 2 | 2 | 2 | 0 | 1.0000 | 0 | 2 | 2 | 0 |
| projection_unknown_seizure_free_arbitration | llm_candidate_sidecar_rescue_gate_v0 | 6 | 1 | 3 | 2 | 1 | 0 | 1.0000 | 0 | 2 | 2 | 4 |
| projection_unknown_seizure_free_arbitration | combined_selective_gate_v0 | 6 | 4 | 6 | 4 | 4 | 0 | 1.0000 | 0 | 4 | 4 | 2 |

## Hidden-Family Summary

| Slice | Family | Variant | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| candidate_generation_rescue | benchmark_format_convention | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | benchmark_format_convention | combined_selective_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | benchmark_format_convention | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | benchmark_format_convention | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | benchmark_format_convention | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | benchmark_format_convention | projection_boundary_state_priority_gate_v0 | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | cluster_burden | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | cluster_burden | combined_selective_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | cluster_burden | competing_frequency_uncertainty | 1 | 0 | 0 | 0.0000 | 0 |
| candidate_generation_rescue | cluster_burden | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | cluster_burden | lowest_current_frequency | 1 | 0 | 0 | 0.0000 | 0 |
| candidate_generation_rescue | cluster_burden | projection_boundary_state_priority_gate_v0 | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | competing_semiologies | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | competing_semiologies | combined_selective_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | competing_semiologies | competing_frequency_uncertainty | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | competing_semiologies | llm_candidate_sidecar_rescue_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | competing_semiologies | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | competing_semiologies | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | current_vs_historical | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | current_vs_historical | combined_selective_gate_v0 | 4 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | current_vs_historical | competing_frequency_uncertainty | 1 | 0 | 0 | 0.0000 | 0 |
| candidate_generation_rescue | current_vs_historical | llm_candidate_sidecar_rescue_gate_v0 | 4 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | current_vs_historical | lowest_current_frequency | 1 | 0 | 0 | 0.0000 | 0 |
| candidate_generation_rescue | current_vs_historical | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | diary_or_log_aggregation | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | diary_or_log_aggregation | combined_selective_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | diary_or_log_aggregation | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | diary_or_log_aggregation | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | diary_or_log_aggregation | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | diary_or_log_aggregation | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | rate_bucket_or_denominator | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | rate_bucket_or_denominator | combined_selective_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | rate_bucket_or_denominator | competing_frequency_uncertainty | 3 | 1 | 0 | 0.5000 | 0 |
| candidate_generation_rescue | rate_bucket_or_denominator | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | rate_bucket_or_denominator | lowest_current_frequency | 3 | 1 | 0 | 0.5000 | 0 |
| candidate_generation_rescue | rate_bucket_or_denominator | projection_boundary_state_priority_gate_v0 | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | seizure_free_duration | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | seizure_free_duration | combined_selective_gate_v0 | 6 | 4 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | seizure_free_duration | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | seizure_free_duration | llm_candidate_sidecar_rescue_gate_v0 | 6 | 4 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | seizure_free_duration | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | seizure_free_duration | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | uncertainty_or_ambiguity | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | uncertainty_or_ambiguity | combined_selective_gate_v0 | 7 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | uncertainty_or_ambiguity | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | uncertainty_or_ambiguity | llm_candidate_sidecar_rescue_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | uncertainty_or_ambiguity | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | uncertainty_or_ambiguity | projection_boundary_state_priority_gate_v0 | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unclassified | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unclassified | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unclassified | competing_frequency_uncertainty | 1 | 0 | 0 | 0.0000 | 0 |
| candidate_generation_rescue | unclassified | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unclassified | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unclassified | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unknown_boundary | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unknown_boundary | combined_selective_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | unknown_boundary | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | unknown_boundary | llm_candidate_sidecar_rescue_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_rescue | unknown_boundary | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| candidate_generation_rescue | unknown_boundary | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | benchmark_format_convention | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | benchmark_format_convention | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | benchmark_format_convention | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | benchmark_format_convention | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | benchmark_format_convention | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | benchmark_format_convention | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | cluster_burden | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | cluster_burden | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | cluster_burden | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | cluster_burden | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | cluster_burden | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | cluster_burden | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | competing_semiologies | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | competing_semiologies | combined_selective_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | competing_semiologies | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | competing_semiologies | llm_candidate_sidecar_rescue_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | competing_semiologies | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | competing_semiologies | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | current_vs_historical | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | current_vs_historical | combined_selective_gate_v0 | 4 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | current_vs_historical | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | current_vs_historical | llm_candidate_sidecar_rescue_gate_v0 | 4 | 2 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | current_vs_historical | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | current_vs_historical | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | diary_or_log_aggregation | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | diary_or_log_aggregation | combined_selective_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | diary_or_log_aggregation | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | diary_or_log_aggregation | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | diary_or_log_aggregation | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | diary_or_log_aggregation | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | rate_bucket_or_denominator | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | rate_bucket_or_denominator | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | rate_bucket_or_denominator | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | rate_bucket_or_denominator | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | rate_bucket_or_denominator | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | rate_bucket_or_denominator | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | seizure_free_duration | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | seizure_free_duration | combined_selective_gate_v0 | 6 | 4 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | seizure_free_duration | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | seizure_free_duration | llm_candidate_sidecar_rescue_gate_v0 | 6 | 4 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | seizure_free_duration | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | seizure_free_duration | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | uncertainty_or_ambiguity | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | uncertainty_or_ambiguity | combined_selective_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | uncertainty_or_ambiguity | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | uncertainty_or_ambiguity | llm_candidate_sidecar_rescue_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | uncertainty_or_ambiguity | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | uncertainty_or_ambiguity | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | unknown_boundary | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | unknown_boundary | combined_selective_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | unknown_boundary | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | unknown_boundary | llm_candidate_sidecar_rescue_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | unknown_boundary | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| candidate_generation_unknown_seizure_free_boundary | unknown_boundary | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | benchmark_format_convention | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | benchmark_format_convention | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | benchmark_format_convention | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | benchmark_format_convention | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | benchmark_format_convention | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| projection_arbitration | benchmark_format_convention | projection_boundary_state_priority_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | cluster_burden | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | cluster_burden | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | cluster_burden | competing_frequency_uncertainty | 1 | 0 | 0 | 0.0000 | 0 |
| projection_arbitration | cluster_burden | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | cluster_burden | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | cluster_burden | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | competing_semiologies | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | competing_semiologies | combined_selective_gate_v0 | 3 | 3 | 0 | 1.0000 | 0 |
| projection_arbitration | competing_semiologies | competing_frequency_uncertainty | 2 | 1 | 0 | 0.5000 | 0 |
| projection_arbitration | competing_semiologies | llm_candidate_sidecar_rescue_gate_v0 | 1 | 0 | 0 |  | 0 |
| projection_arbitration | competing_semiologies | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | competing_semiologies | projection_boundary_state_priority_gate_v0 | 3 | 3 | 0 | 1.0000 | 0 |
| projection_arbitration | current_vs_historical | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | current_vs_historical | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_arbitration | current_vs_historical | competing_frequency_uncertainty | 2 | 1 | 0 | 0.5000 | 0 |
| projection_arbitration | current_vs_historical | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | current_vs_historical | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | current_vs_historical | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_arbitration | diary_or_log_aggregation | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | diary_or_log_aggregation | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | diary_or_log_aggregation | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| projection_arbitration | diary_or_log_aggregation | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | diary_or_log_aggregation | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| projection_arbitration | diary_or_log_aggregation | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | rate_bucket_or_denominator | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | rate_bucket_or_denominator | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | rate_bucket_or_denominator | competing_frequency_uncertainty | 3 | 1 | 0 | 0.5000 | 0 |
| projection_arbitration | rate_bucket_or_denominator | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | rate_bucket_or_denominator | lowest_current_frequency | 3 | 2 | 0 | 1.0000 | 0 |
| projection_arbitration | rate_bucket_or_denominator | projection_boundary_state_priority_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | seizure_free_duration | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | seizure_free_duration | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_arbitration | seizure_free_duration | competing_frequency_uncertainty | 2 | 1 | 0 | 0.5000 | 0 |
| projection_arbitration | seizure_free_duration | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | seizure_free_duration | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | seizure_free_duration | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_arbitration | uncertainty_or_ambiguity | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | uncertainty_or_ambiguity | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_arbitration | uncertainty_or_ambiguity | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | uncertainty_or_ambiguity | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | uncertainty_or_ambiguity | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| projection_arbitration | uncertainty_or_ambiguity | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_arbitration | unclassified | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | unclassified | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | unclassified | competing_frequency_uncertainty | 1 | 0 | 0 | 0.0000 | 0 |
| projection_arbitration | unclassified | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | unclassified | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | unclassified | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | unknown_boundary | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_arbitration | unknown_boundary | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_arbitration | unknown_boundary | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | unknown_boundary | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_arbitration | unknown_boundary | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| projection_arbitration | unknown_boundary | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | cluster_burden | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | cluster_burden | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | cluster_burden | competing_frequency_uncertainty | 1 | 0 | 0 | 0.0000 | 0 |
| projection_unknown_seizure_free_arbitration | cluster_burden | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | cluster_burden | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | cluster_burden | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | competing_semiologies | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | competing_semiologies | combined_selective_gate_v0 | 3 | 3 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | competing_semiologies | competing_frequency_uncertainty | 2 | 1 | 0 | 0.5000 | 0 |
| projection_unknown_seizure_free_arbitration | competing_semiologies | llm_candidate_sidecar_rescue_gate_v0 | 1 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | competing_semiologies | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | competing_semiologies | projection_boundary_state_priority_gate_v0 | 3 | 3 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | current_vs_historical | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | current_vs_historical | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | current_vs_historical | competing_frequency_uncertainty | 2 | 1 | 0 | 0.5000 | 0 |
| projection_unknown_seizure_free_arbitration | current_vs_historical | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | current_vs_historical | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | current_vs_historical | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | rate_bucket_or_denominator | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | rate_bucket_or_denominator | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | rate_bucket_or_denominator | competing_frequency_uncertainty | 1 | 0 | 0 | 0.0000 | 0 |
| projection_unknown_seizure_free_arbitration | rate_bucket_or_denominator | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | rate_bucket_or_denominator | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | rate_bucket_or_denominator | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | seizure_free_duration | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | seizure_free_duration | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | seizure_free_duration | competing_frequency_uncertainty | 2 | 1 | 0 | 0.5000 | 0 |
| projection_unknown_seizure_free_arbitration | seizure_free_duration | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | seizure_free_duration | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | seizure_free_duration | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | uncertainty_or_ambiguity | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | uncertainty_or_ambiguity | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | uncertainty_or_ambiguity | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | uncertainty_or_ambiguity | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | uncertainty_or_ambiguity | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | uncertainty_or_ambiguity | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | unknown_boundary | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | unknown_boundary | combined_selective_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | unknown_boundary | competing_frequency_uncertainty | 1 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | unknown_boundary | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | unknown_boundary | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| projection_unknown_seizure_free_arbitration | unknown_boundary | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |

## Would-Change Rows

### Projection Boundary-State Priority
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 6889 | projection_arbitration | multiple per week | 1 per 2 to 3 week | multiple per week | rate_bucket_or_denominator;benchmark_format_convention | Projected with selective unknown/unresolved boundary-state priority. |
| 9943 | candidate_generation_rescue | 1 cluster per 4 to 5 week, multiple per cluster | 1 per 4 to 5 week | 1 per multiple week | cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention | Projected with selective unknown/unresolved boundary-state priority. |
| 11216 | projection_arbitration | unknown | seizure free for 4 month | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11216 | projection_unknown_seizure_free_arbitration | unknown | seizure free for 4 month | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11254 | projection_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11254 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11259 | projection_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11259 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11272 | projection_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11272 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |

### LLM Candidate Sidecar Rescue
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 3356 | candidate_generation_rescue | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 3356 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6244 | candidate_generation_rescue | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6244 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6321 | candidate_generation_rescue | unknown | 1 per day | unknown | unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6321 | candidate_generation_unknown_seizure_free_boundary | unknown | 1 per day | unknown | unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 10266 | candidate_generation_rescue | unknown | 1 per 5 day | unknown | unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 10266 | candidate_generation_unknown_seizure_free_boundary | unknown | 1 per 5 day | unknown | unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 11254 | projection_arbitration | unknown | seizure free for multiple year | seizure free | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 11254 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | seizure free | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 11259 | projection_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 11259 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 13858 | candidate_generation_rescue | seizure free for multiple month | no seizure frequency reference | unknown | seizure_free_duration;diary_or_log_aggregation;current_vs_historical | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 13858 | candidate_generation_unknown_seizure_free_boundary | seizure free for multiple month | no seizure frequency reference | unknown | seizure_free_duration;diary_or_log_aggregation;current_vs_historical | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14025 | candidate_generation_rescue | unknown | seizure free for multiple year | 2 per 6 weeks | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14025 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | 2 per 6 weeks | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14076 | candidate_generation_rescue | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14076 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 15193 | candidate_generation_rescue | multiple per 13 month | seizure free for multiple year | unknown | seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 15193 | candidate_generation_unknown_seizure_free_boundary | multiple per 13 month | seizure free for multiple year | unknown | seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention | LLM sidecar rescue gate fired after strict evidence/source/id checks. |

### Combined Selective Gate
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 3356 | candidate_generation_rescue | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 3356 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6244 | candidate_generation_rescue | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6244 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6321 | candidate_generation_rescue | unknown | 1 per day | unknown | unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6321 | candidate_generation_unknown_seizure_free_boundary | unknown | 1 per day | unknown | unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6889 | projection_arbitration | multiple per week | 1 per 2 to 3 week | multiple per week | rate_bucket_or_denominator;benchmark_format_convention | Projected with selective unknown/unresolved boundary-state priority. |
| 9943 | candidate_generation_rescue | 1 cluster per 4 to 5 week, multiple per cluster | 1 per 4 to 5 week | 1 per multiple week | cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention | Projected with selective unknown/unresolved boundary-state priority. |
| 10266 | candidate_generation_rescue | unknown | 1 per 5 day | unknown | unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 10266 | candidate_generation_unknown_seizure_free_boundary | unknown | 1 per 5 day | unknown | unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 11216 | projection_arbitration | unknown | seizure free for 4 month | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11216 | projection_unknown_seizure_free_arbitration | unknown | seizure free for 4 month | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11254 | projection_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11254 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11259 | projection_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11259 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11272 | projection_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 11272 | projection_unknown_seizure_free_arbitration | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 13858 | candidate_generation_rescue | seizure free for multiple month | no seizure frequency reference | unknown | seizure_free_duration;diary_or_log_aggregation;current_vs_historical | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 13858 | candidate_generation_unknown_seizure_free_boundary | seizure free for multiple month | no seizure frequency reference | unknown | seizure_free_duration;diary_or_log_aggregation;current_vs_historical | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14025 | candidate_generation_rescue | unknown | seizure free for multiple year | 2 per 6 weeks | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14025 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | 2 per 6 weeks | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14076 | candidate_generation_rescue | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14076 | candidate_generation_unknown_seizure_free_boundary | unknown | seizure free for multiple year | unknown | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 15193 | candidate_generation_rescue | multiple per 13 month | seizure free for multiple year | unknown | seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 15193 | candidate_generation_unknown_seizure_free_boundary | multiple per 13 month | seizure free for multiple year | unknown | seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
