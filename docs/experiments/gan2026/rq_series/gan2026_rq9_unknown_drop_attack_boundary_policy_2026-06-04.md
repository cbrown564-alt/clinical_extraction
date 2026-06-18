# Gan 2026 RQ9 Unknown And Drop-Attack Boundary Policy

This is a validation-development policy for the future RQ9 selective-action
router. It freezes how the router should treat `unknown`-boundary and
drop-attack cases before any new selective-action surface is scored.

It does not change Gan scorer policy, gold labels, deterministic rules, prompts,
projection policy, locked-test behavior, or benchmark-comparable claims.

## Decision

The selective-action router must not collapse every difficult case into
`unknown`. It must separate:

- predictable frequency or seizure-free rows;
- seizure-frequency evidence that is present but not convertible;
- event-type uncertainty that needs human review;
- benchmark-convention boundaries that need human review;
- true extraction failures that should remain visible for debugging.

`unknown` is allowed as a prediction only when the note clearly discusses
seizures or seizure-like events but does not provide a stable, convertible,
current/recent frequency or seizure-free interval. Drop attacks are allowed as
prediction-bearing frequency evidence only when the note frames them as current
epileptic seizure burden and gives a convertible count/window.

## Evidence Base

- Human Gold Audit report:
  ``
- RQ9 selective-action contract:
  ``
- RQ10 ambiguity answer:
  ``
- Suspicious selected-state routing answer:
  ``
- Validation ambiguity worklist:
  `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`

The human audit found `unknown` to be the main instability zone: 18 of 28
reviewed `unknown` gold-kind rows were human-noncorrect. The same audit showed
that drop attacks are context dependent: some are clearly current seizure
burden, while others are uncertain collapse/spell events or unquantified
since-anchor statements.

## Unknown Boundary Rules

Use these actions for rows where the candidate selected state or source evidence
is near the `unknown` boundary:

| Condition | Action | Primary reason |
| --- | --- | --- |
| Seizures or seizure-like events are discussed, but no current/recent frequency, count, denominator, or seizure-free interval is stated | `predict` `unknown` | `unknown_frequency_unquantified` |
| A vague count is present with no stable denominator, such as "several since discharge" or "multiple since ketogenic diet" when the anchor date/window is unavailable or clinically awkward | `abstain` | `missing_denominator_anchor` |
| Trigger-only evidence is present without a baseline rate, such as events only with sleep deprivation, missed meals, menstrual phase, or another condition | `abstain` | `trigger_conditioned_frequency` |
| Last-event-only evidence gives a date and "none since", but the router cannot determine whether the benchmark-facing answer should be `unknown` or a seizure-free interval | `human_review` | `last_event_boundary` |
| A count since a known date/window can be converted without assuming unstated currentness or denominator | `predict` frequency | `plain_predictable_frequency` |
| A plain seizure-free interval has an explicit last-event date or duration and no contradictory current events | `predict` seizure-free label | `plain_predictable_seizure_free` |
| The note has no usable seizure-frequency evidence at all | `predict` `no seizure frequency reference` | `plain_no_reference` |
| The selected state carries competing current frequency, seizure-free, or no-reference interpretations with no deterministic priority that is both clinical and benchmark-stable | `human_review` | `benchmark_convention_boundary` |

The router may emit `unknown` as a final prediction only for the first row in
the table. Other unknown-near cases should be explicitly abstained or reviewed
so coverage, over-abstention, and hidden-error metrics can distinguish them.

## Drop-Attack Rules

Use these actions when the evidence includes drop attacks, collapses, loss of
tone, falls, spells, or similar event-type language:

| Condition | Action | Primary reason |
| --- | --- | --- |
| The note frames drop attacks as part of established epilepsy or seizure burden and gives a current/recent convertible rate/window | `predict` frequency | `plain_predictable_frequency` |
| Drop attacks are the highest active burden among multiple current seizure semiologies and the rate/window is convertible | `predict` frequency | `plain_predictable_frequency` |
| The note gives drop attacks only as vague "several/multiple since X" with no stable denominator/window | `abstain` | `missing_denominator_anchor` |
| Drop attacks are described as collapses, loss of tone, non-injurious brief events, or events under investigation without clear seizure attribution | `human_review` | `drop_attack_boundary` |
| Drop attacks are trigger-only or condition-only without a stable baseline rate | `abstain` | `trigger_conditioned_frequency` |
| Drop attacks coexist with clearly quantified non-drop epileptic seizures and the target seizure burden is unclear | `human_review` | `competing_semiology_boundary` |
| The note says the events are non-epileptic, functional, syncopal, medication side effects, or otherwise not seizure burden | `predict` based on other seizure-frequency evidence, or `no seizure frequency reference` if none exists | `plain_predictable_frequency` or `plain_no_reference` |

This policy treats drop-attack handling as `clinical_epilepsy` plus
`seizure_frequency` logic. Any later benchmark-format conversion remains
separate and must not be described as model-selected clinical reasoning.

## Router Input Requirements

A router artifact using this policy must expose these fields before action
selection:

- candidate/event kind: frequency, seizure-free, last-event-only,
  unknown-frequency, no-reference, cluster, or non-seizure event
- event target: definite seizure, seizure-like event, drop attack, collapse,
  spell, non-epileptic event, or unknown target
- assertion status and currentness
- trigger or conditionality text
- count, range, denominator/window, and anchor text
- last-event date or seizure-free duration when available
- competing current semiologies and their rates
- evidence exactness and source ids when available

If these fields are unavailable, the row must be marked as insufficiently
instrumented in development accounting rather than silently predicted.

## Router Output Requirements

Each row must emit:

- one action: `predict`, `abstain`, `human_review`, or
  `extraction_error_analysis`
- one primary reason from the RQ9 selective-action contract
- final label only when action is `predict`
- exact selected evidence or `no_exact_evidence`
- boundary fields used to choose the action
- gold-blinded review packet for abstention/review rows
- development-only accounting fields kept outside router input

## Examples From The Audit

| Source row | Policy interpretation |
| --- | --- |
| 14040 | Multiple drop attacks since ketogenic diet, latest on a date, but unable to quantify frequency: `abstain` with `missing_denominator_anchor`; also flag `drop_attack_boundary` as secondary. |
| 14029 | Several drop attacks since ketogenic diet with brief-collapse phenotype and unclear burden: `human_review` with `drop_attack_boundary` unless implementation can prove a stable denominator. |
| 2513 | Two to three drop attacks in the last two weeks in established generalized epilepsy: `predict` frequency. |
| 12537 | Daily drop attacks coexist with less frequent GTC and focal impaired-awareness seizures: `predict` daily frequency because drop attacks are the highest current burden. |
| 11282 | Last seizure on a date, with none since: `human_review` with `last_event_boundary` unless the router can deterministically derive a supported seizure-free interval under a frozen date policy. |
| 3356, 6321, 7168 | Trigger-only frequency boundaries: `abstain` with `trigger_conditioned_frequency` unless a baseline rate is separately present. |

## Scoring And Claim Boundary

This policy is an RQ9 selective-action contract. It should be scored with
coverage, selective accuracy, abstention/review rates, over-abstention,
over-review, rescue value, hidden-error rate, and slices by reason/family.

It must not be used to rewrite gold labels, change Purist or Pragmatic mapping,
smooth parser failures, or claim benchmark comparability. If this policy later
becomes executable code, it should be tested as a router/action layer, not as an
evaluator change.

