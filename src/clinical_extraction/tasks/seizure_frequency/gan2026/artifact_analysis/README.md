# Gan 2026 `artifact_analysis/` — Archive Index

Quarantined no-call / saved-artifact analysis scripts from the Gan 2026 closing campaign. All modules read frozen `experiments/` JSONL/JSON/CSV and emit analysis artifacts (JSONL, JSON, Markdown); most do **not** call models. Shims re-export live pipeline/observatory modules for backward compatibility.

**Phase F consolidators** (`scoped_ablation_analyzer`, `boundary_diagnostic`, `candidate_state_matrix`, `projection_scoring`) replaced ~32 survey scripts — see `__init__.py` registry.

---

### Infrastructure & shims

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `__init__.py` | Package entry; Phase F analyzer registry & completion summary | — |
| `reliability_common.py` | Shared reliability scorecard loaders, subject accessors, consensus/stats | In: frozen reasoner/consensus JSONL → Out: row layers for drivers |
| `replay_io.py` | Shim → `pipeline.replay_io` | — |
| `gold_audit_active_sampler.py` | Shim → `observatory.gan2026.gold_audit_sampler` | — |
| `clinical_assessment_projection_score.py` | Shim → `pipeline.stages.clinical_assessment_projection_score` | — |
| `clinical_assessment_projection_render.py` | Shim → `pipeline.stages.clinical_assessment_projection_render` | — |
| `clinical_assessment_verification_route.py` | Shim → `pipeline.stages.clinical_assessment_verification_route` | — |
| `clinical_assessment_verification_decision.py` | Shim → `pipeline.stages.clinical_assessment_verification_decision` | — |

### Phase F consolidated analyzers

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `scoped_ablation_analyzer.py` | Parameterized ablation metrics, JSON summaries, markdown reports | In: variant run fns + gold → Out: evaluation JSON/MD |
| `boundary_diagnostic.py` | Unified boundary / seizure-free node diagnostics | In: replayed boundary rows → Out: diagnostic JSON/MD |
| `candidate_state_matrix.py` | CandidateSet overlap, union, decision comparison | In: two candidate row sets → Out: comparison JSON/MD |
| `projection_scoring.py` | Projection render/score/route/decision stage summaries | In: stage row JSONL → Out: combined metrics JSON/MD |

### Architecture comparison & component impact

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `three_way_comparison_report.py` | Six-architecture validation750 comparison table + hybrid appendix | In: completed run JSONL → Out: comparison JSONL/MD |
| `phase4_test450_frozen_audit_report.py` | Frozen test450 audit for four authorized architectures | In: test450 artifacts → Out: aggregate audit JSONL/MD |
| `component_stage_ladder.py` | Cumulative stage-ladder replay (purist category accuracy, validation750) | In: saved producer outputs → Out: `ComponentLadder` JSON/MD |
| `component_transition_examples.py` | Illustrative per-note label trajectories for sidebar (non-scoring) | In: ladder providers → Out: example JSON/MD |
| `llm_component_mechanics.py` | Row-level LLM component mechanics from RQ1/RQ2/RQ4 matrices | In: RQ matrices JSONL → Out: mechanics JSONL/MD |

### Ablation studies

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `projection_arbitration_ablation.py` | Projection/arbitration ablations over state-graph artifacts | In: hard-slice + replay JSONL → Out: ablation JSONL/JSON/MD |
| `seizure_free_duration_projection_ablation.py` | Seizure-free duration projection ablation on saved graphs | In: graph JSONL → Out: ablation JSONL/MD |
| `month_bucket_duration_selection_ablation.py` | Month-bucket duration-selection projection ablation | In: state-graph JSONL → Out: ablation JSONL/MD |
| `llm_replacement_postprocessing_ablation.py` | Saved-output replacement ablations for LLM post-processing layers | In: saved layer outputs → Out: ablation JSON/MD |
| `reset_stage_component_ablation_v6.py` | First reset-stage component ablation table from V5/V6 artifacts | In: V5/V6 saved artifacts → Out: ablation table JSON/MD |
| `validation_component_stress_ablation.py` | No-call component-stress ablations over H2/H4 panel | In: stress panel JSONL → Out: ablation JSON/MD |

