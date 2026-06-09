# Gan 2026 Repository Consolidation and Cleanup Report

Date: 2026-06-07
Author: Claude
Status: Completed cleanup record with Phase G sign-off

---

## 1. Executive Summary

Following the completion of the rapid-iteration research phase, the codebase has been audited and consolidated around the canonical architecture surface. Across **5 sequential batches**, we removed superseded runners, exclusive components, coupled analyzers, and mirrored unit test suites representing over 75 files and ~1.2 MB of redundant code.

A complete dependency audit was performed, and all necessary shared infrastructure components were preserved, cleaned, or relocated. The high-risk removal portion of the cleanup is complete, and follow-up Phase F framework consolidation now provides one shared runner/CLI surface plus four official cluster-level analyzer modules.

All remaining **997 unit and integration tests** in the Python test suite pass successfully after Phase G sign-off corrections.

---

## 2. Canonical Architecture Selections

As resolved in the Canonical-Runner Selection decision record, the following representative runners were retained:

| Architecture | Canonical Runner | Description / Role |
| --- | --- | --- |
| **Deterministic** | `pipeline_v1.py` (`Gan2026PipelineV1`) | Pure rule-based extraction baseline. |
| **Fully LLM (One-shot)** | `llm/llm_only_direct_labeler.py` | Baseline for direct single-pass classification. |
| **Fully LLM (Multi-step)** | `llm/hybrid_structured_events.py` | Base for multi-step structured extraction chains. |
| **Hybrid** | `hybrid/reset_clinical_assessment_pipeline.py` | Active hybrid/reset focus composing LLM Select and rule-based Normalize -> Project stages. |

Superseded experimental runners and modules were retired and cleaned up. Historical run records and research artifacts remain as provenance, but deleted runner families are no longer active execution or Observatory replay paths.

---

## 3. Detailed Execution Breakdown

The consolidation was executed in 5 distinct batches, with the test suite verified after each batch before commit:

### Batch 1: `staged_hybrid_assembly` (v0 Lineage)
* **Goal**: Clean up the v0 staged hybrid assembly runner, its coupled analyzers, and its v0-specific components.
* **Preservation/Relocation**:
  - Relocated shared infrastructure components `source_trace.py` and `suspicious_state_policy.py` from `components/` to `artifact_analysis/` and updated their import statements in `suspicious_selected_state_routing.py`.
* **Deletions**:
  - Runner: `staged_hybrid_assembly.py` and test `test_gan2026_staged_hybrid_assembly.py`.
  - Analyzers: `change_only_det_state_family_experiment.py`, `selected_state_union_replay.py`, and test `test_gan2026_selected_state_union_replay.py`.
  - Components: 21 v0-exclusive component files under `components/` and their corresponding test files in `tests/`.
* **Outcome**: Verified green and committed under commit `cbdee19`.

### Batch 2: `hybrid_rules_candidates_llm_adjudicator` (Adjudicator Lineage)
* **Goal**: Clean up the hybrid rules-candidates LLM adjudicator.
* **Preservation/Relocation**:
  - Ported synthetic hard case loaders and constants (`load_synthetic_hard_cases`, `synthetic_records_from_cases`, `attach_hard_case_metadata`, and `SYNTHETIC_*`) from `synthetic_hard_case_component_stress.py` to a new shared location `experiments/synthetic_hard_cases.py`.
  - Retargeted downstream dependents (`boundary_state_graph_replay.py`, `boundary_state_graph_builder.py`, `state_graph_diagnostics.py`) to import from the new home.
* **Deletions**:
  - Unwired CLI specs and observatory registrations.
  - Removed runner `hybrid_rules_candidates_llm_adjudicator.py`, `hybrid_adjudicator_parser.py`, `hybrid_adjudicator_report.py`, `saturated_surface_evaluation.py`, and `architecture_component_ablation.py`.
  - Deleted mirrored tests: `test_gan2026_hybrid_rules_candidates_llm_adjudicator.py`, `test_gan2026_saturated_surface_evaluation.py`, `test_gan2026_synthetic_hard_case_component_stress.py`.
* **Outcome**: Verified green and committed under commit `a916be6`.

### Batch 3: Non-canonical `llm_only_*` Modules
* **Goal**: Remove non-canonical LLM-only experiments with no unified runner.
* **Deletions**:
  - Unwired 6 CLI-registered non-canonical LLM runners from registry and CLI spec.
  - Deleted 8 non-canonical LLM modules: `llm_only_claim_table_selector.py`, `claim_table_parser.py`, `claim_table_report.py`, `claim_table_component_ablation.py`, `llm_only_minimal_evidence_selector.py`, `llm_only_rich_selected_state_reasoner.py`, `llm_only_simplified_selected_state_reasoner.py`, `llm_only_sparse_operands_selected_state_reasoner.py`, `llm_only_typed_adapter_reasoner.py`, `llm_only_typed_operations_reasoner.py`, and `hybrid_structured_events_repair_ablation.py`.
  - Deleted all mirrored test files.
* **Outcome**: Verified green and committed under commit `9777c8c`.

### Batch 4: `staged_assembly_v1` (v1 Lineage)
* **Goal**: Clean up the v1 staged assembly lineage.
* **Deletions**:
  - Removed runner `staged_assembly_v1.py` and its exclusive unit test.
  - Deleted 26 exclusive v1 component files under `components/` and their mirrored tests.
