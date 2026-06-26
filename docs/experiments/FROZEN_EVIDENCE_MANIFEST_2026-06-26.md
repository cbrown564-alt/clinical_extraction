# Frozen Evidence Manifest

Date: 2026-06-26

## Purpose

This manifest records aggregate-claim evidence that must **not** be deleted, moved, or renamed during repo cleanup. It defines the frozen boundary for holdout and full-200 aggregate claims: numbers may be cited only under the inspection rules in each artifact's claim language. It does not authorize post-test tuning, row-level holdout development, or promotion beyond what each source artifact already states.

## Active Indexes

| Index | Path | Role |
| --- | --- | --- |
| Machine registry | [`experiments/registry.jsonl`](../../experiments/registry.jsonl) | Canonical run-of-record; append via registered drivers only |
| Human scan | [`experiments/RUN_INDEX.md`](../../experiments/RUN_INDEX.md) | Generated from `registry.jsonl` |
| Evidence spine + hashes | [`docs/experiments/final_artifact_index_2026-06-22.md`](final_artifact_index_2026-06-22.md) | SHA-256 frozen spine for closeout comparators |
| Archive buckets | [`experiments/archive/ARCHIVE_INDEX.md`](../../experiments/archive/ARCHIVE_INDEX.md) | 438 superseded `.md` notes moved 2026-06-26 |
| Regeneration guide | [`docs/REGENERATION.md`](../REGENERATION.md) | How to refresh indexes; does not authorize deleting frozen artifacts |
| Active surface | [`experiments/README.md`](../../experiments/README.md) | Current comparator scan order |

## ExECTv2 Frozen Paths

| Surface | Primary report | Machine-readable companions | Claim boundary |
| --- | --- | --- | --- |
| **v08 headline (dev140 control)** | [`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`](exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md) | [`experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json`](../../experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json), [`.jsonl`](../../experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl), [`configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml`](../../configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml) | Dev140 `clinical_headline` `0.9152`; performance control, not holdout |
| **v08 full-200 headline** | [`docs/experiments/exectv2/reliability/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.md`](exectv2/reliability/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.md) | [`experiments/exectv2_v08_full200_currentcode_sf_structured_direct_unknown_suppression_20260624.md`](../../experiments/exectv2_v08_full200_currentcode_sf_structured_direct_unknown_suppression_20260624.md) | Full-200 aggregate `0.8502`; no row-level inspection |
| **Component-off full-200** | [`experiments/exectv2_component_off_replay_full200_20260626.md`](../../experiments/exectv2_component_off_replay_full200_20260626.md) | [`.json`](../../experiments/exectv2_component_off_replay_full200_20260626.json), [`.jsonl`](../../experiments/exectv2_component_off_replay_full200_20260626.jsonl); predeclaration [`docs/experiments/exectv2/reliability/exectv2_component_off_full200_predeclaration_2026-06-26.md`](exectv2/reliability/exectv2_component_off_full200_predeclaration_2026-06-26.md) | Component Impact only; separate from reliability scorecard |
| **Same-core full-200** | [`docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`](exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md) | [`experiments/exectv2_same_core_model_swap_full200_20260625.json`](../../experiments/exectv2_same_core_model_swap_full200_20260625.json), [`.jsonl`](../../experiments/exectv2_same_core_model_swap_full200_20260625.jsonl); predeclaration [`exectv2_same_core_full200_predeclaration_2026-06-25.md`](exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md) | GPT `0.8356`, DeepSeek `0.8566`, Qwen repair v02 `0.8197`; aggregate only |
| **Reliability audits** | [`docs/experiments/exectv2/reliability/exectv2_robustness_validation_audit_2026-06-25.md`](exectv2/reliability/exectv2_robustness_validation_audit_2026-06-25.md) | Preflight [`exectv2_robustness_panels_preflight_2026-06-25.md`](exectv2/reliability/exectv2_robustness_panels_preflight_2026-06-25.md); calibration [`exectv2_calibration_validation_audit_2026-06-25.md`](exectv2/reliability/exectv2_calibration_validation_audit_2026-06-25.md); review routing [`exectv2_review_routing_validation_audit_2026-06-24.md`](exectv2/reliability/exectv2_review_routing_validation_audit_2026-06-24.md) | Hard-slice F1 `0.8336`; validation aggregate only |

## Gan 2026 Frozen Paths

