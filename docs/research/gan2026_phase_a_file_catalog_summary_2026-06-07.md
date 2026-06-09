# Gan 2026 Phase A — File Catalog Summary

Date: 2026-06-07

Author: Claude

Status: survey output — companion to
`gan2026_phase_a_file_catalog_2026-06-07.csv`. Produces the master inventory
called for by [[gan2026_repo_consolidation_and_cleanup_plan]] Section 3
(Phase A). Survey-only; no files modified or removed.

---

## 1. Scope And Method

Catalogued **396 files**: 237 `.py` modules under
`src/clinical_extraction/tasks/seizure_frequency/gan2026/` (all listed
subdirectories plus `deterministic/` — included because it is exclusive
support for the canonical deterministic runner and is otherwise part of the
same tree — and the top-level files) plus **159** `tests/test_gan2026_*.py`
files. `__pycache__` artifacts and the observatory `PROGRESS.md` doc were
included/excluded as noted in the CSV; no `.jsonl`/run-artifact files live
under the `gan2026/` package tree itself (those live in the repo-level
`experiments/` directory, out of scope for this catalog).

Classification was done by: directory/filename pattern matching (primary
signal), docstring skim (first ~30 lines) for ambiguous cases, and
`grep -rl` cross-reference checks against the four named superseded hybrid
lineages, the 8 non-canonical `llm_only_*` modules, and the two canonical
fully-LLM choices, to confirm import-graph membership before assigning
lineage/status.

---

## 2. Totals

### By architecture lineage

| Lineage | Count |
| --- | --- |
| `hybrid-reset-current` | 113 |
| `shared-infrastructure` | 92 |
| `hybrid-staged-v1` | 56 |
| `hybrid-staged-v0` | 46 |
| `llm-only` | 34 |
| `deterministic` | 24 |
| `hybrid-parallel-state` | 21 |
| `hybrid-rules-adjudicator` | 10 |
| `unclear` | 0 |

(`hybrid-reset-current` is large because most `artifact_analysis/` analyzers
and their mirrored tests default there — the reset pipeline is the
"current focus" architecture and most live exploration work targets it.)

### By status

| Status | Count |
| --- | --- |
| `shared-keep` | 194 |
| `needs-decision` | 132 |
| `canonical` | 42 |
| `superseded-candidate` | 28 |

### By role

| Role | Count |
| --- | --- |
| `test` | 159 |
| `component` | 92 |
| `analyzer` | 82 |
| `experiment-artifact` | 18 |
| `runner` | 16 |
| `doc` | 14 |
| `contract-schema` | 10 |
| `report` | 5 |

### `needs-decision` rows by lineage (132 total)

| Lineage | Count |
| --- | --- |
| `hybrid-staged-v1` | 54 |
| `hybrid-staged-v0` | 44 |
| `hybrid-parallel-state` | 19 |
| `llm-only` | 7 |
| `hybrid-rules-adjudicator` | 6 |
| `hybrid-reset-current` | 2 |

---

## 3. `superseded-candidate` Roster (28 files)

Directly named in the canonical-runner selection decision:

- **Hybrid lineages (6 src + 2 test)**: `staged_hybrid_assembly.py`,
  `staged_assembly_v1.py`, `hybrid_parallel_state_candidate_reasoner.py`,
  `hybrid_rules_candidates_llm_adjudicator.py`,
  `hybrid_adjudicator_parser.py`, plus
  `reports/hybrid_adjudicator_report.py` (exclusive report writer for the
  adjudicator lineage), and the corresponding
  `tests/test_gan2026_staged_hybrid_assembly.py`,
  `tests/test_gan2026_staged_assembly_v1.py`,
  `tests/test_gan2026_hybrid_parallel_state_candidate_reasoner.py`,
  `tests/test_gan2026_hybrid_rules_candidates_llm_adjudicator.py`.
- **Non-canonical `llm_only_*` (8 src + 8 test + 2 exclusive support)**:
  `llm_only_claim_table_selector.py`, `llm_only_minimal_evidence_selector.py`,
  `llm_only_rich_selected_state_reasoner.py`,
  `llm_only_simplified_selected_state_reasoner.py`,
  `llm_only_sparse_operands_selected_state_reasoner.py`,
  `hybrid_structured_events_repair_ablation.py`,
  `llm_only_typed_adapter_reasoner.py`,
  `llm_only_typed_operations_reasoner.py`, plus their mirrored tests, plus
  exclusive support modules `llm/claim_table_parser.py` and
  `reports/claim_table_report.py` (both used only by
  `llm_only_claim_table_selector`).
