# Gan 2026 Selective Safety-Floor Gate v0 Validation Replay (No-Call)

Validation-cycle full-validation replay over saved artifacts only. This is a validation development result and does not imply production promotion or holdout performance.

- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Slice manifest: `experiments/gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json`
- Predeclaration/input manifest: `experiments/gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.json`
- Split manifest: `gan2026_split_v1`
- Rows: 750
- JSONL artifact: `experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.jsonl`
- Summary JSON: `experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.json`

## Slice-level Summary

| Slice | Variant | Rows | Purist correct | Pragmatic correct | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions | Evidence-exact changed | Source-id valid changed | Fallback |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| validation750 | baseline_safety_floor_v2 | 750 | 697 | 704 | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 |
| validation750 | projection_boundary_state_priority_gate_v0 | 750 | 682 | 691 | 13 | 5 | 0 | 1.0000 | 0 | 13 | 13 | 67 |
| validation750 | competing_frequency_uncertainty | 750 | 555 | 557 | 129 | 4 | 112 | 0.0331 | 112 | 129 | 129 | 0 |
| validation750 | lowest_current_frequency | 750 | 584 | 624 | 114 | 5 | 83 | 0.0562 | 83 | 114 | 114 | 0 |
| validation750 | llm_candidate_sidecar_rescue_gate_v0 | 750 | 704 | 711 | 10 | 7 | 0 | 1.0000 | 0 | 10 | 10 | 740 |
| validation750 | combined_selective_gate_v0 | 750 | 708 | 715 | 21 | 11 | 0 | 1.0000 | 0 | 21 | 21 | 729 |
| validation750 | selective_safety_floor_gate_v0 | 750 | 708 | 715 | 21 | 11 | 0 | 1.0000 | 0 | 21 | 21 | 729 |

## Frozen Fixed-Slice Summary

Prior fixed-slice accounting from the frozen manifest source. `combined_selective_gate_v0` is the candidate seed for `selective_safety_floor_gate_v0`.

| Slice | Candidate seed Purist | Candidate seed Pragmatic | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| candidate_generation_rescue | 6 | 10 | 9 | 6 | 0 | 1.0000 | 0 |
| candidate_generation_unknown_seizure_free_boundary | 6 | 6 | 8 | 6 | 0 | 1.0000 | 0 |
| projection_arbitration | 5 | 8 | 5 | 5 | 0 | 1.0000 | 0 |
| projection_unknown_seizure_free_arbitration | 4 | 6 | 4 | 4 | 0 | 1.0000 | 0 |

## Scoring-Convention Caveats

| Row | Gold | Baseline | Candidate | Caveat |
| ---: | --- | --- | --- | --- |
| 15193 | multiple per 13 month | seizure free for multiple year | unknown | `unknown` maps to the same Purist/Pragmatic scorer category as `multiple per 13 month`; treat this as a benchmark-format scoring convention, not exact-label normalization. |

## Hidden-Family Summary

