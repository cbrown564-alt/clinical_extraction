# Project Status

Last updated: 2026-06-25

## Active Objective

ExECTv2 is in a reliability and component-evidence phase after the Satellite 13 LLM-only plateau. Phase 0 through Phase 6 are complete, including the DeepSeek/Qwen `decision_table_sf_inv` transfer readout. The research push is to turn the ExECTv2 reliability scorecard from dev-only trust evidence into frozen aggregate validation across calibration, review-routing, robustness, and consistency. Three of those four dimensions are now resolved: calibration is promoted to `4/5` coverage on the full-200 surface, review-routing has been through frozen aggregate validation (the lower-burden candidate was tested and not promoted, leaving the high-recall operating point as standing evidence), and same-prompt consistency now has saved live-repeat evidence for the selected GPT-4.1-mini 2-call no-SF-adjudicator candidate. The remaining open dimension is perturbation/hard-slice robustness, which is still preflight only.

## Current Read

Decision 0027 established clinical recovery as the ExECTv2 headline and projection as an artifact layer. ADR 0033 applies that framing to LLM-only development: the target is de-duplicated clinical-fact recovery, not strict full-schema annotation reproduction.

The controls are fixed. Bare rich-schema LLM-only remains far below the v08 hybrid dev140 clinical-recovery control (`0.9155`). Phase 6 localized the direct LLM-only gap: DeepSeek reached `0.745`, Qwen reached `0.694`, and strict benchmark F1 stayed near `0.13`. The remaining gap is prediction-bearing Diagnosis ontology/granularity and SeizureFrequency state/unit selection, not infrastructure. Active scoreboard: `docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`.

The 2026-06-25 reliability refresh keeps same-surface rich-schema DeepSeek/Qwen rows separate from newer active LLM-only Phase 6 transfer rows. Current computed evidence includes cross-model agreement `0.8852` mean pairwise Jaccard, a dev140 grouped cross-validated calibration rule (`0.0277` ECE, `0.1774` Brier vs `0.1874` base-rate Brier), high-recall review routing `0.9408` burden / `0.8897` catch, and a lower-burden dev candidate `0.7567` burden / `0.8028` catch. The frozen aggregate-only full-200 calibration audit promotes the scoring rule as validation evidence (`0.0432` ECE, `0.2245` Brier vs `0.2387` base-rate Brier, five monotone bins, all families reported), raising calibration coverage to `4/5` without making holdout or deployment-probability claims.

The scorecard is improved but not finished. The biggest reliability gains now require frozen validation rather than another aggregate prompt run: calibrated risk modeling, lower-burden review routing, perturbation/hard-slice robustness, and true component-off reliability ablations. The frozen audit protocol is now predeclared at `docs/experiments/exectv2/reliability/exectv2_reliability_audit_protocol_predeclaration_2026-06-24.md`; it allows aggregate validation only and keeps full-200/holdout row-level inspection blocked. The current-code v08-shape full-200 artifact was accepted as a one-shot aggregate review-routing validation surface, but the lower-burden dev candidate failed promotion because validation burden rose to `0.9661` while catch was `0.9037`; the null result is recorded at `docs/experiments/exectv2/reliability/exectv2_review_routing_validation_audit_2026-06-24.md`.

