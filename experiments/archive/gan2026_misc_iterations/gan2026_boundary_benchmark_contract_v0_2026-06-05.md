# Gan 2026 Boundary/Benchmark Contract Smoke v0

Synthetic H3/H7 mechanism contract smoke. It executes typed boundary classification and benchmark rendering over the seed panel while keeping clinical state and Gan-rendered label separate. It does not connect to final-label policy and is not validation or holdout evidence.

## Decision

boundary_renderer_contract_passed

## Summary

| Metric | Value |
| --- | ---: |
| rows | 36 |
| pairs | 18 |
| clinical-state invariant pairs | 18 |
| contract-matched rows | 36 |
| exact evidence rows | 36 |
| final-label policy connected | False |

## Target Mechanisms

| Mechanism | Rows |
| --- | ---: |
| `benchmark_convention_renderer_v0` | 16 |
| `seizure_free_boundary_event_v0` | 20 |

## Benchmark Rules

| Rule | Rows |
| --- | ---: |
| `gan_cluster_multiple_per_cluster` | 6 |
| `gan_non_epileptic_seizure_free_projection` | 2 |
| `gan_unknown_sentinel` | 4 |
| `gan_vague_multiple_frequency` | 4 |
| `none_boundary_state_only` | 20 |

## Next Step

Port only the stable typed boundary and benchmark-renderer fields to a validation hard-slice panel. Keep final-label policy disconnected until the validation mechanism surface is robust.

## Artifacts

- Contract JSONL: `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
