# Gan 2026 VerificationDecision V0 Baseline

deterministic verification-action baseline over routed rows; no verifier model call, no manual annotation, no replacement label invention, and score context is audit-only

## Artifacts

- Decision JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.verification_decision.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.verification_decision.json`
- Route source: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_qwen36_35b_v0_2026-06-07.route.jsonl`

## Summary

- Input route rows: 750
- Input routed rows: 92
- Decision rows: 92

## Actions

- `abstain`: 92

## Route Families

- `cluster_axis_ambiguity`: 10
- `conditional_only_trigger`: 1
- `denominator_window_mismatch`: 1
- `mixed_window_or_vague_addition`: 2
- `rendered_label_supported_but_policy_sensitive`: 30
- `selected_source_id_invalid`: 46
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Decision Rows

- 1030: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 1046: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 1317: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 1706: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 3356: `abstain`; basis `route_family_policy`; families: conditional_only_trigger; reason: routed risk family has no deterministic V0 action beyond abstention
- 3507: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 3512: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 3600: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 3791: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 3801: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 4562: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 4592: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 4732: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 5490: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 5837: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 5974: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 6065: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 6153: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 6273: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 6501: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 6571: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 6607: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 7141: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 7198: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 7290: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
