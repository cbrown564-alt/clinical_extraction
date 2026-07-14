# 0008: Require component attribution before adopting a method

Date: 2026-06-03

Before broad validation, holdout use, or production language, a report must say:

- which component solved each clinical subproblem;
- what evidence supported that decision;
- which data were used;
- whether a rules-correct row became wrong;
- whether model changes to rules-based answers helped or hurt.

The required fields and report are defined in
`docs/design/component_evidence_attribution_architecture.md`. Smoke tests do not
need the full report. Adoption, holdout readiness, and claims that a model is
better do.

Aggregate F1 cannot separate clinical reasoning, mechanical formatting,
deterministic fallback, and later repair. Reports therefore preserve output
after each step, model changes versus rules, exact evidence, regressions, first
failure, clinically meaningful case types, and the split, model, scorer, and
repair policy.

If those records are missing, add instrumentation or replay saved outputs before
running more data. Combined methods may be strong, but their gains must not be
credited to the model alone.
