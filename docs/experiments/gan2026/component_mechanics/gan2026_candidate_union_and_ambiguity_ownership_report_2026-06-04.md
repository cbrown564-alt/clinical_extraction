# Gan 2026 Candidate Union And Ambiguity Ownership Report

Date: 2026-06-04

Status: architecture research report and next-experiment framing. This is a
validation-development planning artifact, not a holdout-transfer,
production, or benchmark-comparable claim.

## Question

RQ1-RQ4 have narrowed the architecture question. The remaining issue is no
longer whether deterministic or LLM components are globally better. The open
question is where each component should be allowed to contribute:

1. Should deterministic and LLM candidate generation run independently, with a
   later component selecting from the union, or should deterministic candidates
   be given as context to a first LLM call that also selects the final state?
2. Should ambiguity be handled inside the LLM clinical state representation, or
   should a later LLM reviewer/verifier decide whether the state is too
   uncertain or ambiguous?

## Prior Evidence

RQ1 showed that broad LLM candidate generation is unsafe as a replacement, but
useful as a selective proposer for boundary, uncertainty, seizure-free,
conditional, and competing-state candidates. The deterministic/state-graph
candidate substrate remains the broad recall and safety-floor component.

RQ2 showed that LLMs are strong evidence locators but unsafe broad clinical
selectors. Exact evidence frequently exists before the system has the typed
state needed to decide currentness, denominator, cluster axis, seizure-free
duration, or uncertainty.

RQ3 showed that a rich selected-state schema can carry clinically meaningful
facts into structured fields. The model often overuses broad categories such as
`state_kind=frequency`, but the nested fields can preserve conditionality,
currentness, ambiguity, cluster burden, denominator, seizure-free blockers, and
competing-state information.

RQ4 showed that projection succeeds only when narrow, gated, exact-evidence
backed, and metadata-explicit. Broad graph projection and unconstrained LLM
label projection are negative results.

## Candidate Architecture Decision

The preferred next architecture is parallel candidate proposal followed by a
gated union and selected-state reasoning:

```text
clinical note
  -> deterministic candidate generator
  -> LLM selective boundary/ambiguity candidate proposer
  -> union + evidence/metadata/burden gates
  -> rich selected-state reasoner or selector
  -> deterministic projection policy
```

This is preferred over placing deterministic candidates only inside the first
LLM prompt as context. A single prompt that receives deterministic candidates
and emits a final determination would collapse several component questions into
one opaque step:

- whether the LLM discovered a missing candidate;
- whether it copied or was anchored by a deterministic candidate;
- whether it selected the right clinical fact from the candidate set;
- whether final-label projection or rendering caused the success or failure.

Keeping deterministic and LLM candidate generation as separate materialized
surfaces preserves attribution. It also allows the project to measure candidate
recall, exact evidence, candidate burden, metadata completeness, and
downstream regression risk before any final-label claim.

The LLM candidate proposer should not be asked for broad replacement
candidates. Its remit should be selective:

- conditional-only seizure states;
- uncertainty and unknown-boundary states;
- seizure-free claims with blockers or competing evidence;
- competing semiologies;
- diary/log states where a count or window may be implicit;
- vague rate phrases that need projection policy rather than direct rendering.

## Candidate Union Experiment

The next candidate experiment should materialize three candidate surfaces:

- `deterministic_candidates`: the frozen broad substrate and safety floor;
- `llm_boundary_candidate_proposals`: selective LLM candidates for named
  boundary and ambiguity families;
- `union_verified_candidates`: the gated union after exact-evidence,
  source-id, metadata, and burden checks.

Primary metrics:

- gold-state candidate recall;
- recall rescue over deterministic candidates;
- exact evidence rate;
- valid source-id rate;
- candidate count and false-positive burden;
- metadata completeness for currentness, assertion/certainty, denominator,
  cluster burden, seizure-free duration, and ambiguity;