| Slice | Family | Variant | Changed rows | Wrong→Correct | Correct→Wrong | Precision | Deterministic regressions |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| validation750 | benchmark_format_convention | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | benchmark_format_convention | combined_selective_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| validation750 | benchmark_format_convention | competing_frequency_uncertainty | 2 | 2 | 0 | 1.0000 | 0 |
| validation750 | benchmark_format_convention | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation750 | benchmark_format_convention | lowest_current_frequency | 2 | 0 | 0 |  | 0 |
| validation750 | benchmark_format_convention | projection_boundary_state_priority_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| validation750 | benchmark_format_convention | selective_safety_floor_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| validation750 | cluster_burden | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | cluster_burden | combined_selective_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| validation750 | cluster_burden | competing_frequency_uncertainty | 2 | 0 | 0 | 0.0000 | 0 |
| validation750 | cluster_burden | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation750 | cluster_burden | lowest_current_frequency | 2 | 1 | 0 | 0.5000 | 0 |
| validation750 | cluster_burden | projection_boundary_state_priority_gate_v0 | 1 | 0 | 0 |  | 0 |
| validation750 | cluster_burden | selective_safety_floor_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| validation750 | competing_semiologies | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | competing_semiologies | combined_selective_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| validation750 | competing_semiologies | competing_frequency_uncertainty | 4 | 1 | 1 | 0.3333 | 1 |
| validation750 | competing_semiologies | llm_candidate_sidecar_rescue_gate_v0 | 4 | 2 | 0 | 1.0000 | 0 |
| validation750 | competing_semiologies | lowest_current_frequency | 3 | 2 | 1 | 0.6667 | 1 |
| validation750 | competing_semiologies | projection_boundary_state_priority_gate_v0 | 3 | 3 | 0 | 1.0000 | 0 |
| validation750 | competing_semiologies | selective_safety_floor_gate_v0 | 6 | 5 | 0 | 1.0000 | 0 |
| validation750 | current_vs_historical | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | current_vs_historical | combined_selective_gate_v0 | 8 | 6 | 0 | 1.0000 | 0 |
| validation750 | current_vs_historical | competing_frequency_uncertainty | 3 | 1 | 0 | 0.3333 | 0 |
| validation750 | current_vs_historical | llm_candidate_sidecar_rescue_gate_v0 | 6 | 3 | 0 | 1.0000 | 0 |
| validation750 | current_vs_historical | lowest_current_frequency | 2 | 1 | 0 | 0.5000 | 0 |
| validation750 | current_vs_historical | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| validation750 | current_vs_historical | selective_safety_floor_gate_v0 | 8 | 6 | 0 | 1.0000 | 0 |
| validation750 | diary_or_log_aggregation | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | diary_or_log_aggregation | combined_selective_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| validation750 | diary_or_log_aggregation | competing_frequency_uncertainty | 0 | 0 | 0 |  | 0 |
| validation750 | diary_or_log_aggregation | llm_candidate_sidecar_rescue_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| validation750 | diary_or_log_aggregation | lowest_current_frequency | 0 | 0 | 0 |  | 0 |
| validation750 | diary_or_log_aggregation | projection_boundary_state_priority_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation750 | diary_or_log_aggregation | selective_safety_floor_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| validation750 | rate_bucket_or_denominator | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | rate_bucket_or_denominator | combined_selective_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| validation750 | rate_bucket_or_denominator | competing_frequency_uncertainty | 7 | 2 | 1 | 0.4000 | 1 |
| validation750 | rate_bucket_or_denominator | llm_candidate_sidecar_rescue_gate_v0 | 1 | 1 | 0 | 1.0000 | 0 |
| validation750 | rate_bucket_or_denominator | lowest_current_frequency | 7 | 3 | 1 | 0.6000 | 1 |
| validation750 | rate_bucket_or_denominator | projection_boundary_state_priority_gate_v0 | 2 | 1 | 0 | 1.0000 | 0 |
| validation750 | rate_bucket_or_denominator | selective_safety_floor_gate_v0 | 3 | 2 | 0 | 1.0000 | 0 |
| validation750 | seizure_free_duration | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | seizure_free_duration | combined_selective_gate_v0 | 10 | 8 | 0 | 1.0000 | 0 |
| validation750 | seizure_free_duration | competing_frequency_uncertainty | 2 | 1 | 0 | 0.5000 | 0 |
| validation750 | seizure_free_duration | llm_candidate_sidecar_rescue_gate_v0 | 8 | 5 | 0 | 1.0000 | 0 |
| validation750 | seizure_free_duration | lowest_current_frequency | 1 | 1 | 0 | 1.0000 | 0 |
| validation750 | seizure_free_duration | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| validation750 | seizure_free_duration | selective_safety_floor_gate_v0 | 10 | 8 | 0 | 1.0000 | 0 |
| validation750 | uncertainty_or_ambiguity | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | uncertainty_or_ambiguity | combined_selective_gate_v0 | 11 | 9 | 0 | 1.0000 | 0 |
| validation750 | uncertainty_or_ambiguity | competing_frequency_uncertainty | 2 | 2 | 0 | 1.0000 | 0 |
| validation750 | uncertainty_or_ambiguity | llm_candidate_sidecar_rescue_gate_v0 | 8 | 6 | 0 | 1.0000 | 0 |
| validation750 | uncertainty_or_ambiguity | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| validation750 | uncertainty_or_ambiguity | projection_boundary_state_priority_gate_v0 | 5 | 4 | 0 | 1.0000 | 0 |
| validation750 | uncertainty_or_ambiguity | selective_safety_floor_gate_v0 | 11 | 9 | 0 | 1.0000 | 0 |
| validation750 | unclassified | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | unclassified | combined_selective_gate_v0 | 7 | 0 | 0 |  | 0 |
| validation750 | unclassified | competing_frequency_uncertainty | 119 | 0 | 111 | 0.0000 | 111 |
| validation750 | unclassified | llm_candidate_sidecar_rescue_gate_v0 | 0 | 0 | 0 |  | 0 |
| validation750 | unclassified | lowest_current_frequency | 105 | 1 | 82 | 0.0120 | 82 |
| validation750 | unclassified | projection_boundary_state_priority_gate_v0 | 7 | 0 | 0 |  | 0 |
| validation750 | unclassified | selective_safety_floor_gate_v0 | 7 | 0 | 0 |  | 0 |
| validation750 | unknown_boundary | baseline_safety_floor_v2 | 0 | 0 | 0 |  | 0 |
| validation750 | unknown_boundary | combined_selective_gate_v0 | 10 | 9 | 0 | 1.0000 | 0 |
| validation750 | unknown_boundary | competing_frequency_uncertainty | 2 | 2 | 0 | 1.0000 | 0 |
| validation750 | unknown_boundary | llm_candidate_sidecar_rescue_gate_v0 | 8 | 6 | 0 | 1.0000 | 0 |
| validation750 | unknown_boundary | lowest_current_frequency | 1 | 0 | 0 |  | 0 |
| validation750 | unknown_boundary | projection_boundary_state_priority_gate_v0 | 4 | 4 | 0 | 1.0000 | 0 |
| validation750 | unknown_boundary | selective_safety_floor_gate_v0 | 10 | 9 | 0 | 1.0000 | 0 |

