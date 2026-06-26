# Gan 2026 Verification Route Mechanics

Deterministic validation250 verification-route mechanics only. Routes use predeclared clinical/projection risk predicates over structured projection/render fields; score fields are audit context only and no verifier action is emitted.

## Artifacts

- Route JSONL: `experiments\gan2026_validation250_verification_route_v0.jsonl`
- Summary JSON: `experiments\gan2026_validation250_verification_route_v0.json`
- Score source: `experiments\gan2026_clinical_assessment_projection_score_validation250_v0.jsonl`

## Summary

- Rows: 250
- Routed rows: 2
- Unrouted rows: 248

## Route Families

- `mixed_window_or_vague_addition`: 1
- `multiple_current_primary_facts`: 1

## Routed Score Statuses

- `not_scored_null_rendered_label`: 1
- `scored`: 1

## Routed Rows

- 744: mixed_window_or_vague_addition; score `not_scored_null_rendered_label`; purist `None`; reasons: additive assessment includes mixed-window, vague, or incomplete values
- 3534: multiple_current_primary_facts; score `scored`; purist `False`; reasons: multiple primary candidate ids are present outside an additive or cluster-axis policy
