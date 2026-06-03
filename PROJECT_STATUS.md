# Project Status

Last updated: 2026-06-03

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving evidence trails,
component ablations, split discipline, and conservative benchmark language.

## Current Strategy

The leading development lane is hybrid deterministic safety-floor architecture
work, not an LLM-first or holdout claim. Full validation750 no-call replay of
`hybrid_parallel_state_candidate_reasoner` reaches 697/750 Purist (0.9293) and
704/750 Pragmatic (0.9387), with 750/750 exact selected evidence, 750/750 valid
source ids, 0 deterministic-correct regressions, and 136/750 safety-floor
fallbacks.

Candidate promotion now has a durable component evidence contract:
`docs/design/component_evidence_attribution_architecture.md`, Decision 0008
`docs/decisions/0008-component-evidence-contract-for-candidate-promotion.md`,
and runbook `docs/runbooks/gan2026_component_evidence_audit.md`. Future
promotion, LLM-superiority, and holdout-readiness claims must answer the
clinical subproblem/component/evidence/regression/distribution questions before
broader validation or locked-test movement.

`selective_safety_floor_gate_v0` is a frozen validation-cycle candidate seed,
not production promotion. Validation750 no-call replay reaches 708/750 Purist
(0.9440) and 715/750 Pragmatic (0.9533), with 21 changed rows, 11
wrong-to-correct, 0 correct-to-wrong, 0 deterministic-correct regressions, and
21/21 changed rows with exact evidence and valid source ids. The validation
manifest remains validation-only; locked test requires
`docs/research/gan2026_selective_safety_floor_gate_v0_frozen_test_audit_plan_2026-06-03.md`.
Frozen-test first readout is now recorded in
`experiments/gan2026_selective_safety_floor_gate_v0_test450_frozen_audit_first_readout_2026-06-03.md`
with `.json`/`.jsonl` and frozen-test manifest
`experiments/gan2026_selective_safety_floor_gate_v0_frozen_test_audit_manifest_2026-06-03.json`.
On test450, `selective_safety_floor_gate_v0` improves the safety-floor baseline
from 343/450 to 351/450 Purist and 354/450 to 361/450 Pragmatic, with 14
changed rows, 8 wrong-to-correct, 0 correct-to-wrong, 0 deterministic-correct
regressions, and 14/14 changed rows with exact evidence and valid source ids.
This is a valid frozen holdout first readout, but still hybrid deterministic
safety-floor evidence, not LLM-first, production-policy, benchmark-comparable,
or tuning evidence.
Post-hoc component-evidence interpretation is recorded in
`experiments/gan2026_selective_safety_floor_gate_v0_component_evidence_audit_2026-06-03.md`:
the frozen-test gain is attribution-valid for a hybrid selective-action audit,
with sidecar gains separated from deterministic projection and safety-floor
fallback, but residual holdout first-failure ownership remains an
instrumentation gap.

Attribution caveat: this is a hybrid deterministic-safety-floor development
result, not an LLM-first result and not a benchmark or holdout claim. Decision
0007 remains the primary LLM-heavy design lane, but v1 validation250 was
rejected. The `llm_only_typed_operations_reasoner` validation25 repair pass
remains revise-only but is cleaner after source-checked evidence-copy repair,
selected-operation graph projection repair, and a 4800-token default budget.
The max4800 live smoke in
`experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.md`
had no truncation warnings, 25/25 structured records, 22/25 selected evidence
valid, 25/25 selected-evidence arithmetic Purist, and 23/25 typed-operation
graph Purist. A no-call replay after generalized evidence-artifact cleanup and
graph-label precedence repair is recorded in
`experiments/gan2026_llm_only_typed_operations_reasoner_validation25_max4800_no_call_replay_2026-06-03.md`:
25/25 selected evidence valid, 25/25 typed-operation graph Purist, and 25/25
typed-operation graph Pragmatic after selected labels and complete operands
were made to outrank loose raw-phrase repair. This is still a validation25
saved-output replay, not promotion evidence. Validation50 live escalation is
recorded in
`experiments/gan2026_llm_only_typed_operations_reasoner_validation50_gpt41mini_v0_contractfix_max4800_2026-06-03.md`:
49/50 structured records, 48/50 selected evidence valid, 47/50
selected-evidence arithmetic Purist, and 47/50 typed-operation graph Purist.
Interpretation changed after review: treat this as evidence that the 4800-token
budget is too tight for the current schema depth, not as a reason to patch row
103 locally. Short-term plan is performance-first: increase max_tokens to 10000,
run validation250, assess performance, then scale to validation750 with
comprehensive schema/error tracking before token/schema-efficiency ablations.

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
- Before promoting a candidate or claiming LLM superiority, apply Decision 0008:
  component evidence matrix, exact changed-row evidence, LLM delta accounting,
  and deterministic-correct regression accounting are required.

