# Gan 2026 Boundary/Benchmark Seed Panel v0

Synthetic H3/H7 mechanism seed panel. It tests typed candidate exposure, seizure-free boundary state, benchmark-renderer transparency, and minimal-pair consistency. It is not validation750, not holdout, and not final-label promotion evidence.

## Decision

ready_for_boundary_renderer_contract_tests

## Summary

| Metric | Value |
| --- | ---: |
| rows | 12 |
| pairs | 6 |
| clinical-state invariant pairs | 6 |
| exact evidence rows | 12 |
| boundary rows | 6 |
| renderer rows | 6 |
| hard rows | 10 |
| control rows | 2 |

## Target Families

| Family | Rows |
| --- | ---: |
| `benchmark_format_convention` | 6 |
| `seizure_free_duration` | 6 |

## Target Mechanisms

| Mechanism | Rows |
| --- | ---: |
| `benchmark_convention_renderer_v0` | 6 |
| `seizure_free_boundary_event_v0` | 6 |

## Next Step

Implement typed boundary and benchmark-renderer contract tests against this panel before connecting the mechanisms to any final-label policy.

## Artifacts

- Panel JSONL: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`
