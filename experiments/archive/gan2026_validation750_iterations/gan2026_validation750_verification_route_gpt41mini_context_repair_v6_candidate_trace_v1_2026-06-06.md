# Gan 2026 Verification Route Mechanics

Deterministic validation750 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation750_verification_route_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_verification_route_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl`

## Summary

- Rows: 750
- Routed rows: 56
- Unrouted rows: 694

## Route Families

- `cluster_axis_ambiguity`: 13
- `conditional_only_trigger`: 1
- `cyclic_window_without_event_count`: 5
- `mixed_window_or_vague_addition`: 29
- `relative_only_trend`: 2
- `rendered_label_supported_but_policy_sensitive`: 1
- `seizure_free_proxy_evidence_overreach`: 1
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Routed Score Statuses

- `None`: 56

## Routed Rows

- 1317: unresolved_cluster_cadence_with_per_cluster_burden; score `None`; purist `None`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 1706: cluster_axis_ambiguity; score `None`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 3356: conditional_only_trigger; score `None`; purist `None`; reasons: frequency statement is conditioned on a trigger without a stable baseline rate
- 3468: cyclic_window_without_event_count; score `None`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3469: cyclic_window_without_event_count; score `None`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3482: cyclic_window_without_event_count; score `None`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3493: cyclic_window_without_event_count; score `None`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3507: relative_only_trend; score `None`; purist `None`; reasons: frequency statement gives only a relative change without an absolute current rate
- 3512: relative_only_trend; score `None`; purist `None`; reasons: frequency statement gives only a relative change without an absolute current rate
- 3534: seizure_free_proxy_evidence_overreach; score `None`; purist `None`; reasons: seizure-free projection is based on proxy or conditional evidence
- 5551: mixed_window_or_vague_addition; score `None`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 5791: mixed_window_or_vague_addition; score `None`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 6209: mixed_window_or_vague_addition; score `None`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 6501: cluster_axis_ambiguity; score `None`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 6889: mixed_window_or_vague_addition; score `None`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 7141: unresolved_cluster_cadence_with_per_cluster_burden; score `None`; purist `None`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 7785: rendered_label_supported_but_policy_sensitive; score `None`; purist `None`; reasons: seizure-free duration was derived from prior-encounter context
- 9879: cluster_axis_ambiguity; score `None`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 9937: cluster_axis_ambiguity; score `None`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10189: unresolved_cluster_cadence_with_per_cluster_burden; score `None`; purist `None`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 10200: unresolved_cluster_cadence_with_per_cluster_burden; score `None`; purist `None`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 10434: cluster_axis_ambiguity; score `None`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10509: cyclic_window_without_event_count; score `None`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 10542: cluster_axis_ambiguity; score `None`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10578: cluster_axis_ambiguity; score `None`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
