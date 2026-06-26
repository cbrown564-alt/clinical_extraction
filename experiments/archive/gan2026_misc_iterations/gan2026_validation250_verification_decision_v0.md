# Gan 2026 VerificationDecision V0 Baseline

deterministic validation250 verification-action baseline over routed rows; no verifier model call, no manual annotation, no replacement label invention, and score context is audit-only

## Artifacts

- Decision JSONL: `experiments\gan2026_validation250_verification_decision_v0.jsonl`
- Summary JSON: `experiments\gan2026_validation250_verification_decision_v0.json`
- Route source: `experiments\gan2026_validation250_verification_route_v6.jsonl`

## Summary

- Input route rows: 250
- Input routed rows: 5
- Decision rows: 5

## Actions

- `abstain`: 4
- `human_review`: 1

## Route Families

- `cyclic_window_without_event_count`: 3
- `medication_cadence_ambiguity`: 1
- `seizure_free_proxy_evidence_overreach`: 1

## Decision Rows

- 3468: `abstain`; basis `route_family_policy`; families: cyclic_window_without_event_count; reason: cyclic vulnerability window lacks event count or burden for automated projection
- 3469: `abstain`; basis `route_family_policy`; families: cyclic_window_without_event_count; reason: cyclic vulnerability window lacks event count or burden for automated projection
- 3493: `abstain`; basis `route_family_policy`; families: cyclic_window_without_event_count; reason: cyclic vulnerability window lacks event count or burden for automated projection
- 3534: `abstain`; basis `route_family_policy`; families: seizure_free_proxy_evidence_overreach; reason: proxy-only seizure-free evidence has no safe automated replacement label
- 5476: `human_review`; basis `manual_review_required`; families: medication_cadence_ambiguity; reason: cadence may describe medication or rescue use rather than event occurrence
