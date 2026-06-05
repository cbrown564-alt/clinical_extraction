# Gan 2026 Boundary Renderer Component Ablation v1

Validation-development boundary_renderer_component_ablation_v1. It connects the passed typed-event panel only inside a validation diagnostic layer, separates benchmark-only rendering from clinical boundary projection, writes no source note text, and does not authorize final-label promotion or holdout use.

## Decision

boundary_renderer_component_ablation_v1_rejected_revise_only

## Summary

| Metric | Value |
| --- | ---: |
| candidate rows | 30 |
| selected prediction-bearing rows | 30 |
| W->C rows | 6 |
| C->W rows | 1 |
| C->W rate | 0.0333 |
| non-convention C->W rows | 1 |
| H6 control rows | 37 |
| selected H6 rows | 5 |
| H6 control regression rows | 1 |
| exact evidence rows | 30 |
| source-note-text rows | 0 |
| final-label policy connected | False |
| frozen test audit ready | False |

## Gate Failures

- `coverage_below_150`
- `w_to_c_below_25`
- `c_to_w_outside_benchmark_convention`
- `h6_control_regression`

## Effect Classes

| Effect class | W->C | C->W | C->C | W->W |
| --- | ---: | ---: | ---: | ---: |
| `benchmark_only_rendering` | 0 | 0 | 11 | 0 |
| `clinical_boundary_projection` | 6 | 1 | 12 | 0 |

## Next Step

Do not promote this low-exposure typed layer. Revise the validation-only cycle to improve selector precision for last-event and unknown-frequency boundary rows before any larger diagnostic assembly.

## Artifacts

- Ablation JSONL: `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.jsonl`
- Source current candidate JSONL: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.jsonl`
