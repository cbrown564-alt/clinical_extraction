# Project Status

Last updated: 2026-06-17

## Active Objective

Shift active implementation focus to ExECTv2 and use the Gan 2026 closeout as
the strategy template for full deterministic, LLM-only, and hybrid runs.

Gan is no longer an open `>=0.900` Purist chase. The accepted ceiling for the
current V12 fresh-evidence hybrid family is `379/450` Purist (`0.842`) on
locked `test450`. The recommended simple Gan labeler is the single GPT
structured-event pass: `364/450` Purist (`0.809`) on locked `test450`, verified
on `gpt-4.1-mini`, with no reasoner, peer ensemble, or guard layer.

ExECTv2 is now the forward workstream. Active experiments should use
`gpt-4.1-mini` for rapid loops. Qwen 3.6:35B is paused as the main loop and
moved to a separate overnight transfer track after GPT reaches
benchmark-beating architecture evidence.

## Recent Context

- Split discipline remains intact: `gan2026_split_v1` has 300 train,
  750 validation, and 450 locked holdout rows. Gan `test450` remains
  aggregate-only for development; no row-level holdout tuning is authorized.
- The Gan closeout localized the hard residual to unknown-vs-rate and
  cluster-burden clinical reasoning. Its durable methodology is source-near
  structured state, exact evidence, component attribution, validation hard
  slices, benchmark-format ablations, family-aware promotion gates, and
  conservative claim language.
- The GPT-first ExECTv2 strategy lives at
  `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`.
  Current freeze blockers are rules-only all-9 below target, LLM-only all-9
  only covered by the negative single-pass baseline rather than per-entity
  frames, and hybrid evidence still SF-only.
- The first deterministic all-9 dev scorecard is registered at
  `experiments/exectv2_deterministic_all9_dev_20260617.md`. It scores all nine
  entities with active rules for Prescription, Investigations, Diagnosis, and
  SeizureFrequency. Overall all-9 remains below freeze target because several
  entities are absent or early-stage.
- Prescription has an ADR-backed scorecard split: one clinical headline for
  regimen recovery plus diagnostics for benchmark projection, defaults, future
  plans, weight-based dosing, and rescue handling. The clinical headline is F1
  `0.9072`; name/dose/frequency diagnostics are `0.9257`/`0.9343`/`0.9307`;
  ordinary complete tuple F1 is `0.9096`.
- Prescription now has a code-backed benchmark projection ladder in the
  deterministic all-9 scorecard: phrase scope `0.3069`, semantic-without-CUI
  `0.3020`, benchmark-with-CUI `0.3020`, clinical medication identity `0.9257`,
  `DrugName`+CUI projection `0.7921`, source-stated frequency `0.6523`, and
  guideline-defaulted frequency `0.1760`.
