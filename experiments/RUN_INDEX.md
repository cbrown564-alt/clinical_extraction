# Gan 2026 Run Registry

Generated from `experiments/registry.jsonl`. The JSONL file remains the canonical machine-readable registry.

## Paper-Writing Workstream Artifacts

### `P3c-wall-transfers-manuscript-draft` (2026-06-27)

- **Deliverable**: `docs/research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md`
- **Workstream**: P3c — wall-transfers reframe; writing only, no model calls.
- **Verdict**: draft complete; one section gated `[PENDING PROBE]` pending
  `exectv2_sf_wall_transfer_probe_2026-06-27.md`.
- **Key finding**: ExECTv2 SF gap (GPT 0.7525, DeepSeek 0.7602 full-200 aggregate) is
  structurally parallel to the Gan confident-over-reading wall (P2.1: mean label entropy
  0.012, `band_unknown` entropy 0.000). The framing converts "SF is our weakest family"
  into the paper's strongest generalization claim: **a task-bound, not system-bound, ceiling
  that transfers across datasets and models**. Mechanism confirmation ([PENDING PROBE])
  requires a forward-observable-feature entropy probe on an ExECTv2 SF slice.
- **Recommended placement**: capability-first spine §3 (*What generalizes*), subsection 3.2,
  following the model-swap / model-agnostic subsection.
- **Orchestrator state**: cycle `P3c-wall-transfers-manuscript-draft` recorded in
  `experiments/gan2026_f1_orchestrator_state.json`.

---

## Reliability Scorecard

### `exectv2_robustness_validation_audit_2026-06-25`
- Date/split: `2026-06-25`; `full200_aggregate`; `200` rows.
- Pipeline: `exectv2_robustness_validation_audit`; mode `aggregate-only robustness validation`; replay `analysis_only`.
- Model role: Aggregate robustness hard-slice analysis over the current-code v08-shaped full-200 artifact; no live model calls.; model `openai/gpt-4.1-mini`.
- Registry roles: `reliability_scorecard`.
- Repair mode/config: `frozen robustness taxonomy from preflight panels`.
- Primary metrics: call_failures=0, eligible_family_cells=619, evidence_validity=1.0, hard_slice_delta_vs_overall=-0.0167, hard_slice_f1=0.8336, hard_slice_family_cells=414, non_hard_slice_f1=0.8909, overall_f1=0.8503, parse_schema_failures=0, schema_validity=1.0.
- Evidence validity: Aggregate hard-slice validation only; schema and evidence validity both 1.0000 with no row-level examples or identifiers emitted.
- Claim language: Promotes the frozen robustness taxonomy as aggregate full-200 hard-slice validation evidence. Evidence paraphrase/deletion remain adversarial fixture stress evidence, not naturally observed full-200 failures.
- Artifacts: `docs/experiments/exectv2/reliability/exectv2_robustness_validation_audit_2026-06-25.md`, `docs/experiments/exectv2/reliability/exectv2_robustness_panels_preflight_2026-06-25.md`.

### `gan2026_reliability_scorecard_phase1_2026-06-17`
- Date/split: `2026-06-17`; `test450`; `450` rows.
- Pipeline: `reliability_scorecard_phase1`; mode `no-call replay`; replay `analysis_only`.
- Model role: none; aggregate-only port of P0.2 (risk-coverage) and P0.5 (family parity) to the locked split, scored on the canonical `v0_reference` subject. Two-agent agreement leg only (weaker replay, decision 0018); model `none`.
- Registry roles: `reliability_scorecard`.
- Repair mode/config: `reliability_scorecard_v1`.
- Primary metrics: summary=test_base_error_rate=0.191, agree_only_coverage=0.658, agree_only_selective_risk=0.122, disagree_set_error=0.325, two_agent_failure_auroc=0.648, parity_overall_acc=0.812, band_error_spread=0.199, band_acc_cv=0.082, worst_band=band_submonthly@0.695.
- Evidence validity: Zero model calls; aggregate-only readout (0 forbidden markers: source_row_index/transition_vs_v0/score_layers absent). Both transforms predeclared and hash-frozen before touching test450 (two_agent_external_risk sha256, classify_boundary_families validation classifier sha256). Per-row correctness read internally for aggregation only; no row-level holdout inspection.
- Claim language: Phase 1 freeze-warden-gated holdout port. The two-agent agreement leg still separates holdout error (abstaining the disagreement set cuts error 0.191→0.122; AUROC 0.648 < validation 0.781 by construction). Per-family parity confirms the validation picture: disparity in rate bands + over-reading families, not band_unknown. Not a new benchmark claim.
- Artifacts: `experiments/gan2026_reliability_p1_1_test450_risk_coverage_2026-06-17.json`, `experiments/gan2026_reliability_p1_1_test450_risk_coverage_2026-06-17.md`, `experiments/gan2026_reliability_p1_2_test450_error_parity_2026-06-17.json`, `experiments/gan2026_reliability_p1_2_test450_error_parity_2026-06-17.md`.

### `gan2026_reliability_scorecard_phase0_2026-06-17`
- Date/split: `2026-06-17`; `validation750+test450`; `1200` rows.
- Pipeline: `reliability_scorecard_phase0`; mode `no-call replay`; replay `analysis_only`.
- Model role: none; deterministic re-analysis of frozen artifacts on the canonical `v0_reference` single-SE-mini subject layer (decision 0018). Shared code: `artifact_analysis/reliability_common.py`; model `none`.
- Registry roles: `reliability_scorecard`.
- Repair mode/config: `reliability_scorecard_v1`.
- Primary metrics: summary=subject_purist_val=0.881, subject_purist_test=0.809, faithfulness_val=0.921, faithfulness_test=0.929, faithful_but_wrong_val=80, faithful_but_wrong_test=80, risk_coverage_auc=0.0404, external_score_failure_auroc=0.781, external_confidence_ece=0.080, external_confidence_brier=0.102, robustness_index_v0_5=0.547, robustness_index_v0_6=0.694, robustness_index_v0_7=1.000, band_error_spread=0.078, band_acc_cv=0.032, model_render_failures=0, recoverable_repairs=5483, est_cost_per_1000_notes_usd=1.16, hard50_temp0_unanimous_acc=0.689.
- Evidence validity: Zero model calls. Every metric re-derived from frozen JSONL/JSON; subject numbers read from `v0_reference`, comparator numbers tagged. test450 touched only via aggregate-safe joins on the saved reasoner artifact. parse_errors are recoverable repairs (not failures); self-consistency leg is temp-0 reproducibility only (varying-temperature P2.1 pending).
- Claim language: Phase 0 (zero-budget) reliability scorecard re-expressing the strand's logged evidence into ten reliability dimensions. Mean coverage ≈3.5/5; Calibration 2→3, Abstention 4→5, Operational 3→4, Consistency 3→2 (temp-0 caveat). Not a new benchmark claim; a re-expression of existing results onto the canonical subject layer.
- Artifacts: `experiments/gan2026_reliability_master_scorecard_2026-06-17.json`, `experiments/gan2026_reliability_master_scorecard_2026-06-17.md`, `experiments/gan2026_reliability_p0_1_faithfulness_correctness_2026-06-17.json`, `experiments/gan2026_reliability_p0_1_faithfulness_correctness_2026-06-17.md`, `experiments/gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.json`, `experiments/gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.md`, `experiments/gan2026_reliability_p0_3_external_calibration_validation750_2026-06-17.json`, `experiments/gan2026_reliability_p0_3_external_calibration_validation750_2026-06-17.md`, `experiments/gan2026_reliability_p0_4_robustness_index_2026-06-17.json`, `experiments/gan2026_reliability_p0_4_robustness_index_2026-06-17.md`, `experiments/gan2026_reliability_p0_5_error_parity_validation750_2026-06-17.json`, `experiments/gan2026_reliability_p0_5_error_parity_validation750_2026-06-17.md`, `experiments/gan2026_reliability_p0_6_safety_table_2026-06-17.json`, `experiments/gan2026_reliability_p0_6_safety_table_2026-06-17.md`, `experiments/gan2026_reliability_p0_7_operational_2026-06-17.json`, `experiments/gan2026_reliability_p0_7_operational_2026-06-17.md`, `experiments/gan2026_reliability_p0_8_self_consistency_hard50_2026-06-17.json`, `experiments/gan2026_reliability_p0_8_self_consistency_hard50_2026-06-17.md`.

### `gan2026_reliability_p2_1_semantic_entropy_2026-06-17`
- Date/split: `2026-06-17`; `validation`; `150` rows.
- Pipeline: `reliability_p2_1_semantic_entropy`; mode `live`; replay `live`.
- Model role: structured-event extractor multi-sampled at VARYING temperatures (0.3/0.5/0.7/1.0) to measure two-level semantic entropy (Purist label + selected kind); model `openai/gpt-4.1-mini`.
- Repair mode/config: `structured_events default repair; varying-temperature sampling`.
- Primary metrics: summary=temps=[0.3,0.5,0.7,1.0], k=4, n_rows=150, residual_rows=23, mean_label_entropy=0.012, mean_kind_entropy=0.003, rows_nonzero_label_entropy=4, residual_label_entropy=0.018, nonresidual_label_entropy=0.011, band_unknown_label_entropy=0.000, verdict=H0_confident_over_reading, decision_stable_under_temperature=True, raw_prose_varies=True.
- Evidence validity: Live gpt-4.1-mini, validation split only (no test exposure). 25-row degeneracy preflight gate run first; 150-row residual-enriched tier confirms the result on 23 residual rows. Verified non-artifact: raw_output differs across temperatures while the rendered label/kind does not (genuine decision-stability, not caching). Full validation750 x4 (~3,000 calls) deliberately not spent once the gate fired.
- Claim language: THE research swing, falsification test of The Wall. H0 confirmed: varying-temperature semantic entropy is ~0 everywhere, the residual (incl. band_unknown=0.000) is no more uncertain than the rest -> the unknown-vs-rate over-reading is CONFIDENT, not uncertain. Converts the closeout's negative result into a mechanism; no abstention/calibration signal derivable from the model's own samples. Restores Consistency to 4/5.
- Artifacts: `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.json`, `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md`, `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight25_2026-06-17.json`, `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight25_2026-06-17.md`, `experiments/gan2026_reliability_p2_1_samples_preflight{25,150}_temp{0.3,0.5,0.7,1.0}_2026-06-17.jsonl`.

### `gan2026_reliability_d_gating_value_validation750_2026-06-17`
- Date/split: `2026-06-17`; `validation`; `748` rows.
- Pipeline: `reliability_d_gating_value`; mode `replay`; replay `saved_output_replay`.
- Model role: none. Simulates using the variant-D `calibrated_confidence` as an abstention gate on the PRIMARY single gpt-4.1-mini SE architecture; scored vs `v0_reference.comparison.purist_correct`; model `none`.
- Primary metrics: summary=base accuracy 0.884 (error 0.116), D AUROC 0.684. Gate selective accuracy / abstention precision: cov 95% → 0.890 / 0.243; cov 90% → 0.905 / 0.307 (peak, 2.6× the 0.116 random bar); cov 80% → 0.921 / 0.267; cov 50% → 0.952 / 0.184. Errors shed at 90% cov ≈ 26% of total. External composite gate shown as context-only ceiling (needs 3 models, unavailable single-model).
- Evidence validity: Validation-only; test450 untouched. The random-abstention bar (= base error rate, selective accuracy unchanged in expectation) is the comparison; D clears it (abstention precision 2–2.6× random across operating points).
- Claim language: On the single-model architecture, variant-D confidence is a REAL but MODEST gate — genuinely beats random abstention (precision 2–2.6×), monotone selective-accuracy curve, but small absolute accuracy lift (88.4%→90.5% costs 10% coverage) because confident over-reading errors are invisible to any self-signal. Practical value depends on tolerance for discarded coverage + one extra mini call/row. test450 usefulness UNKNOWN pending a freeze-warden-gated, aggregate-only holdout port. Does not change champion/robustness status.
- Artifacts: `experiments/gan2026_reliability_d_gating_value_validation750_2026-06-17.json`, `experiments/gan2026_reliability_d_gating_value_validation750_2026-06-17.md`.

### `gan2026_reliability_d_gating_test450_2026-06-17`
- Date/split: `2026-06-17`; `test`; `450` rows.
- Pipeline: `reliability_d_gating_test450`; mode `live`; replay `live`.
- Model role: decoupled variant-D confidence reviewer (`variant_D_decoupled_v1`) over the canonical single-SE-mini `v0_reference` test450 answers (decision 0018); GATES NOTHING in production — simulates an abstention gate; model `openai/gpt-4.1-mini`.
- Registry roles: `reliability_scorecard`.
- Primary metrics: summary=base accuracy 364/450 = **0.8089** (Wilson CI 0.770–0.843), base error 0.1911; D failure-AUROC **0.649** (CI 0.581–0.717, > chance). Gating (selective acc · abstention precision vs 0.191 random bar): 95% cov → 0.820 · 0.409; 90% cov → 0.825 · 0.333 (1.74× random, +14.2pp); 80% cov → 0.856 · 0.378; 70% cov → 0.867 · 0.326; 50% cov → 0.880 · 0.262. Selective-accuracy lift positive + monotone.
- Evidence validity: Frozen aggregate-only holdout readout; no row-level test inspection; no test tuning; single run. Test-split-integrity preflight passed (450/450 unique, coverage == manifest, v0_reference on all 450); V12 source-symmetry preflight structurally inapplicable to a single-model run (substituted direct integrity check, per house precedent). Subject source-symmetry inherited from the certified v0.4 artifact.
- Claim language: MEETS the predeclared success criterion — variant-D confidence is a usable abstention/triage gate on the primary single gpt-4.1-mini architecture on the locked holdout (AUROC CI above chance; 90%-cov abstention precision 1.74× random; monotone selective-accuracy lift). But the benefit is MODEST and ATTENUATES from validation (AUROC 0.684→0.649; 90%-cov selective acc 0.905→0.825; abstention precision 2.6×→1.74× random). Absolute lift small (80.9%→82.5% at 90% cov costs 10% coverage) because confident over-reading errors are invisible to any self-signal. Does NOT change champion/label/robustness status; it is a triage knob costing one extra mini call/row.
- Artifacts: `experiments/gan2026_reliability_d_gating_test450_2026-06-17.json`, `experiments/gan2026_reliability_d_gating_test450_2026-06-17.md`, `experiments/gan2026_reliability_d_gating_test450_samples_2026-06-17.jsonl`, ``.

### `gan2026_reliability_confidence_elicitation_pilot160_2026-06-17`
- Date/split: `2026-06-17`; `validation`; `160` rows.
- Pipeline: `reliability_confidence_elicitation`; mode `live`; replay `live`.
- Model role: DECOUPLED second-pass confidence elicitation over the canonical `v0_reference` production answers (decision 0018); production path NOT modified. Two predeclared variants — C (second-reader agreement) and D (failure-mode-primed correctness). Single-shot calibration probe; model `openai/gpt-4.1-mini`.
- Repair mode/config: `none (probability elicitation only; robust JSON parse with int fallback, 0 parse failures)`.
- Primary metrics: summary=n=160, failures=12; baseline joint self-confidence top-bucket=99.9%/AUROC=0.503 (chance); variant C top-bucket=40.6%, ECE=0.070, Brier=0.081, failure_AUROC=0.611; variant D top-bucket=78.1%, ECE=0.069, Brier=0.073, failure_AUROC=0.755; external-signal comparator AUROC=0.781; verdict (strict conjunctive gate) H0 both, but axes decompose: D recovers DISCRIMINATION (near-external AUROC) via failure-mode priming, C recovers spread-without-signal.
- Evidence validity: Validation-only; test450 untouched. Subject answers read per-row from `v0_reference` layer (single-SE-mini, decision 0018). Elicitation is a separate candidate self-signal, not a production change. Predeclared before run in ``. AUROC CIs wide (12 failures); validation750 needed to confirm D's 0.755.
- Claim language: Calibration probe. Joint self-confidence is dead (AUROC 0.503). Verbalized self-confidence is NOT strictly irrecoverable — naming the dominant unknown↔rate failure mode (variant D) recovers a discriminative self-signal (failure AUROC 0.755, near the external-corroboration 0.781) from one extra mini call, though it stays high-valued and still hides ~half the failures at ≥0.9. Second-reader framing (C) spreads confidence but the spread is noise (AUROC 0.611). Does not promote any candidate or change champion/robustness status.
- Artifacts: `experiments/gan2026_reliability_confidence_elicitation_pilot160_2026-06-17.json`, `experiments/gan2026_reliability_confidence_elicitation_pilot160_2026-06-17.md`, `experiments/gan2026_reliability_confidence_elicitation_samples_pilot160_C_2026-06-17.jsonl`, `experiments/gan2026_reliability_confidence_elicitation_samples_pilot160_D_2026-06-17.jsonl`.

### `gan2026_reliability_blend_external_plus_d_validation750_2026-06-17`
- Date/split: `2026-06-17`; `validation`; `748` rows.
- Pipeline: `reliability_blend_external_plus_d`; mode `replay`; replay `saved_output_replay`.
- Model role: none. Blends the P0.2 external composite risk (`3*(3-agreement)+source_flags+ambiguity`, from consensus votes + rq9 packet) with the variant-D self-signal (`1 - calibrated_confidence`, from the validation750 shadow run). Target = `v0_reference.comparison.purist_correct` (canonical, decision 0018); SE-pass vs v0_reference correctness mismatch = 0/748 (confirms shadow scored the canonical subject); model `none`.
- Primary metrics: summary=failure-prediction AUROC — external alone **0.783** (≈ P0.2's 0.781), variant D alone 0.684, rank-average blend **0.797** (Δ +0.014), CV-weighted held-out 0.786, whole-data best-w 0.795; Spearman(external-risk, D-risk) = 0.234; selective risk-coverage AUC ext 0.0392 vs blend ~similar; verdict H0_redundant (Δ < predeclared +0.02).
- Evidence validity: Validation-only; test450 untouched. No fitting in the headline (rank-average is unsupervised); the CV-weighted blend uses honest per-fold weight selection (no whole-data overfit).
- Claim language: Combining the cheap variant-D self-signal with external corroboration does NOT materially beat corroboration alone — the unsupervised rank-average edges external by only +0.014 (within CI on 87 errors), and the honest CV-weighted blend collapses to external alone (0.786 vs 0.783). NOT due to redundancy (Spearman only 0.234 → partly independent errors); D is simply the weaker/noisier ranker, so fusion mostly adds noise. External corroboration remains the single best forward-observable signal; D's value stays as a cheaper standalone proxy where 3-model agreement is unavailable. Does not change champion/robustness status.
- Artifacts: `experiments/gan2026_reliability_blend_external_plus_d_validation750_2026-06-17.json`, `experiments/gan2026_reliability_blend_external_plus_d_validation750_2026-06-17.md`.

### `gan2026_confidence_reviewer_shadow_validation750_2026-06-17`
- Date/split: `2026-06-17`; `validation`; `750` rows.
- Pipeline: `confidence_reviewer_shadow`; mode `live`; replay `live`.
- Model role: DECOUPLED variant-D confidence reviewer (`agentic/confidence_reviewer.py`, `variant_D_decoupled_v1`) wired as an opt-in SHADOW stage; stamps `calibrated_confidence` per row ALONGSIDE the intrinsic `selection.confidence`/`uncertainty` fields; GATES NOTHING, label/score path untouched; model `openai/gpt-4.1-mini`.
- Repair mode/config: `none (probability elicitation; robust JSON parse with int fallback)`.
- Primary metrics: summary=variant D top-bucket=76.5%, mean p=0.863, ECE=0.052, Brier=0.118, failure_AUROC=**0.684**; intrinsic in-pass `selection.confidence` top-bucket=99.5%, failure_AUROC=0.497 (chance) on same rows; external comparator AUROC=0.781; residual (n=269) mean p 0.843/acc 88.8% vs non-resid mean p 0.874/acc 88.1%.
- Evidence validity: Validation-only; test450 untouched. SE answers reused from `..._hybrid_structured_events_gpt41mini_2026-06-07.jsonl` (full 750-row coverage); reviewer scored against the SE pass's own `comparison.purist_correct`. Production-shape scale-confirmation of the pilot.
- Claim language: At validation750 scale and in production shape, the decoupled failure-mode-primed reviewer recovers GENUINE discrimination (AUROC 0.684 vs intrinsic-field chance 0.497) and survives integration — but it is WEAKER than the residual-enriched 160-row pilot implied (0.755, only 12 failures) and below external corroboration (0.781). Residual rows are not meaningfully less accurate on this distribution, so D's confidence barely drops there. Remains a SHADOW signal complementing (not replacing) external corroboration; not promoted to gating. Does not change champion/robustness status.
- Artifacts: `experiments/gan2026_confidence_reviewer_shadow_validation750_2026-06-17.json`, `experiments/gan2026_confidence_reviewer_shadow_validation750_2026-06-17.md`, `experiments/gan2026_confidence_reviewer_shadow_validation750_2026-06-17.jsonl`.

### `gan2026_confidence_one_vs_two_call_validation750_2026-06-17`
- Date/split: `2026-06-17`; `validation`; `750` rows.
- Pipeline: `confidence_one_vs_two_call_paired`; mode `live`; replay `live`.
- Model role: tests whether variant-D's discrimination comes from the DECOUPLED second call or simply the changed PROMPT WORDING (failure-mode priming). Joint arm = 1 call emitting `selection.answer_probability_correct` with the verbatim priming embedded; decoupled arm = existing `ConfidenceReviewer` over the joint answers; model `openai/gpt-4.1-mini`.
- Primary metrics: summary=joint(1-call) failure-AUROC **0.609** (ECE 0.050, Brier 0.119, top-bucket 91.0%); decoupled(2-call) failure-AUROC **0.641** (ECE 0.080, Brier 0.139, top-bucket 79.8%); **paired AUROC difference (decoupled − joint) = +0.032, 95% CI [−0.032, +0.098]** (1000 bootstrap reps; CI includes 0). Joint-arm Purist acc 0.863 (≈ SE baseline 0.881 — priming doesn't move the answer at scale). Comparators: decoupled-on-frozen-SE 0.684, intrinsic in-pass 0.497, external corroboration 0.781.
- Evidence validity: Validation-only; test450 untouched. 0 parse failures either arm; 13 unscorable-gold rows dropped. Internally valid paired comparison (both signals share the joint answer set).
- Claim language: **H_wording — the variant-D gain is a PROMPT-WORDING effect, not a decoupling effect.** Folding the verbatim failure-mode priming into the single extraction call recovers essentially the same failure-prediction discrimination (0.609 vs 0.641, difference CI straddles 0) at ONE call instead of two, with BETTER calibration (ECE/Brier). Falsifies the prior belief (recorded in `confidence_reviewer.py`) that joint-pass folding "re-degenerates" — it does not. The degenerate intrinsic `selection.confidence` (0.497) is degenerate because it is unprimed/categorical, not because it is in-pass. Both signals remain modest (<external 0.781) and gate nothing; the practical implication is the decoupled second call can be retired in favour of the free in-pass primed field.
- Artifacts: `experiments/gan2026_confidence_one_vs_two_call_validation750_2026-06-17.json`, `experiments/gan2026_confidence_one_vs_two_call_validation750_2026-06-17.md`, `experiments/gan2026_confidence_one_vs_two_joint_validation750_2026-06-17.jsonl`, `experiments/gan2026_confidence_one_vs_two_decoupled_validation750_2026-06-17.jsonl`, ``.

### `gan2026_confidence_one_vs_two_call_test450_2026-06-17`
- Date/split: `2026-06-17`; `test`; `450` rows.
- Pipeline: `confidence_one_vs_two_call_test450`; mode `live`; replay `live`.
- Model role: holdout confirmation of the validation paired test — does variant-D's discrimination come from the decoupled call or the prompt wording?; model `openai/gpt-4.1-mini`.
- Registry roles: `reliability_scorecard`, `component_ladder`.
- Primary metrics: summary=joint(1-call) failure-AUROC **0.601** (ECE 0.146, Brier 0.197, top-bucket 92.4%); decoupled(2-call) **0.669** (ECE 0.146, Brier 0.190, top-bucket 80.9%); **paired AUROC difference (decoupled − joint) = +0.068, 95% CI [+0.014, +0.132]** (1000 reps; CI EXCLUDES 0). Joint-arm Purist accuracy **0.767** (< SE test baseline 0.809 — priming degrades the extractor on the holdout). Comparators (validation750): joint 0.609, decoupled 0.641, diff CI [−0.032, +0.098].
- Evidence validity: Frozen aggregate-only holdout readout; no row-level test inspection; single run; preflight-gated. 0 parse failures either arm; 4 unscorable-gold rows dropped. Internally valid paired comparison (shared joint answer set).
- Claim language: **The validation H_wording conclusion does NOT replicate on the holdout.** On test450 the decoupled two-call reviewer ranks errors significantly better than the one-call joint signal (paired diff +0.068, CI excludes 0), and folding the priming into the extraction pass costs ~4pp Purist accuracy. Direction (decoupled ≥ joint) was consistent across both splits; validation lacked the gap/power to call it. CORRECTED conclusion: KEEP the two-call decoupled `ConfidenceReviewer` stage — the extra call earns its cost on the holdout; the validation-only "removable" read was a false economy. Retracts the earlier validation-based recommendation. Both signals remain modest (< external 0.781) and gate nothing.
- Artifacts: `experiments/gan2026_confidence_one_vs_two_call_test450_2026-06-17.json`, `experiments/gan2026_confidence_one_vs_two_call_test450_2026-06-17.md`, `experiments/gan2026_confidence_one_vs_two_joint_test450_2026-06-17.jsonl`, `experiments/gan2026_confidence_one_vs_two_decoupled_test450_2026-06-17.jsonl`, ``.

## Promote

### `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26`
- Date/split: `2026-06-26`; `test`; `450` rows.
- Pipeline: `consensus_fresh_agreement_selector_frozen_gate4_exact`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: No-call aggregate-only replay of frozen v0.9 selector over exact Gate 3 deterministic rules-tool, three-agent consensus, and fresh-evidence test components.; model `none`.
- Registry roles: `holdout_anchor`, `component_ladder`.
- Repair mode/config: `selector_v0_9_exact_source_no_call_replay`.
- Primary metrics: changed_label_precision=0.6, changed_labels=35, claim_scope=exact_v0_9_selector_holdout, correct_to_wrong=5, deterministic_purist_correct=343, exact_source_symmetry=yes, gate_passed=yes, net_purist_gain_vs_deterministic=16, row_level_output_written=no, selected_pragmatic_correct=368, selected_purist_correct=359, wrong_to_correct=21.
- Evidence validity: User-authorized frozen aggregate-only locked test450 audit. No row-level failures, rationales, evidence, selected events, or transitions are reported; source symmetry is exact for the documented source set.
- Cache/reuse source: Exact Gate 3 source set: rules-tool deterministic floor, exact three-agent consensus test450, and V12 fresh-evidence v0.6/safety-v0.9 test450 artifact.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_exact_source_symmetry_preflight_2026-06-26`, `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26`.
- Claim language: Exact-source Gate 4 promotion bars pass. Record as an exact v0.9 selector holdout result under the frozen source set. Do not tune from this test result or open row-level failures for development.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`, `experiments/build_gan2026_v09_frozen_gate4_exact_aggregate_audit.py`.

### `gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Stage D promotion gate: rebuilds the resolve_label graph query deterministically from the validation750 v4 claim-table and feeds it as a P2-gated fourth component to the frozen v0.9 selector replay on a predeclared 250-row residual-inclusive slice. No model calls and no holdout rows are read.; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `state_graph_resolve_label_promotion_gate_v1`.
- Primary metrics: graph_component_purist_correct=99, graph_mints_correct_for_no_correct=7, graph_mints_correct_for_predeclared_residual=7, no_correct_pool_rows=11, p1_unilateral_correct_to_wrong=147, p2_corroborated_correct_to_wrong=0, p2_corroborated_net_purist_gain=1, p2_corroborated_wrong_to_correct=1, p3_unknown_only_correct_to_wrong=71, predeclared_residual_rows=11, rows=250, v09_selected_purist_correct=238.
- Evidence validity: Validation-only saved-output replay on a predeclared 250-row slice containing all 11/750 no-correct residual rows (residual UNION first 239 non-residual rows in source order). Gold-free graph rebuild from the v4 claim-table (raw_frequency normalized, no diary/window arithmetic; v3->v4 extractor change is a declared confound held constant across the slice); gold labels used only for post-hoc Purist scoring. No holdout rows are read and no model calls are made.
- Cache/reuse source: claim_table:gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.jsonl;selector:gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl;residual_audit:gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.json.
- Claim language: Stage D promotion gate for the graph-as-component generator. Not a holdout-facing candidate; a promote decision clears the validation ladder only and test450 remains locked behind a separate frozen protocol. The graph enters the selector only under independent-corroboration gating (P2, the Stage C survivor); P1/P3 are effect bounds. Evaluated where the no-correct residual actually lives.
- Artifacts: `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15.json`, `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15.md`, `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_graphs.jsonl`, `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_rows.jsonl`.

### `gan2026_robustness_battery_v1_evidence_v0_7_gpt41mini_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `27` rows.
- Pipeline: `robustness_battery_generalization_adversary`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler (prompt v0.7 label-binding) scored live on authored-fresh OOD / adversarial cases for synthetic-artifact overfit and transfer.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `robustness_battery_v1`.
- Primary metrics: panel_A_both_correct_pairs=6, panel_A_overfit_only_pairs=0, panel_A_pairs=6, panel_A_pass=True, panel_B_cases=7, panel_B_correct=7, panel_B_pass=True, panel_C_cases=8, panel_C_correct=8, panel_C_fraction=1.0, panel_C_pass=True, verdict=transfers, weakest_axis=None.
- Evidence validity: Authored-fresh OOD/adversarial cases (NOT Gan rows, NOT test450 holdout). Gold Purist computed from authored labels via the project normalizer + labels.map_purist. Live gpt-4.1-mini, temperature 0. Transfer/overfit estimate, not a holdout benchmark.
- Cache/reuse source: experiments\gan2026_robustness_battery_v1_evidence_v0_7_checkpoints.
- Claim language: Cycle-3 fitness tier 2 robustness gate for the v0.7 label-binding candidate. 'transfers' is necessary (not sufficient) for Freeze Warden test450 authorisation; any failed bar returns the candidate as revise.
- Artifacts: `experiments/gan2026_robustness_battery_v1_evidence_v0_7_gpt41mini_2026-06-15.json`, `experiments/gan2026_robustness_battery_v1_evidence_v0_7_gpt41mini_2026-06-15.md`, `experiments/gan2026_robustness_battery_v1_cases.json`.

### `gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `750` rows.
- Pipeline: `fresh_evidence_reasoner`; mode `live`; replay `live`.
- Model role: V12 LLM-owned fresh-evidence reviewer over saved GPT/Qwen/DeepSeek structured-event scaffolding; the model may keep the original GPT structured-event final or replace it with a direct label grounded in exact raw-note evidence.; model `openai/gpt-4.1`.
- Registry roles: `component_ladder`, `historical_lineage`.
- Repair mode/config: `format-only label repair, exact-substring evidence filtering, and predeclared safety gates; fallback is only to the original GPT structured-event LLM final, not deterministic top.`.
- Primary metrics: call_failures=0, changed_label_precision_vs_v0=0.2857, changed_labels_vs_v0=147, correct_to_wrong_vs_v0=22, evidence_exact_substrings=703, final_minus_v0_purist_correct=21, final_pragmatic_correct=698, final_purist_correct=682, format_only_purist_correct=676, fresh_evidence_gate_fallbacks=8, fresh_evidence_replace_actions=182, net_purist_gain_vs_v0=20, parse_or_validation_failures=0, prediction_bearing_rows=749, raw_model_purist_correct=676, rows=750, v0_pragmatic_correct=679, v0_purist_correct=661, wrong_to_correct_vs_v0=42.
- Evidence validity: 703/750 final decisions cite exact raw-note evidence substrings after filtering; 0 call failures and 0 parse/schema/label failures.
- Cache/reuse source: Saved validation structured-event artifacts used as prompt scaffolding; no gold labels, row IDs, split labels, or deterministic top labels are provided to the model.
- Supersedes: `gan2026_cross_model_challenge_gated_adjudicator_v0_1_validation_ladder_2026-06-13`.
- Claim language: Validation-development promotion only: V12 v0.4 passed validation25, fixed hard50, family-slice, validation250, and full validation750 transfer checks. It is frozen as the current candidate for one explicit aggregate-only test450 authorization request; it is not yet a holdout result or benchmark-comparable claim.
- Artifacts: `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`, `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.md`.

### `gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13`
- Date/split: `2026-06-13`; `test_planned`; `0` rows.
- Pipeline: `fresh_evidence_reasoner_frozen_test_protocol`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only frozen-protocol authorization packet for the V12 fresh-evidence reasoner; pins the exact candidate, hashes, command, permitted aggregate readout, aggregate-only Markdown report behavior, CLI launch guard, deterministic preflight, and stop rule.; model `openai/gpt-4.1`.
- Repair mode/config: `no new repair; protocol freezes V12 v0.4 format repair, evidence filtering, and safety gates`.
- Primary metrics: authorization_required=yes, confirm_test_audit_required=yes, focused_frozen_gate_tests_passed=72, gan2026_pytest_modules_passed=1172, partial_test_subsets_allowed=no, preflight_ok=yes, ruff_guard_status=passed, target_test450_purist_correct=383, target_test450_purist_rate=0.8511, test_markdown_row_table_allowed=no, test_rows_read=0, v12_hard50_final_purist_correct=42, v12_validation250_final_purist_correct=242, v12_validation750_final_purist_correct=682, v12_validation750_v0_purist_correct=661.
- Evidence validity: No new prediction evidence. The protocol pins validation750 exact-evidence summary at 703/750, requires the CLI test-audit guard, has a passing deterministic preflight, emits aggregate-only test Markdown, and forbids row-level test inspection. Focused frozen gate tests pass 72/72, Ruff passes, and the full offline Gan pytest module suite passes 1172/1172 before authorization.
- Cache/reuse source: Protocol summarizes completed validation artifacts; makes no model calls and reads no test rows.
- Supersedes: `gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13`.
- Claim language: Pre-registration only, not a holdout result and not user authorization by itself. Use only if the user explicitly authorizes one frozen aggregate-only test450 audit.
- Artifacts: ``.

### `gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `750` rows.
- Pipeline: `agentic_structured_event_consensus`; mode `no_call_replay`; replay `saved_output_replay`.
- Model role: deterministic tool floor plus structured-event agent unanimity selector; model `panel: deterministic_rules_tool + gpt-4.1-mini + qwen3-235b-a22b + deepseek`.
- Registry roles: `component_ladder`.
- Repair mode/config: `exact_label_unanimity_over_structured_events`.
- Primary metrics: baseline_pragmatic_correct=704, baseline_purist_correct=697, changed_label_precision=0.22131147540983606, consensus_pragmatic_correct=713, consensus_purist_correct=708, correct_to_wrong=16, net_purist_gain=11, switched_labels=122, wrong_to_correct=27.
- Evidence validity: Validation-development saved-output replay over deterministic top plus three saved structured-event agent outputs; gold labels used only for post-hoc scoring.
- Claim language: First tool-floor + structured-event multi-agent consensus replay to exceed 700/750 Purist on validation. Promote the selector direction, with regression-filter hardening required before holdout.
- Artifacts: `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.jsonl`, `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.md`.

### `gan2026_agentic_structured_event_patch_recent_unresolved_burden_validation750_qwen3635b_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `750` rows.
- Pipeline: `agentic_structured_event_patch`; mode `validation750 no-call structured-event selection patch replay`; replay `saved_output_replay`.
- Model role: No-call tool/agent selection-patch replay over Qwen SE v0.6 structured events; the source LLM owns event extraction and baseline selection, while the patcher may only select an already extracted event through conservative gates.; model `none; saved ollama_chat/qwen3.6:35b structured-events outputs only`.
- Repair mode/config: `recent_unresolved_burden_v0 selection patch: non-selected frequency_rate event, temporality=recent, assertion_status=asserted, semantic_kind=unresolved_multiple, exact evidence, normalized label contains multiple`.
- Primary metrics: accepted_patches=2, baseline_pragmatic_correct=656, baseline_purist_accuracy=0.8507, baseline_purist_correct=638, changed_label_precision=1.0, changed_labels=2, correct_to_wrong=0, patched_pragmatic_correct=658, patched_purist_accuracy=0.8533, patched_purist_correct=640, row_count=750, wrong_to_correct=2.
- Evidence validity: Accepted patch evidence was exact-substring gated: 2/2 accepted patches passed; source artifact evidence_valid was 581/750.
- Cache/reuse source: experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl.
- Claim language: Promoted only as validation-development evidence that a narrow structured-event patch can improve the already successful Qwen SE substrate. No new model calls, no holdout rows, no row-level test inspection, and no multi-agent superiority claim.
- Artifacts: `experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_validation750_qwen3635b_2026-06-12.jsonl`, `experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_validation750_qwen3635b_2026-06-12.md`.

### `gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_boundary_guide_rescue_replay`; mode `no_call_replay`; replay `saved_output_replay`.
- Model role: D0 no-call boundary-guide rescue replay over saved E1/E2 validation hard50 traces; tests rescue-only policies using direct_no_tool_context and single_self_consistency_temperature fallbacks.; model `none`.
- Repair mode/config: `saved-output policy replay; no scorer or label repair changes`.
- Primary metrics: best_promotable_policy=higher_burden_only, cluster_restore_only_correct_to_wrong=0, cluster_restore_only_wrong_to_correct=2, higher_burden_only_changed_label_precision=0.75, higher_burden_only_changed_labels=4, higher_burden_only_correct_to_wrong=0, higher_burden_only_net_purist_gain=3, higher_burden_only_pragmatic_correct=36, higher_burden_only_purist_correct=35, higher_burden_only_wrong_to_correct=3, holdout_authorized=no, promoted_policy_count=1, rows=50.
- Evidence validity: No new prediction evidence. Replay uses saved validation hard50 E1/E2 final labels, normalized vote features, repair notes, and manifest slice tags for validation-only analysis.
- Cache/reuse source: experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.jsonl; experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl.
- Claim language: Validation-development no-call replay only. higher_burden_only passed the D0 gate (3 wrong-to-correct, 0 correct-to-wrong, precision 0.750), but this does not by itself authorize holdout use, benchmark claims, or live validation250 escalation.
- Artifacts: `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.jsonl`, `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.md`.

### `gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `12` rows.
- Pipeline: `agentic_boundary_audit_prompt_v2`; mode `saved_output_reparse`; replay `saved_output_replay`.
- Model role: D1 one-call boundary-audit prompt v2 over the predeclared validation micro-panel; fixed boundary-guide context only, parser candidates disabled.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `format-only audit-field shape repair plus existing label/evidence repair; parser candidates disabled as prompt context`.
- Primary metrics: call_failures=0, changed_label_precision=0.4286, changed_labels_vs_reference=7, e2_loss_sentinel_regressions=0, holdout_authorized=no, losses_vs_single_self_consistency_temperature=1, panel_gate=pass, parse_or_validation_failures=0, pragmatic_correct=10, purist_correct=10, rows=12, wins_vs_single_self_consistency_temperature=3.
- Evidence validity: 10/12 exact evidence substrings after saved-output reparse; no new prediction evidence during reparse.
- Cache/reuse source: live raw outputs in experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.jsonl.
- Supersedes: `gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12`.
- Claim language: Validation micro-panel development result only. Panel gate passed and authorized D1 hard50, but this artifact does not authorize broader validation or holdout use.
- Artifacts: `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.jsonl`, `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.md`.

## Promote Hybrid Structured Events Direction

### `gan2026_failure_mode_comparison_table_2026-06-12`
- Date/split: `2026-06-12`; `validation+test_aggregate`; `1200` rows.
- Pipeline: `gan2026_failure_mode_comparison`; mode `analysis-only`; replay `analysis_only`.
- Model role: Paper-facing consolidation of existing Gan 2026 failure-mode evidence for deterministic, fully LLM, hybrid_structured_events, CandidateSet hybrid, tool-using single-agent, and matched multi-agent comparators.; model `none`.
- Primary metrics: agentic_hard50_multi_agent_matched_purist=22, agentic_hard50_single_agent_tools_purist=20, agentic_hard50_single_greedy_purist=34, holdout_row_level_analysis=no, se_test450_purist_correct_of_rendered=364, se_test450_rendered=448, se_validation750_purist_correct_of_rendered=661, se_validation750_rendered=748.
- Evidence validity: No new run. Consolidates architecture-specific evidence metrics from existing validation750, aggregate test450, and validation hard50 artifacts; evidence metrics are not treated as interchangeable.
- Claim language: Analysis-only close-off table. Validation results are development evidence; locked test450 values are aggregate-only. Does not authorize row-level holdout tuning or any benchmark-comparable claim. Describes hybrid_structured_events as hybrid LLM extraction plus deterministic normalization/projection.
- Artifacts: ``.

### `gan2026_closeoff_report_2026-06-12`
- Date/split: `2026-06-12`; `validation+test`; `1200` rows.
- Pipeline: `gan2026_closeoff_synthesis`; mode `analysis-only`; replay `analysis_only`.
- Model role: Synthesis-only close-off report over existing Gan 2026 comparison, prompt-optimization, and frozen aggregate audit artifacts.; model `none`.
- Primary metrics: deepseek_se_v06_validation250_delta_purist_correct=5, gpt41mini_test450_se_pragmatic_correct_of_rendered=381, gpt41mini_test450_se_purist_correct_of_rendered=364, gpt41mini_test450_se_rendered=448, gpt41mini_validation750_se_purist_correct_of_rendered=661, gpt41mini_validation750_se_rendered=748, promoted_architecture=hybrid_structured_events, qwen_se_v06_validation250_delta_purist_correct=5.
- Evidence validity: Surfaces that evidence metrics differ by architecture: evidence_valid, evidence_text_contained, and CandidateSet source-id validity are not interchangeable.
- Claim language: Close-off implementation-direction synthesis. Promotes hybrid_structured_events as the current Gan 2026 direction while preserving split discipline: validation is development evidence; completed test450 audit is aggregate-only; no row-level holdout tuning or new benchmark claim is authorized.
- Artifacts: ``.

## Promote To Phase3 Report

### `gan2026_hybrid_v5_validation750_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `hybrid`; mode `live`; replay `assessment_stage_only`.
- Model role: hybrid clinical assessment probe (v5): CandidateSet -> clinical assessment schema; deterministic downstream (normalize/project/render/score/route) applied in deep-replay.; model `openai/gpt-4.1-mini`.
- Primary metrics: call_errors=0, parse_errors=1, prompt_version=gan2026_candidate_set_clinical_assessment_probe_v5, rows=750.
- Evidence validity: Assessment-stage probe only -- CandidateSet source-id validity rates are computed in deep-replay during report build, not in this artifact directly.
- Supersedes: `gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08`.
- Claim language: Phase 3 hybrid v5 prompt run (validation750, gpt-4.1-mini). Prompt bumped from v4 to gan2026_candidate_set_clinical_assessment_probe_v5. Four new instructions added to address Phase 3 failure modes: FM-6 (highest-frequency-type selection, not highest-severity), FM-2a (menstrual/cyclic risk-window seizure-free FP suppression), FM-2b (recent burst + seizure-free run stays frequency_rate not seizure_free), FM-5b (cluster_frequency only for true recurring grouped-episode patterns, not incidental use of word cluster). 750/750 rows, 0 call errors, 1 parse error, all at v5. Supersedes Phase 1 hybrid run (v4 prompt, gan2026_candidate_set_clinical_assessment_probe_v4).
- Artifacts: `experiments/gan2026_hybrid_v5_validation750_gpt41mini_2026-06-09.jsonl`.

## Revise

### `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26`
- Date/split: `2026-06-26`; `validation_hard_slice+robustness+test_planned`; `0` rows.
- Pipeline: `consensus_fresh_agreement_selector_frozen_protocol`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only frozen hard-slice, robustness, and locked-test protocol for selector v0.9; no model calls and no holdout rows are read.; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `selector_v0_9_protocol_no_new_repair`.
- Primary metrics: current_validation_correct_to_wrong=0, current_validation_selected_purist_correct=733, hard_slice_gate_required=yes, robustness_gate_required=yes, test_authorization_required=yes, test_rows_read=0.
- Evidence validity: No new prediction evidence. The protocol freezes selector code and source artifacts, requires hard-slice and robustness gates before test, and forbids test row-level inspection.
- Cache/reuse source: Existing v0.9 validation replay, synthetic stress, residual audit, and v0.10 repair probe artifacts; no new run.
- Claim language: Pre-registration only. Keeps v0.9 as component-ladder evidence until hard-slice, robustness, and explicitly authorized aggregate-only test gates pass; does not authorize test or row-level holdout inspection.
- Artifacts: `docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_source_symmetry_preflight_2026-06-26`
- Date/split: `2026-06-26`; `test_preflight_metadata_only`; `450` rows.
- Pipeline: `consensus_fresh_agreement_selector_frozen_gate3_source_symmetry_preflight`; mode `analysis-only`; replay `analysis_only`.
- Model role: analysis-only source-symmetry inventory over frozen deterministic, constrained consensus, fresh-evidence, and structured-event test artifacts; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `none`.
- Primary metrics: consensus_coverage=450, coverage_ok=yes, deterministic_coverage=450, duplicates_total=0, exact_consensus_available=no, fresh_evidence_coverage=450, gate_passed=yes, gate_scope=constrained_source_symmetry, locked_test_audit_authorized=no, off_manifest_total=0, prompt_hygiene_ok=yes, substrate_count=3.
- Evidence validity: Metadata-only inventory. Coverage and prompt-key hygiene checked without reporting test labels, correctness, rationales, evidence, selected events, or row-level transitions.
- Cache/reuse source: Existing frozen test450 component/source artifacts only; no model calls and no selector scoring.
- Claim language: Gate 3 passes only as constrained source-symmetry: deterministic, available two-agent consensus, fresh-evidence, and GPT/Qwen/DeepSeek source substrates each cover 450/450 manifest rows with 0 duplicates and 0 off-manifest rows. Exact three-agent consensus replay is not present, so any later Gate 4 audit requires explicit user authorization and must be labeled constrained holdout evidence, not an exact v0.9 selector holdout claim.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_source_symmetry_preflight_2026-06-26.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_source_symmetry_preflight_2026-06-26.md`, `experiments/build_gan2026_v09_frozen_gate3_source_symmetry_preflight.py`.

### `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_exact_source_symmetry_preflight_2026-06-26`
- Date/split: `2026-06-26`; `test_preflight_metadata_only`; `450` rows.
- Pipeline: `consensus_fresh_agreement_selector_frozen_gate3_exact_source_symmetry_preflight`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only exact source-symmetry inventory over deterministic rules-tool floor, exact three-agent consensus, fresh-evidence counterpart, and GPT/Qwen/DeepSeek source substrates.; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `none`.
- Primary metrics: consensus_coverage=450, coverage_ok=yes, deterministic_coverage=450, duplicates_total=0, fresh_evidence_coverage=450, gate_passed=yes, gate_scope=exact_source_symmetry, locked_test_audit_authorized=no, off_manifest_total=0, prompt_hygiene_ok=yes, role_parity_ok=yes, row_content_boundary_ok=yes.
- Evidence validity: Metadata-only exact-source inventory. Coverage, role parity, row-content boundary, and prompt-key hygiene checked without reporting test labels, correctness, rationales, evidence, selected events, or row-level transitions.
- Cache/reuse source: Existing frozen test450 component/source artifacts plus the newly generated exact three-agent consensus component; no model calls and no selector scoring.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_source_symmetry_preflight_2026-06-26`, `gan2026_agentic_structured_event_consensus_unanimous_exact_test450_2026-06-26`.
- Claim language: Exact-source Gate 3 passes and enables only a separately authorized fresh aggregate-only exact-source Gate 4 audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_exact_source_symmetry_preflight_2026-06-26.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_exact_source_symmetry_preflight_2026-06-26.md`, `experiments/build_gan2026_v09_frozen_gate3_exact_source_symmetry_preflight.py`.

### `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate2_robustness_stress_2026-06-26`
- Date/split: `2026-06-26`; `synthetic_source_near_validation_only`; `24` rows.
- Pipeline: `consensus_fresh_agreement_selector_frozen_gate2`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only Gate 2 robustness/stress panel over hand-specified synthetic/source-near component states using the frozen v0.9 selector; no model calls and no holdout rows are read.; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `selector_v0_9_frozen_gate2_no_new_repair`.
- Primary metrics: changed_label_precision=1.0, changed_labels=12, cluster_burden_demotions=0, correct_to_wrong=0, desired_action_match_rate=1.0, desired_action_matches=24, deterministic_correct_false_positive_actions=0, families_below_0_80=0, forbidden_no_reference_to_unknown_churn=0, gate_passed=yes, panel_rows=24, selected_pragmatic_correct=24, selected_purist_correct=23, test_rows_read=0, wrong_to_correct=12.
- Evidence validity: Synthetic/source-near mechanism panel only. Cases exercise all eight predeclared Gate 2 families with positive, deterministic-correct negative-control, and perturbation rows where natural; no locked test rows are read.
- Cache/reuse source: Hand-specified Gate 2 component states plus frozen selector implementation; no saved test artifacts opened.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26`.
- Claim language: Gate 2 passes as a mechanism test and authorizes only Gate 3 source-symmetry preflight. It remains component-ladder evidence; no test450 audit is authorized until Gate 3 passes and the user explicitly authorizes the frozen aggregate-only holdout audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate2_robustness_stress_2026-06-26.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate2_robustness_stress_2026-06-26.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26`
- Date/split: `2026-06-26`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector_frozen_gate1`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only Gate 1 hard-slice audit over frozen v0.9 validation replay and residual audit; no model calls and no holdout rows are read.; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `selector_v0_9_frozen_gate1_no_new_repair`.
- Primary metrics: band_submonthly_changed_precision=0.2, band_weekly_changed_precision=0.4, changed_label_precision=0.7347, changed_labels=49, correct_to_wrong=0, gate_passed=yes, residual_no_correct_component=11, selected_pragmatic_correct=735, selected_purist_correct=733, test_rows_read=0, wrong_to_correct=36.
- Evidence validity: Validation-only saved-output hard-slice audit. The replay exposes decision features and fresh-evidence boundary profiles but no explicit source-validity fields; no locked test rows are read.
- Cache/reuse source: Frozen v0.9 validation replay plus frozen residual component-generation audit from 2026-06-15.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26`.
- Claim language: Gate 1 passes but only advances the frozen selector to Gate 2 robustness/stress panels. Low changed-label precision in submonthly and weekly bands remains a portability risk; 11 residual wrong rows are excluded from selector-superiority claims because no current component can produce the gold label. No test450 audit is authorized.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26.md`.

### `gan2026_agentic_structured_event_consensus_unanimous_exact_test450_2026-06-26`
- Date/split: `2026-06-26`; `test_component_replay`; `450` rows.
- Pipeline: `agentic_structured_event_consensus`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: No-call exact three-agent consensus component replay over saved GPT, Qwen, and DeepSeek structured-event test artifacts plus the validation-matched rules-tool floor.; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `exact_three_agent_unanimous_label_component_replay`.
- Primary metrics: accepted_unanimous_exact_label=85, actions_keep_baseline=365, actions_switch_to_consensus=85, consensus_matches_baseline=160, missing_agent_rows=0, no_unanimous_exact_label=205, row_level_correctness_written=no.
- Evidence validity: Component-freeze artifact only. It writes source_row_index, labels, and consensus decision metadata, but no row-level correctness, failures, evidence, selected events, or transitions.
- Cache/reuse source: Saved test450 rules-tool baseline plus GPT, Qwen recent-patch, and DeepSeek v0.6 structured-event artifacts.
- Supersedes: `gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13`.
- Claim language: Generated to resolve the exact v0.9 source-parity blocker. It is not a Gate 4 result and does not authorize tuning or row-level test review.
- Artifacts: `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_test450_2026-06-26.jsonl`, `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_test450_2026-06-26.md`, `experiments/build_gan2026_exact_three_agent_consensus_test_replay.py`.

### `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140`
- Date/split: `2026-06-25`; `dev`; `140` rows.
- Pipeline: `exectv2_same_core_model_swap`; mode `live_plus_replay`; replay `live`.
- Model role: Qwen repair v02 structured key-family and Diagnosis producers; deterministic code owns SF projection/union, Prescription repair, and finding assembly replay.; model `ollama_chat/qwen3.6:35b`.
- Registry roles: `model_family_variant`.
- Repair mode/config: `qwen_output_contract_repair_v02 plus shared_standard_source_exact_evidence_repair`.
- Primary metrics: benchmark_cui_overall_f1=0.8049, call_failures=0, clinical_headline_f1=0.8319, diagnosis_f1=0.8473, evidence_valid_overall_f1=0.8049, final_lane_evidence_rate=1.0, investigations_f1=0.8755, parse_schema_failures=0, prescription_changed_rows_vs_v042=127, prescription_f1=0.8895, raw_candidate_overall_f1=0.7668, seizure_frequency_f1=0.7182, structured_evidence_invalid_after_standard_repair=3, structured_evidence_validity_rate_after_standard_repair=0.9964, structured_mentions_raw=827, structured_mentions_scored_after_standard_repair=824.
- Evidence validity: Structured saved-raw replay with standard source-exact repair: 824/827 scored, 3 invalid, 0.9964 validity. Final assembled lane diagnostics report 1.0000 exact evidence for Diagnosis, SeizureFrequency, Prescription, and Investigations.
- Cache/reuse source: Live structured and Diagnosis repair-v02 producers plus frozen deterministic same-core replay components; no full-200 or holdout row inspection.
- Supersedes: `exectv2_2call_no_sf_adjudicator_qwen36_dev140`.
- Claim language: Qwen repair v02 passes predeclared dev140 repair gates after shared source-exact evidence repair and completed downstream same-core assembly. Clinical-headline F1 is 0.8319 with SF 0.7182 and 0 call/parse failures. Full-200 aggregate-only follow-up completed separately on 2026-06-26.
- Artifacts: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.json`, `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.jsonl`, `docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_2026-06-25.md`, `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_repair_v02_dev140_readout_2026-06-25.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_diagnosis_decomposer.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_diagnosis_decomposer.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_structured_direct.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_structured_direct.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_state_projection_combined.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_state_projection_combined.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_unknown_suppression.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_unknown_suppression.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_union_arbitration.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_sf_union_arbitration.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_prescription_deterministic_repair_v03.jsonl`, `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140.json`, `docs/experiments/exectv2/reliability/exectv2_qwen_repair_v02_full200_predeclaration_2026-06-26.md`.

### `exectv2_2call_no_sf_adjudicator_qwen36_dev140`
- Date/split: `2026-06-25`; `dev`; `140` rows.
- Pipeline: `exectv2_same_core_model_swap`; mode `live_plus_replay`; replay `live`.
- Model role: ExECTv2 same-core structured key-family and Diagnosis extractor; deterministic code owns SF projection/union and Prescription repair.; model `ollama_chat/qwen3.6:35b`.
- Registry roles: `model_family_variant`.
- Repair mode/config: `qwen_compact_prompt_without_v02_output_contract_repair`.
- Primary metrics: call_failures=1, clinical_headline_f1=0.8018, diagnosis_f1=0.8027, investigations_f1=0.8354, min_evidence_rate=1.0, parse_schema_failures=12, prescription_f1=0.8895, seizure_frequency_f1=0.6919.
- Evidence validity: Min exact evidence rate 1.0000 on completed same-core dev140 comparison.
- Cache/reuse source: Same-core dev140 model-swap assembly with frozen deterministic replay components.
- Claim language: Diagnostic dev140 same-core model-swap row under the frozen exectv2_2call_no_sf_adjudicator_model_swap core. Qwen trails GPT-4.1-mini and DeepSeek on clinical_headline F1 and carries operational-stability caveats from 1 call failure and 12 parse/schema failures.
- Artifacts: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625.json`, `experiments/exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625.jsonl`, `docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_qwen36_dev140_2026-06-25.md`, `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_dev140.json`.

### `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140`
- Date/split: `2026-06-25`; `dev`; `140` rows.
- Pipeline: `exectv2_same_core_model_swap`; mode `live_plus_replay`; replay `live`.
- Model role: ExECTv2 same-core structured key-family and Diagnosis extractor; deterministic code owns SF projection/union and Prescription repair.; model `openai/gpt-4.1-mini`.
- Registry roles: `model_family_variant`.
- Primary metrics: call_failures=0, clinical_headline_f1=0.8396, diagnosis_f1=0.8573, investigations_f1=0.8347, min_evidence_rate=1.0, parse_schema_failures=0, prescription_f1=0.8895, seizure_frequency_f1=0.7645.
- Evidence validity: Min exact evidence rate 1.0000 on completed same-core dev140 comparison.
- Cache/reuse source: Same-core dev140 model-swap assembly with frozen deterministic replay components.
- Claim language: Operational reference row for the dev140 same-core model-swap comparison under the frozen exectv2_2call_no_sf_adjudicator_model_swap core. GPT-4.1-mini is cleaner operationally than DeepSeek/Qwen but trails DeepSeek on clinical_headline F1; not a full-200 or benchmark-win claim.
- Artifacts: `experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_20260625.json`, `experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_20260625.jsonl`, `docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_2026-06-25.md`, `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140.json`.

### `exectv2_2call_no_sf_adjudicator_deepseek_dev140`
- Date/split: `2026-06-25`; `dev`; `140` rows.
- Pipeline: `exectv2_same_core_model_swap`; mode `live_plus_replay`; replay `live`.
- Model role: ExECTv2 same-core structured key-family and Diagnosis extractor; deterministic code owns SF projection/union and Prescription repair.; model `deepseek/deepseek-chat`.
- Registry roles: `model_family_variant`.
- Primary metrics: call_failures=0, clinical_headline_f1=0.8596, diagnosis_f1=0.8845, investigations_f1=0.8966, min_evidence_rate=1.0, parse_schema_failures=1, prescription_f1=0.8895, seizure_frequency_f1=0.7658.
- Evidence validity: Min exact evidence rate 1.0000 on completed same-core dev140 comparison.
- Cache/reuse source: Same-core dev140 model-swap assembly with frozen deterministic replay components.
- Claim language: Diagnostic dev140 same-core model-swap row under the frozen exectv2_2call_no_sf_adjudicator_model_swap core. DeepSeek leads the completed dev140 comparison on clinical_headline F1 (0.8596) but carries an operational caveat from 1 parse/schema failure; not a full-200 or benchmark-win claim.
- Artifacts: `experiments/exectv2_2call_no_sf_adjudicator_deepseek_dev140_20260625.json`, `experiments/exectv2_2call_no_sf_adjudicator_deepseek_dev140_20260625.jsonl`, `docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_deepseek_dev140_2026-06-25.md`, `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_dev140.json`.

### `exectv2_llm_sf_verifier_v03_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_sf_verifier`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency-focused verifier v0.3 over the v0.5 single structured key-entity draft. The model owns normalized SeizureFrequency event text and may keep, delete, edit, or add SF mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Registry roles: `component_ladder`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_sf_verifier_v0.3, seizure_frequency_clinical_headline_f1=0.831, seizure_frequency_clinical_headline_precision=0.794, seizure_frequency_clinical_headline_recall=0.871, seizure_frequency_source_near_f1=0.831.
- Evidence validity: 0 call failures, 0 parse failures; 34/34 evidence-valid rendered mentions.
- Supersedes: `exectv2_llm_sf_verifier_v02_dev25_gpt41mini_20260618`.
- Claim language: First SeizureFrequency-specific candidate to clear the dev25 clinical-recovery target (0.831 > 0.8) while keeping evidence validity 1.0000. Development-surface success only; requires dev140 confirmation before any generalization claim.
- Artifacts: `experiments/exectv2_llm_sf_verifier_v03_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_sf_verifier_v03_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_verifier_v03_pilot_report_2026-06-18.md`.

### `exectv2_llm_sf_verifier_v02_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_sf_verifier`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency-focused verifier v0.2 over the v0.5 single structured key-entity draft. The model owns normalized SeizureFrequency event text and may keep, delete, edit, or add SF mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_sf_verifier_v0.2, seizure_frequency_clinical_headline_f1=0.788, seizure_frequency_clinical_headline_precision=0.743, seizure_frequency_clinical_headline_recall=0.839, seizure_frequency_source_near_f1=0.818.
- Evidence validity: 0 call failures, 0 parse failures; 35/35 evidence-valid rendered mentions.
- Supersedes: `exectv2_llm_sf_verifier_v01_dev25_gpt41mini_20260618`.
- Claim language: Strong near-miss SeizureFrequency verifier iteration. v0.2 improves over v0.1 (0.788 vs 0.667) and v0.5 single structured (0.633) while keeping evidence validity 1.0000, but remains just below the 0.8 target. One narrow residual pass is justified before dev140.
- Artifacts: `experiments/exectv2_llm_sf_verifier_v02_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_sf_verifier_v02_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_verifier_v02_pilot_report_2026-06-18.md`.

### `exectv2_llm_sf_verifier_v01_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_sf_verifier`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency-focused verifier v0.1 over the v0.5 single structured key-entity draft. The model owns normalized SeizureFrequency event text and may keep, delete, edit, or add SF mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_sf_verifier_v0.1, seizure_frequency_clinical_headline_f1=0.667, seizure_frequency_clinical_headline_precision=0.629, seizure_frequency_clinical_headline_recall=0.71, seizure_frequency_source_near_f1=0.727.
- Evidence validity: 0 call failures, 0 parse failures; 35/35 evidence-valid rendered mentions.
- Claim language: First SeizureFrequency verifier diagnostic over the v0.5 single structured draft. It improves recall and headline F1 over v0.5 single structured (0.667 vs 0.633) while keeping evidence validity 1.0000, but remains below the 0.8 target and loses precision. Revise from residual errors before dev140.
- Artifacts: `experiments/exectv2_llm_sf_verifier_v01_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_sf_verifier_v01_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_verifier_v01_pilot_report_2026-06-18.md`.

### `exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_only_key_entities_structured`; mode `live`; replay `native_run_split`.
- Model role: LLM-only single-prompt structured clinical event extractor over medication, diagnosis, seizure frequency, and investigations; deterministic code limited to schema/evidence gates, neutral attribute repair, CUI projection, and scoring.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: benchmark_per_item_f1=0.274, diagnosis_clinical_headline_f1=0.569, diagnosis_semantic_f1=0.407, evidence_validity_rate=0.9684, investigations_clinical_headline_f1=0.837, investigations_semantic_f1=0.512, parse_failures=0, phrase_only_per_item_f1=0.508, prescription_clinical_headline_f1=0.897, prescription_semantic_f1=0.204, prompt_version=exectv2_llm_only_key_entities_structured_v0.5, seizurefrequency_clinical_headline_f1=0.633, seizurefrequency_semantic_f1=0.433, semantic_per_item_f1=0.368, source_near_f1=0.729.
- Evidence validity: 0 call failures, 0 parse failures; 153/158 evidence-valid rendered mentions (0.9684).
- Supersedes: `exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618`.
- Claim language: Best single-prompt structured dev25 candidate so far, but revise-only. v0.5 lifts Diagnosis headline F1 (0.460->0.569) while preserving medication (0.897) and Investigations (0.837) above target and SF near v0.4 (0.633). Next: specialist Diagnosis prompt comparison on dev25 before dev140.
- Artifacts: `experiments/exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_key_entities_structured_v05_pilot_report_2026-06-18.md`.

### `exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_only_key_entities_structured`; mode `live`; replay `native_run_split`.
- Model role: LLM-only single-prompt structured clinical event extractor over medication, diagnosis, seizure frequency, and investigations; deterministic code limited to schema/evidence gates, neutral attribute repair, CUI projection, and scoring.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: benchmark_per_item_f1=0.256, diagnosis_clinical_headline_f1=0.46, diagnosis_semantic_f1=0.202, evidence_validity_rate=0.9695, investigations_clinical_headline_f1=0.837, investigations_semantic_f1=0.558, parse_failures=0, phrase_only_per_item_f1=0.446, prescription_clinical_headline_f1=0.9, prescription_semantic_f1=0.192, prompt_version=exectv2_llm_only_key_entities_structured_v0.4, seizurefrequency_clinical_headline_f1=0.644, seizurefrequency_semantic_f1=0.441, semantic_per_item_f1=0.295, source_near_f1=0.728.
- Evidence validity: 0 call failures, 0 parse failures; 159/164 evidence-valid rendered mentions (0.9695).
- Supersedes: `exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618`.
- Superseded by: `exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618`.
- Claim language: Best single-prompt structured dev25 candidate so far, but revise-only. v0.4 recovers SeizureFrequency headline F1 (0.421->0.644) while preserving medication (0.900) and Investigations (0.837) above target. Diagnosis remains the bottleneck (0.460), so next v0.5 should focus on Diagnosis hard cases before dev140 or specialist-prompt comparison.
- Artifacts: `experiments/exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_key_entities_structured_v04_pilot_report_2026-06-18.md`.

### `exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_only_key_entities_structured`; mode `live`; replay `native_run_split`.
- Model role: LLM-only single-prompt structured clinical event extractor over medication, diagnosis, seizure frequency, and investigations; deterministic code limited to schema/evidence gates, neutral attribute repair, CUI projection, and scoring.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: benchmark_per_item_f1=0.235, diagnosis_clinical_headline_f1=0.455, diagnosis_semantic_f1=0.257, evidence_validity_rate=0.9441, investigations_clinical_headline_f1=0.878, investigations_semantic_f1=0.585, parse_failures=0, phrase_only_per_item_f1=0.436, prescription_clinical_headline_f1=0.883, prescription_semantic_f1=0.198, prompt_version=exectv2_llm_only_key_entities_structured_v0.3, seizurefrequency_clinical_headline_f1=0.421, seizurefrequency_semantic_f1=0.246, semantic_per_item_f1=0.282, source_near_f1=0.718.
- Evidence validity: 0 call failures, 0 parse failures; 152/161 evidence-valid rendered mentions (0.9441).
- Supersedes: `exectv2_llm_only_key_entities_structured_v02_dev25_gpt41mini_20260618`.
- Superseded by: `exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618`.
- Claim language: Revise-only development pilot for v0.3 single structured schema + single prompt. Medication and Investigations clear the clinical-recovery headline target (0.883/0.878), Diagnosis improves modestly (0.455), but SeizureFrequency regresses (0.421) and evidence validity falls (0.9441). Not promoted; next v0.4 should preserve medication/investigation wins and isolate SF headline-state misses.
- Artifacts: `experiments/exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_key_entities_structured_v03_pilot_report_2026-06-18.md`.

### `exectv2_llm_only_key_entities_structured_v02_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_only_key_entities_structured`; mode `live`; replay `native_run_split`.
- Model role: LLM-only single-prompt structured clinical event extractor over medication, diagnosis, seizure frequency, and investigations; deterministic code limited to schema/evidence gates, neutral attribute repair, CUI projection, and scoring.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: benchmark_per_item_f1=0.22, diagnosis_clinical_headline_f1=0.414, diagnosis_semantic_f1=0.283, evidence_validity_rate=0.976, investigations_clinical_headline_f1=0.783, investigations_semantic_f1=0.522, parse_failures=0, phrase_only_per_item_f1=0.408, prescription_clinical_headline_f1=0.846, prescription_semantic_f1=0.172, prompt_version=exectv2_llm_only_key_entities_structured_v0.2, seizurefrequency_clinical_headline_f1=0.456, seizurefrequency_semantic_f1=0.21, semantic_per_item_f1=0.272, source_near_f1=0.68.
- Evidence validity: 0 call failures, 0 parse failures; 163/167 evidence-valid rendered mentions (0.9760).
- Supersedes: `exectv2_llm_only_key_entities_structured_dev25_gpt41mini_20260618`.
- Superseded by: `exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618`.
- Claim language: Development pilot for error-analysis-led v0.2 of the single structured schema + single prompt key-family architecture. Improved semantic item F1 0.206->0.272 and benchmark 0.158->0.220 with clean gate; refreshed clinical-recovery headlines show medication above target (0.846), Investigations near target (0.783), and Diagnosis/SF still below target (0.414/0.456). Not promoted. Next: v0.3 Diagnosis/SF hard-case panel, Investigation FP cleanup, and medication regression protection before dev140.
- Artifacts: `experiments/exectv2_llm_only_key_entities_structured_v02_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_only_key_entities_structured_v02_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_key_entities_structured_v02_pilot_report_2026-06-18.md`.

### `exectv2_llm_only_key_entities_structured_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_only_key_entities_structured`; mode `live`; replay `native_run_split`.
- Model role: LLM-only single-prompt structured clinical event extractor over medication, diagnosis, seizure frequency, and investigations; deterministic code limited to schema/evidence gates, neutral attribute repair, CUI projection, and scoring.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only`.
- Primary metrics: benchmark_per_item_f1=0.158, diagnosis_semantic_f1=0.204, evidence_validity_rate=0.9539, investigations_semantic_f1=0.267, parse_failures=0, phrase_only_per_item_f1=0.385, prescription_semantic_f1=0.264, prompt_version=exectv2_llm_only_key_entities_structured_v0.1, seizurefrequency_semantic_f1=0.07, semantic_per_item_f1=0.206, source_near_f1=0.722.
- Evidence validity: 0 call failures, 0 parse failures; 145/152 evidence-valid rendered mentions (0.9539).
- Claim language: Development pilot for the user-requested single structured schema + single prompt extreme over the four key families (Prescription/medication, Diagnosis, SeizureFrequency, Investigations). Viable schema and evidence gate, not promoted: source-near F1 0.722 but semantic item F1 only 0.206; next iteration should target attribute agreement and phrase altitude, especially SeizureFrequency quantification.
- Artifacts: `experiments/exectv2_llm_only_key_entities_structured_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_only_key_entities_structured_dev25_gpt41mini_20260618.md`.

### `exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_med_inv_verifier`; mode `live`; replay `native_run_split`.
- Model role: Prescription/Investigations verifier v0.1 over the v0.5 single structured key-entity draft. The model owns revised Prescription and Investigations mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Registry roles: `component_ladder`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: evidence_validity_rate=0.9792, investigations_f1=0.496, parse_failures=0, prescription_f1=0.817, prescription_precision=0.773, prescription_recall=0.865, prompt_version=exectv2_llm_med_inv_verifier_v0.1.
- Evidence validity: 0 call failures, 0 parse failures; 376/384 evidence-valid rendered mentions.
- Claim language: Split decision. Use v0.1 as the current Prescription candidate because it clears dev140 target (0.817 > 0.8), but reject it for Investigations because it regresses from the single structured baseline (0.496 vs 0.786). Build a dedicated Investigations verifier next.
- Artifacts: `experiments/exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618.md`, `docs/experiments/exectv2/medication_investigations/exectv2_med_inv_verifier_v01_dev140_report_2026-06-18.md`.

### `exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_investigations_verifier`; mode `live`; replay `native_run_split`.
- Model role: Investigations-focused verifier v0.1 over the v0.5 single structured key-entity draft. The model owns revised Investigations mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Registry roles: `component_ladder`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: evidence_validity_rate=0.9928, investigations_f1=0.872, investigations_precision=0.869, investigations_recall=0.875, parse_failures=0, prompt_version=exectv2_llm_investigations_verifier_v0.1.
- Evidence validity: 0 call failures, 0 parse failures; 137/138 evidence-valid rendered mentions.
- Claim language: First Investigations-specific candidate to clear the dev140 clinical-recovery target (0.872 > 0.8). Confirms Investigations should be split from medication verification.
- Artifacts: `experiments/exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.md`, `docs/experiments/exectv2/medication_investigations/exectv2_investigations_verifier_v01_dev140_report_2026-06-18.md`.

### `exectv2_llm_diagnosis_verifier_v05_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_diagnosis_verifier`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis-focused verifier v0.5 over the v0.5 single structured key-entity draft. The model owns normalized Diagnosis concept text and may keep, delete, edit, or add Diagnosis mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Registry roles: `component_ladder`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: diagnosis_clinical_headline_f1=0.837, diagnosis_clinical_headline_precision=0.911, diagnosis_clinical_headline_recall=0.774, diagnosis_semantic_item_f1=0.62, diagnosis_source_near_f1=0.84, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_diagnosis_verifier_v0.5.
- Evidence validity: 0 call failures, 0 parse failures; 44/44 evidence-valid rendered mentions.
- Supersedes: `exectv2_llm_diagnosis_verifier_v04_dev25_gpt41mini_20260618`.
- Claim language: First Diagnosis-specific candidate to clear the dev25 clinical-recovery target (0.837 > 0.8) while keeping evidence validity 1.0000. Development-surface success only; requires dev140 confirmation before any generalization claim. Shift key-entity work to SeizureFrequency next.
- Artifacts: `experiments/exectv2_llm_diagnosis_verifier_v05_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_diagnosis_verifier_v05_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_verifier_v05_pilot_report_2026-06-18.md`.

### `exectv2_llm_diagnosis_verifier_v04_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_diagnosis_verifier`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis-focused verifier v0.4 over the v0.5 single structured key-entity draft. The model owns normalized Diagnosis concept text and may keep, delete, edit, or add Diagnosis mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: diagnosis_clinical_headline_f1=0.768, diagnosis_clinical_headline_precision=0.826, diagnosis_clinical_headline_recall=0.717, diagnosis_semantic_item_f1=0.554, diagnosis_source_near_f1=0.792, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_diagnosis_verifier_v0.4.
- Evidence validity: 0 call failures, 0 parse failures; 45/45 evidence-valid rendered mentions.
- Supersedes: `exectv2_llm_diagnosis_verifier_v03_dev25_gpt41mini_20260618`.
- Claim language: Best Diagnosis-specific candidate so far, but revise-only. v0.4 improves over verifier v0.3 (0.768 vs 0.701) and v0.5 single structured (0.569) while keeping evidence validity 1.0000, but remains just below the 0.8 target. One more residual-error iteration is justified before dev140 if precision stays protected.
- Artifacts: `experiments/exectv2_llm_diagnosis_verifier_v04_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_diagnosis_verifier_v04_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_verifier_v04_pilot_report_2026-06-18.md`.

### `exectv2_llm_diagnosis_verifier_v03_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_diagnosis_verifier`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis-focused verifier v0.3 over the v0.5 single structured key-entity draft. The model owns normalized Diagnosis concept text and may keep, delete, edit, or add Diagnosis mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: diagnosis_clinical_headline_f1=0.701, diagnosis_clinical_headline_precision=0.773, diagnosis_clinical_headline_recall=0.641, diagnosis_semantic_item_f1=0.49, diagnosis_source_near_f1=0.755, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_diagnosis_verifier_v0.3.
- Evidence validity: 0 call failures, 0 parse failures; 42/42 evidence-valid rendered mentions.
- Supersedes: `exectv2_llm_diagnosis_verifier_v02_dev25_gpt41mini_20260618`.
- Claim language: Best Diagnosis-specific candidate so far, but revise-only. v0.3 improves over verifier v0.2 (0.701 vs 0.619) and v0.5 single structured (0.569) while keeping evidence validity 1.0000, but remains below the 0.8 target. Run v0.4 from residual error analysis before dev140.
- Artifacts: `experiments/exectv2_llm_diagnosis_verifier_v03_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_diagnosis_verifier_v03_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_verifier_v03_pilot_report_2026-06-18.md`.

### `exectv2_llm_diagnosis_verifier_v02_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_diagnosis_verifier`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis-focused verifier v0.2 over the v0.5 single structured key-entity draft. The model owns normalized Diagnosis concept text and may keep, delete, edit, or add Diagnosis mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: diagnosis_clinical_headline_f1=0.619, diagnosis_clinical_headline_precision=0.682, diagnosis_clinical_headline_recall=0.566, diagnosis_semantic_item_f1=0.424, diagnosis_source_near_f1=0.727, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_diagnosis_verifier_v0.2.
- Evidence validity: 0 call failures, 0 parse failures; 43/43 evidence-valid rendered mentions (1.0000).
- Supersedes: `exectv2_llm_diagnosis_verifier_v01_dev25_gpt41mini_20260618`.
- Claim language: Best Diagnosis-specific multi-prompt candidate so far, but revise-only. v0.2 improves over verifier v0.1 (0.619 vs 0.592) and v0.5 single structured (0.569) while keeping evidence validity 1.0000, but remains recall-limited and below the 0.8 target.
- Artifacts: `experiments/exectv2_llm_diagnosis_verifier_v02_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_diagnosis_verifier_v02_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_verifier_v02_pilot_report_2026-06-18.md`.

### `exectv2_llm_diagnosis_verifier_v01_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_diagnosis_verifier`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis-focused verifier over the v0.5 single structured key-entity draft. The model may keep, delete, edit, or add Diagnosis mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: diagnosis_clinical_headline_f1=0.592, diagnosis_clinical_headline_precision=0.644, diagnosis_clinical_headline_recall=0.547, diagnosis_semantic_item_f1=0.449, diagnosis_source_near_f1=0.694, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_diagnosis_verifier_v0.1.
- Evidence validity: 0 call failures, 0 parse failures; 42/42 evidence-valid rendered mentions (1.0000).
- Supersedes: `exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618`.
- Superseded by: `exectv2_llm_diagnosis_verifier_v02_dev25_gpt41mini_20260618`.
- Claim language: First multi-prompt variant to improve over the best single structured Diagnosis candidate (0.592 vs v0.5 0.569), but still far below the 0.8 target and recall-limited. Revise with targeted Diagnosis recall before dev140.
- Artifacts: `experiments/exectv2_llm_diagnosis_verifier_v01_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_diagnosis_verifier_v01_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_verifier_v01_pilot_report_2026-06-18.md`.

### `exectv2_key_entities_dev140_transfer_readout_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_key_entities_transfer_readout`; mode `live`; replay `analysis_only`.
- Model role: Transfer readout combining the single structured v0.5 dev140 draft with Diagnosis verifier v0.5 and SeizureFrequency verifier v0.3 dev140 runs.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema/evidence repair + benchmark CUI projection only; per-family outputs reported separately`.
- Primary metrics: diagnosis_verifier_f1=0.616, investigations_f1=0.786, prescription_f1=0.777, seizure_frequency_verifier_f1=0.602, structured_call_failures=0, structured_parse_failures=0.
- Evidence validity: Structured draft evidence validity 0.9563; Diagnosis verifier 0.9832; SeizureFrequency verifier 0.9796. All three dev140 runs had 0 call failures and 0 parse failures.
- Supersedes: `exectv2_llm_sf_verifier_v03_dev25_gpt41mini_20260618`, `exectv2_llm_diagnosis_verifier_v05_dev25_gpt41mini_20260618`.
- Claim language: Negative transfer readout. The dev25 target-clearing configuration does not transfer to dev140: all four key families remain below 0.8. Medication and Investigations are near misses; Diagnosis and SeizureFrequency require dev140 residual-led development. Do not promote or claim generalization from dev25.
- Artifacts: `experiments/exectv2_llm_only_key_entities_structured_v05_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_only_key_entities_structured_v05_dev140_gpt41mini_20260618.md`, `experiments/exectv2_llm_diagnosis_verifier_v05_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_diagnosis_verifier_v05_dev140_gpt41mini_20260618.md`, `experiments/exectv2_llm_sf_verifier_v03_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_sf_verifier_v03_dev140_gpt41mini_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_key_entities_dev140_transfer_readout_2026-06-18.md`.

### `exectv2_key_entities_clinical_error_ledger_diagv06_sfv04_dev140_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_key_entities_clinical_error_ledger`; mode `analysis-only`; replay `analysis_only`.
- Model role: Clinical-recovery error ledger over the residual-led dev140 Diagnosis v0.6 and SeizureFrequency v0.4 artifacts. Prescription/Investigations are unchanged from the single structured substrate in this ledger and should not supersede their current family-specific candidates.; model `none`.
- Repair mode/config: `no model calls; clinical-recovery key analysis only`.
- Primary metrics: diagnosis_f1=0.651, records=547, seizure_frequency_f1=0.623.
- Evidence validity: No new model calls. Ledger keys are the same clinical-recovery keys used by the headline scorers.
- Cache/reuse source: Read-only analysis over exectv2_llm_only_key_entities_structured_v05_dev140_gpt41mini_20260618, exectv2_llm_diagnosis_verifier_v06_dev140_gpt41mini_20260618, and exectv2_llm_sf_verifier_v04_dev140_gpt41mini_20260618.
- Supersedes: `exectv2_key_entities_clinical_error_ledger_dev140_20260618`.
- Claim language: Diagnostic residual taxonomy for the next Diagnosis/SF architecture loop. Current promoted family candidates remain Prescription verifier v0.1 and Investigations verifier v0.1; this ledger is for remaining below-target families.
- Artifacts: `experiments/exectv2_key_entities_clinical_error_ledger_diagv06_sfv04_dev140_20260618.json`, `experiments/exectv2_key_entities_clinical_error_ledger_diagv06_sfv04_dev140_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_diag_sf_verifier_v06_v04_dev140_report_2026-06-18.md`.

### `exectv2_key_entities_clinical_error_ledger_dev140_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_key_entities_clinical_error_ledger`; mode `analysis-only`; replay `analysis_only`.
- Model role: Clinical-recovery error ledger over the dev140 transfer artifacts: single structured v0.5 for Prescription/Investigations, Diagnosis verifier v0.5, and SeizureFrequency verifier v0.3.; model `none`.
- Repair mode/config: `no model calls; clinical-recovery key analysis only`.
- Primary metrics: diagnosis_f1=0.616, investigations_f1=0.786, prescription_f1=0.777, records=569, seizure_frequency_f1=0.602.
- Evidence validity: No new model calls. Ledger keys are the same clinical-recovery keys used by the headline scorers.
- Cache/reuse source: Read-only analysis over exectv2_llm_only_key_entities_structured_v05_dev140_gpt41mini_20260618, exectv2_llm_diagnosis_verifier_v05_dev140_gpt41mini_20260618, and exectv2_llm_sf_verifier_v03_dev140_gpt41mini_20260618.
- Supersedes: `exectv2_key_entities_dev140_transfer_readout_20260618`.
- Claim language: Diagnostic residual taxonomy for the failed dev140 transfer readout. Use this as the control surface for the next targeted verifier iteration; do not treat it as a promoted candidate.
- Artifacts: `experiments/exectv2_key_entities_clinical_error_ledger_dev140_20260618.json`, `experiments/exectv2_key_entities_clinical_error_ledger_dev140_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_key_entities_dev140_clinical_error_ledger_readout_2026-06-18.md`.

### `exectv2_hybrid_sf_state_adjudicator_v05_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.5 pilot over the v0.5 single structured key-entity draft. v0.5 adds explicit seizure-free-anchor specialization while preserving typed candidate metadata.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic typed candidate spans and seizure-free anchor guide are attention scaffolding, not predictions`.
- Primary metrics: candidate_spans=79, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.5, seizure_frequency_f1=0.918, seizure_frequency_precision=0.933, seizure_frequency_recall=0.903.
- Evidence validity: 0 call failures, 0 parse failures; 30/30 evidence-valid rendered mentions.
- Supersedes: `exectv2_hybrid_sf_state_adjudicator_v04_dev25_gpt41mini_20260618`.
- Claim language: Pilot-only signal. v0.5 remains above target on dev25 but below v0.4 local F1; dev140 transfer is the decision surface.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v05_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v05_dev25_gpt41mini_20260618.md`.

### `exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.5 over the v0.5 single structured key-entity draft. v0.5 specializes seizure-free anchors and adds residual-supported benchmark-format SF CUI projection variants.; model `openai/gpt-4.1-mini`.
- Registry roles: `component_ladder`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic typed candidate spans and seizure-free anchor guide are attention scaffolding, not predictions`.
- Primary metrics: active_rate_f1=0.762, candidate_spans=414, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.5, seizure_free_f1=0.781, seizure_frequency_f1=0.721, seizure_frequency_precision=0.71, seizure_frequency_recall=0.733, unknown_f1=0.476.
- Evidence validity: 0 call failures, 0 parse failures; 193/193 evidence-valid rendered mentions. Residual ledger is analysis-only over the same JSONL.
- Supersedes: `exectv2_hybrid_sf_state_adjudicator_v04_dev140_gpt41mini_20260618`.
- Claim language: Revise-only current best SF candidate. Seizure-free specialization improves dev140 from 0.707 to 0.721 and seizure-free F1 from 0.738 to 0.781, but unknown-state regression keeps the family below the 0.8 target.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618.md`, `experiments/exectv2_sf_state_adjudicator_v05_residual_ledger_dev140_20260618.json`, `experiments/exectv2_sf_state_adjudicator_v05_residual_ledger_dev140_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_state_adjudicator_v05_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_sf_state_adjudicator_v04_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.4 pilot over the v0.5 single structured key-entity draft. v0.4 adds typed candidate metadata for generic/named active-rate, seizure-free anchors, qualitative change, prior-event references, and reject contexts.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic typed candidate spans are attention scaffolding, not predictions`.
- Primary metrics: candidate_spans=79, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.4, seizure_frequency_f1=0.935, seizure_frequency_precision=0.935, seizure_frequency_recall=0.935.
- Evidence validity: 0 call failures, 0 parse failures; 31/31 evidence-valid rendered mentions.
- Supersedes: `exectv2_hybrid_sf_state_adjudicator_v03_dev25_gpt41mini_20260618`.
- Claim language: Pilot-only escalation signal. Typed candidate decomposition stayed strong on dev25 and justified dev140 transfer testing.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v04_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v04_dev25_gpt41mini_20260618.md`.

### `exectv2_hybrid_sf_state_adjudicator_v04_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.4 over the v0.5 single structured key-entity draft. v0.4 adds typed candidate metadata before LLM adjudication while leaving final mention selection to the model.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic typed candidate spans are attention scaffolding, not predictions`.
- Primary metrics: active_rate_f1=0.746, candidate_spans=412, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.4, seizure_free_f1=0.738, seizure_frequency_f1=0.707, seizure_frequency_precision=0.704, seizure_frequency_recall=0.711, unknown_f1=0.525.
- Evidence validity: 0 call failures, 0 parse failures; 189/189 evidence-valid rendered mentions. Residual ledger is analysis-only over the same JSONL.
- Supersedes: `exectv2_hybrid_sf_state_adjudicator_v03_dev140_gpt41mini_20260618`.
- Claim language: Revise-only current best SF candidate. Typed candidate decomposition improves dev140 from 0.681 to 0.707 but remains below the 0.8 target; next loop should specialize seizure-free anchors.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v04_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v04_dev140_gpt41mini_20260618.md`, `experiments/exectv2_sf_state_adjudicator_v04_residual_ledger_dev140_20260618.json`, `experiments/exectv2_sf_state_adjudicator_v04_residual_ledger_dev140_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_state_adjudicator_v04_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_sf_state_adjudicator_v03_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.3 pilot over the v0.5 single structured key-entity draft. v0.3 adds a separate unknown/change-state recovery lane on top of the v0.2 generic keep/reject policy; the model owns final mention selection and state choice.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic candidate spans are attention scaffolding, not predictions`.
- Primary metrics: candidate_spans=79, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.3, seizure_frequency_f1=0.921, seizure_frequency_precision=0.906, seizure_frequency_recall=0.935.
- Evidence validity: 0 call failures, 0 parse failures; 32/32 evidence-valid rendered mentions.
- Supersedes: `exectv2_hybrid_sf_state_adjudicator_v02_dev25_gpt41mini_20260618`.
- Claim language: Pilot-only continuation of the unknown/change-state recovery loop. v0.3 remained strong on dev25 but lower than v0.2; full dev140 was still required for transfer evidence.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v03_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v03_dev25_gpt41mini_20260618.md`.

### `exectv2_hybrid_sf_state_adjudicator_v03_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.3 over the v0.5 single structured key-entity draft. v0.3 adds a separate unknown/change-state recovery lane after v0.2 improved precision but collapsed unknown-state recall.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic candidate spans are attention scaffolding, not predictions`.
- Primary metrics: active_rate_f1=0.722, candidate_spans=412, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.3, seizure_free_f1=0.754, seizure_frequency_f1=0.681, seizure_frequency_precision=0.667, seizure_frequency_recall=0.695, unknown_f1=0.424.
- Evidence validity: 0 call failures, 0 parse failures; 195/195 evidence-valid rendered mentions. Residual ledger is analysis-only over the same JSONL.
- Supersedes: `exectv2_hybrid_sf_state_adjudicator_v02_dev140_gpt41mini_20260618`.
- Claim language: Revise-only. Best SF dev140 score so far (0.681) and unknown-state F1 improves from 0.235 to 0.424, but the gain is small and still below the 0.8 target. Next loop should use typed candidate decomposition plus constrained state classification rather than more broad prompt accretion.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v03_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v03_dev140_gpt41mini_20260618.md`, `experiments/exectv2_sf_state_adjudicator_v03_residual_ledger_dev140_20260618.json`, `experiments/exectv2_sf_state_adjudicator_v03_residual_ledger_dev140_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_state_adjudicator_v03_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_sf_state_adjudicator_v02_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.2 pilot over the v0.5 single structured key-entity draft. v0.2 adds stricter generic active-rate/seizure-free/unknown keep-reject policy; the model still owns final mention selection and state choice.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic candidate spans are attention scaffolding, not predictions`.
- Primary metrics: candidate_spans=79, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.2, seizure_frequency_f1=0.951, seizure_frequency_precision=0.967, seizure_frequency_recall=0.935.
- Evidence validity: 0 call failures, 0 parse failures; 30/30 evidence-valid rendered mentions.
- Supersedes: `exectv2_hybrid_sf_state_adjudicator_v01_dev25_gpt41mini_20260618`.
- Claim language: Pilot-only escalation signal. Strong dev25 precision improvement (0.951 F1, precision 0.967) justified dev140, but the effect did not transfer.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v02_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v02_dev25_gpt41mini_20260618.md`.

### `exectv2_hybrid_sf_state_adjudicator_v02_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.2 over the v0.5 single structured key-entity draft. v0.2 adds stricter generic active-rate/seizure-free/unknown keep-reject policy; the model still owns final mention selection and state choice.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic candidate spans are attention scaffolding, not predictions`.
- Primary metrics: active_rate_f1=0.725, candidate_spans=412, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.2, seizure_free_f1=0.77, seizure_frequency_f1=0.672, seizure_frequency_precision=0.687, seizure_frequency_recall=0.658, unknown_f1=0.235.
- Evidence validity: 0 call failures, 0 parse failures; 179/179 evidence-valid rendered mentions. Residual ledger is analysis-only over the same JSONL.
- Claim language: Revise-only. v0.2 improves precision versus v0.1 but loses enough recall that F1 is slightly worse (0.672 vs 0.674). Unknown-state recall collapses; next loop should add a separate unknown/change-state recovery lane rather than tighten generic rejection further.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v02_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v02_dev140_gpt41mini_20260618.md`, `experiments/exectv2_sf_state_adjudicator_v02_residual_ledger_dev140_20260618.json`, `experiments/exectv2_sf_state_adjudicator_v02_residual_ledger_dev140_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_state_adjudicator_v02_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_sf_state_adjudicator_v01_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.1 pilot over the v0.5 single structured key-entity draft. Deterministic code proposes exact candidate evidence spans and hints; the model owns keep/reject, state choice, text normalization, and final mentions.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic candidate spans are attention scaffolding, not predictions`.
- Primary metrics: candidate_spans=79, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.1, seizure_frequency_f1=0.921, seizure_frequency_precision=0.906, seizure_frequency_recall=0.935.
- Evidence validity: 0 call failures, 0 parse failures; 32/32 evidence-valid rendered mentions.
- Supersedes: `exectv2_llm_sf_verifier_v04_dev140_gpt41mini_20260618`.
- Claim language: Pilot-only escalation signal. Candidate-span/state adjudication cleared dev25 strongly (0.921 F1) with clean gates, justifying the dev140 architecture probe. This is not a transfer or promotion claim.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v01_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v01_dev25_gpt41mini_20260618.md`.

### `exectv2_hybrid_sf_state_adjudicator_v01_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_sf_state_adjudicator`; mode `live`; replay `native_run_split`.
- Model role: SeizureFrequency candidate-span state adjudicator v0.1 over the v0.5 single structured key-entity draft. Deterministic code proposes exact candidate evidence spans and hints; the model owns keep/reject, state choice, text normalization, and final mentions. Post-processing only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic candidate spans are attention scaffolding, not predictions`.
- Primary metrics: active_rate_f1=0.726, candidate_spans=412, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_sf_state_adjudicator_v0.1, seizure_free_f1=0.734, seizure_frequency_f1=0.674, seizure_frequency_precision=0.653, seizure_frequency_recall=0.695, unknown_f1=0.351.
- Evidence validity: 0 call failures, 0 parse failures; 199/199 evidence-valid rendered mentions. Residual ledger is analysis-only over the same JSONL.
- Supersedes: `exectv2_llm_sf_verifier_v04_dev140_gpt41mini_20260618`.
- Claim language: Revise-only architecture evidence. Candidate-span/state adjudication improves over SF verifier v0.4 (0.623 -> 0.674) and keeps gates clean, but remains below the 0.8 target. Residuals show generic seizure active-rate over-emission and generic unknown/seizure-free misses; next loop should tighten generic candidate keep/reject rather than discard the architecture.
- Artifacts: `experiments/exectv2_hybrid_sf_state_adjudicator_v01_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_sf_state_adjudicator_v01_dev140_gpt41mini_20260618.md`, `experiments/exectv2_sf_state_adjudicator_v01_residual_ledger_dev140_20260618.json`, `experiments/exectv2_sf_state_adjudicator_v01_residual_ledger_dev140_20260618.md`, `docs/experiments/exectv2/seizure_frequency/exectv2_sf_state_adjudicator_v01_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_diagnosis_reconciler_v02_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_diagnosis_reconciler`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis reconciler v0.2 pilot over Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 candidates. v0.2 adds explicit candidate concept groups before final mention rendering.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; verifier/decomposer inputs and concept groups are candidate scaffolding`.
- Primary metrics: diagnosis_f1=0.844, diagnosis_precision=0.821, diagnosis_recall=0.868, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_diagnosis_reconciler_v0.2, source_near_overlap_f1=0.86.
- Evidence validity: 0 call failures, 0 parse failures; 65/65 evidence-valid rendered mentions.
- Cache/reuse source: Uses saved Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 dev140 artifacts as candidate inputs, restricted to the first 25 dev letters for this pilot.
- Supersedes: `exectv2_hybrid_diagnosis_reconciler_v01_dev25_gpt41mini_20260618`.
- Claim language: Pilot-only escalation signal. Concept grouping improved dev25 slightly over v0.1 (0.844 vs 0.833), but required dev140 transfer evidence before any candidate claim.
- Artifacts: `experiments/exectv2_hybrid_diagnosis_reconciler_v02_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_diagnosis_reconciler_v02_dev25_gpt41mini_20260618.md`.

### `exectv2_hybrid_diagnosis_reconciler_v01_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_diagnosis_reconciler`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis reconciler v0.1 pilot over Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 candidates. The model owns final keep/reject, concept specificity, certainty, and evidence selection.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; verifier/decomposer inputs are candidate scaffolding`.
- Primary metrics: diagnosis_f1=0.833, diagnosis_precision=0.818, diagnosis_recall=0.849, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_diagnosis_reconciler_v0.1.
- Evidence validity: 0 call failures, 0 parse failures; 64/64 evidence-valid rendered mentions.
- Cache/reuse source: Uses saved Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 dev140 artifacts as candidate inputs, restricted to the first 25 dev letters for this pilot.
- Supersedes: `exectv2_hybrid_diagnosis_decomposer_v01_dev25_gpt41mini_20260618`.
- Claim language: Pilot-only escalation signal. Strong dev25 balance (0.833 F1) justified the dev140 run but does not transfer by itself.
- Artifacts: `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev25_gpt41mini_20260618.md`.

### `exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_diagnosis_reconciler`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis reconciler v0.1 over Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 candidates. The model owns final keep/reject, concept specificity, certainty, and evidence selection; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; verifier/decomposer inputs are candidate scaffolding`.
- Primary metrics: diagnosis_f1=0.658, diagnosis_precision=0.658, diagnosis_recall=0.658, evidence_validity_rate=0.9954, parse_failures=0, prompt_version=exectv2_hybrid_diagnosis_reconciler_v0.1, source_near_overlap_f1=0.787.
- Evidence validity: 0 call failures, 0 parse failures; 436/438 evidence-valid rendered mentions. Residual ledger is analysis-only over the same JSONL.
- Cache/reuse source: Uses saved Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 dev140 artifacts as candidate inputs.
- Supersedes: `exectv2_llm_diagnosis_verifier_v06_dev140_gpt41mini_20260618`.
- Claim language: Revise-only. Best Diagnosis dev140 score so far, but only a small gain over verifier v0.6 (0.658 vs 0.651) and still far below the 0.8 target. Residuals show generic epilepsy and tonic-clonic over-emission plus focal epilepsy/secondary-generalised misses.
- Artifacts: `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.md`, `experiments/exectv2_diagnosis_reconciler_v01_residual_ledger_dev140_20260618.json`, `experiments/exectv2_diagnosis_reconciler_v01_residual_ledger_dev140_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_reconciler_v01_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_diagnosis_decomposer_v01_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_diagnosis_decomposer`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis heading/narrative decomposer v0.1 pilot over the v0.5 single structured key-entity draft. Deterministic code proposes heading and narrative candidate spans; the model owns final Diagnosis mentions.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic diagnosis spans are checklist scaffolding, not predictions`.
- Primary metrics: diagnosis_f1=0.814, diagnosis_precision=0.767, diagnosis_recall=0.868, diagnosis_spans=120, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_diagnosis_decomposer_v0.1.
- Evidence validity: 0 call failures, 0 parse failures; 69/69 evidence-valid rendered mentions.
- Supersedes: `exectv2_llm_diagnosis_verifier_v06_dev140_gpt41mini_20260618`.
- Claim language: Pilot-only escalation signal. Diagnosis heading/narrative decomposition cleared dev25 (0.814 F1) with clean gates, justifying the dev140 architecture probe. This is not a transfer or promotion claim.
- Artifacts: `experiments/exectv2_hybrid_diagnosis_decomposer_v01_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_diagnosis_decomposer_v01_dev25_gpt41mini_20260618.md`.

### `exectv2_diag_sf_verifier_v06_v04_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_diag_sf_verifier_residual_iteration`; mode `live`; replay `native_run_split`.
- Model role: Residual-led Diagnosis verifier v0.6 and SeizureFrequency verifier v0.4 over the v0.5 single structured key-entity draft. The model owns revised family mentions; deterministic code only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection`.
- Primary metrics: diagnosis_evidence_validity_rate=0.9906, diagnosis_f1=0.651, diagnosis_precision=0.706, diagnosis_recall=0.604, parse_failures=0, sf_evidence_validity_rate=0.9905, sf_f1=0.623, sf_precision=0.591, sf_recall=0.658.
- Evidence validity: Diagnosis 0 call failures, 0 parse failures, 317/320 evidence-valid rendered mentions. SeizureFrequency 0 call failures, 0 parse failures, 208/210 evidence-valid rendered mentions.
- Supersedes: `exectv2_key_entities_dev140_transfer_readout_20260618`.
- Claim language: Revise-only dev140 improvement. Diagnosis improves 0.616 -> 0.651 and SeizureFrequency improves 0.602 -> 0.623, but both remain below the 0.8 target. Next iteration should use stronger task decomposition, not more broad prompt accretion.
- Artifacts: `experiments/exectv2_llm_diagnosis_verifier_v06_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_diagnosis_verifier_v06_dev140_gpt41mini_20260618.md`, `experiments/exectv2_llm_sf_verifier_v04_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_llm_sf_verifier_v04_dev140_gpt41mini_20260618.md`, `docs/experiments/exectv2/key_entities/exectv2_diag_sf_verifier_v06_v04_dev140_report_2026-06-18.md`.

### `gan2026_cluster_axis_gate_v1_tightened_2026-06-16`
- Date/split: `2026-06-16`; `validation+test`; `1200` rows.
- Pipeline: `cluster_axis_gate_no_call_replay`; mode `analysis/no-call`; replay `saved_output_replay`.
- Model role: No-call post-hoc replay over v0.4 fresh-evidence outputs. No model calls made. Test450 rows read only after gate cleared precision check and gap_robust on validation750.; model `none`.
- Repair mode/config: `cluster_axis_retention_gate_v1`.
- Primary metrics: gap_robust=True, genuine_rate_regressions=0, test_baseline_purist=379, test_correct_to_wrong=0, test_delta_vs_379_baseline=0, test_gated_purist=379, test_net_purist=0, test_total_rows=450, test_touched=0, test_wrong_to_correct=0, validation_baseline_purist=682, validation_correct_to_wrong=0, validation_gated_purist=683, validation_net_purist=1, validation_total_rows=750, validation_touched=1, validation_wrong_to_correct=1.
- Evidence validity: Validation-only replay for gate development (step 1-2). Test450 applied only after validation gate cleared: zero genuine-rate regressions + gap_robust. Test450 result reported verbatim, no tuning on test.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl.
- Claim language: C6 cluster-axis RETENTION gate: fires only on plain-rate v0.4 predictions where the note has explicit recurring-cluster language AND the rewrite changes the Purist bucket. Zero unknown-coercion; additive cluster-axis only. Genuine-rate regression count must be 0 to clear precision gate.
- Artifacts: `experiments/gan2026_cluster_axis_gate_v1_tightened_2026-06-16.json`, `experiments/gan2026_cluster_axis_gate_v1_tightened_2026-06-16.md`.

### `gan2026_cluster_axis_gate_v1_2026-06-16`
- Date/split: `2026-06-16`; `validation`; `750` rows.
- Pipeline: `cluster_axis_gate_no_call_replay`; mode `analysis/no-call`; replay `saved_output_replay`.
- Model role: No-call post-hoc replay over v0.4 fresh-evidence outputs. No model calls made. Test450 rows read only after gate cleared precision check and gap_robust on validation750.; model `none`.
- Repair mode/config: `cluster_axis_retention_gate_v1`.
- Primary metrics: gap_robust=False, genuine_rate_regressions=6, validation_baseline_purist=682, validation_correct_to_wrong=6, validation_gated_purist=677, validation_net_purist=-5, validation_total_rows=750, validation_touched=7, validation_wrong_to_correct=1.
- Evidence validity: Validation-only replay for gate development (step 1-2). Test450 applied only after validation gate cleared: zero genuine-rate regressions + gap_robust. Test450 result reported verbatim, no tuning on test.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl.
- Claim language: C6 cluster-axis RETENTION gate: fires only on plain-rate v0.4 predictions where the note has explicit recurring-cluster language AND the rewrite changes the Purist bucket. Zero unknown-coercion; additive cluster-axis only. Genuine-rate regression count must be 0 to clear precision gate.
- Artifacts: `experiments/gan2026_cluster_axis_gate_v1_2026-06-16.json`, `experiments/gan2026_cluster_axis_gate_v1_2026-06-16.md`.

### `gan2026_unknown_frequency_ambiguity_panel_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `6` rows.
- Pipeline: `fresh_evidence_reasoner_ambiguity_panel`; mode `analysis-only`; replay `analysis_only`.
- Model role: Supervisor-seeded unknown-frequency ambiguity component contract; parser and safety-gate replay only.; model `none`.
- Repair mode/config: `optional model-owned ambiguity_classification field before fresh-evidence final-label rendering`.
- Primary metrics: panel_failed=0, panel_passed=6, panel_rows=6, prompt_version=gan2026_fresh_evidence_reasoner_v0_6, safety_gate_version=gan2026_fresh_evidence_safety_gate_v0_9.
- Evidence validity: Synthetic validation-only policy panel derived from supervisor clarification. No model calls, no scorer changes, and no locked test row inspection.
- Supersedes: `gan2026_fresh_evidence_reasoner_unknown_policy_v0_6_safety_v0_9_replay_2026-06-15`.
- Claim language: Adds a hard-negative ambiguity-classification contract for unknown-frequency cases. This is prerequisite validation infrastructure, not a promoted test450 candidate.
- Artifacts: `experiments/gan2026_unknown_frequency_ambiguity_panel_2026-06-15.json`, `experiments/gan2026_unknown_frequency_ambiguity_panel_2026-06-15.md`.

### `gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `50` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Stage C component-contribution test: rebuilds the resolve_label graph query deterministically from the validation50 v3 claim-table and feeds it as a fourth component to the frozen v0.9 selector replay. No model calls and no holdout rows are read.; model `none`.
- Repair mode/config: `state_graph_resolve_label_component_contribution_v1`.
- Primary metrics: graph_component_purist_correct=30, graph_mints_correct_for_no_correct=0, no_correct_pool_rows=0, p1_unilateral_correct_to_wrong=20, p2_corroborated_correct_to_wrong=0, p2_corroborated_net_purist_gain=0, p3_unknown_only_correct_to_wrong=5, rows=50, v09_selected_purist_correct=50.
- Evidence validity: Validation-only saved-output replay over the first-50 validation rows. Gold-free graph rebuild (raw_frequency normalized, no diary/window arithmetic); gold labels used only for post-hoc Purist scoring. No holdout rows are read and no model calls are made. The pool already covers all 50 rows, so Arm 1 has no no-correct targets in this slice.
- Cache/reuse source: claim_table:gan2026_section_claim_table_validation50_gpt41mini_v3_2026-06-01.jsonl;selector:gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl.
- Claim language: Stage C gate for the graph-as-component generator. Not a holdout-facing candidate. Finds the graph component regression-safe only under independent-corroboration gating (P2), neutral on the solved first-50 slice; an unconditional graph component regresses (P1/P3). The no-correct-residual uplift is untested here because the residual is not in this slice.
- Artifacts: `experiments/gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15.json`, `experiments/gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15.md`, `experiments/gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15_graphs.jsonl`, `experiments/gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15_rows.jsonl`.

### `gan2026_state_graph_ontology_stage_b_viability_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `25` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `analysis-only`; replay `analysis_only`.
- Model role: Stage B gold-free viability gate replaying saved LLM atomic-claim graphs through the ontology dual-validation + resolve_label query; no model calls and no holdout rows are read.; model `none`.
- Repair mode/config: `state_graph_ontology_dual_validation_resolve_label_v1`.
- Primary metrics: admitted=79, exact_evidence=79, over_inference_rejected=0, rows_component_localized=25, structural_rejected=1, structural_valid=79, total_nodes=80.
- Evidence validity: Validation-only viability gate over a saved atomic-claim artifact. Gold-free: no gold labels, no holdout rows, and no model calls. The C2 over-inference guard fired 0 times because the v3 atomic-claim builder mints no quantifying states; the gate's structural and interpretability sub-gates pass.
- Cache/reuse source: artifact:gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.jsonl.
- Claim language: Stage B viability gate for the ontology + typed-edge atomic-claim component generator. Not a holdout-facing candidate. The guard's rejection mechanism is unexercised on this artifact; informs whether and how the ladder proceeds to Stage C.
- Artifacts: `experiments/gan2026_state_graph_ontology_stage_b_viability_2026-06-15.json`, `experiments/gan2026_state_graph_ontology_stage_b_viability_2026-06-15.md`.

### `gan2026_state_graph_ontology_stage_b_rebuild_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `25` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `analysis-only`; replay `analysis_only`.
- Model role: Stage B (rebuilt) viability gate: re-converts the v3 claim-table with deterministic raw_frequency normalization, then runs the ontology dual-validation + resolve_label query. No model calls and no holdout rows are read.; model `none`.
- Repair mode/config: `state_graph_ontology_dual_validation_resolve_label_v1`.
- Primary metrics: admitted=79, exact_evidence=80, over_inference_rejected=1, rows_component_localized=25, structural_rejected=0, structural_valid=80, total_nodes=80.
- Evidence validity: Validation-only viability gate over rebuilt atomic-claim graphs. Gold-free: no gold labels, no holdout rows, and no model calls. raw_frequency is normalized with the project scorer-facing grammar (no diary/window arithmetic). The C2 over-inference guard fired 1 time(s) on uncurated quantifying mints out of unknown-only evidence shapes.
- Cache/reuse source: claim_table:gan2026_section_claim_table_validation25_gpt41mini_v3_2026-06-01.jsonl.
- Claim language: Stage B (rebuilt) gate for the ontology + typed-edge atomic-claim component generator. Not a holdout-facing candidate. The guard is now exercised; informs whether the ladder proceeds to Stage C.
- Artifacts: `experiments/gan2026_state_graph_ontology_stage_b_rebuild_2026-06-15.json`, `experiments/gan2026_state_graph_ontology_stage_b_rebuild_2026-06-15.md`, `experiments/gan2026_state_graph_ontology_stage_b_rebuild_2026-06-15_graphs.jsonl`.

### `gan2026_state_graph_ontology_oracle_uplift_stage_a_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `analysis-only`; replay `analysis_only`.
- Model role: Stage A no-spend oracle-uplift gate over the deterministic state graph; no model calls and no holdout rows are read.; model `none`.
- Repair mode/config: `state_graph_ontology_dual_validation_resolve_label_v1`.
- Primary metrics: admitted_representable=599, baseline_representable=599, projection_correct=641, resolve_correct=641, resolve_minus_projection=0.
- Evidence validity: Validation-only oracle-uplift gate. Gold labels are used only for post-hoc Purist correctness and band breakdown; no holdout rows are read and no model is called.
- Cache/reuse source: split:gan2026_split_v1.
- Claim language: Stage A viability gate for the ontology + typed-edge component generator. Not a holdout-facing candidate; informs whether the validation-only ladder proceeds to Stage B.
- Artifacts: `experiments/gan2026_state_graph_ontology_oracle_uplift_stage_a_2026-06-15.json`, `experiments/gan2026_state_graph_ontology_oracle_uplift_stage_a_2026-06-15.md`.

### `gan2026_source_near_contrast_panel_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `6` rows.
- Pipeline: `fresh_evidence_reasoner_source_near_contrast_panel`; mode `analysis-only`; replay `analysis_only`.
- Model role: Paired source-near hard-negative ambiguity contract; parser and safety-gate replay only, no model calls.; model `none`.
- Repair mode/config: `optional model-owned ambiguity_classification field before fresh-evidence final-label rendering`.
- Primary metrics: cases=6, failed=0, pairs_both_directions_pass=3, passed=6, prompt_version=gan2026_fresh_evidence_reasoner_v0_6, safety_gate_version=gan2026_fresh_evidence_safety_gate_v0_9.
- Evidence validity: Synthetic validation-only contrast panel derived from the supervisor distinctions. No model calls, no scorer changes, no locked test row inspection. Static passing is necessary but not sufficient for the live run.
- Claim language: Adds paired source-near hard negatives stressing the ambiguous-vs-determinate distinction. Prerequisite validation infrastructure for the live ambiguity run, not a promoted test450 candidate.
- Artifacts: `experiments/gan2026_source_near_contrast_panel_2026-06-15.json`, `experiments/gan2026_source_near_contrast_panel_2026-06-15.md`.

### `gan2026_robustness_battery_v1_gpt41mini_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `27` rows.
- Pipeline: `robustness_battery_generalization_adversary`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler scored live on authored-fresh OOD / adversarial cases for synthetic-artifact overfit and transfer.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `robustness_battery_v1`.
- Primary metrics: panel_A_both_correct_pairs=2, panel_A_overfit_only_pairs=3, panel_A_pairs=6, panel_A_pass=False, panel_B_cases=7, panel_B_correct=5, panel_B_pass=False, panel_C_cases=8, panel_C_correct=7, panel_C_fraction=0.875, panel_C_pass=True, verdict=overfit, weakest_axis=cluster_axis_retention.
- Evidence validity: Authored-fresh OOD/adversarial cases (NOT Gan rows, NOT test450 holdout). Gold Purist computed from authored labels via the project normalizer + labels.map_purist. Live gpt-4.1-mini, temperature 0. Transfer/overfit estimate, not a holdout benchmark.
- Cache/reuse source: experiments\gan2026_robustness_battery_v1_checkpoints.
- Claim language: Fitness tier 2 robustness gate. 'transfers' is necessary (not sufficient) for Freeze Warden test450 authorisation; any failed bar returns the candidate as revise.
- Artifacts: `experiments/gan2026_robustness_battery_v1_gpt41mini_2026-06-15.json`, `experiments/gan2026_robustness_battery_v1_gpt41mini_2026-06-15.md`, `experiments/gan2026_robustness_battery_v1_cases.json`.

### `gan2026_robustness_battery_v1_evidence_v0_6_gpt41mini_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `27` rows.
- Pipeline: `robustness_battery_generalization_adversary`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler (prompt v0.6 triage-scaffold evidence presentation) scored live on authored-fresh OOD / adversarial cases for synthetic-artifact overfit and transfer.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `robustness_battery_v1`.
- Primary metrics: panel_A_both_correct_pairs=3, panel_A_overfit_only_pairs=2, panel_A_pairs=6, panel_A_pass=False, panel_B_cases=7, panel_B_correct=5, panel_B_pass=False, panel_C_cases=8, panel_C_correct=8, panel_C_fraction=1.0, panel_C_pass=True, verdict=overfit, weakest_axis=cluster_axis_retention.
- Evidence validity: Authored-fresh OOD/adversarial cases (NOT Gan rows, NOT test450 holdout). Gold Purist computed from authored labels via the project normalizer + labels.map_purist. Live gpt-4.1-mini, temperature 0. Transfer/overfit estimate, not a holdout benchmark.
- Cache/reuse source: experiments\gan2026_robustness_battery_v1_evidence_v0_6_checkpoints.
- Claim language: Fitness tier 2 robustness gate. 'transfers' is necessary (not sufficient) for Freeze Warden test450 authorisation; any failed bar returns the candidate as revise.
- Artifacts: `experiments/gan2026_robustness_battery_v1_evidence_v0_6_gpt41mini_2026-06-15.json`, `experiments/gan2026_robustness_battery_v1_evidence_v0_6_gpt41mini_2026-06-15.md`, `experiments/gan2026_robustness_battery_v1_cases.json`.

### `gan2026_residual_component_diversity_audit_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `17` rows.
- Pipeline: `consensus_fresh_agreement_selector_component_diversity`; mode `analysis-only`; replay `analysis_only`.
- Model role: Deterministic re-analysis of saved v0.9 residual component labels; normalizes each component to its Purist bucket to measure correlated versus independent failure.; model `none`.
- Repair mode/config: `none`.
- Primary metrics: correlated_failure_fraction=0.6364, no_correct_correlated_one_bucket=7, no_correct_rows=11, no_correct_split_across_buckets=4.
- Evidence validity: Validation-only re-analysis of saved component labels. No model calls, no scorer changes, no locked test rows read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.json.
- Claim language: Quantifies whether the no-correct residual is correlated (single-bucket) or independent (split) failure. Diagnostic instrumentation for the component-generation bet, not a holdout-facing candidate.
- Artifacts: `experiments/gan2026_residual_component_diversity_audit_2026-06-15.json`, `experiments/gan2026_residual_component_diversity_audit_2026-06-15.md`.

### `gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `llm_only_direct_labeler`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler prompt v0.7 (label binding) live on validation750; v0.5 re-parsed baseline; held-out-family CV.; model `openai/gpt-4.1-mini`.
- Registry roles: `negative_attribution`.
- Repair mode/config: `v0_7_label_binding`.
- Primary metrics: aggregate_net_purist_gain=-106, correct_to_wrong_vs_v05=149, gap_robust=False, net_purist_vs_v05=-106, v05_baseline_purist=575, v07_purist=469, wrong_to_correct_vs_v05=43.
- Evidence validity: validation750 development split (gan2026_split_v1), NOT a holdout or test450 result. Live gpt-4.1-mini, temperature 0. Family CV is within-validation leave-one-boundary-band-out; gap_robust is a promotion-stability estimate, not a test450 number.
- Cache/reuse source: experiments\gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15.jsonl.
- Claim language: Cycle-3 validation750 + family-CV gate for v0.7 label binding. gap_robust + positive net is necessary, NOT sufficient, for test450 authorisation. Not a holdout result.
- Artifacts: `experiments/gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15.json`, `experiments/gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15.md`, `experiments/gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15.jsonl`.

### `gan2026_fresh_evidence_reasoner_unknown_policy_v0_6_safety_v0_9_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `250` rows.
- Pipeline: `fresh_evidence_reasoner`; mode `no-call-replay`; replay `saved_output_replay`.
- Model role: V12 fresh-evidence reasoner replay testing safety-gate v0.9 over saved validation raw outputs; no new prediction-bearing model calls.; model `none; no-call replay over saved openai/gpt-4.1 v0.6 raw outputs`.
- Repair mode/config: `safety gate v0.9: unknown-boundary safeguards, vague-multiple exactification and same-day cluster downgrade fallbacks, plus scorer-neutral no-reference-to-unknown semantic repair when seizure evidence exists but count/window is unclear`.
- Primary metrics: trigger_full_correct_to_wrong=0, trigger_full_final_purist_correct=109, trigger_full_rows=123, trigger_full_semantic_no_reference_to_unknown_repairs=4, trigger_full_v0_purist_correct=105, trigger_full_wrong_to_correct=4, v0_4_validation250_comparator_correct=242, validation250_correct_to_wrong=0, validation250_final_purist_correct=240, validation250_semantic_no_reference_to_unknown_repairs=5, validation250_v0_purist_correct=236, validation250_wrong_to_correct=4.
- Evidence validity: No-call replay preserves 239/250 exact evidence substrings on validation250 and 115/123 on the trigger panel; no call failures or parse/schema/label failures; semantic no-reference-to-unknown repairs are scorer-neutral.
- Cache/reuse source: Raw outputs from gan2026_fresh_evidence_reasoner_validation250_live_gpt41_v0_6_safety_v0_7_2026-06-15 and trigger_full v0.6/safety-v0.7 artifacts.
- Claim language: Validation diagnostic only. Safety v0.9 preserves the v0.8 Purist counts, repairs no-reference fallbacks to unknown on 5 validation250 rows and 4 trigger-panel rows, and still trails the v0.4 validation250 comparator (240/250 vs 242/250), so it is not a promoted holdout candidate and does not authorize a test450 run.
- Artifacts: ``, `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_nocall_replay_v0_6_safety_v0_9_2026-06-15.jsonl`, `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_nocall_replay_v0_6_safety_v0_9_2026-06-15.md`, `experiments/gan2026_fresh_evidence_reasoner_validation250_nocall_replay_v0_6_safety_v0_9_2026-06-15.jsonl`, `experiments/gan2026_fresh_evidence_reasoner_validation250_nocall_replay_v0_6_safety_v0_9_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_validation750_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Hybrid saved-output selector: deterministic baseline is the floor; exact consensus switch is accepted only when V12 independently emits the same final label.; model `panel: deterministic_rules_tool + exact structured-event consensus + V12 fresh-evidence reasoner`.
- Primary metrics: changed_label_precision=0.2385, changed_labels=109, correct_to_wrong=11, deterministic_purist_correct=697, fresh_evidence_v12_purist_correct=682, net_purist_gain_vs_deterministic=15, selected_purist_correct=712, validation750_rows=750, wrong_to_correct=26.
- Evidence validity: No new model evidence. Reuses saved deterministic, consensus, and V12 validation artifacts; scoring and boundary-band summaries are post-hoc validation instrumentation only.
- Cache/reuse source: Saved validation artifacts: deterministic gpt41mini 2026-06-07, exact consensus 2026-06-13, and V12 fresh_evidence_reasoner v0.4 2026-06-13.
- Claim language: Validation-only no-call selector replay. It improves aggregate validation750 to 712/750 by accepting exact consensus switches only when V12 fresh-evidence independently agrees, but changed-label precision remains low outside band_daily; revise, do not freeze or request holdout.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: No-call replay of selector v0.9 over saved v0.8 validation selector rows reconstructed into component rows.; model `none`.
- Registry roles: `component_ladder`.
- Repair mode/config: `selector_v0_9_semantic_equiv_unknown_uncertainty`.
- Primary metrics: changed_label_precision=0.7347, changed_labels=49, consensus_purist_correct=708, correct_to_wrong=0, deterministic_purist_correct=697, fresh_evidence_purist_correct=682, selected_purist_correct=733, wrong_to_correct=36.
- Evidence validity: Saved-output validation replay; gold labels are used only for post-hoc scoring. No holdout rows are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15`.
- Claim language: v0.9 improves saved validation through two narrow residual selector gates. Still validation-only and not holdout authorization.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15`
- Date/split: `2026-06-15`; `synthetic_semantic_equiv_unknown_probe`; `7` rows.
- Pipeline: `consensus_fresh_agreement_selector_synthetic_v09_stress`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthetic probe over hand-specified v0.9 stress cases; no model calls and no Gan rows are read.; model `none`.
- Repair mode/config: `selector_v0_9_semantic_equiv_unknown_uncertainty`.
- Primary metrics: changed_label_precision=1.0, conservative_false_negative_count=1, correct_to_wrong=0, current_rule_false_positive_count=0, desired_action_matches=7, selected_purist_correct=6, wrong_to_correct=2.
- Evidence validity: Synthetic mechanism evidence only; no validation or holdout records are read.
- Cache/reuse source: Synthetic hand-specified component outputs only.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_8_parseable_refinement_synthetic_stress_2026-06-15`.
- Claim language: v0.9 passes source-near hard negatives for two narrow residual selector gates, but does not authorize a frozen holdout audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector_residual_audit`; mode `analysis-only`; replay `analysis_only`.
- Model role: Validation-only residual analysis over saved v0.9 selector rows; no model calls and no holdout rows are read.; model `none`.
- Repair mode/config: `selector_v0_9_residual_component_generation_audit`.
- Primary metrics: correct_component_available=6, no_correct_component=11, residual_component_generation_required=11, residual_selector_only_headroom=6, selected_correct=733, selected_wrong=17, selector_only_oracle_correct=739.
- Evidence validity: Validation-only saved-output audit. Gold labels are used only for post-hoc component availability and residual taxonomy; no holdout rows are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15`.
- Claim language: Identifies component-generation bottlenecks in the v0.9 validation residual, especially unknown-frequency over-inference. Not a holdout-facing candidate.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: No-call replay of selector v0.8 over saved v0.7 validation selector rows reconstructed into component rows.; model `none`.
- Repair mode/config: `selector_v0_8_parseable_denominator_window_refinement`.
- Primary metrics: changed_label_precision=0.7234, changed_labels=47, consensus_purist_correct=708, correct_to_wrong=0, deterministic_purist_correct=697, fresh_evidence_purist_correct=682, selected_purist_correct=731, wrong_to_correct=34.
- Evidence validity: Saved-output validation replay; gold labels are used only for post-hoc scoring. No holdout rows are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15`.
- Claim language: v0.8 improves saved validation through a narrow parseable denominator/window refinement gate. Still validation-only and not holdout authorization.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_8_parseable_refinement_synthetic_stress_2026-06-15`
- Date/split: `2026-06-15`; `synthetic_parseable_refinement_probe`; `11` rows.
- Pipeline: `consensus_fresh_agreement_selector_synthetic_refinement_stress`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthetic probe over hand-specified parseable refinement stress cases; no model calls and no Gan rows are read.; model `none`.
- Repair mode/config: `selector_v0_8_parseable_denominator_window_refinement`.
- Primary metrics: changed_label_precision=1.0, conservative_false_negative_count=1, correct_to_wrong=0, current_rule_false_positive_count=0, desired_action_matches=11, selected_purist_correct=8, wrong_to_correct=3.
- Evidence validity: Synthetic mechanism evidence only; no validation or holdout records are read.
- Cache/reuse source: Synthetic hand-specified component outputs only.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_7_unknown_count_window_synthetic_stress_2026-06-15`.
- Claim language: v0.8 passes source-near parseable-refinement hard negatives, but does not authorize a frozen holdout audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_parseable_refinement_synthetic_stress_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_parseable_refinement_synthetic_stress_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: No-call replay of selector v0.7 over saved v0.6 validation selector rows reconstructed into component rows.; model `none`.
- Repair mode/config: `selector_v0_7_unknown_count_window_rescue`.
- Primary metrics: changed_label_precision=0.775, changed_labels=40, consensus_purist_correct=708, correct_to_wrong=0, deterministic_purist_correct=697, fresh_evidence_purist_correct=682, selected_purist_correct=728, wrong_to_correct=31.
- Evidence validity: Saved-output validation replay; gold labels are used only for post-hoc scoring. No holdout rows are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15`.
- Claim language: v0.7 preserves the v0.6 validation score and adds a guarded unknown-origin count-window mechanism. Still validation-only and not holdout authorization.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_7_unknown_count_window_synthetic_stress_2026-06-15`
- Date/split: `2026-06-15`; `synthetic_unknown_count_window_probe`; `12` rows.
- Pipeline: `consensus_fresh_agreement_selector_synthetic_boundary_stress`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthetic probe over hand-specified unknown count-window stress cases; no model calls and no Gan rows are read.; model `none`.
- Repair mode/config: `selector_v0_7_unknown_count_window_rescue`.
- Primary metrics: changed_label_precision=1.0, conservative_false_negative_count=2, correct_to_wrong=0, current_rule_false_positive_count=0, desired_action_matches=12, selected_purist_correct=10, wrong_to_correct=5.
- Evidence validity: Synthetic mechanism evidence only; no validation or holdout records are read.
- Cache/reuse source: Synthetic hand-specified component outputs only.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_6_boundary_rescue_synthetic_stress_2026-06-15`.
- Claim language: v0.7 passes a source-near unknown count-window synthetic mechanism probe, but it does not improve saved validation and does not authorize a frozen holdout audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_unknown_count_window_synthetic_stress_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_unknown_count_window_synthetic_stress_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_7_residual_headroom_audit_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector_residual_audit`; mode `analysis-only`; replay `analysis_only`.
- Model role: Validation-only residual analysis over saved v0.7 selector rows; no model calls and no holdout rows are read.; model `none`.
- Repair mode/config: `selector_v0_7_residual_headroom_audit`.
- Primary metrics: oracle_correct_available=11, oracle_correct_unavailable=11, parseable_other_candidate_actions=27, parseable_other_correct_to_wrong=5, parseable_other_net_purist_gain=-1, parseable_other_wrong_to_correct=4, selected_correct=728, selected_wrong=22.
- Evidence validity: Validation-only saved-output audit. Gold labels are used only for post-hoc scoring and transition accounting; no holdout rows are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15`.
- Claim language: Identifies residual selector headroom and rejects broad parseable-other relaxation as validation-negative. Not a holdout-facing candidate.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_residual_headroom_audit_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_residual_headroom_audit_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: No-call replay of selector v0.6 over saved v0.5 validation selector rows reconstructed into component rows.; model `none`.
- Repair mode/config: `selector_v0_6_profile_guard_boundary_rescue`.
- Primary metrics: changed_label_precision=0.775, changed_labels=40, consensus_purist_correct=708, correct_to_wrong=0, deterministic_purist_correct=697, fresh_evidence_purist_correct=682, selected_purist_correct=728, wrong_to_correct=31.
- Evidence validity: Saved-output validation replay; gold labels are used only for post-hoc scoring. No holdout rows are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15`.
- Claim language: v0.6 preserves the v0.5 validation score while adding a profile guard motivated by a synthetic hard-negative panel. Still validation-only and not holdout authorization.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_6_boundary_rescue_synthetic_stress_2026-06-15`
- Date/split: `2026-06-15`; `synthetic_boundary_rescue_probe`; `12` rows.
- Pipeline: `consensus_fresh_agreement_selector_synthetic_boundary_stress`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthetic replay over hand-specified v0.5 boundary-rescue stress cases; no model calls and no Gan rows are read.; model `none`.
- Repair mode/config: `selector_v0_6_profile_guard_boundary_rescue`.
- Primary metrics: changed_label_precision=1.0, conservative_false_negative_count=1, correct_to_wrong=0, current_rule_false_positive_count=0, desired_future_action_matches=11, selected_purist_correct=11, wrong_to_correct=5.
- Evidence validity: Synthetic mechanism evidence only; no validation or holdout records are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15.json.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15`.
- Claim language: v0.6 blocks v0.5's synthetic hard-negative false positives and keeps intended positives. This supports revision but does not authorize a frozen holdout audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_boundary_rescue_synthetic_stress_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_boundary_rescue_synthetic_stress_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Hybrid saved-output selector: v0.4 consensus+fresh agreement plus narrow V12 fresh boundary rescue for deterministic seizure-free/no-reference overreach.; model `panel: deterministic_rules_tool + exact structured-event consensus + V12 fresh-evidence reasoner`.
- Repair mode/config: `fresh_boundary_rescue_v0_5 over saved deterministic/consensus/V12 labels`.
- Primary metrics: changed_label_precision=0.775, changed_labels=40, consensus_purist_correct=708, correct_to_wrong=0, deterministic_purist_correct=697, fresh_boundary_rescue_actions=14, fresh_evidence_v12_purist_correct=682, net_purist_gain_vs_deterministic=31, selected_purist_correct=728, validation750_rows=750, wrong_to_correct=31.
- Evidence validity: No new model evidence. Reuses saved deterministic, consensus, and V12 validation artifacts; gold labels are used only for post-hoc scoring and band summaries.
- Cache/reuse source: Saved validation artifacts: deterministic gpt41mini 2026-06-07, exact consensus 2026-06-13, and V12 fresh_evidence_reasoner v0.4 2026-06-13.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_4_validation750_replay_2026-06-15`.
- Claim language: Validation-only no-call selector replay. v0.5 improves the saved validation aggregate by rescuing deterministic seizure-free/no-reference boundary overreach with V12 fresh evidence, but it remains mined on validation and needs targeted robustness evidence before any holdout-facing protocol.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15`
- Date/split: `2026-06-15`; `synthetic_boundary_rescue_probe`; `12` rows.
- Pipeline: `consensus_fresh_agreement_selector_synthetic_boundary_stress`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthetic boundary-rescue probe over hand-specified deterministic, consensus, and V12 fresh-evidence labels; no model calls and no Gan rows are read.; model `none`.
- Repair mode/config: `selector_v0_5_fresh_boundary_rescue`.
- Primary metrics: consensus_purist_correct=6, conservative_false_negative_count=1, current_rule_false_positive_count=3, desired_future_action_matches=8, deterministic_purist_correct=6, expected_v05_action_matches=12, fresh_purist_correct=6, rows=12, safety_success_count=3, selected_purist_correct=8.
- Evidence validity: Synthetic mechanism evidence only: source-near note fragments and hand-specified labels are scored through the current Gan Purist mapping; no validation or holdout records are read.
- Cache/reuse source: Synthetic hand-specified component outputs only.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15`.
- Claim language: Predeclared synthetic component-stress probe for selector v0.5. Supports deterministic seizure-free/no-reference overreach rescue as a direction, but exposes hard-negative false positives from the label-only rescue rule. Does not authorize a frozen holdout audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector_boundary_rescue_audit`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only hard-slice audit of v0.5 fresh-boundary-rescue actions over saved validation selector rows.; model `none; analysis-only replay over saved v0.5 selector rows`.
- Repair mode/config: `fresh_boundary_rescue_v0_5_audit`.
- Primary metrics: fresh_boundary_rescue_actions=14, fresh_boundary_rescue_correct_to_wrong=0, fresh_boundary_rescue_wrong_to_correct=14, v05_changed_label_precision=0.775, v05_changed_labels=40, v05_correct_to_wrong=0, v05_selected_purist_correct=728, v05_wrong_to_correct=31.
- Evidence validity: No new prediction evidence. Uses saved validation v0.5 selector rows; gold labels are used only after reproducible action membership for scoring.
- Cache/reuse source: experiments\gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15`.
- Claim language: Validation-only audit. v0.5 fresh-boundary-rescue actions are 14/14 wrong-to-correct on saved validation, but this remains validation-mined evidence requiring robustness before holdout.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_4_validation750_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Hybrid saved-output selector: deterministic baseline is the floor; v0.4 accepts exact consensus plus V12 agreement after unknown/ambiguous safeguards and cluster-cadence preservation.; model `panel: deterministic_rules_tool + exact structured-event consensus + V12 fresh-evidence reasoner`.
- Repair mode/config: `cluster_cadence_precision_v0_4`.
- Primary metrics: band_weekly_changed_label_precision=0.4, band_weekly_correct_to_wrong=0, band_weekly_net_gain=4, changed_label_precision=0.6538, changed_labels=26, consensus_purist_correct=708, correct_to_wrong=0, deterministic_purist_correct=697, fresh_evidence_v12_purist_correct=682, net_purist_gain_vs_deterministic=17, selected_purist_correct=714, validation750_rows=750, wrong_to_correct=17.
- Evidence validity: No new model evidence. Reuses saved deterministic, consensus, and V12 validation artifacts; scoring and boundary-band summaries are post-hoc validation instrumentation only.
- Cache/reuse source: Saved validation artifacts: deterministic gpt41mini 2026-06-07, exact consensus 2026-06-13, and V12 fresh_evidence_reasoner v0.4 2026-06-13.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_3_validation750_replay_2026-06-15`.
- Claim language: Validation-only no-call selector replay. v0.4 improves the selector-family front-runner to 714/750, removes all correct-to-wrong regressions in changed labels, and raises changed-label precision to 0.6538. Still revise-only: it needs predeclared hard-slice/robustness evidence and a frozen protocol before any holdout-facing claim.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_4_unknown_origin_relaxation_probe_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector_unknown_origin_relaxation_probe`; mode `analysis-only`; replay `analysis_only`.
- Model role: Validation-only counterfactual probe of a label-only unknown-origin relaxation for selector v0.4; no model calls.; model `none; analysis-only replay over saved selector rows`.
- Repair mode/config: `counterfactual_unknown_origin_relaxation_over_v0_4_selector_rows`.
- Primary metrics: counterfactual_correct_to_correct=2, counterfactual_correct_to_wrong=2, counterfactual_wrong_to_correct=0, counterfactual_wrong_to_wrong=0, net_if_accept_all_unknown_origin=-2, source_rows=750, unknown_origin_blocked_switches=4.
- Evidence validity: No new prediction evidence. Uses saved validation selector rows; gold labels score only a counterfactual action policy.
- Cache/reuse source: experiments/gan2026_consensus_fresh_agreement_selector_v0_4_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_4_synthetic_component_stress_2026-06-15`.
- Claim language: Validation-only counterfactual showing that a label-only relaxation out of deterministic unknown origins would be net negative; keep v0.4 until an evidence-based explicit count-window feature is tested.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_unknown_origin_relaxation_probe_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_unknown_origin_relaxation_probe_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_4_synthetic_component_stress_2026-06-15`
- Date/split: `2026-06-15`; `synthetic_validation_probe`; `20` rows.
- Pipeline: `consensus_fresh_agreement_selector_synthetic_component_stress`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthetic component-stress probe over hand-specified deterministic, consensus, and V12 fresh-evidence labels; no model calls and no Gan rows are read.; model `none`.
- Repair mode/config: `selector_v0_4_cluster_cadence_precision`.
- Primary metrics: consensus_purist_correct=11, desired_future_action_matches=18, deterministic_purist_correct=13, expected_v04_action_matches=20, false_negative_count=2, fresh_purist_correct=12, rows=20, safety_success_count=9, selected_purist_correct=18.
- Evidence validity: Synthetic mechanism evidence only: source-near note fragments and hand-specified labels are scored through the current Gan Purist mapping; no validation or holdout records are read.
- Cache/reuse source: Synthetic hand-specified component outputs only.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15`.
- Claim language: Predeclared synthetic component-stress probe for selector v0.4. Supports the cluster-cadence and unknown-boundary mechanics, exposes the conservative unknown-origin false-negative cost, and does not authorize a frozen holdout audit.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_synthetic_component_stress_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_synthetic_component_stress_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector_hard_slice_audit`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only hard-slice audit of v0.4 selector actions over saved deterministic, consensus, and V12 validation artifacts.; model `none; analysis-only replay over saved selector rows`.
- Repair mode/config: `cluster_cadence_precision_v0_4_hard_slice_audit`.
- Primary metrics: suppressed_cluster_cadence_changes=1, suppressed_cluster_demotions=1, suppressed_v3_to_v4=2, suppressed_v3_to_v4_correct_to_wrong=2, v04_block_count_with_regression=0, v04_changed_label_precision=0.6538, v04_changed_labels=26, v04_correct_to_wrong=0, v04_selected_purist_correct=714, v04_wrong_to_correct=17.
- Evidence validity: No new prediction evidence. Uses saved validation selector rows; gold labels are used only after reproducible slice membership for scoring.
- Cache/reuse source: Saved v0.1-v0.4 consensus_fresh_agreement_selector validation750 replay artifacts from 2026-06-15.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_4_validation750_replay_2026-06-15`.
- Claim language: Validation-only hard-slice audit. Supports v0.4 cluster-cadence gate: the two v0.3 switches suppressed by v0.4 were both correct-to-wrong regressions, while v0.4 keeps all 17 wrong-to-correct changes. Still revise-only; next evidence should be predeclared synthetic/robustness panel before any holdout-facing claim.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_3_validation750_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Hybrid saved-output selector: deterministic baseline is the floor; v0.3 accepts exact consensus plus V12 agreement only when the deterministic origin is not unknown/no-reference and the agreed replacement is a specific non-ambiguous label.; model `panel: deterministic_rules_tool + exact structured-event consensus + V12 fresh-evidence reasoner`.
- Repair mode/config: `specific_label_precision_v0_3`.
- Primary metrics: band_unknown_net_gain=5, band_weekly_changed_label_precision=0.3333, changed_label_precision=0.6071, changed_labels=28, consensus_purist_correct=708, correct_to_wrong=2, deterministic_purist_correct=697, fresh_evidence_v12_purist_correct=682, net_purist_gain_vs_deterministic=15, selected_purist_correct=712, validation750_rows=750, wrong_to_correct=17.
- Evidence validity: No new model evidence. Reuses saved deterministic, consensus, and V12 validation artifacts; scoring and boundary-band summaries are post-hoc validation instrumentation only.
- Cache/reuse source: Saved validation artifacts: deterministic gpt41mini 2026-06-07, exact consensus 2026-06-13, and V12 fresh_evidence_reasoner v0.4 2026-06-13.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_2_validation750_replay_2026-06-15`.
- Claim language: Validation-only no-call selector replay. v0.3 restores the v0.1 aggregate 712/750 while reducing changed labels to 28 and raising changed-label precision to 0.6071, but weekly-band precision remains weak; revise, do not freeze or request holdout.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_3_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_3_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_2_validation750_replay_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Hybrid saved-output selector: deterministic baseline is the floor; v0.2 accepts exact consensus plus V12 agreement only for non-boundary precision cases.; model `panel: deterministic_rules_tool + exact structured-event consensus + V12 fresh-evidence reasoner`.
- Repair mode/config: `nonboundary_precision_v0_2`.
- Primary metrics: changed_label_precision=0.3621, changed_labels=58, correct_to_wrong=8, deterministic_purist_correct=697, fresh_evidence_v12_purist_correct=682, net_purist_gain_vs_deterministic=13, selected_purist_correct=710, validation750_rows=750, wrong_to_correct=21.
- Evidence validity: No new model evidence. Reuses saved deterministic, consensus, and V12 validation artifacts; scoring and boundary-band summaries are post-hoc validation instrumentation only.
- Cache/reuse source: Saved validation artifacts: deterministic gpt41mini 2026-06-07, exact consensus 2026-06-13, and V12 fresh_evidence_reasoner v0.4 2026-06-13.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_validation750_replay_2026-06-15`.
- Claim language: Validation-only no-call selector replay. v0.2 suppresses no-reference-origin switches and unknown/seizure-free consensus replacements, improving changed-label precision from v0.1 0.2385 to 0.3621 while retaining 710/750 Purist. Still revise-only: submonthly/monthly/weekly changed-label precision remains below the promotion bar.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_2_validation750_no_call_replay_2026-06-15.jsonl`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_2_validation750_no_call_replay_2026-06-15.md`.

### `gan2026_ambiguity_slice_semantic_scorer_v0_7_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `22` rows.
- Pipeline: `fresh_evidence_reasoner_ambiguity_semantic_scorer`; mode `analysis-only`; replay `analysis_only`.
- Model role: Deterministic semantic / over-specificity overlay on the saved live ambiguity slice; scores clinical decision kind alongside Purist and flags re-bucketing and class/label incoherence.; model `none`.
- Repair mode/config: `none`.
- Primary metrics: class_label_incoherent_count=3, over_specific_rebucket_count=0, purist_correct=8, purist_minus_semantic=0, rows=22, semantic_correct=8.
- Evidence validity: Validation-only diagnostic overlay on saved live outputs. No model calls, no scorer policy change, no locked test rows read. The frozen Purist scorer is unchanged; this is an additional view used to keep the live run honest about re-bucketing.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_7_safety_v0_9_2026-06-15.jsonl.
- Claim language: Adds a semantic / over-specificity view so the live ambiguity run cannot be credited for Purist re-bucketing. Diagnostic instrumentation, not a holdout-facing candidate or a scorer replacement.
- Artifacts: `experiments/gan2026_ambiguity_slice_semantic_scorer_v0_7_2026-06-15.json`, `experiments/gan2026_ambiguity_slice_semantic_scorer_v0_7_2026-06-15.md`, `experiments/gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_7_safety_v0_9_2026-06-15.jsonl`.

### `gan2026_ambiguity_slice_semantic_scorer_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `22` rows.
- Pipeline: `fresh_evidence_reasoner_ambiguity_semantic_scorer`; mode `analysis-only`; replay `analysis_only`.
- Model role: Deterministic semantic / over-specificity overlay on the saved live ambiguity slice; scores clinical decision kind alongside Purist and flags re-bucketing and class/label incoherence.; model `none`.
- Repair mode/config: `none`.
- Primary metrics: class_label_incoherent_count=2, over_specific_rebucket_count=0, purist_correct=12, purist_minus_semantic=0, rows=22, semantic_correct=12.
- Evidence validity: Validation-only diagnostic overlay on saved live outputs. No model calls, no scorer policy change, no locked test rows read. The frozen Purist scorer is unchanged; this is an additional view used to keep the live run honest about re-bucketing.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl.
- Claim language: Adds a semantic / over-specificity view so the live ambiguity run cannot be credited for Purist re-bucketing. Diagnostic instrumentation, not a holdout-facing candidate or a scorer replacement.
- Artifacts: `experiments/gan2026_ambiguity_slice_semantic_scorer_2026-06-15.json`, `experiments/gan2026_ambiguity_slice_semantic_scorer_2026-06-15.md`, `experiments/gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl`.

### `gan2026_ambiguity_live_component_generation_audit_v0_7_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `22` rows.
- Pipeline: `fresh_evidence_reasoner_ambiguity_component_generation`; mode `live`; replay `live`.
- Model role: Live v0.7 + safety-v0.9 ambiguity-aware fresh-evidence generation over a predeclared 22-row validation hard slice. Scored against gold for component availability; no holdout rows are read.; model `openai/gpt-4.1`.
- Repair mode/config: `ambiguity_classification_component_generation`.
- Primary metrics: new_oracle_ceiling=739, no_correct_rows=11, no_correct_rows_fixed_by_live_fresh=1, oracle_ceiling_delta=0, prior_oracle_ceiling=739, recoverable_rows_fresh_preserved=5, supervisor_panel_pass=2.
- Evidence validity: Validation-only live generation. Gold labels are used post-hoc for component availability and the supervisor panel; no locked test rows are read and no scorer policy changes.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_7_safety_v0_9_2026-06-15.jsonl.
- Supersedes: `gan2026_ambiguity_live_component_generation_audit_2026-06-15`.
- Claim language: Measures whether the ambiguity contract lifts the component oracle ceiling on the predeclared residual slice. Not a holdout-facing candidate; a wider validation replay and held-out-family CV are required before any freeze.
- Artifacts: `experiments/gan2026_ambiguity_live_component_generation_audit_v0_7_2026-06-15.json`, `experiments/gan2026_ambiguity_live_component_generation_audit_v0_7_2026-06-15.md`, `experiments/gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_7_safety_v0_9_2026-06-15.jsonl`.

### `gan2026_ambiguity_live_component_generation_audit_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `22` rows.
- Pipeline: `fresh_evidence_reasoner_ambiguity_component_generation`; mode `live`; replay `live`.
- Model role: Live v0.6 + safety-v0.9 ambiguity-aware fresh-evidence generation over a predeclared 22-row validation hard slice. Scored against gold for component availability; no holdout rows are read.; model `openai/gpt-4.1`.
- Repair mode/config: `ambiguity_classification_component_generation`.
- Primary metrics: new_oracle_ceiling=741, no_correct_rows=11, no_correct_rows_fixed_by_live_fresh=3, oracle_ceiling_delta=2, prior_oracle_ceiling=739, recoverable_rows_fresh_preserved=5, supervisor_panel_pass=5.
- Evidence validity: Validation-only live generation. Gold labels are used post-hoc for component availability and the supervisor panel; no locked test rows are read and no scorer policy changes.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15`.
- Claim language: Measures whether the ambiguity contract lifts the component oracle ceiling on the predeclared residual slice. Not a holdout-facing candidate; a wider validation replay and held-out-family CV are required before any freeze.
- Artifacts: `experiments/gan2026_ambiguity_live_component_generation_audit_2026-06-15.json`, `experiments/gan2026_ambiguity_live_component_generation_audit_2026-06-15.md`, `experiments/gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl`.

### `gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14`
- Date/split: `2026-06-14`; `validation+test_aggregate`; `1200` rows.
- Pipeline: `gan2026_agentic_fresh_evidence_synthesis`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis of hybrid structured events, agentic/consensus variants, and V12 fresh-evidence reasoning after the frozen aggregate-only V12 test450 audit.; model `none`.
- Primary metrics: agentic_major_variant_families_summarized=14, best_completed_test450_pragmatic_correct=394, best_completed_test450_purist_correct=379, consensus_test450_purist_correct=365, consensus_validation750_purist_correct=708, hybrid_structured_events_test450_pragmatic_correct=381, hybrid_structured_events_test450_purist_correct=364, hybrid_structured_events_validation750_purist_correct=661, hybrid_structured_events_validation750_rendered_rows=748, row_level_holdout_inspection=no, v12_target_reached=false, v12_target_test450_purist_correct=383, v12_test450_pragmatic_correct=394, v12_test450_purist_correct=379, v12_validation750_pragmatic_correct=698, v12_validation750_purist_correct=682.
- Evidence validity: No new prediction evidence. Uses validation-development metrics and aggregate-only locked-test metrics; V12 test row-level failures, rationales, evidence, selected events, and transitions were not inspected.
- Cache/reuse source: Existing Gan 2026 registry, RUN_INDEX, project status, validation reports, and aggregate-only locked-test reports; no new model calls and no row-level test artifact inspection.
- Claim language: Post-audit analysis-only synthesis. Summarizes why hybrid structured events remain the durable substrate, why agentic/consensus variants mostly failed or failed to transfer, and why V12 fresh_evidence_reasoner is the best completed holdout result but still missed the 383/450 Purist target. Does not authorize a new test run or any test-row tuning.
- Artifacts: ``.

### `gan2026_llm_reasoning_agentic_test085_experiment_plan_2026-06-13`
- Date/split: `2026-06-13`; `validation_planned_then_frozen_test`; `0` rows.
- Pipeline: `agentic_llm_reasoning_plan`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only experiment plan for LLM-owned structured-event reasoning, tool-calling agents, and matched-budget multi-agent variants.; model `none`.
- Primary metrics: current_best_test450_structured_events_purist_correct=364, first_gate=validation25_contract_then_fixed_hard50_and_family_hard_slices, required_test450_gain_over_best_structured_events=19, second_gate=validation250, target_test450_purist_correct=383.
- Evidence validity: Plan artifact only. No new model calls, no scorer changes, no test-row inspection.
- Claim language: Next-cycle plan after deterministic-floor consensus failed to generalize. Requires LLM-owned selection over structured events, validation hard-slice and validation250 gates, and a frozen aggregate test audit only after explicit authorization.
- Artifacts: ``.

### `gan2026_llm_event_reasoner_validation25_live_gpt41mini_v1_3_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `25` rows.
- Pipeline: `llm_event_reasoner`; mode `live`; replay `live`.
- Model role: V1 single LLM-owned event reasoner over saved GPT structured-event V0; deterministic code limited to prompt assembly, format-only label repair, evidence validation, and scoring.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `format-only label repair plus enum/shape schema repair; no semantic fallback`.
- Primary metrics: call_failures=0, evidence_exact_substrings=24, final_purist_correct=25, format_only_purist_correct=25, model_calls_attempted=25, net_purist_gain_vs_v0=0, parse_or_validation_failures=0, raw_model_purist_correct=25, rows=25, v0_purist_correct=25.
- Evidence validity: 24/25 final decisions cited exact evidence substrings; one case retained a correct label with non-exact evidence casing/context.
- Cache/reuse source: Structured-event source: experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl.
- Supersedes: `gan2026_llm_event_reasoner_validation25_live_gpt41mini_v1_2_2026-06-13`.
- Claim language: Validation-development contract smoke only. v1.3 clears schema/evidence smoke and authorizes fixed hard50, but does not by itself authorize family slices, validation250, holdout use, or benchmark claims.
- Artifacts: `experiments/gan2026_llm_event_reasoner_validation25_live_gpt41mini_v1_3_2026-06-13.jsonl`, `experiments/gan2026_llm_event_reasoner_validation25_live_gpt41mini_v1_3_2026-06-13.md`.

### `gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13`
- Date/split: `2026-06-13`; `test`; `450` rows.
- Pipeline: `agentic_structured_event_consensus`; mode `no_call_replay`; replay `saved_output_replay`.
- Model role: deterministic tool floor plus available structured-event agent exact-label unanimity selector; model `panel: deterministic_rules_tool + gpt-4.1-mini + qwen3.6:35b; DeepSeek test450 artifact unavailable`.
- Repair mode/config: `available_two_agent_exact_label_unanimity_over_test450_structured_events`.
- Primary metrics: changed_label_precision=0.39473684210526316, constrained_consensus_pragmatic_correct=375, constrained_consensus_purist_correct=365, correct_to_wrong=23, deterministic_floor_pragmatic_correct=354, deterministic_floor_purist_correct=343, exact_three_agent_test450_available=no, net_purist_gain=22, switched_labels=114, validation_three_agent_consensus_purist_correct=708, wrong_to_correct=45.
- Evidence validity: Final holdout aggregate saved-output replay. Exact validation policy cannot be fully replayed because no DeepSeek test450 structured-event artifact is available on disk; no test-row failure inspection or tuning.
- Claim language: Constrained two-agent holdout audit improves the weak deterministic test floor but drops far below validation consensus rate; reject robust-final-claim interpretation and start any follow-up from validation only.
- Artifacts: `experiments/gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13.jsonl`, `experiments/gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13.md`, `experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_qwen3635b_2026-06-13.jsonl`.

### `gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: Local Qwen LLM structured-events extractor and selector using SE v0.6; deterministic code limited to Gan normalization, evidence validation, and scoring/repair after structured model selection.; model `ollama_chat/qwen3.6:35b`.
- Registry roles: `model_family_variant`.
- Repair mode/config: `hybrid_full_stack`.
- Primary metrics: call_failures=0, evidence_valid_rows=581, json_dialect_repairs=746, parse_or_validation_failures=4, pragmatic_accuracy=0.8747, pragmatic_correct=656, prompt_version=gan2026_hybrid_structured_events_v0.6, purist_accuracy=0.8507, purist_correct=638, rendered_rows=746, structured_records=746.
- Evidence validity: 581/750 rows carry an evidence_valid substring-presence trace; 0 call failures; 4 unrendered rows in the combined summary. Qwen still relies heavily on JSON dialect repair.
- Cache/reuse source: Resumed from completed validation250 prefix artifact experiments/gan2026_v06_validation250_hybrid_structured_events_qwen3635b_2026-06-11.jsonl; --resume-existing skipped 250 completed rows and ran the remaining 500 validation rows live through local Ollama.
- Supersedes: `gan2026_v06_validation250_hybrid_structured_events_qwen3635b_2026-06-11`.
- Claim language: User-approved close-off confirmation for SE v0.6 on the full validation750 surface. Validation development evidence only, not a holdout or benchmark claim. Qwen SE v0.6 improves over the Phase 1 validation750 SE result, with 638/746 Purist rendered-correct versus the earlier 624/746 and 656/746 Pragmatic rendered-correct. Curated 2026-06-26 as a best SE v0.6 model-family validation variant; kept unsurfaced so Phase 1 canonical rows are not silently replaced.
- Artifacts: `experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl`, `experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.md`.

### `gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: LLM structured-events extractor and selector using SE v0.6; deterministic code limited to Gan normalization, evidence validation, and scoring/repair after structured model selection.; model `deepseek/deepseek-chat`.
- Registry roles: `model_family_variant`.
- Repair mode/config: `hybrid_full_stack`.
- Primary metrics: call_failures=0, evidence_valid_rows=719, parse_or_validation_failures=5, pragmatic_accuracy=0.8613, pragmatic_correct=646, prompt_version=gan2026_hybrid_structured_events_v0.6, purist_accuracy=0.8293, purist_correct=622, rendered_rows=745, structured_records=745.
- Evidence validity: 719/750 rows carry an evidence_valid substring-presence trace; 0 call failures; 5 unrendered rows in the combined summary.
- Cache/reuse source: Resumed from completed validation250 prefix artifact experiments/gan2026_v06_validation250_hybrid_structured_events_deepseek_2026-06-10.jsonl; --resume-existing skipped 250 completed rows and ran the remaining 500 validation rows live.
- Supersedes: `gan2026_v06_validation250_hybrid_structured_events_deepseek_2026-06-10`.
- Claim language: User-approved close-off confirmation for SE v0.6 on the full validation750 surface. Validation development evidence only, not a holdout or benchmark claim. Compared to the earlier DeepSeek SE Phase 1 validation750 result, v0.6 improves Purist from 609/742 rendered to 622/745 rendered and Pragmatic from 634/742 to 646/745. Curated 2026-06-26 as a best SE v0.6 model-family validation variant; kept unsurfaced so Phase 1 canonical rows are not silently replaced.
- Artifacts: `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.jsonl`, `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.md`.

### `gan2026_agentic_pipeline_phase_plan_2026-06-12`
- Date/split: `2026-06-12`; `none`; `0` rows.
- Pipeline: `gan2026_agentic_pipeline_plan`; mode `analysis-only`; replay `analysis_only`.
- Model role: Research and implementation plan defining the final Gan 2026 agentic phases: matched-budget self-consistency, tool-using single-agent pipelines, and matched-budget multi-agent comparison.; model `none`.
- Primary metrics: holdout_authorized=no, planned_phase_5=agent definition and matched-budget protocol, planned_phase_6=tool-using single-agent versus matched-budget multi-agent evaluation.
- Evidence validity: No data run. The plan requires future tool traces to report evidence validity with architecture-specific definitions and explicit attribution.
- Claim language: Planning artifact only. Does not authorize new holdout use, test-row inspection, or benchmark-facing claims. Establishes that multi-agent claims must be compared against single-agent self-consistency under matched model-call, token, tool-call, and aggregation budgets.
- Artifacts: ``.

### `gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `25` rows.
- Pipeline: `agentic_matched_budget`; mode `live`; replay `native_run_split`.
- Model role: Gan Phase 6 validation25 post-voting live single-agent comparison restricted to single_greedy, single_self_consistency_temperature, and single_agent_tools; cross-model and multi-agent conditions intentionally skipped until the single-agent comparator is stable.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair + deterministic normalized-label vote`.
- Primary metrics: call_failures=0, condition_disagreement_rows=5, conditions=3, decision_records=150, holdout_authorized=no, model_calls_attempted=150, normalized_label_vote_repairs=70, parse_or_validation_failures=0, pragmatic_correct_call_level=150, prediction_bearing_rows=25, purist_correct_call_level=150, row187_status=scoring_equivalent_disagreement, row_final_pragmatic_correct=25, row_final_purist_correct=25, rows=25, single_agent_tools_purist_correct=25, single_greedy_purist_correct=25, single_self_consistency_temperature_purist_correct=25, tool_smoke_calls=52.
- Evidence validity: Prediction-bearing validation development smoke: 150/150 decision records, 0 call failures, 0 blocking parse/validation failures, 52 parser/guide tool smoke calls, 70 normalized-label vote repairs, and no holdout use.
- Supersedes: `gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12`.
- Claim language: Validation development result only, not a benchmark claim. Deterministic normalized-label voting stabilizes all three active single-agent condition finals at 25/25 Purist/Pragmatic with no call or blocking parse failures. Five condition-label disagreements remain scoring-equivalent; row 187 remains 1 per 7 to 9 day versus 2 per month. This clears the planned single-agent comparator gate before spending matched multi_agent_matched calls.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.md`.

### `gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `25` rows.
- Pipeline: `agentic_matched_budget`; mode `live`; replay `native_run_split`.
- Model role: Gan Phase 6 validation25 live single-agent comparison restricted to single_greedy, single_self_consistency_temperature, and single_agent_tools; cross-model and multi-agent conditions intentionally skipped until the single-agent comparator is understood.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair only`.
- Primary metrics: call_failures=0, condition_disagreement_rows=3, conditions=3, decision_records=150, holdout_authorized=no, model_calls_attempted=150, parse_or_validation_failures=0, pragmatic_correct_call_level=147, prediction_bearing_rows=25, purist_correct_call_level=147, row_final_pragmatic_correct=24, row_final_purist_correct=24, rows=25, single_agent_tools_purist_correct=24, single_greedy_purist_correct=24, single_self_consistency_temperature_purist_correct=25, tool_smoke_calls=52.
- Evidence validity: Prediction-bearing validation development smoke: 150/150 decision records, 0 call failures, 0 blocking parse/validation failures, 52 parser/guide tool smoke calls, and no holdout use. Format repairs were common and should be treated as direct-label parser/schema repair, not semantic promotion.
- Supersedes: `gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12`.
- Claim language: Validation development result only, not a benchmark claim. The condition filter prevented multi_agent_matched and single_self_consistency_cross_model calls; single_self_consistency_temperature was 25/25 Purist-correct at condition-final level, while single_greedy and single_agent_tools were each 24/25. Next work should inspect/repair label-format normalization and disagreement rows before spending matched multi-agent calls.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12.md`.

### `gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `25` rows.
- Pipeline: `agentic_matched_budget`; mode `prompt-only`; replay `native_run_split`.
- Model role: Gan Phase 6 prompt-only/no-call matched-budget runner surface covering single_greedy, single_self_consistency_temperature, single_self_consistency_cross_model, single_agent_tools, and multi_agent_matched conditions.; model `openai/gpt-4.1-mini`.
- Primary metrics: conditions=5, holdout_authorized=no, prediction_bearing_rows=0, rows=25, tool_smoke_calls=104.
- Evidence validity: No prediction-bearing evidence metric. Tool contract smoke emitted parser/guide traces only: 104 tool smoke calls and 0 prediction-bearing rows.
- Claim language: Phase 6 runner-surface contract artifact only. Validation25 prompt-only run made no model calls and produces no accuracy claim. It verifies shared CLI wiring, matched budget trace shape, parser-as-tool output, boundary-guide retrieval, and no-prediction attribution before live agentic comparisons.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12.md`.

### `gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `1` rows.
- Pipeline: `agentic_matched_budget`; mode `live`; replay `native_run_split`.
- Model role: Gan Phase 6 live matched-budget smoke over all five initial conditions: single_greedy, single_self_consistency_temperature, single_self_consistency_cross_model, single_agent_tools, and multi_agent_matched.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair only`.
- Primary metrics: call_failures=0, conditions=5, decision_records=14, holdout_authorized=no, model_calls_attempted=14, parse_or_validation_failures=0, pragmatic_correct_call_level=11, prediction_bearing_rows=1, purist_correct_call_level=11, rows=1.
- Evidence validity: First live transport smoke only; 14 model calls attempted, 14 decision records, 0 call failures, 0 parse/validation failures, and tool traces preserved for tool-using conditions.
- Supersedes: `gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12`.
- Claim language: Validation development live smoke only, not an accuracy comparison or benchmark claim. Confirms that the agentic matched-budget runner can make live calls, parse prediction-bearing labels, score call-level outputs, and preserve tool/no-tool trace attribution. Validation25 live comparison remains the next scale-up before any multi-agent value claim.
- Artifacts: `experiments/gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12.jsonl`, `experiments/gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12.md`.

### `gan2026_agentic_hard50_tool_context_ablation_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_tool_context_ablation`; mode `live`; replay `live`.
- Model role: E1 one-call direct-label context ablation over fixed validation hard50: no tool context, parser only, boundary guide only, and parser plus boundary guide.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair + deterministic normalized-label vote`.
- Primary metrics: call_failures=0, decision_records=200, direct_boundary_guide_only_purist_correct=34, direct_no_tool_context_purist_correct=30, direct_parser_only_purist_correct=21, direct_parser_plus_boundary_guide_purist_correct=19, holdout_authorized=no, model_calls_attempted=200, non_harmful_contexts=['direct_boundary_guide_only'], parse_or_validation_failures=0, rows=50.
- Evidence validity: Prediction-bearing validation hard50 development run: 200/200 decision records, 0 call failures, 0 parse/schema/label failures. Evidence substring metric not computed for this ablation artifact.
- Claim language: Validation-development hard-slice result only. Parser context was harmful, while boundary-guide-only was non-harmful and improved to 34/50 Purist; E2 therefore used boundary guides only and excluded parser candidates.
- Artifacts: `experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.jsonl`, `experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.md`.

### `gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_redesign_protocol`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only validation-cycle redesign after E2 hard50 stop; reframes follow-up work as rescue-only boundary auditing with parser context excluded.; model `none`.
- Primary metrics: e1_boundary_guide_only_purist_correct=34, e1_parser_only_purist_correct=21, e2_losses_vs_reference=2, e2_purist_correct=34, e2_wins_vs_reference=4, holdout_authorized=no, rows=50.
- Evidence validity: No new prediction evidence. Consolidates E5/E1/E2 validation hard50 artifacts and predeclares D0-D4 surfaces, gates, and attribution requirements.
- Supersedes: `gan2026_agentic_hard50_tool_self_consistency_2026-06-12`.
- Claim language: Validation-development design artifact only. It supersedes only unrun E3/E4 live designs from the prior hard50 plan and does not authorize holdout use, scorer changes, or validation250/full-validation escalation without a D-series hard50 gate.
- Artifacts: `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`.

### `gan2026_three_way_comparison_validation750_deterministic_phase2_gan_shorthand_generalized_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator -- rules-only candidate extraction, normalization, and projection; no model calls. Phase 2 iteration 1: GAN_SHORTHAND group de-overfitted (word-number patterns removed, separator-prefix patterns removed).; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=683, purist_correct_of_rendered=674, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace (this architecture's reported evidence-trace metric); formal CandidateSet source-id validity is not computed for single-shot architectures.
- Claim language: Phase 2 de-overfitting iteration 1 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): GAN_SHORTHAND rules rewritten to generalized clinical shorthand patterns -- digit-only counts, no special separator prefixes (asterisk/X/times), portability promoted from GAN2026_SPECIFIC to SEIZURE_FREQUENCY or CLINICAL_EPILEPSY. Expected and intentional regression of 14 rows (688 -> 674 purist-correct) -- these rows depended on benchmark-specific notation not present in real clinical documentation. Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_phase2_gan_shorthand_generalized_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_validation750_deterministic_phase2_cluster_diary_digit_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator -- rules-only candidate extraction, normalization, and projection; no model calls. Phase 2 iteration 2: CLUSTER_ARITHMETIC (cluster.compact_count_per_period) and DIARY_LOG_AGGREGATION (diary.seizure_days_fraction) de-overfitted to digit-only compact shorthand.; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=681, purist_correct_of_rendered=673, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace.
- Claim language: Phase 2 de-overfitting iteration 2 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): CLUSTER_ARITHMETIC and DIARY_LOG_AGGREGATION rules generalized -- cluster.compact_count_per_period and diary.seizure_days_fraction now require digit-only counts in compact shorthand notation (word numbers in compact notation are GAN-dataset-specific). Word numbers in running prose (PORTABLE_RATE_EXPRESSIONS family) assessed and confirmed NOT GAN-specific; no change to that family. Expected and intentional regression of 1 row (674 -> 673 purist-correct) relative to iteration 1: row 148 (Seizure days: six/30 this month) depended on GAN-specific compact notation. Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_phase2_cluster_diary_digit_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_gan_shorthand_generalized_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator routed through the staged canonical-pipeline architecture -- rules-only; no model calls. Phase 2 iteration 1: GAN_SHORTHAND group de-overfitted (word-number patterns removed, separator-prefix patterns removed).; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=683, purist_correct_of_rendered=674, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace; identical to the deterministic architecture's numbers on this split -- the staged canonical-pipeline wrapper converges on the same rendered answers as the unstaged baseline (confirmed in Phase 1 and still holds in Phase 2).
- Claim language: Phase 2 de-overfitting iteration 1 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): same GAN_SHORTHAND rule rewrite as the deterministic counterpart, routed through the staged canonical-pipeline architecture. Produces identical purist/pragmatic/distribution numbers as the unstaged deterministic architecture (staged wrapper converges on the same rendered answers). Expected and intentional regression of 14 rows (688 -> 674 purist-correct). Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_gan_shorthand_generalized_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_cluster_diary_digit_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator routed through the staged canonical-pipeline architecture -- rules-only candidate extraction, normalization, and projection; no model calls. Phase 2 iteration 2: CLUSTER_ARITHMETIC (cluster.compact_count_per_period) and DIARY_LOG_AGGREGATION (diary.seizure_days_fraction) de-overfitted to digit-only compact shorthand.; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=681, purist_correct_of_rendered=673, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace.
- Claim language: Phase 2 de-overfitting iteration 2 data point (validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4): same CLUSTER_ARITHMETIC and DIARY_LOG_AGGREGATION rule generalization as the deterministic counterpart; routed through the staged canonical-pipeline architecture -- cluster.compact_count_per_period and diary.seizure_days_fraction now require digit-only counts in compact shorthand notation (word numbers in compact notation are GAN-dataset-specific). Word numbers in running prose (PORTABLE_RATE_EXPRESSIONS family) assessed and confirmed NOT GAN-specific; no change to that family. Expected and intentional regression of 1 row (674 -> 673 purist-correct) relative to iteration 1: row 148 (Seizure days: six/30 this month) depended on GAN-specific compact notation. Not a standalone promote/reject verdict -- see gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09 for cross-architecture synthesis.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_phase2_cluster_diary_digit_2026-06-09.jsonl`.

### `gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase2_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads Phase 2 deterministic/deterministic_canonical_pipeline artifacts and Phase 1 LLM-architecture artifacts; assembles a shared comparison table plus a hybrid-only routing-taxonomy appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=674, deterministic_purist_correct_of_rendered=674, hybrid_purist_correct_of_rendered=500, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=581, llm_only_direct_labeler_purist_correct_of_rendered=564, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (free-text substring presence), llm_only_canonical_pipeline reports the deliberately distinct evidence_text_contained, and hybrid reports a formal CandidateSet source-id validity rate. The report footnotes and per-architecture metric table make this explicit.
- Claim language: Phase 2 de-overfitting iteration 1 comparison report synthesis (validation750 only; gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4). No test450 read, no holdout-facing or benchmark-comparable claim. Compares six PipelineArchitecture configs; deterministic and deterministic_canonical_pipeline are from Phase 2 runs (GAN_SHORTHAND de-overfitted); hybrid, llm_only_direct_labeler, hybrid_structured_events, llm_only_canonical_pipeline are from the Phase 1 gpt-4.1-mini pass (unchanged). Key finding: expected and intentional 14-row regression on deterministic architectures (674 vs 688 purist-correct); validates that the removed rules were GAN-dataset-specific and not genuinely generalizable clinical patterns.
- Artifacts: `experiments/gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase2_report_gan_shorthand_generalized_validation750_2026-06-09.md`.

### `gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase2_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads Phase 2 iteration 2 deterministic/deterministic_canonical_pipeline artifacts and Phase 1 LLM-architecture artifacts; assembles a shared comparison table plus a hybrid-only routing-taxonomy appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=673, deterministic_purist_correct_of_rendered=673, hybrid_purist_correct_of_rendered=500, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=581, llm_only_direct_labeler_purist_correct_of_rendered=564, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (free-text substring presence), llm_only_canonical_pipeline reports the deliberately distinct evidence_text_contained, and hybrid reports a formal CandidateSet source-id validity rate.
- Claim language: Phase 2 de-overfitting iteration 2 comparison report synthesis (validation750 only; gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 4). No test450 read, no holdout-facing or benchmark-comparable claim. Compares six PipelineArchitecture configs; deterministic and deterministic_canonical_pipeline are from Phase 2 iteration 2 runs (GAN_SHORTHAND + CLUSTER_ARITHMETIC + DIARY_LOG_AGGREGATION de-overfitted); hybrid, llm_only_direct_labeler, hybrid_structured_events, llm_only_canonical_pipeline are from the Phase 1 gpt-4.1-mini pass (unchanged). Key finding: expected and intentional total regression of 15 rows across both de-overfitting iterations (688 -> 673 purist-correct); validates that the removed rules depended on GAN-dataset-specific notation.
- Artifacts: `experiments/gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09.md`.

### `gan2026_three_way_comparison_validation750_llm_only_direct_labeler_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_direct_labeler`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler -- single DSPy call renders the final label directly from the note; no deterministic CandidateSet. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Primary metrics: call_failures=0, evidence_valid_rate=0.941, evidence_valid_rows=706, null_rows=0, parse_or_validation_failures=0, pragmatic_accuracy=0.781, pragmatic_correct=586, purist_accuracy=0.744, purist_correct=558, rendered_rows=750.
- Evidence validity: 706/750 rows (94.1%) carry an evidence_valid substring-presence trace. This architecture structurally cannot produce a null/unrendered row.
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_canonical_pipeline`; mode `validation750 replay`; replay `saved_output_replay`.
- Model role: llm_only architecture comparator; model `ollama_chat/qwen3.6:35b`.
- Registry roles: `architecture_comparator`.
- Primary metrics: evidence_trace_metric=evidence_text_contained, evidence_trace_valid_rate=0.7653333333333333, evidence_trace_valid_rows=574, null_rows=2, pragmatic_correct_of_rendered=582, pragmatic_correct_rate_of_rendered=0.7780748663101604, purist_correct_of_rendered=544, purist_correct_rate_of_rendered=0.7272727272727273, rendered_rows=748.
- Evidence validity: Backfilled from the full Qwen Phase 1 validation750 report: 574/750 rows carry the llm_only_canonical_pipeline evidence_text_contained trace; this metric is deliberately distinct from evidence_valid.
- Claim language: Phase 1 three-way architecture comparison data point for Qwen LLM-only canonical pipeline on validation750. Metrics are backfilled from gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09; validation development only, no test450 or benchmark-comparable claim.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.md`.

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_canonical_pipeline`; mode `live`; replay `live`.
- Model role: LLM-only canonical pipeline -- single DSPy call collapses extract/select/normalize/project/render into one pass; no deterministic CandidateSet or projection stage; model `openai/gpt-4.1-mini`.
- Registry roles: `architecture_comparator`.
- Primary metrics: evidence_text_contained_rows=700, null_rows=0, pragmatic_correct_of_rendered=626, purist_correct_of_rendered=581, rendered_rows=750.
- Evidence validity: 700/750 rows (93.3%) carry an evidence_text_contained free-text trace -- a metric this architecture reports in place of (and deliberately distinct from) the evidence_valid substring-presence metric the other five architectures report; do not compare the two as one accuracy number (see Phase 1 report footnote).
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands. Newest of the six architectures -- the 'purest form' fully-LLM comparator with the deterministic/hybrid clinical-reasoning rule taxonomy embedded as prompt instructions rather than pre/post processing.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `llm_only_canonical_pipeline`; mode `live`; replay `live`.
- Model role: LLM-only canonical pipeline -- single DSPy call collapses extract/select/normalize/project/render into one pass; no deterministic CandidateSet or projection stage. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Registry roles: `architecture_comparator`.
- Primary metrics: call_failures=0, evidence_text_contained_rate=0.925, evidence_text_contained_rows=694, null_rows=0, parse_or_validation_failures=0, pragmatic_accuracy=0.781, pragmatic_correct=586, purist_accuracy=0.753, purist_correct=565, rendered_rows=750.
- Evidence validity: 694/750 rows (92.5%) carry an evidence_text_contained free-text trace -- a metric this architecture reports in place of (and deliberately distinct from) the evidence_valid substring-presence metric other architectures report; do not compare directly across architectures.
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `validation750 replay`; replay `saved_output_replay`.
- Model role: hybrid architecture comparator; model `ollama_chat/qwen3.6:35b`.
- Registry roles: `architecture_comparator`.
- Primary metrics: evidence_trace_metric=evidence_valid, evidence_trace_valid_rate=0.748, evidence_trace_valid_rows=561, null_rows=4, pragmatic_correct_of_rendered=646, pragmatic_correct_rate_of_rendered=0.8659517426273459, purist_correct_of_rendered=624, purist_correct_rate_of_rendered=0.8364611260053619, rendered_rows=746.
- Evidence validity: Backfilled from the full Qwen Phase 1 validation750 report: 561/750 rows carry the architecture-specific evidence_valid trace; evidence trace metrics are not uniform across architectures.
- Claim language: Phase 1 three-way architecture comparison data point for Qwen SE on validation750. Metrics are backfilled from gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09; validation development only, no test450 or benchmark-comparable claim.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.md`.

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: LLM-only structured-events extractor and selector -- slim source-near event schema; deterministic code limited to Gan normalization, evidence validation, and scoring; model `openai/gpt-4.1-mini`.
- Registry roles: `architecture_comparator`.
- Primary metrics: evidence_valid_rows=691, null_rows=2, pragmatic_correct_of_rendered=679, purist_correct_of_rendered=661, rendered_rows=748.
- Evidence validity: 691/750 rows (92.1%) carry an evidence_valid substring-presence trace; the 2 null rows are rare parse failures, not a structural give-up signal -- see the Phase 1 report's per-architecture rendered/null derivation footnote.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands. Restarted after fixing a schema_repair.py _ASSERTION_ALIASES bug that remapped the already-valid assertion_status value 'unknown' to the invalid 'unclear'; confirmed clean via re-pilot validation25 (0 failures, 100% accuracy) before this full run (see run markdown header).
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: LLM-only structured-events extractor and selector -- slim source-near event schema; deterministic code limited to Gan normalization, evidence validation, and scoring. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Registry roles: `architecture_comparator`.
- Primary metrics: call_failures=0, evidence_valid_rate=0.957, evidence_valid_rows=718, null_rows=8, parse_or_validation_failures=8, pragmatic_accuracy=0.845, pragmatic_correct=634, purist_accuracy=0.812, purist_correct=609, rendered_rows=742.
- Evidence validity: 718/750 rows (95.7%) carry an evidence_valid substring-presence trace. 8 parse_or_validation_failures (~1%) -- within accepted noise for this architecture.
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid`; mode `live`; replay `live`.
- Model role: Hybrid -- deterministic CandidateSet extraction + LLM-extracted CandidateSet union (both generated live, per row, replicating the static _v2_high_recall artifact's own build methodology) feeding a clinical-assessment probe; shared-table numbers below come from a deep-replay of those rows through projection_render -> score -> verification_route -> verification_decision, not from the probe's raw run_split output (the probe reports schema-fit diagnostics only and has no rendered/null/purist/routed numbers of its own).; model `openai/gpt-4.1-mini`.
- Primary metrics: evidence_trace_valid_rows=734, null_rows=149, pragmatic_correct_of_rendered=536, purist_correct_of_rendered=511, rendered_rows=600, routed_rows=42.
- Evidence validity: 734/750 rows (0.979) carry a valid candidate_set_source_id_status -- a formal CandidateSet source-id validity rate, NOT the evidence_valid substring-presence metric the other five architectures report (see the Phase 1 report's evidence-trace-metric-by-architecture table; these numbers are not directly comparable).
- Supersedes: `gan2026_three_way_comparison_validation750_hybrid_gpt41mini_2026-06-07`.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis. This run replaces the prior 250-row-scoped hybrid run (gan2026_three_way_comparison_validation750_hybrid_gpt41mini_2026-06-07, kept for the historical record of what that scoping looked like): run_split's fallback CandidateSet path was rewired from a static 250-row precomputed artifact (which emitted candidate_set_missing placeholders for the other 500 rows) to live per-row generation that replicates the static artifact's own deterministic+LLM-extraction union methodology, so this run finally covers the full 750-row validation surface like the other five architectures (missing_candidate_set_rows: 0, call_failures: 0, parse_or_validation_failures: 1). Launched as a fully OS-detached process (harness silently kills long-running background bash tasks at ~9 minutes; PowerShell Start-Process survives past that window) and resumed via --resume-existing after an earlier interruption -- see run markdown header for the resume provenance.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_live_candidate_sets_gpt41mini_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `hybrid`; mode `live`; replay `live`.
- Model role: Hybrid -- deterministic CandidateSet extraction + LLM-extracted CandidateSet union (both generated live, per row) feeding a clinical-assessment probe; shared-table numbers come from a deep-replay of those rows through projection_render -> score -> verification_route -> verification_decision. deepseek-chat alias for deepseek-v4-flash non-thinking mode -- calling deepseek-v4-flash directly defaults to thinking mode (emits reasoning_content blocks that exhaust max_tokens before producing JSON output); deepseek-chat is the official non-thinking-mode alias for the same underlying v4-flash model; model `deepseek/deepseek-chat`.
- Primary metrics: evidence_trace_valid_rate=0.985, evidence_trace_valid_rows=739, null_rows=146, pragmatic_correct_of_rendered=520, pragmatic_correct_rate_of_rendered=0.861, purist_correct_of_rendered=490, purist_correct_rate_of_rendered=0.811, rendered_rows=604, routed_rows=123.
- Evidence validity: 739/750 rows (98.5%) carry a valid candidate_set_source_id_status -- a formal CandidateSet source-id validity rate from the deep-replay (NOT the evidence_valid substring-presence metric other architectures report; these numbers are not directly comparable across architecture types).
- Claim language: Phase 1 three-way architecture comparison data point (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); deepseek-v4-flash pass (third model alongside gpt-4.1-mini and qwen3.6-35b). Run had two transient Windows OSError [Errno 22] crashes during checkpoint writes (likely anti-virus file-locking); both were recovered via --resume-existing without data loss. deterministic and deterministic_canonical_pipeline are rule-based (no LLM calls); their results are shared from the gpt-4.1-mini canonical artifacts (2026-06-07) -- byte-identical across models.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08.md`.

### `gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08`
- Date/split: `2026-06-08`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase1_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads six already-completed gpt-4.1-mini validation750 architecture-comparison artifacts (deterministic, deterministic_canonical_pipeline, hybrid, llm_only_direct_labeler, hybrid_structured_events, llm_only_canonical_pipeline) and assembles a shared comparison table plus a hybrid-only routing-taxonomy appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=688, deterministic_purist_correct_of_rendered=688, hybrid_purist_correct_of_rendered=511, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=581, llm_only_direct_labeler_purist_correct_of_rendered=564, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (free-text substring presence), llm_only_canonical_pipeline reports the deliberately distinct evidence_text_contained, and hybrid reports a formal CandidateSet source-id validity rate. The report's footnotes and per-architecture metric table make this explicit so readers do not compare these as one accuracy number.
- Claim language: Phase 1 three-way architecture comparison synthesis (gpt-4.1-mini pass, validation750 only; gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 and gan2026_three_way_comparison_phase1_report_design_2026-06-07). No test450 read, no holdout-facing or benchmark-comparable claim -- compares six PipelineArchitecture configs on universally meaningful axes (rendered/null disposition, Purist/Pragmatic-correct of rendered rows, evidence-trace validity, final-answer distribution); hybrid additionally carries a routing-taxonomy appendix with no analogous surface in the other five. hybrid's shared-table row is sourced from build_unified_pipeline_artifact deep-replay (using the live-generated CandidateSets the now-fixed hybrid run embeds in its own output rows), not raw run_split output -- this asymmetry is the architectural fact under comparison, not a methodology artifact, and the report's footnotes say so explicitly. A notable finding surfaced here: deterministic and deterministic_canonical_pipeline produce IDENTICAL purist/pragmatic/distribution numbers, i.e. the staged canonical-pipeline wrapper converges on the same rendered answers as the unstaged baseline on this pass.
- Artifacts: `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.json`, `experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.md`.

### `gan2026_three_way_comparison_validation750_llm_only_direct_labeler_gpt41mini_2026-06-07`
- Date/split: `2026-06-07`; `validation`; `750` rows.
- Pipeline: `llm_only_direct_labeler`; mode `live`; replay `live`.
- Model role: LLM-only direct labeler -- single DSPy call renders the final label directly from the note; no deterministic CandidateSet; model `openai/gpt-4.1-mini`.
- Primary metrics: evidence_valid_rows=711, null_rows=0, pragmatic_correct_of_rendered=599, purist_correct_of_rendered=564, rendered_rows=750.
- Evidence validity: 711/750 rows (94.8%) carry an evidence_valid substring-presence trace. This architecture structurally cannot produce a null/unrendered row -- see the Phase 1 report's footnote on the rendered-disposition asymmetry between single-shot LLM-only and deterministic-routed architectures.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands. Restarted mid-effort after fixing an answer_kind prompt/schema mismatch bug; confirmed clean via re-pilot validation25 (0 failures, 100% accuracy) before this full run (see run markdown header).
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_llm_only_direct_labeler_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_deterministic_gpt41mini_2026-06-07`
- Date/split: `2026-06-07`; `validation`; `750` rows.
- Pipeline: `deterministic`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator -- rules-only candidate extraction, normalization, and projection; no model calls; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=695, purist_correct_of_rendered=688, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace (this architecture's reported evidence-trace metric); formal CandidateSet source-id validity is not computed for single-shot architectures.
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_deterministic_gpt41mini_2026-06-07.md`.

### `gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07`
- Date/split: `2026-06-07`; `validation`; `750` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `live`; replay `live`.
- Model role: deterministic baseline comparator routed through the staged canonical-pipeline architecture -- rules-only; no model calls; model `none (deterministic rules pipeline; no LLM calls)`.
- Primary metrics: evidence_valid_rows=750, null_rows=9, pragmatic_correct_of_rendered=695, purist_correct_of_rendered=688, rendered_rows=741.
- Evidence validity: 750/750 rows carry an evidence_valid substring-presence trace; identical to the `deterministic` architecture's numbers and final-label distribution on this split -- the staged canonical-pipeline wrapper converges on the same rendered answers as the unstaged baseline (see Phase 1 report).
- Claim language: Phase 1 three-way architecture comparison data point (gpt-4.1-mini pass, validation750, gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07); not a standalone promote/reject verdict on its own -- see gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08 for cross-architecture synthesis once it lands.
- Artifacts: `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07.jsonl`, `experiments/gan2026_three_way_comparison_validation750_deterministic_canonical_pipeline_gpt41mini_2026-06-07.md`.

### `gan2026_llm_only_typed_operations_reasoner_v3_max4800_validation25_live_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_only_typed_operations_reasoner`; mode `live validation25 typed-operations evidence-copy, graph-projection, and max4800 smoke`; replay `cache_first`.
- Model role: LLM-only typed operation extraction, operation selection, model-owned final rendering, and graph-overlay sidecar; model `openai/gpt-4.1-mini`.
- Repair mode/config: `source-checked evidence-copy repair for escaped inequality artifacts; selected current/recent operation graph projection; selected-evidence arithmetic graph fallback; max_tokens=4800`.
- Primary metrics: call_failures=0, event_evidence_total=37, event_evidence_valid=34, format_only_purist_correct=20, max_tokens=4800, parse_failures=0, raw_llm_purist_correct=15, raw_llm_scorable=15, row_count=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_valid=22, selected_operation_trace_mismatches=0, structured_records=25, truncation_warnings=0, typed_graph_raw_correct_to_wrong=1, typed_graph_raw_wrong_to_correct=9, typed_operation_graph_projection_purist_correct=23, typed_operation_graph_projection_scorable=25.
- Evidence validity: Selected evidence exact 22/25; event evidence exact 34/37; selected-operation trace mismatches 0/25. Remaining typed-graph misses are row 446 invalid selected evidence and row 467 operand-to-graph rendering.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse. The CLI default max token budget for this pipeline is now 4800.
- Superseded by: `gan2026_llm_only_typed_operations_reasoner_v3_max4800_no_call_replay_2026-06-03`.
- Claim language: Validation25 development smoke only. The 4800-token budget removed truncation warnings. This live artifact is superseded for deterministic replay interpretation by the no-call replay after generalized evidence-artifact cleanup and graph-label precedence repair.
- Artifacts: `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.jsonl`, `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.md`.

### `gan2026_llm_only_typed_operations_reasoner_v3_max4800_no_call_replay_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_only_typed_operations_reasoner`; mode `saved-output no-call replay after evidence artifact and graph-label precedence repair`; replay `saved_output_replay`.
- Model role: analysis-only replay of LLM-only typed operation extraction, selection, final rendering, and graph-overlay sidecar; model `none; saved openai/gpt-4.1-mini max4800 outputs`.
- Repair mode/config: `No-call replay using generalized semantically-neutral evidence artifact cleanup, source-note mojibake cleanup, typed graph label precedence fix, and typed_operation_graph_projection semantic repair metadata.`.
- Primary metrics: event_evidence_total=37, event_evidence_valid=37, format_only_purist_correct=20, parse_failures=0, raw_llm_purist_correct=15, raw_llm_scorable=15, row_count=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_valid=25, selected_operation_trace_mismatches=0, structured_records=25, typed_operation_graph_projection_pragmatic_correct=25, typed_operation_graph_projection_purist_correct=24, typed_operation_graph_projection_scorable=25.
- Evidence validity: Selected evidence exact 25/25; event evidence exact 37/37; selected-operation trace mismatches 0/25.
- Cache/reuse source: experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v3_max4800_2026-06-03.jsonl.
- Supersedes: `gan2026_llm_only_typed_operations_reasoner_v3_max4800_validation25_live_2026-06-03`.
- Claim language: Saved-output replay only: no hosted calls, prompt changes, scorer changes, split changes, or holdout behavior changes. Row 446 and row 467 deterministic replay bugs are fixed; row 598 remains a Purist graph-rendering miss, so revise before validation50.
- Artifacts: `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_max4800_no_call_replay_2026-06-03.jsonl`, `experiments/gan2026_llm_only_typed_operations_reasoner_validation25_max4800_no_call_replay_2026-06-03.md`.

### `gan2026_llm_heavy_evidence_selection_decision0007_validation25_contract_triage_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_heavy_evidence_selection_with_deterministic_adapters`; mode `saved-output Decision 0007 validation25 contract triage`; replay `analysis_only`.
- Model role: analysis-only reviewer for selected evidence, operand completeness, raw parser-label grammar, and cluster-axis failure slices; model `none; saved outputs only`.
- Repair mode/config: `analysis only; proposed v1 prompt/schema contract without scorer, split, adapter, or gate changes`.
- Primary metrics: adapted_miss_rows=10,128,187,190,280,446, exact_evidence_failure_rows=10,40,79,103,409,446, missing_operand_rows=128, raw_parser_label_scorable=0, row_count=25, wrong_fact_or_operand_rows=187,190,280.
- Evidence validity: Identified exact-evidence escaping failures on rows 10, 40, 79, 103, 409, and 446; later v1 reduced these to rows 10, 40, and 446.
- Cache/reuse source: Saved-output row review of the v0 Decision 0007 validation25 smoke; no hosted calls.
- Superseded by: `gan2026_llm_heavy_evidence_selection_decision0007_v1_validation25_live_2026-06-03`.
- Claim language: Analysis-only triage predeclared a v1 prompt/schema revision. It did not change scorer, split, adapter, gate, or holdout behavior.
- Artifacts: `experiments/gan2026_llm_heavy_decision0007_validation25_contract_triage_2026-06-03.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `gated month-bucket duration-selection projection ablation v1`; replay `analysis_only`.
- Model role: diagnostic gated month-bucket duration projection replay over enriched target graphs plus validation hard-slice regression panel; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `gated diagnostic month_bucket_duration_selection_v1 projection variant only; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=22, already_correct_regressions=0, frequency_with_seizure_free_node_changes=0, regression_changed_labels=4, regression_rows=232, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, unknown_no_reference_boundary_changes=1.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02`.
- Claim language: Diagnostic validation-cycle projection ablation. Gating preserves the 18/18 target corrections while removing v0 already-correct and frequency-with-seizure-free regressions; four wrong-to-wrong regression changes remain, so this is the best revise-only seed, not production policy.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `month-bucket duration-selection projection ablation v0`; replay `analysis_only`.
- Model role: diagnostic month-bucket duration projection replay over enriched target graphs plus validation hard-slice regression panel; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic month_bucket_duration_selection projection variant only; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=55, already_correct_regressions=27, frequency_with_seizure_free_node_changes=19, regression_changed_labels=37, regression_rows=232, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, unknown_no_reference_boundary_changes=2.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02`.
- Claim language: Diagnostic validation-cycle projection ablation. It fixes the intended 18-row duration surface but causes 27 already-correct validation hard-slice regressions, so it is not promoted as a production projection policy; next work should design a gated/narrow policy.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `graph-gated month-bucket duration-selection broad regression panel`; replay `analysis_only`.
- Model role: diagnostic graph-metadata-gated month-bucket duration projection replay; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `graph_gated_v2 diagnostic month_bucket_duration_selection projection variant plus graph metadata gate; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=18, already_correct_regressions=0, frequency_with_seizure_free_node_changes=0, graph_gate_active_boundary_state_node_rows=6, graph_gate_blocked_rows=46, graph_gate_selected_rule_not_duration_normalization_v0_rows=46, regression_changed_labels=0, regression_rows=232, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, unknown_no_reference_boundary_changes=0.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows; graph gate blocked 46 month-bucket replacements using graph metadata.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02`.
- Claim language: Diagnostic validation-cycle graph-metadata gate replay. The gate preserves 18/18 enriched duration corrections and blocks all broad-regression label changes by requiring selected month-bucket nodes to come from seizure_free_duration_node_normalization_v0 and by refusing active boundary-state graphs; no production projection policy is promoted.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.md`.

### `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `gated month-bucket duration-selection broad regression panel`; replay `analysis_only`.
- Model role: diagnostic gated month-bucket duration projection replay with hard-slice family regression accounting; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `gated diagnostic month_bucket_duration_selection_v1 projection variant plus hidden-family regression tags; no scorer, graph-builder, production projection-policy, or holdout change`.
- Primary metrics: all_rows_changed_labels=22, already_correct_regressions=0, cluster_or_diary_changed_labels=4, frequency_with_seizure_free_node_changes=0, regression_changed_labels=4, regression_rows=232, seizure_free_overreach_changed_labels=3, target_exact_duration_corrections=18, target_exact_duration_regressions=0, target_rows=18, temporal_conflict_changed_labels=4, unknown_no_reference_boundary_changes=1.
- Evidence validity: Selected-node evidence was exact-offset valid for 18/18 target rows and 232/232 regression rows.
- Cache/reuse source: Saved seizure-free duration node replay JSONL and validation hard-slice state-graph diagnostics; no hosted calls.
- Supersedes: `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02`.
- Claim language: Diagnostic validation-cycle broad-regression replay. Gated v1 preserves 18/18 enriched duration corrections, adds hidden-family regression accounting, and leaves four wrong-to-wrong regression changes concentrated in cluster/diary plus temporal-conflict rows, including one unknown-boundary row; no production policy is promoted.
- Artifacts: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.jsonl`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.json`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.md`.

### `gan2026_llm_replacement_postprocessing_ablation_validation250_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `250` rows.
- Pipeline: `llm_replacement_postprocessing_ablation`; mode `saved-output no-call post-processing replacement ablation`; replay `saved_output_replay`.
- Model role: analysis-only deterministic post-processing replacement replay; model `none; saved outputs only`.
- Repair mode/config: `raw_llm + format_only + selected_evidence_arithmetic + benchmark_aligned`.
- Primary metrics: benchmark_aligned_adapter_purist_correct=204, condition_rows=1000, format_only_repair_purist_correct=188, raw_model_selected_label_purist_correct=188, reused_raw_output_rows=50, row_count=250, selected_evidence_arithmetic_only_purist_correct=219.
- Evidence validity: Reports selected-evidence exactness, event/node evidence validity, and selected-event trace mismatches for each replacement condition.
- Cache/reuse source: experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl.
- Supersedes: `gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02`.
- Claim language: Diagnostic saved-output replay only. No hosted calls, prompt changes, scorer changes, production projection policy changes, or holdout behavior changes are made.
- Artifacts: `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.jsonl`, `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.json`, `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.md`.

### `gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices_planned`; `250` rows.
- Pipeline: `llm_replacement_postprocessing_ablation`; mode `LLM-replacement deterministic post-processing ablation design`; replay `analysis_only`.
- Model role: analysis-only replacement-ablation planner for deterministic post-processing ownership; model `none`.
- Repair mode/config: `planning only; no scorer, projection, graph-builder, prompt, or holdout change`.
- Primary metrics: planned_conditions=11, replacement_targets=6, required_report_families=6, validation_surface_max_rows=250.
- Evidence validity: Design requires every replay to report selected-evidence exactness, event/node evidence exactness, selected-event trace mismatches, selected-node source, and rows dropped for non-exact evidence.
- Cache/reuse source: No hosted calls; design derived from project retrospective, LLM-heavy v1 validation250 failure families, state-graph diagnostics, and existing repair-attribution conventions.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation250_live_2026-06-02`, `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02`.
- Claim language: Diagnostic design only. Predeclares replacement ablations for deterministic post-processing modules before LLM-heavy v2 prompt work; no scorer, prompt, production projection policy, or holdout behavior changed.
- Artifacts: `experiments/gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation250_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `250` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation250 diagnostic scale-up after validation50 gate`; replay `cache_first`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 prompt/schema plus non-semantic enum/unit alias repair; benchmark-aligned layer remains side-car and selected-evidence arithmetic remains diagnostic attribution only`.
- Primary metrics: benchmark_aligned_purist_correct=204, call_failures=0, event_evidence_total=535, event_evidence_valid=508, format_only_purist_correct=188, parse_failures=13, raw_llm_pragmatic_correct=195, raw_llm_purist_correct=188, raw_llm_scorable=213, row_count=250, selected_event_trace_mismatches=9, selected_evidence_arithmetic_pragmatic_correct=225, selected_evidence_arithmetic_purist_correct=219, selected_evidence_valid=230, structured_records=237.
- Evidence validity: Selected evidence exact 230/250; event evidence exact 508/535; nine selected-event trace mismatches and 13 parse/schema failures remain.
- Cache/reuse source: Reused validation50 v1 raw outputs for the first 50 rows and ran rows 51-250 live with DSPy cache enabled.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation50_live_2026-06-02`.
- Claim language: Validation250 rejects promotion of v1 as an LLM-heavy final-label candidate: raw/format-only Purist is 188/250 and the stronger 219/250 selected-evidence arithmetic layer is attribution-diagnostic, not LLM-heavy success.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_schema_smoke_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation25 followed by saved-output schema replay after scalar-list shape repair`; replay `schema_replay`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `raw_llm + format_only + selected_evidence_arithmetic + benchmark_aligned + oracle_format_upper_bound layers; scalar-list schema repair only`.
- Primary metrics: benchmark_aligned_purist_correct=13, format_only_purist_correct=10, raw_llm_scorable=0, row_count=25, schema_valid_rows=24, selected_event_trace_mismatches=0, selected_evidence_arithmetic_purist_correct=23, selected_evidence_valid=18.
- Evidence validity: Event evidence 42/47 exact; selected evidence 18/25 exact, below the Stage A 22/25 stop rule.
- Cache/reuse source: DSPy cache enabled for the initial live run; saved raw outputs replayed after non-semantic scalar-list schema repair.
- Supersedes: `gan2026_llm_heavy_extraction_protocol_2026-06-02`.
- Claim language: LLM-heavy validation development smoke only. Schema validity reaches the 24/25 minimum after shape replay, but selected evidence exactness and raw LLM scorer format fail the Stage A stop rule; revise prompt/schema before validation50.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.md`, `experiments/gan2026_llm_heavy_extraction_protocol_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `row-level error analysis of validation25 schema smoke`; replay `analysis_only`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `analysis over raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, and oracle_format_upper_bound layers`.
- Primary metrics: benchmark_aligned_purist_correct=13, benchmark_regressions_vs_arithmetic=10, deterministic_v1_same_rows_purist_correct=25, event_evidence_total=47, event_evidence_valid=42, format_only_purist_correct=10, raw_llm_scorable=0, selected_evidence_arithmetic_purist_correct=23, selected_evidence_valid=18, structured_records=24.
- Evidence validity: Selected evidence exactness 18/25 and event evidence exactness 42/47; selected-event traces had 0 mismatches.
- Cache/reuse source: No new hosted calls; analysis uses saved validation25 JSONL and deterministic V1 same-row comparator.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_schema_smoke_2026-06-02`.
- Claim language: Full validation-development error analysis. High selected-evidence arithmetic score is diagnostic only because raw LLM labels are 0/25 scorable and the best layer depends on deterministic derivation over selected evidence; revise before validation50.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.csv`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.json`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`.

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `25` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration projection ablation over saved state graphs`; replay `analysis_only`.
- Model role: diagnostic seizure-free duration projection replay over saved graph rows; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic seizure-free duration projection variants only; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: baseline_exact_matches=0, exact_node_not_selected_rows=3, non_seizure_free_selected_rows=4, numeric_duration_present_gold_absent_rows=2, numeric_duration_priority_exact_matches=7, only_broad_duration_nodes_rows=16, oracle_exact_node_matches=7, row_count=25, seizure_free_priority_exact_matches=6, shortest_duration_exact_matches=7.
- Evidence validity: Replayed saved graph nodes from exact-evidence-gated diagnostic artifacts; this artifact measures duration projection behavior, not new evidence extraction.
- Cache/reuse source: Saved validation hard-slice projection/arbitration surface reused; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. Projection-only policies recover at most 7/25 exact seizure-free duration labels because most misses lack an exact gold duration node; the next repair target is seizure-free duration graph-node construction/normalization, not a production projection-policy promotion.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration graph-node construction/normalization replay`; replay `analysis_only`.
- Model role: diagnostic seizure-free duration node-construction replay over saved graph rows; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `seizure_free_duration_node_normalization_v0 merged into saved diagnostic graphs; unchanged projection policy`.
- Primary metrics: baseline_exact_gold_duration_rows=0, exact_evidence_valid_nodes=21, month_scale_representability_gains=16, month_scale_representable_rows=18, new_duration_nodes=21, replayed_exact_gold_duration_rows=17, still_only_over_broad_year_rows=0, unchanged_projection_changed_from_baseline=0, unchanged_projection_exact_matches=0.
- Evidence validity: New duration-node replay emitted 21/21 exact-evidence-valid nodes over the 18 predeclared validation rows, with 0 row-level evidence errors.
- Cache/reuse source: Saved validation hard-slice projection/arbitration graph rows; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_ablation_design_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. Node construction recovered month-scale representability on all 18 target rows, but unchanged projection still recovered 0/18 exact duration labels, so projection/arbitration remains separate and no production policy is promoted.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_ablation_design_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration graph-node construction/normalization ablation design`; replay `analysis_only`.
- Model role: analysis-only graph-node ablation designer; model `none`.
- Repair mode/config: `planning only; no scorer, graph-builder, or projection repair`.
- Primary metrics: existing_rule_families=5, gold_multiple_month_rows=17, numeric_duration_present_gold_absent_rows=2, only_broad_duration_nodes_rows=16, target_rows=18.
- Evidence validity: Design requires exact-evidence validity for newly emitted duration nodes before any diagnostic replay can be interpreted.
- Cache/reuse source: No hosted calls; design derived from saved validation hard-slice duration projection ablation rows.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02`.
- Claim language: Diagnostic design only. Predeclares an 18-row validation hard-slice node-construction surface and acceptance criteria for month-scale seizure-free duration representability; no scorer, projection, production graph-builder, or holdout policy change.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_ablation_design_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `seizure-free duration enriched projection replay`; replay `analysis_only`.
- Model role: diagnostic duration-selection replay over enriched seizure-free duration graphs; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic duration-selection variants over replayed_graph, including month_bucket_duration_selection; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: baseline_exact_matches=0, exact_node_not_selected_rows=17, month_bucket_duration_selection_exact_matches=18, numeric_duration_present_gold_absent_rows=1, oracle_exact_node_matches=17, row_count=18, shortest_duration_exact_matches=14.
- Evidence validity: Uses replayed graphs from the exact-evidence-valid duration-node artifact; this artifact measures projection selection over enriched graphs, not new evidence extraction.
- Cache/reuse source: Saved validation hard-slice seizure-free duration node replay JSONL; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. The month_bucket_duration_selection variant recovers 18/18 exact duration labels on this enriched validation surface by preferring broad month-bucket nodes over numeric-month or broad-year conflicts and preserving plural numeric-month output on row 5040; no scorer normalization or production projection policy is changed.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `42` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `projection/arbitration ablation over saved state graphs`; replay `analysis_only`.
- Model role: diagnostic projection/arbitration replay over already-representable graph rows; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `diagnostic projection variants only; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: accepted_replay_projection_misses=4, baseline_exact_matches=0, boundary_state_priority_exact_matches=17, boundary_state_priority_purist_f1=0.8571, hard_slice_representable_projection_misses=38, lowest_current_frequency_exact_matches=3, oracle_gold_node_exact_matches=23, oracle_gold_node_purist_f1=1.0, row_count=42, seizure_free_priority_exact_matches=8.
- Evidence validity: Replayed only saved graph nodes from exact-evidence-gated diagnostic artifacts; this artifact measures arbitration/projection behavior, not new evidence extraction.
- Cache/reuse source: Saved validation hard-slice state-graph diagnostics plus accepted boundary-node replay JSONL; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02`.
- Claim language: Diagnostic validation-cycle replay only. Boundary-state priority is the strongest non-oracle signal, but oracle exact-label gaps show seizure-free duration projection remains separate work; do not promote a production policy from this artifact alone.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `18` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `month-bucket duration selection projection-ablation decision`; replay `analysis_only`.
- Model role: analysis-only duration-selection policy decision; model `none; saved validation graph artifacts reused`.
- Repair mode/config: `decision only; month_bucket_duration_selection remains diagnostic and seeds a separately named projection ablation; no scorer, graph-builder, or production projection-policy change`.
- Primary metrics: baseline_exact_matches=0, enriched_replay_rows=18, month_bucket_duration_selection_exact_matches=18, oracle_exact_node_matches=17.
- Evidence validity: Decision relies on exact-evidence-valid duration nodes from the replayed graph artifact; the next ablation must preserve selected-node evidence validity.
- Cache/reuse source: Decision derived from saved enriched validation hard-slice projection replay; no hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02`.
- Claim language: Diagnostic validation-cycle decision. month_bucket_duration_selection becomes a separately named projection-ablation seed, not scorer normalization, benchmark evidence, or production policy.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_live_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices+synthetic_hard_cases`; `39` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `live boundary-state graph-builder validation31 plus synthetic unknown8 stress`; replay `live`.
- Model role: hosted boundary-state graph node builder; model `openai/gpt-4.1-mini`.
- Repair mode/config: `exact-evidence-gated unknown/unresolved_multiple node construction; no final-label projection`.
- Primary metrics: call_failures=0, synthetic_exact_evidence_total=0, synthetic_exact_evidence_valid=0, synthetic_representability_gain_candidates=0, synthetic_row_count=8, synthetic_schema_valid_rows=8, validation_exact_evidence_total=29, validation_exact_evidence_valid=28, validation_representability_gain_candidates=10, validation_row_count=31, validation_schema_valid_rows=30.
- Evidence validity: Validation31 produced 28/29 exact-evidence-valid nodes with 30/31 schema-valid rows and one row-level schema/evidence miss; synthetic unknown8 was schema-valid but emitted 0 nodes.
- Cache/reuse source: DSPy cache enabled; validation31 and synthetic unknown8 live runs recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02`.
- Claim language: Hosted graph-builder diagnostic only. It emitted no final Gan labels and did not run projection or arbitration; keep revise-only pending accepted-node graph replay and separate projection/arbitration ablations.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_gpt41mini_live_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_gpt41mini_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_gpt41mini_live_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_interpretation_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_2026-06-02`
- Date/split: `2026-06-02`; `synthetic_hard_cases`; `8` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `live boundary-state graph-builder synthetic unknown8 v1 unknown-recall stress`; replay `live`.
- Model role: hosted boundary-state graph node builder; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 unknown-recall prompt + root-level JSON output contract; no final-label projection`.
- Primary metrics: call_failures=0, exact_evidence_total=8, exact_evidence_valid=8, representability_gain_candidates=8, row_count=8, schema_valid_rows=8.
- Evidence validity: Synthetic unknown8 v1 produced 8/8 exact-evidence-valid unknown nodes with 8/8 schema-valid rows, 0 call failures, and 8/8 representability-gain candidates.
- Cache/reuse source: DSPy cache enabled; synthetic unknown8 v1 live run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_live_2026-06-02`.
- Claim language: Hosted graph-builder diagnostic only. The v1 prompt fixes synthetic unknown-state node recall and root-level output shape, emits no final Gan labels, and does not run graph merge, projection, arbitration, or benchmark scoring.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `1` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `live boundary-state graph-builder smoke`; replay `live`.
- Model role: hosted boundary-state graph node builder; model `openai/gpt-4.1-mini`.
- Repair mode/config: `exact-evidence-gated unknown/unresolved_multiple node construction; no final-label projection`.
- Primary metrics: call_failures=0, exact_evidence_total=2, exact_evidence_valid=2, representability_gain_candidates=1, row_count=1, schema_valid_rows=1.
- Evidence validity: Live one-row smoke produced 2/2 exact-evidence nodes and 1/1 representability-gain candidate, with 1/1 schema-valid rows and 0 call failures.
- Cache/reuse source: DSPy cache enabled; live smoke recorded 0 reused raw outputs. Prompt-only replay seed is available at experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_smoke_reuse_2026-06-02.jsonl.
- Supersedes: `gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02`.
- Claim language: Hosted graph-builder component smoke only. It emits exact-evidence unknown/unresolved_multiple nodes and no final Gan label; projection F1 and arbitration are intentionally out of scope.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_live_smoke_2026-06-02.md`.

### `gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices`; `10` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `accepted boundary-node graph replay`; replay `analysis_only`.
- Model role: diagnostic graph replay over accepted hosted boundary-state nodes; model `none; saved openai/gpt-4.1-mini boundary-builder outputs reused`.
- Repair mode/config: `accepted_boundary_state_nodes_v0 merged into deterministic graph; unchanged projection policy`.
- Primary metrics: accepted_boundary_rows=10, accepted_hosted_nodes=18, baseline_representable_rows=0, projection_changed_from_baseline=7, projection_exact_label_matches=6, projection_pragmatic_f1=0.9, projection_purist_f1=0.9, replayed_representable_rows=10, representability_gains=10.
- Evidence validity: Accepted replay used only validation gain-candidate rows with schema-valid exact-evidence nodes; row 869 and synthetic unknown stress rows were excluded.
- Cache/reuse source: Saved validation31 hosted boundary-state graph-builder JSONL; no new hosted calls.
- Supersedes: `gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_live_2026-06-02`.
- Claim language: Diagnostic graph replay only. It shows accepted nodes recover graph representability on the 10 gain rows; projection/arbitration changes remain separate ablation work and this is not a benchmark result.
- Artifacts: `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.jsonl`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.json`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_2026-06-02.md`.

### `gan2026_clinical_frequency_state_graph_validation_cycle_diagnostics_2026-06-02`
- Date/split: `2026-06-02`; `validation+synthetic_hard_cases`; `381` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `validation-only state-graph diagnostics`; replay `analysis_only`.
- Model role: diagnostic graph scaffold plus saved LLM atomic claims; model `none; saved openai/gpt-4.1-mini claim-table outputs reused for atomic-claim conversion`.
- Repair mode/config: `deterministic_oracle_span_harvester_v0 + gan2026_state_graph_projection_v0 + llm_atomic_claim_graph_builder_v0`.
- Primary metrics: counterfactual_order_invariance=1.0, counterfactual_paraphrase_invariance=0.98, hard_slice_oracle_coverage=0.876, hard_slice_projection_purist_f1=0.916, llm_atomic_claim_exact_nodes=79, llm_atomic_claim_nodes=80, synthetic_oracle_coverage=0.5357, synthetic_projection_purist_f1=0.6964, validation50_oracle_coverage=0.94, validation50_projection_purist_f1=0.96.
- Evidence validity: Deterministic graph nodes preserve exact evidence offsets; saved LLM atomic-claim conversion produced 79/80 exact-evidence-certain nodes and downgraded one non-exact claim to uncertain.
- Cache/reuse source: No hosted calls for deterministic diagnostics; LLM atomic-claim rows reused saved validation25 claim-table output.
- Supersedes: `gan2026_clinical_frequency_state_graph_protocol_2026-06-02`.
- Claim language: Diagnostic architecture cycle only. Separates oracle coverage, projection-only F1, exact-evidence-gated LLM claim rows, counterfactual invariance, and validation-only grouping; no benchmark or holdout claim.
- Artifacts: `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation25_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_synthetic_hard_cases_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.jsonl`, `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_validation50_counterfactual_invariance_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_family_aware_validation_grouping_2026-06-02.json`, `experiments/gan2026_clinical_frequency_state_graph_family_aware_validation_grouping_2026-06-02.md`.

### `gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02`
- Date/split: `2026-06-02`; `validation_hard_slices+synthetic_hard_cases`; `306` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `row/family diagnostic review`; replay `analysis_only`.
- Model role: analysis-only reviewer; model `none`.
- Repair mode/config: `planning only; no scorer or projection repair`.
- Primary metrics: hard_slice_missing_representability_rows=31, hard_slice_missing_unknown_rows=20, hard_slice_missing_unresolved_multiple_rows=11, representable_projection_miss_rows=34, synthetic_missing_frequency_rows=16, synthetic_missing_unknown_rows=8.
- Evidence validity: Review uses graph rows with exact-evidence offsets; next hosted builder must measure exact-evidence validity for newly proposed unknown/unresolved_multiple nodes.
- Cache/reuse source: No hosted calls; reviewed existing validation-only state-graph diagnostic artifacts and synthetic hard-case diagnostics.
- Supersedes: `gan2026_clinical_frequency_state_graph_validation_cycle_diagnostics_2026-06-02`.
- Claim language: Diagnostic planning artifact only. Chooses the next hosted graph-builder target from validation-only row/family review; no benchmark or holdout claim.
- Artifacts: `experiments/gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02.md`.

### `gan2026_clinical_frequency_state_graph_protocol_2026-06-02`
- Date/split: `2026-06-02`; `validation protocol`; `0` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `protocol and deterministic scaffold`; replay `analysis_only`.
- Model role: diagnostic graph scaffold; model `none`.
- Repair mode/config: `graph_oracle_coverage + deterministic_projection + counterfactual_invariance`.
- Primary metrics: scaffold_tests=5.
- Evidence validity: Graph nodes are tested for exact evidence offsets; no corpus run yet.
- Supersedes: `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_generalization_audit_2026-06-02`.
- Claim language: Architecture scaffold only, not a benchmark result. Next results must separate graph coverage, projection, invariance, and arbitration effects.
- Artifacts: `experiments/gan2026_clinical_frequency_state_graph_protocol_2026-06-02.md`.

### `gan2026_qwen36_35b_ollama_chat_setup_smoke_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `1` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `native Ollama chat setup smoke`; replay `live`.
- Model role: local LLM-only claim-table selector; model `ollama_chat/qwen3.6:35b`.
- Repair mode/config: `none; endpoint smoke before Qwen-specific schema repair`.
- Primary metrics: call_failures=0, parse_schema_failures=1, row_count=1, structured_rows=0.
- Evidence validity: No structured record; output-contract smoke only.
- Cache/reuse source: DSPy cache disabled; native Ollama /api/chat smoke used think=false.
- Claim language: Endpoint setup is unblocked through ollama_chat/qwen3.6:35b with think=false, but v5 is not ladder-ready for Qwen: validation1 returned a nonempty Python-style dict and final_selector shape, producing a schema parse failure. Do not treat this as model-quality evidence or start validation5/25 until prompt hardening or a named schema-repair ablation exists. Dedicated schema-contract risk note logged for future Qwen prompt/repair design.
- Artifacts: `experiments/gan2026_qwen36_35b_ollama_chat_setup_smoke_2026-06-01.md`, ``, `experiments/gan2026_llm_only_claim_table_selector_validation1_prompt_only_v5_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_validation1_prompt_only_v5_2026-06-01.md`, `experiments/gan2026_llm_only_claim_table_selector_validation1_qwen36_35b_v5_ollama_chat_smoke_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_validation1_qwen36_35b_v5_ollama_chat_smoke_2026-06-01.md`.

### `gan2026_minimal_evidence_selector_validation25_gpt41mini_v0_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `25` rows.
- Pipeline: `llm_only_minimal_evidence_selector`; mode `live minimal answer plus supporting_facts contract`; replay `live`.
- Model role: hosted LLM-only minimal evidence selector baseline; model `openai/gpt-4.1-mini`.
- Repair mode/config: `minimal alias/shape repair available; strict_format + frozen_clean_scorer_facing scoring`.
- Primary metrics: answer_evidence_valid=24, call_failures=0, clean_pragmatic_correct=16, clean_purist_correct=16, derived_state_complete=25, invalid_json_failures=0, minimal_records=25, parse_schema_failures=0, raw_pragmatic_correct=2, raw_purist_correct=2, raw_scorable=2, review_projection_complete=25, row_count=25, strict_format_purist_correct=15, supporting_fact_evidence_total=50, supporting_fact_evidence_valid=49.
- Evidence validity: Answer evidence exact in 24/25 rows; supporting-fact evidence exact in 49/50 facts. Row 243 used a non-exact answer/supporting evidence substring.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs; first-device OpenAI/LiteLLM smoke passed from .env before run.
- Claim language: Hosted simplified-contract baseline is output-contract clean with no JSON/schema failures and no alias repairs, but raw source-near answers are mostly scorer-unparsable; frozen clean scorer-facing score is 16/25 Purist and Pragmatic. Use as matched GPT-4.1 mini transfer baseline for Qwen minimal-contract validation, not holdout evidence.
- Artifacts: `experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v0_2026-06-01.jsonl`, `experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v0_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v02_validation250_live_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live rules candidates then conservative LLM adjudicator`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: adjudicator_pragmatic_correct=245, adjudicator_purist_correct=244, call_failures=0, candidate_set_purist_recall=246, changed_final_labels=8, deterministic_correct_to_adjudicator_wrong=2, deterministic_pragmatic_correct=246, deterministic_purist_correct=246, deterministic_wrong_to_adjudicator_correct=0, parse_failures=0, raw_adjudicator_purist_correct=245, raw_changed_final_labels=9, row_count=250.
- Evidence validity: Deterministic candidate evidence 250/250 exact in component ablation; raw/gated adjudicator evidence not independently scored in this artifact.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_validation50_live_2026-06-01`.
- Claim language: Revise before any broader run or holdout: validation250 live underperformed deterministic top, made 8 gated label changes, introduced 2 deterministic-correct regressions, and produced 0 deterministic-wrong to gated-correct Purist corrections.
- Artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.json`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_audit_trail_interpretation_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v02_synthetic_hard_case_component_stress_2026-06-01`
- Date/split: `2026-06-01`; `synthetic_hard_cases`; `56` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live synthetic hard-case component stress`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: candidate_set_purist_recall=42, deterministic_correct_to_adjudicator_wrong=0, deterministic_purist_correct=39, gated_changed_labels=5, gated_purist_correct=42, parse_failures=5, raw_changed_labels=7, raw_correct_to_wrong=0, raw_purist_correct=44, raw_wrong_to_correct=5, row_count=56.
- Evidence validity: Row-level failure review completed: schema failures are enum/output-contract hygiene; cluster/diary misses are candidate-recall limited; proxy boundary demotions need a separate gate ablation.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_saturated_surface_analysis_2026-06-01`.
- Claim language: Diagnostic/revise-only synthetic hard-case component stress. Row-level review chose cluster/diary candidate-generation recall as the single next v0.2 revision target; schema repair and proxy/boundary gate relaxation stay separate named ablations.
- Artifacts: `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_failure_review_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v02_saturated_surface_analysis_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `validation hard-slice and selective-action analysis`; replay `analysis_only`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback; no new repair`.
- Primary metrics: candidate_absent_or_weak_rows=4, deterministic_miss_rows=4, flag_only_actions=10, gated_action_rate=0.032, gated_changed_labels=8, gated_correct_to_wrong=2, gated_wrong_to_correct=0, raw_action_rate=0.036, raw_changed_labels=9, raw_correct_to_wrong=2, raw_wrong_to_correct=1, row_count=250, synthetic_hard_cases=56.
- Evidence validity: Accepted-change evidence proxy counted 2 evidence-valid raw/gated changes; exact LLM evidence validity still requires hard-case/component-stress review.
- Cache/reuse source: Saved v0.2 validation250 live JSONL; no hosted calls.
- Supersedes: `gan2026_hybrid_adjudicator_v02_validation250_live_2026-06-01`.
- Claim language: Analysis-only saturated-surface report: raw changes show one useful correction but gated changes have 0 corrections and 2 regressions. Keep v0.2 revise-only and move to manual review of the synthetic hard-case panel or stricter selective-action design before any holdout audit.
- Artifacts: `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slices_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01.jsonl`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_case_schema_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slice_schema_2026-06-01.json`.

### `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_case_component_stress_2026-06-01`
- Date/split: `2026-06-01`; `synthetic_hard_cases`; `56` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live synthetic hard-case component stress with cluster_diary_candidate_recall`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `cluster_diary_candidate_recall + conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: candidate_set_purist_recall=50, deterministic_correct_to_adjudicator_wrong=0, deterministic_purist_correct=39, gated_changed_labels=13, gated_purist_correct=50, parse_failures=1, raw_changed_labels=15, raw_correct_to_wrong=0, raw_purist_correct=52, raw_wrong_to_correct=13, row_count=56.
- Evidence validity: Candidate revision preserves exact evidence substrings for added cluster/diary candidates; raw/gated adjudicator evidence still not independently scored beyond selected candidate support and gate checks.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_synthetic_hard_case_component_stress_2026-06-01`.
- Claim language: Diagnostic/revise-only named hybrid v0.2 candidate-recall revision outside frozen deterministic V1. The branch fixed all targeted cluster/diary recall misses on the synthetic panel and improved gated hard-case performance without regressions, but remaining proxy/boundary, seizure-free, shorthand, and schema failures stay separate ablation targets.
- Artifacts: `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`, `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_gpt41mini_live_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_component_stress_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_component_stress_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v01_validation750_schema_replay_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `rules candidates then LLM adjudicator schema replay`; replay `schema_replay`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `parser defaults + clean_scorer_facing`.
- Primary metrics: deterministic_top_purist_correct=697, parse_failures=0, pragmatic_correct=689, purist_correct=680, row_count=750.
- Evidence validity: See full-validation interpretation report.
- Cache/reuse source: saved raw outputs from hybrid v0.1 validation750.
- Supersedes: `gan2026_hybrid_adjudicator_v01_validation250_schema_replay_2026-06-01`.
- Claim language: Revise before holdout; underperformed deterministic top on full validation because adjudicator introduced 24 deterministic-correct regressions against 7 corrections.
- Artifacts: `experiments/gan2026_arch2_validation750_gpt41mini_v01_schema_replay_2026-06-01.jsonl`, `experiments/archive/gan2026_arch2_smoke_iterations/gan2026_arch2_validation750_gpt41mini_v01_schema_replay_2026-06-01.md`, `experiments/archive/gan2026_arch2_smoke_iterations/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v01_validation250_schema_replay_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `rules candidates then LLM adjudicator schema replay`; replay `schema_replay`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `parser defaults + clean_scorer_facing`.
- Primary metrics: candidate_set_purist_recall=246, parse_failures=0, pragmatic_correct=244, purist_correct=243, row_count=250.
- Evidence validity: Candidate-set Purist recall 246/250.
- Cache/reuse source: saved raw outputs from hybrid v0.1 validation250.
- Superseded by: `gan2026_hybrid_adjudicator_v01_validation750_schema_replay_2026-06-01`.
- Claim language: Strongest 250-row validation candidate, but deterministic-correct regressions and candidate-recall misses required full failure review before any promotion.
- Artifacts: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.jsonl`, `experiments/archive/gan2026_arch2_smoke_iterations/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`, `experiments/archive/gan2026_arch2_smoke_iterations/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`.

### `gan2026_claim_table_v4_validation250_schema_replay_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `250` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `prompt-only schema replay`; replay `schema_replay`.
- Model role: LLM-only claim-table selector; model `openai/gpt-4.1-mini`.
- Repair mode/config: `strict_format + clean_scorer_facing`.
- Primary metrics: clean_pragmatic_correct=238, clean_purist_correct=231, parse_schema_failures=0, row_count=250, structured_rows=250.
- Evidence validity: 247/250 selected evidence exact in live diagnostic; replay repaired non-semantic output shape.
- Cache/reuse source: saved raw outputs from v4 validation250.
- Supersedes: `gan2026_claim_table_v4_validation250_live_2026-06-01`.
- Superseded by: `gan2026_claim_table_v4_validation750_2026-06-01`.
- Claim language: Development diagnostic cleared 0.9000 on 250 rows after schema replay, but semantic failure families keep it revise-only.
- Artifacts: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.jsonl`, `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`.

## Reject

### `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26`
- Date/split: `2026-06-26`; `test`; `450` rows.
- Pipeline: `consensus_fresh_agreement_selector_frozen_gate4`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: No-call aggregate-only replay of frozen v0.9 selector over Gate 3 constrained deterministic, two-agent consensus, and fresh-evidence test components.; model `none`.
- Registry roles: `holdout_anchor`, `component_ladder`.
- Repair mode/config: `selector_v0_9_constrained_no_call_replay`.
- Primary metrics: changed_label_precision=0.5909, changed_labels=44, claim_scope=constrained_holdout_evidence, correct_to_wrong=7, deterministic_purist_correct=329, exact_source_symmetry=no, gate_passed=no, net_purist_gain_vs_deterministic=19, row_level_output_written=no, selected_pragmatic_correct=358, selected_purist_correct=348, wrong_to_correct=26.
- Evidence validity: User-authorized frozen aggregate-only locked test450 audit. No row-level failures, rationales, evidence, selected events, or transitions are reported; source symmetry is constrained, not exact.
- Cache/reuse source: Gate 3 constrained source set: deterministic DCP test450, available two-agent consensus test450, and V12 fresh-evidence v0.6/safety-v0.9 test450 artifact.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_source_symmetry_preflight_2026-06-26`.
- Claim language: Gate 4 numeric bars fail. Record as final-evaluation evidence and return any follow-up to validation-only component-generation work.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.md`, `experiments/build_gan2026_v09_frozen_gate4_constrained_aggregate_audit.py`.

### `exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_llm_only_per_entity`; mode `live`; replay `native_run_split`.
- Model role: Existing focused per-entity Diagnosis prompt, run as the first specialist-prompt comparison against v0.5 single structured key-entity prompt.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only`.
- Primary metrics: diagnosis_clinical_headline_f1=0.282, diagnosis_semantic_item_f1=0.259, diagnosis_source_near_f1=0.565, diagnosis_source_near_recall=0.429, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_llm_only_per_entity_v0.4.
- Evidence validity: 0 call failures, 0 parse failures; 29/29 evidence-valid rendered mentions (1.0000).
- Claim language: Negative specialist-prompt comparison. The existing per-entity Diagnosis prompt is cleaner than the old all-9 baseline on source-near recall, but it is not competitive with the v0.5 single structured prompt on objective-aligned Diagnosis clinical recovery (0.282 vs 0.569). Do not promote; next specialist attempt should start from v0.5 guidance or use a verifier/repair prompt.
- Artifacts: `experiments/exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618_diagnosis.jsonl`, `experiments/exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618_diagnosis.md`, `experiments/exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618_combined.json`, `experiments/exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618_combined.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_specialist_prompt_comparison_2026-06-18.md`.

### `exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_diagnosis_reconciler`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis reconciler v0.2 over Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 candidates. v0.2 adds explicit candidate concept groups for generic epilepsy, focal-family, tonic-clonic, secondary-generalised, and structural/symptomatic decisions.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; verifier/decomposer inputs and concept groups are candidate scaffolding`.
- Primary metrics: diagnosis_f1=0.647, diagnosis_precision=0.636, diagnosis_recall=0.658, evidence_validity_rate=0.9956, parse_failures=0, prompt_version=exectv2_hybrid_diagnosis_reconciler_v0.2, source_near_overlap_f1=0.777.
- Evidence validity: 0 call failures, 0 parse failures; 449/451 evidence-valid rendered mentions. Residual ledger is analysis-only over the same JSONL.
- Cache/reuse source: Uses saved Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 dev140 artifacts as candidate inputs.
- Claim language: Reject as current Diagnosis candidate. v0.2 concept grouping improved dev25 but transferred worse than v0.1 on dev140 (0.647 vs 0.658), with higher FP count. Keep v0.1 as current numeric Diagnosis candidate; next loop should use constrained accept/reject gating.
- Artifacts: `experiments/exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618.md`, `experiments/exectv2_diagnosis_reconciler_v02_residual_ledger_dev140_20260618.json`, `experiments/exectv2_diagnosis_reconciler_v02_residual_ledger_dev140_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_reconciler_v02_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_diagnosis_decomposer_v01_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_diagnosis_decomposer`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis heading/narrative decomposer v0.1 over the v0.5 single structured key-entity draft. Deterministic code proposes heading and narrative candidate spans; the model owns final Diagnosis mentions. Post-processing only gates schema/evidence, strips model CUI/CUIPhrase, projects CUIs, and scores.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `neutral schema repair + benchmark CUI projection only; model-supplied CUI/CUIPhrase stripped before projection; deterministic diagnosis spans are checklist scaffolding, not predictions`.
- Primary metrics: diagnosis_f1=0.642, diagnosis_precision=0.631, diagnosis_recall=0.653, diagnosis_spans=812, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_diagnosis_decomposer_v0.1.
- Evidence validity: 0 call failures, 0 parse failures; 462/462 evidence-valid rendered mentions.
- Claim language: Reject as current Diagnosis candidate. The decomposition increased source-near recall but over-emitted too many Diagnosis mentions and underperformed verifier v0.6 (0.642 vs 0.651). Keep v0.6 as current Diagnosis baseline; future decomposition needs an explicit reconciler/verifier.
- Artifacts: `experiments/exectv2_hybrid_diagnosis_decomposer_v01_dev140_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_diagnosis_decomposer_v01_dev140_gpt41mini_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_decomposer_v01_dev140_report_2026-06-18.md`.

### `exectv2_hybrid_diagnosis_acceptance_gate_v01_dev25_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `25` rows.
- Pipeline: `exectv2_hybrid_diagnosis_acceptance_gate`; mode `live`; replay `native_run_split`.
- Model role: Diagnosis accept/reject gate v0.1 over fixed verifier v0.6 and decomposer v0.1 Diagnosis candidates. The model only accepts or rejects candidate IDs; deterministic code renders accepted candidates.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `fixed candidate rendering + neutral schema repair + benchmark CUI projection only; model owns accept/reject decisions but cannot invent mentions`.
- Primary metrics: accepted_candidates=42, candidate_mentions=87, diagnosis_f1=0.625, diagnosis_precision=0.698, diagnosis_recall=0.566, evidence_validity_rate=1.0, parse_failures=0, prompt_version=exectv2_hybrid_diagnosis_acceptance_gate_v0.1.
- Evidence validity: 0 call failures, 0 parse failures; 42/42 evidence-valid rendered mentions.
- Cache/reuse source: Uses saved Diagnosis verifier v0.6 and Diagnosis decomposer v0.1 dev140 artifacts as candidate inputs, restricted to the first 25 dev letters for this pilot.
- Claim language: Reject before dev140. The constrained gate is clean but too conservative on dev25 (0.625 F1, recall 0.566), so a full dev140 run is not justified. Next gate needs named seizure-type recovery rather than a broad frequency-only rejection rule.
- Artifacts: `experiments/exectv2_hybrid_diagnosis_acceptance_gate_v01_dev25_gpt41mini_20260618.jsonl`, `experiments/exectv2_hybrid_diagnosis_acceptance_gate_v01_dev25_gpt41mini_20260618.md`, `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_acceptance_gate_v01_pilot_report_2026-06-18.md`.

### `gan2026_kg_family_gated_graph_trust_2026-06-16`
- Date/split: `2026-06-16`; `validation`; `250` rows.
- Pipeline: `hybrid_clinical_frequency_state_graph`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: C7 P2.5 family-gated graph-trust posture. Recomputes dual-validation/resolve deterministically from the frozen Stage D graphs and scores a corroboration-free, forward-observable family gate (withholding graph_kind + no admitted quantified node) against the v0.9 selected baseline, alongside P1/P2/P3. No model calls and no holdout rows are read.; model `none`.
- Registry roles: `negative_attribution`.
- Repair mode/config: `state_graph_family_gated_graph_trust_p2_5_v1`.
- Primary metrics: p2_5_correct_to_wrong=121, p2_5_gap_robust=0, p2_5_genuine_rate_regressions=121, p2_5_harvested_minted_residual=7, p2_5_net_purist_gain=-113, p2_5_overrides=149, p2_5_wrong_to_correct=8, rows=250, v09_selected_purist_correct=238.
- Evidence validity: Validation-only no-call replay over the frozen Stage D predeclared 250-row residual-inclusive slice. Graphs reused from the Stage D graphs artifact; dual-validation/resolve recomputed deterministically (no model calls). v0.9 components/baseline from the Stage D rows artifact; gold used only for post-hoc Purist scoring and an honest discriminability probe. No holdout rows.
- Cache/reuse source: stage_d_graphs:gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_graphs.jsonl;stage_d_rows:gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_rows.jsonl.
- Claim language: Tests whether a corroboration-free family-gated graph-trust posture (P2.5) can harvest the 7 minted residual rows without re-introducing P3 genuine-rate regressions. Not a holdout-facing candidate. A reject means no forward-observable family gate separates the harvest set from the genuine-rate casualties; test450 stays locked.
- Artifacts: `experiments/gan2026_kg_family_gated_graph_trust_2026-06-16.json`, `experiments/gan2026_kg_family_gated_graph_trust_2026-06-16.md`, `experiments/gan2026_kg_family_gated_graph_trust_predeclaration_2026-06-16.md`.

### `gan2026_fresh_evidence_v0_12_gpt_deepseek_validation750_live_gpt41_2026-06-16`
- Date/split: `2026-06-16`; `validation`; `750` rows.
- Pipeline: `fresh_evidence_reasoner`; mode `live`; replay `live`.
- Model role: A4 two-model fresh-evidence reasoner (v0_12, GPT+deepseek) live on validation750; third model dropped; v0.4 3-agent baseline for comparison; held-out-family CV.; model `openai/gpt-4.1`.
- Repair mode/config: `v0_12_two_model_gpt_deepseek`.
- Primary metrics: a4_purist=631, baseline_purist=682, gap_robust=False, genuine_rate_regressions=67, gpt_only_purist=661, net_vs_baseline=-51, reasoner_net_vs_gpt=-30.
- Evidence validity: validation750 development split (gan2026_split_v1), NOT a holdout or test450 result. Live openai/gpt-4.1 (synonymous with gpt-4.1-mini), temperature 0; DeepSeek peer trace is a saved artifact. Family CV is within-validation leave-one-band-out.
- Cache/reuse source: experiments\gan2026_fresh_evidence_v0_12_gpt_deepseek_validation750_live_gpt41_2026-06-16.jsonl.
- Claim language: A4 two-model rung, run for information. Within-tolerance + gap_robust is necessary, NOT sufficient, for any test450 authorisation.
- Artifacts: `experiments/gan2026_fresh_evidence_v0_12_gpt_deepseek_validation750_live_gpt41_2026-06-16.json`, `experiments/gan2026_fresh_evidence_v0_12_gpt_deepseek_validation750_live_gpt41_2026-06-16.md`, `experiments/gan2026_fresh_evidence_v0_12_gpt_deepseek_validation750_live_gpt41_2026-06-16.jsonl`.

### `gan2026_fresh_evidence_v0_11_gpt_only_validation750_live_gpt41_2026-06-16`
- Date/split: `2026-06-16`; `validation`; `750` rows.
- Pipeline: `fresh_evidence_reasoner`; mode `live`; replay `live`.
- Model role: A3 GPT-trace-only fresh-evidence reasoner (v0_11) live on validation750; Qwen + DeepSeek dropped from prompt; v0.4 3-agent baseline for comparison; held-out-family CV.; model `openai/gpt-4.1`.
- Repair mode/config: `v0_11_gpt_only_prompt`.
- Primary metrics: a3_purist=610, baseline_purist=682, gap_robust=False, genuine_rate_regressions=89, gpt_only_purist=661, net_vs_baseline=-72, reasoner_net_vs_gpt=-51.
- Evidence validity: validation750 development split (gan2026_split_v1), NOT a holdout or test450 result. Live openai/gpt-4.1 (synonymous with gpt-4.1-mini), temperature 0. Family CV is within-validation leave-one-band-out.
- Cache/reuse source: experiments\gan2026_fresh_evidence_v0_11_gpt_only_validation750_live_gpt41_2026-06-16.jsonl.
- Claim language: A3 simplest-architecture rung. Within-tolerance + gap_robust is necessary, NOT sufficient, for test450 authorisation; the robustness battery gate sits between this and any holdout run.
- Artifacts: `experiments/gan2026_fresh_evidence_v0_11_gpt_only_validation750_live_gpt41_2026-06-16.json`, `experiments/gan2026_fresh_evidence_v0_11_gpt_only_validation750_live_gpt41_2026-06-16.md`, `experiments/gan2026_fresh_evidence_v0_11_gpt_only_validation750_live_gpt41_2026-06-16.jsonl`.

### `gan2026_fresh_evidence_triage_v0_10_validation750_live_gpt41_2026-06-16`
- Date/split: `2026-06-16`; `validation`; `750` rows.
- Pipeline: `fresh_evidence_reasoner`; mode `live`; replay `live`.
- Model role: Fresh-evidence reasoner v0.10 triage scaffold (Cycle C5) live on validation750; v0.4 baseline for comparison; held-out-family CV.; model `openai/gpt-4.1`.
- Repair mode/config: `v0_10_confidence_gated_triage_scaffold`.
- Primary metrics: aggregate_net_purist_gain=-81, correct_to_wrong_vs_v04=95, gap_robust=False, genuine_rate_regressions=73, net_purist_vs_v04=-81, no_correct_rows_flipped_correct=4, v010_purist=601, v04_baseline_purist=682, wrong_to_correct_vs_v04=14.
- Evidence validity: validation750 development split (gan2026_split_v1), NOT a holdout or test450 result. Live openai/gpt-4.1 (synonymous with gpt-4.1-mini per predeclaration), temperature 0. Family CV is within-validation leave-one-boundary-band-out; gap_robust is a promotion-stability estimate, not a test450 number.
- Cache/reuse source: experiments\gan2026_fresh_evidence_triage_v0_10_validation750_live_gpt41_2026-06-16.jsonl.
- Supersedes: `gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13`.
- Claim language: Cycle C5 confidence-gated triage scaffold fresh-evidence reasoner v0.10. gap_robust + non-negative net is necessary, NOT sufficient, for test450 authorisation. Not a holdout result. Stop rule: reject if net < 0 or not gap_robust or genuine-rate regressions > 0.
- Artifacts: `experiments/gan2026_fresh_evidence_triage_v0_10_validation750_live_gpt41_2026-06-16.json`, `experiments/gan2026_fresh_evidence_triage_v0_10_validation750_live_gpt41_2026-06-16.md`, `experiments/gan2026_fresh_evidence_triage_v0_10_validation750_live_gpt41_2026-06-16.jsonl`.

### `gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15`
- Date/split: `2026-06-15`; `test`; `450` rows.
- Pipeline: `fresh_evidence_reasoner`; mode `live`; replay `live`.
- Model role: V12 LLM-owned fresh-evidence reviewer over saved GPT/Qwen/DeepSeek structured-event scaffolding; the model may keep the original GPT structured-event final or replace it with a direct label grounded in exact raw-note evidence. Deterministic code limited to prompt assembly, schema/format repair, exact-substring evidence filtering, predeclared safety gates, rendering, and scoring.; model `openai/gpt-4.1`.
- Registry roles: `holdout_anchor`, `negative_attribution`.
- Repair mode/config: `format_only_repair_plus_predeclared_safety_gates`.
- Primary metrics: call_failures=0, changed_label_precision_vs_v0=0.2205, changed_labels_vs_v0=127, correct_to_wrong_vs_v0=42, evidence_exact_substrings=423, final_pragmatic_correct=362, final_purist_correct=351, format_only_pragmatic_correct=357, format_only_purist_correct=349, fresh_evidence_gate_fallbacks=6, fresh_evidence_replace_actions=157, model_calls_attempted=450, net_purist_gain_vs_v0=-14, parse_or_validation_failures=0, pragmatic_accuracy=0.8044, prediction_bearing_rows=449, prompt_version=gan2026_fresh_evidence_reasoner_v0_6, purist_accuracy=0.78, raw_model_pragmatic_correct=357, raw_model_purist_correct=349, rows=450, safety_gate_version=gan2026_fresh_evidence_safety_gate_v0_9, target_purist_correct=383, target_reached=False, v0_pragmatic_correct=381, v0_purist_correct=364, wrong_to_correct_vs_v0=28.
- Evidence validity: 450/450 rows ran with 0 call failures and 0 parse/schema/label failures; 423/450 final decisions cite exact raw-note evidence substrings after filtering; 449 prediction-bearing rows.
- Cache/reuse source: Saved test450 GPT/Qwen/DeepSeek structured-event artifacts used only as prompt scaffolding; no gold labels, row IDs, split labels, or deterministic top labels provided to the model.
- Claim language: User-authorized (2026-06-15) frozen aggregate-only test450 holdout of V12 fresh_evidence_reasoner prompt v0.6 + safety gate v0.9 in its current reverted form; v0.6 had never been run on test450. Preflight passed ok=true after recomputing the drifted fresh_evidence_reasoner.py and test hashes to match the working tree. Final-evaluation evidence only: final Purist 351/450 is below the 383/450 target and below the V0 baseline 364/450 (net -14). Per the frozen stop rule, no row-level holdout failures were inspected and any follow-up must start as a new validation-only candidate. v0.4 (379/450) remains the best comparator; v0.6/safety-v0.9 is a measured-and-rejected holdout config.
- Artifacts: `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl`, `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.md`.

### `gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15`
- Date/split: `2026-06-15`; `validation`; `750` rows.
- Pipeline: `consensus_fresh_agreement_selector_component_repair_probe`; mode `no-call replay`; replay `saved_output_replay`.
- Model role: Validation-only no-call component-repair probe over saved v0.9 selector rows; no model calls and no holdout rows are read.; model `none`.
- Repair mode/config: `deterministic_last_event_to_unknown_component_probe`.
- Primary metrics: baseline_selected_purist_correct=733, best_probe_delta_selected_purist_correct=0, best_probe_selected_purist_correct=733, rules_tested=3.
- Evidence validity: Validation-only saved-output replay. Gold labels are used only for post-hoc scoring and transition accounting; no holdout rows are read.
- Cache/reuse source: C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl.
- Supersedes: `gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15`.
- Claim language: Rejects broad deterministic last-event-to-unknown component repair as validation-negative or non-improving. Supports a model-owned ambiguity-classification redesign instead.
- Artifacts: `experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.json`, `experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.md`.

### `gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13`
- Date/split: `2026-06-14`; `test`; `450` rows.
- Pipeline: `fresh_evidence_reasoner`; mode `live`; replay `live`.
- Model role: V12 LLM-owned fresh-evidence reviewer over frozen GPT/Qwen test450 structured-event scaffolding; DeepSeek test source unavailable; model may keep the original GPT structured-event final or replace it with exact raw-note evidence.; model `openai/gpt-4.1`.
- Repair mode/config: `format-only label repair, exact-substring evidence filtering, and predeclared safety gates; fallback only to the original GPT structured-event LLM final, not deterministic top.`.
- Primary metrics: authorization_date=2026-06-14, call_failures=0, changed_label_precision_vs_v0=0.3171, changed_labels_vs_v0=82, correct_to_wrong_vs_v0=13, evidence_exact_substrings=423, final_pragmatic_correct=394, final_pragmatic_rate=0.8755555555555555, final_purist_correct=379, final_purist_rate=0.8422222222222222, format_only_pragmatic_correct=387, format_only_purist_correct=372, fresh_evidence_gate_fallbacks=9, fresh_evidence_keep_original_actions=332, fresh_evidence_replace_actions=118, model_calls_attempted=450, net_purist_gain_vs_v0=13, parse_or_validation_failures=0, prediction_bearing_rows=450, raw_model_pragmatic_correct=387, raw_model_purist_correct=372, row_level_holdout_inspection=no, rows=450, target_purist_correct=383, target_purist_rate=0.8511111111111112, target_reached=false, v0_pragmatic_correct=381, v0_purist_correct=364, wrong_to_correct_vs_v0=26.
- Evidence validity: Aggregate-only frozen test readout: 423/450 final decisions cite exact raw-note evidence substrings after filtering; 0 call failures and 0 parse/schema/label failures. First readout used the pinned aggregate-only Markdown helper; no row-level holdout failures, rationales, evidence, selected events, or transitions were inspected.
- Cache/reuse source: Frozen split-aware test sources: GPT structured-event test450 artifact and Qwen patched structured-event test450 artifact; no source overrides.
- Supersedes: `gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13`.
- Claim language: Explicitly authorized frozen aggregate-only test450 audit. Final Purist 379/450 (0.8422) missed the preregistered 383/450 target, so the >0.85 goal is not achieved. Treat as final-evaluation evidence; any follow-up must start from validation only and must not tune from test row-level data.
- Artifacts: `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl`, `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md`, `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.stdout.txt`, `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.stderr.txt`.

### `gan2026_temporal_sentinel_specialist_v0_3_validation_ladder_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `475` rows.
- Pipeline: `temporal_sentinel_specialist`; mode `live`; replay `live`.
- Model role: V9 temporal/sentinel specialist over saved GPT-4.1-mini pure structured-event V0 rows; the model owns keep-or-replace actions, while deterministic code renders model-selected existing normalized events and applies a high-precision safety gate back to the original LLM structured-event final when a proposed replacement falls outside predeclared safe patterns.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `action-rendered keep_original_structured_event_final or replace_with_existing_event only; prompt version gan2026_temporal_sentinel_specialist_v0_1 plus safety gate gan2026_temporal_sentinel_safety_gate_v0_2; no deterministic top, no free recomputation, fallback only to original LLM structured-event final`.
- Primary metrics: hard50_changed_label_precision_vs_v0=1.0, hard50_correct_to_wrong_vs_v0=0, hard50_final_purist_correct=42, hard50_net_purist_gain_vs_v0=3, hard50_v0_purist_correct=39, hard50_wrong_to_correct_vs_v0=3, seizure_free_last_event_final_purist_correct_raw_v0_2_slice=18, seizure_free_last_event_final_purist_correct_safety_replay=16, seizure_free_last_event_v0_purist_correct=15, unknown_no_reference_final_purist_correct_raw_v0_2_slice=36, unknown_no_reference_final_purist_correct_safety_replay=35, unknown_no_reference_v0_purist_correct=34, validation250_changed_label_precision_vs_v0=1.0, validation250_correct_to_wrong_vs_v0=0, validation250_final_purist_correct=237, validation250_net_purist_gain_vs_v0=1, validation250_parse_or_validation_failures=2, validation250_v0_purist_correct=236, validation250_wrong_to_correct_vs_v0=1, validation25_final_purist_correct=25, validation25_v0_purist_correct=25.
- Evidence validity: validation25 exact evidence 24/25; hard50 exact evidence 48/50; validation250 exact evidence 239/250. The two validation250 parse failures are rows missing the structured-event substrate/original final, not safety-gate regressions.
- Cache/reuse source: Input substrate: experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl; fixed hard50 source rows and Stage 0 temporal/sentinel validation50 family slices. v0.3 validation250 reused cached v0.1 prompt outputs with a stricter safety gate.
- Supersedes: `gan2026_represented_event_normalizer_v0_2_validation_ladder_2026-06-13`.
- Claim language: Validation-development V9 diagnostic. The specialist plus safety gate is safe and useful on fixed hard50 (+3 net, 0 regressions), but validation250 transfer is only +1 net and misses the predeclared +5 validation250 gate. Do not escalate to validation750 or frozen test450; use the result as evidence that high-precision original-LLM fallback gates are safer than free recomputation, but too weak for the >0.85 test objective.
- Artifacts: `experiments/gan2026_temporal_sentinel_specialist_validation25_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_temporal_sentinel_specialist_validation25_live_gpt41mini_v0_3_2026-06-13.md`, `experiments/gan2026_temporal_sentinel_specialist_hard50_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_temporal_sentinel_specialist_hard50_live_gpt41mini_v0_3_2026-06-13.md`, `experiments/gan2026_temporal_sentinel_specialist_unknown_no_reference_validation50_live_gpt41mini_v0_2_2026-06-13.jsonl`, `experiments/gan2026_temporal_sentinel_specialist_unknown_no_reference_validation50_live_gpt41mini_v0_2_2026-06-13.md`, `experiments/gan2026_temporal_sentinel_specialist_seizure_free_last_event_validation50_live_gpt41mini_v0_2_2026-06-13.jsonl`, `experiments/gan2026_temporal_sentinel_specialist_seizure_free_last_event_validation50_live_gpt41mini_v0_2_2026-06-13.md`, `experiments/gan2026_temporal_sentinel_specialist_validation250_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_temporal_sentinel_specialist_validation250_live_gpt41mini_v0_3_2026-06-13.md`.

### `gan2026_targeted_boundary_router_validation_ladder_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `150` rows.
- Pipeline: `targeted_boundary_router`; mode `live`; replay `live`.
- Model role: V3 targeted boundary router over saved GPT-4.1-mini pure structured-event V0 rows; the model owns keep-or-replace action and routed profile, while deterministic code renders only the model-selected existing normalized structured-event candidate and scores afterward.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `action-rendered keep_original_structured_event_final or replace_with_existing_event only; no deterministic top or final-label fallback; v0.4 adds split-neutral router_hints diagnostics but still requires model-owned action`.
- Primary metrics: v0_1_hard50_changed_label_precision_vs_v0=0.5, v0_1_hard50_correct_to_wrong_vs_v0=2, v0_1_hard50_final_purist_correct=40, v0_1_hard50_wrong_to_correct_vs_v0=3, v0_2_hard50_changed_label_precision_vs_v0=1.0, v0_2_hard50_final_purist_correct=40, v0_2_hard50_net_purist_gain_vs_v0=1, v0_2_validation25_final_purist_correct=25, v0_4_hard50_correct_to_wrong_vs_v0=1, v0_4_hard50_final_purist_correct=39, v0_4_hard50_wrong_to_correct_vs_v0=1.
- Evidence validity: All recorded router variants had 0 parse/action-render failures. v0.2 validation25 exact evidence 24/25 and hard50 exact evidence 46/50; v0.4 validation25 exact evidence 24/25 and hard50 exact evidence 46/50.
- Cache/reuse source: Input substrate: experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl. v0.1-v0.4 prompt variants were run on validation25 and fixed hard50 only; v0.2 was the safest variant, v0.4 added split-neutral router hints but did not improve the gate.
- Supersedes: `gan2026_structured_event_verifier_v0_5_validation_ladder_2026-06-13`.
- Claim language: Validation-development V3 targeted-router attempt. The implementation is auditable and LLM-owned over saved structured-event rows, but no variant passed the Stage 2 gate. v0.1 found 3 hard50 wins but also 2 losses (changed-label precision 0.50); v0.2 was safe but weak at +1 net; v0.3 made no label changes; v0.4 with router_hints regressed to V0 parity with one win and one loss. Do not escalate this branch to validation250, validation750, or holdout.
- Artifacts: `experiments/gan2026_targeted_boundary_router_validation25_live_gpt41mini_v0_2_2026-06-13.jsonl`, `experiments/gan2026_targeted_boundary_router_validation25_live_gpt41mini_v0_2_2026-06-13.md`, `experiments/gan2026_targeted_boundary_router_hard50_live_gpt41mini_v0_2_2026-06-13.jsonl`, `experiments/gan2026_targeted_boundary_router_hard50_live_gpt41mini_v0_2_2026-06-13.md`, `experiments/gan2026_targeted_boundary_router_validation25_live_gpt41mini_v0_4_2026-06-13.jsonl`, `experiments/gan2026_targeted_boundary_router_validation25_live_gpt41mini_v0_4_2026-06-13.md`, `experiments/gan2026_targeted_boundary_router_hard50_live_gpt41mini_v0_4_2026-06-13.jsonl`, `experiments/gan2026_targeted_boundary_router_hard50_live_gpt41mini_v0_4_2026-06-13.md`.

### `gan2026_structured_event_verifier_v0_5_validation_ladder_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `175` rows.
- Pipeline: `structured_event_verifier`; mode `live`; replay `live`.
- Model role: V4 structured-event verifier over saved GPT-4.1-mini pure structured-event V0 rows; the model owns an explicit keep-or-replace action, while deterministic code renders only the model-selected action against existing normalized structured-event candidates and scores afterward.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `action-rendered keep_original_structured_event_final or replace_with_existing_event only; free recomputation and abstention disabled in prompt v0.5; format-only label repair recorded as a separate score layer`.
- Primary metrics: frequency_denominator_final_purist_correct=8, frequency_denominator_net_purist_gain_vs_v0=1, frequency_denominator_v0_purist_correct=7, hard50_changed_label_precision_vs_v0=1.0, hard50_final_purist_correct=40, hard50_net_purist_gain_vs_v0=1, hard50_v0_purist_correct=39, unknown_no_reference_final_purist_correct=34, unknown_no_reference_net_purist_gain_vs_v0=0, unknown_no_reference_v0_purist_correct=34, validation25_final_purist_correct=25, validation25_v0_purist_correct=25.
- Evidence validity: validation25 exact evidence 24/25; hard50 exact evidence 46/50; frequency_denominator validation50 exact evidence 46/50; unknown_no_reference validation50 exact evidence 44/50. All runs had 0 parse/action-render failures.
- Cache/reuse source: Input substrate: experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl. Prompt iterations v0.1-v0.4 were used only to harden the v0.5 contract before this recorded ladder.
- Supersedes: `gan2026_llm_event_reasoner_hard50_live_gpt41mini_v1_3_2026-06-13`.
- Claim language: Validation-development V4 verifier-first attempt. v0.5 is safe where it acts (hard50 +1 net, 1.0 changed-label precision, 0 losses; frequency-denominator slice +1 net, 0 losses) but far below the predeclared +4 hard50 and +5 validation250 promotion gates. Do not escalate this branch to validation250, validation750, or holdout; next work should use a different specialist/selector rather than free recomputation.
- Artifacts: `experiments/gan2026_structured_event_verifier_validation25_live_gpt41mini_v0_5_2026-06-13.jsonl`, `experiments/gan2026_structured_event_verifier_validation25_live_gpt41mini_v0_5_2026-06-13.md`, `experiments/gan2026_structured_event_verifier_hard50_live_gpt41mini_v0_5_2026-06-13.jsonl`, `experiments/gan2026_structured_event_verifier_hard50_live_gpt41mini_v0_5_2026-06-13.md`, `experiments/gan2026_structured_event_verifier_frequency_denominator_validation50_live_gpt41mini_v0_5_2026-06-13.jsonl`, `experiments/gan2026_structured_event_verifier_frequency_denominator_validation50_live_gpt41mini_v0_5_2026-06-13.md`, `experiments/gan2026_structured_event_verifier_unknown_no_reference_validation50_live_gpt41mini_v0_5_2026-06-13.jsonl`, `experiments/gan2026_structured_event_verifier_unknown_no_reference_validation50_live_gpt41mini_v0_5_2026-06-13.md`.

### `gan2026_represented_event_normalizer_v0_2_validation_ladder_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `75` rows.
- Pipeline: `represented_event_normalizer`; mode `live`; replay `live`.
- Model role: V8 represented-event normalizer over saved GPT-4.1-mini pure structured-event V0 rows; the model owns keep-or-recompute action over selected existing event evidence, while deterministic code validates membership, format, evidence substrings, and scoring afterward.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `action-rendered keep_original_structured_event_final or replace_with_recomputed_fact_from_selected_evidence only; replace_with_existing_event disabled in prompt v0.2 after v0.1 caused a saturated validation25 regression; recompute requires selected existing event IDs and a scorable model label`.
- Primary metrics: all_recorded_action_render_failures=0, all_recorded_parse_or_validation_failures=0, hard50_changed_label_precision_vs_v0=0.0, hard50_correct_to_wrong_vs_v0=1, hard50_final_purist_correct=38, hard50_net_purist_gain_vs_v0=-1, hard50_recomputed_fact_actions=3, hard50_v0_purist_correct=39, hard50_wrong_to_correct_vs_v0=0, validation25_final_purist_correct=25, validation25_recomputed_fact_actions=1, validation25_v0_purist_correct=25.
- Evidence validity: validation25 exact evidence 24/25; hard50 exact evidence 46/50. Both recorded v0.2 runs had 0 call failures, 0 parse/schema/action-render failures.
- Cache/reuse source: Input substrate: experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl; fixed hard50 source rows from experiments/gan2026_agentic_validation_hard50_source_rows_2026-06-12.txt.
- Supersedes: `gan2026_event_completion_reasoner_v0_3_validation_ladder_2026-06-13`.
- Claim language: Validation-development V8 diagnostic. The represented-event recompute contract is clean, but fixed hard50 regressed from V0 39/50 to 38/50: 3 recompute actions, 0 wins, and 1 regression, mainly from over-selecting seizure-free evidence. Do not escalate to family slices, validation250, validation750, or holdout. Next work should use a more explicit specialist gate rather than free recomputation.
- Artifacts: `experiments/gan2026_represented_event_normalizer_validation25_live_gpt41mini_v0_2_2026-06-13.jsonl`, `experiments/gan2026_represented_event_normalizer_validation25_live_gpt41mini_v0_2_2026-06-13.md`, `experiments/gan2026_represented_event_normalizer_hard50_live_gpt41mini_v0_2_2026-06-13.jsonl`, `experiments/gan2026_represented_event_normalizer_hard50_live_gpt41mini_v0_2_2026-06-13.md`.

### `gan2026_llm_event_reasoner_hard50_live_gpt41mini_v1_3_2026-06-13`
- Date/split: `2026-06-13`; `validation_hard50`; `50` rows.
- Pipeline: `llm_event_reasoner`; mode `live`; replay `live`.
- Model role: V1 single LLM-owned event reasoner over saved GPT structured-event V0 on the fixed validation hard50 source-row file.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `format-only label repair plus enum/shape schema repair; no semantic fallback`.
- Primary metrics: call_failures=0, changed_label_precision_vs_v0=0.0769, correct_to_wrong_vs_v0=5, evidence_exact_substrings=46, final_purist_correct=35, format_only_purist_correct=35, model_calls_attempted=50, net_purist_gain_vs_v0=-4, parse_or_validation_failures=0, raw_model_purist_correct=35, rows=50, v0_purist_correct=39, wrong_to_correct_vs_v0=1.
- Evidence validity: 46/50 final decisions cited exact evidence substrings; evidence quality did not prevent semantic regressions on seizure-free boundaries.
- Cache/reuse source: Structured-event source: experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl; source rows: experiments/gan2026_agentic_validation_hard50_source_rows_2026-06-12.txt.
- Supersedes: `gan2026_llm_event_reasoner_hard50_live_gpt41mini_v1_2_2026-06-13`.
- Claim language: Validation-development fixed hard50 rejection. v1.3 regressed from V0 39/50 Purist to 35/50, so V1 free second-pass reasoning is blocked from family-slice, validation250, validation750, or holdout escalation.
- Artifacts: `experiments/gan2026_llm_event_reasoner_hard50_live_gpt41mini_v1_3_2026-06-13.jsonl`, `experiments/gan2026_llm_event_reasoner_hard50_live_gpt41mini_v1_3_2026-06-13.md`.

### `gan2026_event_completion_reasoner_v0_3_validation_ladder_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `275` rows.
- Pipeline: `event_completion_reasoner`; mode `live`; replay `live`.
- Model role: V7 event-completion reasoner over saved GPT-4.1-mini pure structured-event V0 rows; the model owns an explicit keep-or-create action, while deterministic code renders only the model-selected action and scores afterward.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `action-rendered keep_original_structured_event_final or create_completed_event_final only; keep ignores irrelevant completed_event payloads, create requires completed_event_1 and a scorable model label; format-only label repair recorded as a separate score layer`.
- Primary metrics: all_recorded_action_render_failures=0, all_recorded_completed_event_actions=0, all_recorded_parse_or_validation_failures=0, cluster_axis_final_purist_correct=7, cluster_axis_v0_purist_correct=7, frequency_denominator_final_purist_correct=7, frequency_denominator_v0_purist_correct=7, hard50_final_purist_correct=39, hard50_net_purist_gain_vs_v0=0, hard50_v0_purist_correct=39, multi_semiology_burden_final_purist_correct=7, multi_semiology_burden_v0_purist_correct=7, seizure_free_last_event_final_purist_correct=15, seizure_free_last_event_v0_purist_correct=15, validation25_final_purist_correct=25, validation25_v0_purist_correct=25.
- Evidence validity: validation25 exact evidence 24/25; hard50 exact evidence 46/50; seizure_free_last_event 45/50; frequency_denominator 46/50; cluster_axis 46/50; multi_semiology_burden 46/50. All recorded runs had 0 call failures, 0 parse/schema/action-render failures, and 0 completed-event actions.
- Cache/reuse source: Input substrate: experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl. Family source-row files from Stage 0 validation-only manifests.
- Supersedes: `gan2026_targeted_boundary_router_validation_ladder_2026-06-13`.
- Claim language: Validation-development V7 diagnostic. The contract is clean and safe, but the strict event-absence framing produced no create actions on hard50 or the four omission-heavy family slices, so it cannot clear the Stage 2 gate or support validation250, validation750, or holdout escalation. The result suggests many misses are represented in the event table but not normalized/selected correctly, rather than literally absent from the extracted events.
- Artifacts: `experiments/gan2026_event_completion_reasoner_validation25_live_gpt41mini_v0_3b_2026-06-13.jsonl`, `experiments/gan2026_event_completion_reasoner_validation25_live_gpt41mini_v0_3b_2026-06-13.md`, `experiments/gan2026_event_completion_reasoner_hard50_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_event_completion_reasoner_hard50_live_gpt41mini_v0_3_2026-06-13.md`, `experiments/gan2026_event_completion_reasoner_seizure_free_last_event_validation50_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_event_completion_reasoner_seizure_free_last_event_validation50_live_gpt41mini_v0_3_2026-06-13.md`, `experiments/gan2026_event_completion_reasoner_frequency_denominator_validation50_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_event_completion_reasoner_frequency_denominator_validation50_live_gpt41mini_v0_3_2026-06-13.md`, `experiments/gan2026_event_completion_reasoner_cluster_axis_validation50_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_event_completion_reasoner_cluster_axis_validation50_live_gpt41mini_v0_3_2026-06-13.md`, `experiments/gan2026_event_completion_reasoner_multi_semiology_burden_validation50_live_gpt41mini_v0_3_2026-06-13.jsonl`, `experiments/gan2026_event_completion_reasoner_multi_semiology_burden_validation50_live_gpt41mini_v0_3_2026-06-13.md`.

### `gan2026_cross_model_structured_event_adjudicator_v0_4_validation_ladder_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `75` rows.
- Pipeline: `cross_model_structured_event_adjudicator`; mode `live`; replay `live`.
- Model role: V10 cross-model structured-event adjudicator over saved GPT, Qwen, and DeepSeek structured-event finals; the model owns selected-agent action choice while deterministic code renders the selected saved final.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `selected saved-agent final with high-precision peer-selection gate; fallback only to original GPT structured-event final; no deterministic top or final-label fallback`.
- Primary metrics: all_recorded_action_render_failures=0, all_recorded_parse_or_validation_failures=0, hard50_correct_to_wrong_vs_v0=0, hard50_final_purist_correct=40, hard50_net_purist_gain_vs_v0=1, hard50_v0_purist_correct=39, hard50_wrong_to_correct_vs_v0=1, validation25_final_purist_correct=25, validation25_v0_purist_correct=25.
- Evidence validity: validation25 and fixed hard50 had 0 parse/schema/action-render failures; evidence and selected-agent traces are recorded in the run artifacts.
- Cache/reuse source: Saved GPT/Qwen/DeepSeek validation structured-event artifacts plus validation25 and fixed hard50 source rows.
- Supersedes: `gan2026_temporal_sentinel_specialist_v0_3_validation_ladder_2026-06-13`.
- Claim language: Validation-development V10 diagnostic only. The high-precision peer gate is safe but too weak: fixed hard50 improves by only +1, below the +4 gate, so do not escalate to validation250, validation750, or holdout.
- Artifacts: `experiments/gan2026_cross_model_structured_event_adjudicator_validation25_live_gpt41mini_v0_4_2026-06-13.jsonl`, `experiments/gan2026_cross_model_structured_event_adjudicator_validation25_live_gpt41mini_v0_4_2026-06-13.md`, `experiments/gan2026_cross_model_structured_event_adjudicator_hard50_live_gpt41mini_v0_4_2026-06-13.jsonl`, `experiments/gan2026_cross_model_structured_event_adjudicator_hard50_live_gpt41mini_v0_4_2026-06-13.md`.

### `gan2026_cross_model_challenge_gated_adjudicator_v0_1_validation_ladder_2026-06-13`
- Date/split: `2026-06-13`; `validation`; `325` rows.
- Pipeline: `cross_model_challenge_adjudicator`; mode `live plus no-call validation250 upper-bound diagnostic`; replay `live`.
- Model role: V11 cross-model peer challenge adjudicator over saved GPT, Qwen, and DeepSeek structured-event finals; the model challenges agent disagreements and selects a saved agent final, with deterministic code limited to rendering, evidence validation, scoring, and the high-precision gate.; model `openai/gpt-4.1`.
- Repair mode/config: `model-owned selected-agent action with high-precision peer gate; fallback only to original GPT structured-event final; escaped-list-item quote JSON dialect repair; no deterministic top or final-label fallback`.
- Primary metrics: all_recorded_action_render_failures=0, all_recorded_parse_or_validation_failures=0, cluster_axis_final_purist_correct=8, cluster_axis_v0_purist_correct=7, frequency_denominator_final_purist_correct=8, frequency_denominator_v0_purist_correct=7, hard50_correct_to_wrong_vs_v0=0, hard50_final_purist_correct=41, hard50_net_purist_gain_vs_v0=2, hard50_v0_purist_correct=39, hard50_wrong_to_correct_vs_v0=2, multi_semiology_burden_final_purist_correct=8, multi_semiology_burden_v0_purist_correct=7, seizure_free_last_event_final_purist_correct=16, seizure_free_last_event_v0_purist_correct=15, unknown_no_reference_final_purist_correct=35, unknown_no_reference_v0_purist_correct=34, validation250_prefix_upper_bound_net_gain=2, validation250_prefix_upper_bound_optimistic_purist_correct=238, validation250_prefix_upper_bound_v0_purist_correct=236, validation25_final_purist_correct=25, validation25_v0_purist_correct=25.
- Evidence validity: Gated GPT-4.1 V11: validation25 exact evidence 24/25, hard50 50/50, and each validation50 family slice 49/50; all recorded gated runs had 0 call failures and 0 parse/schema/action-render failures after dialect repair.
- Cache/reuse source: Saved GPT/Qwen/DeepSeek structured-event validation artifacts; live validation25, fixed hard50, and five validation50 family slices. The validation250 prefix value is a no-call upper-bound diagnostic, not a live score.
- Supersedes: `gan2026_cross_model_structured_event_adjudicator_v0_4_validation_ladder_2026-06-13`.
- Claim language: Validation-development V11 diagnostic only. The open challenge prompt found real peer rescues but regressed on seizure-free and GPT-unknown-to-peer-numeric overreach. The high-precision gate removed hard50 regressions and improved five family slices by +1 each, but hard50 +2 misses the +4 gate and the validation250 prefix upper bound is only +2, below the +5 gate; do not escalate to validation250 live, validation750, frozen test450, or benchmark claims.
- Artifacts: `experiments/gan2026_cross_model_challenge_gated_adjudicator_validation25_live_gpt41_v0_1_2026-06-13.jsonl`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_validation25_live_gpt41_v0_1_2026-06-13.md`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_hard50_live_gpt41_v0_1_2026-06-13.jsonl`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_hard50_live_gpt41_v0_1_2026-06-13.md`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_unknown_no_reference_validation50_live_gpt41_v0_1_2026-06-13.jsonl`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_unknown_no_reference_validation50_live_gpt41_v0_1_2026-06-13.md`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_frequency_denominator_validation50_live_gpt41_v0_1_2026-06-13.jsonl`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_frequency_denominator_validation50_live_gpt41_v0_1_2026-06-13.md`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_cluster_axis_validation50_live_gpt41_v0_1_2026-06-13.jsonl`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_cluster_axis_validation50_live_gpt41_v0_1_2026-06-13.md`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_multi_semiology_burden_validation50_live_gpt41_v0_1_2026-06-13.jsonl`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_multi_semiology_burden_validation50_live_gpt41_v0_1_2026-06-13.md`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_seizure_free_last_event_validation50_live_gpt41_v0_1_2026-06-13.jsonl`, `experiments/gan2026_cross_model_challenge_gated_adjudicator_seizure_free_last_event_validation50_live_gpt41_v0_1_2026-06-13.md`.

### `gan2026_agentic_hard50_tool_self_consistency_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_tool_self_consistency`; mode `live`; replay `live`.
- Model role: E2 four-call boundary-guide-only tool self-consistency with deterministic normalized-label voting, compared against saved single_self_consistency_temperature hard50 condition.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `direct-label parser/schema repair + deterministic normalized-label vote`.
- Primary metrics: call_failures=0, decision_records=200, gate_max_losses=2, gate_required_wins=5, holdout_authorized=no, losses_vs_single_self_consistency_temperature=2, model_calls_attempted=200, parse_or_validation_failures=0, pragmatic_correct=35, purist_correct=34, rows=50, wins_vs_single_self_consistency_temperature=4.
- Evidence validity: Prediction-bearing validation hard50 development run: 200/200 decision records, 0 call failures, 0 parse/schema/label failures. Evidence substring metric not computed for this ablation artifact.
- Supersedes: `gan2026_agentic_hard50_tool_context_ablation_2026-06-12`.
- Claim language: Validation-development hard-slice result only. E2 missed the promotion gate by one rescue (4 wins, 2 losses; gate required at least 5 wins and at most 2 losses), so E3 and E4 were not run under the predeclared stop rule.
- Artifacts: `experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl`, `experiments/archive/exectv2_self_consistency_intermediate_notes/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.md`.

### `gan2026_agentic_hard50_selective_fallback_replay_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_selective_fallback_replay`; mode `no_call_replay`; replay `saved_output_replay`.
- Model role: No-call selective fallback replay over saved hard50 matched-budget agentic traces, using single_self_consistency_temperature as fallback comparator.; model `none`.
- Repair mode/config: `saved-output policy replay; no scorer or label repair changes`.
- Primary metrics: all_agree_multi_accept_net_purist_gain=-6, all_agree_tool_accept_net_purist_gain=-12, boundary_coordinator_agree_net_purist_gain=-3, diagnostic_policy_count=1, holdout_authorized=no, promoted_policy_count=0, raw_repair_disagreement_fallback_net_purist_gain=-6, rows=50.
- Evidence validity: No new prediction evidence. Replay uses saved validation hard50 condition traces, final labels, role labels, normalized votes, and manifest slice tags for validation-only analysis.
- Cache/reuse source: experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.jsonl.
- Claim language: Validation-development replay only. No promotable selective fallback policy produced any wrong-to-correct changes; all eligible policies were reject signals, so the branch moved to E1 tool-context ablation rather than new live multi-agent calls.
- Artifacts: `experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.jsonl`, `experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.md`.

### `gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `12` rows.
- Pipeline: `agentic_direct_boundary_critic_rescue`; mode `live_then_saved_output_replay`; replay `saved_output_replay`.
- Model role: D2 two-call direct-plus-boundary-critic rescue-only micro-panel; direct no-tool answer plus fixed boundary-guide critic, parser candidates disabled.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `format-only critic-field shape repair plus existing direct-label repair; parser candidates disabled as prompt context`.
- Primary metrics: accepted_action_regressions=0, accepted_boundary_demotions=0, accepted_rescue_correct=0, changed_label_precision=0.4, changed_labels_vs_reference=5, direct_purist_correct=10, fallback_rate=1.0, hard50_authorized=no, holdout_authorized=no, losses_vs_single_self_consistency_temperature=0, model_calls_attempted=24, panel_gate=reject_or_revise_before_hard50, parse_or_validation_failures=0, pragmatic_correct=10, purist_correct=10, raw_critic_proposed_purist_correct=0, rows=12, schema_or_label_repair_rows=9, wins_vs_single_self_consistency_temperature=2.
- Evidence validity: 24/24 exact evidence substrings after saved-output format repair; no new prediction evidence during replay.
- Cache/reuse source: live raw outputs in experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12.jsonl.
- Claim language: Validation micro-panel development result only. D2 failed the panel gate after format-only repair because the critic accepted 0 rescue actions; do not run D2 hard50, D3, D4, validation250, or holdout from this branch.
- Artifacts: `experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12.jsonl`, `experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12.md`, `experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_format_repair_replay_2026-06-12.jsonl`, `experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_format_repair_replay_2026-06-12.md`.

### `gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12`
- Date/split: `2026-06-12`; `validation`; `50` rows.
- Pipeline: `agentic_boundary_audit_prompt_v2`; mode `live`; replay `live`.
- Model role: D1 one-call boundary-audit prompt v2 over the fixed validation hard50 slice; fixed boundary-guide context only, parser candidates disabled.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `format-only audit-field shape repair plus existing label/evidence repair; parser candidates disabled as prompt context`.
- Primary metrics: boundary_demotion_count=1, call_failures=0, changed_label_precision=0.3636, changed_labels_vs_reference=22, evidence_exact_substrings=35, hard50_gate=reject_or_revise, holdout_authorized=no, losses_vs_single_self_consistency_temperature=2, parse_or_validation_failures=0, pragmatic_correct=38, purist_correct=38, rows=50, schema_or_label_repair_rows=44, wins_vs_single_self_consistency_temperature=8.
- Evidence validity: 35/50 exact evidence substrings. Prediction-bearing hard50 run had 50/50 decision records, 0 call failures, and 0 parse/schema/label failures after format-only audit repair.
- Supersedes: `gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12`.
- Claim language: Validation hard-slice development result only. Despite 8 rescues, D1 missed the hard50 gate because it caused 2 regressions and changed-label precision was 0.3636; do not escalate D1 to validation250, D3, or holdout.
- Artifacts: `experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.jsonl`, `experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.md`.

### `gan2026_llm_heavy_evidence_selection_decision0007_v1_validation25_live_2026-06-03`
- Date/split: `2026-06-03`; `validation`; `25` rows.
- Pipeline: `llm_heavy_evidence_selection_with_deterministic_adapters`; mode `live validation25 Decision 0007 v1 selected-fact and operand contract smoke`; replay `live`.
- Model role: LLM-owned clinical fact, evidence, temporal state, raw parser label, and operands; deterministic code mechanically renders selected operands; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 prompt/schema-only contract: exact Unicode evidence copying, clinical-kind/operand consistency, vague-count guidance, and parser-ready raw-label grammar; scorer, split, adapter, and gate unchanged`.
- Primary metrics: adapter_parse_failures=0, benchmark_convention_adapter_purist_correct=23, call_failures=0, format_only_repair_purist_correct=25, mechanical_adapter_label_pragmatic_correct=24, mechanical_adapter_label_purist_correct=23, mechanical_adapter_raw_correct_to_wrong=2, mechanical_adapter_raw_wrong_to_correct=0, operand_complete_rows=25, raw_model_parser_label_purist_correct=25, raw_model_parser_label_scorable=25, row_count=25, selected_evidence_valid=22, selected_fact_trace_mismatches=0, structured_records=25.
- Evidence validity: Selected evidence exact 22/25; selected fact trace mismatches 0/25. Remaining failures are special-character evidence escaping on rows 10, 40, and 446.
- Cache/reuse source: DSPy cache disabled for the live v1 smoke; no saved raw-output reuse.
- Supersedes: `gan2026_llm_heavy_evidence_selection_decision0007_validation25_contract_triage_2026-06-03`.
- Claim language: Decision 0007 validation25 development smoke only. V1 fixes raw parser-label grammar and operand completeness, but promotion remains rejected because selected evidence exactness is 22/25 and the mechanical adapter regresses two raw-correct cluster-cadence rows.
- Artifacts: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_2026-06-03.jsonl`, `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_2026-06-03.md`.

### `gan2026_llm_only_typed_adapter_reasoner_v0_validation50_diagnostic_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `50` rows.
- Pipeline: `llm_only_typed_adapter_reasoner`; mode `live validation50 typed DSPy JSONAdapter diagnostic plus saved-output row-level error analysis`; replay `cache_first`.
- Model role: LLM-only typed DSPy event extraction, clinical selection, and parser-ready final-label renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `typed DSPy JSONAdapter outputs with raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, and oracle_format_upper_bound layers; deterministic arithmetic and benchmark alignment remain side-cars`.
- Primary metrics: adapter_parse_failures=0, arithmetic_trace_present=38, benchmark_aligned_purist_correct=43, call_failures=0, event_evidence_total=85, event_evidence_valid=79, format_only_purist_correct=45, parse_failures=0, raw_llm_pragmatic_correct=42, raw_llm_purist_correct=42, raw_llm_scorable=45, rendering_operands_present=49, row_count=50, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=49, selected_evidence_arithmetic_purist_correct=49, selected_evidence_arithmetic_raw_wrong_to_correct=7, selected_evidence_valid=45, structured_records=50.
- Evidence validity: Selected evidence exact 45/50; event evidence exact 79/85; selected-event trace mismatches 0/50.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for the validation50 diagnostic. Error analysis reuses the saved validation50 JSONL only.
- Supersedes: `gan2026_llm_only_typed_adapter_reasoner_v0_validation25_live_2026-06-02`.
- Claim language: User-approved validation50 diagnostic after failed validation25 gate. Reject promotion: typed JSONAdapter/schema reliability is strong, but raw model-owned labels, exact selected evidence, and arithmetic traces are not clean enough; selected-evidence arithmetic is a deterministic side-car, not LLM-only success.
- Artifacts: `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_gpt41mini_v0_diagnostic_2026-06-02.jsonl`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_gpt41mini_v0_diagnostic_2026-06-02.md`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.csv`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.json`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.md`.

### `gan2026_llm_only_typed_adapter_reasoner_v0_validation25_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_only_typed_adapter_reasoner`; mode `live validation25 typed DSPy JSONAdapter architecture smoke`; replay `cache_first`.
- Model role: LLM-only typed DSPy event extraction, clinical selection, and parser-ready final-label renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `typed DSPy JSONAdapter outputs with raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, and oracle_format_upper_bound layers; deterministic arithmetic and benchmark alignment are side-cars`.
- Primary metrics: adapter_parse_failures=0, arithmetic_trace_present=17, benchmark_aligned_purist_correct=22, call_failures=0, event_evidence_total=38, event_evidence_valid=31, format_only_purist_correct=24, parse_failures=0, raw_llm_pragmatic_correct=22, raw_llm_purist_correct=22, raw_llm_scorable=22, rendering_operands_present=25, row_count=25, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_arithmetic_raw_wrong_to_correct=3, selected_evidence_valid=19, structured_records=25.
- Evidence validity: Selected evidence exact 19/25; event evidence exact 31/38; selected-event trace mismatches 0/25.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for this typed JSONAdapter smoke.
- Supersedes: `gan2026_dspy_adapter_architecture_report_2026-06-02`.
- Claim language: Typed-adapter LLM-only architecture smoke only. The scoped JSONAdapter and typed DSPy outputs produced 25/25 structured records with no adapter parse failures, but selected evidence exactness, parser-ready raw label rendering, and arithmetic traces miss the validation25 gate; selected-evidence arithmetic remains a deterministic side-car, not LLM-only success.
- Artifacts: `experiments/gan2026_dspy_adapter_architecture_report_2026-06-02.md`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation25 decision-0006 selected-evidence arithmetic/rendering smoke`; replay `cache_first`.
- Model role: LLM-heavy extraction, selected evidence, model-owned arithmetic/rendering, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v2 prompt/schema with model-owned rendering_operands and arithmetic_trace; deterministic selected-evidence arithmetic remains side-car only`.
- Primary metrics: arithmetic_trace_present=22, benchmark_aligned_purist_correct=21, deterministic_arithmetic_raw_wrong_to_correct=0, event_evidence_total=53, event_evidence_valid=51, format_only_purist_correct=21, parse_failures=3, raw_llm_pragmatic_correct=22, raw_llm_purist_correct=21, raw_llm_scorable=22, rendering_operands_present=22, row_count=25, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=22, selected_evidence_arithmetic_purist_correct=21, selected_evidence_valid=22, structured_records=22.
- Evidence validity: Selected evidence exact 22/25; event evidence exact 51/53; selected-event trace mismatches 0/25.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for this v2 prompt run.
- Supersedes: `gan2026_llm_replacement_postprocessing_ablation_validation250_2026-06-02`, `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation250_live_2026-06-02`.
- Claim language: Validation25 development smoke rejects validation50 escalation under decision 0006: raw model-owned Purist is 21/25 with zero deterministic arithmetic gap, but structured/scorable labels, selected evidence exactness, rendering operands, and arithmetic traces are only 22/25.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.md`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `saved-output row-level error analysis of decision-0006 validation25 smoke`; replay `analysis_only`.
- Model role: analysis-only row-level reviewer for v2 validation25 output-contract and label failures; model `none; saved openai/gpt-4.1-mini outputs only`.
- Repair mode/config: `analysis only over raw_llm, format_only, selected_evidence_arithmetic, and benchmark_aligned layers; no scorer/parser/prompt change`.
- Primary metrics: analysis_rows=6, invalid_json_truncation=1, missing_required_final_answer_field=2, nonselected_event_evidence_not_exact=2, raw_llm_purist_correct=21, selected_event_trace_mismatches=0, selected_evidence_arithmetic_purist_correct=21, wrong_selected_fact_or_cluster_semantics=1.
- Evidence validity: Classifies 2 invalid non-selected event-evidence rows; selected-answer evidence failures are attributable to the 3 blocking parse/schema rows.
- Cache/reuse source: experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.jsonl.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_live_2026-06-02`.
- Claim language: Analysis confirms no validation50 escalation: failure is mainly compactness/output contract, with one true cluster-cadence selected-fact/semantics error and zero deterministic-arithmetic rescue gap.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.csv`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.json`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact_validation25_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `25` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation25 compact decision-0006 selected-evidence arithmetic/rendering smoke`; replay `cache_first`.
- Model role: LLM-heavy extraction, selected evidence, compact model-owned arithmetic/rendering, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v2_compact prompt/schema with compact final_answer and model-owned rendering_operands/arithmetic_trace; deterministic selected-evidence arithmetic remains side-car only`.
- Primary metrics: arithmetic_trace_present=24, benchmark_aligned_purist_correct=23, deterministic_arithmetic_raw_wrong_to_correct=3, event_evidence_total=37, event_evidence_valid=35, format_only_purist_correct=22, parse_failures=0, raw_llm_pragmatic_correct=23, raw_llm_purist_correct=22, raw_llm_scorable=23, rendering_operands_present=24, row_count=25, selected_event_trace_mismatches=0, selected_evidence_arithmetic_pragmatic_correct=25, selected_evidence_arithmetic_purist_correct=25, selected_evidence_valid=22, structured_records=25.
- Evidence validity: Selected evidence exact 22/25; event evidence exact 35/37; selected-event trace mismatches 0/25.
- Cache/reuse source: DSPy cache enabled; no saved raw-output reuse for this compact v2 prompt run.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02`.
- Claim language: Validation25 development smoke rejects validation50 escalation under decision 0006. Compact schema fixed the prior truncation/missing-selected-event-id failures with 25/25 structured records, but raw parser compatibility, selected evidence exactness, and model-owned rendering remain below stop rules; selected-evidence arithmetic is a deterministic side-car, not LLM-heavy success.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact_validation25_predeclaration_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.jsonl`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.md`.

### `gan2026_llm_structured_v05_full_validation_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `llm_structured_events`; mode `live/cache-first structured v0.5 full-validation completion`; replay `cache_first`.
- Model role: LLM-first structured event extractor and clinical selector; model `openai/gpt-4.1-mini`.
- Registry roles: `negative_attribution`, `historical_lineage`.
- Repair mode/config: `v0.5 structured-event selector plus large deterministic post-LLM repair stack`.
- Primary metrics: call_failures=0, deterministic_repair_notes=481, exact_selection_evidence_substrings=714, parse_schema_label_issues=0, pragmatic_correct=690, purist_correct=675, row_count=750, structured_records=750.
- Evidence validity: Exact selection evidence substrings 714/750; evidence exactness does not establish final repaired-label attribution.
- Cache/reuse source: Reused 720 raw model outputs from the validation ladder; live calls only for rows 721-750.
- Supersedes: `gan2026_llm_first_direct_extractor_validation750_2026-06-01`.
- Claim language: Reached 675/750 Purist on validation, but retrospective/audit reject it as a clean LLM-first result because deterministic semantic repair became prediction-bearing.
- Artifacts: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.jsonl`, `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.md`, `experiments/gan2026_llm_structured_decision_retrospective_2026-06-01.md`.

### `gan2026_llm_first_direct_extractor_validation750_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `llm_first_direct_extractor`; mode `live direct extraction validation ladder through rare full validation`; replay `cache_first`.
- Model role: LLM-first note-to-label extractor; model `openai/gpt-4.1-mini`.
- Registry roles: `negative_attribution`, `historical_lineage`.
- Repair mode/config: `deterministic code limited to label repair, evidence validation, and scoring`.
- Primary metrics: decision_records=709, exact_evidence_substrings=670, parse_schema_label_issues=41, pragmatic_correct=544, purist_correct=505, row_count=750.
- Evidence validity: Exact evidence substrings 670/750; 41 parse/schema/label issues.
- Cache/reuse source: DSPy cache; full validation reused 610 raw model outputs.
- Claim language: Validation development result only. Full validation reached 505/750 Purist, rejecting direct note-to-label extraction as the active LLM-first path.
- Artifacts: `experiments/gan2026_llm_first_validation25_gpt41mini_2026-05-31.jsonl`, `experiments/gan2026_llm_first_validation25_gpt41mini_2026-05-31.md`, `experiments/gan2026_llm_first_validation25_gpt41mini_v02_2026-05-31.jsonl`, `experiments/gan2026_llm_first_validation25_gpt41mini_v02_2026-05-31.md`, `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.jsonl`, `experiments/gan2026_llm_first_validation250_gpt41mini_v01_2026-05-31.md`, `experiments/gan2026_llm_first_validation750_gpt41mini_v01_2026-06-01.jsonl`, `experiments/gan2026_llm_first_validation750_gpt41mini_v01_2026-06-01.md`.

### `gan2026_claim_table_v5_validation250_test450_generalization_audit_2026-06-01`
- Date/split: `2026-06-01`; `validation+test`; `700` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `v5 max-token validation250 followed by frozen locked-test generalization audit`; replay `cache_first`.
- Model role: LLM-only direct-labeler claim extractor and final query selector; model `openai/gpt-4.1-mini`.
- Repair mode/config: `strict_schema_repair + frozen clean scorer-facing policy; no deterministic candidates before prediction`.
- Primary metrics: test_clean_pragmatic_correct=320, test_clean_purist_correct=301, test_exact_selected_final_evidence=418, test_parse_failures=5, test_raw_purist_correct=293, test_row_count=450, test_strict_purist_correct=294, test_structured_records=445.
- Evidence validity: Locked-test audit reports 1145/1188 exact claim evidence substrings and 418/450 exact selected-final evidence substrings; do not tune from test rows.
- Cache/reuse source: DSPy cache enabled; test450 resumed from 150 saved raw outputs.
- Supersedes: `gan2026_claim_table_v4_validation750_2026-06-01`.
- Claim language: Frozen generalization audit for claim-table v5. Test clean Purist was 301/450, so the path remains a comparator/failure-analysis artifact, not an active promoted candidate.
- Artifacts: `experiments/gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_2026-06-01.md`, `experiments/gan2026_llm_only_claim_table_selector_validation250_v5_max2400_component_ablation_2026-06-01.json`, `experiments/gan2026_llm_only_claim_table_selector_validation250_v5_max2400_component_ablation_2026-06-01.md`, `experiments/gan2026_llm_only_claim_table_selector_test450_gpt41mini_v5_max2400_2026-06-01.jsonl`, `experiments/gan2026_llm_only_claim_table_selector_test450_gpt41mini_v5_max2400_2026-06-01.md`.

### `gan2026_claim_table_v4_validation750_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `750` rows.
- Pipeline: `llm_only_claim_table_selector`; mode `prompt-only`; replay `cache_first`.
- Model role: LLM-only claim-table selector; model `openai/gpt-4.1-mini`.
- Registry roles: `negative_attribution`, `historical_lineage`.
- Repair mode/config: `clean_scorer_facing`.
- Primary metrics: clean_pragmatic_correct=577, clean_purist_correct=528, row_count=750.
- Evidence validity: See full-validation interpretation report.
- Cache/reuse source: DSPy cache/live completion mix recorded in artifact metadata.
- Supersedes: `gan2026_claim_table_v4_validation250_schema_replay_2026-06-01`.
- Claim language: Reject for holdout; full validation exposed cluster-axis and boundary-state collapse.
- Artifacts: `experiments/gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.jsonl`, `experiments/gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.md`, `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`.

## Inform Phase7

### `exectv2_llm_only_all_entities_dev140_gpt41mini_20260612`
- Date/split: `2026-06-12`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_all_entities`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only all-entity single-pass extractor (one call per letter, all nine entities).; model `openai/gpt-4.1-mini`.
- Primary metrics: benchmark_per_item_f1=0.0, benchmark_per_letter_f1=0.0, call_failures=0, evidence_validity_rate=0.9418, mentions_scored=988, mentions_total=1049, parse_failures=0, phrase_only_per_item_f1=0.143, phrase_only_per_letter_f1=0.346, prompt_version=exectv2_llm_only_all_entities_v0.1, semantic_per_item_f1=0.087, semantic_per_letter_f1=0.236.
- Evidence validity: evidence_is_substring; 988/1049 valid, 61 dropped.
- Claim language: ExECTv2 Phase 6 LLM-only all-9 dev140 gpt-4.1-mini. Contract-clean (0 call/parse failures), evidence validity 94.18%, but low semantic overall F1 0.087/0.236 and benchmark with-CUI 0.000/0.000; suitable as locked all-entity LLM-only baseline for the authorized overall audit, not a competitive result.
- Artifacts: `experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl`, `experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.md`.

## Phase4 Complete

### `gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10`
- Date/split: `2026-06-10`; `test`; `450` rows.
- Pipeline: `phase4_test450_frozen_audit_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis: reads the four Phase 4 test450 frozen-audit artifacts (DCP, hybrid v5 with deep-replay via build_unified_pipeline_artifact, SE v0.5, CP v0.5); assembles the shared comparison table plus the hybrid-only routing appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Registry roles: `holdout_anchor`, `architecture_comparator`.
- Primary metrics: architectures_compared=4, deterministic_canonical_pipeline_purist_correct_of_rendered=329, deterministic_canonical_pipeline_purist_rate=0.731, deterministic_canonical_pipeline_rendered_rows=450, hybrid_null_rows=116, hybrid_purist_correct_of_rendered=269, hybrid_purist_rate=0.805, hybrid_rendered_rows=334, hybrid_routed_rows=30, hybrid_structured_events_purist_correct_of_rendered=364, hybrid_structured_events_purist_rate=0.812, hybrid_structured_events_rendered_rows=448, llm_only_canonical_pipeline_purist_correct_of_rendered=326, llm_only_canonical_pipeline_purist_rate=0.724, llm_only_canonical_pipeline_rendered_rows=450, rows_per_architecture=450.
- Evidence validity: Surfaces, but does not collapse, that evidence-trace metrics are NOT uniform across architectures: DCP and SE report evidence_valid (substring presence), llm_only_canonical_pipeline reports evidence_text_contained, hybrid reports a CandidateSet source-id validity rate from deep-replay.
- Claim language: Phase 4 frozen test450 aggregate audit report (authorized 2026-06-09, plan Section 6): one-shot frozen aggregate read of the locked test450 split for deterministic_canonical_pipeline, hybrid (v5 prompt, deep-replayed), hybrid_structured_events (v0.5), and llm_only_canonical_pipeline (v0.5); deterministic and llm_only_direct_labeler intentionally excluded (Section 6 rationale). Of-rendered purist/pragmatic accuracy: DCP 0.731/0.758 (450/450 rendered), hybrid 0.805/0.841 (334/450 rendered, 30 routed all abstained), SE 0.812/0.850 (448/450 rendered), CP 0.724/0.769 (450/450 rendered). SE leads on both purist and pragmatic of-rendered accuracy; hybrid is second on accuracy of-rendered but renders the fewest rows (116 null/unscored of 450). No row-level holdout tuning; no re-runs based on these results.
- Artifacts: `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.jsonl`, `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.json`, `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`.

### `gan2026_test450_phase4_frozen_audit_llm_only_canonical_pipeline_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `llm_only_canonical_pipeline`; mode `live`; replay `native_run_split`.
- Model role: fully-LLM canonical-pipeline labeler (v0.5): single LLM call -> decision_record with rule-taxonomy self-report.; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, evidence_text_contained=415, evidence_text_contained_rate=0.9222, parse_or_validation_failures=0, pragmatic_accuracy=0.7689, pragmatic_correct=346, prompt_version=gan2026_llm_only_canonical_pipeline_v0.5, purist_accuracy=0.7244, purist_correct=326, repair_notes=227, rows=450.
- Evidence validity: evidence_text_contained reported per row (deliberately distinct from evidence_valid).
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- llm_only_canonical_pipeline v0.5 prompt (gan2026_llm_only_canonical_pipeline_v0.5) over the locked test450 split. 450/450 decision records, 0 call failures, 0 parse/schema/label issues, 227 deterministic repair notes, evidence_text_contained 415/450 (0.9222). Purist accuracy 0.7244 (326/450), Pragmatic accuracy 0.7689 (346/450).
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_llm_only_canonical_pipeline_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_llm_only_canonical_pipeline_gpt41mini_2026-06-09.md`, `experiments/gan2026_test450_phase4_cp_gpt41mini_2026-06-09_stdout.txt`, `experiments/gan2026_test450_phase4_cp_gpt41mini_2026-06-09_stderr.txt`.

### `gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `native_run_split`.
- Model role: structured-events extraction (v0.5): raw note text -> structured events; deterministic normalize/project/render/score/route downstream.; model `openai/gpt-4.1-mini`.
- Repair mode/config: `hybrid_full_stack`.
- Primary metrics: call_failures=0, evidence_valid=418, evidence_valid_rate=0.929, parse_or_validation_failures=2, pragmatic_accuracy=0.8467, pragmatic_correct=381, prompt_version=gan2026_hybrid_structured_events_v0.5, purist_accuracy=0.8089, purist_correct=364, repair_notes=306, rows=450, structured_records=448.
- Evidence validity: evidence_valid (free-text substring presence) reported per row.
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- hybrid_structured_events v0.5 prompt (gan2026_hybrid_structured_events_v0.5) over the locked test450 split, repair_mode hybrid_full_stack. Structured records 448/450, 0 call failures, 2 parse/schema/label issues, 306 deterministic repair notes, evidence_valid 418/450 (0.929). Purist accuracy 0.8089 (364/450), Pragmatic accuracy 0.8467 (381/450).
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.md`, `experiments/gan2026_test450_phase4_se_gpt41mini_2026-06-09_stdout.txt`, `experiments/gan2026_test450_phase4_se_gpt41mini_2026-06-09_stderr.txt`.

### `gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `hybrid`; mode `live`; replay `assessment_stage_only`.
- Model role: hybrid clinical assessment probe (v5): CandidateSet -> clinical assessment schema; deterministic downstream (normalize/project/render/score/route) applied in deep-replay.; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, missing_candidate_set_rows=0, parse_or_validation_failures=0, prompt_version=gan2026_candidate_set_clinical_assessment_probe_v5, rows=450.
- Evidence validity: Assessment-stage probe only -- CandidateSet source-id validity rate computed in deep-replay during report build, not in this artifact directly.
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- hybrid v5 prompt (gan2026_candidate_set_clinical_assessment_probe_v5) clinical-assessment probe over the locked test450 split, live-generated CandidateSets embedded per row. 450/450 rows, 0 call failures, 0 parse/validation failures, 0 missing candidate sets. Assessment-stage probe only -- no rendered/null/purist/routed numbers of its own; those are produced via deep-replay in gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09.md`, `experiments/gan2026_test450_phase4_hybrid_gpt41mini_2026-06-09_stdout.txt`, `experiments/gan2026_test450_phase4_hybrid_gpt41mini_2026-06-09_stderr.txt`.

### `gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09`
- Date/split: `2026-06-09`; `test`; `450` rows.
- Pipeline: `deterministic_canonical_pipeline`; mode `deterministic`; replay `native_run_split`.
- Model role: Deterministic canonical-pipeline baseline; no model calls.; model `none`.
- Primary metrics: pragmatic_accuracy=0.7578, pragmatic_correct=341, purist_accuracy=0.7311, purist_correct=329, rows=450.
- Evidence validity: evidence_valid (free-text substring presence) reported per row.
- Claim language: Phase 4 frozen test450 aggregate audit (authorized 2026-06-09, plan Section 6) -- deterministic_canonical_pipeline over the locked test450 split. Fully deterministic pipeline, no live model calls (gpt41mini in the filename reflects the comparison cohort label, not a model dependency). One-shot frozen aggregate read; no row-level tuning, no re-runs based on results.
- Artifacts: `experiments/gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09.jsonl`, `experiments/gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09.md`.

## Inform Phase4

### `gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14`
- Date/split: `2026-06-14`; `test`; `450` rows.
- Pipeline: `hybrid_structured_events`; mode `live`; replay `live`.
- Model role: LLM structured-events extractor and selector using SE v0.6 on the locked test450 split; deterministic code limited to Gan normalization, evidence validation, and scoring/repair after structured model selection.; model `deepseek/deepseek-chat`.
- Registry roles: `holdout_anchor`.
- Repair mode/config: `hybrid_full_stack`.
- Primary metrics: call_failures=0, evidence_valid_rows=440, parse_or_validation_failures=4, pragmatic_accuracy=0.8178, pragmatic_correct=368, prompt_version=gan2026_hybrid_structured_events_v0.6, purist_accuracy=0.7867, purist_correct=354, rendered_rows=446, structured_records=446.
- Evidence validity: 440/450 rows carry an evidence_valid substring-presence trace; 0 call failures; 4 parse/schema/label issues; 446 structured records.
- Claim language: User-authorized DeepSeek structured-events test450 source-coverage run to correct the missing cross-model holdout artifact noted in the 2026-06-14 structured-events/agentic synthesis. Aggregate artifact generation only; no row-level holdout failure analysis or post-test tuning is authorized by this entry. This fills the DeepSeek SE source gap for future frozen aggregate-only consensus/scaffolding audits, but is not itself a promoted final-answer architecture.
- Artifacts: `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl`, `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.md`.

### `exectv2_hybrid_dev140_qwen3635b_20260611`
- Date/split: `2026-06-11`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 hybrid candidate-set + clinical-assessment extractor (deterministic candidates -> LLM keep/route/attribute -> deterministic normalize, SeizureFrequency only).; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: call_failures=0, candidates_offered=639, mentions_kept=313, mentions_routed=45, mentions_scored=235, parse_failures=1, phrase_only_per_item_f1=0.498, phrase_only_per_letter_f1=0.73, prompt_version=exectv2_hybrid_candidate_assessment_v0.2, sf_benchmark_per_item_f1=0.228, sf_benchmark_per_letter_f1=0.451, sf_semantic_per_item_f1=0.228, sf_semantic_per_letter_f1=0.451.
- Evidence validity: evidence_is_substring (exact source-text substring check); routing taxonomy {no_frequency_attributes:25, bare_nonzero_count:13, empty_evidence:5, evidence_not_substring:2}.
- Supersedes: `exectv2_hybrid_dev50partial_qwen3635b_20260611`.
- Claim language: ExECTv2 Phase 4 - hybrid (candidate + assessment) full dev run (140 letters, D16 gold, SeizureFrequency only), qwen3.6:35b. Completed by RESUMING from a 50/140 checkpoint after a power interruption (core.run_resume; n_resumed=50) - no work re-spent. phrase_only per-item F1 0.498, per-letter 0.730 - below gpt-4.1-mini hybrid (0.585/0.781) but above the deterministic baseline per-letter (0.604) and the qwen LLM-only per_entity (0.642). sf_semantic == sf_benchmark per-item 0.228, per-letter 0.451 - below gpt hybrid (0.327/0.578) and deterministic (0.362/0.575), far above qwen LLM-only (0.036/0.104). 639 candidates offered, 313 kept by LLM, 235 scored, 45 routed; 0 call failures, 1 parse failure (one max_tokens=3000 truncation). gpt-4.1-mini > qwen on hybrid, mirroring the LLM-only result.
- Artifacts: `experiments/exectv2_hybrid_v02_dev140_qwen3635b_20260611.jsonl`, `experiments/exectv2_hybrid_v02_dev140_qwen3635b_20260611.md`.

### `exectv2_hybrid_dev140_gpt41mini_20260611`
- Date/split: `2026-06-11`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 hybrid candidate-set + clinical-assessment extractor (deterministic candidates -> LLM keep/route/attribute -> deterministic normalize, SeizureFrequency only).; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, candidates_offered=639, mentions_kept=288, mentions_routed=37, mentions_scored=247, parse_failures=0, phrase_only_per_item_f1=0.585, phrase_only_per_letter_f1=0.781, prompt_version=exectv2_hybrid_candidate_assessment_v0.2, sf_benchmark_per_item_f1=0.327, sf_benchmark_per_letter_f1=0.578, sf_semantic_per_item_f1=0.327, sf_semantic_per_letter_f1=0.578.
- Evidence validity: evidence_is_substring (exact source-text substring check); routing taxonomy {no_frequency_attributes:7, bare_nonzero_count:29, evidence_not_substring:1}.
- Claim language: ExECTv2 Phase 4 - hybrid (candidate + assessment) full dev run (140 letters, D16 gold, SeizureFrequency only). phrase_only per-item F1 0.585, per-letter 0.781 - best phrase recall of any family and the only architecture whose per-letter clears the SF benchmark target 0.68. sf_semantic == sf_benchmark per-item 0.327, per-letter 0.578 - best attribute-aware per-letter of any architecture (above deterministic 0.575 and far above LLM-only), marginally below deterministic on per-item (0.362). 639 candidates offered, 288 kept by LLM, 247 scored, 37 routed; 0 call/parse failures.
- Artifacts: `experiments/exectv2_hybrid_v02_dev140_gpt41mini_20260611.jsonl`, `experiments/exectv2_hybrid_v02_dev140_gpt41mini_20260611.md`.

### `exectv2_llm_only_single_pass_dev140_qwen3635b_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_single_pass`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only single-pass extractor (one call per letter, all SF mentions + attributes + evidence).; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.945, mentions_scored=189, mentions_total=200, parse_failures=2, phrase_only_per_item_f1=0.383, phrase_only_per_letter_f1=0.623, prompt_version=exectv2_llm_only_single_pass_v0.2, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.09, sf_semantic_per_letter_f1=0.213.
- Evidence validity: evidence_is_substring; 189/200 valid, 11 dropped.
- Claim language: ExECTv2 Phase 3 — qwen3.6:35b single_pass dev140. phrase_only per-letter 0.623 (below gpt-4.1-mini 0.701 by 11%). sf_semantic per-letter 0.213 (above gpt-4.1-mini 0.197 by 8%). 2 parse failures. 94.5% evidence validity. sf_benchmark 0.000 (CUI D3).
- Artifacts: `experiments/exectv2_llm_only_single_pass_dev140_qwen3635b_20260610.jsonl`, `experiments/exectv2_llm_only_single_pass_dev140_qwen3635b_20260610.md`.

### `exectv2_llm_only_single_pass_dev140_gpt41mini_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_single_pass`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only single-pass extractor (one call per letter, all SF mentions + attributes + evidence).; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.9749, mentions_scored=195, mentions_total=199, parse_failures=0, phrase_only_per_item_f1=0.466, phrase_only_per_letter_f1=0.701, prompt_version=exectv2_llm_only_single_pass_v0.2, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.094, sf_semantic_per_letter_f1=0.197.
- Evidence validity: evidence_is_substring (exact source-text substring check); 195/199 valid, 4 dropped.
- Claim language: ExECTv2 Phase 3 — LLM-only single-pass full dev run (140 letters, D16 gold, SeizureFrequency only). phrase_only per-item F1 0.466, per-letter 0.701 (exceeds SF benchmark target 0.68). sf_semantic near-zero (attribute-convention mismatch). sf_benchmark 0.000 (CUI lookup is shared post-step D3). Deterministic baseline: phrase_only 0.382/0.604.
- Artifacts: `experiments/exectv2_llm_only_single_pass_dev140_gpt41mini_20260610.jsonl`, `experiments/exectv2_llm_only_single_pass_dev140_gpt41mini_20260610.md`.

### `exectv2_llm_only_per_entity_dev140_qwen3635b_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_per_entity`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only per-entity extractor (one focused call per entity type per letter, SF only).; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.961, mentions_scored=197, mentions_total=205, parse_failures=0, phrase_only_per_item_f1=0.401, phrase_only_per_letter_f1=0.642, prompt_version=exectv2_llm_only_per_entity_v0.2, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.036, sf_semantic_per_letter_f1=0.104.
- Evidence validity: evidence_is_substring; 197/205 valid, 8 dropped.
- Claim language: ExECTv2 Phase 3 — qwen3.6:35b per_entity dev140. phrase_only per-letter 0.642 (below gpt-4.1-mini 0.698 by 8%). sf_semantic per-item 0.036, per-letter 0.104 — dramatically worse than gpt-4.1-mini per_entity (0.135/0.264). Unlike gpt-4.1-mini, qwen does NOT benefit from focused per_entity prompt for attributes; sf_semantic is even worse than qwen single_pass (0.090/0.213). 0 parse failures, 96.1% evidence validity. sf_benchmark 0.000 (CUI D3).
- Artifacts: `experiments/exectv2_llm_only_per_entity_dev140_qwen3635b_20260610.jsonl`, `experiments/exectv2_llm_only_per_entity_dev140_qwen3635b_20260610.md`.

### `exectv2_llm_only_per_entity_dev140_gpt41mini_20260610`
- Date/split: `2026-06-10`; `dev`; `140` rows.
- Pipeline: `exectv2_llm_only_per_entity`; mode `live`; replay `native_run_split`.
- Model role: ExECTv2 LLM-only per-entity extractor (one focused call per entity type per letter, SF only).; model `openai/gpt-4.1-mini`.
- Primary metrics: call_failures=0, evidence_validity_rate=0.9632, mentions_scored=183, mentions_total=190, parse_failures=0, phrase_only_per_item_f1=0.486, phrase_only_per_letter_f1=0.698, prompt_version=exectv2_llm_only_per_entity_v0.1, sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.135, sf_semantic_per_letter_f1=0.264.
- Evidence validity: evidence_is_substring (exact source-text substring check); 183/190 valid, 7 dropped.
- Claim language: ExECTv2 Phase 3 — LLM-only per-entity full dev run (140 letters, D16 gold, SeizureFrequency only). phrase_only per-item F1 0.486, per-letter 0.698 (exceeds SF benchmark target 0.68). sf_semantic 0.135/0.264 — 44% better than single_pass per-item (0.094), 34% better per-letter (0.197). sf_benchmark 0.000 (CUI D3). Best LLM-only config for attribute matching. Deterministic baseline: phrase_only 0.382/0.604.
- Artifacts: `experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260610.jsonl`, `experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260610.md`.

## Phase3 Complete Gpt41Mini

### `gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase3_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis: reads Phase 2 deterministic/DCP artifacts, Phase 3 hybrid v5 artifact (with deep-replay for rendered/null/purist/routed numbers), Phase 3 DL v0.5 / CP v0.5 artifacts, Phase 1 SE artifact; assembles shared comparison table plus hybrid-only routing appendix; makes no hosted LLM calls of its own.; model `openai/gpt-4.1-mini`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=673, deterministic_purist_correct_of_rendered=673, hybrid_purist_correct_of_rendered=526, hybrid_purist_rate=0.881, hybrid_rendered_rows=597, hybrid_structured_events_purist_correct_of_rendered=661, llm_only_canonical_pipeline_purist_correct_of_rendered=582, llm_only_direct_labeler_purist_correct_of_rendered=575, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, that evidence-trace metrics are NOT uniform across architectures: four report evidence_valid (substring presence), llm_only_canonical_pipeline reports evidence_text_contained, hybrid reports CandidateSet source-id validity rate.
- Supersedes: `gan2026_three_way_comparison_phase2_report_cluster_diary_digit_validation750_2026-06-09`.
- Claim language: Phase 3 three-way architecture comparison report (validation750, gpt-4.1-mini). Deterministic/DCP from Phase 2 iteration 2 (digit-only de-overfitting); hybrid from v5 run (FM-2/FM-5b/FM-6 prompt fixes); DL v0.5 / CP v0.5 from Phase 3 LLM-only runs; SE from Phase 1 (no SE-specific Phase 3 changes). Key Phase 3 vs Phase 2 delta for hybrid (gpt-4.1-mini): 597 rendered vs 589 (+8 more rendered), 526/597 purist = 88.1% vs 500/589 = 84.9% (+3.2pp); 545/597 pragmatic = 91.3%. hybrid_structured_events leads purist at 661/748=88.4%. deterministic/DCP ceiling: 673/741=90.8%. No test450 read; no holdout-facing claim.
- Artifacts: `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.md`.

## Inform Phase3

### `gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase1_report`; mode `analysis-only`; replay `analysis_only`.
- Model role: Analysis-only synthesis -- reads completed validation750 run artifacts; assembles shared comparison table plus hybrid-only routing appendix; makes no hosted LLM calls.; model `ollama_chat/qwen3.6:35b`.
- Primary metrics: architectures_compared=6, deterministic_canonical_pipeline_purist_correct_of_rendered=688, deterministic_purist_correct_of_rendered=688, hybrid_purist_correct_of_rendered=291, hybrid_rendered_rows=400, hybrid_structured_events_purist_correct_of_rendered=624, llm_only_canonical_pipeline_purist_correct_of_rendered=544, llm_only_direct_labeler_purist_correct_of_rendered=550, rows_per_architecture=750.
- Evidence validity: Surfaces, but does not collapse, the fact that evidence-trace metrics are NOT uniform across architectures.
- Supersedes: `gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09`.
- Claim language: Phase 1 three-way architecture comparison, ollama_chat/qwen3.6:35b pass, validation750 only (gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07 Section 3 + Section 8b). Full 750-row surface: hybrid now uses the live-wired candidate-set generation (section 8a) merged from the resume-part into the 2026-06-08 file; 0 candidate_set_missing rows. Supersedes the interim 250-row-scoped hybrid report (gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09). Key findings: hybrid_structured_events leads at 624/746 (0.836); hybrid renders only 400/750 rows (much lower surface than gpt-4.1-mini 589/750 or deepseek 604/750), with 62 routed (15.5%); llm_only_direct_labeler and llm_only_canonical_pipeline nearly tied (550/749=0.734 vs 544/748=0.727). Closes Section 8b.
- Artifacts: `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.jsonl`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.json`, `experiments/gan2026_three_way_comparison_phase1_report_qwen3635b_full_validation750_2026-06-09.md`.

### `gan2026_phase3_error_analysis_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `three_way_comparison_phase3_error_analysis`; mode `analysis-only`; replay `analysis_only`.
- Model role: Error analysis and failure taxonomy for Phase 3 prompt engineering; model `none`.
- Primary metrics: architectures_analysed=4, cp_failures=169, cp_rule_fire_failure_rate_max=0.426, dl_failures=186, hybrid_failures=88, named_failure_modes=8, se_failures=89, universal_failures=20.
- Evidence validity: Analysis draws directly from Phase 1 validation750 JSONL artifacts; row-by-row tables verified against source prediction and gold records.
- Claim language: Phase 3 error analysis: row-by-row + thematic failure catalogue over Phase 1 validation750 results for four architectures (gpt-4.1-mini). Documents 8 named failure modes (FM-1 through FM-8) across 532 total failures. Critical finding: four highest-failure-rate CP rules (seizure_free_conflict 42.6%, same_window_additive_frequency 34.7%, denominator_window_mismatch 30.3%, concrete_frequency_precedence 27.8%) account for 143/169 CP failures where a rule was cited — model cites rule then violates it. 20 universal failures (all 4 architectures). Priority ranking: FM-2 seizure-free FP (97) > FM-1 denominator window (~66 LLM-improvable) > FM-3 unknown FP (132) > FM-6 highest-type selection (~25 universal). Input to Phase 3 prompt-engineering decisions.
- Artifacts: ``.

### `gan2026_cross_model_comparison_2026-06-09`
- Date/split: `2026-06-09`; `validation`; `750` rows.
- Pipeline: `cross_model_comparison`; mode `analysis-only`; replay `analysis_only`.
- Model role: Cross-model synthesis document -- no model calls; reads existing Phase 1 artifacts and computed failure breakdowns.; model `none`.
- Registry roles: `model_family_variant`.
- Primary metrics: architectures_compared=6, deepseek_dl_sf_false_pos=56, deepseek_hybrid_rendered=604, deepseek_se_purist_rate=0.821, gpt41mini_dl_unknown_false_pos=59, gpt41mini_hybrid_rendered=589, gpt41mini_se_purist_rate=0.884, models_compared=3, qwen_dl_unknown_false_pos=91, qwen_hybrid_rendered=400, qwen_se_purist_rate=0.836.
- Evidence validity: Derived from Phase 1 per-row JSONL comparison fields for DL, CP, SE; aggregate numbers from Phase 1 report JSONLs for hybrid and all architectures.
- Claim language: Cross-model synthesis comparing all three Phase 1 models (gpt-4.1-mini, deepseek-v4-flash, qwen3.6-35b) across all six architecture configurations on validation750. Includes per-row failure category breakdowns for DL, CP, SE (hybrid row-level data not available for deepseek/qwen without deep-replay extraction). Key findings: (1) SE is consistently best across models but gpt-4.1-mini leads by 5-6pp; (2) qwen dominant failure is unknown_false_pos (91 DL vs 59 gpt-4.1-mini) -- reverse of deepseek (highest seizure_free_false_pos: 56 DL); (3) CP guidance block helps gpt-4.1-mini (+2.3pp) but harms qwen (-0.7pp); (4) FM-6 drop-attack selection is gpt-4.1-mini-specific -- qwen and deepseek already correct; (5) qwen hybrid renders only 400/750 rows vs 589/604 for gpt/deepseek; (6) deepseek hybrid routing dominated by rendered_label_supported_but_policy_sensitive (97/123) driven by its SF over-confidence.
- Artifacts: ``.

## Inform Architecture Loop

### `exectv2_hybrid_benchmark_overall_dev_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid_benchmark_overall`; mode `analysis_only`; replay `analysis_only`.
- Model role: Merged hybrid key-family + deterministic all-9, benchmark surface.; model `gpt-4.1-mini (key families) + deterministic`.
- Primary metrics: benchmark_per_item_f1=0.3877, benchmark_per_letter_f1=0.6972, paper_overall_per_item_f1=0.87, paper_overall_per_letter_f1=0.9, phrase_only_per_item_f1=0.4549, semantic_per_item_f1=0.4008.
- Claim language: Like-for-like benchmark-surface overall for the synthesis hybrid key-family architecture. Dev140, analysis-only, no full-200 audit.
- Artifacts: `experiments\exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json`, `experiments\exectv2_hybrid_benchmark_overall_bestof_dev_20260618.md`.

### `exectv2_deterministic_all9_dev_20260617`
- Date/split: `2026-06-17`; `dev`; `140` rows.
- Pipeline: `exectv2_deterministic_all9`; mode `deterministic`; replay `analysis_only`.
- Model role: ExECTv2 deterministic all-9 baseline; active rules for Prescription, Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory, EpilepsyCause, PatientHistory, and SeizureFrequency.; model `(model-independent)`.
- Primary metrics: active_entities=['Prescription', 'Investigations', 'Diagnosis', 'Onset', 'WhenDiagnosed', 'BirthHistory', 'EpilepsyCause', 'PatientHistory', 'SeizureFrequency'], benchmark_per_item_f1=0.3625, benchmark_per_letter_f1=0.6747, call_failures=0, cui_attachment_rate=0.9909, evidence_not_substring_count=0, evidence_validity_rate=1.0, mentions_total=992, mentions_with_cui=983, parse_failures=0, phrase_only_per_item_f1=0.4571, phrase_only_per_letter_f1=0.7526, prescription_benchmark_with_cui_f1=0.302, prescription_clinical_headline_f1=0.9072, prompt_version=n/a (deterministic rules), routing_count=0, schema_error_count=0, schema_repairs=0, semantic_per_item_f1=0.3754, semantic_per_letter_f1=0.6814.
- Evidence validity: exact source substring validation summarized in scorecard.
- Claim language: First GPT-first rules_only all-9 substrate. Not freeze-ready; incomplete entity coverage remains explicit in per-entity scores.
- Artifacts: `experiments/exectv2_deterministic_all9_dev_20260617.json`, `experiments/exectv2_deterministic_all9_dev_20260617.md`.

## Clinical Recovery Reporting

### `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200`
- Date/split: `2026-06-26`; `full200_aggregate`; `200` rows.
- Pipeline: `exectv2_same_core_model_swap`; mode `live_plus_replay`; replay `live`.
- Model role: Qwen repair v02 structured key-family and Diagnosis producers; deterministic code owns SF projection/union, Prescription repair, and finding assembly replay.; model `ollama_chat/qwen3.6:35b`.
- Registry roles: `model_family_variant`.
- Repair mode/config: `qwen_output_contract_repair_v02 plus shared_standard_source_exact_evidence_repair`.
- Primary metrics: benchmark_cui_overall_f1=0.4537, call_failures=0, clinical_headline_f1=0.8197, diagnosis_f1=0.8307, evidence_valid_overall_f1=0.7895, final_lane_evidence_rate=1.0, investigations_f1=0.8503, parse_schema_failures=0, prescription_f1=0.8926, seizure_frequency_f1=0.702, structured_evidence_invalid_after_standard_repair=6, structured_evidence_validity_rate_after_standard_repair=0.995, structured_mentions_raw=1197, structured_mentions_scored_after_standard_repair=1191.
- Evidence validity: Structured saved-raw replay with standard source-exact repair: 1191/1197 scored, 6 invalid, 0.9950 validity. Final assembled lane diagnostics report 1.0000 exact evidence for Diagnosis, SeizureFrequency, Prescription, and Investigations.
- Cache/reuse source: Live structured and Diagnosis repair-v02 producers plus frozen deterministic same-core replay components; aggregate-only full-200 validation with no row-level failure inspection.
- Claim language: Separate same-core full-200 aggregate-only Qwen repair v02 row. Clinical-headline F1 is 0.8197 with SF 0.7020, 0 call/parse failures, and structured evidence validity 0.9950. Passes the predeclared full-200 stop rule but trails GPT-4.1-mini (0.8356) and DeepSeek (0.8566). Does not retroactively alter the GPT-4.1-mini plus DeepSeek full-200 protocol; not a strict benchmark or holdout claim.
- Artifacts: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_20260626.json`, `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_20260626.jsonl`, `docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_2026-06-26.md`, `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_repair_v02_full200_readout_2026-06-26.md`, `docs/experiments/exectv2/reliability/exectv2_qwen_repair_v02_full200_predeclaration_2026-06-26.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_structured.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_structured.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_diagnosis_decomposer.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_diagnosis_decomposer.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_sf_union_arbitration.md`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_sf_union_arbitration.jsonl`, `experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_prescription_deterministic_repair_v03.jsonl`, `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200.json`.

### `exectv2_same_core_model_swap_full200_20260625`
- Date/split: `2026-06-25`; `full200_aggregate`; `200` rows.
- Pipeline: `exectv2_same_core_model_swap`; mode `aggregate-only comparison report`; replay `analysis_only`.
- Model role: Aggregate-only same-core full-200 comparison for the frozen two-call no-SF-adjudicator architecture.; model `openai/gpt-4.1-mini; deepseek/deepseek-chat`.
- Registry roles: `architecture_comparator`, `model_family_variant`.
- Repair mode/config: `exectv2_2call_no_sf_adjudicator_model_swap frozen component graph`.
- Primary metrics: deepseek_call_failures=0, deepseek_clinical_headline_f1=0.8566, deepseek_diagnosis_f1=0.8708, deepseek_investigations_f1=0.9091, deepseek_parse_schema_failures=1, deepseek_prescription_f1=0.8926, deepseek_seizure_frequency_f1=0.7602, gpt41mini_call_failures=0, gpt41mini_clinical_headline_f1=0.8356, gpt41mini_diagnosis_f1=0.8397, gpt41mini_investigations_f1=0.8563, gpt41mini_parse_schema_failures=0, gpt41mini_prescription_f1=0.8926, gpt41mini_seizure_frequency_f1=0.7525, min_exact_evidence_rate=1.0, model_count=2.
- Evidence validity: Aggregate-only report: completed rows minimum exact evidence rate 1.0000; DeepSeek accepted with one Diagnosis parse/schema caveat.
- Cache/reuse source: GPT-4.1-mini full-200 reference plus DeepSeek full-200 same-core run; no full-200 row-level failure analysis.
- Claim language: Accepted same-core full-200 aggregate validation with schema-stability caveat. Strict benchmark/CUI scores remain diagnostic and no full-200 row-level failure analysis or tuning is authorized.
- Artifacts: `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`, `docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`, `experiments/exectv2_same_core_model_swap_full200_20260625.json`, `experiments/exectv2_same_core_model_swap_full200_20260625.jsonl`.

### `exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624`
- Date/split: `2026-06-24`; `full200_aggregate`; `200` rows.
- Pipeline: `exectv2_holistic_finding_assembly`; mode `authorized full-200 aggregate replay`; replay `saved_output_replay`.
- Model role: Current-code v08-shaped GPT-4.1-mini holistic finding assembly with focused Diagnosis, SF, Prescription, and Investigations lanes; aggregate-only full-200 audit.; model `openai/gpt-4.1-mini`.
- Registry roles: `architecture_comparator`, `component_ladder`.
- Repair mode/config: `diagnosis_heading_recovery_residual_benchmark_v05 + sf_state_union_arbitration_v08 + prescription_regimen_v01 + investigations_result_v01`.
- Primary metrics: benchmark_cui_overall_f1=0.8191, call_failures=0, clinical_headline_f1=0.8502, diagnosis_f1=0.8321, evidence_valid_overall_f1=0.8191, investigations_f1=0.9213, min_exact_evidence_rate=1.0, parse_schema_failures=0, prescription_f1=0.8926, raw_candidate_overall_f1=0.7908, seizure_frequency_active_rate_fidelity=0.5564, seizure_frequency_f1=0.785.
- Evidence validity: Aggregate report lens diagnostics show exact evidence rate 1.0000 for every family; no full-200 row-level failure analysis is authorized.
- Claim language: Authorized full-200 aggregate audit of the current-code v08-shaped surface. It is not byte-identical to archived dev140 v08 and is not a locked-test, benchmark, or row-level tuning claim.
- Artifacts: `docs/experiments/exectv2/reliability/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.md`, `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.json`, `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl`.

### `exectv2_v09_single_gpt_simplification_study_dev140_20260621`
- Date/split: `2026-06-21`; `dev`; `140` rows.
- Pipeline: `exectv2_holistic_finding_assembly`; mode `dev140 simplification study`; replay `analysis_only`.
- Model role: v09 single-GPT plus standard-dictionary simplification study and partial-hybrid no-call assembly comparison.; model `openai/gpt-4.1-mini`.
- Registry roles: `component_ladder`, `negative_attribution`.
- Repair mode/config: `standard_dictionary plus v09 partial-hybrid ablation configs`.
- Primary metrics: gpt_only_dictionary_clinical_headline_f1=0.7552, partial_hybrid_clinical_headline_f1=0.9059, partial_hybrid_diagnosis_f1=0.9083, partial_hybrid_investigations_f1=0.8549, partial_hybrid_prescription_f1=0.9357, partial_hybrid_seizure_frequency_f1=0.9053, v08_dev140_comparator_f1=0.9152.
- Evidence validity: Dev140-only simplification evidence from the v09 study; no full-200, locked-test, or benchmark claim.
- Claim language: Single GPT plus standard dictionaries does not clear 0.9 at GPT-4.1-mini; the accepted partial hybrid reaches 0.9059 by keeping focused Diagnosis, SeizureFrequency, and Prescription lanes while simplifying Investigations.
- Artifacts: `docs/experiments/exectv2/key_entities/exectv2_v09_single_gpt_simplification_study_dev140_20260621.md`, `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_dev140.yaml`, `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml`, `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09b_leanhybrid_dev140.yaml`, `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09h1_presc_sf_dev140.yaml`, `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09h2_presc_dx_dev140.yaml`, `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09h3_presc_sf_dx_dev140.yaml`.

## Historical

### `exectv2_arbitration_v02_dev140_gpt41mini_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `exectv2_hybrid`; mode `live`; replay `live`.
- Model role: one arbitration call per letter over the union per-entity candidate pool; model `openai/gpt-4.1-mini`.
- Primary metrics: summary=git_head=291a6c6d19d7, prompt_version=exectv2_arbitration_v0.2, semantic_per_item_f1=0.190 (P0.278 R0.144), benchmark_per_item_f1=0.137, diagnosis_semantic_f1=0.270, parse_failures=0.
- Claim language: REJECTED as headline. Entity retyping works (named seizure types -> Diagnosis + SF replication) but a single combined call cannot reproduce the recall of nine focused passes -> 0.190 < 0.220 bare union. Regeneration is recall-limited.
- Artifacts: `experiments/archive/gan2026_historical_lineage/exectv2_arbitration_v02_dev140_gpt41mini_20260618.md`, `experiments/exectv2_arbitration_v02_dev140_gpt41mini_20260618.jsonl`.

### `exectv2_altitude_proj_dev140_20260618`
- Date/split: `2026-06-18`; `dev`; `140` rows.
- Pipeline: `deterministic_benchmark_altitude`; mode `replay`; replay `saved_output_replay`.
- Model role: deterministic compound-split + seizure-type entity-norm + affirmed-default attributes; no model; model `projection`.
- Primary metrics: summary=git_head=291a6c6d19d7, prompt_version=benchmark_altitude_v0.1, semantic_per_item_f1=0.242 (from 0.220 bare union), diagnosis_semantic_f1=0.318 (from 0.243), patienthistory_semantic_f1=0.180, benchmark_per_item_f1=0.181.
- Claim language: recall-preserving deterministic projection, separate projection credit (never LLM reasoning). Diagnosis +0.075, overall +0.022. Oracle phrase-snap caps F1=0.42; 0.7 on populous entities NOT reachable via projection (PH recall-bound, SF quantification-bound). See docs/research/exectv2_gpt_first_error_analysis_2026-06-18.md.
- Artifacts: `experiments/archive/gan2026_historical_lineage/exectv2_altitude_proj_dev140_20260618.md`, `experiments/exectv2_altitude_proj_dev140_20260618.jsonl`.

### `exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612`
- Date/split: `2026-06-12`; `full200_overall_audit`; `200` rows.
- Pipeline: `exectv2_llm_only_all_entities`; mode `live`; replay `live`.
- Model role: ExECTv2 Phase 7 frozen full-200 overall all-entity LLM-only audit.; model `openai/gpt-4.1-mini`.
- Primary metrics: authorization=full-200 overall read authorized by user 2026-06-12 (Phase 6/7), benchmark_per_item_ci=[0.0, 0.0], benchmark_per_item_f1=0.0, benchmark_per_letter_ci=[0.0, 0.0], benchmark_per_letter_f1=0.0, call_failures=0, evidence_validity_rate=0.9323, git_head=8d7ecfbc101f+dirty, mentions_raw=1492, mentions_scored=1391, parse_failures=0, phrase_only_per_item_f1=0.147, phrase_only_per_letter_f1=0.362, prompt_version=exectv2_llm_only_all_entities_v0.1, semantic_per_item_ci=[0.0711, 0.0985], semantic_per_item_f1=0.0844, semantic_per_letter_ci=[0.2007, 0.2632], semantic_per_letter_f1=0.2317.
- Evidence validity: frozen audit; exact substring evidence gate recorded in report.
- Claim language: Phase 7 frozen overall all-entity audit. Semantic overall F1 0.084/0.232; benchmark with-CUI F1 0.000/0.000; locked at git 8d7ecfbc101f+dirty.
- Artifacts: `experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl`, `experiments/archive/gan2026_historical_lineage/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.md`.

### `exectv2_audit_rules_full200_modelindependent_20260611`
- Date/split: `2026-06-11`; `full200_audit`; `200` rows.
- Pipeline: `exectv2_deterministic`; mode `deterministic`; replay `analysis_only`.
- Model role: ExECTv2 Phase 7 frozen full-200 SF audit (rules).; model `(model-independent)`.
- Primary metrics: authorization=full-200 read authorized by user 2026-06-11 (Phase 7), call_failures=0, git_head=ab0d8d5cb7aa, parse_failures=0, phrase_only_per_item_f1=0.4725, phrase_only_per_letter_f1=0.6756, prompt_version=n/a (deterministic rules), sf_benchmark_per_item_ci=[0.2538, 0.3879], sf_benchmark_per_item_f1=0.3211, sf_benchmark_per_letter_ci=[0.451, 0.6184], sf_benchmark_per_letter_f1=0.5392, sf_semantic_per_item_f1=0.3211, sf_semantic_per_letter_f1=0.5392.
- Evidence validity: frozen audit; gates recorded in the audit report.
- Claim language: Phase 7 frozen SF audit over all 200 letters (authorized 2026-06-11). Headline sf_benchmark per-item F1 0.321 (CI 0.254-0.388), per-letter F1 0.539 (CI 0.451-0.618) vs published 0.66/0.68. Immutable; locked at git ab0d8d5cb7aa.
- Artifacts: `experiments/archive/gan2026_historical_lineage/exectv2_audit_rules_full200_modelindependent_20260611.md`, `experiments/exectv2_audit_rules_full200_modelindependent_20260611.jsonl`.

### `exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611`
- Date/split: `2026-06-11`; `full200_audit`; `200` rows.
- Pipeline: `exectv2_llm_only_per_entity`; mode `live`; replay `live`.
- Model role: ExECTv2 Phase 7 frozen full-200 SF audit (llm_only_per_entity/per_entity).; model `openai/gpt-4.1-mini`.
- Primary metrics: authorization=full-200 read authorized by user 2026-06-11 (Phase 7), call_failures=0, git_head=ab0d8d5cb7aa, parse_failures=0, phrase_only_per_item_f1=0.4627, phrase_only_per_letter_f1=0.6766, prompt_version=exectv2_llm_only_per_entity_v0.2, sf_benchmark_per_item_ci=[0.0, 0.0], sf_benchmark_per_item_f1=0.0, sf_benchmark_per_letter_ci=[0.0, 0.0], sf_benchmark_per_letter_f1=0.0, sf_semantic_per_item_f1=0.1216, sf_semantic_per_letter_f1=0.2463.
- Evidence validity: frozen audit; gates recorded in the audit report.
- Claim language: Phase 7 frozen SF audit over all 200 letters (authorized 2026-06-11). Headline sf_benchmark per-item F1 0.000 (CI 0.000-0.000), per-letter F1 0.000 (CI 0.000-0.000) vs published 0.66/0.68. Immutable; locked at git ab0d8d5cb7aa.
- Artifacts: `experiments/archive/gan2026_historical_lineage/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.md`, `experiments/exectv2_audit_llm_only_per_entity_full200_gpt41mini_20260611.jsonl`.

### `exectv2_audit_hybrid_full200_gpt41mini_20260611`
- Date/split: `2026-06-11`; `full200_audit`; `200` rows.
- Pipeline: `exectv2_hybrid`; mode `live`; replay `live`.
- Model role: ExECTv2 Phase 7 frozen full-200 SF audit (hybrid).; model `openai/gpt-4.1-mini`.
- Primary metrics: authorization=full-200 read authorized by user 2026-06-11 (Phase 7), call_failures=0, git_head=ab0d8d5cb7aa, parse_failures=0, phrase_only_per_item_f1=0.5482, phrase_only_per_letter_f1=0.7778, prompt_version=exectv2_hybrid_candidate_assessment_v0.2, sf_benchmark_per_item_ci=[0.1924, 0.3008], sf_benchmark_per_item_f1=0.2458, sf_benchmark_per_letter_ci=[0.3874, 0.5462], sf_benchmark_per_letter_f1=0.4696, sf_semantic_per_item_f1=0.2458, sf_semantic_per_letter_f1=0.4696.
- Evidence validity: frozen audit; gates recorded in the audit report.
- Claim language: Phase 7 frozen SF audit over all 200 letters (authorized 2026-06-11). Headline sf_benchmark per-item F1 0.246 (CI 0.192-0.301), per-letter F1 0.470 (CI 0.387-0.546) vs published 0.66/0.68. Immutable; locked at git ab0d8d5cb7aa.
- Artifacts: `experiments/archive/gan2026_historical_lineage/exectv2_audit_hybrid_full200_gpt41mini_20260611.md`, `experiments/exectv2_audit_hybrid_full200_gpt41mini_20260611.jsonl`.

### `gan2026_llm_heavy_clinical_frequency_reasoner_v1_validation50_live_2026-06-02`
- Date/split: `2026-06-02`; `validation`; `50` rows.
- Pipeline: `llm_heavy_clinical_frequency_reasoner`; mode `live validation50 output-contract gate with first 25 rows reused after alias repair`; replay `cache_first`.
- Model role: LLM-heavy extraction, clinical selection, and scoring-schema renderer; model `openai/gpt-4.1-mini`.
- Repair mode/config: `v1 prompt/schema plus non-semantic enum/unit alias repair; score layers raw_llm, format_only, selected_evidence_arithmetic, benchmark_aligned, oracle_format_upper_bound`.
- Primary metrics: benchmark_aligned_purist_correct=45, call_failures=0, event_evidence_total=125, event_evidence_valid=120, format_only_purist_correct=41, parse_failures=0, raw_llm_purist_correct=41, raw_llm_scorable=45, row_count=50, selected_event_trace_mismatches=1, selected_evidence_arithmetic_purist_correct=48, selected_evidence_valid=48, structured_records=50.
- Evidence validity: Selected evidence exact 48/50; event evidence exact 120/125; one selected-event trace mismatch.
- Cache/reuse source: Reused first 25 raw outputs from the interrupted validation50 checkpoint, then ran rows 26-50 live with DSPy cache enabled.
- Supersedes: `gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02`.
- Claim language: Validation50 passed the v1 output-contract gate, but raw/format-only Purist was only 41/50; escalation to validation250 was diagnostic, not promotional.
- Artifacts: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation50_gpt41mini_v1_2026-06-02.jsonl`, `experiments/archive/gan2026_historical_lineage/gan2026_llm_heavy_clinical_frequency_reasoner_validation50_gpt41mini_v1_2026-06-02.md`.

### `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_generalization_audit_2026-06-02`
- Date/split: `2026-06-02`; `validation+test`; `1200` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `frozen generalization audit with cluster_diary_candidate_recall`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `cluster_diary_candidate_recall + conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: test_candidate_set_purist_recall=359, test_correct_to_wrong=9, test_deterministic_purist_correct=343, test_gated_pragmatic_correct=353, test_gated_purist_correct=343, test_wrong_to_correct=9, validation_candidate_set_purist_recall=707, validation_deterministic_purist_correct=697, validation_gated_pragmatic_correct=686, validation_gated_purist_correct=677.
- Evidence validity: Aggregate and slice-level locked-test audit only; no test row text inspection for tuning.
- Cache/reuse source: DSPy cache enabled; validation/test artifacts recorded 0 reused raw outputs.
- Supersedes: `gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_case_component_stress_2026-06-01`.
- Claim language: Frozen comparator-only generalization audit. Do not tune v0.2 gates, prompts, candidate generation, or repair policy from locked-test behavior; use the state-graph validation cycle for new development.
- Artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation750_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`, `experiments/archive/gan2026_historical_lineage/gan2026_hybrid_rules_candidates_llm_adjudicator_validation750_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.md`, `experiments/archive/gan2026_historical_lineage/gan2026_generalization_gap_research_report_2026-06-02.md`.

### `gan2026_llm_structured_v05_attribution_repair_ladder650_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `650` rows.
- Pipeline: `llm_structured_events`; mode `saved-output repair-family attribution ladder over structured v0.5 outputs`; replay `saved_output_replay`.
- Model role: analysis-only attribution and deterministic repair-family replay; model `none; saved openai/gpt-4.1-mini outputs only`.
- Registry roles: `negative_attribution`, `historical_lineage`.
- Repair mode/config: `raw_model_selection + strict_format + frozen_clean_policy + named deterministic semantic repair families`.
- Primary metrics: clean_policy_purist_correct=438, full_stack_pragmatic_correct=598, full_stack_purist_correct=588, raw_purist_correct=394, row_count=650, selected_evidence_repair_purist_correct=546, strict_format_purist_correct=413.
- Evidence validity: Saved-output replay keeps exact selection evidence at 619/650 from the audited source; repair-family attribution separates evidence validity from final-label ownership.
- Cache/reuse source: Saved raw output source: experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl.
- Supersedes: `gan2026_llm_structured_v05_full_validation_2026-06-01`.
- Claim language: Backfilled attribution ladder. Clean attribution ends at 438/650 Purist under frozen clean policy; full 588/650 stack is hybrid deterministic post-processing, not clean LLM-first success.
- Artifacts: `experiments/archive/gan2026_historical_lineage/gan2026_llm_structured_validation750_v05_repair_audit_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.json`, `experiments/archive/gan2026_historical_lineage/gan2026_llm_structured_validation750_v05_repair_ablation_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_basic_split_repair_ablation_2026-06-01.json`, `experiments/archive/gan2026_historical_lineage/gan2026_llm_structured_validation750_v05_basic_split_repair_ablation_2026-06-01.md`, `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.json`, `experiments/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.csv`, `experiments/archive/gan2026_historical_lineage/gan2026_llm_structured_validation750_v05_strict_format_regression_audit_2026-06-01.md`, `experiments/gan2026_clean_policy_freeze_ladder650_v0_2026-06-01.json`, `experiments/archive/gan2026_historical_lineage/gan2026_clean_policy_freeze_ladder650_v0_2026-06-01.md`, `experiments/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.json`, `experiments/archive/gan2026_historical_lineage/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.md`, `experiments/gan2026_combined_attribution_repair_ladder650_v0_2026-06-01.json`, `experiments/archive/gan2026_historical_lineage/gan2026_combined_attribution_repair_ladder650_v0_2026-06-01.md`.

### `gan2026_hybrid_adjudicator_v02_validation50_live_2026-06-01`
- Date/split: `2026-06-01`; `validation`; `50` rows.
- Pipeline: `hybrid_rules_candidates_llm_adjudicator`; mode `live rules candidates then conservative LLM adjudicator`; replay `live`.
- Model role: hybrid adjudicator over deterministic candidates; model `openai/gpt-4.1-mini`.
- Repair mode/config: `conservative_overreach_gates + deterministic_fallback`.
- Primary metrics: adjudicator_pragmatic_correct=49, adjudicator_purist_correct=48, call_failures=0, changed_final_labels=3, deterministic_correct_to_adjudicator_wrong=2, deterministic_pragmatic_correct=50, deterministic_purist_correct=50, deterministic_wrong_to_adjudicator_correct=0, parse_failures=0, row_count=50.
- Evidence validity: Deterministic candidate evidence 50/50 exact in component ablation; raw/gated adjudicator evidence not independently scored in this artifact.
- Cache/reuse source: DSPy cache enabled; run recorded 0 reused raw outputs.
- Claim language: Validation50 is output-contract clean but the prefix is saturated; 2 deterministic-correct Purist regressions are a row-review note, not enough evidence for a revise decision. Escalate to 250 rows before tuning gates.
- Artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.jsonl`, `experiments/archive/gan2026_historical_lineage/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_v02_live_component_ablation_2026-06-01.json`, `experiments/archive/gan2026_historical_lineage/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_v02_live_component_ablation_2026-06-01.md`.

### `gan2026_rules_only_v1_test_holdout_2026-05-31`
- Date/split: `2026-05-31`; `test`; `450` rows.
- Pipeline: `rules_only`; mode `locked-test holdout evaluation of frozen rules_only_v1`; replay `analysis_only`.
- Model role: deterministic comparator; model `none`.
- Registry roles: `holdout_anchor`.
- Repair mode/config: `deterministic_v1; no test-row tuning or row-level text inspection`.
- Primary metrics: rows=450, test_pragmatic_f1=0.7867, test_purist_f1=0.76, validation_purist_f1_context=0.9293.
- Evidence validity: Aggregate holdout report; no test row-level debugging allowed.
- Supersedes: `gan2026_rules_only_v1_baseline_2026-05-31`.
- Claim language: Final holdout result for frozen deterministic V1 only; useful as generalization context, not a benchmark-comparable paper claim or tuning surface.
- Artifacts: `experiments/gan2026_v1_test_holdout_2026-05-31.md`.

### `gan2026_rules_only_v1_baseline_2026-05-31`
- Date/split: `2026-05-31`; `validation+test`; `1200` rows.
- Pipeline: `rules_only`; mode `rules_only_v1`; replay `analysis_only`.
- Model role: deterministic comparator; model `none`.
- Repair mode/config: `deterministic_v1`.
- Primary metrics: test_pragmatic=0.7867, test_purist=0.76, validation_pragmatic=0.9387, validation_purist=0.9293.
- Evidence validity: Report-level deterministic evidence summary.
- Claim language: Frozen rules_only_v1 comparator; aggregate locked-test context is historical, not a tuning surface.
- Artifacts: `experiments/archive/gan2026_historical_lineage/gan2026_v1_deterministic_baseline_2026-05-31.md`.

### `gan2026_dspy_adjudicator_devset_v04_2026-05-31`
- Date/split: `2026-05-31`; `validation_devset`; `16` rows.
- Pipeline: `dspy_final_selection_adjudicator`; mode `live validation-only dev-set adjudicator run`; replay `live`.
- Model role: final-selection adjudicator over deterministic V1 diagnostics; model `openai/gpt-4.1-mini`.
- Repair mode/config: `frozen deterministic V1 diagnostics; no scorer or split-policy change`.
- Primary metrics: call_failures=0, parse_failures=0, pragmatic_correct=12, purist_correct=9, row_count=16.
- Evidence validity: Uses deterministic V1 candidate diagnostics from validation-mined dev set; no locked-test row failures inspected.
- Claim language: Early validation-only DSPy adjudicator diagnostic. Kept as lineage for later hybrid adjudicator work; not a promoted candidate or benchmark result.
- Artifacts: `experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl`, `experiments/archive/gan2026_historical_lineage/gan2026_v1_prompt_adjudicator_devset_2026-05-31.md`, `experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_v04_2026-05-31.jsonl`, `experiments/archive/gan2026_historical_lineage/gan2026_v1_dspy_adjudicator_devset_gpt41mini_v04_2026-05-31.md`.

## Calibration Measure Val To Test Gap

### `gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16`
- Date/split: `2026-06-16`; `test`; `450` rows.
- Pipeline: `llm_only_direct_labeler`; mode `live`; replay `live`.
- Model role: LLM-only direct-labeler note-to-label extractor (prompt v0.5); deterministic code limited to label repair, evidence validation, and scoring after the model emits the final label.; model `openai/gpt-4.1-mini`.
- Registry roles: `holdout_anchor`.
- Repair mode/config: `llm_only_label_repair`.
- Primary metrics: call_failures=0, decision_records=450, evidence_valid_rows=422, max_tokens=900, parse_or_validation_failures=0, pragmatic_accuracy=0.7867, pragmatic_correct=354, prompt_version=gan2026_llm_only_direct_labeler_v0.5, purist_accuracy=0.7222, purist_correct=325, temperature=0.0, val_to_test_gap_purist=0.0444, validation750_reference_purist_accuracy=0.7667, validation750_reference_purist_correct=575.
- Evidence validity: USER-AUTHORISED CALIBRATION measurement of the validation->test gap on gpt-4.1-mini, NOT a robustness-certified result. Candidate failed the Cycle 1 robustness battery and is NOT certified; it was run once only to obtain the first-ever mini test450 number. 422/450 rows carry an evidence_valid substring-presence trace; 0 call failures; 0 parse/schema/label failures; 450/450 decision records; all 450 rows split=test with unique source_row_index. No tuning on test, no re-run, no row-level failure inspection.
- Claim language: First-ever frozen test450 Purist for llm_only direct labeler v0.5 on gpt-4.1-mini. test450 Purist = 325/450 = 0.7222. validation750 reference (mini, v0.5) = 575/750 = 0.7667. val->test gap = +0.0444 (+4.44 pp); -20 rows vs the val-implied 345/450. Prior holdouts (incl. V12 379/450) used full gpt-4.1, not mini, so this is the first mini val->test anchor. Calibration only; does not promote this candidate or change champion/robustness status.
- Artifacts: `experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16.jsonl`, `experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16.md`, `experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16_record.md`.
