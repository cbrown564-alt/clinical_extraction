# Gan 2026 Boundary/Benchmark Contract Smoke v0

Synthetic H3/H7 mechanism contract smoke. It executes typed boundary classification and benchmark rendering over the seed panel while keeping clinical state and Gan-rendered label separate. It does not connect to final-label policy and is not validation or holdout evidence.

## Decision

boundary_renderer_contract_passed

## Summary

| Metric | Value |
| --- | ---: |
| rows | 12 |
| pairs | 6 |
| clinical-state invariant pairs | 6 |
| contract-matched rows | 12 |
| exact evidence rows | 12 |
| final-label policy connected | False |

## Target Mechanisms

| Mechanism | Rows |
| --- | ---: |
| `benchmark_convention_renderer_v0` | 6 |
| `seizure_free_boundary_event_v0` | 6 |

## Benchmark Rules

| Rule | Rows |
| --- | ---: |
| `gan_cluster_multiple_per_cluster` | 2 |
| `gan_unknown_sentinel` | 2 |
| `gan_vague_multiple_frequency` | 2 |
| `none_boundary_state_only` | 6 |

## Next Step

Broaden the mechanism contract with generated hard/control cases and then port only the stable typed fields to a validation hard-slice panel.

## Artifacts

- Contract JSONL: `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
