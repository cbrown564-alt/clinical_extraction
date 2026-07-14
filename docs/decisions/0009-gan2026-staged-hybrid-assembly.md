# 0009. Gan 2026 Staged LLM-with-Rules Assembly

Date: 2026-06-04

## Status

Accepted for validation development.

## Context

The earlier Gan 2026 pipeline direction emphasized an LLM-first extraction
pipeline with deterministic validation, evidence checks, arithmetic,
normalization, benchmark-format repair, and scoring. Subsequent RQ1-RQ10
component studies showed that broad LLM replacement, broad graph projection,
and all-in-one prompting are not the reliable path for this task.

The strongest evidence now supports a staged LLM-with-rules architecture where each
component owns a narrow clinical subproblem and every label-changing action is
gated by exact evidence, source ids, and regression accounting.

## Decision

Use a staged LLM-with-rules architecture for the next Gan 2026 assembled candidate:

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

The assembled candidate must be described as LLM with rules. It must not be described
as LLM-first, because deterministic candidate generation, state graph nodes,
projection policies, rendering, abstention/review policy, and safety-floor
fallback remain prediction-bearing.

## Consequences

- Direct final-label LLM prompting is not a promotion candidate.
- Broad state-graph projection is not a promotion candidate.
- `typed_operations_v0` and similarly deep schemas remain negative controls
  unless redesigned with a single decision owner and a clean ablation.
- New implementation must first materialize source ids for rich selected
  states and add deterministic suspicious-state checks.
- Any future holdout-facing use requires a frozen predeclared audit protocol.

## Retained Evidence

The selected Gan architecture artifacts, hashes, and no-call replay closure live
in `docs/experiments/retained_evidence_manifest.json`. Historical RQ reports are
recoverable from Git but are not active evidence owners.