* **Outcome**: Verified green and committed under commit `c205136`.

### Batch 5: `hybrid_parallel_state_candidate_reasoner` (Parallel Hybrid Lineage)
* **Goal**: Clean up the hybrid parallel state candidate reasoner lineage.
* **Preservation/Relocation**:
  - Relocated the `classify_hidden_families` classification helper logic to `labels.py` so that kept analyzers (`h1_hidden_family_slice_aggregates.py` and `rq1_rq2_control_panels.py`) can import it.
  - Inlined RQ10 default json and jsonl paths as literal Path objects in `rq9_abstention_review_predeclaration.py` to sever dependencies on the deleted `rq10_gold_scorer_ambiguity_audit.py`.
* **Deletions**:
  - Unwired runner from `FAMILY_SHORT_LABELS` in `api.py` and CLI spec in `llm_pipeline_cli.py`.
  - Deleted runner `hybrid_parallel_state_candidate_reasoner.py` and 12 string-coupled analyzers from `artifact_analysis/`.
  - Deleted 10 mirrored tests.
* **Outcome**: Verified green and committed under commit `bc3341f`.

---

## 4. Phase F Framework Consolidation

Phase F is now complete as a shared infrastructure layer:

- **Pipeline runners / CLI**: `src/clinical_extraction/tasks/seizure_frequency/gan2026/runner.py` exposes the unified runner/configuration surface for deterministic, hybrid, `llm_only_direct_labeler`, and `hybrid_structured_events` executions. The single CLI registry delegates through this surface rather than keeping the retired standalone-runner registry pattern.
- **Hybrid/reset metadata boundary**: `hybrid/reset_clinical_assessment_pipeline.py` reuses the unified stage builder but preserves the canonical reset artifact identity (`reset_clinical_assessment_pipeline`) and reset-specific claim boundary.
- **Reporting / artifact analysis**: `artifact_analysis/__init__.py` exposes the official Phase F analyzer registry. The four cluster-level modules are:
  - `scoped_ablation_analyzer.py` for the ablation cluster.
  - `boundary_diagnostic.py` for boundary/seizure-free diagnostics.
  - `candidate_state_matrix.py` for candidate/state comparisons.
  - `projection_scoring.py` for projection/render/scoring/routing/decision summaries.
- Remaining `artifact_analysis/` modules are retained as source-specific producers, narrow diagnostics, or historical-read helpers. They are no longer the official cluster-level API for new report work.

The consolidated analyzer registry replaces the 32 cluster-file memberships identified in the Phase A survey for the four Phase F target clusters (ablation 8, boundary/seizure-free 8, candidate/state 11, projection/render/scoring 5) without changing scoring policy.

---

## 5. Phase G Verification And Sign-Off

### Automated Verification
A final execution of the Python test suite confirms that the cleanup has left the backend package in a healthy, green state:

```powershell
pytest tests/
```
**Results**:
- **Collected**: 997 items
- **Passed**: 997 passed
- **Errors/Failures**: 0

Focused Ruff verification over the touched Phase F/G Python files also passes.
Whole-repo Ruff still reports pre-existing lint in scratch files and older
retained analyzers/tests that were outside this cleanup batch.

### Observatory Registry Sign-Off

`/pipeline-families` now exposes exactly:

- canonical families: `rules_only`, `llm_only_direct_labeler`,
  `hybrid_structured_events`, `reset_clinical_assessment_pipeline`;
- retained comparators, when backed by registry rows:
  `dspy_final_selection_adjudicator`,
  `hybrid_clinical_frequency_state_graph`, `llm_first_direct_extractor`,
  `llm_heavy_clinical_frequency_reasoner`,
  `llm_heavy_evidence_selection_with_deterministic_adapters`,
  `llm_replacement_postprocessing_ablation`, and `llm_structured_events`.

Deleted and unreviewed historical registry families remain queryable through
`/registry`, but do not repopulate active pipeline selectors.

### Closing Accounting

- Phase E removal batches deleted `159` tracked files and reduced the tree by a
  net `56,476` lines.
- Phase F replaced `32` surveyed overlap-cluster memberships with four
  official cluster-level analyzers: `scoped_ablation_analyzer`,
  `boundary_diagnostic`, `candidate_state_matrix`, and `projection_scoring`.
- The surviving DRY framework is `gan2026.runner` for pipeline/CLI
  configuration plus the Phase F analyzer registry in
  `artifact_analysis/__init__.py`.

### Follow-Up Corrections
An audit after the initial cleanup report found and fixed several sign-off gaps:

- Removed a stale `pyproject.toml` console script that pointed at the deleted `selective_safety_floor_gate_replay.py` module.
- Filtered retired runner families out of active Observatory `/pipeline-families` and frontend run-selection/replay surfaces while preserving historical registry rows.
- Tightened Observatory backend filtering so only canonical families and
  explicitly retained comparators can appear in `/pipeline-families`.
- Pruned frontend replay adapters and tests that still treated deleted runner families as supported.
- Updated `PROJECT_STATUS.md` and this report to record Phase F completion and the new analyzer registry boundary.

### Repository Cleanliness
* Follow-up corrections are intentionally left as the current working-tree changes until reviewed and committed.
* The original lineage-removal batches used git-tracked deletions so file history is preserved.
