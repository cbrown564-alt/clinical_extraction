# Gan 2026 Benchmark Renderer Fixture v1

Synthetic benchmark_renderer_fixture_v1. It freezes input clinical state, exercises benchmark-only rendering, exposes renderer rule ids and scorer-sentinel use, and keeps final-label policy disconnected. It is not validation or holdout evidence.

## Decision

benchmark_renderer_fixture_v1_passed

## Summary

| Metric | Value |
| --- | ---: |
| rows | 16 |
| clinical-state preserved rows | 16 |
| format-only rows | 16 |
| renderer rule-id rows | 16 |
| sentinel visibility rows | 16 |
| scorer-sentinel used rows | 14 |
| exact evidence rows | 16 |
| contract-matched rows | 16 |
| final-label policy connected | False |

## Renderer Rules

| Rule | Rows |
| --- | ---: |
| `gan_cluster_multiple_per_cluster` | 6 |
| `gan_non_epileptic_seizure_free_projection` | 2 |
| `gan_unknown_sentinel` | 4 |
| `gan_vague_multiple_frequency` | 4 |

## Next Step

Run boundary_renderer_component_ablation_v1 as validation diagnostics with benchmark-only gains separated from clinical-state changes.

## Artifacts

- Fixture JSONL: `experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
