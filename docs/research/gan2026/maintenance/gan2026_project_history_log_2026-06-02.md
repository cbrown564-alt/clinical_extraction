# Gan 2026 Project History Log

Date: 2026-06-02

This log holds historical context that used to bloat `PROJECT_STATUS.md`.
`PROJECT_STATUS.md` should stay short and action-oriented; this document is the
place to preserve milestone history, important caveats, and reference links.

This is a development-history document, not a benchmark claim. Validation
results are development evidence under `gan2026_split_v1`; locked-test results
are frozen-audit context only unless an evaluation protocol says otherwise.

## Current Reference Map

Core control and design docs:

- `PROJECT_STATUS.md`
- `docs/design/gan2026_split_protocol.md`
- `docs/design/gan2026_saturated_validation_protocol.md`
- `docs/design/data_contract.md`
- `docs/research/contribution_thesis.md`
- `docs/design/model_strategy.md`
- `experiments/registry.jsonl`
- `experiments/RUN_INDEX.md`

Current architecture and attribution docs:

- `docs/design/gan2026_optimal_architectures_2026-06-02.md`
- `docs/decisions/0005-benchmark-format-rules-vs-llm-clinical-reasoning.md`
- `docs/decisions/0006-validation25-llm-owned-selected-evidence-rendering-smoke.md`
- `docs/decisions/0007-llm-heavy-clinical-selection-deterministic-adapters.md`
- `experiments/gan2026_hybrid_llm_deterministic_boundary_report_2026-06-02.md`
- `experiments/gan2026_rule_ownership_audit_2026-06-02.md`
- `experiments/gan2026_rule_ownership_matrix_2026-06-02.csv`

Synthesis and retrospective docs:

- ``
- `experiments/gan2026_generalization_gap_research_report_2026-06-02.md`
- ``
- ``

State-graph and projection docs:

- `experiments/gan2026_clinical_frequency_state_graph_protocol_2026-06-02.md`
- `experiments/gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02.md`
- `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.md`
- `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.md`
- `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.md`

LLM-heavy and typed-adapter docs:

- `experiments/gan2026_llm_heavy_extraction_protocol_2026-06-02.md`
- `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.md`
- `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.md`
- `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.md`
- `experiments/gan2026_dspy_adapter_architecture_report_2026-06-02.md`
- `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_gpt41mini_v0_diagnostic_2026-06-02.md`

Prior comparator docs:

- `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`
- `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`
- `experiments/gan2026_hybrid_adjudicator_v02_saturated_surface_evaluation_plan_2026-06-01.md`

Local model transfer docs:

- `docs/runbooks/windows_local_ollama.md`
- ``

## Durable Findings

- `rules_only_v1` is the frozen transparent comparator. It reached 0.9293
  Purist and 0.9387 Pragmatic on validation, then dropped to about 0.7600
  Purist and 0.7867 Pragmatic on locked test. That gap is the central
  generalization warning.
- Structured-events v0.5 reached 0.9000 validation Purist only as
  repair-heavy hybrid behavior. Clean LLM-owned final-label performance
  remained well below target.
- Claim-table v4/v5 produced useful transparent intermediate representations
  and complementarity with deterministic V1, but validation-prefix optimism did
  not survive broader validation or locked-test audit.
- Hybrid v0.2 showed that deterministic candidate selection can become a hard
  recall ceiling. The LLM cannot recover a correct fact it never sees.
- State-graph diagnostics are the strongest current research substrate because
  they separate coverage, projection, boundary-state construction, invariance,
  and arbitration.
- LLM-heavy v1/v2 variants showed that models can often select useful evidence
  but still fail on parser grammar, arithmetic rendering, cluster syntax,
  compact intervals, and benchmark conventions.
- Decision 0007 reframed the LLM-heavy boundary: the model owns clinical
  selection; deterministic adapters may own mechanical and benchmark-facing
  rendering from model-selected facts and operands.
- Typed DSPy outputs with scoped `JSONAdapter` should be the default substrate
  for new LLM/DSPy architectures unless a run is explicitly preserving an
  opaque-string comparator.

