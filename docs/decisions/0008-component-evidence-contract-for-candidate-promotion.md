# 0008: Component Evidence Contract For Candidate Promotion

Date: 2026-06-03

## Decision

Candidate promotion must use a component evidence contract before broad
validation, production-language, or locked-holdout movement.

The contract is defined in
`docs/design/component_evidence_attribution_architecture.md` and requires every
promotion report to answer:

- which clinical subproblem each component solved;
- what evidence gate was satisfied;
- what distribution was used;
- whether the candidate regressed deterministic-correct rows;
- whether LLM changes to deterministic answers were correct.

## Scope

This decision applies to Gan 2026 development candidates and to any later
clinical extraction task once it starts producing candidate-promotion claims.

It does not require every smoke test to produce a full report. It does require
the full report before calling a candidate promoted, production-ready,
LLM-superior, or ready for locked holdout.

## Rationale

The project now has high validation scores and multiple overlapping mechanisms:
deterministic rules, LLM-selected evidence, deterministic adapters, graph
projection, safety floors, and benchmark-format repair. Aggregate F1 cannot
separate clinical reasoning from mechanical rendering or safety-floor behavior.

A reusable evidence contract keeps the research claims aligned with the system
architecture:

- deterministic rules remain controlled variables;
- LLM-owned clinical selection remains distinguishable from hybrid projection;
- exact-evidence and source-id validity remain promotion gates;
- saturated validation aggregates do not substitute for mechanism evidence;
- locked holdout remains frozen and protected from row-level tuning.

## Required Reporting

Promotion reports must include:

- a component evidence matrix grouped by clinical subproblem;
- a score-layer ladder for raw model, adapter, projection, safety floor, and
  final policy when available;
- an LLM delta table against the deterministic comparator;
- changed-row exact-evidence and valid-source accounting;
- deterministic-correct regression accounting;
- first-failure owner and hidden-family breakdowns;
- claim language naming split, distribution, model, replay mode, scorer policy,
  repair policy, and experiment family.

## Consequences

- Broad validation and locked-holdout execution should be blocked when the
  report cannot explain changed-label precision and regression risk.
- Architecture work should prioritize reusable artifact fields over isolated
  markdown summaries.
- LLM-superiority claims must be restricted to LLM-owned clinical decisions that
  satisfy exact-evidence and no-regression gates.
- Hybrid safety-floor results can still be strong, but they must be described
  as hybrid and not LLM-first.

## Related Artifacts

- `docs/design/component_evidence_attribution_architecture.md`
- `docs/runbooks/gan2026_component_evidence_audit.md`
- `docs/research/contribution_thesis.md`
- `docs/design/gan2026_split_protocol.md`
- `docs/design/gan2026_saturated_validation_protocol.md`
- `docs/decisions/0007-llm-heavy-clinical-selection-deterministic-adapters.md`
