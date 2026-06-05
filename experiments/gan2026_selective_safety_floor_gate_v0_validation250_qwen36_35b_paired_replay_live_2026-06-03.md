# Gan 2026 Selective Safety-Floor Gate v0 Validation Replay (No-Call)

Validation-cycle full-validation replay over saved artifacts only. This is a validation development result and does not imply production promotion or holdout performance.

- Source artifact: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation250_qwen36_35b_paired_gate_v0_live_2026-06-03.jsonl`
- Slice manifest: `experiments\gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json`
- Predeclaration/input manifest: `experiments\gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json`
- Split manifest: `gan2026_split_v1`
- Rows: 250
- JSONL artifact: `experiments\gan2026_selective_safety_floor_gate_v0_validation250_qwen36_35b_paired_replay_live_2026-06-03.jsonl`
- Summary JSON: `experiments\gan2026_selective_safety_floor_gate_v0_validation250_qwen36_35b_paired_replay_live_2026-06-03.json`

## Slice-level Summary

| Slice | Variant | Rows | Purist correct | Pragmatic correct | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions | Evidence-exact changed | Source-id valid changed | Fallback |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| validation250 | baseline_safety_floor_v2 | 250 | 243 | 243 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| validation250 | projection_boundary_state_priority_gate_v0 | 250 | 237 | 239 | 5 | 2 | 0 | 1.0000 | 0 | 3 | 3 | 13 |
| validation250 | competing_frequency_uncertainty | 250 | 185 | 185 | 51 | 0 | 48 | 0.0000 | 50 | 49 | 49 | 0 |
| validation250 | lowest_current_frequency | 250 | 208 | 222 | 42 | 1 | 25 | 0.0385 | 26 | 40 | 40 | 0 |
| validation250 | llm_candidate_sidecar_rescue_gate_v0 | 250 | 244 | 244 | 1 | 1 | 0 | 1.0000 | 0 | 1 | 1 | 249 |
| validation250 | combined_selective_gate_v0 | 250 | 246 | 246 | 6 | 3 | 0 | 1.0000 | 0 | 4 | 4 | 244 |
| validation250 | selective_safety_floor_gate_v0 | 250 | 246 | 246 | 6 | 3 | 0 | 1.0000 | 0 | 4 | 4 | 244 |

## Frozen Fixed-Slice Summary

Prior fixed-slice accounting from the frozen manifest source. `combined_selective_gate_v0` is the candidate seed for `selective_safety_floor_gate_v0`.

| Slice | Candidate seed Purist | Candidate seed Pragmatic | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| candidate_generation_rescue | 6 | 10 | 9 | 6 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | 6 | 6 | 8 | 6 | 0 | 1.0000 | 0 |
| projection_arbitration | 5 | 8 | 5 | 5 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | 4 | 6 | 4 | 4 | 0 | 1.0000 | 0 |

## Hidden-Family Summary

| Slice | Family | Variant | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| validation250 | benchmark_format_convention | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | benchmark_format_convention | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | benchmark_format_convention | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| validation250 | benchmark_format_convention | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | benchmark_format_convention | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| validation250 | benchmark_format_convention | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | benchmark_format_convention | selective_safety_floor_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | competing_semiologies | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | competing_semiologies | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | competing_semiologies | competing_frequency_uncertainty | 1 | 0 | 1 | 0.0000 | 1 |
| validation250 | competing_semiologies | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | competing_semiologies | lowest_current_frequency | 1 | 0 | 1 | 0.0000 | 1 |
| validation250 | competing_semiologies | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | competing_semiologies | selective_safety_floor_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | current_vs_historical | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | current_vs_historical | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | current_vs_historical | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| validation250 | current_vs_historical | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | current_vs_historical | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| validation250 | current_vs_historical | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | current_vs_historical | selective_safety_floor_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | diary_or_log_aggregation | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | diary_or_log_aggregation | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | diary_or_log_aggregation | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| validation250 | diary_or_log_aggregation | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | diary_or_log_aggregation | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| validation250 | diary_or_log_aggregation | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | diary_or_log_aggregation | selective_safety_floor_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | rate_bucket_or_denominator | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | rate_bucket_or_denominator | combined_selective_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | rate_bucket_or_denominator | competing_frequency_uncertainty | 1 | 0 | 1 | 0.0000 | 1 |
| validation250 | rate_bucket_or_denominator | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | rate_bucket_or_denominator | lowest_current_frequency | 1 | 0 | 1 | 0.0000 | 1 |
| validation250 | rate_bucket_or_denominator | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | rate_bucket_or_denominator | selective_safety_floor_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | seizure_free_duration | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | seizure_free_duration | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | seizure_free_duration | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| validation250 | seizure_free_duration | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | seizure_free_duration | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| validation250 | seizure_free_duration | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | seizure_free_duration | selective_safety_floor_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | uncertainty_or_ambiguity | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | uncertainty_or_ambiguity | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | uncertainty_or_ambiguity | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| validation250 | uncertainty_or_ambiguity | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | uncertainty_or_ambiguity | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| validation250 | uncertainty_or_ambiguity | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | uncertainty_or_ambiguity | selective_safety_floor_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | unclassified | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | unclassified | combined_selective_gate_v0 | 5 | 2 | 0 | 1.0000 | 0 |
| validation250 | unclassified | competing_frequency_uncertainty | 50 | 0 | 47 | 0.0000 | 49 |
| validation250 | unclassified | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | unclassified | lowest_current_frequency | 41 | 1 | 24 | 0.0400 | 25 |
| validation250 | unclassified | projection_boundary_state_priority_gate_v0 | 5 | 2 | 0 | 1.0000 | 0 |
| validation250 | unclassified | selective_safety_floor_gate_v0 | 5 | 2 | 0 | 1.0000 | 0 |
| validation250 | unknown_boundary | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation250 | unknown_boundary | combined_selective_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | unknown_boundary | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| validation250 | unknown_boundary | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation250 | unknown_boundary | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| validation250 | unknown_boundary | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation250 | unknown_boundary | selective_safety_floor_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |

## Would-Change Rows

### Projection Boundary-State Priority
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1880 | validation250 | 8 per 2 month |  | 8 per 2 month |  | Projected the graph by selecting the highest current frequency node. |
| 1979 | validation250 | 6 per 2 month |  | 6 per 2 month |  | Projected the graph by selecting the highest current frequency node. |
| 2907 | validation250 | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2932 | validation250 | seizure free for 9 month | seizure free for 9 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2938 | validation250 | seizure free for 8 month | seizure free for 8 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |

### LLM Candidate Sidecar Rescue
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 3356 | validation250 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |

### Combined Selective Gate
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1880 | validation250 | 8 per 2 month |  | 8 per 2 month |  | Projected the graph by selecting the highest current frequency node. |
| 1979 | validation250 | 6 per 2 month |  | 6 per 2 month |  | Projected the graph by selecting the highest current frequency node. |
| 2907 | validation250 | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2932 | validation250 | seizure free for 9 month | seizure free for 9 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2938 | validation250 | seizure free for 8 month | seizure free for 8 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 3356 | validation250 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |

### Selective Safety-Floor Gate v0
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1880 | validation250 | 8 per 2 month |  | 8 per 2 month |  | Projected the graph by selecting the highest current frequency node. |
| 1979 | validation250 | 6 per 2 month |  | 6 per 2 month |  | Projected the graph by selecting the highest current frequency node. |
| 2907 | validation250 | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2932 | validation250 | seizure free for 9 month | seizure free for 9 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2938 | validation250 | seizure free for 8 month | seizure free for 8 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 3356 | validation250 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
