# Project Status

Last updated: 2026-06-17

## Active Objective

Shift active implementation focus to ExECTv2 and use the Gan 2026 closeout as
the strategy template for full deterministic, LLM-only, and hybrid runs.

Gan is no longer an open `>=0.900` Purist chase. The accepted ceiling for the
current V12 fresh-evidence hybrid family is `379/450` Purist (`0.842`) on
locked `test450`. The recommended simple Gan labeler is the single GPT
structured-event pass: `364/450` Purist (`0.809`) on locked `test450`, verified
on `gpt-4.1-mini`, with no reasoner, peer ensemble, or guard layer. The full
3-model + reasoner + guard stack buys only `+15` test rows for much higher
operational and attribution complexity.

The Gan closeout and reliability scorecard are now strategy inputs for ExECTv2:
source-near structured state, exact evidence, component attribution,
benchmark-format ablations, family-aware promotion gates, and conservative
claim language. Active ExECTv2 experimentation should use `gpt-4.1-mini` for
rapid loops. Qwen 3.6:35B is paused as the main loop and moved to a separate
overnight transfer track after GPT reaches benchmark-beating architecture
evidence.

## Recent Context

- Split discipline remains intact: `gan2026_split_v1` has 300 train,
  750 validation, and 450 locked holdout rows. Gan `test450` remains
  aggregate-only for development; no row-level holdout tuning is authorized.
- V12 v0.4 is the best completed frozen Gan holdout:
  `379/450` Purist, `394/450` Pragmatic, with `0` call failures and `0`
  parse/schema/label failures. V12 v0.6 + safety-v0.9 was rejected at
  `351/450` Purist.
- The 2026-06-16 dynamic workflow closed the `0.90` chase. Selector saturation,
  deterministic rewrite regressions, and KG/family-gate failures all localized
  the hard residual to unknown-vs-rate and cluster-burden clinical reasoning.
- The simplest near-ceiling analysis shifted the default recommendation:
  single GPT structured-event pass (`661/750` validation, `364/450` test) over
  the full V12 stack (`682/750` validation, `379/450` test) unless the extra
  `+15` holdout rows justify the added complexity.
- ExECTv2 is the forward workstream. The new GPT-first strategy lives at
  `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`.
  It pauses Qwen as an overnight transfer track and prioritizes
  `gpt-4.1-mini` loops across deterministic all-9, per-entity LLM-only, and
  hybrid candidate-assessment architectures.

## Gan Research Questions To Close Out

- Can deterministic rules alone solve Gan seizure-frequency extraction?
  They are a strong transparent floor and controlled variable, but validation
  overstated holdout generalisation.
- Can a single LLM own the clinical interpretation?
  Direct final-label prediction was too weak (`~0.71-0.72` mini `test450`);
  structured-event extraction was much stronger (`0.809` test) because it
  forced evidence-grounded intermediate state.
- Do hybrid or agentic components close the gap?
  They help modestly. V12 reaches `0.842`, but the gain over the single
  structured-event pass is small relative to its complexity.
- Where is the hard residual?
  Unknown-vs-rate and cluster-burden reasoning: the system over-infers habitual
  rates or seizure-free durations from last-event-only, provoked/transient,
  adherence-confounded, or underspecified evidence.
- What methodology survived?
  Component attribution, exact evidence checks, validation hard slices,
  synthetic/adversarial panels, held-out-family CV, and frozen aggregate-only
  test audits were more informative than broad metric chasing.
- What is the paper-facing lesson?
  The durable contribution is auditable modular extraction and disciplined
  evaluation, not a near-perfect Gan score claim.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence, selected
  events, or transitions for development.
- New Gan holdout-facing runs require explicit frozen-protocol authorization.
- Keep architecture claims attribution-clean across `rules_only`, `llm_only`,
  and `hybrid`.
- Treat Gan-specific rules and benchmark-format repairs as controlled variables,
  not hidden implementation detail.

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

