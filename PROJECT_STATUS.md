# Project Status

Last updated: 2026-06-25

## Active Objective

ExECTv2 is in a reliability and component-evidence phase after the Satellite 13 LLM-only plateau. Phase 0 through Phase 6 are complete, including the DeepSeek/Qwen `decision_table_sf_inv` transfer readout. The next research push is to turn the ExECTv2 reliability scorecard from dev-only trust evidence into validated calibration, review-routing, robustness, and consistency evidence.

## Current Read

Decision 0027 established clinical recovery as the ExECTv2 headline and projection as an artifact layer. ADR 0033 applies that framing to LLM-only development: the target is de-duplicated clinical-fact recovery, not strict full-schema annotation reproduction.

The controls are fixed. Bare rich-schema LLM-only remains far below the v08 hybrid dev140 clinical-recovery control (`0.9155`). Phase 6 localized the direct LLM-only gap: DeepSeek reached `0.745`, Qwen reached `0.694`, and strict benchmark F1 stayed near `0.13`. The remaining gap is prediction-bearing Diagnosis ontology/granularity and SeizureFrequency state/unit selection, not infrastructure. Active scoreboard: `docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`.

The 2026-06-24 reliability refresh added no-call dev140 evidence from saved artifacts only. Mean scorecard coverage is now `4.1/5` with no weak dimensions. It keeps same-surface rich-schema DeepSeek/Qwen rows separate from newer active LLM-only Phase 6 transfer rows. Current computed evidence: cross-model agreement `0.8852` mean pairwise Jaccard, calibration proxy `0.1456` ECE, high-recall review routing `0.9408` burden / `0.8897` catch, and a lower-burden dev candidate `0.7567` burden / `0.8028` catch.

The scorecard is improved but not finished. The biggest reliability gains now require frozen validation rather than another aggregate prompt run: calibrated risk modeling, lower-burden review routing, perturbation/hard-slice robustness, same-prompt consistency, and true component-off reliability ablations. The frozen audit protocol is now predeclared at `docs/experiments/exectv2/reliability/exectv2_reliability_audit_protocol_predeclaration_2026-06-24.md`; it allows aggregate validation only and keeps full-200/holdout row-level inspection blocked. The current-code v08-shape full-200 artifact was accepted as a one-shot aggregate review-routing validation surface, but the lower-burden dev candidate failed promotion because validation burden rose to `0.9661` while catch was `0.9037`; the null result is recorded at `docs/experiments/exectv2/reliability/exectv2_review_routing_validation_audit_2026-06-24.md`.

The authorized full-200 GPT-4.1-mini run now exists for the strongest v08-shaped architecture using the current code path. Aggregate headline clinical-recovery F1 is `0.8502` overall: Diagnosis `0.8321`, SeizureFrequency `0.7850`, Prescription `0.8926`, Investigations `0.9213`. A no-verifier ablation scored `0.8431` overall: Diagnosis `0.8410`, SeizureFrequency `0.7850`, Prescription `0.8926`, Investigations `0.8563`. The simplification frontier found the first cost-performance cliff: the 3-call structured + Diagnosis decomposer + SF adjudicator candidate passes (`0.8426` overall), while removing the Diagnosis decomposer drops Diagnosis to `0.7643` and removing the SF adjudicator drops SF to `0.7525`; the frontier is recorded at `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`.

The 2026-06-25 aggregate-only Investigations rule ablation shows deterministic replacement is not ready: structured direct + result lens scores `0.8563`, adding pending-test suppression reaches `0.8665`, verifier-only scores `0.8770`, and verifier + deterministic suppression remains strongest at `0.9213`. A first selective-adjudicator diagnostic routes `73.5%` of letters and scores `0.8812`, so the next useful work is a sharper predeclared selective-routing policy, not deterministic-only promotion. Artifact: `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`.

## Active Priorities

1. Treat `clinical_headline` de-duplicated clinical recovery as the primary LLM-only optimization target; report strict benchmark results only as a diagnostic/comparability surface.
2. Preserve attribution discipline: the model emits every scored fact; deterministic code may validate evidence and perform tagged meaning-preserving projection, but must not add, select, or reject clinical facts inside the LLM-only score line.
3. Keep Reliability Scorecard separate from Component Impact: reliability is trust evidence; component impact must be ablation/delta evidence.
4. Treat reliability-score improvements as research work: every score increase should name the split, scorer, inspection boundary, and whether evidence is dev-only, validation, full-200, or holdout.

## Work Board

### Now

- Treat `exectv2_holistic_finding_assembly_full200_gpt41mini_3call_dxdecomposer_sfadjudicator` as the current lean GPT-4.1-mini cost-performance diagnostic from the simplification frontier; do not use it as the validation/review-routing surface without a fresh predeclaration that freezes that exact candidate.
- Redesign the Investigations selective-adjudicator router on dev-only features to reduce the `0.7350` call burden while preserving more of the verifier + deterministic suppression control (`0.9213` F1); start from `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`.
- Use the refreshed ExECTv2 reliability scorecard and frozen audit protocol as the control surface for calibration, robustness, and consistency work; keep the failed lower-burden review-routing candidate unpromoted unless a fresh dev140 risk-feature redesign is predeclared.

### Next

- Replace the heuristic calibration proxy with a frozen, leakage-audited risk model or cross-validated scoring rule; report ECE, Brier score, reliability bins, and per-family calibration before claiming calibration coverage above `3/5`.
- Build robustness panels that can move the scorecard: current-vs-historical SF state perturbations, medication current-vs-plan ambiguity, investigation result-state ambiguity, diagnosis assertion/hierarchy conventions, and evidence paraphrase/deletion stress tests.
- Add same-prompt/cross-seed consistency panels for live LLM surfaces, with schema validity, evidence validity, call failures, and family-cell agreement separated from deterministic replay stability.
- Keep Phase 3-6 direct LLM-only runs as plateau comparators with fixed clinical-recovery claim language when updating scoreboards or paper-facing summaries.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection remains blocked; the reliability-audit protocol only authorizes aggregate validation outputs.
- Promotion of the lower-burden review-routing candidate is blocked by failed aggregate validation; any retry needs dev140-only risk-feature redesign plus a fresh predeclaration.

### Done Recently

- 2026-06-25: Completed the aggregate-only Investigations rule/adjudicator ablation at `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`; deterministic pending-test suppression improves structured direct from `0.8563` to `0.8665`, but verifier + deterministic suppression remains strongest at `0.9213`, and the first selective diagnostic routes `73.5%` of letters for `0.8812` F1.
- 2026-06-24: Completed the aggregate-only ExECTv2 review-routing validation on the accepted current-code v08-shape full-200 artifact at `docs/experiments/exectv2/reliability/exectv2_review_routing_validation_audit_2026-06-24.md`; the lower-burden dev candidate is not promoted because validation burden rose to `0.9661` despite `0.9037` catch.
- 2026-06-24: Completed the GPT-4.1-mini ExECTv2 simplification frontier at `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`; the recommended lean current-code full-200 candidate is the 3-call structured + Diagnosis decomposer + SF adjudicator architecture (`0.8426` overall), with both 2-call removals failing predeclared family guardrails.
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
