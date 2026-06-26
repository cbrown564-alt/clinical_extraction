# Gan 2026 Verification Route Mechanics

Deterministic validation750 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation750_verification_route_gpt41mini_context_repair_v0_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_verification_route_gpt41mini_context_repair_v0_2026-06-06.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v0_2026-06-06.jsonl`

## Summary

- Rows: 750
- Routed rows: 48
- Unrouted rows: 702

## Route Families

- `cluster_axis_ambiguity`: 13
- `cyclic_window_without_event_count`: 5
- `mixed_window_or_vague_addition`: 29
- `seizure_free_proxy_evidence_overreach`: 1

## Routed Score Statuses

- `not_scored_null_rendered_label`: 48

## Routed Rows

- 1706: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 3468: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3469: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3482: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3493: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3534: seizure_free_proxy_evidence_overreach; score `not_scored_null_rendered_label`; purist `None`; reasons: seizure-free projection is based on proxy or conditional evidence
- 5551: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 5791: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 6209: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 6501: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 6889: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 9879: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 9937: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 10434: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 10509: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 10542: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 10578: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 10630: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis operands
- 12127: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 12192: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 12236: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 12366: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 12378: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 12403: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
- 12422: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete operands
