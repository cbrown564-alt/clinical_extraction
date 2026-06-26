# Gan 2026 VerificationDecision V0 Baseline

deterministic verification-action baseline over routed rows; no verifier model call, no manual annotation, no replacement label invention, and score context is audit-only

## Artifacts

- Decision JSONL: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.verification_decision.jsonl`
- Summary JSON: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.verification_decision.json`
- Route source: `experiments\gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.route.jsonl`

## Summary

- Input route rows: 750
- Input routed rows: 73
- Decision rows: 73

## Actions

- `abstain`: 73

## Route Families

- `cluster_axis_ambiguity`: 13
- `conditional_only_trigger`: 1
- `cyclic_window_without_event_count`: 5
- `mixed_window_or_vague_addition`: 29
- `relative_only_trend`: 2
- `rendered_label_supported_but_policy_sensitive`: 1
- `seizure_free_proxy_evidence_overreach`: 1
- `selected_source_id_invalid`: 18
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Decision Rows

- 1317: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 1706: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 3356: `abstain`; basis `route_family_policy`; families: conditional_only_trigger; reason: routed risk family has no deterministic V0 action beyond abstention
- 3468: `abstain`; basis `route_family_policy`; families: cyclic_window_without_event_count; reason: cyclic vulnerability window lacks event count or burden for automated projection
- 3469: `abstain`; basis `route_family_policy`; families: cyclic_window_without_event_count; reason: cyclic vulnerability window lacks event count or burden for automated projection
- 3482: `abstain`; basis `route_family_policy`; families: cyclic_window_without_event_count; reason: cyclic vulnerability window lacks event count or burden for automated projection
- 3493: `abstain`; basis `route_family_policy`; families: cyclic_window_without_event_count; reason: cyclic vulnerability window lacks event count or burden for automated projection
- 3507: `abstain`; basis `route_family_policy`; families: relative_only_trend; reason: routed risk family has no deterministic V0 action beyond abstention
- 3512: `abstain`; basis `route_family_policy`; families: relative_only_trend; reason: routed risk family has no deterministic V0 action beyond abstention
- 3534: `abstain`; basis `route_family_policy`; families: seizure_free_proxy_evidence_overreach; reason: proxy-only seizure-free evidence has no safe automated replacement label
- 5551: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 5791: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 5974: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 6153: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 6209: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 6501: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 6607: `abstain`; basis `route_family_policy`; families: selected_source_id_invalid; reason: routed risk family has no deterministic V0 action beyond abstention
- 6889: `abstain`; basis `route_family_policy`; families: mixed_window_or_vague_addition; reason: routed risk family has no deterministic V0 action beyond abstention
- 7141: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 7785: `abstain`; basis `route_family_policy`; families: rendered_label_supported_but_policy_sensitive; reason: routed risk family has no deterministic V0 action beyond abstention
- 9879: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 9937: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
- 10189: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 10200: `abstain`; basis `route_family_policy`; families: unresolved_cluster_cadence_with_per_cluster_burden; reason: routed risk family has no deterministic V0 action beyond abstention
- 10434: `abstain`; basis `route_family_policy`; families: cluster_axis_ambiguity; reason: routed risk family has no deterministic V0 action beyond abstention
