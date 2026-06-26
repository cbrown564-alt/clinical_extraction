# Gan 2026 H5 Repair Family Ablation

Validation-development same-output ladder interpretation only. No prediction policy changes or locked-test row-level artifacts are used.

- Hypothesis: `H5`
- Split manifest: `gan2026_split_v1`
- Decision: `repair_policy_review_required_before_new_candidate`
- Locked-test row-level artifacts used: `0`

## Family Decisions

| Family | Changed | Semantic-kind transitions | W->C | C->W | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `benchmark_convention_renderer` | 28 | 15 | 16 | 0 | `review_required` |
| `format_only_prediction_surface` | 7 | 0 | 0 | 0 | `keep_allowed` |
| `selected_evidence_arithmetic` | 57 | 16 | 32 | 1 | `revise_or_bound` |

## Interpretation

Format-only repair remains allowed. Any family with semantic-kind, Purist/Pragmatic category, or raw-correct-to-wrong transitions needs a bounded policy decision before it can contribute to a promoted candidate. Benchmark rendering remains review-required because its wins are scorer-facing unless clinical state preservation is shown separately.
