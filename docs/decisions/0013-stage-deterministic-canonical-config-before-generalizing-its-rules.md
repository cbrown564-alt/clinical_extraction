# 0013: Stage The deterministic_canonical_pipeline Config Before Generalizing Its Rules

Date: 2026-06-07

## Status

Accepted.

## Decision

Add the new `deterministic_canonical_pipeline` configuration for
`Gan2026PipelineRunner`
([[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]) in
two passes rather than one:

1. **Staging pass (this decision's scope)**: restructure the existing
   deterministic logic into named, stage-owned, ablatable form — its current
   rules left otherwise unchanged — and get that running as the baseline for
   the three-way comparison's Phase 1.
2. **Generalization pass (later, Section 4)**: only then run the plan's
   family-by-family de-overfitting rewrite against the now-legible staged
   structure, re-running and comparing the validation score after each family.

## Context

When planning this configuration, we considered building it as a single
combined pass: restructure the existing deterministic logic into named stages
*and* rewrite its validation-phrase-shaped rules into general, source-backed
ones (Section 4 of the cross-pollination plan) at the same time, since the
goal is the best possible deterministic pipeline, not a museum artifact of
overfitting.

## Why

Combining the passes would remove the plan's own before/after signal — Section
4 explicitly wants to check "does the validation score move in a plausible,
explicable direction after each rewritten family," which requires a known,
measurable starting point. Staging-first is also a genuine prerequisite, not a
detour: Section 4's mechanism (rewrite one family at a time, ablate, re-run) is
impossible without named, separable stages to rewrite within. Doing both in one
pass would make the comparison look cleaner sooner but would permanently
destroy the ability to measure the de-overfitting delta the plan is built
around.

## Consequences

- The staging pass must be a pure mechanical restructure: no rule or behavior
  changes, and the new configuration's diagnostics must remain directly
  comparable to the existing `deterministic` configuration's so that "rules
  unchanged" is an assertable equivalence, not a claim taken on faith.
- Section 4's de-overfitting rewrite must wait until the staged structure
  exists and is proven equivalent — it cannot be folded into the same change
  that introduces the staged seams.
- See [[0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline]]
  for the related decision on naming this configuration's new verify-adjacent
  stage.