## Would-Change Rows

### Projection Boundary-State Priority
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 2907 | validation750 | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2932 | validation750 | seizure free for 9 month | seizure free for 9 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2938 | validation750 | seizure free for 8 month | seizure free for 8 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 6889 | validation750 | multiple per week | 1 per 2 to 3 week | multiple per week | benchmark_format_convention;rate_bucket_or_denominator | Projected with selective unknown/unresolved boundary-state priority. |
| 7785 | validation750 | seizure free for 12 month | seizure free for 12 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 8079 | validation750 | seizure free for 18 month | seizure free for 18 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 9943 | validation750 | 1 cluster per 4 to 5 week, multiple per cluster | 1 per 4 to 5 week | 1 per multiple week | benchmark_format_convention;cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 10594 | validation750 | unknown, 2 per cluster | unknown, 2 per cluster | unknown |  | Projected the graph from an unquantified seizure-frequency state node. |
| 11216 | validation750 | unknown | seizure free for 4 month | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11254 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11259 | validation750 | unknown | seizure free for multiple year | unknown | current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11272 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11350 | validation750 | unknown | multiple per week | multiple per 2 month |  | Projected the graph from an unresolved multiple-frequency state node. |

### LLM Candidate Sidecar Rescue
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 3356 | validation750 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6244 | validation750 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6321 | validation750 | unknown | 1 per day | unknown | rate_bucket_or_denominator;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 10266 | validation750 | unknown | 1 per 5 day | unknown | cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 11254 | validation750 | unknown | seizure free for multiple year | seizure free | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 11259 | validation750 | unknown | seizure free for multiple year | unknown | current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 13858 | validation750 | seizure free for multiple month | no seizure frequency reference | unknown | current_vs_historical;diary_or_log_aggregation;seizure_free_duration | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14025 | validation750 | unknown | seizure free for multiple year | 2 per 6 weeks | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14076 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 15193 | validation750 | multiple per 13 month | seizure free for multiple year | unknown | benchmark_format_convention;competing_semiologies;current_vs_historical;seizure_free_duration | LLM sidecar rescue gate fired after strict evidence/source/id checks. |

