# Gan 2026 Boundary Event Contract v1

Synthetic boundary_event_contract_v1 mechanism smoke. It exposes clinical_event, boundary_state, selected_frequency_state, projection_policy, and gan_rendered_label while keeping final-label policy disconnected. It is not validation or holdout evidence.

## Decision

boundary_event_contract_v1_passed

## Summary

| Metric | Value |
| --- | ---: |
| rows | 36 |
| pairs | 18 |
| clinical-state invariant pairs | 18 |
| contract-matched rows | 36 |
| exact evidence rows | 36 |
| typed-event complete rows | 36 |
| projection-policy complete rows | 36 |
| final-label policy connected | False |

## Event Kinds

| Event kind | Rows |
| --- | ---: |
| `active_residual_seizure_frequency` | 4 |
| `benchmark_format_convention` | 16 |
| `conditional_or_trigger_only` | 4 |
| `last_event_only` | 4 |
| `no_boundary_evidence` | 2 |
| `non_epileptic_current_events` | 2 |
| `seizure_free_interval` | 4 |

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `benchmark_renderer` | 16 |
| `boundary_projection_policy` | 20 |

## Next Step

Run boundary_event_validation_panel_v1 on validation hard/control rows with final policy disconnected, exact evidence required, and unsupported candidates suppressed.

## Artifacts

- Contract JSONL: `experiments/gan2026_boundary_event_contract_v1_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_event_contract_v1_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
