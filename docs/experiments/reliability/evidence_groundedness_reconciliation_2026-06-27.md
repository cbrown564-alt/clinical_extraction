# Evidence Groundedness Reconciliation — Phase 3 Replay

Date: 2026-06-27  ·  Model calls: 0 (replay-only)

Replay-only recompute of the unified `evidence_grounded_rate` over saved artifacts using the canonical metric in `core/evidence.py`. See [docs/reference/evidence_groundedness_metric.md](../../reference/evidence_groundedness_metric.md).

## Qwen headline (validation750 surfaced rows)

- **Hybrid structured-events:** exact-valid 74.8% → grounded 94.7% (string-level); row-grounded 86.4%
- **LLM-only canonical:** exact-valid 76.5% → grounded 90.9% (string-level); row-grounded 90.9%

The Qwen gap was overwhelmingly `REPAIRED_*` formatting (especially `≤` copy artifacts), not absent evidence — the old exact-substring metric penalised grounded copy fidelity.

## Priority set (9 promote + 6 surface-as-architecture)

| Run | Task | Model | Before (exact) | After (grounded) | Exact sub-metric |
|---|---|---|---:|---:|---:|
| `gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12` | gan2026 | openai/gpt-4.1-mini | 83.3% | 83.3% | 83.3% |
| `gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12` | gan2026 | none | 0.0% | 0.0% | 0.0% |
| `gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13` | gan2026 | panel: deterministic_rules_tool + gpt-4.1-mini + qwen3-235b-a22b + deepseek **Qwen** | 0.0% | 0.0% | 0.0% |
| `gan2026_agentic_structured_event_patch_recent_unresolved_burden_validation750_qwen3635b_2026-06-12` | gan2026 | none; saved ollama_chat/qwen3.6:35b structured-events outputs only **Qwen** | 77.5% | 87.9% | 89.6% |
| `gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13` | gan2026 | openai/gpt-4.1 | 93.7% | 93.6% | 95.0% |
| `gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15` | gan2026 | none | 0.0% | 0.0% | 0.0% |
| `gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08` | gan2026 | DeepSeek | 95.7% | 94.9% | 97.8% |
| `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07` | gan2026 | GPT-4.1-mini | 92.1% | 92.1% | 94.8% |
| `gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08` | gan2026 | Qwen **Qwen** | 74.8% | 86.4% | 88.6% |
| `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08` | gan2026 | DeepSeek | 92.5% | 95.6% | 92.5% |
| `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07` | gan2026 | GPT-4.1-mini | 93.3% | 95.5% | 93.3% |
| `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08` | gan2026 | Qwen **Qwen** | 76.5% | 90.9% | 76.5% |

## Wider registry + reliability catalog

| Run | Source | Before (exact) | After (grounded) | Exact sub-metric |
|---|---|---:|---:|---:|
| `decision_table_sf_inv_deepseek_chat_dev140` | exectv2_reliability_catalog | 0.0% | 99.7% | 99.7% |
| `decision_table_sf_inv_gpt41mini_dev140` | exectv2_reliability_catalog | 0.0% | 99.7% | 99.7% |
| `decision_table_sf_inv_qwen36_side11435_dev140` | exectv2_reliability_catalog | 0.0% | 100.0% | 100.0% |
| `exectv2_holistic_finding_assembly_v08_dev140` | exectv2_reliability_catalog | 100.0% | 99.7% | 99.5% |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | exectv2_reliability_catalog | 100.0% | 99.8% | 99.8% |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | exectv2_reliability_catalog | 100.0% | 99.9% | 99.9% |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | exectv2_reliability_catalog | 100.0% | 99.6% | 99.3% |

Registry rows annotated in-place; prior exact-substring prose preserved under `superseded_evidence_validity` in `primary_metrics`. No prediction or accuracy numbers changed.
