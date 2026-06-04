# Gan 2026 Selective Verifier C->W Regression Adjudication

Validation-development adjudication of the five `gan2026_selective_verifier_v0`
rows where the live verifier changed the routing policy from Purist-correct to
Purist-wrong. This is not a locked-test inspection and does not authorize
prediction-bearing verifier use.

## Inputs

- Live verifier run:
  `experiments/gan2026_selective_verifier_live_gpt41mini_2026-06-04.jsonl`
- Frozen predeclaration:
  `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl`
- Routing comparator:
  `experiments/gan2026_suspicious_selected_state_routing_2026-06-04.jsonl`
- Selected-state union replay:
  `experiments/gan2026_selected_state_union_replay_v3_2026-06-04.jsonl`
- RQ10 ambiguity audit:
  `experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.jsonl`

## Decision

Reject `gan2026_selective_verifier_v0` as a prediction-bearing policy. The
five C->W rows are real safety failures of the verifier action policy: it
trusted a plausible selected state when the routing policy's conservative
`route_unknown` action was the safer scored outcome. Four rows had exact
verifier evidence quotes, so exact quotation alone is not a sufficient veto
release gate. Row `15193` also failed the changed-row evidence gate because one
verifier quote came from the supplied competing-hypothesis text rather than the
source-selected evidence.

## Regression Table

| Row | Gold | Routing label | Verifier label | Evidence exact | Primary failure | Adjudication |
| ---: | --- | --- | --- | --- | --- | --- |
| 2080 | `multiple per month` | `unknown` | `1 cluster per month, 2 per cluster` | yes | Cluster cadence overfit plus count ambiguity | Verifier should not render cluster syntax from "a few events" / "a couple of significant turns and several brief spells"; route remains conservative. |
| 5534 | `1 per multiple month` | `unknown` | `1 per 2 week` | yes | Last-event recency treated as rate denominator | The note says a single event occurred a fortnight ago and was the first in several months; RQ10 classifies the row as `underdetermined_note`. |
| 6209 | `multiple per day` | `unknown` | `2 to 3 per day` | yes | Benchmark convention and unresolved daily multiplicity | The evidence supports daily brief events but not an exact count per day; RQ10 classifies the row as `benchmark_convention_dominated`. |
| 7168 | `unknown` | `unknown` | `1 cluster per year, 2 per cluster` | yes | Competing semiology suppression | The verifier ignored day-to-day myoclonic jerks and rendered the lower-frequency tonic-clonic count; RQ10 classifies the row as `underdetermined_note`. |
| 15193 | `multiple per 13 month` | `unknown` | `0 per 9 to 10 month` | no | Seizure-free overreach across seizure types | The verifier chose the generalized-seizure no-event state despite ongoing absences; one evidence quote was not an exact source quote. |

## Mechanism Findings

The verifier did not create new clinical evidence. It mainly removed the
routing policy's veto in rows that were predeclared suspicious:

- `frequency_with_count_blocking_ambiguity`: rows `2080`, `5534`, `6209`,
  `15193`.
- `unresolved_cluster_cadence_with_per_cluster_burden`: rows `2080`, `7168`.

The dominant failure mode is not parsing. It is action calibration: the model
can explain why a selected state is plausible, but it does not reliably decide
when plausible evidence is still too ambiguous to render as a final label under
Gan scoring conventions.

## Design Consequences

Any verifier redesign should be veto-first rather than render-first:

- Treat exact evidence as necessary but not sufficient.
- Force `render_as_unknown` or `abstain_review` when the selected state carries
  count-blocking ambiguity, unresolved cluster cadence, or seizure-free
  boundary conflict.
- Require the verifier to account for all listed competing hypotheses before
  `render_as_selected_state`.
- Disallow evidence quotes copied from competing-hypothesis summaries when
  evaluating changed-row evidence exactness.
- Preserve `route_unknown` unless the verifier can name a scorer-compatible
  label and explain why every predeclared ambiguity flag is non-blocking.

## Claim Boundary

On validation development under `gan2026_split_v1`,
`gan2026_selective_verifier_v0` changed 23 scorable routing decisions, with 6
W->C and 5 C->W. The C->W adjudication supports rejecting v0 for
prediction-bearing use. It supports a narrower future experiment on
veto-calibrated ambiguity resolution; it does not support verifier promotion,
whole-pipeline promotion, locked-test use, or benchmark-comparable language.
