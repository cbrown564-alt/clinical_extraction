# Gan 2026 Boundary/Benchmark Seed Panel v0

Synthetic H3/H7 mechanism seed panel. It tests typed candidate exposure, seizure-free boundary state, benchmark-renderer transparency, and minimal-pair consistency. It is not validation750, not holdout, and not final-label promotion evidence.

## Decision

ready_for_boundary_renderer_contract_tests

## Summary

| Metric | Value |
| --- | ---: |
| rows | 36 |
| pairs | 18 |
| clinical-state invariant pairs | 18 |
| exact evidence rows | 36 |
| boundary rows | 20 |
| renderer rows | 16 |
| hard rows | 24 |
| control rows | 12 |

## Target Families

| Family | Rows |
| --- | ---: |
| `benchmark_format_convention` | 16 |
| `seizure_free_duration` | 20 |

## Target Mechanisms

| Mechanism | Rows |
| --- | ---: |
| `benchmark_convention_renderer_v0` | 16 |
| `seizure_free_boundary_event_v0` | 20 |

## Next Step

Port only the stable typed boundary and benchmark-renderer fields to a validation hard-slice panel. Keep final-label policy disconnected until the validation mechanism surface is robust.

## Artifacts

- Panel JSONL: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`
