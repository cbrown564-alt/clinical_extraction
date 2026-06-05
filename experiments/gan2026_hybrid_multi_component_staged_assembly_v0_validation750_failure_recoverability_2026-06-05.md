# Gan 2026 Assembly Failure Recoverability

Validation-development recoverability analysis over assembly failure rows and saved candidate-discovery artifacts. It does not inspect locked-test row-level failures, change predictions, change scorer policy, or make a benchmark-comparable claim.

## Summary

Failure rows analyzed: 53.
Actionable candidate rows: 21 (0.396).
Exact-label actionable rows: 16; Purist-category-only actionable rows: 5.
Oracle upper-bound full-row Purist scores: exact-label only 0.925; all actionable 0.932.

## Recoverability

| Class | Rows |
| --- | ---: |
| `actionable_candidate` | 21 |
| `candidate_with_evidence_or_source_issue` | 1 |
| `no_recalled_candidate` | 14 |
| `semantic_state_only` | 17 |

## Failure Transitions

| Transition | Rows |
| --- | ---: |
| `W_to_W` | 38 |
| `W_to_abstain` | 9 |
| `W_to_review` | 6 |

## Best Generator

| Generator | Rows |
| --- | ---: |
| `deterministic_candidates_all` | 27 |
| `llm_candidate_selector_raw` | 12 |
| `none` | 14 |

## Interpretation

Run a validation ablation that lets `llm_candidate_selector_raw` override only the 11 actionable failure rows it already recalls with exact evidence and valid source ids; compare W->C and C->W before any holdout use.

## Artifacts

- Recoverability CSV: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_failure_recoverability_2026-06-05.csv`
- Recoverability JSON: `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_failure_recoverability_2026-06-05.json`
