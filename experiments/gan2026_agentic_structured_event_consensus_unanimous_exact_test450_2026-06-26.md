# Gan 2026 Agentic Structured-Event Consensus: Exact Three-Agent Test Replay

Date: 2026-06-26

## Experiment Unit

- Work class: no-call component replay for exact v0.9 source parity.
- Surface: locked `test450`, manifest `gan2026_split_v1`.
- Policy: keep the rules-tool baseline unless GPT, Qwen, and DeepSeek structured-event agents emit the same non-null exact final label.
- Inspection boundary: no row-level correctness, failures, evidence, selected events, or transitions are written.

## Source Artifacts

- `rules_tool_baseline`: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl` (`8155612105b462ec126df3aaebe5e81e2d730448babe1fcc3bfa60348e45dbf2`)
- `structured_event_agent_gpt41mini_v05`: `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl` (`0c9bd96a49cfd22e57f2f9c421dbc78bf0e3a0f16233a67e09c853c174c2b40c`)
- `structured_event_agent_qwen3635b_recent_patch`: `experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_qwen3635b_2026-06-13.jsonl` (`61ac7d12c9580188c3f5c467a41d55d4962cf7f81052e5617dd19868ef997f59`)
- `structured_event_agent_deepseek_v06`: `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl` (`d57dc30c7c859c47e072e9278df3f2be1e70c56a9e62acae0e16f43f5c0cddca`)

## Technical Summary

- Rows: `450`
- Actions: `{'keep_baseline': 365, 'switch_to_consensus': 85}`
- Reasons: `{'accepted_unanimous_exact_label': 85, 'consensus_matches_baseline': 160, 'no_unanimous_exact_label': 205}`
- Missing agent rows: `{}`
- JSONL artifact: `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_test450_2026-06-26.jsonl`

## Claim Boundary

Exact three-agent test consensus component for source parity only. It is not a Gate 4 result and does not authorize tuning or row-level test failure inspection.