- Shared active-entity benchmark projection is code-backed in
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/benchmark_projection.py`.
  Prescription, Investigations, and Diagnosis deterministic rules reuse that
  projection surface; the regenerated deterministic all-9 scorecard had no
  metric drift apart from the new diagnostic table.

## Active Priorities

1. Execute the GPT-first ExECTv2 strategy: deterministic all-9 baseline,
   per-entity LLM-only structured mention frames, and hybrid candidate
   assessment over live candidate sets.
2. Target benchmark-beating dev evidence before any new full-200 audit:
   overall `0.87` per-item / `0.90` per-letter, plus per-entity tables,
   evidence/schema reliability, semantic-vs-CUI gaps, and ablations.
3. Keep Qwen 3.6:35B as a separate overnight transfer track. Resume dev25/dev140
   only after the GPT architecture shape has produced strong, attributable
   ExECTv2 evidence.

## Work Board

### Now

- Use the new Prescription benchmark projection ladder to attack diagnostic gaps
  without moving the clinical headline: improve `DrugName`+CUI projection,
  guideline-defaulted frequency recall, and phrase-scope policy visibility.
- Improve Investigations exactness and add the next structured deterministic
  entity engines with rule-family/CUI ablations.

### Next

- Extend shared CUI/benchmark-format projection beyond the active deterministic
  entities and wire the architecture-agnostic `project_cuis` post-step into
  LLM-only and hybrid pilots; keep semantic-vs-benchmark ablations explicit.
- Run GPT per-entity LLM-only pilots for the entities most likely to move the
  overall benchmark fastest: Prescription, Investigations, Diagnosis, then
  SeizureFrequency as the hard transfer check.
- Extend the hybrid live candidate-assessment pattern from SF to all nine
  entities, using deterministic and GPT mention-frame outputs as candidate
  sources rather than hidden final truth.
- Add an ExECTv2 error ledger with projection gap families before promoting any
  architecture: phrase scope, CUI, attribute bundle, split/merge, false current
  regimen, missed current regimen, source-stated/defaulted frequency, future
  medication, weight-based dosing, and rescue convention mismatch.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, or post-test tuning remain
  blocked without explicit authorization and a frozen protocol.
- New ExECTv2 full-200 benchmark-facing audits are blocked until a GPT-first
  architecture has benchmark-beating dev evidence and a predeclared aggregate
  readout.
- Gan historical branches V1, V3, V4, V7, V8, V9, V10, V11, E3, and E4 remain
  blocked from escalation except as comparison artifacts.

### Backlog

- Resume ExECTv2 Qwen event-frame dev25/dev140 as an overnight transfer track
  after GPT-first architecture choices are clearer.
- Run the one-peer Qwen reasoner rung as the stronger A4 variant if Gan frontier
  curiosity resumes.
- Optional: turn the simplest Gan near-ceiling analysis into a compact
  architecture-cost table for paper use.

### Done Recently

- 2026-06-17: Added the Prescription benchmark projection ladder to
  `score_prescription_benchmark_projection()`, rendered it in the deterministic
  all-9 scorecard, regenerated the JSON/Markdown artifacts and registry row, and
  verified focused ExECTv2 tests plus Ruff pass.
- 2026-06-17: Added shared active-entity ExECTv2 benchmark projection
  (`benchmark_projection.py`) with tests, refactored deterministic all-9
  Prescription/Investigations/Diagnosis CUI attachment to reuse it, regenerated
  the deterministic all-9 scorecard with no metric drift, and verified `1559`
  tests pass.
- 2026-06-17: Implemented the first deterministic all-9 ExECTv2 baseline and
  scorecard generator; Prescription now reports a clinical headline at `0.9072`
  and separate diagnostics for name, dose, frequency, rescue, future medication,
  weight-based dosing, phrase/CUI, and default-frequency surfaces.
- 2026-06-17: Documented the Prescription component-vs-benchmark scoring split
  and ADR-backed policy in
  `docs/research/exectv2_prescription_component_vs_benchmark_scoring_2026-06-17.md`.
- 2026-06-17: Added the code-backed GPT-first ExECTv2 architecture-loop status
  report and generated
  `experiments/exectv2_gpt_first_architecture_loop_status_20260617.md`.
- 2026-06-17: Wrote the GPT-first ExECTv2 full-architecture strategy and moved
  Qwen to an overnight transfer track.
- 2026-06-14 to 2026-06-17: Closed the Gan strand: V12 v0.4 frozen `test450`
  reached `379/450` Purist, V12 v0.6 safety was rejected at `351/450`, the
  accepted ceiling became `379/450`, the simple single-GPT structured-event pass
  became the recommended Gan architecture, and the closeout synthesis captured
  the paper-facing lessons.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- New Gan holdout-facing runs require explicit frozen-protocol authorization.
- Keep architecture claims attribution-clean across `rules_only`, `llm_only`,
  and `hybrid`.
- Treat Gan-specific rules and benchmark-format repairs as controlled variables,
  not hidden implementation detail.

## Core Artifacts

- `docs/research/gan2026_research_closeout_synthesis_2026-06-17.md`
- `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`
- `docs/research/exectv2_prescription_component_vs_benchmark_scoring_2026-06-17.md`
- `experiments/exectv2_gpt_first_architecture_loop_status_20260617.md`
- `experiments/exectv2_deterministic_all9_dev_20260617.md`
- `docs/research/gan2026_f1_dynamic_workflow_night_synthesis_2026-06-16.md`
- `docs/research/gan2026_simplest_near_ceiling_architecture_results_2026-06-16.md`
- `docs/research/exectv2_llm_only_qwen36_event_frame_synthesis_2026-06-16.md`
- `experiments/gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16.md`
- `experiments/RUN_INDEX.md`