- **`artifact_analysis/claim_table_component_ablation.py`** plus its test —
  built specifically for the superseded claim-table selector.

All 28 are flagged for the Phase C dependency audit before any removal —
several (`architecture_component_ablation.py`,
`saturated_surface_evaluation.py`, `synthetic_hard_case_component_stress.py`,
`evidence_selection_matrix.py`, `direct_labeler_unrecalled_failure_slice_experiment.py`,
`fewshot_train_exemplar_candidate_experiment.py`) reference the named
superseded lineages but were classified `needs-decision` rather than
`superseded-candidate` because they sit in `artifact_analysis/`/`experiments/`
rather than being the lineage's own runner — Phase C should determine whether
they are exclusive to the superseded lineage (then candidates for the same
removal batch) or have independent canonical-line value.

---

## 4. `artifact_analysis/` Overlap Clusters (76 analyzer files)

Mapped against the 9 clusters named in the cleanup plan Section 1. Counts
below are analyzer-file memberships identified during this survey (some
files plausibly span more than one cluster; each was assigned to its primary
cluster for this catalog):

| Cluster | Approx. count | Example members |
| --- | --- | --- |
| ablation | 8 | `architecture_component_ablation`, `claim_table_component_ablation`, `llm_replacement_postprocessing_ablation`, `month_bucket_duration_selection_ablation`, `projection_arbitration_ablation`, `reset_stage_component_ablation_v6`, `validation_component_stress_ablation` |
| verification/routing | 13 | `clinical_assessment_first_verifier_experiment`, `clinical_assessment_verification_decision`, `clinical_assessment_verification_route`, `selective_verifier_experiment`, `selective_verifier_predeclaration`, `change_only_det_state_family_experiment`, `change_only_llm_selector_family_experiment`, `combined_change_only_switch_layer_experiment` |
| boundary/seizure-free | 8 | `boundary_state_graph_replay`, `seizure_free_duration_node_replay`, `seizure_free_duration_projection_ablation`, `selective_boundary_candidate_experiment`, `selective_safety_floor_gate_replay`, `atlas_hard_slice_diagnostic` |
| candidate/state | 11 | `candidate_discovery_matrix`, `candidate_set_comparison`, `candidate_set_diagnostics`, `candidate_set_replay`, `candidate_set_union`, `candidate_union`, `selected_candidate_decision_diagnostics`, `selected_state_union_replay`, `evidence_selection_matrix` |
| projection/render/scoring | 5 | `clinical_assessment_projection_render`, `clinical_assessment_projection_score`, `projection_decision_matrix`, `component_projection_panel`, `rq5_rendering_matrix` |
| RQ-panels | 9 | `rq1_rq2_control_panels`, `rq8_telemetry_guard`, `rq9_abstention_pressure`, `rq9_router_pressure_points`, `rq9_selective_action_router`, `rq10_gold_scorer_ambiguity_audit` |
| validation surfaces | 10 | `null_reduction_validation_slices`, `validation_component_stress_panel`, `validation_gold_ambiguity_inventory`, `validation_test_gap_matrix`, `validation_test_surface_map`, `gold_audit_active_sampler`, `nonprediction_recovery_audit` |
| hidden-family/repair-policy | 9 | `h1_hidden_family_slice_aggregates`, `h5_repair_policy_manifest`, `h5_semantic_repair_gap`, `h9_action_policy_gap`, `h9_action_policy_sidecars`, `h10_raw_identity_sidecar`, `hidden_family_atlas` |
| pressure/policy-routing | 4 | `suspicious_selected_state_routing`, `residual_nonprediction_audit`, `nonprediction_recovery_audit`, `nonprediction_release_candidate` |

Three analyzers sit outside all nine clusters and are exclusive
canonical-pipeline support: `replay_io.py` (shared replay IO helper, used
directly by `hybrid_structured_events`), `reset_stage_component_inventory.py`
(documents the reset-lineage crosswalk), and the four
`clinical_assessment_projection_render/score/verification_decision/route.py`
modules that the canonical `reset_clinical_assessment_pipeline.py` imports
directly as composed stages — these were marked `canonical`, not clustered.

These clusters are exactly the Phase F.2 consolidation targets (the plan
names ablation → 1 module, boundary/seizure-free → 1, candidate/state → 1,
projection/render/scoring → 1).

---

## 5. Surprises / Ambiguities Flagged `needs-decision`

