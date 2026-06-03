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

The selective safety-floor fixed-slice replay has graduated from pure
diagnostic accounting to a separate frozen validation-cycle candidate seed:
`combined_selective_gate_v0`, with projection-boundary arbitration first and
LLM sidecar rescue second. This is not production promotion. The freeze is only
for a named validation candidate because the fixed slices showed high-precision
rescues, 0 deterministic-correct regressions, exact evidence, and valid source
ids, while remaining narrow, no-call, and validation-derived.
The frozen manifest is
`experiments/gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.md`
with machine-readable JSON alongside it.
The validation750 no-call replay is recorded in
`experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.md`
and `.json`/`.jsonl`: `selective_safety_floor_gate_v0` reaches 708/750
Purist (0.9440) and 715/750 Pragmatic (0.9533), with 21 changed rows, 11
wrong-to-correct, 0 correct-to-wrong, 0 deterministic-correct regressions, and
21/21 changed rows with exact evidence and valid source ids.

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

- Decide whether to write a separate frozen-test audit plan for
  `selective_safety_floor_gate_v0`; do not run locked test from the validation
  manifest.

### Next

- If iterating on Decision 0007, focus on selected-fact and operand completeness
  only after slice targets and stop rules are predeclared.
- Run a validation25 typed-operations smoke for
  `llm_only_typed_operations_reasoner`: event count, time window, denominator,
  cluster size, seizure-free duration, temporal anchor, semiology grouping,
  uncertainty type, and selected evidence ID are now typed outputs, with a
  model-derived state-node graph projection side-car.
- If freezing `selective_safety_floor_gate_v0` for holdout, write a new
  frozen-test audit plan that fixes candidate, source artifacts, gate order,
  scorer, slice definitions, and inspection policy before any locked-test read.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the safety-floor candidate is frozen.

### Backlog

- Explore a multi-agent LLM architecture that decomposes the task into sequential, separately optimized calls for candidate identification, candidate selection, candidate normalization, and clinical verification, with component ownership and ablations explicit under the `llm_only`/`hybrid` ontology.

### Blocked

- Benchmark language and holdout analysis are blocked until the frozen-test plan is followed without post-test tuning.
- Qwen 3.6 full v5 validation ladder remains blocked until strict schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Ran the frozen validation-only no-call replay for
  `selective_safety_floor_gate_v0`:
  `experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.md`,
  `.json`, and `.jsonl`. The candidate improves the safety-floor baseline from
  697/750 to 708/750 Purist and 704/750 to 715/750 Pragmatic, with 21 changed
  rows, 11 wrong-to-correct, 0 correct-to-wrong, 1.0000 changed-label
  precision, 0 deterministic-correct regressions, and 21/21 changed rows with
  exact evidence and valid source ids. The report explicitly calls out row
  15193: `unknown` scores in the same Purist/Pragmatic category as
  `multiple per 13 month`, so that rescue remains a benchmark-format caveat,
  not exact-label normalization.
- 2026-06-03: Implemented the typed-operations LLM-heavy lane scaffold:
  `llm_only_typed_operations_reasoner`, registered in the shared
  `gan2026-llm-experiment` CLI. It uses scoped DSPy `JSONAdapter`, extracts the
  typed operands requested in the work board, validates selected evidence IDs
  and exact evidence, and projects a graph built only from model-extracted
  operation nodes. Targeted tests and prompt-hygiene coverage are in place; no
  live validation smoke has been run yet.
- 2026-06-03: Wrote the frozen `selective_safety_floor_gate_v0`
  validation-cycle manifest:
  `experiments/gan2026_selective_safety_floor_gate_v0_validation_cycle_manifest_2026-06-03.md`
  and `.json`. It freezes candidate name, source artifacts, gate order,
  scorer/repair policy, validation-only inspection policy, required reporting,
  and promote/revise/reject stop rules; locked test remains out of scope.
- 2026-06-03: Interpreted the selective safety-floor fixed-slice replay as
  strong enough to seed a separately frozen validation-cycle candidate, not
  strong enough for production promotion or holdout language.
  `combined_selective_gate_v0` is the candidate seed because individual
  projection and LLM-sidecar gates cleared fixed-slice regression accounting:
  0 deterministic-correct regressions, 1.0000 changed-label precision on the
  target rescue slices, exact changed-row evidence, and valid source ids. Caveat:
  the LLM sidecar still includes a scoring-path convention where `unknown`
  counts Purist-correct against `multiple per 13 month`; preserve that as a
  validation-cycle attribution caveat.
- 2026-06-03: Implemented and generated the predeclared selective safety-floor
  no-call replay over the fixed atlas validation slices:
  `experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.md`,
  `.json`, and `.jsonl`. Projection gate rescues 5/11 and 4/6 Purist misses;
  LLM sidecar rescues 6/44 and 6/26; combined gate has 0 deterministic-correct
  regressions across all 87 slice memberships.
- 2026-06-03: Built the hidden-family atlas and fixed hard-slice surfaces.
  Among 89 Purist misses, first-failure owners were candidate generation (44),
  LLM clinical selection (22), projection (9), operand exposure (8),
  deterministic adapter (3), final projection (2), and schema/parse (1).
- 2026-06-03: Rejected Decision 0007 v1 after validation250 reached 0.8560
  Purist F1 on `final_projected_label` but failed the mechanical-adapter gate
  (180/250 vs >=220), with regressions and incomplete operands.
- 2026-06-03: Ran the hybrid frozen-test audit and validation750 safety-floor
  replay. Holdout: 0.7622 Purist / 0.7867 Pragmatic, 0 deterministic-correct
  regressions. Validation750 safety-floor replay: 697/750 Purist (0.9293),
  704/750 Pragmatic (0.9387), 136/750 fallbacks.

## Immediate Next Step

Choose the next branch of work: write a frozen-test audit plan for
`selective_safety_floor_gate_v0`, or continue with the validation25
typed-operations smoke. Locked test remains blocked until a new frozen-test plan
exists.
