# Project Status

Last updated: 2026-06-23

## Active Objective

Satellite 13 is now the primary ExECTv2 research focus: build an
attribution-clean LLM-only route that emits de-duplicated clinical facts directly
for the `clinical_headline` scorer. Phase 0, Phase 1 cleanup, Phase 2
route/adapter construction, and Phase 3 single-prompt GPT-4.1-mini iteration are
complete; Phase 4 per-family fallback prompts are next.

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
Prescription `0.814`, Investigations `0.832`. This does not clear the `>0.900`
target and is essentially the clean-render replay baseline, so Phase 4 should
move to lean per-family LLM-only prompts rather than more single-prompt tuning.
Readout:
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase3_single_prompt_plateau_2026-06-23.md`.

The Qwen generation-and-selection work remains useful negative evidence for the
strict full-schema target. The strongest clean-render dev5 branch reached only
about `0.517` strict F1, and bounded oracle audits showed format projection over
already emitted facts cannot plausibly recover `>0.900` on that surface. That is
why the active LLM-only workstream now targets the simpler de-duplicated
clinical facts directly.

## Active Priorities

1. Start Phase 4 fallback rung 1: lean per-family LLM-only prompts for
   Diagnosis and SeizureFrequency, preserving the same attribution-clean adapter
   boundary.
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

- Start Phase 4 fallback rung 1 with lean per-family LLM-only prompts, beginning
  with Diagnosis and SeizureFrequency.
- Keep `single_call_dedup_facts` v0.5 as the single-prompt plateau comparator
  (`0.710` dev140 `clinical_headline`, evidence validity `0.9613`).

### Next

- If a per-family fallback clears the dev25 gate, confirm on dev140 against the
  v0.5 single-prompt plateau, clean-render replay baseline, and v08 hybrid
  control.
- Roll a winning Phase 4 configuration to DeepSeek and Qwen only after
  GPT-4.1-mini clears the dev140 de-duplicated target or the fallback plateau is
  documented.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

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
