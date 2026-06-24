# Project Status

Last updated: 2026-06-24

## Active Objective

Satellite 13 remains the primary ExECTv2 research focus, but the direct
de-duplicated clinical-fact LLM-only path has plateaued. Phase 0 through Phase
6 are complete, including the DeepSeek/Qwen `decision_table_sf_inv` transfer
readout. The final project consolidation plan is complete through Phase 4 setup:
canonical indexes/reports, frontend ExECTv2 MVP, non-canonical quarantine,
shared final-consolidation builder, cross-dataset reliability scorecard tab,
simplified Gan component-ablation surface, and replay/API tests are in place.
ExECTv2 component ablation infrastructure is now the declared next phase.

## Current Read

Decision 0027 established clinical recovery as the ExECTv2 headline and
projection as an artifact layer. ADR 0033 applies that framing to LLM-only
development: the target is de-duplicated clinical-fact recovery, not strict
full-schema annotation reproduction.

The controls are fixed. Bare rich-schema LLM-only remains far below the v08
hybrid dev140 clinical-recovery control (`0.9155`). The active scoreboard is
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`.

The ExECTv2 component replay artifacts now exist as layered aggregate ladders
for v08, v09 partial hybrid, DeepSeek v0.9.16, and Qwen v0.9.22 dev140. Each
architecture is shown across raw candidates, source scoring, evidence
validation, dictionary normalization, residual semantic additions, final
assembly, and headline projection. The most visible gains come from dictionary
normalization, residual semantic additions, and headline projection.

Phases 2-6 localized the LLM-only plateau. The best
`decision_table_sf_inv` dev140 readout reached `0.729`; DeepSeek reached
`0.745`; Qwen reached `0.694`; all strict benchmark F1s stayed near `0.13`.
The remaining gap is prediction-bearing Diagnosis ontology/granularity and
SeizureFrequency state/unit selection, not infrastructure.

Phase 5 added the deterministic projection taxonomy and Prescription pilot.
Allowed projection barely moved clinical headline (`0.812` -> `0.814`);
hybrid rescue and verifier candidates remain separated and unapplied.

## Active Priorities

1. Keep Satellite 13 Phase 5 as a projection-aware Prescription pilot, not a
   hidden clinical-recovery rescue.
2. Treat `clinical_headline` de-duplicated clinical recovery as the primary
   LLM-only optimization target; report strict benchmark results only as a
   diagnostic/comparability surface.
3. Preserve attribution discipline: the model emits every scored fact;
   deterministic code may validate evidence and perform tagged
   meaning-preserving projection, but must not add, select, or reject clinical
   facts inside the LLM-only score line.
4. Keep Reliability Scorecard separate from Component Impact: reliability is
   trust evidence; component impact must be ablation/delta evidence.

## Work Board

### Now

- Keep Phase 3-6 direct LLM-only runs as plateau comparators with fixed
  clinical-recovery claim language.
- Use the redesigned ExECTv2 Component Impact page as the aggregate layer
  replay surface across v08, v09, DeepSeek, and Qwen.

### Next

- Predeclare split/surface, scorer, stop rule, and row-inspection boundary
  before any paper-facing ExECTv2 audit.
- Extend ExECTv2 component ablations from saved layer ladders to true
  one-component-off rows only when upstream candidates, family deltas,
  transition counts, and provenance tags can be preserved cleanly.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs a benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

- 2026-06-24: Generated ExECTv2 replay-only layered component-impact artifacts
  for v08, v09, DeepSeek, and Qwen dev140: aggregate JSON/JSONL/Markdown,
  frontend payload, and 28 layer YAML configs. The redesigned Component Impact
  page now shows architecture ladders, layer deltas, and selected-run details.
  The replay is no-call, aggregate-only, and leaves full-200/holdout row-level
  guardrails unchanged.
- 2026-06-24: Completed final project consolidation Phase 4: split Reliability
  Scorecard into its own cross-dataset tab for Gan and ExECTv2, simplified Gan
  Component Impact into baseline-vs-ablation deltas, documented the ExECTv2
  replay-ablation contract, and kept ExECTv2 Component Impact provenance-only
  until replay artifacts exist.
- 2026-06-24: Completed final project consolidation Phase 3: shared ExECTv2
  final-consolidation builder, static and live reliability scorecard JSON,
  ExECTv2 scorecard surface, and parser/static/API replay tests. No
  optional non-GPT dev140 rerun or full-200/holdout protocol was started.
- 2026-06-24: Completed final project consolidation Phase 2 on
  `codex/final-consolidation-phase2`: canonical hashes/index entries,
  ExECTv2 frontend MVP, frontend lint/type fixes, and documented
  `experiments/_archive/` quarantine policy.
- 2026-06-24: Completed Satellite 13 Phases 4-6: fallback plateau, projection
  taxonomy and Prescription pilot, and DeepSeek/Qwen model-transfer readout.
- 2026-06-23: Completed Satellite 13 Phases 0-3: ADR 0033, rich-schema archive
  cleanup, `single_call_dedup_facts` route/adapter/tests, and single-prompt
  plateau report.
- 2026-06-22: Added the LLM repair-attribution protocol and completed the v08
  all-four ExECTv2 consolidation work.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict
  benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development
  without explicit authorization and a frozen protocol.
- Keep deterministic projection, hybrid rescue, and verifier rejection
  provenance-stamped and separated in reported score lines.
