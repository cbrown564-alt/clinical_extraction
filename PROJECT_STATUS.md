# Project Status

Last updated: 2026-06-24

## Active Objective

Satellite 13 remains the primary ExECTv2 research focus, but the direct
de-duplicated clinical-fact LLM-only path has now plateaued. Phase 0 through
Phase 6 are complete. The DeepSeek/Qwen rollout was reactivated for the stated
`decision_table_sf_inv` transfer question and is now complete; no model-swap
condition closes the gap to the v08 hybrid. The post-plateau Prescription
projection pilot remains separate from hybrid-rescue and verifier-filtered
score lines.

## Current Read

Decision 0027 established clinical recovery as the ExECTv2 headline and
projection as an artifact layer. ADR 0033 now applies that framing to LLM-only
development: the active target is de-duplicated clinical-fact recovery, not
strict full-schema annotation reproduction.

The controls are fixed. Bare rich-schema LLM-only `single_call_clean_render_ids`
scored `0.334`/`0.339` strict F1 for GPT-4.1-mini/Qwen on dev140 but
`0.713`/`0.725` on de-duplicated `clinical_headline`; v08 hybrid remains the
dev140 clinical-recovery control at `0.9155`. The active scoreboard is
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`.

Phases 2-4 built the `single_call_dedup_facts` routes and localized the
LLM-only plateau. GPT-4.1-mini scored `0.710` with the single prompt, compact
per-family prompting reached `0.796` on dev25, and the best
`decision_table_sf_inv` dev140 readout reached only `0.729`. The remaining gap
is prediction-bearing Diagnosis ontology/granularity and SeizureFrequency
state/unit selection, not infrastructure. Readouts:
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase3_single_prompt_plateau_2026-06-23.md`,
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_fallback_plateau_2026-06-24.md`,
and
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_decision_table_prompt_probe_2026-06-24.md`.

Phase 6 then ran the same mixed `decision_table_sf_inv` dev140 configuration on
DeepSeek and Qwen. DeepSeek reached `0.745` clinical headline F1, Qwen reached
`0.694`, and GPT-4.1-mini remains `0.729`; all strict benchmark F1s stayed near
`0.13`. The rollout report is
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase6_model_rollout_2026-06-24.md`.

Phase 5 added the deterministic projection taxonomy
(`docs/design/deterministic_projection_rule_taxonomy.md`) and the Prescription
pilot report
(`docs/experiments/exectv2/key_entities/exectv2_phase5_prescription_projection_pilot_2026-06-24.md`).
On Phase 3 GPT-4.1-mini dev140 replay, allowed Prescription projection moved
clinical headline only `0.812` -> `0.814`, while benchmark+CUI moved `0.000` ->
`0.180` and Drug+CUI moved `0.000` -> `0.907`. Boundary actions were counted
but not applied to the LLM-only line: missed-medication rescue `21`,
missing dose/frequency completion `8`, duplicate-regimen collapse `20`, and
unsupported-medication rejection `35`.

## Active Priorities

1. Keep Satellite 13 Phase 5 as the completed projection-aware Prescription
   pilot: use it to explain benchmark-convention effects, not as a hidden
   clinical-recovery rescue.
2. Treat `clinical_headline` de-duplicated clinical recovery as the primary
   LLM-only optimization target; report strict benchmark results only as a
   required diagnostic/comparability surface.
3. Preserve attribution discipline: the model must emit every scored fact;
   deterministic code may validate evidence and perform tagged
   meaning-preserving projection, but must not add, select, or reject clinical
   facts inside the LLM-only score line.
4. Treat Phase 6 as a completed model-transfer readout; further improvement
   needs a new architecture, ontology-supervision experiment, or explicitly
   separated projection/hybrid score line.

## Work Board

### Now

- Keep the Phase 3-6 direct LLM-only runs as plateau comparators with fixed
  clinical-recovery claim language.

### Next

- If a paper-facing ExECTv2 audit is proposed, predeclare the split/surface,
  scorer, stop rule, and row-inspection boundary before running it.
- If continuing Satellite 13, choose a new declared path: ontology supervision,
  hybrid/selector ownership, or projection-aware analysis.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs a benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

- 2026-06-24: Completed Satellite 13 Phase 6 model rollout for the
  `decision_table_sf_inv` dev140 transfer question. DeepSeek reached `0.745`
  clinical headline F1, Qwen reached `0.694`, and neither changed the plateau
  conclusion.
- 2026-06-24: Completed Satellite 13 Phase 5 with the deterministic projection
  taxonomy and Prescription projection pilot. Allowed projection mainly restored
  benchmark/CUI convention visibility (`0.000` -> `0.180`) while clinical
  headline barely moved (`0.812` -> `0.814`); hybrid rescue and verifier
  candidates stayed separated and unapplied.
- 2026-06-24: Completed Satellite 13 Phase 4 as an LLM-only fallback plateau,
  added error analysis, and tested decision-table prompt guidelines. Best
  prompt-guideline dev140 score was `0.729`.
- 2026-06-23: Completed Satellite 13 Phases 0-3: ADR 0033, rich-schema archive
  cleanup, the `single_call_dedup_facts` route/adapter/tests, and the
  single-prompt plateau report.
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
