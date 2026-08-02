# Decision 0048 retention slice: candidate-only prompt draft notes

Date: 2026-08-02  
Status: complete  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md)  
Scope: three working prompt draft notes listed in ACTIVE_ROADMAP as
candidate-only retention candidates.

This slice removed working draft notes whose durable content is owned by
protocols, exemplar packs, prompt-contract snapshots, panel reports, and
research threads. No protocol, exemplar pack, residual analysis, research
report, or machine artifact was deleted.

## Per-file decisions

| File | Decision | Evidence |
| --- | --- | --- |
| `docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_draft_notes_2026-07-31.md` | **Delete** | Panel complete under [dev140 protocol](../../experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md) and [dev140 report](../../experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_2026-07-31.md). B/C drafting rationale and row cues live in [exemplar pack](../../experiments/exectv2/reliability/exectv2_luna_prompt_variants_exemplar_pack_2026-07-31.md). Rendered variants are pinned in prompt-contract snapshots. Plain-language audit was process metadata, not a named claim. |
| `docs/experiments/gan2026/gan2026_luna_prompt_variants_draft_notes_2026-07-30.md` | **Delete** | Stale status ("no Luna A/B/C runs yet") contradicted the finalized [dev750 protocol](../../experiments/gan2026/gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md) and [research report](../../research/gan2026_luna_prompt_variants_report_2026-07-30.md). Drafting aid, row briefs, and slice targets are in [exemplar pack](../../experiments/gan2026/gan2026_luna_prompt_variants_exemplar_pack_2026-07-30.md); snapshots and panel artifacts retain prompt identity. |
| `docs/experiments/gan2026/gan2026_deepseek_unknown_prompt_draft_notes_2026-07-31.md` | **Delete** | Negative stop is recorded in [thread](../../research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md), [A/U run protocol](../../experiments/gan2026/gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md), and [UNK-slice pilot compare](../../../experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json). Phase 2 intent is in the parent [unknown-competence protocol](../../experiments/gan2026/gan2026_deepseek_unknown_competence_protocol_2026-07-31.md); candidate U text is in `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.8_deepseek_unknown.txt`. Draft bullet list did not add claim evidence beyond those owners. |

## Inbound links retargeted

| Source | Change |
| --- | --- |
| `docs/experiments/exectv2/reliability/exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md` | Removed draft-notes line; exemplar pack remains the drafting aid. |
| `docs/experiments/gan2026/gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md` | Removed draft-notes line; exemplar pack remains in drafting-aid section. |
| `docs/experiments/gan2026/gan2026_deepseek_unknown_competence_protocol_2026-07-31.md` | Removed Phase 2 draft link; Phase 2 run protocol is the owner. |
| `docs/experiments/gan2026/gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md` | Removed draft-notes line. |
| `docs/THREAD_MAP.md` | DeepSeek path now goes A/U run protocol → roadmap. |
| `docs/NAVIGATION.md` | Replaced draft-notes link with UNK-slice pilot compare artifact. |

## Kept files

None from this slice. All three drafts were deleted after link retargeting.

## Claim boundary

Documentation-only cleanup. No source, scorer, prompt default, repair policy,
selected evidence, or clinical behavior changed. Recovery is available from Git
history.
