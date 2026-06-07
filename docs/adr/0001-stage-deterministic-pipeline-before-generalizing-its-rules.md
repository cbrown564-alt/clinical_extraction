# Stage the deterministic canonical pipeline before generalizing its rules

When assembling `Gan2026PipelineV1` into the deterministic canonical runner for
the three-way architecture comparison
([[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]), we
considered doing the staging (splitting its monolithic logic into named
Extract/Normalize/Project/Render/Verify stages) and the de-overfitting
rewrite (Section 4 of that plan — replacing validation-phrase-shaped rules with
general, source-backed ones) in a single combined pass, since we want the
deterministic pipeline to be the best it can be rather than a museum artifact.

We decided to do these in two passes instead: stage the existing rules as-is
first (pure restructuring, no rule changes — matching the Phase 0 gate of
"mechanical/structural work, no validation-score risk"), get that staged,
known-overfit version running as the Phase 0/Phase 1 baseline, and only then
run Section 4's family-by-family generalization rewrite against the now-legible
staged structure, re-running and comparing after each family.

## Why

Combining the passes would remove the plan's own before/after signal — Section
4 explicitly wants to check "does the validation score move in a plausible,
explicable direction after each rewritten family." That check requires a known,
measurable starting point. Staging-first also isn't wasted scaffolding: Section
4's mechanism (rewrite one family at a time, ablate, re-run) is impossible
without named, separable stages to rewrite within — staging is a prerequisite
for the rewrite, not a detour from it. Doing both in one pass would have made
the comparison cleaner-looking sooner but would have permanently destroyed the
ability to measure the de-overfitting delta the plan is built around.
