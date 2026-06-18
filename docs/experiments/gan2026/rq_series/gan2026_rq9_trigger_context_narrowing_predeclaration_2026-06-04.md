# Gan 2026 RQ9 Trigger-Context Narrowing Predeclaration

This is a validation-development predeclaration for a future RQ9 selective-action
router revision. It narrows which trigger-context rows may stay
prediction-bearing after the conservative v2 router abstained on all
trigger-conditioned rows.

It does not change scorer policy, gold labels, deterministic extraction rules,
prompts, projection policy, locked-test behavior, or benchmark-comparable
claims.

## Decision

Do not release all trigger-conditioned v2 abstentions as predictions. The
abstention-pressure artifact shows that 26 trigger rows have non-sentinel
candidate labels, but only 17/26 are development-safe if predicted. A future v3
router may make a trigger-context row prediction-bearing only when a
gold-blinded rule can distinguish baseline/current rates with trigger context
from true trigger-only or unquantified evidence.

## Evidence Base

- V2 router:
  `experiments/gan2026_rq9_selective_action_router_v2_2026-06-04.*`
- Abstention pressure interpretation:
  `experiments/gan2026_rq9_abstention_pressure_v0_2026-06-04.*`
- Frozen RQ9 boundary policy:
  ``
- Selective-action evaluation contract:
  ``

## Candidate Surface

The rule applies only to v2 nonprediction rows with:

- `selective_action == abstain`
- `primary_reason == trigger_conditioned_frequency`
- a non-sentinel candidate label, meaning not `unknown` and not
  `no seizure frequency reference`

All other v2 nonprediction rows remain unchanged:

- missing-anchor rows stay `abstain`
- last-event rows stay `human_review` until a frozen date-window policy exists
- trigger rows with `unknown` or `no seizure frequency reference` stay abstain
  unless a later policy proves a stable prediction-bearing label

## Gold-Blinded Release Criteria

A candidate trigger-context row may become prediction-bearing only if all of the
following are true before development accounting is consulted:

1. The candidate final label is non-sentinel and scorable.
2. `unknown_gold_boundary` is absent from the pre-routing ambiguity reasons.
3. The selected evidence or router packet contains an explicit event target or
   frequency context, such as seizure, seizures, event, events, episode,
   episodes, cluster, clusters, convulsion, myoclonic, focal, absence, frequency,
   rate, or a clearly named seizure semiology.
4. The selected evidence supports a count/range plus denominator/window, or a
   seizure-free interval, without requiring an unstated anchor date.
5. Trigger language is contextual rather than exclusive. Wording such as
   "around", "often", "after", "following", or "during periods of" can be
   prediction-bearing when the baseline/current count is still explicit.
   Wording such as "only when", "only with", "outside this window no events",
   or a missing baseline rate remains abstention.

This is a `seizure_frequency` rule with clinical context sensitivity. It is not
a scorer change or benchmark-format repair.

## Required V3 Accounting

If implemented, v3 must report:

- coverage, selective accuracy, abstention rate, and human-review rate
- trigger-context release count
- trigger-context rows kept abstained
- development-safe and development-unsafe released trigger rows
- hidden-error rate
- row-level examples for released-safe, released-unsafe, and kept-abstained
  trigger rows

The v3 report must compare against v2 and must not use gold labels, human audit
classes, Purist correctness, or W/C fields as router inputs.

## Expected Direction

This predeclaration should reduce over-abstention without returning to broad
trigger release. Based on the v0 abstention-pressure artifact, a strict
gold-blinded rule should recover a subset of the 17 development-safe trigger
candidates while intentionally leaving ambiguous unknown-boundary and terse
context-poor rate fragments abstained.

## Claim Boundary

This predeclaration can support a validation-development v3 router experiment.
It does not authorize holdout use, final pipeline promotion, gold rewrites,
scorer changes, or benchmark-comparable language.