## Active Priorities

1. Preserve attribution language for the achieved result: hybrid
   deterministic-safety-floor, validation development only.
2. If running locked test, follow the frozen-test audit plan exactly before any
   holdout execution or row-level inspection.
3. Use the hidden-family/first-failure atlas to target candidate-generation,
   projection, and LLM clinical-selection hard slices before any broad rerun.
4. Keep Decision 0007 alive as the LLM-heavy lane, but do not escalate v1 until
   selected-fact and operand failures have a targeted validation-cycle plan.
5. Use Decision 0008 and the component evidence audit runbook to answer the
   critical research questions for each candidate before promotion.

## Work Board

### Now

- Run `llm_only_typed_operations_reasoner` validation250 live with
  `max_tokens=10000`, using the current schema and prompt unchanged except for
  the larger completion budget. Assess performance first; do not patch row 103
  or other validation50 tails before this run.

### Next

- If validation250 is promising, run validation750 with comprehensive evaluation:
  schema/call tracking, exact-evidence tracking, raw/format/arithmetic/graph
  attribution layers, row-level error analysis, and failure-family summaries.
- After validation750, evaluate the cost/benefit of the current typed schema
  depth and 10000-token budget. Then run ablations that remove or simplify
  schema pieces until performance/token efficiency is better balanced.
- Keep local-LLM transfer in mind for the ablation phase: smaller local models
  are likely slower and more fragile under excessive schema complexity, so
  schema/token efficiency should become a named objective after the
  performance-first validation250/750 readout.
- If doing row-level review of the `selective_safety_floor_gate_v0` holdout,
  treat it only as post-hoc final-evaluation analysis; any fix must start a new
  validation-cycle candidate.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the safety-floor candidate is frozen.

### Backlog

- Explore a multi-agent LLM architecture that decomposes the task into sequential, separately optimized calls for candidate identification, candidate selection, candidate normalization, and clinical verification, with component ownership and ablations explicit under the `llm_only`/`hybrid` ontology.

### Blocked

- Benchmark-comparable language remains blocked; the
  `selective_safety_floor_gate_v0` holdout first readout is a local frozen
  generalization audit only.
- Qwen 3.6 full v5 validation ladder remains blocked until strict schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Repaired `llm_only_typed_operations_reasoner` evidence-copy and
  graph-projection sidecars, raised the typed-operations default max token
  budget to 4800, and reran validation25 live with no truncation warnings.
  Result:
  `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.md`
  reached 25/25 structured, 22/25 selected evidence valid, 25/25
  selected-evidence arithmetic Purist, and 23/25 typed-operation graph Purist.
  Decision: revise, do not escalate.
- 2026-06-03: Generalized semantically-neutral evidence artifact cleanup for
  inequality/control-character copy artifacts and source Gan note mojibake, fixed
  typed-operation graph label precedence so bad model-normalized labels cannot
  outrank parseable raw phrases or complete operands, fixed row 598's
  `1 per eight months` window rendering miss by prioritizing selected labels and
  complete operands before loose raw-phrase repair, and reclassified
  `typed_operation_graph_projection` as deterministic semantic graph projection.
  Saved-output replay:
  `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_max4800_no_call_replay_2026-06-03.md`
  reached 25/25 selected evidence valid, 25/25 typed-operation graph Purist, and
  25/25 typed-operation graph Pragmatic. Decision: validation25 cleanup is
  complete; validation50 needs predeclared stop rules before any run.