1. **`components/*` (47 files) have no live import from the canonical reset
   pipeline.** A grep confirmed `reset_clinical_assessment_pipeline.py`
   imports nothing from `components/`; only two (`source_trace.py`,
   `suspicious_state_policy.py`) have any cross-module dependents at all
   (both from `artifact_analysis/suspicious_selected_state_routing.py` and
   `selected_state_union_replay.py`). The rest look like standalone
   validation/research scripts from the staged-assembly eras
   (`structured_*` → likely `staged_assembly_v1`/v0 work;
   `boundary_*`/`staged_decision_policy`/`trigger_*`/`selective_*` →
   likely `staged_hybrid_assembly` v0 work, per docstrings naming "staged
   hybrid assembly rows"). Marked `needs-decision` rather than
   `superseded-candidate` because their lineage attribution is inferred from
   naming/docstring, not confirmed by import-graph membership in a named
   lineage runner — Phase C should confirm exclusivity before reclassifying.
2. **`llm_heavy_clinical_frequency_reasoner.py` and
   `llm_heavy_evidence_selection_with_deterministic_adapters.py`** are
   pre-`llm_only_*`-naming-convention experiments with no found dependents —
   they predate the architecture taxonomy this catalog uses and don't fit
   cleanly into either `llm-only` or `hybrid-reset-current`. Flagged
   `needs-decision`: are these retired precursors (fold into lineage doc) or
   living comparators that should be renamed into the convention?
3. **`experiments/saturated_surface_evaluation.py` and
   `experiments/synthetic_hard_case_component_stress.py`** import/reference
   `hybrid_rules_candidates_llm_adjudicator` (a named superseded lineage) but
   live in the shared `experiments/` infrastructure package rather than in
   `hybrid/`. Flagged `needs-decision`: confirm in Phase C whether they are
   exclusive to the superseded adjudicator lineage (→ remove together) or
   have independent value as generic stress/evaluation harnesses that should
   be re-pointed at the canonical hybrid runner.
4. **`artifact_analysis/architecture_component_ablation.py`,
   `evidence_selection_matrix.py`, `candidate_discovery_matrix.py`,
   `rq5_rendering_matrix.py`, `rq9_selective_action_router.py`,
   `h10_raw_identity_sidecar.py`, `h10_runtime_variance_audit.py`,
   `hidden_family_atlas.py`, `rq10_gold_scorer_ambiguity_audit.py`,
   `selective_safety_floor_gate_replay.py`,
   `structured_projection_port_frozen_test_audit.py`,
   `change_only_llm_selector_family_experiment.py`,
   `combined_change_only_switch_layer_experiment.py`** (13 files, plus
   mirrored tests) reference `hybrid_parallel_state_candidate_reasoner` —
   a named superseded lineage — yet several are also wired into
   `cli/llm_pipeline_cli.py` and/or `observatory/api.py`'s
   `_PIPELINE_FAMILIES`. This is the exact "blocked — has live dependents"
   scenario the cleanup plan's Phase C anticipates: removing the
   parallel-state lineage cleanly requires first auditing whether these
   analyzer/CLI/observatory references can be retargeted or must be retired
   alongside it.
5. **`cli/llm_pipeline_cli.py` and `observatory/api.py`** both reference
   canonical AND superseded-candidate runners in the same registry — by
   design (the registry-of-standalone-scripts pattern the plan's Phase F.3
   names for collapse). Marked `shared-keep` (they are live, load-bearing
   infrastructure), but every superseded-candidate's removal requires a
   registry-unwiring step first; this is noted per-file in the CSV.
6. **`reports/claim_table_report.py` and
   `reports/hybrid_adjudicator_report.py`** are report writers exclusively
   serving superseded-candidate runners (`llm_only_claim_table_selector` and
   `hybrid_rules_candidates_llm_adjudicator` respectively) — classified
   `superseded-candidate` rather than `shared-keep`, since `reports/base.py`
   (the actual shared scaffold both build on) is the load-bearing shared
   piece.
7. **`hybrid_structured_events_repair_ablation.py`** — per the selection
   decision's own note, this "should survive Phase C only if it remains the
   active mechanism for ablating the canonical runner's repair-family
   policies." Catalogued as `superseded-candidate` (matching the decision
   doc's framing that it likely folds into the lineage doc) but flagged
   for explicit re-check in Phase C since it is a companion to a *canonical*
   module, not an independent retired architecture.

No files were left in lineage `unclear` — every file received at minimum a
best-guess lineage from directory/naming/import-graph signals, with status
`needs-decision` carrying the residual uncertainty (132 such rows, concentrated
in the `hybrid-staged-v0`/`hybrid-staged-v1`/`hybrid-parallel-state` lineages,
i.e. exactly the superseded-candidate territory Phase C needs to dependency-audit).
