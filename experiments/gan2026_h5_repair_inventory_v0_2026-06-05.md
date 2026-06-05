# Gan 2026 H5 Semantic Repair Inventory

Validation-development repair taxonomy only. No locked-test row-level artifacts are used.

- Hypothesis: `H5`
- Split manifest: `gan2026_split_v1`
- Decision: `ready_for_one_family_at_a_time_ablation`
- Locked-test row-level artifacts used: `0`

## Summary

- Repair families: `6`
- Semantic families: `5`
- Quarantined or review-required families: `4`

## Family Taxonomy

| Family | Layer | Portability | Effect | Default policy |
| --- | --- | --- | --- | --- |
| `format_only_prediction_surface` | `format_only_repair` | `general` | `format_only` | `allowed` |
| `selected_evidence_arithmetic` | `selected_evidence_arithmetic_only` | `seizure_frequency` | `denominator_or_window_policy` | `allowed_with_ablation` |
| `benchmark_convention_renderer` | `benchmark_aligned_adapter` | `benchmark_format` | `benchmark_convention_or_sentinel_policy` | `review_required` |
| `seizure_free_boundary_duration` | `semantic_repair_helper` | `clinical_epilepsy` | `boundary_state_or_selected_event` | `quarantine_until_panel_ablation` |
| `non_epileptic_current_event_projection` | `semantic_repair_helper` | `clinical_epilepsy` | `semantic_kind_or_sentinel_state` | `quarantine_until_panel_ablation` |
| `cluster_and_vague_multiple_completion` | `semantic_repair_helper` | `benchmark_format` | `cluster_interpretation_or_benchmark_convention` | `review_required` |

## Saved Ladder Mapping

| Condition | Family | Changed | Semantic-kind transitions | W->C | C->W |
| --- | --- | ---: | ---: | ---: | ---: |
| `benchmark_aligned_adapter` | `benchmark_convention_renderer` | 28 | 15 | 16 | 0 |
| `format_only_repair` | `format_only_prediction_surface` | 7 | 0 | 0 | 0 |
| `full_stack` | `benchmark_convention_renderer` | 28 | 15 | 16 | 0 |
| `selected_evidence_arithmetic_only` | `selected_evidence_arithmetic` | 57 | 16 | 32 | 1 |

## Interpretation

This inventory separates format-only label cleanup from semantic repair families that can change the prediction-bearing clinical state or Gan-rendered label. The next experiment should disable or isolate one semantic family at a time; no boundary/renderer or action-policy changes should be mixed into that ablation.
