# Gan 2026 Verification Route Mechanics

Deterministic validation250 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation250_verification_route_v5.jsonl`
- Summary JSON: `experiments\gan2026_validation250_verification_route_v5.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_score_validation250_v5.jsonl`

## Summary

- Rows: 250
- Routed rows: 5
- Unrouted rows: 245

## Route Families

- `cyclic_window_without_event_count`: 3
- `medication_cadence_ambiguity`: 1
- `multiple_current_primary_facts`: 1

## Routed Score Statuses

- `not_scored_null_rendered_label`: 4
- `scored`: 1

## Routed Rows

- 3468: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3469: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3493: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3534: multiple_current_primary_facts; score `scored`; purist `False`; reasons: multiple primary candidate ids are present outside an additive or cluster-axis policy
- 5476: medication_cadence_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cadence evidence may describe medication or rescue use rather than events