| Surface | Primary report | Machine-readable companions | Claim boundary |
| --- | --- | --- | --- |
| **v0.7 test450 (DeepSeek SE)** | [`experiments/gan2026_v07_test450_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260625.md`](../../experiments/gan2026_v07_test450_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260625.md) | [`.jsonl`](../../experiments/gan2026_v07_test450_hybrid_structured_events_deepseek_reasoner_thinking_maxtok32000_20260625.jsonl) | Frozen aggregate `346/450` Purist, `365/450` Pragmatic; cross-model holdout fill |
| **Phase 4 three-way test450** | [`experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`](../../experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md) | Per-architecture frozen audits `gan2026_test450_phase4_frozen_audit_*_gpt41mini_2026-06-09.{md,jsonl}`; V12 best [`gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.{md,jsonl}`](../../experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md) | Locked `test450` three-way + V12 `379/450`; aggregate only |
| **Gate 4 exact (v0.9)** | [`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`](../../experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md) | [`.json`](../../experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.json); protocol [`docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`](gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md) | Passed: `359/450` selected Purist, `+16` net, precision `0.6000` |
| **Gate 4 constrained (v0.9)** | [`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.md`](../../experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.md) | [`.json`](../../experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.json) | Failed promotion: `348/450`, precision `0.5909`; final-evaluation only |
| **Reliability scorecard** | [`experiments/gan2026_reliability_master_scorecard_2026-06-17.md`](../../experiments/gan2026_reliability_master_scorecard_2026-06-17.md) | [`.json`](../../experiments/gan2026_reliability_master_scorecard_2026-06-17.json); Phase 0 `gan2026_reliability_p0_*_2026-06-17.{json,md}`; Phase 1 test450 port `gan2026_reliability_p1_*_test450_2026-06-17.{json,md}` | Re-expression of reliability dimensions; not a new benchmark claim |

## Paper-Facing Docs (`docs/research/`)

| Doc | Role |
| --- | --- |
| [`docs/research/paper_manuscript_2026-06-26.md`](../research/paper_manuscript_2026-06-26.md) | Integrated IEEE results draft; cites frozen aggregates above |
| [`docs/research/exectv2_results_section_draft_2026-06-26.md`](../research/exectv2_results_section_draft_2026-06-26.md) | ExECTv2 Section 4.2 prose |
| [`docs/research/exectv2_results_section_scaffold_2026-06-25.md`](../research/exectv2_results_section_scaffold_2026-06-25.md) | Table shells and scaffolding |
| [`docs/research/exectv2_reliability_component_evidence_paper_language_2026-06-25.md`](../research/exectv2_reliability_component_evidence_paper_language_2026-06-25.md) | Reliability vs Component Impact claim language |
| [`docs/research/exectv2_component_off_reliability_ablation_plan_2026-06-26.md`](../research/exectv2_component_off_reliability_ablation_plan_2026-06-26.md) | Component-off ablation protocol |
| [`docs/research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md`](../research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md) | Gan closeoff synthesis |
| [`docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`](../research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md) | Gan reliability closeout |
| [`docs/research/README.md`](../research/README.md) | Paper sprint index |
| [`literature/IEEE/IEEE-conference-template-062824/IEEE-conference-template-062824.tex`](../../literature/IEEE/IEEE-conference-template-062824/IEEE-conference-template-062824.tex) | Checked-in LaTeX source (regenerate PDF locally) |

## Local-Only (Gitignored — Never Commit)

| Path | Contents |
| --- | --- |
| `mlruns/`, `mlflow.db*` | Local MLflow tracking state |
| `output/` | New operational captures (legacy tracked files remain in git history) |
| `scratch/` | Ad-hoc diagnostics and scratch scripts |
| `logs/` | Run log captures |
| `experiments/**/traces/`, `experiments/**/predictions*.{csv,json}` | Row-level outputs unless explicitly force-added |
| `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `frontend/node_modules/`, `frontend/.next/` | Build and test caches |

## Archive Policy

| Rule | Detail |
| --- | --- |
| Superseded human notes | Moved to [`experiments/archive/`](../../experiments/archive/) per [`ARCHIVE_INDEX.md`](../../experiments/archive/ARCHIVE_INDEX.md); **438** notes archived 2026-06-26 |
| Machine-readable artifacts | JSON/JSONL stay in [`experiments/`](../../experiments/) for reproduction even when the companion `.md` was archived |
| Do not archive | Frozen holdout rows, reliability scorecards, active ExECTv2/Gan comparators listed above, or anything indexed in `registry.jsonl` / `final_artifact_index_2026-06-22.md` |
| Checkpoint notes | Mid-run checkpoints under `experiments/archive/exectv2_checkpoints/` are superseded by completed JSON/JSONL reports |
