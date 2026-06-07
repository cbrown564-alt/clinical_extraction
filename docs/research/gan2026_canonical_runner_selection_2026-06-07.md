# Gan 2026 Canonical-Runner Selection (Phase 0 / Cleanup-Plan Phase B)

Date: 2026-06-07

Author: Claude

Status: decision record — resolves the shared "what do we keep" prerequisite
named by both
[[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
Section 2 (Phase 0) and
[[gan2026_repo_consolidation_and_cleanup_plan]] Phase B. Mechanical/structural
decision; no authorization gate required (comparison plan Section 6, Phase 0
row).

---

## Decision

| Architecture | Canonical runner | Disposition |
| --- | --- | --- |
| Deterministic | `pipeline_v1.py` (`Gan2026PipelineV1`) | confirmed — only candidate |
| Hybrid | `hybrid/reset_clinical_assessment_pipeline.py` | confirmed — already named "current focus" in `PROJECT_STATUS.md` |
| Fully LLM (One-shot variant) | **`llm/llm_only_direct_labeler.py`** | **selected as canonical base** for the one-shot LLM-only version |
| Fully LLM (Two- / Three-step variants) | **`llm/llm_only_structured_events.py`** | **selected as canonical base** for the multi-step variants |

The remaining **8** `llm_only_*` modules become superseded-candidates, subject
to the Phase C dependency audit:

- `llm_only_claim_table_selector.py`
- `llm_only_minimal_evidence_selector.py`
- `llm_only_rich_selected_state_reasoner.py`
- `llm_only_simplified_selected_state_reasoner.py`
- `llm_only_sparse_operands_selected_state_reasoner.py`
- `llm_only_structured_events_repair_ablation.py` (companion ablation for the
  canonical module — see note below; likely folds into the lineage doc rather
  than surviving as a standalone file)
- `llm_only_typed_adapter_reasoner.py`
- `llm_only_typed_operations_reasoner.py`

---

## Rationale

**Why `llm_only_direct_labeler` as the base for the One-shot LLM-only version:**

It serves as the canonical baseline for direct classification without intermediate step models, representing the most straightforward direct LLM application.

**Why `llm_only_structured_events` as the base for the Two/Three-step variants:**

1. **Output shape decomposes along family lines, not a single answer field.**
   It produces a structured intermediate ("events") with explicit per-family
   label-derivation helpers (`monthly_diary_label_from_events`,
   `breakthrough_label_from_events`, `dated_sequence_label_from_events`,
   `elapsed_since_anchor_label_from_events`, `non_epileptic_label_from_events`,
   `post_change_burst_label_from_events`, `residual_jerk_label_from_events`).
   This is structurally the right shape to chain through the reset pipeline's
   deterministic Normalize -> Project stages "verbatim" (Option A's
   requirement): the LLM selects/structures; deterministic stages still own
   representation, arithmetic, and format — the same separation of concerns
   the comparison plan's Cross-Pollination B section names as the central
   lesson to port into fully-LLM prompting.
2. **Structured base for multi-step reasoning.**
   It provides the logical structured-event extraction foundation required for the more complex 2-step and 3-step LLM architectures.
3. **Already integrated at the same seams as the canonical hybrid runner.**
   It imports `contract.label_parser`, `contract.schema_repair`, and
   `normalize` — the same shared modules the reset pipeline composes — so
   assembling the chain is "swap the Select stage," not "build new
   integration plumbing."
4. **Already wired into CLI and observatory** (`cli/llm_pipeline_cli.py`,
   `observatory/api.py` `_PIPELINE_FAMILIES`), with a mature run history
   (`experiments/gan2026_llm_only_structured_events_validation250_*`,
   `..._test_qwen36_35b_max5000_live_2026-06-04*`) including its own repair
   ablation companion — i.e., it already has the kind of ablatable,
   trace-visible structure the reset discipline requires.

**A note on `llm_only_structured_events_repair_ablation.py`**: this is a
companion ablation harness for the canonical module, not an independent
architecture candidate. It should survive Phase C only if it remains the
active mechanism for ablating the canonical runner's repair-family policies;
otherwise its contribution (the ablation methodology, not the file) belongs in
the Phase D lineage doc and the file becomes part of the same removal batch as
the other non-canonical `llm_only_*` modules.

---

## What this unblocks

- [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
  Phase 0 can now proceed: assemble the one-shot and multi-step chains and verify artifact-shape compatibility.
- [[gan2026_repo_consolidation_and_cleanup_plan]] Phase B is now complete for
  all three architecture types; Phase C (dependency audit) can proceed against
  a concrete superseded-candidate list (the 8 modules above, plus the 4
  hybrid/staged lineages already named in that plan's Phase B section).

---

## Revisability

This is a development-mechanics selection, not a frozen claim — if Phase 1's
apples-to-apples comparison shows `llm_only_structured_events` integrates
poorly with the reset back-half, that is itself a Phase-1 finding and this
selection should be revisited before Phase C removal proceeds for the other modules.