- 2026-06-03: Ran `llm_only_typed_operations_reasoner` validation50 live at
  max_tokens=4800 with predeclared stop rules. Result:
  `experiments/gan2026_llm_only_typed_operations_reasoner_validation50_gpt41mini_v0_contractfix_max4800_2026-06-03.md`
  reached 49/50 structured records, 48/50 selected evidence valid, 47/50
  selected-evidence arithmetic Purist, and 47/50 typed-operation graph Purist.
  Follow-up interpretation: row 103 likely reflects insufficient completion
  budget for the current schema depth, so the next step is not a local schema
  repair. Increase max_tokens to 10000 and run validation250, then scale to
  validation750 with full diagnostics if performance warrants it.
- 2026-06-03: Ran `llm_only_typed_operations_reasoner` validation25 live smoke.
  Initial v0: 22/25 structured records, 3 parse/schema failures, 16/25 selected
  evidence valid, 19/25 typed-graph Purist, and one raw-correct-to-graph-wrong
  regression. Added v0 contract-fix prompt/output constraints and raised the
  default token budget to 2400; contract-fix run improved to 24/25 structured
  and 0 raw-correct-to-graph-wrong regressions, but selected evidence remained
  17/25 valid and typed-graph Purist was 18/25. Decision: revise, do not
  escalate.
- 2026-06-03: Applied the component evidence audit contract to the
  `selective_safety_floor_gate_v0` validation/test artifacts. The report
  preserves the hybrid deterministic-safety-floor attribution, separates
  projection from LLM sidecar gains, confirms 14/14 frozen-test changed rows
  with exact evidence and valid source ids, and records first-failure ownership
  for residual holdout misses as an instrumentation gap.
- 2026-06-03: Added the component evidence attribution architecture, Decision
  0008 promotion contract, and Gan 2026 component evidence audit runbook. Also
  created local Codex skills for repeatable component-evidence and LLM-delta
  audits.
- 2026-06-03: Ran the no-call frozen-test first readout for
  `selective_safety_floor_gate_v0`: 351/450 Purist and 361/450 Pragmatic versus
  baseline 343/450 and 354/450, with 14 changed rows, 8 wrong-to-correct, 0
  correct-to-wrong, 0 deterministic-correct regressions, and 14/14 changed rows
  with exact evidence and valid source ids. The Markdown first readout omits
  row-level locked-test details.
- 2026-06-03: Decided that `selective_safety_floor_gate_v0` needs its own
  frozen-test audit plan before any holdout use; no locked test was run.
- 2026-06-03: Ran the frozen validation-only no-call replay for
  `selective_safety_floor_gate_v0`: 708/750 Purist, 715/750 Pragmatic, 21
  changed rows, 11 wrong-to-correct, 0 correct-to-wrong, and 21/21 changed rows
  with exact evidence and valid source ids.
- 2026-06-03: Implemented the typed-operations LLM-heavy lane scaffold:
  `llm_only_typed_operations_reasoner`; no live validation smoke has been run
  yet.
- 2026-06-03: Wrote the frozen `selective_safety_floor_gate_v0` validation-cycle
  manifest; locked test remains out of scope.
- 2026-06-03: Interpreted selective safety-floor fixed-slice replay as strong
  enough to seed a separately frozen validation-cycle candidate, not strong
  enough for production promotion or holdout language.
- 2026-06-03: Implemented and generated the predeclared selective safety-floor
  no-call replay over fixed atlas validation slices; combined gate has 0
  deterministic-correct regressions across all 87 slice memberships.
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

Run `llm_only_typed_operations_reasoner` validation250 with max_tokens=10000 and
record raw, format-only, selected-evidence arithmetic, typed-graph projection,
schema/call, and evidence-exactness metrics. Do not tune from locked-test
row-level behavior.
