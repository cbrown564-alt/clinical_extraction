# Gan 2026 Exact-Label Selector Ablation

Validation-development selector ablation. Candidate selection uses only non-gold candidate features; gold_match_status is used only after selection to score W->C and C->W. This artifact does not change predictions, inspect locked-test row-level failures, or make a benchmark-comparable claim.

## Summary

Base full-row Purist proxy: 0.9040 (678 / 750).

| Selector | Selected | W->C | C->W | Projected proxy | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `deterministic_window_parseable_v0` | 129 | 6 | 97 | 0.7827 | `reject` |
| `deterministic_non_seizure_free_parseable_v0` | 169 | 16 | 116 | 0.7707 | `reject` |
| `llm_unknown_current_v0` | 98 | 16 | 49 | 0.8600 | `reject` |
| `llm_unknown_any_v0` | 189 | 21 | 122 | 0.7693 | `reject` |
| `nonprediction_llm_unknown_current_v0` | 9 | 9 | 0 | 0.9160 | `promote_candidate` |
| `nonprediction_llm_unknown_any_v0` | 13 | 13 | 0 | 0.9213 | `promote_candidate` |

## Interpretation

`nonprediction_llm_unknown_any_v0` is the least-bad diagnostic selector with projected 691 correct rows, but promotion still depends on proving low C->W risk on a predeclared validation or synthetic hard-slice gate.

## Artifacts

- Ablation CSV: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_exact_label_selector_ablation_2026-06-05.csv`
- Ablation JSON: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_exact_label_selector_ablation_2026-06-05.json`
