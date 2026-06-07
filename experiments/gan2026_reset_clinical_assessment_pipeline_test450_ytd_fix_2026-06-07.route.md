# Gan 2026 Verification Route Mechanics

Deterministic validation450 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.route.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.route.json`
- Score source: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.score.jsonl`

## Summary

- Rows: 450
- Routed rows: 41
- Unrouted rows: 409

## Route Families

- `cluster_axis_ambiguity`: 7
- `denominator_window_mismatch`: 2
- `mixed_window_or_vague_addition`: 13
- `relative_only_trend`: 1
- `selected_source_id_invalid`: 15
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Routed Score Statuses

- `not_scored_null_rendered_label`: 21
- `scored`: 20

## Routed Rows

- 750: denominator_window_mismatch; score `scored`; purist `True`; reasons: the chosen phrase implies a windowed cadence that may not match the rendered denominator
- 892: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 1629: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 2597: selected_source_id_invalid; score `scored`; purist `False`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 2725: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 2749: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 3353: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 3514: relative_only_trend; score `not_scored_null_rendered_label`; purist `None`; reasons: frequency statement gives only a relative change without an absolute current rate
- 3906: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 7993: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 9562: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 9786: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 9926: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 9942: denominator_window_mismatch; score `scored`; purist `False`; reasons: the chosen phrase implies a windowed cadence that may not match the rendered denominator
- 9979: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10009: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10031: selected_source_id_invalid; score `scored`; purist `False`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 10186: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 10213: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 10441: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10445: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `False`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 10538: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 10553: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 11401: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 11499: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
