# Gan 2026 Boundary/Benchmark Validation Contract Smoke v0

Validation-development H3/H7 typed-field contract smoke over the boundary/benchmark validation panel. It checks typed-field classification, exact-evidence carry-through, renderer transparency, and absence of note text or final-label policy connection. It does not authorize candidate assembly or holdout use.

## Decision

boundary_renderer_validation_contract_passed

## Summary

| Metric | Value |
| --- | ---: |
| rows | 30 |
| hard rows | 22 |
| control rows | 8 |
| contract-matched rows | 30 |
| exact evidence rows | 30 |
| source-note-text rows | 0 |
| final-label policy connected | False |

## Target Mechanisms

| Mechanism | Rows |
| --- | ---: |
| `benchmark_convention_renderer_v0` | 11 |
| `seizure_free_boundary_event_v0` | 19 |

## Slices

| Slice | Rows |
| --- | ---: |
| `asserted_seizure_free_interval` | 8 |
| `cluster_multiple_per_cluster` | 3 |
| `conditional_or_trigger_only` | 3 |
| `last_event_only` | 6 |
| `non_epileptic_current_events` | 2 |
| `unknown_sentinel` | 1 |
| `vague_multiple_frequency` | 7 |

## Benchmark Rules

| Rule | Rows |
| --- | ---: |
| `gan_cluster_multiple_per_cluster` | 3 |
| `gan_unknown_sentinel` | 1 |
| `gan_vague_multiple_frequency` | 7 |
| `none_boundary_state_only` | 19 |

## Next Step

Use this passed validation mechanism contract as a pre-assembly control, then decide whether to connect the typed boundary/renderer fields to a candidate assembly protocol on validation only.

## Artifacts

- Contract JSONL: `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.jsonl`
