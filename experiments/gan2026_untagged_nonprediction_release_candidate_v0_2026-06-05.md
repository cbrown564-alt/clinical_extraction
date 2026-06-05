# Gan 2026 Untagged Nonprediction Release Candidate v0

Validation-development no-call candidate patch. It releases only staged-policy nonprediction rows with no hidden-family tags by falling back to the deterministic comparator label. This does not authorize holdout use or benchmark-comparable claims.

## Decision

candidate_patch_passes_validation_no_regression_gate

## Summary

| Metric | Value |
| --- | ---: |
| rows | 750 |
| released rows | 19 |
| panel released rows | 16 |
| prediction-bearing rows | 735 |
| correct prediction rows | 697 |
| release correct rows | 19 |
| release wrong rows | 0 |
| H6 controls | 37 |
| H6 regressions | 0 |

## Release Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_abstain` | 17 |
| `C_to_review` | 2 |

## Next Step

Freeze this validation-cycle candidate in a protocol addendum before any broader assembly use: no hidden-family tags, staged nonprediction, deterministic comparator fallback, and H6 controls unchanged.

## Artifacts

- Candidate JSONL: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.json`
- Component matrix: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`
- H2/H4 panel: `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl`
