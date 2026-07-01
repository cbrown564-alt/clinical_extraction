> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 Null Action Taxonomy V6

Date: 2026-06-06

Scope: define an action-oriented taxonomy for the 51 null rows in the
`context_repair_v6` verifier-candidate surface described in
``.

This is validation-development mechanics work only. It does not authorize
locked-test inspection, benchmark-comparable language, or LLM-verifier
promotion.

## Goal

The 51 null clinical/policy rows should not all be treated as one kind of
failure.

For the reset architecture, the useful action taxonomy is:

1. `clinically_unknown`
2. `abstain`
3. `human_review`
4. `missing_upstream_policy_or_parser`
5. `verifier_eligible_ambiguity`

This note assigns the current V6 null surface to those buckets.

## Top-Line Split

The 51 null rows distribute as:

- `clinically_unknown`: `0`
- `abstain`: `4`
- `human_review`: `0`
- `missing_upstream_policy_or_parser`: `18`
- `verifier_eligible_ambiguity`: `29`

Bottom line:

- the current null surface is dominated by ambiguity and contract debt, not by
  clean "unknown" statements
- no row in this 51-row set currently demands a separate human-review bucket as
  the primary reset action

## Bucket Definitions

### 1. `clinically_unknown`

Definition:

- the note supports an explicit unknown-like frequency state
- rendering `unknown` would be semantically owned and not just a fallback for
  missing policy

V6 assignment:

- `0` rows

Interpretation:

- this null surface is not a pile of notes saying "frequency unknown"
- the rows generally contain some burden or timing content, but that content is
  incomplete, mixed, conditional, or policy-sensitive

### 2. `abstain`

Definition:

- evidence is real but does not support a safe scorer-facing burden label
- the row is not mainly a parser gap or missing benchmark convention
- verifier/action policy should prefer "do not affirm a frequency label"

V6 assignment:

- `4` rows

Families:

- `relative_only_trend`: `2`
- `conditional_only_trigger`: `1`
- `seizure_free_proxy_evidence_overreach`: `1`

Rows:

- `3356`
- `3507`
- `3512`
- `3534`

Rationale:

- `relative_only_trend` rows report increase or decrease without a current
  baseline
- `conditional_only_trigger` reports seizures only under a trigger condition,
  but without a stable burden denominator
- `seizure_free_proxy_evidence_overreach` names a proxy outcome that should not
  be upgraded to seizure freedom

These are best treated as true abstention cases, not hidden invitations to
recover a label.

### 3. `human_review`

Definition:

- evidence is potentially clinically consequential but the current reset
  contracts cannot safely decide between plausible actions
- escalation to a human would add value beyond abstain plus routing

V6 assignment:

- `0` rows

Interpretation:

- the current null surface does not yet justify a distinct human-review-first
  bucket
- the reset route families here are still better described as ambiguity or
  missing policy

This does not mean human review is never needed in the broader pipeline. It
means the present 51-row null surface does not naturally split that way.

### 4. `missing_upstream_policy_or_parser`

Definition:

- the note contains structured timing or cluster burden content
- the reset currently lacks an owned contract to project it safely
- the blocker is missing deterministic policy representation, not first-pass
  verifier judgment

V6 assignment:

- `18` rows

Families:

- `cluster_axis_ambiguity`: `13`
- `cyclic_window_without_event_count`: `5`

Rows:

- `1706`
- `3468`
- `3469`
- `3482`
- `3493`
- `6501`
- `9879`
- `9937`
- `10434`
- `10509`
- `10542`
- `10578`
- `10630`
- `15242`
- `15262`
- `16757`
- `16839`
- `16907`

Rationale:

- the cluster-family pass already shows these are mostly contract-boundary
  rows, not narrow parser misses
- cyclic-window rows name timing windows or triggers without an owned event
  count convention
- cluster-axis rows often express burst size, vague cluster-day cadence, or
  dated bursts without a stable recurrence denominator

Recommended treatment:

- keep these rows visible in verifier reports
- do not use them as the main success criterion for the first verifier
- track them as upstream policy debt unless a future contract explicitly
  promotes them

### 5. `verifier_eligible_ambiguity`

Definition:

- the note contains more than one burden signal, window, or semiology
- projection refusal is appropriate, but the row still represents a meaningful
  action-choice surface for verification or adjudication
- the problem is not simply "we failed to parse"

V6 assignment:

- `29` rows

Family:

- `mixed_window_or_vague_addition`: `29`

Rows:

- `5551`
- `5791`
- `6209`
- `6889`
- `12127`
- `12192`
- `12236`
- `12366`
- `12378`
- `12403`
- `12422`
- `12456`
- `12460`
- `12484`
- `12502`
- `12506`
- `12537`
- `12548`
- `12551`
- `12556`
- `12562`
- `12573`
- `12584`
- `12641`
- `12676`
- `12679`
- `12749`
- `12751`
- `12823`

Rationale:

- these rows mix windows, event types, or summary levels that the reset should
  not collapse automatically
- many rows contain individually parseable burdens, but no deterministic rule
  yet owns which burden should control
- this is the cleanest first verifier/action-policy surface in the null set

Examples:

- `6209`: `daily brief events and 2-3 longer episodes per month`
- `12366`: `simple partial seizures 4 times per day and tonic-clonic seizures 2 times per month`
- `12537`: `up to three generalised tonic-clonic seizures per week, daily drop attacks, and focal impaired-awareness seizures every four to six weeks`

## Practical Consequences

### What the first verifier should mainly target

The strongest first verifier/action-policy null surface is:

- `29` rows of `verifier_eligible_ambiguity`

These rows have the most plausible value for action adjudication because they
already contain multiple competing burden signals rather than only contract
gaps.

### What should not be mistaken for verifier failure

The `18` rows in `missing_upstream_policy_or_parser` are important, but they
are not the best first verifier benchmark surface.

Using them as the main success criterion would blur two different questions:

1. should a verifier adjudicate competing burden statements?
2. or does the deterministic pipeline first need a better cluster/cyclic
   contract?

### What counts as a real abstention slice

The `4` abstain rows are small but semantically important.

They define clear negative boundaries:

- trend without baseline
- trigger-only burden without denominator
- seizure-free proxy evidence that should not be upgraded

These are useful prompt exemplars because they show where the right action is
to decline a frequency label rather than manufacture one.

## Recommended Reporting Split

For the first verifier planning/reporting loop, use this operational layout:

1. `verifier_eligible_ambiguity`
   main null action set
2. `missing_upstream_policy_or_parser`
   upstream debt appendix
3. `abstain`
   negative-boundary appendix
4. rendered policy-sensitive rows
   separate appendix from
   ``

Provenance-sidecar decision:

- on the 39 mixed clinical/policy rows, provenance sidecars should remain
  visible to the first verifier prompt
- they should be treated as supporting audit context rather than the main
  action bucket
- action evaluation should still be grouped by
  `verifier_eligible_ambiguity`, `missing_upstream_policy_or_parser`, and
  `abstain`

## Recommendation

Treat the null-render/action taxonomy as complete for `context_repair_v6`.

The next useful step is to predeclare the first verifier report layout now that
the provenance-sidecar policy is decided.