### Combined Selective Gate
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 2907 | validation750 | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2932 | validation750 | seizure free for 9 month | seizure free for 9 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2938 | validation750 | seizure free for 8 month | seizure free for 8 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 3356 | validation750 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6244 | validation750 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6321 | validation750 | unknown | 1 per day | unknown | rate_bucket_or_denominator;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6889 | validation750 | multiple per week | 1 per 2 to 3 week | multiple per week | benchmark_format_convention;rate_bucket_or_denominator | Projected with selective unknown/unresolved boundary-state priority. |
| 7785 | validation750 | seizure free for 12 month | seizure free for 12 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 8079 | validation750 | seizure free for 18 month | seizure free for 18 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 9943 | validation750 | 1 cluster per 4 to 5 week, multiple per cluster | 1 per 4 to 5 week | 1 per multiple week | benchmark_format_convention;cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 10266 | validation750 | unknown | 1 per 5 day | unknown | cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 10594 | validation750 | unknown, 2 per cluster | unknown, 2 per cluster | unknown |  | Projected the graph from an unquantified seizure-frequency state node. |
| 11216 | validation750 | unknown | seizure free for 4 month | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11254 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11259 | validation750 | unknown | seizure free for multiple year | unknown | current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11272 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11350 | validation750 | unknown | multiple per week | multiple per 2 month |  | Projected the graph from an unresolved multiple-frequency state node. |
| 13858 | validation750 | seizure free for multiple month | no seizure frequency reference | unknown | current_vs_historical;diary_or_log_aggregation;seizure_free_duration | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14025 | validation750 | unknown | seizure free for multiple year | 2 per 6 weeks | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14076 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 15193 | validation750 | multiple per 13 month | seizure free for multiple year | unknown | benchmark_format_convention;competing_semiologies;current_vs_historical;seizure_free_duration | LLM sidecar rescue gate fired after strict evidence/source/id checks. |

### Selective Safety-Floor Gate v0
| Row | Slice | Gold | Baseline | Variant | Families | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 2907 | validation750 | seizure free for 6 month | seizure free for 6 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2932 | validation750 | seizure free for 9 month | seizure free for 9 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 2938 | validation750 | seizure free for 8 month | seizure free for 8 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 3356 | validation750 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6244 | validation750 | unknown | seizure free for multiple year | unknown | seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6321 | validation750 | unknown | 1 per day | unknown | rate_bucket_or_denominator;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 6889 | validation750 | multiple per week | 1 per 2 to 3 week | multiple per week | benchmark_format_convention;rate_bucket_or_denominator | Projected with selective unknown/unresolved boundary-state priority. |
| 7785 | validation750 | seizure free for 12 month | seizure free for 12 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 8079 | validation750 | seizure free for 18 month | seizure free for 18 month | seizure free for multiple year |  | Projected the graph from an explicit seizure-free state node. |
| 9943 | validation750 | 1 cluster per 4 to 5 week, multiple per cluster | 1 per 4 to 5 week | 1 per multiple week | benchmark_format_convention;cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity | Projected with selective unknown/unresolved boundary-state priority. |
| 10266 | validation750 | unknown | 1 per 5 day | unknown | cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 10594 | validation750 | unknown, 2 per cluster | unknown, 2 per cluster | unknown |  | Projected the graph from an unquantified seizure-frequency state node. |
| 11216 | validation750 | unknown | seizure free for 4 month | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11254 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11259 | validation750 | unknown | seizure free for multiple year | unknown | current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11272 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | Projected with selective unknown/unresolved boundary-state priority. |
| 11350 | validation750 | unknown | multiple per week | multiple per 2 month |  | Projected the graph from an unresolved multiple-frequency state node. |
| 13858 | validation750 | seizure free for multiple month | no seizure frequency reference | unknown | current_vs_historical;diary_or_log_aggregation;seizure_free_duration | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14025 | validation750 | unknown | seizure free for multiple year | 2 per 6 weeks | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 14076 | validation750 | unknown | seizure free for multiple year | unknown | competing_semiologies;current_vs_historical;seizure_free_duration;uncertainty_or_ambiguity;unknown_boundary | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
| 15193 | validation750 | multiple per 13 month | seizure free for multiple year | unknown | benchmark_format_convention;competing_semiologies;current_vs_historical;seizure_free_duration | LLM sidecar rescue gate fired after strict evidence/source/id checks. |
