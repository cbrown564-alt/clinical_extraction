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
The atlas-derived hard-slice predeclaration is fixed in
`experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.md`
and JSON manifest
`experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json`.
The no-call fixed-slice diagnostic is recorded in
`experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.md`.
Regenerate it with `gan2026-atlas-hard-slice-diagnostic`; the standard report
now includes automated "Rows That Would Change" tables plus a required
after-generation human interpretation note.

Attribution caveat: this is a hybrid deterministic-safety-floor development
result, not an LLM-first result and not a benchmark or holdout claim. Decision
0007 remains the primary LLM-heavy design lane, but v1 validation250 was
rejected; fixed atlas slices now point next toward candidate-generation rescue
and projection arbitration before another broad architecture or multi-agent run.

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
5. Answer the critical research questions for each candidate before promotion:
   - For each clinical subproblem, can the system show which component solves it, under what evidence constraints, with what regression risk, and on which distribution?
   - Which clinically meaningful decisions can the LLM make more robustly than deterministic rules under exact-evidence and regression constraints?
   - When the LLM changes the deterministic answer, how often is that change correct?

## Work Board

### Now

- Interpret the selective safety-floor fixed-slice replay and decide whether it
  remains diagnostic or becomes a separately frozen validation-cycle candidate.

### Next

- If iterating on Decision 0007, focus on selected-fact and operand completeness
  only after slice targets and stop rules are predeclared.
- Implement the typed-operations target as the next LLM-heavy lane (leveraging the `llm_only_structured_events` design pattern): extract event count, time window, denominator, cluster size, seizure-free duration, temporal anchor, semiology grouping, uncertainty type, and selected evidence ID, then overlay the state-node graph to transparently select the best set of facts for the target scoring policy or clinical clarity.
- If the selective gate replay clears fixed-slice accounting, decide whether to
  freeze a separate validation-cycle candidate or keep the gate diagnostic.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the safety-floor candidate is frozen.

### Backlog

- Explore a multi-agent LLM architecture that decomposes the task into sequential, separately optimized calls for candidate identification, candidate selection, candidate normalization, and clinical verification, with component ownership and ablations explicit under the `llm_only`/`hybrid` ontology.

### Blocked

- Benchmark language and holdout analysis are blocked until the frozen-test plan is followed without post-test tuning.
- Qwen 3.6 full v5 validation ladder remains blocked until strict schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Implemented and generated the predeclared selective safety-floor
  no-call replay over the fixed atlas validation slices:
  `experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.md`,
  `.json`, and `.jsonl`. The replay reports
  `projection_boundary_state_priority_gate_v0`,
  `llm_candidate_sidecar_rescue_gate_v0`, and `combined_selective_gate_v0`
  against `baseline_safety_floor_v2`, with changed-label precision,
  wrong-to-correct, correct-to-wrong, deterministic-correct regressions,
  evidence exactness, source-id validity, and fallback counts. On fixed
  projection slices, projection gate rescues 5/11 and 4/6 Purist misses; on
  fixed candidate-generation slices, the LLM sidecar rescues 6/44 and 6/26; the
  combined gate records 0 deterministic-correct regressions across all 87 slice
  memberships. Treat as validation-cycle diagnostic accounting, not production
  promotion.
- 2026-06-03: Predeclared the selective safety-floor gate design in
  `experiments/gan2026_selective_safety_floor_gate_predeclaration_2026-06-03.md`
  and JSON manifest. The first implementation target is a no-call replay that
  leaves the deterministic safety-floor final policy unchanged while exposing
  ablated projection-boundary-state, LLM-sidecar rescue, and combined gate
  score layers with fixed-slice regression accounting.
- 2026-06-03: Ran the atlas hard-slice no-call diagnostic over saved validation
  artifacts: 87 slice memberships / 55 unique source rows. Candidate-generation
  slices showed 6 saved LLM-candidate sidecar rescues among 8 scorable sidecars
  (44-row broad slice; same 6 on the 26-row unknown/seizure-free boundary
  subset). Projection-arbitration slices showed boundary-state priority
  correcting 9/11 projection memberships where 9 rows had saved graph replay,
  and 6/6 on the unknown/seizure-free/current-vs-historical projection subset.
  Treat as revise/design signal, not promotion. The diagnostic generator now
  emits row-level "would change" tables and marks the post-hoc interpretation
  section as required before any implementation predeclaration.
- 2026-06-03: Predeclared atlas-derived hard slices for the next diagnostic
  experiment and added reusable manifest/report generation in
  `hidden_family_atlas.py`. Fixed slices: candidate-generation rescue (44),
  candidate-generation unknown/seizure-free boundary (26), projection
  arbitration (11), and projection unknown/seizure-free arbitration (6).
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

Implement the predeclared no-call selective-action replay from
`experiments/gan2026_selective_safety_floor_gate_predeclaration_2026-06-03.json`
and report changed-label precision, wrong-to-correct, correct-to-wrong,
deterministic-correct regressions, evidence exactness, and source-id validity by
fixed validation slice.
