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
  Current freeze blockers are rules-only all-9 still below target, PatientHistory
  still absent deterministically, LLM-only all-9 only covered by the negative
  single-pass baseline rather than per-entity frames, and hybrid evidence still
  SF-only.
- The deterministic all-9 dev scorecard is registered at
  `experiments/exectv2_deterministic_all9_dev_20260617.md`. It scores all nine
  entities with active rules for Prescription, Investigations, Diagnosis, Onset,
  and SeizureFrequency. Overall all-9 remains below freeze target because
  BirthHistory, EpilepsyCause, PatientHistory, and WhenDiagnosed are absent.
- Prescription has an ADR-backed scorecard split: one clinical headline for
  regimen recovery plus diagnostics for benchmark projection, defaults, future
  plans, weight-based dosing, and rescue handling. The clinical headline is F1
  `0.9072`; name/dose/frequency diagnostics are `0.9257`/`0.9343`/`0.9307`;
  ordinary complete tuple F1 is `0.9096`.
- Prescription now has a code-backed benchmark projection ladder in the
  deterministic all-9 scorecard: phrase scope `0.3069`, semantic-without-CUI
  `0.3020`, benchmark-with-CUI `0.3020`, clinical medication identity `0.9257`,
  `DrugName`+CUI projection `0.9158`, source-stated frequency `0.9307`, and
  no remaining guideline-defaulted frequency items on dev under the source-context
  diagnostic policy.
- Shared active-entity benchmark projection is code-backed in
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/benchmark_projection.py`.
  Prescription, Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory,
  and EpilepsyCause deterministic rules now reuse that projection surface. The
  regenerated deterministic all-9 scorecard improved benchmark overall to
  `0.3309` item / `0.6072` letter on dev; new per-entity benchmark item F1s are
  WhenDiagnosed `0.8182`, BirthHistory `0.5574`, and EpilepsyCause `0.5333`.

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

- Add the remaining deterministic PatientHistory substrate and error ledger,
  keeping phrase scope, temporal attributes, negation, and CUI projection
  ablations explicit.

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

- 2026-06-17: Added deterministic WhenDiagnosed, BirthHistory, and EpilepsyCause
  engines with shared benchmark CUI projection, regenerated the deterministic
  all-9 scorecard/registry row, and verified `1571` tests pass plus Ruff on
  touched files. Full-project Ruff remains blocked by pre-existing lint in old
  experiment/test surfaces.
- 2026-06-17: Built the deterministic all-9 ExECTv2 baseline through
  Prescription, Investigations, Diagnosis, and Onset; added the Prescription
  ADR-backed clinical headline and benchmark projection ladder; regenerated the
  JSON/Markdown artifacts and registry row across those steps.
- 2026-06-17: Added the code-backed GPT-first ExECTv2 architecture-loop status
  report, wrote the full-architecture strategy, and moved Qwen to an overnight
  transfer track.
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
