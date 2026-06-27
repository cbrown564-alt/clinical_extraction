# Agentic `run_driver` Decomposition Plan — Wave 1 Kickoff

**Date:** 2026-06-27  
**Status:** Wave 3 S1 in progress — 5/12 legacy `run_split` slices migrated  
**Parent:** [`closing_campaign_orchestration_plan_2026-06-27.md`](closing_campaign_orchestration_plan_2026-06-27.md) Track S1  
**Reference:** [`thermo_nuclear_code_quality_audit_plan_2026-06-26.md`](thermo_nuclear_code_quality_audit_plan_2026-06-26.md) P3-1

**Coordination note (2026-06-27):** Wave 2 slices 3 (`event_completion_reasoner`) and 4
(`temporal_sentinel_specialist`) were migrated in parallel; both use the same
`structured_event` dispatch pattern with no overlap on gate logic.

## Goal

Migrate ~21k LOC across 11 large Gan 2026 `agentic/` modules onto the shared
`agentic/run_driver.py` split-runner scaffold so row loops, DSPy configuration,
metadata assembly, and progress checkpointing live in one place. Stages keep
only prompt builders, decision schemas, postprocess policy, and summary/gate hooks.

## Coordination with M2 (evidence-validity unification)

**Do not restructure `fresh_evidence_reasoner.py` gate logic in Wave 1.** M2 Phase 2
will swap the evidence call site in `llm_event_reasoner.py` and must leave the
`fresh_evidence_reasoner.py` safety gate byte-for-byte unchanged.

| Workstream | Allowed touch in Wave 1 | Wave 2+ |
| --- | --- | --- |
| **S1 (this plan)** | `run_driver` registry/dispatch; migrate legacy inline `run_split` loops; no gate edits in `fresh_evidence_reasoner.py` | Continue monolith migration; optional register already-migrated stages |
| **M2** | Phase 0 audit only | Re-point `llm_event_reasoner.py` evidence scoring; rebase onto S1 if S1 owns agentic surface first |

The orchestrator must not let S1 and M2 edit the same agentic files in one wave
without explicit rebasing.

## Current scaffold (`run_driver.py`)

| Helper | Purpose |
| --- | --- |
| `SplitRunParams` | Shared split-run parameters |
| `run_standard_split` | Per-record loop + metadata + checkpoints |
| `run_structured_event_split` | Single saved structured-event JSONL substrate |
| `run_cross_model_structured_event_split` | Multi-agent GPT/Qwen/DeepSeek substrate |
| `register_agentic_stage` / `dispatch_registered_split` | **Wave 1** — stage registry and dispatch routing |

Dispatch kinds: `standard`, `structured_event`, `cross_model_structured_event`.

## Per-file inventory (HEAD 2026-06-27)

LOC counts are physical lines (including blanks/docstrings). **Migrated** =
`run_split` delegates row-loop ceremony to `run_driver` (directly or via
`dispatch_registered_split`). **Legacy** = inline loop still in module.

