# Gan 2026 Validation750 First Component Ablation Table V6

saved validation-development reset-stage component ablation summary only; it uses the reset inventory plus saved V5/V6 and candidate-trace route artifacts, authorizes no locked-test row-level inspection, no live model call, and no benchmark-comparable claim

## Status

This saved-artifact report materializes the first reset-stage component ablation table from the inventory plus the V5/V6 and candidate-trace route artifacts. Where a family-level off-state delta is not isolated by those saved artifacts, the report leaves the field pending instead of inventing precision.

## Surface Summary

| Surface | Count |
| --- | ---: |
| V5 rendered rows | `573` |
| V6 rendered rows | `580` |
| V5 null rows | `177` |
| V6 null rows | `170` |
| V6 provenance-only routed rows | `220` |
| V6 clinical/policy routed rows | `56` |
| candidate-trace routed rows | `56` |
| candidate-trace clinical/policy rows | `56` |
| candidate-trace pure non-provenance target rows | `56` |
| candidate-trace residual `selected_source_id_invalid` tail | `0` |

## Recovered Rows

- Recovered row ids: `2609, 4690, 4694, 4700, 4709, 6180, 7409`
- Recovered projection rule ids: `{'frequency_rate_values_v0': 7}`
- Recovered projection issue counts: `{'vague_count': 6, 'vague_frequency_with_explicit_time_period': 1}`
- Recovered frequency-family counts: `{'selected_evidence_frequency_value_recovery': 5, 'vague_period_frequency_value_recovery': 2}`
- Recovered frequency-family rows: `{'diary_date_list_frequency_recovery': [], 'selected_evidence_frequency_value_recovery': [2609, 4690, 4694, 4700, 4709], 'vague_period_frequency_value_recovery': [6180, 7409]}`

## One-Family-Off Rerun Status

These are true one-family-off mechanics replays over the saved validation750 ClinicalAssessment/CandidateSet artifacts. They use named projection/render ablation switches and are compared against the clean candidate-trace V6 route baseline, not the provenance-expanded route.

| Family | Status | Disabled switch | Rendered delta | Newly null | W->C | C->W |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `current_summary_rate_priority` | `executed_one_family_off_replay` | `project_current_summary_rate_priority` | `0` | `0` | `0` | `0` |
| `major_recent_relapse_over_background_frequency` | `executed_one_family_off_replay` | `project_major_recent_relapse_over_background_frequency` | `0` | `0` | `0` | `0` |
| `previous_active_month_over_current_month_zero` | `executed_one_family_off_replay` | `project_previous_active_month_over_current_month_zero` | `0` | `0` | `0` | `0` |
| `seizure_free_duration_date_instrumentation` | `executed_one_family_off_replay` | `normalize_seizure_free_duration_date_instrumentation` | `-41` | `41` | `0` | `0` |

## Provenance Sidecars

| Surface or family | Rows with sidecar |
| --- | ---: |
| `clinical_policy_rows_with_sidecar` | `39` |
| `clinical_policy_rows_without_sidecar` | `17` |
| `pure_non_provenance_target_rows_with_sidecar` | `39` |
| `pure_non_provenance_target_rows_without_sidecar` | `17` |
| `provenance_only_rows` | `220` |

Family-level clinical/policy sidecars:

| Family | Rows with sidecar |
| --- | ---: |
| `cluster_axis_ambiguity` | `6` |
| `conditional_only_trigger` | `1` |
| `mixed_window_or_vague_addition` | `28` |
| `relative_only_trend` | `1` |
| `seizure_free_proxy_evidence_overreach` | `1` |
| `unresolved_cluster_cadence_with_per_cluster_burden` | `2` |

## Audit-Only V5->V6 Counts

These counts are saved for report accounting only. They are not included in verifier-visible input packets.

