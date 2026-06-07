# Gan 2026 Verification Route Mechanics

Deterministic validation750 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_current_compare_2026-06-07.route.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_current_compare_2026-06-07.route.json`
- Score source: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_current_compare_2026-06-07.score.jsonl`

## Summary

- Rows: 750
- Routed rows: 68
- Unrouted rows: 682

## Route Families

- `cluster_axis_ambiguity`: 13
- `conditional_only_trigger`: 1
- `mixed_window_or_vague_addition`: 29
- `relative_only_trend`: 2
- `rendered_label_supported_but_policy_sensitive`: 1
- `seizure_free_proxy_evidence_overreach`: 1
- `selected_source_id_invalid`: 18
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Routed Score Statuses

- `not_scored_null_rendered_label`: 47
- `scored`: 21

## Routed Rows

- 1317: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 1706: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 3356: conditional_only_trigger; score `not_scored_null_rendered_label`; purist `None`; reasons: frequency statement is conditioned on a trigger without a stable baseline rate
- 3507: relative_only_trend; score `not_scored_null_rendered_label`; purist `None`; reasons: frequency statement gives only a relative change without an absolute current rate
- 3512: relative_only_trend; score `not_scored_null_rendered_label`; purist `None`; reasons: frequency statement gives only a relative change without an absolute current rate
- 3534: seizure_free_proxy_evidence_overreach; score `not_scored_null_rendered_label`; purist `None`; reasons: seizure-free projection is based on proxy or conditional evidence
- 5551: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 5791: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 5974: selected_source_id_invalid; score `not_scored_null_rendered_label`; purist `None`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 6153: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 6209: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 6501: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 6607: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 6889: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 7141: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 7785: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: seizure-free duration was derived from prior-encounter context
- 9879: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 9937: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10189: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 10200: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 10434: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10542: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10578: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10618: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 10630: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
