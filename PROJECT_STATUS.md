# Project Status

Last updated: 2026-06-24

## Active Objective

Satellite 13 remains the primary ExECTv2 research focus, but the direct
de-duplicated clinical-fact LLM-only path has now plateaued. Phase 0 through
Phase 4 are complete. No Phase 5 DeepSeek/Qwen rollout is promoted because no
GPT-4.1-mini fallback configuration cleared the dev25 gate.

## Current Read

Decision 0027 established clinical recovery as the ExECTv2 headline and
projection as an artifact layer. ADR 0033 now applies that framing to LLM-only
development: the active target is de-duplicated clinical-fact recovery, not
strict full-schema annotation reproduction.

The controls are fixed for the next phase. Bare rich-schema LLM-only
`single_call_clean_render_ids` scored `0.334`/`0.339` strict F1 for
GPT-4.1-mini/Qwen on dev140, but `0.713`/`0.725` on de-duplicated
`clinical_headline`. The v08 hybrid remains the dev140 clinical-recovery
performance control at overall `0.9155`, Diagnosis `0.9090`,
SeizureFrequency `0.9053`, Prescription `0.9357`, Investigations `0.9132`.
Phase 1 archived the superseded rich-schema iteration sprawl under
`experiments/_archive/exectv2_richschema_iterations/` and replaced the old
cross-model closeout table with a narrow active scoreboard:
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`.

Phase 2 added the `single_call_dedup_facts` route, simplified fact parser,
representation-only adapter, runner wiring, and focused tests. The canonical
headline summary now uses Diagnosis `concept_negation`. No-call replays through
the new adapter exactly reproduce the fixed canonical clean-render baselines:
GPT-4.1-mini `0.7114` and Qwen `0.7215` overall `clinical_headline`.

Phase 3 tested five GPT-4.1-mini single-prompt variants. The best gate-clean
candidate, `single_call_dedup_facts` v0.5, had zero call/parse failures and
evidence validity `0.9613` on dev140, but plateaued at `0.710` canonical
`clinical_headline` overall: Diagnosis `0.672`, SeizureFrequency `0.558`,
Prescription `0.814`, Investigations `0.832`. Readout:
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase3_single_prompt_plateau_2026-06-23.md`.

Phase 4 added `single_call_dedup_facts_per_family` and ran two GPT-4.1-mini
dev25 gates. Compact per-family reached `0.796` canonical `clinical_headline`
with Diagnosis `0.698` and SeizureFrequency `0.690`; full-example per-family
reached `0.782`, with SeizureFrequency falling to `0.593`. Both had zero
call/parse/schema failures and evidence validity near Phase 3, but neither
beat the Phase 3 dev25 gate (`0.800`) or approached `>0.900`, so no dev140
confirmation or model rollout was promoted. Readout:
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_fallback_plateau_2026-06-24.md`.

The Qwen generation-and-selection work remains useful negative evidence for the
strict full-schema target. The strongest clean-render dev5 branch reached only
about `0.517` strict F1, and bounded oracle audits showed format projection over
already emitted facts cannot plausibly recover `>0.900` on that surface. That is
why the active LLM-only workstream now targets the simpler de-duplicated
clinical facts directly.

## Active Priorities

1. Decide whether Satellite 13 should close as a documented LLM-only plateau or
   pivot to a new, explicitly hybrid/selector-owned recovery architecture.
2. Treat `clinical_headline` de-duplicated clinical recovery as the primary
   LLM-only optimization target; report strict benchmark results only as a
   required diagnostic/comparability surface.
3. Preserve attribution discipline: the model must emit every scored fact;
   deterministic code may validate evidence/map representation/score, but must
   not add or select clinical facts.
4. Keep all dev140/full-200/holdout-facing escalation behind a frozen protocol
   and explicit authorization.

## Work Board

### Now

- Choose the post-Phase-4 direction: close the Satellite 13 LLM-only direct
  prompting track as a plateau, or predeclare a separate hybrid/selector
  experiment with attribution language that is not LLM-only.
- Keep `single_call_dedup_facts` v0.5 and
  `single_call_dedup_facts_per_family` compact as plateau comparators.

### Next

- If a new architecture is authorized, predeclare the ownership boundary,
  scorer surface, dev gate, stop rule, and whether it is still an LLM-only claim.
- Keep DeepSeek/Qwen rollout parked unless there is a winning GPT-4.1-mini
  configuration to transfer unchanged.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

- 2026-06-24: Completed Satellite 13 Phase 4 as a fallback plateau. Added the
  `single_call_dedup_facts_per_family` route and tests, then ran compact and
  full-example GPT-4.1-mini dev25 gates. Best canonical `clinical_headline` was
  `0.796`, below the Phase 3 dev25 gate (`0.800`) and far below `>0.900`; the
  remaining gap is still Diagnosis/SF, so no Phase 5 rollout was promoted.
- 2026-06-23: Completed Satellite 13 Phase 3 as a localized single-prompt
  plateau. GPT-4.1-mini `single_call_dedup_facts` v0.5 reached dev140
  `clinical_headline` `0.710` with evidence validity `0.9613`, 0 call failures,
  and 0 parse/schema failures; the remaining gap is Diagnosis/SF, so Phase 4
  per-family prompts are next.
- 2026-06-23: Completed Satellite 13 Phase 2 by adding
  `single_call_dedup_facts`, the simplified clinical-fact adapter, runner
  wiring, prompt-only smoke coverage, exact clean-render no-call replay reports,
  and canonical `clinical_headline` overall reporting with Diagnosis =
  `concept_negation`.
- 2026-06-23: Completed Satellite 13 Phase 1 cleanup by archiving 694
  superseded rich-schema iteration artifacts under
  `experiments/_archive/exectv2_richschema_iterations/`, adding the archive
  manifest, and replacing the live scoreboard with
  `docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`.
- 2026-06-23: Completed Satellite 13 Phase 0 with ADR 0033, fixing the primary
  de-duplicated LLM-only target and handing off to Phase 1 cleanup.
- 2026-06-23: Added the Satellite 13 plan
  `docs/plans/exectv2/13_dedup_clinical_facts_llm_only.md`, reframing the
  post-Qwen strict-schema results around direct `clinical_headline` recovery.
- 2026-06-23: Ran and documented Qwen repair-attribution/generation-selection
  diagnostics. The direct clean paths remained below promotion quality, and
  candidate-backed/default-keep success is classified as hybrid selector
  evidence rather than an LLM-attributed extraction pass.
- 2026-06-22: Added
  `docs/design/llm_repair_attribution_protocol_2026-06-22.md`, separating
  model-preserving canonical repair from prediction-bearing rescue repair and
  tightening the model-origin generation requirement.
- 2026-06-21 to 2026-06-22: Completed ExECTv2 v08 all-four clearance,
  reliability scorecard, clinical-utility companion, Phase 1 final
  consolidation refresh, and frontend static-review data refresh.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict
  benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development
  without explicit authorization and a frozen protocol.
- Keep deterministic certainty/CUI/format repairs and semantic add/drop/replace
  actions provenance-stamped and attribution-clean.