| Family | W->C | C->W | Null->C | Null->W |
| --- | ---: | ---: | ---: | ---: |
| `cluster_axis_ambiguity` | `0` | `0` | `0` | `0` |
| `conditional_only_trigger` | `0` | `0` | `0` | `0` |
| `cyclic_window_without_event_count` | `0` | `0` | `0` | `0` |
| `mixed_window_or_vague_addition` | `0` | `0` | `0` | `0` |
| `relative_only_trend` | `0` | `0` | `0` | `0` |
| `rendered_label_supported_but_policy_sensitive` | `0` | `0` | `0` | `0` |
| `seizure_free_proxy_evidence_overreach` | `0` | `0` | `0` | `0` |
| `selected_evidence_missing_exact_trace` | `0` | `0` | `0` | `0` |
| `selected_source_id_invalid` | `0` | `0` | `0` | `0` |
| `unresolved_cluster_cadence_with_per_cluster_burden` | `0` | `0` | `0` | `0` |

## Recovery Families

| Family | Stage | Status | Recovered | Newly routed | Remaining null | Provenance validity | Audit W->C | Audit C->W | Pending isolated ablation |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| `selected_evidence_frequency_value_recovery` | `normalize` | `ported_v6` | `5` | `0` | `pending` | - | `pending` | `pending` | - |
| `vague_period_frequency_value_recovery` | `normalize` | `ported_v6` | `2` | `0` | `pending` | - | `pending` | `pending` | - |
| `diary_date_list_frequency_recovery` | `normalize` | `ported_v6` | `0` | `0` | `pending` | - | `pending` | `pending` | - |
| `seizure_free_duration_date_instrumentation` | `normalize` | `ported_v6` | `pending` | `0` | `121` | - | `pending` | `pending` | - |
| `current_summary_rate_priority` | `project` | `ported_v6` | `pending` | `0` | `pending` | - | `pending` | `pending` | - |
| `previous_active_month_over_current_month_zero` | `project` | `ported_v6` | `pending` | `0` | `pending` | - | `pending` | `pending` | - |
| `major_recent_relapse_over_background_frequency` | `project` | `ported_v6` | `pending` | `0` | `pending` | - | `pending` | `pending` | - |

## Clinical/Policy Route Families

| Family | Stage | Status | Recovered | Newly routed | Remaining null | Provenance validity | Audit W->C | Audit C->W | Pending isolated ablation |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| `relative_only_trend` | `verify` | `ported_route_family_v6` | `0` | `2` | `2` | exact=`1` source-valid=`1` invalid/unresolved=`1` | `0` | `0` | attach row-level sidecar and audit-only changed-row accounting |
| `conditional_only_trigger` | `verify` | `ported_route_family_v6` | `0` | `1` | `1` | exact=`0` source-valid=`0` invalid/unresolved=`1` | `0` | `0` | attach row-level sidecar and audit-only changed-row accounting |
| `denominator_window_mismatch` | `verify` | `ported_route_family_v6` | `0` | `0` | `0` | - | `0` | `0` | confirm whether this family is absent on the current saved surface or only appears in a separate rendered-policy pass |
| `unresolved_cluster_cadence_with_per_cluster_burden` | `verify` | `ported_route_contract_v6` | `0` | `4` | `0` | exact=`2` source-valid=`2` invalid/unresolved=`2` | `0` | `0` | attach row-level sidecar and audit-only ownership movement |

## Provenance Route Appendix

| Family | Stage | Status | Recovered | Newly routed | Remaining null | Provenance validity | Audit W->C | Audit C->W | Pending isolated ablation |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| `selected_evidence_missing_exact_trace` | `verify` | `ported_route_family_v6` | `0` | `215` | `80` | exact=`0` source-valid=`0` invalid/unresolved=`250` | `0` | `0` | split mixed versus provenance-only rows directly from the saved artifacts |
| `selected_source_id_invalid` | `verify` | `ported_route_family_v6` | `0` | `9` | `5` | exact=`9` source-valid=`0` invalid/unresolved=`9` | `0` | `0` | split the 26 provenance-only unresolved-source rows from the single mixed row |

## Next Fill-In Pass

1. repair the remaining candidate-trace selected_source_id_invalid tail without merging it into the verifier main table
2. run the first verifier experiment only on the clean 29-row ambiguity core and appendices