| LOC | Module | `run_split` | Status | Primary responsibility | Internal agentic deps | Suggested dispatch kind |
| ---: | --- | --- | --- | --- | --- | --- |
| 64 | `contracts.py` | — | Shared types | Matched-budget Pydantic contracts for Phase 6 runner | — | N/A (no runner) |
| 263 | `tools.py` | — | Shared helpers | Tool parsers (`read_boundary_guide`, candidate parse) | — | N/A |
| 174 | `family_transitions.py` | — | Leaf analytics | Per-family transition decomposition for replay surfaces | — | N/A (called post-split) |
| 179 | `family_cv_promotion.py` | — | Leaf analytics | Held-out-family CV promotion verdict | — | N/A |
| 286 | `precision_gated_selector.py` | — | Leaf analytics | Precision-gated selector summary | `family_cv_promotion` | N/A |
| 297 | `confidence_reviewer.py` | — | Migrated (no split) | Shadow confidence reviewer; single-row `review()` | `stage_protocol` | N/A |
| 347 | `structured_event_consensus.py` | — | Legacy replay | Consensus replay orchestration (not split runner) | `family_*`, `precision_gated_selector` | N/A |
| 510 | `stage_protocol.py` | — | Shared scaffold | `AgenticStage`, parse/postprocess, metadata, JSONL, checkpoints | — | N/A |
| 587 | `structured_event_patches.py` | — | Legacy utility | Deterministic structured-event patch helpers | — | N/A |
| 565 | `cross_model_challenge_adjudicator.py` | ✓ | **Migrated W1** | V11 open peer-challenge over saved multi-agent finals | `cross_model_structured_event_adjudicator`, `llm_event_reasoner` | `cross_model_structured_event` |
| 629 | `represented_event_normalizer.py` | ✓ | **Migrated W2** | V8 represented-event normalization | `llm_event_reasoner`, `structured_event_verifier` | `structured_event` |
| 669 | `tool_self_consistency.py` | ✓ | Legacy | Tool self-consistency ablation split | `runner`, `tool_context_ablation`, `tools` | `standard` |
| 699 | `selective_fallback_replay.py` | — | Legacy replay | Selective fallback replay (no `run_split`) | — | N/A |
| 751 | `runner.py` | ✓ | Legacy (Phase 6) | Matched-budget multi-condition agentic runner | `contracts`, `tools` | `standard` (custom loop) |
| 768 | `tool_context_ablation.py` | ✓ | Legacy | Tool-context ablation split | `runner`, `tools` | `standard` |
| 771 | `llm_reasoning_stage0.py` | — | Legacy utility | Stage-0 reasoning surfaces / hard50 indexing | — | N/A |
| 819 | `boundary_guide_rescue_replay.py` | — | Legacy replay | Boundary-guide rescue replay | — | N/A |
| 734 | `targeted_boundary_router.py` | ✓ | **Migrated W3** | V3 targeted boundary router | `llm_event_reasoner`, `structured_event_verifier` | `structured_event` |
| ~790 | `event_completion_reasoner.py` | ✓ | **Migrated W2** | V9 event-completion reasoner | `llm_event_reasoner` | `structured_event` |
| 906 | `boundary_audit_prompt_v2.py` | ✓ | Migrated | D1 boundary audit panel/hard50 | `stage_protocol`, `tools` | `standard` |
| 1,071 | `llm_event_reasoner.py` | ✓ | Legacy (**M2 touch**) | Core structured-event LLM reasoner + shared scoring helpers | — | `structured_event` |
| 1,114 | `temporal_sentinel_specialist.py` | ✓ | **Migrated W2** | Temporal sentinel specialist | `llm_event_reasoner` | `structured_event` |
| 1,149 | `structured_event_verifier.py` | ✓ | Migrated | V4 verifier-first structured-event correction | `llm_event_reasoner`, `stage_protocol` | `structured_event` |
| 1,251 | `consensus_fresh_agreement_selector.py` | — | Legacy replay | Consensus/fresh agreement selector | — | N/A (replay) |
| 1,392 | `cross_model_structured_event_adjudicator.py` | ✓ | Legacy | V10 cross-model adjudicator (base for challenge/fresh) | `llm_event_reasoner` | `cross_model_structured_event` |
| 1,423 | `direct_boundary_critic_rescue.py` | ✓ | Migrated | D2 direct + boundary critic rescue | `stage_protocol`, `tools` | `standard` |
| 1,956 | `fresh_evidence_reasoner.py` | ✓ | Migrated (**gate frozen**) | V12 fresh-evidence reasoner + safety gate | `run_driver`, `family_*`, `precision_gated_selector` | `cross_model_structured_event` |
| ~400 | `run_driver.py` (post-W1) | — | Scaffold | Shared split runners + stage registry | `stage_protocol`, `cross_model_structured_event_adjudicator` | — |

**Aggregate:** ~21k LOC across 28 Python modules; 11 modules ≥700 LOC; 8 legacy
inline `run_split` implementations remain after Wave 3 slice 5.

## Migration order (smallest / leafiest first)

Priority rule: migrate modules whose `run_split` only needs an existing dispatch
kind, with minimal post-split instrumentation, before touching monoliths that
share scoring/gate logic with M2.

| Wave | Order | Module | Rationale |
| ---: | ---: | --- | --- |
| **1** | 1 | `cross_model_challenge_adjudicator.py` | ✓ Done — smallest legacy `run_split` using existing `cross_model_structured_event` helper; no M2 overlap |
| 2 | 2 | `represented_event_normalizer.py` | ✓ Done — straight `structured_event` substrate; 629 LOC |
| 2 | 3 | `event_completion_reasoner.py` | ✓ Done — same `structured_event` pattern; 830 LOC |
| 2 | 4 | `temporal_sentinel_specialist.py` | ✓ Done — structured-event leaf; no gate edits |
| 2 | 5 | `targeted_boundary_router.py` | ✓ Done — structured-event router; 734 LOC |
| 3 | 6 | `cross_model_structured_event_adjudicator.py` | Base adjudicator; unblocks further cross-model variants |
| 3 | 7 | `llm_event_reasoner.py` | **Coordinate with M2** — evidence call-site swap |
| 3 | 8 | `tool_context_ablation.py` | Phase 6 ablation; depends on `runner` |
| 3 | 9 | `tool_self_consistency.py` | Chains off tool ablation |
| 4 | 10 | `runner.py` | Matched-budget multi-condition loop (may need new dispatch kind) |
| **never W1** | — | `fresh_evidence_reasoner.py` | Already on `run_driver`; gate logic frozen for M2 |
| defer | — | `direct_boundary_critic_rescue.py`, `structured_event_verifier.py`, `boundary_audit_prompt_v2.py` | Already on `AgenticStage` / shared helpers — register only |

