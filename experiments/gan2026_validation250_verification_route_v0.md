# Gan 2026 Verification Route V0

Deterministic validation250 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation250_verification_route_v0.jsonl`
- Summary JSON: `experiments\gan2026_validation250_verification_route_v0.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_score_validation250_v0.jsonl`

## Summary

- Rows: 250
- Routed rows: 13
- Unrouted rows: 237

## Route Families

- `cluster_axis_ambiguity`: 11
- `mixed_window_or_vague_addition`: 1
- `multiple_current_primary_facts`: 1

## Routed Score Statuses

- `not_scored_null_rendered_label`: 12
- `scored`: 1

## Routed Rows

- 338: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 744: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 1317: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 1573: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 1707: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3468: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3469: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3493: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3534: multiple_current_primary_facts; score `scored`; purist `False`; reasons: multiple primary candidate ids are present outside an additive or cluster-axis policy
- 4173: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 4480: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 5476: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 5551: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