- downstream selected-state W->C and C->W accounting under a deterministic
  safety floor.

Decision rule:

The union is useful only if it improves representability of hard states without
unacceptable candidate burden or deterministic-correct regressions. Aggregate
validation F1 should remain secondary.

## Ambiguity Ownership Decision

The preferred first design is to embed ambiguity estimation inside the rich
selected state, then let deterministic policy consume it:

```text
LLM rich selected state
  -> selected evidence
  -> currentness
  -> assertion and certainty
  -> competing hypotheses
  -> ambiguity flags
  -> reasons not directly renderable

deterministic policy
  -> render
  -> abstain
  -> choose unknown
  -> route to review
```

This follows the strongest RQ3 result: the LLM is useful as a typed fact
carrier, especially when it exposes ambiguity and boundary facts that a
deterministic projection policy can inspect. It also preserves the RQ4 lesson
that final benchmark-facing decisions should be gated and accountable rather
than unconstrained LLM label choices.

A post-state LLM reviewer/verifier is plausible, but should not be the first
broad architecture. A reviewer introduces a second prediction-bearing model
component after the selected state, so it needs its own attribution, evidence,
and regression accounting. Used broadly, it risks recreating the unsafe
unconstrained LLM selection pattern that RQ2 and RQ4 rejected.

The safer backup role is selective review:

- run deterministic consistency checks over the rich selected state;
- flag suspicious states such as `state_kind=frequency` plus exclusive
  conditionality, unresolved cluster cadence, seizure-free blockers, competing
  current rates, missing denominator/window, or vague trend without an absolute
  count;
- send only those predeclared suspicious slices to an LLM verifier;
- require exact evidence, changed-row W->C/C->W accounting, and no silent
  override of deterministic policy.

## Ambiguity Experiment

The next ambiguity experiment should compare:

1. embedded ambiguity fields consumed by deterministic policy;
2. deterministic suspicious-state checks plus abstention/review routing;
3. a selective LLM verifier only on predeclared suspicious-state slices.

Primary metrics:

- ambiguity-field completeness;
- suspicious-state detection rate;
- correct `unknown` or abstention decisions;
- W->C and C->W changes versus deterministic policy;
- exact evidence/source-id preservation;
- hidden-family performance for unknown boundaries, seizure-free blockers,
  competing semiologies, cluster burden, diary/log aggregation, and
  current-vs-historical conflicts.

Decision rule:

Prefer embedded ambiguity plus deterministic policy unless the selective LLM
verifier shows high-precision W->C gains with no deterministic-correct
regressions on a predeclared slice.

## Recommended Path Forward

The best current pathway is:

1. Preserve deterministic/state-graph candidates as the broad substrate and
   safety floor.
2. Add a selective LLM boundary-candidate proposer as a separate materialized
   component.
3. Build a gated candidate union with evidence, source-id, metadata, and burden
   checks.
4. Feed the union into the rich selected-state surface.
5. Keep ambiguity fields inside the selected state and let deterministic
   policy decide render, unknown, abstain, or review.
6. Add optional LLM verification only for predeclared suspicious-state slices
   after deterministic consistency checks identify them.

## Backup Paths

- Use deterministic candidates only plus LLM evidence/location sidecars if the
  candidate union creates too much burden.
- Keep the LLM boundary proposer but route its outputs to human-review or
  abstention instead of final-label projection.
- Use an LLM reviewer only as an audit layer for suspicious selected states,
  with no automatic override.
- Fall back to ACD-style deterministic projection policies for ambiguity
  families where LLM verifier precision is not clean.
- Treat the whole candidate-union/verifier surface as diagnostic until a frozen
  predeclared validation or holdout-facing audit is complete.

## Claim Boundary

This report authorizes narrow validation-development experiments only. It does
not authorize holdout row inspection, benchmark-comparable claims, scorer/gold
policy changes, or whole-pipeline promotion.
