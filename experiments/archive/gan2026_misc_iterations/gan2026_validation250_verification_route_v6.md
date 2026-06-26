# Gan 2026 Verification Route Mechanics

Deterministic validation250 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation250_verification_route_v6.jsonl`
- Summary JSON: `experiments\gan2026_validation250_verification_route_v6.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_score_validation250_v6.jsonl`

## Summary

- Rows: 250
- Routed rows: 5
- Unrouted rows: 245

## Route Families

- `cyclic_window_without_event_count`: 3
- `medication_cadence_ambiguity`: 1
- `seizure_free_proxy_evidence_overreach`: 1

## Routed Score Statuses

- `not_scored_null_rendered_label`: 5

## Routed Rows

- 3468: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3469: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3493: cyclic_window_without_event_count; score `not_scored_null_rendered_label`; purist `None`; reasons: cyclic vulnerability window is present without event count or burden
- 3534: seizure_free_proxy_evidence_overreach; score `not_scored_null_rendered_label`; purist `None`; reasons: seizure-free projection is based on proxy or conditional evidence
- 5476: medication_cadence_ambiguity; score `not_scored_null_rendered_label`; purist `None`; reasons: cadence evidence may describe medication or rescue use rather than events
