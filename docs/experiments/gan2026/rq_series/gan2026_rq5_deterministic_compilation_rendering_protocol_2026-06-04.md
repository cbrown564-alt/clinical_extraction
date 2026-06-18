# Gan 2026 RQ5 Deterministic Compilation/Rendering Protocol

Date: 2026-06-04

Scope: validation-development protocol for RQ5. This is a deterministic
compiler/rendering component question over fixed selected clinical states and
explicit ACD projection-policy decisions. It is not a whole-pipeline promotion,
holdout-transfer claim, or benchmark-comparable result.

## Question

Given fixed candidate, evidence, selected-state, and gated projection-policy
decisions, can the deterministic compiler/rendering layer emit Gan-compatible
labels without semantic drift, benchmark-format leakage, or loss of exact
evidence attribution?

Primary component under test: deterministic compilation/rendering from a fixed
selected state and fixed projection-policy decision into the final scorer-facing
Gan label.

Fixed upstream components:

- candidate set and selected candidate/state;
- selected evidence text and source ids;
- selected graph/state nodes and typed operands;
- explicit ACD projection-policy decision, when applicable;
- deterministic top label as frozen comparator and safety floor only.

Surface: saved validation-development replay under `gan2026_split_v1`,
plus focused ACD policy fixtures. Locked holdout rows are excluded.

## Claim Boundary

The answer may only be described as a validation-development compiler/rendering
answer. It may decide whether the current deterministic rendering contract is
mechanically faithful for fixed states, which policy families need ablation, and
which failures belong to missing upstream state representation rather than
rendering.

It must not claim:

- that a whole pipeline is promoted;
- that ACD policies transfer to holdout;
- that deterministic rules are the research answer to RQ1/RQ2/RQ4;
- that validation aggregate F1 is benchmark-comparable.

## Artifacts To Replay

Replay saved artifacts before any fresh model calls or broad validation runs:

- `experiments/gan2026_component_projection_followup_panel_2026-06-04.md`
- `experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl`
- `experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl`
- ``
- ``
- focused tests in `tests/test_gan2026_state_graph.py` for ACD-003 through
  ACD-010

If a needed row lacks materialized selected-state or rendering metadata, mark it
as an instrumentation gap. Do not infer promotable results from prose-only
inspection.

## Fixed State Bundle

Each RQ5 row must freeze a state bundle before rendering:

- `source_row_index`, split, artifact path, and row role;
- gold label and gold label kind for scoring reference;
- deterministic baseline label and correctness;
- selected state id or node ids;
- selected state kind, temporality, assertion status, applies-to/semiology, and
  certainty;
- selected evidence exact substring and source ids;
- typed operands needed for rendering, such as count, count range, denominator,
  duration, calendar span, seizure-free interval, cluster axis, event dates,
  or uncertainty flag;
- active projection policy, including `projection_policy.acd_*` when applicable;
- projection rationale and first-failure owner from the source artifact when
  available.

The fixed state bundle is the contract. RQ5 may change only compilation or
rendering behavior over that bundle, not which state was selected.

## Explicit ACD Projection Policies

RQ5 must test the rendering behavior of the predeclared ACD policies as named
policy inputs:

| Policy | Fixed decision | Rendering expectation |
| --- | --- | --- |
| ACD-003 | Vague count adjective with denominator is projection-compatible; vague adjective without denominator is unknown. | Render `multiple per <denominator>` or `unknown` without inventing counts. |
| ACD-004 | Conditional-only trigger without cadence is not a rate. | Render `unknown`; preserve trigger evidence. |
| ACD-005 | Relative-only trend without absolute rate is not a current rate. | Render `unknown` unless a fixed absolute operand exists. |
| ACD-006 | Diary dates are summed and normalized to the covered calendar span. | Render count/range over month span, preserving date-list evidence. |
| ACD-007 | No definite epileptic events with non-epileptic triage is seizure-free. | Render the fixed seizure-free month bucket; do not count triaged events. |
| ACD-008 | Explicit current qualitative summary overrides derived long-period average. | Render the summary rate, not the arithmetic average. |
| ACD-009 | Previous-month active burden overrides short current-month-to-date zero count. | Render the previous-month burden unless a fixed long seizure-free state exists. |
| ACD-010 | Recent major-semiology relapse outranks lower-severity interictal rates. | Render the major-relapse rate/window. |

ACD-001 and ACD-002 remain interpretation-policy inputs for
projection-compatible phrases and denominator-ambiguous facts. Include them in
diagnostics when rows expose those phrases, but do not broaden production scope
unless a later predeclaration adds them.

