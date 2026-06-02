# Project Status

Last updated: 2026-06-02

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving transparent evidence
trails, component ablations, split discipline, and conservative benchmark
language.

## Current Strategy

Keep frozen comparators stable, and spend the next development cycle on the two
predeclared optimal architecture candidates:

- `hybrid_parallel_state_candidate_reasoner`
- `llm_heavy_evidence_selection_with_deterministic_adapters`

Both are specified in
`docs/design/gan2026_optimal_architectures_2026-06-02.md`.

Hybrid tests candidate-recall and graph-representability rescue. LLM-heavy
tests Decision 0007: model-owned clinical selection with deterministic
mechanical adapters.

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
- Use typed DSPy outputs with scoped `JSONAdapter` for new LLM/DSPy
  architectures unless a run is explicitly an opaque-string comparator.

## Context Links

- The full research history and reference map now live in
  `docs/research/gan2026_project_history_log_2026-06-02.md`.
- Current synthesis: `docs/research/gan2026_full_research_retrospective_2026-06-02.md`,
  `experiments/gan2026_hybrid_llm_deterministic_boundary_report_2026-06-02.md`,
  `docs/decisions/0007-llm-heavy-clinical-selection-deterministic-adapters.md`.

## Active Priorities

1. Run a matched validation25 comparison of the two predeclared architecture
   candidates before any broad validation run.
2. Measure candidate-recall rescue, graph-representability rescue,
   deterministic-correct regressions, selected-evidence exactness, selected
   operand completeness, adapter gains, and adapter regressions.
3. Preserve attribution language: hybrid for semantic deterministic
   participation; LLM-heavy only for deterministic rendering from
   model-selected facts and operands.

## Work Board

### Now

- Implement the validation25 smoke for
  `hybrid_parallel_state_candidate_reasoner`, including deterministic-top,
  state-graph projection, LLM-candidate, raw adjudicator, and adapter layers.
- Implement the validation25 smoke for
  `llm_heavy_evidence_selection_with_deterministic_adapters`, including typed
  selected fact/evidence/operand output and mechanical adapter layers.
- Add the shared comparison report that evaluates both smokes on matched rows
  with rescue/regression and attribution metrics.

### Next

- Review the Workstream B rule-ownership matrix before changing any adapter,
  prompt instruction, projection rule, or deterministic fallback.
- If the LLM-heavy smoke fails, triage in this order: wrong selected clinical
  fact, exact-evidence failure, missing operands, adapter rendering bug, raw
  parser-label grammar.
- If the hybrid smoke fails, triage in this order: deterministic recall miss
  not rescued, graph representability not used, LLM candidate evidence
  non-exact, deterministic-correct regression, gate/adjudicator overreach.
- After the matched validation25 report, decide whether either candidate earns
  validation50, needs a targeted hard-slice panel, or should be rejected.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the
  architecture smokes clarify the output contract.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability is explicit and locked-test discipline
  permits.
- Qwen 3.6 full v5 claim-table validation ladder remains blocked until
  `ollama_chat/qwen3.6:35b` produces strict schema-compatible v5 output, or a
  named Qwen schema-repair ablation is designed and reported separately.

### Backlog

- Consolidate remaining saved-output replay helpers into artifact-analysis
  modules.
- Extend saturated-surface tooling over reviewed hard panels.
- Compare minimal evidence selector against claim-table v5 after local-model
  transfer is unblocked.
- Revisit claim-table v5 only as a comparator, not as the active architecture.

## Immediate Next Step

Start with `hybrid_parallel_state_candidate_reasoner`: scaffold the matched
validation25 smoke so it can emit deterministic-top, state-graph projection,
LLM-candidate, raw adjudicator, adapted adjudicator, rescue, and regression
layers on the same rows.