## 2026-06-02 Milestones

- Added the two predeclared optimal architecture candidates:
  `hybrid_parallel_state_candidate_reasoner` and
  `llm_heavy_evidence_selection_with_deterministic_adapters`.
- Completed the rule-ownership audit and added Decision 0007. The audit
  recorded deterministic mechanical adapters separately from model-owned
  clinical selection and hybrid semantic replacement.
- Added the hybrid LLM/deterministic boundary report. It records the
  deterministic-candidate-recall ceiling in the hybrid adjudicator line, the
  opposite LLM-heavy overreach into arbitrary/mechanical rule decisions, and
  typed DSPy `JSONAdapter` as the default for new LLM/DSPy architectures.
- Scaffolded and ran `llm_only_typed_adapter_reasoner_v0`. Validation25 and
  validation50 diagnostics confirmed strong adapter mechanics but rejected the
  architecture for promotion because raw model-owned performance and selected
  evidence/operand completeness were not sufficient.
- Ran `llm_heavy_clinical_frequency_reasoner_v2` and `v2_compact` validation25
  smokes. Compact fixed truncation/schema failures, but both were rejected for
  escalation under the old Decision 0006 gate.
- Ran saved-output LLM-replacement post-processing ablations on the LLM-heavy
  v1 validation250 artifact. Selected-evidence arithmetic was the dominant
  deterministic rescue layer, confirming the need for explicit attribution.
- Completed graph-gated `month_bucket_duration_selection_graph_gated_v2`.
  It preserved 18/18 enriched duration corrections and left 0/232 broad
  regression label changes, but remains validation-only diagnostic evidence.
- Completed the state-graph coverage, projection, boundary-state, unknown8
  replay, and seizure-free duration diagnostic cycle. Coverage and node
  construction are promising; projection and arbitration remain the bottleneck.
- Added the full research retrospective and rendered it as HTML/PDF.
- Extended named repair-mode metadata across claim-table, hybrid adjudicator,
  repair-family ablation, and component-ablation artifacts.
- Consolidated saved-output replay and artifact-ablation helpers into
  `gan2026/artifact_analysis`.
- Completed the hybrid v0.2 `cluster_diary_candidate_recall` frozen
  generalization audit and moved development away from final-label gate tuning.

## 2026-06-01 Milestones

- Completed the v0.2 hybrid adjudicator development cycle through
  validation25/50/250, saturated-surface analysis, synthetic hard-case stress,
  row-level failure review, and named candidate-recall revision.
- Added intermediate-schema synthesis, saturated-validation workflow,
  cache-first LLM experiment CLI, cross-architecture component-ablation
  tooling, package-organization cleanup, and restored green Ruff, mypy, and
  full pytest after schema-repair and ownership-boundary work.
- Ran the first hosted simplified-contract baseline,
  `llm_only_minimal_evidence_selector_v0`, on GPT-4.1 mini validation25. The
  run showed excellent schema/evidence behavior but weak scorer-facing
  parser-readiness.
- Added minimal evidence-selector error analysis. The main failure family was
  scorer-facing normalization, not evidence selection.
- Completed the Qwen 3.6/Ollama setup lane. Endpoint routing is unblocked, but
  full v5 Qwen remains blocked on strict JSON/schema adherence or a named
  schema-repair ablation.
- Rejected LLM-only claim-table selector v4 for holdout after full validation
  fell to 528/750 clean Purist despite stronger prefix results.
- Designed and implemented claim-table v5 and hybrid rules-candidates LLM
  adjudicator v0.2.
- Completed hybrid rules-candidates LLM adjudicator v0.1 ladder and
  full-validation review; it cleared 0.9000 in schema replay but regressed too
  many deterministic-correct rows to freeze.
- Finished the codebase review follow-up with ownership splits across
  deterministic extraction, selected-evidence derivation, LLM/hybrid
  parser/report modules, artifact IO, run metadata, registry reporting, and Gan
  package organization.
