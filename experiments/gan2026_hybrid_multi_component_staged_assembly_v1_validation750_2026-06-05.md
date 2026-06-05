# Gan 2026 Hybrid Multi-Component Staged Assembly v1

Validation-development saved-replay final assembly. It makes no new model calls, uses no locked-test row-level artifacts, and does not authorize whole-pipeline promotion or benchmark-comparable claims.

## Coverage

The saved-replay validation assembly emits 750 rows with 735 prediction-bearing rows and 15 abstain/review rows.

## Component Overlay

Boundary/renderer selector rows: 28 selected and 2 suppressed. Suppressed rows keep the base assembled-candidate owner.

## Freeze-Gate Checks

- Final row contract issues: `[]`
- Sidecar gate issues: `[]`
- H6 regressions: `0`
- Release-applied rows: `19`

## Artifacts

- Final assembly JSONL: `experiments/gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05.json`
- Component matrix CSV: `experiments/gan2026_hybrid_multi_component_staged_assembly_v1_validation750_component_matrix_2026-06-05.csv`

## Action Counts

| Action | Rows |
| --- | ---: |
| `abstain` | 9 |
| `human_review` | 6 |
| `predict` | 735 |

## Component Owners

| Owner | Rows |
| --- | ---: |
| `benchmark_renderer` | 10 |
| `deterministic_adapter` | 684 |
| `deterministic_comparator_fallback` | 15 |
| `safety_floor` | 23 |
| `typed_boundary_classifier` | 18 |
