# Gan 2026 Validation750 Verifier Action-Policy Decision V6

Date: 2026-06-06

Scope: decide the primary verifier action policy after comparing the first live
action-only verifier run against the forced-choice verifier run on the same
clean `56`-row V6 surface.

This is a protocol decision for validation-development only. It does not
authorize benchmark-comparable claims, locked-test inspection, or scorer-facing
replacement labels.

## Decision

The primary verifier policy for the reset thread is `action_only`.

Forced choice is retained as a diagnostic comparison artifact, not as the
primary verifier protocol.

## Why This Decision Fits The Reset Objective

The active reset objective is to make the pipeline stage-owned, evidence-traced,
inspectable, and ablatable before any holdout-facing or promotion work.

On that objective, the verifier should answer:

```text
Should the system affirm, reject, abstain, or escalate this routed case?
```

It should not yet answer:

```text
Which competing burden should replace the current interpretation?
```

Action-only preserves that boundary. Forced choice crosses it by selecting a
prediction-bearing candidate in exactly the cases where the reset surface is
still trying to expose unresolved ambiguity.

## Evidence From The Two Runs

### Action-only run

Source:
`docs/research/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.md`

Main points:

- `56/56` parseable outputs
- `56/56` contract-valid rows
- `27` non-abstain actions overall
- main ambiguity table:
  `1` affirm,
  `5` reject,
  `15` human_review,
  `8` abstain

Interpretation:

- The action-only protocol is operationally clean.
- It preserves explicit distinctions between contradiction, review debt, and
  unresolved policy/aggregation debt.

### Forced-choice run

Source:
`docs/research/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.md`

Main points:

- `40` affirm
- `11` human_review
- `5` reject
- `0` abstain
- only `8/56` agreement (`0.1429`) with the action-only baseline

Interpretation:

- Forced choice is much more aggressive.
- It collapses many ambiguous rows into a selected current burden.
- That behavior is diagnostically interesting, but it is not conservative
  enough for the first reset-owned verifier policy.

## Main-Table Read

On the real `29`-row ambiguity table, the action-only run and forced choice
agree on only `5` rows.

The disagreement is not random. Forced choice repeatedly promotes
highest-frequency or most-current-seeming candidates into equivalent `affirm`
actions on rows where the action-only read still sees one of these:

- mixed-window additive burden
- multiple active semiologies with no stable unifying policy
- seizure-free or no-events context that complicates but does not cleanly
  invalidate the burden
- incomplete normalization or incomplete projection semantics

That is exactly the surface where the reset protocol should keep ambiguity
visible instead of hiding it inside an early selection move.

## Research-Framing Read

This decision supports the paper-facing claims the repo is trying to protect:

- transparency:
  action-only exposes when the verifier can act and when it should not
- deterministic rules as controlled variables:
  it keeps unresolved selection debt visible for later policy and ablation work
- attribution discipline:
  the verifier is not yet allowed to silently replace the prediction-bearing
  interpretation
- saturated-surface discipline:
  this is a calibration/selective-action decision, not a broad "metric bump"
  chase

## Operational Policy

For the reset thread, the verifier should continue to emit only:

- `affirm`
- `reject`
- `abstain`
- `human_review`

It should not emit:

- replacement labels
- forced candidate selection as the primary protocol
- hidden scorer-facing resolution of clinically ambiguous burden competition

## What Forced Choice Is Still Good For

Forced choice remains useful as a diagnostic artifact:

1. it shows which rows tempt the model to over-select a dominant current burden
2. it identifies where the action-only prompt may need clearer anti-overreach
   instructions
3. it can help design later bounded experiments if the project explicitly asks
   whether a narrower adjudicator should select among already-vetted candidates

But none of that changes the current reset-stage verifier contract.

## Immediate Next Step

Use the `29`-row outcome taxonomy to tighten the action-only prompt:

1. require contradiction for `reject`
2. prevent "highest frequency wins" from masquerading as `affirm`
3. distinguish `human_review` from `abstain` more explicitly on mixed-window
   and mixed-semiology rows

## Next Iteration Scope Decision

The next verifier iteration should temporarily concentrate on the `29`-row main
ambiguity table, not the full clean `56`-row surface.

Reason:

- the `29` rows are the true action-boundary learning surface
- they are the only rows that directly pressure the
  `affirm`/`reject`/`human_review`/`abstain` boundary
- the remaining `27` appendix rows are still useful audit context, but they mix
  abstain exemplars, upstream-policy debt, and rendered policy-sensitive cases
  that would blur the first prompt-tightening read

Operational consequence:

- keep the full `56`-row packet as the saved broad comparison surface
- use the `29`-row main ambiguity table as the primary next prompt/policy
  iteration surface
- return to the full `56`-row surface after the action-boundary prompt is more
  stable

## Decision Summary

`action_only` remains the primary verifier action policy because it is:

- contract-clean
- conservative on the real ambiguity surface
- aligned with the reset architecture
- better matched to selective-action analysis than forced choice

Forced choice stays as a diagnostic comparison only.