### Projection & state graph

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `projection_decision_matrix.py` | RQ4 projection-decision matrix from evidence/arbitration/duration artifacts | In: RQ2 + ablation JSONL → Out: RQ4 matrix JSONL/MD |
| `component_projection_panel.py` | Frozen component-projection follow-up panel | In: RQ2/RQ4 + atlas CSV → Out: panel JSONL/JSON/MD |
| `boundary_state_graph_replay.py` | Replay accepted boundary-state builder nodes into diagnostic graphs | In: boundary artifacts → Out: replay JSONL/MD |
| `seizure_free_duration_node_replay.py` | Validation-only seizure-free duration node construction replay | In: validation records + graphs → Out: replay JSONL/MD |

### Candidate set & state space

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `candidate_set_replay.py` | Validation250 deterministic candidate-set replay (architecture reset) | In: validation records → Out: CandidateSet JSONL/JSON/MD |
| `candidate_set_diagnostics.py` | Diagnostics for validation250 CandidateSet replay artifacts | In: replay JSONL → Out: diagnostic JSON/MD |
| `candidate_set_comparison.py` | Compare deterministic vs LLM validation250 CandidateSet diagnostics | In: two replay JSONL → Out: comparison JSON/MD |
| `candidate_set_union.py` | Build deterministic+LLM CandidateSet union for validation250 | In: two CandidateSet JSONL → Out: union JSONL/MD |
| `candidate_union.py` | Saved-artifact candidate-union diagnostics | In: union/control artifacts → Out: union JSON/MD |
| `selected_candidate_decision_diagnostics.py` | Diagnostics for SelectedCandidateDecision selector artifacts | In: selector JSONL → Out: diagnostic JSON/MD |
| `clinical_assessment_diagnostics.py` | Diagnostics for CandidateSet ClinicalAssessment probe artifacts | In: probe JSONL → Out: diagnostic JSON/MD |

### Verifier & selective-action experiments

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `selective_verifier_predeclaration.py` | Predeclare selective verifier input surface from routing rows | In: routing JSONL → Out: predeclared JSONL/MD |
| `selective_verifier_experiment.py` | Run selective verifier on frozen predeclared surface (**calls model**) | In: predeclared JSONL → Out: verifier JSONL/JSON/MD |
| `clinical_assessment_forced_choice_verifier_experiment.py` | Forced-choice verifier variant on validation V6 surface (**calls model**) | In: input + action-only JSONL → Out: forced-choice JSONL/MD |
| `first_verifier_post_run_accounting.py` | Post-run accounting: first-verifier actions vs deterministic V0 by bucket | In: verifier JSONL → Out: accounting JSON/MD |
| `selective_boundary_candidate_predeclaration.py` | Predeclare selective boundary-candidate proposer calls | In: candidate union artifacts → Out: predeclared JSONL/MD |
| `selective_boundary_candidate_experiment.py` | Run predeclared boundary-candidate proposer experiment (**may call model**) | In: predeclared JSONL → Out: experiment JSONL/MD |
| `suspicious_state_policy.py` | Deterministic suspicious selected-state flag policy for assembly | In: state dict → Out: review/unknown flags |
| `source_trace.py` | Source-id and selected-evidence trace checks | In: structured record → Out: trace status dict |
| `suspicious_selected_state_routing.py` | Materialize suspicious selected-state routing diagnostics | In: union + control artifacts → Out: routing JSON/MD |

