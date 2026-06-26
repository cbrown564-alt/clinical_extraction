# Gan 2026 Verification Route Mechanics

Deterministic validation750 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.route.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.route.json`
- Score source: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.score.jsonl`

## Summary

- Rows: 750
- Routed rows: 92
- Unrouted rows: 658

## Route Families

- `cluster_axis_ambiguity`: 10
- `conditional_only_trigger`: 1
- `denominator_window_mismatch`: 1
- `mixed_window_or_vague_addition`: 2
- `rendered_label_supported_but_policy_sensitive`: 30
- `selected_source_id_invalid`: 46
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Routed Score Statuses

- `not_scored_null_rendered_label`: 17
- `scored`: 75

## Routed Rows

- 1030: rendered_label_supported_but_policy_sensitive; score `scored`; purist `False`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 1046: rendered_label_supported_but_policy_sensitive; score `scored`; purist `False`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 1317: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 1706: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 3356: conditional_only_trigger; score `not_scored_null_rendered_label`; purist `None`; reasons: frequency statement is conditioned on a trigger without a stable baseline rate
- 3507: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 3512: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 3600: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 3791: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 3801: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 4562: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 4592: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 4732: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 5490: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 5837: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 5974: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 6065: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 6153: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 6273: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 6501: cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cluster projection has unparsed or incomplete cluster-axis values
- 6571: selected_source_id_invalid; score `not_scored_null_rendered_label`; purist `None`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 6607: selected_source_id_invalid; score `scored`; purist `True`; reasons: selected evidence is exact but its carried source-id trace is invalid
- 7141: unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: cluster burden is rendered but cadence or cluster axis remains unresolved
- 7198: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
- 7290: rendered_label_supported_but_policy_sensitive; score `scored`; purist `True`; reasons: unknown label rendered from explicit ambiguity rather than absence
