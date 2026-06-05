# Gan 2026 H7 Minimal Pair Panel v1

Synthetic H7 minimal-pair robustness panel. It reuses boundary_event_contract_v1 rows to test whether typed mechanism state is preserved across wording, order, section, distractor, semiology, and time-anchor perturbations. It is not validation or holdout evidence and does not connect final-label policy.

## Decision

h7_minimal_pair_panel_v1_passed

## Summary

| Metric | Value |
| --- | ---: |
| rows | 36 |
| pairs | 18 |
| complete pairs | 18 |
| clinical-state invariant pairs | 18 |
| exact evidence rows | 36 |
| final-label policy connected | False |

## Perturbation Axes

| Axis | Pairs | Invariant pairs | Rows |
| --- | ---: | ---: | ---: |
| `distractor_trigger_context` | 1 | 1 | 2 |
| `order` | 3 | 3 | 6 |
| `order_distractor` | 1 | 1 | 2 |
| `order_semiology` | 2 | 2 | 4 |
| `section_distractor` | 1 | 1 | 2 |
| `sentinel_boundary` | 1 | 1 | 2 |
| `wording` | 5 | 5 | 10 |
| `wording_semiology` | 2 | 2 | 4 |
| `wording_time_anchor` | 2 | 2 | 4 |

## Next Step

Add benchmark_renderer_fixture_v1 with clinical state frozen and renderer effects explicit before boundary_renderer_component_ablation_v1.

## Artifacts

- Panel JSONL: `experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.json`
- Source contract JSONL: `experiments/gan2026_boundary_event_contract_v1_2026-06-05.jsonl`
