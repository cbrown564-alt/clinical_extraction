# Project Status

Last updated: 2026-06-24

## Active Objective

Satellite 13 remains the primary ExECTv2 research focus, but the direct
de-duplicated clinical-fact LLM-only path has now plateaued. Phase 0 through
Phase 5 are complete. No DeepSeek/Qwen rollout is promoted because no
GPT-4.1-mini fallback configuration cleared the dev25 gate. The post-plateau
Prescription projection pilot is complete and keeps LLM-only projection,
hybrid-rescue, and verifier-filtered score lines separate.

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

Phase 2 added `single_call_dedup_facts` and fixed canonical headline reporting.
Phase 3 single-prompt GPT-4.1-mini plateaued at dev140 `0.710` with evidence
validity `0.9613`. Phase 4 per-family prompting improved the dev25 gate to
`0.796` but did not beat the Phase 3 dev25 gate (`0.800`) or approach `>0.900`.
Readouts: `docs/experiments/exectv2/key_entities/exectv2_dedup_phase3_single_prompt_plateau_2026-06-23.md`
and `docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_fallback_plateau_2026-06-24.md`.

The Phase 4 error analysis and decision-table prompt probe show the plateau is
prediction-bearing rather than infrastructural. Diagnosis failures are mostly
ontology/granularity errors; SeizureFrequency failures are mostly state and
unit-boundary errors. Clearer prompt guidelines improved dev140 overall only to
`0.729` and did not solve SeizureFrequency. Reports:
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_error_analysis_2026-06-24.md`
and
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_decision_table_prompt_probe_2026-06-24.md`.

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
4. Keep all dev140/full-200/holdout-facing escalation behind a frozen protocol
   and explicit authorization.

## Work Board

### Now

- Keep `single_call_dedup_facts` v0.5 and
  `single_call_dedup_facts_per_family` compact as plateau comparators.
- Keep Phase 6 DeepSeek/Qwen rollout parked unless there is a clearly stated
  transfer question and projection-aware reporting plan.

### Next

- If a paper-facing ExECTv2 audit is proposed, predeclare the split/surface,
  scorer, stop rule, and row-inspection boundary before running it.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

- 2026-06-24: Completed Satellite 13 Phase 5 with the deterministic projection
  taxonomy and Prescription projection pilot. Allowed projection mainly restored
  benchmark/CUI convention visibility (`0.000` -> `0.180`) while clinical
  headline barely moved (`0.812` -> `0.814`); hybrid rescue and verifier
  candidates stayed separated and unapplied.
- 2026-06-24: Completed Satellite 13 Phase 4 as an LLM-only fallback plateau,
  added error analysis, and tested decision-table prompt guidelines. Best
  compact per-family dev25 score was `0.796`; best prompt-guideline dev140 score
  was `0.729`; no model rollout was promoted.
- 2026-06-24: Resolved the deterministic-rule attribution boundary in
  `CONTEXT.md` and updated the Satellite 13 plan. The projection-aware
  Prescription pilot is now the completed Phase 5 handoff artifact.
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