- Start the GPT-first ExECTv2 implementation loop from
  `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`.
  First target: full run matrix design and the next small GPT dev experiment.

### Next

- Build or extend shared CUI/benchmark-format projection for the active ExECTv2
  entities, with semantic-vs-benchmark ablation kept explicit.
- Run GPT per-entity LLM-only pilots for the entities most likely to move the
  overall benchmark fastest: Prescription, Investigations, Diagnosis, then
  SeizureFrequency as the hard transfer check.
- Extend the hybrid live candidate-assessment pattern from SF to all nine
  entities, using deterministic and GPT mention-frame outputs as candidate
  sources rather than hidden final truth.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, or post-test tuning remain
  blocked without explicit authorization and a frozen protocol.
- Gan historical branches V1, V3, V4, V7, V8, V9, V10, V11, E3, and E4 remain
  blocked from escalation except as comparison artifacts.
- New ExECTv2 full-200 benchmark-facing audits are blocked until a GPT-first
  architecture has benchmark-beating dev evidence and a predeclared aggregate
  readout.

### Backlog

- Resume ExECTv2 Qwen event-frame dev25/dev140 as an overnight transfer track
  after GPT-first architecture choices are clearer.
- Run the one-peer Qwen reasoner rung as the stronger A4 variant if Gan frontier
  curiosity resumes. DeepSeek solo underperformed the bare single GPT pass, but
  Qwen performed better than DeepSeek as a standalone structured-event source,
  so GPT+Qwen is the remaining one-peer upper bound.
- Optional: turn the simplest near-ceiling analysis into a compact
  architecture-cost table for paper use.
- Optional: summarize V12 report profile dumps if future reports need them.

### Done Recently

- 2026-06-17: Wrote the GPT-first ExECTv2 full-architecture strategy
  (`docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`),
  translating the Gan closeout and reliability scorecard into deterministic,
  LLM-only, and hybrid ExECTv2 practice; Qwen moved to an overnight transfer
  track.
- 2026-06-17: Wrote the Gan research closeout synthesis
  (`docs/research/gan2026_research_closeout_synthesis_2026-06-17.md`): full
  experiment accounting (architecture arc, RQ1–RQ10, hard residual, surviving
  methodology + negatives), the six central research questions with answers, and
  distilled insights. Closes the Gan strand pending ExECTv2 focus.
- 2026-06-14: Ran the authorized V12 v0.4 frozen aggregate-only `test450` audit:
  `379/450` Purist, `394/450` Pragmatic, no call or parse failures, and no
  row-level holdout analysis.
- 2026-06-15: Rejected V12 v0.6 + safety-v0.9 on frozen `test450` at
  `351/450` Purist; built selector/component-repair evidence showing remaining
  selector headroom was mostly exhausted.
- 2026-06-16: Accepted `379/450` as the honest ceiling for the current V12/mini
  family and recorded unknown-vs-rate as the central unresolved clinical
  reasoning limit.
- 2026-06-16: Selected the single GPT structured-event pass (`364/450` on
  `test450`) as the recommended simple Gan architecture.
- 2026-06-16: Advanced ExECTv2 Qwen `llm_only` event-frame work through v0.19
  dev10 (`0.8780` strict SF F1), pending dev25 and dev140.

## Core Artifacts

- `docs/research/gan2026_research_closeout_synthesis_2026-06-17.md` (closeout synthesis)
- `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`
- `docs/research/gan2026_f1_dynamic_workflow_night_synthesis_2026-06-16.md`
- `docs/research/gan2026_simplest_near_ceiling_architecture_results_2026-06-16.md`
- `docs/research/gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14.md`
- `docs/research/exectv2_llm_only_qwen36_event_frame_synthesis_2026-06-16.md`
- `experiments/gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16.md`
- `experiments/gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16.md`
- `experiments/RUN_INDEX.md`