## Rendering Matrix Schema

Create one row per fixed state bundle and rendering decision with these fields:

- source row, split, row role, hidden-family tags, and source artifact;
- fixed selected state fields and typed operands;
- active projection policy and ACD id, if any;
- compiler/rendering variant name;
- rendered label, rendered label kind, normalized scorer label, and parse status;
- deterministic baseline label and changed-from-baseline flag;
- exact-label match, Purist correctness, and Pragmatic correctness where
  permitted by the saved surface;
- W->C and C->W accounting against the fixed comparator;
- semantic-drift flag and drift family;
- benchmark-format leakage flag;
- exact-evidence-retained flag and source-id-retained flag;
- operand-loss flag, such as lost denominator, lost range, lost duration, lost
  cluster axis, lost uncertainty, or lost semiology priority;
- first-failure owner after rendering: upstream_state, projection_policy,
  compiler_renderer, scorer_gold_ambiguity, or instrumentation_gap;
- claim boundary: materialized replay, focused fixture, diagnostic-only, or
  blocked.

## Compared Compiler/Renderer Variants

At minimum compare:

- current production deterministic rendering;
- ACD-aware rendering with the predeclared policy id retained in metadata;
- ACD-off ablation, where the same fixed state is rendered without the named
  ACD policy decision;
- strict-format rendering, which only accepts labels already in canonical Gan
  grammar;
- evidence-preserving rendering, which emits the same label as production but
  fails if selected evidence or source ids are dropped.

The ACD-off and strict-format variants are ablations, not candidate policies.
Their purpose is to measure how much final correctness depends on explicit
policy and whether formatting alone causes semantic loss.

## Primary Metrics

Report component metrics, not only final F1:

- renderer parse-valid rate;
- exact-label match for fixed-state rows;
- Purist and Pragmatic correctness on materialized saved surfaces;
- semantic-drift count and family breakdown;
- benchmark-format leakage count;
- exact-evidence and source-id retention rate;
- W->C and C->W changed-row accounting against the deterministic comparator;
- ACD-on versus ACD-off delta by policy id;
- hidden-family breakdown for projection-policy, benchmark-format,
  rate-bucket/denominator, seizure-free-duration, cluster/diary, temporal
  conflict, competing-semiology, and uncertainty rows.

## Row-Level Requirements

The report must include representative rows where rendering:

- faithfully converts a projection-compatible phrase into Gan syntax;
- converts a fixed ambiguous or conditional state to `unknown`;
- preserves a diary/date-list count and covered span;
- preserves a seizure-free duration bucket without counting non-epileptic
  events;
- prefers a fixed summary rate over a derived average;
- prefers previous active burden over a short current zero window;
- preserves a major-semiology relapse priority;
- drops or distorts a fixed operand, if any such failures remain.

Separate these cases explicitly:

- the fixed state was wrong upstream;
- the projection policy decision was wrong;
- the compiler/renderer changed the fixed state;
- the scorer/gold label is ambiguous;
- the artifact lacks enough metadata to decide.

## Stop Rule

RQ5 can be marked answered for validation development when the report can state:

- whether deterministic compilation/rendering is faithful over materialized
  fixed selected states;
- which ACD policies are required for correctness and what their ablated effect
  is;
- whether any observed C->W regression is caused by rendering rather than
  upstream selection or projection;
- which hidden families still fail because the selected state bundle lacks
  operands;
- whether evidence/source-id attribution survives final rendering;
- what instrumentation is required before any holdout-facing audit.

If the artifacts do not expose fixed state bundles or rendered metadata at the
needed grain, the correct RQ5 result is "blocked by instrumentation" with a
minimal artifact schema to add next.

## Disallowed Work

- No locked-test row-level inspection or tuning.
- No fresh model calls.
- No changing selected candidates, selected evidence, selected states, or ACD
  policy decisions during the rendering audit.
- No broad validation sweep whose only purpose is aggregate F1.
- No claiming ACD policy transfer without a separate frozen pre-holdout audit.
- No counting deterministic top performance as the RQ5 answer unless the
  fixed-state rendering component has been isolated.

## Next Artifact

Build:

```text
experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.jsonl
```

and a short paired report:

```text
experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.md
```

The JSONL should be the source of truth. The report should summarize the answer,
ACD ablation deltas, row examples, hidden-family readout, transfer confidence,
instrumentation gaps, and the next action.
