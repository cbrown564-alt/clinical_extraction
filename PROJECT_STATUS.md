# Project Status

Last updated: 2026-06-03

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving evidence trails,
component ablations, split discipline, and conservative benchmark language.

## Current Strategy

Keep frozen comparators stable while revising the predeclared architecture
candidates after their matched validation25 smoke comparison. The hybrid
source-id and temporality contract replay is
`experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_contract_fix_replay_2026-06-03.md`;
the matched comparison baseline remains
`experiments/gan2026_predeclared_architecture_matched_validation25_comparison_2026-06-03.md`.
The LLM-heavy Decision 0007 v1 smoke is
`experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_2026-06-03.md`.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
  Validation is the development surface; locked test is not for row-level
  tuning.
- `rules_only_v1` remains the frozen transparent comparator. Do not tune it
  from locked-test audit behavior.
- Hybrid v0.2 `cluster_diary_candidate_recall` remains a frozen comparator-only
  generalization audit result.
- Treat saturated aggregate validation scores as low-information. Prefer
  hard-slice, rescue/regression, evidence-validity, component-stress, and
  frozen-audit evidence.
- Keep semantic repair, graph projection, scorer normalization, deterministic
  adapters, and production policy separately named and ablated.
- Use typed DSPy outputs with scoped `JSONAdapter` for new LLM/DSPy architectures.

## Active Priorities

1. Decide the LLM-heavy Decision 0007 next repair: special-character evidence
   exactness on rows `10`, `40`, `446` and cluster-cadence mechanical-adapter
   regressions on rows `187`, `190`.
2. Triage the remaining hybrid selected-evidence exactness defect before
   treating validation50 as cleanly earned, despite the repaired source-trace
   gate.
3. Preserve attribution language: hybrid for semantic deterministic
   participation; LLM-heavy only for deterministic rendering from
   model-selected facts and operands.

## Work Board

### Now

- For LLM-heavy Decision 0007, review whether the primary layer should be raw
  model parser labels after v1 reached 25/25 raw Purist, or whether the
  mechanical adapter needs a cluster-cadence rendering fix before another smoke.
- Review the one remaining hybrid selected-evidence exactness failure from the
  contract-fix replay before validation50 escalation.

### Next

- Rerun matched validation25 only after LLM-heavy targeted contract fixes are
  explicit.
- Promote neither candidate to validation50 until its smoke gate passes without
  selected-evidence defects.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the
  architecture smokes clarify the output contract.

### Blocked

- Benchmark language and holdout analysis are blocked until replication
  comparability and locked-test discipline permit them.
- Qwen 3.6 full v5 validation ladder remains blocked until strict
  schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Ran live LLM-heavy Decision 0007 v1 validation25 smoke: 25/25
  structured, 0 parse/call
  failures, 25/25 raw parser labels scorable and Purist. Gate still rejects:
  selected evidence exact is 22/25 and the mechanical adapter regresses
  raw-correct cluster-cadence rows `187`, `190`.
- 2026-06-03: Implemented the LLM-heavy Decision 0007 v1 prompt/schema
  contract: exact Unicode evidence copying, clinical-kind/operand consistency,
  vague-count operands, parser-ready raw-label grammar, and v1 artifact paths.
- 2026-06-03: Completed LLM-heavy Decision 0007 validation25 contract triage.
  It identified exact-evidence escaping, operand-kind inconsistency,
  cluster-axis/vague-count issues, and 0/25 parser-ready raw labels.
- 2026-06-03: Repaired `hybrid_parallel_state_candidate_reasoner`
  source-id provenance and LLM-candidate `future` temporality schema handling.
  Replay now has 25/25 source ids valid, 25/25 structured LLM-candidate records,
  0 parse/schema failures, 24/25 selected evidence exact, and
  `promote_to_50`, pending evidence review.
- 2026-06-03: Ran live matched validation25 smokes for
  `llm_heavy_evidence_selection_with_deterministic_adapters` and
  `hybrid_parallel_state_candidate_reasoner`; neither earned validation50.

## Immediate Next Step

Review the LLM-heavy primary-layer contract: preserve raw parser-label success
while fixing evidence escaping and cluster-cadence adapter regressions before
any matched comparison or validation50 escalation.
