# Gan 2026 VerificationDecision V0 Baseline

deterministic verification-action baseline over routed rows; no verifier model call, no manual annotation, no replacement label invention, and score context is audit-only

## Artifacts

- Decision JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.verification_decision.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.verification_decision.json`
- Route source: `experiments\gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.route.jsonl`

## Summary

- Input route rows: 450
- Input routed rows: 41
- Decision rows: 41

## Actions

- `abstain`: 41

## Route Families

- `cluster_axis_ambiguity`: 7
- `denominator_window_mismatch`: 2
- `mixed_window_or_vague_addition`: 13
- `relative_only_trend`: 1
- `selected_source_id_invalid`: 15
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Decision Rows

- 750: `abstain`; basis `route_family_policy`; families: denominator_window_mismatch; reason: routed risk family has no deterministic V0 action beyond abstention
- 892: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 1629: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 2597: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 2725: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 2749: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 3353: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 3514: `abstain`; basis `route_family_policy`; families: relative_only_trend; reason: routed risk family has no deterministic V0 action beyond abstention
- 3906: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 7993: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 9562: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 9786: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 9926: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 9942: `abstain`; basis `route_family_policy`; families: denominator_window_mismatch; reason: routed risk family has no deterministic V0 action beyond abstention
- 9979: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 10009: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 10031: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 10186: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 10213: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 10441: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 10445: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 10538: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 10553: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 11401: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 11499: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
