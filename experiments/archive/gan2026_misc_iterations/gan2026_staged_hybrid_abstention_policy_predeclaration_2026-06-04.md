# Gan 2026 Staged-Hybrid Abstention Policy Predeclaration

Validation-development predeclaration only. This artifact freezes the next gold-blinded abstention-pressure policy work and does not change prediction-bearing behavior, prompts, scorer policy, gold labels, locked-test behavior, verifier use, or benchmark-comparable claims.

## Pressure Surface

Source pressure rows: 34

| Lane | Rows |
| --- | ---: |
| `anchor_policy_needed` | 2 |
| `date_policy_needed` | 8 |
| `keep_nonprediction` | 9 |
| `trigger_release_candidate` | 2 |
| `trigger_sentinel_boundary_review` | 13 |

## Gold-Blinded Release Criteria

### trigger_context_release_rule_v0

Portability: `seizure_frequency`

Decision: A trigger-context row may become prediction-bearing only when the candidate label is non-sentinel and the evidence supports a stable current seizure-frequency answer without relying on gold labels.

Criteria:

- Input lane is trigger_release_candidate.
- Candidate label is not unknown or no seizure frequency reference.
- Selected evidence contains a seizure/event target and an explicit rate, count, or window.
- Trigger wording is contextual, not exclusive trigger-only wording.
- Selected evidence and source ids remain exact and auditable.
- Development correctness is reported after routing and is never an input.

### last_event_date_policy_v0

Portability: `seizure_frequency`

Decision: Last-event rows stay human_review until date instrumentation can derive a stable seizure-free interval from explicit dates and a known note date without contradictory current events.

Criteria:

- Input lane is date_policy_needed.
- Automatic release requires explicit last-event date or duration.
- Automatic release requires a known note or reference date.
- The derived interval must be represented as an auditable intermediate field.
- Rows with conflicting current events, settled recent events, or unclear event target stay human_review.
- No last-event row becomes prediction-bearing in this predeclaration.

## Non-Release Lanes

| Lane | Decision |
| --- | --- |
| `trigger_sentinel_boundary_review` | Do not release automatically. Review whether an explicit unknown-boundary rule should predict unknown or keep abstain. |
| `anchor_policy_needed` | Keep abstain until stable denominator and anchor extraction are available before routing. |
| `keep_nonprediction` | Keep non-prediction under the current boundary policy. |

## Candidate Behavior Changes

| Candidate type | Rows |
| --- | ---: |
| direct trigger release candidates | 2 |
| last event automatic release candidates | 0 |

## Next Step

Implement and test the trigger-context release rule against the pressure lane, then add date instrumentation before any last-event automatic release.

## Artifact

- Summary JSON: `experiments/gan2026_staged_hybrid_abstention_policy_predeclaration_2026-06-04.json`
