> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ8 Efficiency And Operational Reliability Protocol

Date: 2026-06-04

Status: protocol and evidence-gap statement. Superseded for current
interpretation by
``.
Token, latency, retry, and cost-per-1,000-note claims remain blocked by missing
telemetry.

## Question

RQ8 asks which schema and component design gives the best performance per
token, cost, latency, parse reliability, retry burden, metadata yield, and
implementation complexity.

This question should now be answered as a controlled operational comparison
among the surviving component roles, not as a broad architecture race.

## Current Evidence Gap

The repo has scattered operational evidence but no clean RQ8 answer table.
Existing artifacts show:

- rich selected state can parse reliably on focused and hard-panel surfaces;
- candidate-conditioned evidence selection is the cleanest narrow primitive;
- full bundled prompts parse but degrade exact-evidence quality and source-id
  discipline;
- typed operations remain too complex even with large token budgets;
- Qwen/Ollama strict JSON behavior can turn otherwise useful content into parse
  failures;
- deterministic rendering has 0 parse failures on the fixed-state RQ5 matrix.

That is enough to bound likely winners and losers, but not enough to claim an
optimal operational architecture.

## Components To Compare

Use saved artifacts first. New model calls are allowed only if a metric is
missing and the run is predeclared.

| Component | Role | Include why |
| --- | --- | --- |
| `candidate_conditioned_evidence_only` | RQ2 evidence gate | Best extractive primitive in component-control matrix. |
| `gold_query_evidence_only` | Broad evidence packet | Strong broader locator with higher evidence burden. |
| `candidate_only` | Selective candidate proposer | Useful selective RQ1 surface, more schema drift. |
| `rich_selected_state_v0` | RQ3 fact carrier | Preferred state representation, needs operational accounting. |
| `selective_safety_floor_gate_v0` | RQ6 selective action | Best no-regression action policy; mostly no-call replay. |
| `typed_operations_v0` | Negative control | Deep schema with duplicated ownership and token/parse risk. |
| `candidate_plus_evidence_plus_projection` | Overload negative control | Tests why all-in-one prompts should be rejected. |

## Metrics

The RQ8 matrix should report one row per component, model, surface, and run
mode.

Required fields:

- prompt tokens;
- completion tokens;
- total tokens;
- wall-clock latency;
- estimated cost per 1,000 notes;
- call failure count;
- parse/schema failure count;
- retry count;
- structured-record rate;
- exact evidence rate where applicable;
- valid source-id rate where applicable;
- metadata yield per row;
- rows per note or candidates/spans per note;
- downstream W->C/C->W where the component can change labels;
- implementation complexity note: parser special cases, adapter sidecars,
  repair stack, and schema breadth.

## Surfaces

Use paired surfaces rather than another broad F1 race:

1. `balanced_validation50` from the RQ1/RQ2 component-control matrix.
2. `hidden_family_hard_panel` from the same matrix.
3. Saved validation750 or validation250 artifacts only when already available
   for the component.
4. No locked-test operational analysis unless a frozen audit protocol already
   permits the aggregate readout.

## Stop Rule

RQ8 is answered when the report can identify:

- the cheapest reliable evidence-location primitive;
- the cheapest reliable candidate-proposal primitive;
- the least fragile state representation worth carrying forward;
- which schemas are rejected for parse/token/complexity reasons;
- whether any component has unacceptable retry, parse, or source-id burden;
- whether operational cost changes the architecture recommendation from RQ1-RQ7.

## Expected Decision Boundary

Based on current evidence, the likely answer is:

```text
Use narrow extractive prompts and deterministic rendering; avoid deep schemas
and all-in-one prompts unless they prove materially better metadata yield per
token without projection regressions.
```

That sentence is a hypothesis, not yet the RQ8 answer.

## Next Action

Build a no-new-call RQ8 operational matrix from existing JSONL and markdown
artifacts. If token or latency fields are missing for a surviving component,
predeclare one small paired run on `balanced_validation50` and
`hidden_family_hard_panel` before calling RQ8 answered.