The authorized full-200 GPT-4.1-mini run now exists for the strongest v08-shaped architecture using the current code path. Aggregate headline clinical-recovery F1 is `0.8502` overall: Diagnosis `0.8321`, SeizureFrequency `0.7850`, Prescription `0.8926`, Investigations `0.9213`. A no-verifier ablation scored `0.8431` overall: Diagnosis `0.8410`, SeizureFrequency `0.7850`, Prescription `0.8926`, Investigations `0.8563`. The simplification frontier found the best current cost-performance candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` uses `400` full-200 calls and scores `0.8356` overall, with Diagnosis `0.8397`, SeizureFrequency `0.7525`, Prescription `0.8926`, and Investigations `0.8563`. The governing lean-candidate thresholds are now overall `>=0.8350` and SeizureFrequency `>=0.7500`, so `0.7525` SF passes for this cost profile; the no-Diagnosis-decomposer candidate remains rejected because Diagnosis drops to `0.7643`. Frontier artifact: `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`.

The 2026-06-25 aggregate-only Investigations rule ablation shows deterministic replacement is not ready: structured direct + result lens scores `0.8563`, adding pending-test suppression reaches `0.8665`, verifier-only scores `0.8770`, and verifier + deterministic suppression remains strongest at `0.9213`. Selective review burden must be `<=0.20` to be operationally acceptable. V02 lowers full-200 burden from `0.7350` to `0.5100` at unchanged `0.8812` F1, still far above the ceiling. V04 is the first capped scaffold to satisfy the burden gate (`0.2000` on dev140/full-200) but drops F1 (`0.7987` dev140, `0.8655` full-200), so no live selective-adjudicator experiment should run yet. Artifact: `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`.

Gan 2026 completed an explicitly authorized frozen aggregate holdout audit for the v0.7 DeepSeek Reasoner structured-events prompt. The candidate was frozen before test450: `hybrid_structured_events`, prompt `gan2026_hybrid_structured_events_v0.7`, model `deepseek/deepseek-reasoner`, temperature `0.0`, max tokens `32000`, no raw output reuse, split manifest `gan2026_split_v1`, and unchanged `hybrid_full_stack` repair/scoring policy. Validation improved to `642/750` Purist and `668/750` Pragmatic, but the locked test aggregate was `346/450` Purist and `365/450` Pragmatic with `0` call failures. This is a final holdout aggregate result, not a new tuning surface; no row-level test inspection or follow-on prompt/scorer changes are authorized from it.

## Active Priorities

1. Treat `clinical_headline` de-duplicated clinical recovery as the primary LLM-only optimization target; report strict benchmark results only as a diagnostic/comparability surface.
2. Preserve attribution discipline: the model emits every scored fact; deterministic code may validate evidence and perform tagged meaning-preserving projection, but must not add, select, or reject clinical facts inside the LLM-only score line.
3. Keep Reliability Scorecard separate from Component Impact: reliability is trust evidence; component impact must be ablation/delta evidence.
4. Treat reliability-score improvements as research work: every score increase should name the split, scorer, inspection boundary, and whether evidence is dev-only, validation, full-200, or holdout.

## Work Board

### Now

- Treat `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` as the accepted lean GPT-4.1-mini cost-performance surface. The active simplification thresholds are overall `>=0.8350` and SeizureFrequency `>=0.7500`; do not resurrect the older `0.8400`/`0.7700` rejection language.
- Use the refreshed ExECTv2 reliability scorecard and frozen audit protocol as the control surface for validation work; keep calibration, robustness, consistency, and review-routing claims split by dev-only, full-200 aggregate, and holdout authorization.

### Next

- Convert the deterministic robustness preflight into a frozen aggregate-only candidate run; current fixture evidence covers SF state, prescription plan/current, investigation result-state, diagnosis assertion/hierarchy, and evidence perturbations but is not validation evidence.
- Keep Phase 3-6 direct LLM-only runs as plateau comparators with fixed clinical-recovery claim language when updating scoreboards or paper-facing summaries.
- Keep Investigations cost work secondary to robustness validation; if revisited, improve the v04 `<=0.20` capped direct-risk scaffold before any live selective-adjudicator experiment because it passes the burden gate but loses too much F1 to promote.

### Blocked

- Additional Gan holdout-facing reruns, row-level test analysis, and post-test tuning remain blocked after the authorized v0.7 aggregate audit unless separately authorized under a fresh frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection remains blocked; the reliability-audit protocol only authorizes aggregate validation outputs.
- Promotion of the lower-burden review-routing candidate is blocked by failed aggregate validation; any retry needs dev140-only risk-feature redesign plus a fresh predeclaration.

### Done Recently

- 2026-06-25: Corrected the GPT-4.1-mini simplification frontier source of truth: the accepted lean 2-call no-SF-adjudicator package now passes the generated frontier under overall `>=0.8350` and SeizureFrequency `>=0.7500`; stale `do-not-promote`/`0.7700` language was removed from the frontier, deterministic-rule-role note, plan, generator, and self-consistency assembly report stamps.
- 2026-06-25: Completed the authorized aggregate-only Gan v0.7 DeepSeek Reasoner structured-events test450 audit: `346/450` Purist, `365/450` Pragmatic, `446/450` structured records, `0` call failures, `4` parse/schema/label issues, and `442/450` exact evidence. Validation lift did not meaningfully generalize beyond the prior Reasoner holdout aggregate; row-level test inspection and follow-on tuning remain out of bounds.
- 2026-06-25: Completed Gan-comparable ExECTv2 self-consistency for the selected `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` candidate: hard50 temp-0 live repeats (`0.9217` exact family-cell agreement, `0.1261` mean entropy, `0` call/parse failures) and dev140 varying-temperature entropy (`0.8857` exact agreement, `0.1905` mean entropy, `0` call/parse failures), both aggregate-only with raw producer variation confirming non-cache replay.
- 2026-06-25: Completed the aggregate-only ExECTv2 calibration validation audit at `docs/experiments/exectv2/reliability/exectv2_calibration_validation_audit_2026-06-25.md`; the frozen dev140 grouped scoring rule is promoted on the accepted current-code v08-shape full-200 artifact with ECE `0.0432`, Brier `0.2245` versus `0.2387` constant base-rate Brier, five monotone bins, and per-family ECE reported without row-level full-200 inspection.
- 2026-06-25: Merged parallel reliability work: grouped dev140 calibration scoring rule (`0.0277` ECE, `0.1774` Brier), deterministic robustness preflight at `docs/experiments/exectv2/reliability/exectv2_robustness_panels_preflight_2026-06-25.md`, and Investigations v04 capped burden scaffold (`0.2000` burden, not promoted).
- 2026-06-25: Completed the aggregate-only Investigations rule/adjudicator ablation and dev-selected selective-router v02 diagnostic at `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`; deterministic pending-test suppression improves structured direct from `0.8563` to `0.8665`, verifier + deterministic suppression remains strongest at `0.9213`, and v02 cuts full-200 aggregate burden from `0.7350` to `0.5100` at unchanged `0.8812` F1, which still fails the `<=0.20` acceptable review-burden ceiling.
- 2026-06-24: Completed the aggregate-only ExECTv2 review-routing validation on the accepted current-code v08-shape full-200 artifact at `docs/experiments/exectv2/reliability/exectv2_review_routing_validation_audit_2026-06-24.md`; the lower-burden dev candidate is not promoted because validation burden rose to `0.9661` despite `0.9037` catch.
- 2026-06-25: Updated the GPT-4.1-mini ExECTv2 simplification-frontier decision: the recommended lean current-code full-200 candidate is now `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` (`0.8356` overall; Diagnosis `0.8397`, SeizureFrequency `0.7525`, Prescription `0.8926`, Investigations `0.8563`) because the SF drop is acceptable for the `400`-call cost profile; artifact remains `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`.
- 2026-06-24: Ran the authorized full-200 current-code v08-shape GPT-4.1-mini architecture audit and materialized the holistic assembly artifact at `docs/experiments/exectv2/reliability/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.md`; aggregate headline F1 is `0.8502` overall with no producer call/parse failures.
- 2026-06-24: Ran the authorized full-200 no-verifier ablation at `docs/experiments/exectv2/reliability/exectv2_holistic_finding_assembly_v08_full200_currentcode_no_verifiers_gpt41mini_20260624.md`; aggregate headline F1 is `0.8431`, with Diagnosis slightly higher and Investigations lower versus the verifier-backed run.
- 2026-06-24: Upgraded the ExECTv2 reliability scorecard with computed no-call dev140 evidence, latest DeepSeek/Qwen surface separation, calibration proxy, review-routing operating points, frontend payload/UI, and replay/API tests.
- 2026-06-24: Predeclared the frozen ExECTv2 reliability-audit protocol for split/surface, scorer, stop rule, row-inspection boundary, promotion gates, and allowed dev140/full-200/holdout artifact use.
- 2026-06-24: Generated ExECTv2 replay-only layered component-impact artifacts for v08, v09, DeepSeek, and Qwen dev140.
- 2026-06-24: Completed final project consolidation Phases 2-4: canonical indexes/reports, ExECTv2 frontend MVP, archive quarantine, shared final-consolidation builder, cross-dataset reliability scorecard tab, and Gan component-ablation simplification.
- 2026-06-24: Completed Satellite 13 Phases 0-6, including ADR 0033, `single_call_dedup_facts`, projection taxonomy, Prescription pilot, fallback plateau, and DeepSeek/Qwen transfer readout.
- 2026-06-22: Added the LLM repair-attribution protocol and completed the v08 all-four ExECTv2 consolidation work.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence, selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development; the current reliability-audit protocol authorizes aggregate validation only.
- Keep deterministic projection, hybrid rescue, and verifier rejection provenance-stamped and separated in reported score lines.
