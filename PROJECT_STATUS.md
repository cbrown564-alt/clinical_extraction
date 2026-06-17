# Project Status

Last updated: 2026-06-17

## Active Objective

ExECTv2 is now the forward workstream. Use the Gan 2026 closeout as the strategy
template for full deterministic, LLM-only, and hybrid runs: source-near state,
exact evidence, component attribution, benchmark-format ablations, and
family-aware promotion gates.

Active ExECTv2 experiments should use `gpt-4.1-mini` for rapid loops. Qwen
3.6:35B is paused as the main loop and kept as a separate overnight transfer
track after GPT reaches benchmark-beating architecture evidence.

## Recent Context

- Split discipline remains intact. Gan `test450` remains aggregate-only for
  development; ExECTv2 full-200 audits are blocked until a GPT-first architecture
  has benchmark-beating dev evidence and a predeclared readout.
- Gan is no longer an open `>=0.900` Purist chase. The accepted ceiling for the
  V12 fresh-evidence hybrid family is `379/450` Purist (`0.842`) on locked
  `test450`; the recommended simple Gan labeler is the single GPT structured
  event pass at `364/450` Purist (`0.809`).
- The GPT-first ExECTv2 strategy lives at
  `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`.
  Current freeze blockers are rules-only all-9 still below target, LLM-only all-9
  only covered by the negative single-pass baseline rather than per-entity
  frames, and hybrid evidence still SF-only.
- The deterministic all-9 dev scorecard is registered at
  `experiments/exectv2_deterministic_all9_dev_20260617.md`. It now scores all
  nine entities with active deterministic rules and shared benchmark projection:
  `0.3625` benchmark item / `0.6747` benchmark letter on dev. PatientHistory is a
  conservative substrate at `0.2087` item / `0.5475` letter with `157/157`
  emitted PatientHistory mentions carrying CUI and an explicit phrase/attribute/
  CUI error ledger.

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

- Extend shared CUI/benchmark-format projection beyond the deterministic
  rules-only surface and wire the architecture-agnostic `project_cuis` post-step
  into LLM-only and hybrid pilots; keep semantic-vs-benchmark ablations explicit.

### Next

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

### Backlog

- Resume ExECTv2 Qwen event-frame dev25/dev140 as an overnight transfer track
  after GPT-first architecture choices are clearer.

### Done Recently

- 2026-06-17: Added the remaining deterministic PatientHistory substrate with
  compact concept anchors, temporal attributes, febrile-seizure negation, finite
  CUI projection, and a scorecard error ledger. Regenerated the deterministic
  all-9 dev artifacts and registry row: benchmark overall `0.3625` item /
  `0.6747` letter; PatientHistory `0.2087` item / `0.5475` letter. Verified
  `1572` tests pass and Ruff on touched files; full-project Ruff remains blocked
  by pre-existing lint in old experiment/test surfaces.
- 2026-06-17: Added deterministic WhenDiagnosed, BirthHistory, and EpilepsyCause
  engines with shared benchmark CUI projection; earlier the same all-9 baseline
  added Prescription, Investigations, Diagnosis, Onset, the Prescription
  ADR-backed clinical headline, and the benchmark projection ladder.
- 2026-06-14 to 2026-06-17: Closed the Gan strand and wrote the GPT-first
  ExECTv2 architecture strategy; Qwen moved to an overnight transfer track.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- New Gan holdout-facing runs require explicit frozen-protocol authorization.
- Keep architecture claims attribution-clean across `rules_only`, `llm_only`,
  and `hybrid`.
- Treat Gan-specific rules and benchmark-format repairs as controlled variables,
  not hidden implementation detail.

## Core Artifacts

- `experiments/exectv2_deterministic_all9_dev_20260617.md`
- `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`
- `docs/research/gan2026_research_closeout_synthesis_2026-06-17.md`
- `experiments/RUN_INDEX.md`
