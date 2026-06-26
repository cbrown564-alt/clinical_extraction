# Gan 2026 H5 Repair Policy v1 Manifest

Validation-development policy contract for the next diagnostic. No locked-test row-level artifacts are used.

- Repair policy: `h5_repair_policy_v1`
- Split manifest: `gan2026_split_v1`
- Decision: `current_bounded_policy_for_next_validation_diagnostic`
- Locked-test row-level artifacts used: `0`
- Holdout use authorized: `False`

## Validation250 Replay

| Condition | Purist | Changed | W->C | C->W | Semantic-kind transitions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `format_only_repair` | 0.7760 | 20 | 6 | 0 | 0 |
| `selected_evidence_arithmetic_only` | 0.9000 | 70 | 38 | 1 | 16 |
| `benchmark_aligned_adapter` | 0.8520 | 41 | 25 | 0 | 12 |

## Bounds

| Bound | Status |
| --- | --- |
| `frequency_bearing_prediction_may_not_become_no_reference` | `disabled` |
| `per_hour_rates_render_as_multiple_per_day` | `allowed_benchmark_rendering` |
| `vague_frequency_words_render_as_unresolved_multiple` | `allowed_benchmark_rendering` |
| `cluster_context_preserves_frequency_content` | `allowed_with_explicit_ablation` |
| `benchmark_rendering_separate_from_clinical_selection` | `required` |

## Transformation Guard

- Semantic-kind rows: `28`
- Frequency-to-no-reference rows: `0`
- Invalid selected-evidence rows: `2`
- Benchmark adapter Purist replay: `0.8520`

## Interpretation

Use this policy as the bounded H5 repair contract for the next validation diagnostic. It permits format repair and bounded benchmark rendering, blocks broad frequency-to-no-reference demotion, and keeps renderer effects separate from clinical selection claims.
