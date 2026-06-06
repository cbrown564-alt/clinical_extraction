# Gan 2026 Verification Route Mechanics

Deterministic validation750 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v6_2026-06-06.jsonl`

## Summary

- Rows: 750
- Routed rows: 276
- Unrouted rows: 474

## Route Families

- `cluster_axis_ambiguity`: 13
- `conditional_only_trigger`: 1
- `cyclic_window_without_event_count`: 5
- `mixed_window_or_vague_addition`: 29
- `relative_only_trend`: 2
- `rendered_label_supported_but_policy_sensitive`: 1
- `seizure_free_proxy_evidence_overreach`: 1
- `selected_evidence_missing_exact_trace`: 250
- `selected_source_id_invalid`: 9
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

## Routed Score Statuses

- `not_scored_null_rendered_label`: 99
- `scored`: 177

## Routed Rows

- 10: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 79: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 187: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 278: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1223: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1281: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1317: selected_evidence_missing_exact_trace, unresolved_cluster_cadence_with_per_cluster_burden; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact; cluster burden is rendered but cadence or cluster axis remains unresolved
- 1357: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1486: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1573: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1694: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1695: selected_evidence_missing_exact_trace; score `not_scored_null_rendered_label`; purist `None`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 1706: selected_evidence_missing_exact_trace, cluster_axis_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: selected evidence is not an exact carried trace for the chosen primary fact; cluster projection has unparsed or incomplete cluster-axis values
- 1880: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 2114: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 2354: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 2369: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 2932: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 2992: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 3242: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 3281: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 3297: selected_evidence_missing_exact_trace; score `scored`; purist `True`; reasons: selected evidence is not an exact carried trace for the chosen primary fact
- 3356: selected_evidence_missing_exact_trace, conditional_only_trigger; score `not_scored_null_rendered_label`; purist `None`; reasons: selected evidence is not an exact carried trace for the chosen primary fact; frequency statement is conditioned on a trigger without a stable baseline rate
- 3468: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3469: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
