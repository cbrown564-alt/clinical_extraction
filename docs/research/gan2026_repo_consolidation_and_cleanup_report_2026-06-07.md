# Gan 2026 Repository Consolidation and Cleanup Report

Date: 2026-06-07
Author: Claude
Status: Completed / Durable Record

---

## 1. Executive Summary

Following the completion of the rapid-iteration research phase, the codebase has been audited and consolidated to focus exclusively on the three canonical architectures. Across **5 sequential batches**, we removed superseded runners, exclusive components, coupled analyzers, and mirrored unit test suites representing over 75 files and ~1.2 MB of redundant code.

A complete dependency audit was performed, and all necessary shared infrastructure components were preserved, cleaned, or relocated. The repository is now clean, DRY (Don't Repeat Yourself), and structurally ready for upcoming comparison studies and thesis assessments.

All remaining **994 unit and integration tests** in the test suite pass successfully.

---

## 2. Canonical Architecture Selections

As resolved in the Canonical-Runner Selection decision record, the following representative runners were retained:

| Architecture | Canonical Runner | Description / Role |
| --- | --- | --- |
| **Deterministic** | `pipeline_v1.py` (`Gan2026PipelineV1`) | Pure rule-based extraction baseline. |
| **Fully LLM (One-shot)** | `llm/llm_only_direct_labeler.py` | Baseline for direct single-pass classification. |
| **Fully LLM (Multi-step)** | `llm/llm_only_structured_events.py` | Base for multi-step structured extraction chains. |
| **Hybrid** | `hybrid/reset_clinical_assessment_pipeline.py` | Active hybrid/reset focus composing LLM Select and rule-based Normalize -> Project stages. |

All other experimental runners and modules were retired and cleaned up.

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
  - Deleted 8 non-canonical LLM modules: `llm_only_claim_table_selector.py`, `claim_table_parser.py`, `claim_table_report.py`, `claim_table_component_ablation.py`, `llm_only_minimal_evidence_selector.py`, `llm_only_rich_selected_state_reasoner.py`, `llm_only_simplified_selected_state_reasoner.py`, `llm_only_sparse_operands_selected_state_reasoner.py`, `llm_only_typed_adapter_reasoner.py`, `llm_only_typed_operations_reasoner.py`, and `llm_only_structured_events_repair_ablation.py`.
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

## 4. Verification and Clean Slate

### Automated Verification
A final execution of the entire test suite confirms that the cleanup has left the repository in a healthy, green state:

```powershell
pytest tests/
```
**Results**:
- **Collected**: 994 items
- **Passed**: 994 passed in 7.92 seconds
- **Errors/Failures**: 0

### Repository Cleanliness
* No unstaged modifications remain.
* No untracked files remain.
* All deletions have been performed via `git rm` to preserve file history.
