# Gan 2026 Agentic Phase 5 Contracts

Date: 2026-06-12

Status: Phase 5 implementation contract for the agentic comparison phase.

Controlling plan:
`docs/experiments/gan2026/agentic/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`.

## Scope

Phase 5 turns the agentic phase plan into repo-native contracts that can be
tested before any model calls are spent. It does not authorize new holdout use,
row-level test inspection, prompt tuning, or benchmark-facing claims.

## Agent Definition

For Gan 2026, an agentic condition is a model-owned decision loop that may keep
state, request tools, inspect bounded tool output, and then emit the
prediction-bearing clinical interpretation. A tool-assisted result is not
LLM-only unless the model explicitly owns the final clinical selection and the
deterministic layers are limited to schema repair, formatting, normalization of
already selected facts, and scoring.

The initial repo implementation remains a transparent runner around typed
contracts rather than a framework dependency.

## Matched-Budget Contract

`AgentBudget` and `MatchedBudgetComparison` live in:

```text
src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/contracts.py
```

Every Phase 6 comparison must predeclare equal caps for:

- model calls per row;
- prompt token budget;
- maximum completion tokens per call;
- maximum tool calls per row;
- maximum tool-output tokens per row;
- aggregation model-call budget.

The contract rejects comparisons when those caps differ. This keeps
`multi_agent_matched` from being compared against a weaker single-agent baseline.

## Parser Tool Contract

The callable parser wrapper is:

```text
parse_seizure_frequency_candidates(note_text, max_candidates=12)
```

It returns `ParserToolResult` with schema version
`gan2026_agent_parser_tool_v0`.

Allowed output:

- source-near candidate IDs local to the tool response;
- candidate kind;
- evidence text and character span;
- deterministic parser rule ID;
- rule group;
- portability category;
- match groups;
- parse warnings.

Forbidden output:

- gold labels;
- normalized gold labels;
- split membership;
- source row IDs;
- scorer hints.

No-result behavior is explicit: an empty candidate list plus
`no_candidates_found`. The parser tool does not invent
`no seizure frequency reference`; that remains a model-owned or downstream
selection decision.

Attribution: candidate discovery is deterministic-tool-owned. A later
tool-using agent can claim model-owned clinical selection only when the trace
shows that the model selected, combined, or rejected returned candidates with
evidence.

## Boundary Guide Reader Contract

The callable guide wrapper is:

```text
read_boundary_guide(query)
```

It returns `BoundaryGuideResult` with schema version
`gan2026_boundary_guide_v0` and guide version `2026-06-12.phase5`.

The initial split-neutral guide IDs are:

- `multiple_current_events_aggregation`
- `seizure_free_event_conflict`
- `cluster_frequency_vs_incidental_clustering`
- `last_event_only_vs_recurring_rate`
- `unknown_frequency_vs_no_reference`
- `current_vs_historical_window`
- `different_semiology_burdens`

The guide reader fails closed for unknown queries and reports available guide
IDs. Guide text is intentionally compact and contains no row IDs, gold labels,
validation/test references, or answer-bearing dataset examples.

## Validation Surface

The first Phase 6 smoke should use validation-only development surfaces:

1. validation25 contract smoke for schema, tool-call logging, parse failures,
   and trace completeness;
2. synthetic or validation hard-slice panels for boundary behavior;
3. validation50 only after the tool trace is complete enough to inspect.

Locked `test450` remains blocked unless a fresh frozen aggregate protocol is
explicitly authorized.

## Tests

Pinned by:

```text
tests/test_gan2026_agentic_phase5_contracts.py
```

The tests cover parser no-leak behavior, explicit no-result behavior, guide
retrieval, guide fail-closed behavior, and matched-budget mismatch rejection.
