# Gan 2026 Boundary Event Validation Panel v1

Validation-development boundary_event_validation_panel_v1. It emits only supported exact-evidence typed-event rows, suppresses unsupported records from the row artifact, omits source note text, and keeps final-label policy disconnected. It does not authorize candidate assembly or holdout use.

## Decision

boundary_event_validation_panel_v1_ready

## Summary

| Metric | Value |
| --- | ---: |
| source records scanned | 750 |
| emitted rows | 30 |
| suppressed source records | 720 |
| unsupported candidate rows | 0 |
| boundary rows | 19 |
| renderer rows | 11 |
| hard rows | 22 |
| control rows | 8 |
| exact evidence rows | 30 |
| source-note-text rows | 0 |
| typed-event complete rows | 30 |
| projection-policy complete rows | 30 |
| final-label policy connected | False |

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

## Event Kinds

| Event kind | Rows |
| --- | ---: |
| `benchmark_format_convention` | 11 |
| `conditional_or_trigger_only` | 3 |
| `last_event_only` | 6 |
| `non_epileptic_current_events` | 2 |
| `seizure_free_interval` | 8 |

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `benchmark_renderer` | 11 |
| `boundary_projection_policy` | 19 |

## Next Step

Run h7_minimal_pair_panel_v1 and benchmark_renderer_fixture_v1 before connecting this typed-event surface to validation diagnostic assembly.

## Artifacts

- Panel JSONL: `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.json`
