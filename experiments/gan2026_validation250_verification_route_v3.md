# Gan 2026 Verification Route Mechanics

Deterministic validation250 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation250_verification_route_v3.jsonl`
- Summary JSON: `experiments\gan2026_validation250_verification_route_v3.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_score_validation250_v3.jsonl`

## Summary

- Rows: 250
- Routed rows: 6
- Unrouted rows: 244

## Route Families

- `cluster_axis_ambiguity`: 3
- `medication_cadence_ambiguity`: 1
- `mixed_window_or_vague_addition`: 1
- `multiple_current_primary_facts`: 1

## Routed Score Statuses

- `not_scored_null_rendered_label`: 5
- `scored`: 1

## Routed Rows

- 744: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 3468: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3469: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3493: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3534: multiple_current_primary_facts; score `scored`; purist `False`; reasons: multiple primary candidate ids are present outside an additive or cluster-axis policy
- 5476: medication_cadence_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cadence evidence may describe medication or rescue use rather than events
