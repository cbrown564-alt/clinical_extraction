# Gan 2026 Boundary/Benchmark Candidate Assembly v0

Validation-development candidate assembly protocol only. It connects passed H3/H7 boundary and benchmark typed fields to candidate rows for diagnostic transition accounting, writes no source note text, and does not authorize final-label promotion or holdout use.

## Decision

candidate_contract_layer_diagnostic_only

## Architecture Decision

Use the passed boundary/renderer typed fields as a shallow validation-only candidate-contract layer over the current assembled candidate. Defer a richer structured event representation until this layer shows enough coverage and no-regression signal.

## Summary

| Metric | Value |
| --- | ---: |
| candidate rows | 30 |
| selected prediction-bearing rows | 30 |
| W->C rows | 6 |
| C->W rows | 1 |
| parse-ok plus exact-evidence rate | 1.0000 |
| source-note-text rows | 0 |
| final-label policy connected | False |
| frozen test audit ready | False |
| holdout authorized | False |

## Gate Failures

- `coverage_below_150`
- `w_to_c_below_60`

## Target Mechanisms

| Mechanism | Rows |
| --- | ---: |
| `benchmark_convention_renderer_v0` | 11 |
| `seizure_free_boundary_event_v0` | 19 |

## Component Owners

| Owner | Rows |
| --- | ---: |
| `benchmark_renderer` | 11 |
| `typed_boundary_classifier` | 19 |

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

## Next Step

Expand the validation hard/control surface before any frozen test audit. If the typed layer still stays below coverage or W->C gates, move to a richer structured event representation with explicit projection ownership.

## Artifacts

- Candidate JSONL: `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.json`
- Source contract JSONL: `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.jsonl`
- Source current candidate JSONL: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.jsonl`
