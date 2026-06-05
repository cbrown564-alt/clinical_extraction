# Gan 2026 Boundary Selector Precision Revision v1

Validation-only selector precision revision over boundary_renderer_component_ablation_v1. It suppresses unsafe last-event seizure-free overrides and unknown/no-reference sentinel churn, writes no source note text, and does not authorize final-label promotion or holdout use.

## Decision

boundary_selector_precision_revision_v1_precision_fixed_low_coverage

## Summary

| Metric | Value |
| --- | ---: |
| candidate rows | 30 |
| selected prediction-bearing rows | 28 |
| suppressed rows | 2 |
| W->C rows | 6 |
| C->W rows | 0 |
| H6 control regression rows | 0 |
| non-convention C->W rows | 0 |
| final-label policy connected | False |
| frozen test audit ready | False |

## Suppression Reasons

| Reason | Rows |
| --- | ---: |
| `last_event_current_seizure_free_protected` | 1 |
| `unknown_no_reference_sentinel_churn` | 1 |

## Gate Failures

- `coverage_below_150`
- `w_to_c_below_25`

## Next Step

Keep this selector rule as a validation-cycle diagnostic only. The precision issue is fixed, but exposure remains too low for any larger assembly or frozen audit.

## Artifacts

- Revision JSONL: `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json`
- Source ablation JSONL: `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.jsonl`
