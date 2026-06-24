# Project Status

Last updated: 2026-06-24

## Active Objective

Satellite 13 remains the primary ExECTv2 research focus, but the direct
de-duplicated clinical-fact LLM-only path has now plateaued. Phase 0 through
Phase 4 are complete. No DeepSeek/Qwen rollout is promoted because no
GPT-4.1-mini fallback configuration cleared the dev25 gate. The post-plateau
direction is a deterministic projection taxonomy and Prescription-first pilot
with separate LLM-only, hybrid-rescue, and verifier-filtered score lines.

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

The follow-up decision is captured in `CONTEXT.md` and the Satellite 13 plan:
deterministic rules may support meaning-preserving benchmark projection over
model-selected facts, but missing-fact rescue, unsupported-overcall rejection,
specificity promotion, clinical-type conversion, and state inference must be
reported as hybrid or verifier-filtered behavior, not as LLM-only.

## Active Priorities

1. Build the Satellite 13 Phase 5 deterministic projection taxonomy and
   Prescription-first pilot with explicit attribution tags and score-line
   separation.
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

- Draft the Phase 5 deterministic projection rule taxonomy and Prescription
  pilot acceptance tests.
- Keep `single_call_dedup_facts` v0.5 and
  `single_call_dedup_facts_per_family` compact as plateau comparators.

### Next

- Implement the Prescription projection pilot with rule-level attribution tags
  and separate LLM-only, hybrid-rescue, and verifier-filtered score lines.
- Keep DeepSeek/Qwen rollout parked unless there is a clearly stated transfer
  question and projection-aware reporting plan.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

- 2026-06-24: Completed Satellite 13 Phase 4 as an LLM-only fallback plateau,
  added error analysis, and tested decision-table prompt guidelines. Best
  compact per-family dev25 score was `0.796`; best prompt-guideline dev140 score
  was `0.729`; no model rollout was promoted.
- 2026-06-24: Resolved the deterministic-rule attribution boundary in
  `CONTEXT.md` and updated the Satellite 13 plan. The next direction is a
  projection-aware Prescription pilot, not another prompt loop.
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
