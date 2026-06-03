# Project Status

Last updated: 2026-06-03

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving evidence trails,
component ablations, split discipline, and conservative benchmark language.

## Current Strategy

The current leading development candidate is
`hybrid_parallel_state_candidate_reasoner` with a deterministic safety-floor
final policy. Full validation750 no-call replay of the live GPT-4.1 mini
outputs reaches 697/750 Purist (0.9293) and 704/750 Pragmatic (0.9387), with
750/750 exact selected evidence, 750/750 valid source ids, 0
deterministic-correct regressions, and 136/750 safety-floor fallbacks.

Durable artifacts: validation interpretation at
`experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_safety_floor_interpretation_2026-06-03.md`
and frozen-test audit plan at
`docs/research/gan2026_frozen_test_audit_plan_2026-06-03.md`.

Attribution caveat: this is a hybrid deterministic-safety-floor development
result, not an LLM-first result and not a benchmark or holdout claim. LLM-heavy
Decision 0007 v1 remains a revise lane after its validation50 failure rows.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
  Validation is the development surface; locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator. Do not tune it from
  locked-test audit behavior.
- Hybrid v0.2 `cluster_diary_candidate_recall` remains a frozen comparator-only
  generalization audit result.
- Treat saturated aggregate validation scores as low-information; prefer
  hard-slice, component-stress, and frozen-audit evidence.
- Keep semantic repair, graph projection, scorer normalization, deterministic
  adapters, and production policy separately named and ablated.
- Use typed DSPy outputs with scoped `JSONAdapter` for new LLM/DSPy architectures.

## Active Priorities

1. Preserve attribution language for the achieved result: hybrid
   deterministic-safety-floor, validation development only.
2. If running locked test, follow the frozen-test audit plan exactly before any
   holdout execution or row-level inspection.
3. Use component-stress/error analysis to decide whether LLM/graph overrides can
   improve beyond the deterministic safety floor without regressions.
4. Keep LLM-heavy v1 as a separate revise lane: bimonthly operands,
   weekday/vague frequency operands, `≤ N` upper-bound semantics, evidence
   contiguity, and raw-correct adapter fallback.

## Work Board

### Now

- Execute the frozen-test audit under `docs/research/gan2026_frozen_test_audit_plan_2026-06-03.md` now that the validation misses triage is complete.

### Next

- Decide whether to add a selective LLM/graph override gate on hard slices, with
  deterministic safety floor preserved.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the
  safety-floor candidate is frozen.

### Blocked

- Benchmark language and holdout analysis are blocked until the frozen-test plan
  is followed without post-test tuning.
- Qwen 3.6 full v5 validation ladder remains blocked until strict
  schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Triaged the 53 remaining validation750 Purist misses and built the validation hard-slice/component-stress artifact at `experiments/gan2026_validation_53_purist_misses_component_stress_2026-06-03.md`.
- 2026-06-03: Reviewed the safety-floor change, fixed stale full-validation
  report gate language (`promote_to_50` on a 750-row artifact), and drafted the
  frozen-test audit plan with predeclared aggregate/slice inspection policy.
- 2026-06-03: Added deterministic safety-floor final policy to
  `hybrid_parallel_state_candidate_reasoner` and replayed the full validation750
  live outputs. Final replay reached 697/750 Purist (0.9293), 704/750 Pragmatic
  (0.9387), 750/750 exact selected evidence, 750/750 valid source ids, 0
  deterministic-correct regressions, and 136/750 safety-floor fallbacks.
- 2026-06-03: Ran hybrid validation50, validation250, and full validation750
  live escalations. The ungated live full-validation adapted layer reached
  669/750 Purist (0.8920), motivating the deterministic safety-floor replay.
- 2026-06-03: Ran LLM-heavy Decision 0007 validation25/50 contract work. The
  validation50 run had 50/50 structured outputs and 44/50 raw/mechanical Purist,
  but selected-evidence and adapter-regression failures keep it in revise.

## Immediate Next Step

Execute the frozen-test audit plan as written under `docs/research/gan2026_frozen_test_audit_plan_2026-06-03.md`.

