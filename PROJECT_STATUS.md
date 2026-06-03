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
`docs/research/gan2026_frozen_test_audit_plan_2026-06-03.md`, Decision 0007
validation250 rejection
`experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.md`,
and hidden-family/first-failure atlas
`docs/research/gan2026_hidden_family_first_failure_atlas_2026-06-03.md`.

Attribution caveat: this is a hybrid deterministic-safety-floor development
result, not an LLM-first result and not a benchmark or holdout claim. Decision
0007 remains the primary LLM-heavy design lane, but v1 validation250 was
rejected; the atlas points next toward candidate-generation and projection
hard-slice work before another broad architecture or multi-agent run.

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
3. Use the hidden-family/first-failure atlas to target candidate-generation,
   projection, and LLM clinical-selection hard slices before any broad rerun.
4. Keep Decision 0007 alive as the LLM-heavy lane, but do not escalate v1 until
   selected-fact and operand failures have a targeted validation-cycle plan.

## Work Board

### Now

- Design the next diagnostic experiment from the atlas: candidate-generation
  rescue plus projection hard slices, with deterministic safety floor preserved.

### Next

- Convert the atlas owner/family counts into reproducible slice manifests for
  candidate-generation, unknown/seizure-free boundary, and projection failures.
- Decide whether to add a selective LLM/graph override gate on hard slices, with deterministic safety floor preserved.
- If iterating on Decision 0007, focus on selected-fact and operand completeness
  only after slice targets and stop rules are predeclared.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the safety-floor candidate is frozen.

### Backlog

- Explore a multi-agent LLM architecture that decomposes the task into sequential, separately optimized calls for candidate identification, candidate selection, candidate normalization, and clinical verification, with component ownership and ablations explicit under the `llm_only`/`hybrid` ontology.

### Blocked

- Benchmark language and holdout analysis are blocked until the frozen-test plan is followed without post-test tuning.
- Qwen 3.6 full v5 validation ladder remains blocked until strict schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Built a reusable hidden-family/first-failure atlas module and
  generated `docs/research/gan2026_hidden_family_first_failure_atlas_2026-06-03.md`
  over Decision 0007 validation250 plus hybrid safety-floor validation750.
  Among 89 Purist misses, first-failure owners were candidate generation (44),
  LLM clinical selection (22), projection (9), operand exposure (8),
  deterministic adapter (3), final projection (2), and schema/parse (1).
- 2026-06-03: Executed Decision 0007 validation250 stress test; the candidate reached 0.8560 Purist F1 on `final_projected_label` but was rejected due to standalone mechanical adapter accuracy (180/250 vs >=220 gate), regressions, and incomplete operands.
- 2026-06-03: Executed the frozen-test audit of the hybrid candidate on the 450-row locked test split, reaching 0.7622 Purist F1 / 0.7867 Pragmatic F1 with 100% exact selected evidence, 100% valid source IDs, 0 deterministic-correct regressions, and 11 graph projection rescues.
- 2026-06-03: Predeclared Decision 0007 validation250 final-projection stress
  test in
  `experiments/gan2026_llm_heavy_decision0007_v1_validation250_final_projection_predeclaration_2026-06-03.md`.
  The plan allows a targeted validation250 run but treats
  `final_projected_label` as an ablated hybrid/projection layer, not the primary
  LLM-heavy score layer.
- 2026-06-03: Generated Decision 0007 validation50 final-projection replay:
  `final_projected_label` reached 50/50 Purist and 50/50 Pragmatic from saved
  GPT-4.1 mini outputs, after validation50 showed 50/50 structured outputs and
  44/50 mechanical-adapter Purist.
- 2026-06-03: Triaged the 53 remaining validation750 Purist misses, drafted the
  frozen-test audit plan, and replayed the hybrid safety-floor policy to 697/750
  Purist (0.9293), 704/750 Pragmatic (0.9387), 0 deterministic-correct
  regressions, and 136/750 safety-floor fallbacks.

## Immediate Next Step

Predeclare an atlas-driven hard-slice experiment for candidate-generation rescue
and projection arbitration; keep the multi-agent pipeline in backlog until the
slice manifest shows which subtask each call would own.
