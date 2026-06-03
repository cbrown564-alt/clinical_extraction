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

Durable artifacts: hybrid validation interpretation,
`docs/research/gan2026_frozen_test_audit_plan_2026-06-03.md`, and Decision
0007 final-projection replay
`experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation50_gpt41mini_v1_final_projected_replay_2026-06-03.md`.

Attribution caveat: this is a hybrid deterministic-safety-floor development
result, not an LLM-first result and not a benchmark or holdout claim. For the
LLM-heavy lane, Decision 0007 v1 is now the primary architecture: typed
LLM-owned clinical selection plus deterministic mechanical adapters and an
explicit, ablated post-processing layer over selected labels/evidence.

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
4. Advance Decision 0007 as the primary LLM-heavy lane with explicit,
   separately ablated final-projection families.

## Work Board

### Now

- Decide whether to predeclare Decision 0007 validation250 with
  `final_projected_label`, including an explicit stop rule and attribution
  language for deterministic projection families.

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

- 2026-06-03: Generated Decision 0007 validation50 no-call final-projection
  replay from saved GPT-4.1 mini outputs. `final_projected_label` reached 50/50
  Purist and 50/50 Pragmatic, with 50/50 reused raw outputs, 50/50 scorable
  final labels, and projection-family counts recorded in
  `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation50_gpt41mini_v1_final_projected_replay_2026-06-03.md`.
- 2026-06-03: Triaged the 53 remaining validation750 Purist misses in
  `experiments/gan2026_validation_53_purist_misses_component_stress_2026-06-03.md`
  and drafted the frozen-test audit plan.
- 2026-06-03: Added deterministic safety-floor final policy to the hybrid
  reasoner and replayed validation750 live outputs to 697/750 Purist (0.9293),
  704/750 Pragmatic (0.9387), 0 deterministic-correct regressions, and 136/750
  safety-floor fallbacks.
- 2026-06-03: Promoted Decision 0007 to the primary LLM-heavy lane after
  validation50 showed 50/50 structured outputs, 44/50 mechanical-adapter Purist,
  and mostly repairable label-processing failures. Analysis:
  `experiments/gan2026_decision0007_validation50_comprehensive_error_analysis_2026-06-03.md`.

## Immediate Next Step

Draft or reject a predeclared Decision 0007 validation250 plan that names the
`final_projected_label` families, expected learning value, row-inspection
policy, and promotion/rejection criteria before any broader validation run.