Replay-only modules (`consensus_fresh_agreement_selector`, `selective_fallback_replay`,
`boundary_guide_rescue_replay`, `structured_event_consensus`) stay out of scope until
split runners are exhausted.

## Wave 3 deliverables (slice 5 — this tick)

1. **`targeted_boundary_router.run_split`** →
   `dispatch_registered_split("targeted_boundary_router", …)` via
   `run_structured_event_split` with
   `gate_interpretation=structured_event_verifier.gate_interpretation`.
2. **Tests** — extend `tests/test_gan2026_agentic_run_driver.py` with registry +
   dispatch parity; existing `tests/test_gan2026_targeted_boundary_router.py`
   must pass unchanged.

## Wave 2 deliverables (slice 4 — complete)

1. **`temporal_sentinel_specialist.run_split`** →
   `dispatch_registered_split("temporal_sentinel_specialist", …)` via
   `run_structured_event_split` with
   `gate_interpretation=structured_event_verifier.gate_interpretation`.
2. **Tests** — extend `tests/test_gan2026_agentic_run_driver.py` with registry +
   dispatch parity; existing `tests/test_gan2026_temporal_sentinel_specialist.py`
   must pass unchanged.

## Wave 2 deliverables (slice 3 — parallel)

1. **`event_completion_reasoner.run_split`** →
   `dispatch_registered_split("event_completion_reasoner", …)` via
   `run_structured_event_split`.
2. **Tests** — extend `tests/test_gan2026_agentic_run_driver.py` with registry +
   dispatch parity; existing event-completion tests must pass unchanged.

## Wave 2 deliverables (slice 1 — complete)

1. **`represented_event_normalizer.run_split`** →
   `dispatch_registered_split("represented_event_normalizer", …)` via
   `run_structured_event_split` with
   `gate_interpretation=structured_event_verifier.gate_interpretation`.
2. **Tests** — extend `tests/test_gan2026_agentic_run_driver.py` with registry +
   dispatch parity; existing `tests/test_gan2026_represented_event_normalizer.py`
   must pass unchanged.

## Wave 1 deliverables (complete)

1. **Registry scaffold** — `RegisteredAgenticStage`, `AgenticSplitHooks`,
   `dispatch_registered_split`, context dataclasses for structured-event and
   cross-model substrates.
2. **First slice** — `cross_model_challenge_adjudicator.run_split` →
   `dispatch_registered_split("cross_model_challenge_adjudicator", …)`.
3. **Tests** — `tests/test_gan2026_agentic_run_driver.py` (registry + dispatch parity);
   existing `tests/test_gan2026_cross_model_challenge_adjudicator.py` must pass unchanged.

## Recommended Wave 3 next slice

**`cross_model_structured_event_adjudicator.py`** — base adjudicator; unblocks
further cross-model variants; uses existing `cross_model_structured_event` dispatch.

## Previously recommended (completed)

**`targeted_boundary_router.py`** — migrated in Wave 3 slice 5 (this tick).

**`event_completion_reasoner.py`** — migrated in Wave 2 slice 3 (parallel).

**`temporal_sentinel_specialist.py`** — migrated in Wave 2 slice 4 (this tick).

**`represented_event_normalizer.py`** — migrated in Wave 2 slice 1.

## Verification

```bash
pytest tests/test_gan2026_agentic_run_driver.py tests/test_gan2026_targeted_boundary_router.py -q
pytest tests/test_gan2026_agentic_run_driver.py tests/test_gan2026_event_completion_reasoner.py -q
pytest tests/test_gan2026_agentic_run_driver.py tests/test_gan2026_temporal_sentinel_specialist.py -q
pytest tests/test_gan2026_agentic_run_driver.py tests/test_gan2026_represented_event_normalizer.py -q
pytest tests/test_gan2026_agentic_run_driver.py tests/test_gan2026_cross_model_challenge_adjudicator.py -q
```

Behavior-preserving criterion: row dicts and metadata from `run_split` unchanged
modulo shared metadata helper field ordering (tests assert deep equality on migrated slice).
