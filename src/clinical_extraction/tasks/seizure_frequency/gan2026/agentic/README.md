# Gan 2026 agentic stages

DSPy-backed stage runners for validation-development experiments. Shared scaffolding
lives in `stage_protocol.py`; migrated stages implement `AgenticStage` with:

1. **Prompt builder** — serializes one model-facing JSON payload per row
2. **Decision schema** — Pydantic record validated after `contract.schema_repair`
3. **Postprocess policy** — format-only or evidence-guided label repair, substring checks
4. **Thin `run_split`** — row loop, metadata, JSONL, and markdown report via shared helpers

## Migrated (AgenticStage / run_driver)

| Module | Notes |
| --- | --- |
| `confidence_reviewer.py` | Shadow stage; no split runner (single-row `review()` only) |
| `boundary_audit_prompt_v2.py` | D1 panel/hard50 runner |
| `direct_boundary_critic_rescue.py` | D2 direct + boundary critic panel/hard50 runner |
| `structured_event_verifier.py` | V4 verifier-first structured-event correction |
| `fresh_evidence_reasoner.py` | V12 fresh-evidence reasoner; `run_split` on `run_driver` |
| `cross_model_challenge_adjudicator.py` | V11 open peer-challenge; `run_split` via `dispatch_registered_split` |
| `represented_event_normalizer.py` | V8 represented-event normalizer; `run_split` via `dispatch_registered_split` |
| `event_completion_reasoner.py` | V7 event-completion reasoner; `run_split` via `dispatch_registered_split` |
| `temporal_sentinel_specialist.py` | V9 temporal/sentinel specialist; `run_split` via `dispatch_registered_split` |
| `targeted_boundary_router.py` | V3 targeted boundary router; `run_split` via `dispatch_registered_split` |

## Legacy pattern (inline runner)

These modules still duplicate parse/metadata/report boilerplate and are candidates
for incremental migration. Do **not** rewrite monoliths wholesale — migrate one stage at a time.

- `llm_event_reasoner.py`
- `cross_model_structured_event_adjudicator.py`
- `structured_event_consensus.py`
- `structured_event_patches.py`
- `precision_gated_selector.py`
- `consensus_fresh_agreement_selector.py`
- `boundary_guide_rescue_replay.py`
- `selective_fallback_replay.py`
- `tool_context_ablation.py`
- `tool_self_consistency.py`
- `llm_reasoning_stage0.py`
- `runner.py`

## Shared helpers (`stage_protocol.py`)

- `parse_response` — JSON extract + `schema_repair` + optional label repair
- `build_stage_metadata` — wraps `experiments.run_metadata.build_run_metadata`
- `write_stage_jsonl` / `load_stage_jsonl`
- `build_markdown_report_skeleton` — standard experiment report sections
- `configure_dspy_for_stage` / `build_isolated_dspy_lm`
- `emit_progress_checkpoint`
