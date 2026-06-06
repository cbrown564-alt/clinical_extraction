# Gan 2026 Reset-Stage Component Inventory

Validation-development component inventory only. This artifact records how old Gan 2026 component families map into reset-stage owners, portability categories, and ablation switches. It authorizes no locked-test row-level inspection, no benchmark-comparable claim, and no whole-pipeline promotion.

- Split manifest: `gan2026_split_v1`
- Component families: `18`
- Ported or retained families: `15`
- Pending policy families: `1`

## Inventory

| Old family | Reset stage | New family | Portability | Ablation switch | Status |
| --- | --- | --- | --- | --- | --- |
| `selected-evidence frequency repair` | `normalize` | `selected_evidence_frequency_value_recovery` | `seizure_frequency` | `normalize_selected_evidence_frequency_value_recovery` | `ported_v6` |
| `vague period rates` | `normalize` | `vague_period_frequency_value_recovery` | `seizure_frequency` | `normalize_vague_period_frequency_value_recovery` | `ported_v6` |
| `diary date lists` | `normalize` | `diary_date_list_frequency_recovery` | `gan2026_specific` | `normalize_diary_date_list_frequency_recovery` | `ported_v6` |
| `seizure-free duration/date handling` | `normalize` | `seizure_free_duration_date_instrumentation` | `seizure_frequency` | `normalize_seizure_free_duration_date_instrumentation` | `ported_v6` |
| `summary-rate priority` | `project` | `current_summary_rate_priority` | `seizure_frequency` | `project_current_summary_rate_priority` | `ported_v6` |
| `previous-month/current-month aggregation` | `project` | `previous_active_month_over_current_month_zero` | `seizure_frequency` | `project_previous_active_month_over_current_month_zero` | `ported_v6` |
| `major-semiology recent relapse priority` | `project` | `major_recent_relapse_over_background_frequency` | `clinical_epilepsy` | `project_major_recent_relapse_over_background_frequency` | `ported_v6` |
| `relative-only trend guard` | `verify` | `relative_only_trend` | `clinical_epilepsy` | `route_relative_only_trend` | `ported_route_family_v6` |
| `conditional-only trigger guard` | `verify` | `conditional_only_trigger` | `clinical_epilepsy` | `route_conditional_only_trigger` | `ported_route_family_v6` |
| `selected-evidence missing exact trace` | `verify` | `selected_evidence_missing_exact_trace` | `general` | `route_selected_evidence_missing_exact_trace` | `ported_route_family_v6` |
| `selected source id invalid` | `verify` | `selected_source_id_invalid` | `general` | `route_selected_source_id_invalid` | `ported_route_family_v6` |
| `denominator-window mismatch` | `verify` | `denominator_window_mismatch` | `benchmark_format` | `route_denominator_window_mismatch` | `ported_route_family_v6` |
| `cluster cadence versus per-cluster burden ambiguity` | `verify` | `unresolved_cluster_cadence_with_per_cluster_burden` | `seizure_frequency` | `route_unresolved_cluster_cadence_with_per_cluster_burden` | `ported_route_contract_v6` |
| `comparator-label preservation` | `verify` | `named_comparator_preservation_action_policy` | `benchmark_format` | `verify_named_comparator_preservation_action_policy` | `pending_policy_decision` |
| `H6/H9/H10 sidecars` | `report` | `audit_sidecars_only` | `general` | `report_audit_sidecars_only` | `retained_audit_only` |
| `component evidence matrix` | `report` | `stage_owned_component_evidence_matrix` | `general` | `report_stage_owned_component_evidence_matrix` | `retained_audit_only` |
| `broad hybrid adjudicator fallback` | `retired` | `do_not_port_broad_hybrid_fallback` | `gan2026_specific` | `retired_do_not_port_broad_hybrid_fallback` | `retired_do_not_port` |
| `broad state-graph projection` | `retired` | `do_not_port_broad_state_graph_projection` | `seizure_frequency` | `retired_do_not_port_broad_state_graph_projection` | `retired_do_not_port` |

## Notes

| New family | Issue or rule ids | Notes |
| --- | --- | --- |
| `selected_evidence_frequency_value_recovery` | `frequency_rate_values_repaired_from_primary_candidate`, `frequency_rate_values_repaired_from_selected_evidence` | Ported as explicit reset normalization instead of hidden scorer-facing repair. |
| `vague_period_frequency_value_recovery` | `frequency_label_values_unparsed`, `frequency_rate_values_incomplete` | Covers vague weekly/monthly/yearly burden only when an explicit period exists in source-backed evidence. |
| `diary_date_list_frequency_recovery` | `frequency_rate_values_repaired_from_diary_dates` | Kept separate because diary-style aggregation is useful on Gan letters but needs explicit portability discipline. |
| `seizure_free_duration_date_instrumentation` | `seizure_free_duration_repaired_from_since_date`, `seizure_free_duration_repaired_from_last_event_date` | Owns durations, since-dates, last-event anchors, and same-note temporal carry-forward before projection. |
| `current_summary_rate_priority` | `current_summary_rate_priority` | Allows explicit current summary burden to own projection when it cleanly outranks long-window background evidence. |
| `previous_active_month_over_current_month_zero` | `previous_active_month_over_current_month_zero` | Restores the narrow current-vs-historical policy family without reopening broad additive rendering. |
| `major_recent_relapse_over_background_frequency` | `major_recent_relapse_over_background_frequency` | A dominant recent convulsive relapse can own the projected current burden when source-backed and policy-named. |
| `relative_only_trend` | `relative_change_without_current_baseline` | Moved out of anonymous parse failure and into an explicit route family for non-renderable trend-only evidence. |
| `conditional_only_trigger` | `conditional_only_trigger_without_baseline` | Conditional event triggers are now explicit verification debt rather than silent unknown/null drift. |
| `selected_evidence_missing_exact_trace` | `selected_evidence_missing_exact_trace` | Ported only after the reset gained explicit provenance fields with exact-trace and source-id status. |
| `selected_source_id_invalid` | `selected_source_id_invalid` | Separated from missing exact trace so provenance review can distinguish invalid ids from non-exact evidence. |
| `denominator_window_mismatch` | `denominator_window_mismatch` | Kept as route/report ownership because the Gan-compatible label can be rendered while the denominator semantics remain review-sensitive. |
| `unresolved_cluster_cadence_with_per_cluster_burden` | `cluster_cadence_unknown_with_per_cluster_burden` | Reset now allows a convention-compatible rendered label while routing the remaining cadence/axis ambiguity for review. |
| `named_comparator_preservation_action_policy` | `comparator_preservation_policy_pending` | Explicitly deferred. If it returns, it must be a named action policy rather than hidden fallback. |
| `audit_sidecars_only` | `h6_h9_h10_audit_only` | Useful instrumentation remains available, but these no longer count as core reset pipeline stages. |
| `stage_owned_component_evidence_matrix` | `component_evidence_matrix_audit_only` | Retained as audit/reporting debt until it is fully redesigned around the reset-stage schemas. |
| `do_not_port_broad_hybrid_fallback` | `broad_hybrid_fallback_retired` | Explicitly rejected because it blurred selection, projection, and fallback ownership. |
| `do_not_port_broad_state_graph_projection` | `broad_state_graph_projection_retired` | Historical evidence is preserved, but broad projection replacement stays out of the reset path. |

## Interpretation

The reset now has a durable crosswalk for what was ported, what remains audit-only, and what is explicitly retired. New deterministic behavior should add a portability category and named ablation switch before it is described as part of the reset architecture.
