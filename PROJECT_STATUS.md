# Project Status

Last updated: 2026-06-03

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving evidence trails,
component ablations, split discipline, and conservative benchmark language.

## Current Strategy

Keep frozen comparators stable while revising the two predeclared architecture
candidates after their matched validation25 smoke comparison. The live matched
report is
`experiments/gan2026_predeclared_architecture_matched_validation25_comparison_2026-06-03.md`.

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

## Context Links

- Reference map: `docs/research/gan2026_project_history_log_2026-06-02.md`.
- Synthesis: `docs/research/gan2026_full_research_retrospective_2026-06-02.md`.
- Boundary: `experiments/gan2026_hybrid_llm_deterministic_boundary_report_2026-06-02.md`.
- Policy: `docs/decisions/0007-llm-heavy-clinical-selection-deterministic-adapters.md`.

## Active Priorities

1. Repair the `hybrid_parallel_state_candidate_reasoner` source-id provenance
   contract before any validation50 escalation.
2. Revise `llm_heavy_evidence_selection_with_deterministic_adapters` selected
   evidence, operand completeness, and raw parser-label grammar as a Decision
   0007 diagnostic.
3. Preserve attribution language: hybrid for semantic deterministic
   participation; LLM-heavy only for deterministic rendering from
   model-selected facts and operands.

## Work Board

### Now

- Fix hybrid selected-source id normalization/instructions so adjudicator output
  uses valid `det:`, `graph:`, `llm:`, or `synth:` provenance ids.
- Fix the hybrid LLM-candidate temporality enum edge case that caused one
  validation25 schema failure.
- Decide whether source-id repair is format-only enough to rerun validation25
  without changing clinical selection behavior.

### Next

- For LLM-heavy Decision 0007, triage exact-evidence failures, missing operands,
  wrong selected clinical fact/operand rows, and raw parser-label grammar.
- Rerun matched validation25 only after the hybrid provenance fix and LLM-heavy
  targeted contract fixes are explicit.
- Promote neither candidate to validation50 until its smoke gate passes without
  source-trace or selected-evidence defects.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the
  architecture smokes clarify the output contract.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked
  until replication comparability and locked-test discipline permit them.
- Qwen 3.6 full v5 validation ladder remains blocked until strict
  schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Ran live matched validation25 smokes for
  `llm_heavy_evidence_selection_with_deterministic_adapters` and
  `hybrid_parallel_state_candidate_reasoner`, exposed the hybrid candidate
  through the shared CLI, and wrote the matched comparison report. Neither
  candidate earned validation50.
- 2026-06-02: Implemented
  `llm_heavy_evidence_selection_with_deterministic_adapters` scaffolding:
  typed selected fact/evidence/operand DSPy outputs, Decision 0007 mechanical
  adapter score layers, validation25 report gate, and shared CLI exposure.

## Immediate Next Step

Patch the hybrid source-id provenance contract, then rerun validation25 only if
the change is format-only and preserves the matched-row clinical selection
surface.
