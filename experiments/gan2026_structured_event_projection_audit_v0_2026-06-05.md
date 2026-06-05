# Gan 2026 Structured Event Projection Audit v0

Validation-development structured event/projection audit only. It writes no source note text, uses no locked-test row-level artifacts, and does not authorize holdout-facing use.

## Decision

structured_projection_schema_ready_for_validation_expansion

## Representation Decision

Replace the shallow typed-candidate bridge with explicit clinical event ownership and benchmark projection/rendering ownership. This audit is schema and attribution evidence only; validation gates still control any later frozen-test protocol.

## Summary

| Metric | Value |
| --- | ---: |
| candidate rows | 30 |
| selected prediction-bearing rows | 30 |
| W->C rows | 6 |
| C->W rows | 1 |
| C->W rate | 0.0333 |
| parse-ok plus exact-evidence rate | 1.0000 |
| projection-ownership explicit rows | 30 |
| no-regression case rows | 1 |
| source-note-text rows | 0 |
| schema ready | True |
| frozen test audit ready | False |
| holdout authorized | False |

## Gate Failures

- `coverage_below_150`
- `w_to_c_below_60`

## Clinical Event Owners

| Owner | Rows |
| --- | ---: |
| `typed_boundary_classifier` | 19 |
| `typed_event_extractor` | 11 |

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `benchmark_renderer` | 11 |
| `boundary_projection_policy` | 19 |

## Next Step

Broaden the structured event generator around this projection-owner schema and carry the C->W row as a named no-regression control. Do not write a frozen test450 protocol until validation coverage, W->C, C->W, and parse/evidence gates pass.

## Artifacts

- Projection audit JSONL: `experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.json`
- Source candidate JSONL: `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.jsonl`