### RQ / hypothesis panels

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `rq1_rq2_control_panels.py` | RQ1/RQ2 single-task control panels and condition matrices | In: atlas CSV + artifacts → Out: panel JSONL/CSV/MD |
| `rq8_telemetry_guard.py` | Check RQ8 cost/latency/token claims against telemetry | In: telemetry + claims → Out: guard JSON/MD |
| `rq9_abstention_review_predeclaration.py` | Predeclare RQ9 abstention/human-review routing from RQ10 classes | In: RQ10 artifacts → Out: predeclared JSONL/MD |
| `rq9_abstention_pressure.py` | Interpret remaining RQ9 v2 abstention and review pressure | In: router JSONL → Out: pressure JSON/MD |
| `rq9_last_event_boundary.py` | Interpret RQ9 last-event human-review boundaries | In: boundary artifacts → Out: interpretation JSON/MD |
| `rq9_router_pressure_points.py` | Analyze RQ9 selective-action router review pressure points | In: router JSONL → Out: pressure-point JSON/MD |
| `rq9_cluster_convention_monitoring.py` | Predeclare and materialize RQ9 cluster/convention monitoring | In: cluster artifacts → Out: monitoring JSON/MD |
| `h1_hidden_family_slice_aggregates.py` | H1 hidden-family validation/test aggregate slice readouts | In: atlas + split records → Out: slice JSON/MD |
| `h5_semantic_repair_inventory.py` | Inventory H5 semantic repair families before candidate work | In: replacement ladder JSON → Out: inventory + ablation JSON/MD |
| `h5_semantic_repair_gap.py` | Aggregate-safe H5 semantic-repair attribution test | In: saved repair artifacts → Out: gap JSON/MD |
| `h5_repair_policy_manifest.py` | Freeze H5 repair policy v1 as bounded diagnostic contract | In: inventory → Out: policy manifest JSON/MD |
| `h9_action_policy_gap.py` | Test H9 action-policy pressure on validation + aggregate test surfaces | In: assembled artifacts → Out: gap JSON/MD |
| `h9_action_policy_sidecars.py` | Materialize H6/H9 action-policy sidecars (instrumentation only) | In: assembled + boundary JSONL → Out: sidecar JSON/MD |

### Validation, generalization & gold review

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `validation_test_gap_matrix.py` | Validation-only score-layer rows for generalisation-gap matrix | In: validation artifacts → Out: gap matrix JSONL/MD |
| `validation_test_surface_map.py` | Aggregate validation-test surface maps from predeclared artifacts | In: predeclared JSONL → Out: surface map JSON/MD |
| `validation_test_gap_hypothesis_selection.py` | Select controlled hypotheses from validation-test gap matrix | In: gap matrix → Out: hypothesis selection JSON/MD |
| `validation_component_stress_panel.py` | Build H2/H4 validation component-stress hard/control panel | In: component matrix CSV → Out: panel JSONL/MD |
| `validation_gold_ambiguity_inventory.py` | Build validation750 gold-label ambiguity review CSV | In: validation750 gold → Out: review CSV/MD |
| `null_reduction_validation_slices.py` | Validation proxy slices for holdout-aligned null-reduction diagnostics | In: validation artifacts → Out: slice JSON/MD |
| `atlas_hard_slice_diagnostic.py` | No-call diagnostics over atlas-derived hard slices | In: hard-slice manifest → Out: diagnostic JSONL/MD |

### Nonprediction & release candidates

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `nonprediction_release_candidate.py` | Apply untagged-nonprediction release candidate over validation artifacts | In: component matrix + stress panel → Out: assembled JSONL/MD |
| `nonprediction_recovery_audit.py` | Audit gold-blinded lanes for recovering staged-policy nonpredictions | In: blinded artifacts → Out: audit JSON/MD |

### Reset inventory

| Module | Purpose | Key I/O |
|--------|---------|---------|
| `reset_stage_component_inventory.py` | Reset-stage crosswalk from old Gan families to current owners | In: legacy inventory → Out: crosswalk JSON/MD |

---

*Generated for Wave 1 / I3 closing-campaign orchestration. Do not execute blindly — verify artifact paths under `experiments/` before re-running.*
