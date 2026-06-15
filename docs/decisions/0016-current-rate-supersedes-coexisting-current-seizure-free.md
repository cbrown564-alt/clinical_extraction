# 0016: A Current Positive Rate Wins Over A Coexisting Current Seizure-Free Assertion

Date: 2026-06-15

## Status

Accepted.

## Decision

When a **current positive frequency rate** and a **current seizure-free
assertion** apply to the same target and there is **no `SUPERSEDES` edge to
break the tie**, the positive rate wins. The seizure-free node is flagged
`contradicted_by_current_rate` and the resolved label is the rate, not
`unknown` and not seizure-free.

This is the single canonical answer to contradiction **C1** in
[[gan2026_rule_register]] and the rule stated in
[[gan2026_resolve_label_spec]] §3 Step 3.

The `unknown` outcome on a `CONTRADICTS` edge is reserved for the case where the
conflict **cannot** be attributed to a current rate (e.g. both sides are vague).

## Context

The same decision was encoded three different ways:

- `deterministic_selection.py` (`selection_score`, register §5) ranks
  `current_seizure_free` (priority 5) **above** `frequency` (priority 4) —
  seizure-free wins.
- `state_graph/projection.py` (`_select_projection_nodes`,
  `_projection_priority`) selects current-frequency nodes first and ranks
  `FREQUENCY` (4) above `SEIZURE_FREE` (3) — rate wins.
- `state_graph/resolve.py` (`_surviving_contradiction`) returned `"unknown"`
  with flag `unbroken_seizure_free_vs_rate_contradiction` — neither side wins.

Three engines, three answers, for one decision. The register exists to state
each operative rule once; this is its headline contradiction.

## Considered Options

- **Seizure-free wins** (legacy deterministic ladder). Rationale: "current
  control overrides a stale rate." Rejected: the ladder cannot distinguish a
  *current* rate from a *historical* one — historical-rate-vs-current-control is
  already handled by `SUPERSEDES` (the older rate is dominated in Step 1), so the
  ladder's inversion only fires on genuinely *current* conflicts, where it is
  wrong.
- **Preserve `unknown`** (resolve.py as shipped). Rationale: conservative;
  aligns with register §7.1 "if unclear, prefer `unknown`." Rejected: a positive
  current rate is direct evidence of ongoing seizures; abstaining to `unknown`
  discards real quantified evidence. A genuine same-target current contradiction
  is almost always a subtype/scope artifact (seizure-free for one event type,
  a rate for another), not true ambiguity about whether seizures occur.
- **Rate wins** (chosen). A current positive rate is direct evidence of ongoing
  seizures; a same-period seizure-free claim is then about a subtype/scope and
  must not zero out the rate.

## Why

Precedence is decided by *temporality and target of the specific competing
statements*, not by a global kind ranking. Once `SUPERSEDES` has dominated any
historical rate (Step 1), the only conflicts that reach the `CONTRADICTS`
resolution are *current-vs-current for the same target* — and there a quantified
rate is the stronger evidence. This reconciles the projection ladder (which
already does rate-wins) with the register, and isolates the legacy
`deterministic_selection.py` inversion as the outlier to retire.

## Consequences

- `state_graph/resolve.py::_surviving_contradiction` is **wrong as shipped** and
  must change: keep the positive-rate node, flag the seizure-free node
  `contradicted_by_current_rate`, and fall through to ranking. The `unknown`
  branch survives only for non-rate-attributable conflicts. This is a
  label-changing behavior change and must ride the 25→50→250 validation ladder
  ([[gan2026_kg_grounded_component_generation_design_2026-06-15]] §5), not a
  silent patch.
- The projection path already implements rate-wins, so the change is localized
  to removing resolve.py's `unknown` intercept; no projection change is needed.
- The legacy `deterministic_selection.py` seizure-free-above-frequency ladder is
  now a known outlier. It is left untouched on the deterministic path for now
  (parallel posture, see [[0017-ontology-over-inference-guard-is-graph-path-only]]),
  but it no longer represents the canonical rule.

## Related Artifacts

- [[gan2026_rule_register]] — contradiction C1, §5, §8
- [[gan2026_resolve_label_spec]] — §3 Step 3
- [[0017-ontology-over-inference-guard-is-graph-path-only]]
