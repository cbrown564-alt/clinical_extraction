# Gan 2026 Architecture Assembly Readiness Decision

Date: 2026-06-04

Status: validation-development architecture decision. This is not a
holdout-transfer, production, or benchmark-comparable claim.

## Decision

Gan 2026 is ready for staged architecture assembly, but not for whole-pipeline
promotion or benchmark-facing evaluation.

The assembly target is:

```text
deterministic/state-graph substrate
  + selective LLM boundary candidate proposer
  + candidate-conditioned LLM evidence gate
  + rich selected-state fact carrier
  + deterministic consistency checks
  + gated deterministic projection/rendering
  + selective safety floor
  + abstain/review/monitoring policy
```

This supersedes the older broad LLM-first V1 hypothesis as the current
implementation direction. The older hypothesis remains useful historical
context, but the RQ1-RQ10 evidence now supports a staged hybrid with explicit
component ownership and regression gates.

## Why This Is Ready

The component answers now agree on the same boundaries:

- RQ1: LLM candidate generation is useful only as selective boundary,
  uncertainty, seizure-free, and competing-state proposal.
- RQ2: LLM evidence selection is reliable as source-grounded evidence location,
  not broad clinical selection.
- RQ3: rich selected state is the right fact carrier, but needs source-id
  instrumentation and consistency checks.
- RQ4: projection works only when narrow, gated, metadata-explicit, and
  exact-evidence backed.
- RQ5: deterministic rendering preserves fixed selected states; remaining
  errors are upstream state/projection problems.
- RQ6: reliable LLM value is exact-evidence, no-regression selective action
  behind a deterministic safety floor.
- RQ7: hidden-family readouts show which component should own which burden.
- RQ8: narrow extractive prompts are operationally preferable to deep schemas
  and all-in-one prompts.
- RQ9: ambiguous rows need bounded prediction, abstention, review, and
  monitoring.
- RQ10: residual hard rows mix true extraction failures, underdetermined notes,
  and benchmark-convention cases; they should not drive blind retuning.

## Implementable Now

These pieces are ready for implementation or integration under validation
development:

1. Materialized deterministic/state-graph substrate as broad candidate source
   and safety floor.
2. Selective boundary-candidate proposer for named ambiguity, unknown,
   seizure-free, competing-state, and boundary slices.
3. Candidate-conditioned evidence gate as the default LLM evidence primitive.
4. Rich selected-state schema as the fact carrier.
5. Deterministic consistency checks for suspicious selected-state combinations.
6. ACD-style deterministic projection/rendering policies for named families.
7. Selective safety-floor gate for label-changing action.
8. RQ9 abstain/review/monitoring actions for missing anchors, last-event
   boundaries, cluster/convention monitoring, and ambiguity residue.

## Not Ready

These remain diagnostic or blocked:

- broad LLM final-label replacement;
- broad state-graph projection replacement;
- all-in-one candidate/evidence/projection prompt bundling;
- `typed_operations_v0` or similarly deep schemas with duplicated decision
  ownership;
- source-id-free rich selected-state promotion;
- broad cluster/diary/denominator policy expansion without a predeclared gate;
- benchmark-comparable language;
- locked-test row-level tuning.

## Required Assembly Gates

An assembled candidate may move beyond diagnostic validation development only
if it produces a component evidence matrix with:

- one row per source row and component decision;
- source candidate provenance: deterministic, state graph, LLM boundary
  proposal, or union;
- selected evidence and source-id validity;
- rich selected-state trace fields;
- suspicious-state flags and action decision;
- projection policy id and ACD decision id when relevant;
- final label, safety-floor fallback status, and abstain/review/monitor action;
- W->C and C->W accounting against the deterministic comparator;
- hidden-family tags;
- first-failure owner for non-correct rows when available.

Minimum promotion gate:

- no silent semantic overrides after the rich selected state;
- changed rows all exact-evidence and source-id valid;
- no deterministic-correct regressions for any automatic label-changing gate;
- cluster/diary/denominator/convention families either explicitly gated or
  routed to review/monitoring;
- cost/latency telemetry recorded if the run is intended for paper-facing
  operational comparison.

## Architecture Boundary

Claim language for the assembled candidate should be:

```text
hybrid staged candidate/evidence/state architecture with deterministic
projection, safety-floor action, and abstention/review policy
```

Do not call it LLM-first. Deterministic candidates, state graph nodes,
projection policies, rendering, abstention rules, and the safety floor remain
prediction-bearing components.

## Holdout Boundary

No holdout-facing run is authorized by this decision. A holdout-facing audit
would need a separate frozen protocol that fixes:

- candidate version and code commit;
- model, prompt, schema, and max-token settings;
- split manifest and source artifact paths;
- deterministic projection/rendering and ACD policies;
- selective safety-floor policy;
- abstain/review/monitoring policy;
- component evidence matrix fields;
- permitted aggregate readouts;
- row-level inspection limits.

## Next Action

Implement the assembled validation-development candidate in the smallest
possible slice:

1. materialize source ids for rich selected-state rows;
2. add deterministic suspicious-state consistency checks;
3. replay the assembled policy on the existing hard-panel artifacts before any
   new live model calls;
4. only then predeclare a validation50 or validation hard-slice smoke if saved
   replay cannot answer the integration question.
