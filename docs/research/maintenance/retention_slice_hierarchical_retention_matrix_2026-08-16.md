# Retention slice: Hierarchical 3-slot taxonomy and architecture/prompt/rules retention matrix

Date: 2026-08-16
Status: **taxonomy complete**; candidate table follows in
[retention_candidate_table_2026-08-16.md](retention_candidate_table_2026-08-16.md).
ExECT current-hybrid prompt slots were later assigned in
[prompt variant slots](../exectv2/prompt_variant_slots_2026-08-16.md)
(`v0.9.24`, cheap stack, mention-unit v2). This slice records the
taxonomy; that note owns the ExECT prompt fill. Agentic/multi-agent
exploration closed with canonical owner and research reports restored.
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md)
Ledger owner: [REGENERATION.md](../../REGENERATION.md)

## What this slice did

1. **Formalized the Hierarchical 3-Slot Retention Taxonomy in `docs/REGENERATION.md`**:
   - **3 Core Methods** (both tasks): `llm_with_rules` (Hybrid), `llm_only` (Pure model), `rules_only` (Deterministic).
   - **3 Architecture/Pipeline Variants (`llm_with_rules`)**:
     - Slot 1: Current one-call structured hybrid.
     - Slot 2: GEPA program / verify-stage.
     - Slot 3: Agentic / Multi-Agent ceiling evaluation.
   - **3 Prompt Variants (per hybrid task)**:
     - ExECT: later filled as `v0.9.24` (selected), cheap stack
       (`v0.9.40`), and mention-unit v2. `v08` stays the reference
       cell, not a current-hybrid prompt.
     - Gan: `v0.5` matched panel baseline, `Luna` prompt variants ablation, and `DeepSeek Unknown` / `Gemini 3.7` successor.
   - **3 Deterministic Rules & Projection Variants**:
     - Slot 1: Production `rules_only` baseline.
     - Slot 2: Hybrid state projection and bounded repair ruleset.
     - Slot 3: Attribution, rescue provenance, and removal ablation studies.

2. **Restored Agentic / Multi-Agent Canon & Research Evidence (Slot 3 Closure)**:
   - Created canonical claim owner [`docs/canon/11_agentic_exploration.md`](../../canon/11_agentic_exploration.md) documenting empirical findings (Gan hard50 ceiling & dynamism advantage, gate failure due to clean-row regressions, and negative comparison boundary).
   - Restored [`docs/research/gan2026/gan2026_agentic_redo_results_2026-07-01.md`](../gan2026/gan2026_agentic_redo_results_2026-07-01.md).
   - Restored [`docs/research/shared/exploratory_research_directions_multiagent_review_2026-07-01.md`](../shared/exploratory_research_directions_multiagent_review_2026-07-01.md).
   - Updated canon index in [`docs/canon/README.md`](../../canon/README.md).

3. **Safeguards & Verifications Respected**:
   - Zero model calls made.
   - Zero locked rows inspected.
   - Verified retained evidence manifest via `scripts/check_retained_evidence_manifest.py`.
