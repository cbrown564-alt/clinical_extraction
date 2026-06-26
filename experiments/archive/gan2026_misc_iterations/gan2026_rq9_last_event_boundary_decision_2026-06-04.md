# Gan 2026 RQ9 Last-Event Boundary Decision

This is a no-call validation-development decision over the remaining last-event human-review rows in the v3 RQ9 selective-action router.

## Decision

Keep last-event rows as human-review boundaries. Do not promote a v4 date-window projection policy for this slice.

## Rationale

Do not implement a v4 date-window projection policy for this slice. The eight last-event rows are heterogeneous: unknown-convention seizure-free projections, already-unknown last-event rows, and recent frequency-selection failures. A single date-window rule would either predict development-wrong seizure-free labels or fail to address the frequency-selection rows.

## Claim Boundary

Validation-development decision over v3 last-event human-review rows. This artifact does not change scorer, gold, router, prompt, projection, locked-test, or benchmark-comparable policy.

## Artifacts

- Source router JSONL: `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl`
- Row decision JSONL: `experiments/gan2026_rq9_last_event_boundary_decision_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_rq9_last_event_boundary_decision_2026-06-04.json`

## Metrics

| Metric | Value |
| --- | ---: |
| rows | 8 |
| keep human review rows | 8 |
| date policy ready rows | 0 |
| development safe if predicted rows | 2 |
| development unsafe if predicted rows | 6 |

## Failure Modes

| Failure mode | Rows |
| --- | ---: |
| `recent_event_frequency_selection_boundary` | 2 |
| `unknown_convention_blocks_seizure_free_projection` | 4 |
| `unresolved_last_event_unknown_boundary` | 2 |

## Rows

| Row | Failure mode | Candidate label | Dev safe if predicted | Evidence |
| ---: | --- | --- | --- | --- |
| 11216 | `unknown_convention_blocks_seizure_free_projection` | `seizure free for 4 month` | no | `Last seizure on 25 December 2023. This episode was described as a generalised convulsion upon w...` |
| 11254 | `unknown_convention_blocks_seizure_free_projection` | `seizure free for multiple year` | no | `no generalised tonic–clonic seizures reported` |
| 11259 | `unknown_convention_blocks_seizure_free_projection` | `seizure free for multiple year` | no | `no clearly documented events since` |
| 11262 | `unresolved_last_event_unknown_boundary` | `unknown` | yes | `Last seizure` |
| 11272 | `unknown_convention_blocks_seizure_free_projection` | `seizure free for multiple year` | no | `She confirms that her last seizure on 20/Dec occurred in the early morning with a brief general...` |
| 11282 | `unresolved_last_event_unknown_boundary` | `unknown` | yes | `Last seizure` |
| 14810 | `recent_event_frequency_selection_boundary` | `12 per month` | no | `this month, but these have now settled. On 12 May the absence episodes` |
| 14821 | `recent_event_frequency_selection_boundary` | `17 per month` | no | `this month, but these have now settled. On 17 Jul the absence episodes` |
