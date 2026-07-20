# Shared reliability scorecard

Date: 2026-07-18  
Evidence mode: retained no-call replay and synthesis

Gan 2026 and ExECTv2 are assessed with the same eight reliability questions.
Each task keeps its own measurement object, denominator, scorer, output stage,
and claim boundary. No composite reliability score or pooled task ranking is
calculated.

This report is generated from
[`shared_reliability_scorecard_20260718.json`](../../experiments/shared_reliability_scorecard_20260718.json).
The exact selected sources and hashes are owned by the
[retained evidence index](../experiments/retained_evidence_manifest.md).

## Gan 2026 task scorecard

| Criterion | State | Strongest evidence | Result and limit |
| --- | --- | --- | --- |
| Clinical correctness and generalization | `measured` / `complete_for_recorded_scope` | `aggregate_holdout_evidence` | Six-model test450 Purist and Pragmatic accuracy plus the retained subject development/test comparison. |
| Clinical selection and unsupported inference | `measured` / `partial` | `aggregate_holdout_evidence` | Unknown-gold active-rate over-read is retained; selected denominator counts are absent from the compact source. |
| Evidence support and faithfulness | `measured` / `partial` | `aggregate_holdout_evidence` | Textual grounding is measured; independent semantic-support review is not selected. |
| Uncertainty and selective action | `measured` / `complete_for_recorded_scope` | `development_answer` | External-signal calibration and full risk-coverage results are retained for the named subject. |
| Robustness and stability | `measured` / `partial` | `development_answer` | Prompt-version and one-model repeated-temperature results cover named subdimensions only. |
| Component attribution and correction safety | `measured` / `partial` | `development_answer` | The shared normalization ablation is measured; the retained compact package does not reproduce every stage transition count. |
| Coverage and clinical-slice behavior | `measured` / `partial` | `development_answer` | Seizure-band variation is measured; demographic fairness is not measured. |
| Operational reliability | `measured` / `partial` | `aggregate_holdout_evidence` | Six-model failures and repairs plus a bounded historical cost estimate are measured; efficiency telemetry is unmatched. |

### Gan matched six-model test450 panel

| Model | Purist | Pragmatic |
| --- | ---: | ---: |
| GPT-4.1-mini | 353/450 | 371/450 |
| GPT-5.6 Luna | 352/450 | 365/450 |
| GPT-5.6 Sol | 358/450 | 376/450 |
| DeepSeek V4 Flash | 342/450 | 362/450 |
| Qwen 3.6:35B | 367/450 | 380/450 |
| Gemma 4 26B | 343/450 | 367/450 |

The panel is aggregate-only evidence on a previously used locked holdout.
Provider routes and temperatures differ, and the result is not a pristine
one-shot or general model-superiority comparison.

## ExECTv2 task scorecard

| Criterion | State | Strongest evidence | Result and limit |
| --- | --- | --- | --- |
| Clinical correctness and generalization | `measured` / `complete_for_recorded_scope` | `aggregate_holdout_evidence` | Six-model dev140 and aggregate-only test60 clinical-headline F1. |
| Clinical selection and unsupported inference | `not_measurable_current_data` / `blocked_by_data` | `diagnostic` | The predeclared unknown-only denominator is zero; empty-gold letters are not substitutes. |
| Evidence support and faithfulness | `measured` / `partial` | `aggregate_holdout_evidence` | Final exact evidence is measured; a stratified semantic-support sample awaits independent review. |
| Uncertainty and selective action | `measured` / `partial` | `aggregate_holdout_evidence` | Internal scoring-rule calibration and a historical three-model negative routing result are retained. |
| Robustness and stability | `measured` / `partial` | `aggregate_holdout_evidence` | Six-model development-to-holdout changes are measured; perturbation robustness is not. |
| Component attribution and correction safety | `measured` / `complete_for_recorded_scope` | `development_answer` | Six-model score stages, historical family regressions, and SF correction transitions remain separate. |
| Coverage and clinical-slice behavior | `measured` / `partial` | `development_answer` | All four fixed families are reported for six models; demographic fairness is not measured. |
| Operational reliability | `measured` / `partial` | `aggregate_holdout_evidence` | Six-model test60 completion and parse/schema behavior are retained with hosted/local routes separate. |

### ExECT fixed six-model panel

| Model | dev140 F1 | test60 F1 | Change |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8202 | 0.7572 | -0.0630 |
| GPT-5.6 Luna | 0.8832 | 0.7950 | -0.0882 |
| GPT-5.6 Sol | 0.8920 | 0.8047 | -0.0873 |
| DeepSeek V4 Flash | 0.8767 | 0.7881 | -0.0886 |
| Qwen 3.6:35B | 0.8571 | 0.7872 | -0.0699 |
| Gemma 4 26B | 0.8016 | 0.7169 | -0.0847 |

The test60 values are aggregate-only internal-score results over 59 loadable
letters. `clinical_headline` is not the published ExECT benchmark, and these
results are not clinical validation. Hosted and local runtime routes remain
separate conditions.

The six-model SF component replay records
54 wrong-to-correct and
1 correct-to-wrong transitions. The 840
model-letter rows repeat the same 140 letters and are descriptive, not 840
independent clinical samples. The predeclared unknown-only denominator is zero;
empty-gold letters were not relabelled as unknown.

## Cross-task criterion matrix

| Criterion | Comparability | Numerical delta | Reason |
| --- | --- | ---: | --- |
| Clinical correctness and generalization | `construct_only` | — | The tasks answer the same criterion with task-specific measurement objects or units. |
| Clinical selection and unsupported inference | `not_comparable` | — | ExECT has no valid unknown-only denominator. |
| Evidence support and faithfulness | `construct_only` | — | The tasks answer the same criterion with task-specific measurement objects or units. |
| Uncertainty and selective action | `construct_only` | — | The tasks answer the same criterion with task-specific measurement objects or units. |
| Robustness and stability | `construct_only` | — | The tasks answer the same criterion with task-specific measurement objects or units. |
| Component attribution and correction safety | `construct_only` | — | The tasks answer the same criterion with task-specific measurement objects or units. |
| Coverage and clinical-slice behavior | `construct_only` | — | The tasks answer the same criterion with task-specific measurement objects or units. |
| Operational reliability | `construct_only` | — | The tasks answer the same criterion with task-specific measurement objects or units. |

## Evidence-state and comparability matrix

| Criterion | Gan evidence | ExECT evidence | Comparability |
| --- | --- | --- | --- |
| Clinical correctness and generalization | `aggregate_holdout_evidence` | `aggregate_holdout_evidence` | `construct_only` |
| Clinical selection and unsupported inference | `aggregate_holdout_evidence` | `diagnostic` | `not_comparable` |
| Evidence support and faithfulness | `aggregate_holdout_evidence` | `aggregate_holdout_evidence` | `construct_only` |
| Uncertainty and selective action | `development_answer` | `aggregate_holdout_evidence` | `construct_only` |
| Robustness and stability | `development_answer` | `aggregate_holdout_evidence` | `construct_only` |
| Component attribution and correction safety | `development_answer` | `development_answer` | `construct_only` |
| Coverage and clinical-slice behavior | `development_answer` | `development_answer` | `construct_only` |
| Operational reliability | `aggregate_holdout_evidence` | `aggregate_holdout_evidence` | `construct_only` |

## Unresolved dependencies

- `gan_selection_denominator_metadata` (documentation_instrumentation_gap): Keep the retained rates and mark their selected denominator counts unavailable. Unblock when Select a hash-verified machine artifact containing the original unknown-gold counts. The rate is reportable at its retained scope but the criterion remains incomplete.

- `exect_unsupported_selection_denominator` (independent_clinical_review_dependency): Keep the zero-denominator study as a closed diagnostic result. Unblock when Exhaustive independent review distinguishes unsupported predictions from omission, multiplicity, and accepted representation differences. No ExECT unsupported-selection rate or Gan-to-ExECT over-reading transfer claim is permitted.

- `gan_semantic_support_review` (independent_clinical_review_dependency): Do not equate exact source presence with semantic support. Unblock when A governed representative sample is independently reviewed at the reported decision stage. Gan evidence is described as textual grounding, not externally validated faithfulness.

- `exect_semantic_support_review` (independent_clinical_review_dependency): Retain the stratified sample as an unreviewed substrate only. Unblock when Independent reviewers complete the frozen fields with provenance and adjudication. Exact evidence remains separate from semantic support and clinical validation.

- `exect_six_model_uncertainty` (optional_new_experiment): Keep the historical three-model negative result bounded. Unblock when Adopt a named six-model routing claim before writing and running a separate protocol. No six-model or deployment-calibration conclusion is permitted.

- `gan_broad_robustness` (optional_new_experiment): Do not commission perturbation calls merely to fill the framework. Unblock when A named paper claim requires a predeclared perturbation result. Robustness wording remains limited to the recorded prompt and sampling subdimensions.

- `exect_broad_robustness` (optional_new_experiment): Treat dev-to-test and parser/runtime behavior as separate subdimensions. Unblock when A claim-changing protocol predeclares clinically equivalent wording or prompt perturbations. The six-model split change is not called perturbation robustness or self-consistency.

- `gan_full_stage_transition_inventory` (documentation_instrumentation_gap): Report the selected normalization ablation and preserve the stage boundary without reconstructing missing row transitions. Unblock when A no-call retained artifact exposes all stage transitions under the locked-row policy. No new stage-specific correction-safety count is claimed.

- `gan_demographic_fairness` (outside_project_boundary): Do not relabel seizure-band variation as demographic fairness. Unblock when Suitable attributes, sample sizes, and a clinically meaningful fairness question exist. Demographic fairness is not measured.

- `exect_demographic_fairness` (outside_project_boundary): Do not relabel entity-family variation as demographic fairness. Unblock when Suitable attributes, sample sizes, and a clinically meaningful fairness question exist. Demographic fairness is not measured.

- `gan_matched_efficiency_telemetry` (outside_project_boundary): Do not reconstruct unmatched token, cost, latency, hardware, or retry values. Unblock when A matched protocol measures the selected conditions prospectively. Only observed failures, repairs, pass counts, and the bounded offline estimate are reportable.

- `exect_matched_efficiency_telemetry` (outside_project_boundary): Keep hosted and local runtime conditions separate and do not rank efficiency. Unblock when A matched protocol records latency, usage, hardware, retries, and cache state. No cross-route efficiency ranking is permitted.

## Claim boundary

Shared questions with task-specific retained measures. The artifact does not establish a shared metric, cross-task transfer, demographic fairness, deployment reliability, or independent clinical validation.

Exact source presence is not semantic support. Internal review is not
independent clinical validation. Construct-only and not-comparable cells do not
produce cross-task numerical differences. No composite score is reported.

<!-- MACHINE SYNCHRONIZATION MARKERS; generated, do not edit -->
<!-- measurement:gan2026_six_model_test450_purist_accuracy:7a4a3a802ee663cbb142aedb8e51405fc41be6de38a67253eb32af9328da8ba5 -->
<!-- measurement:gan2026_six_model_test450_pragmatic_accuracy:dc3cf80e0695bad91d5cf450e97b925868107d323745f2a534fc31e63c34ff50 -->
<!-- measurement:gan2026_subject_validation750_purist_accuracy:03e28a91a7b4f394eff12e4692ff147c15e750a219b2f6fd8a55ea43f68c73cf -->
<!-- measurement:gan2026_subject_test450_purist_accuracy:b4776790a0149f107b381082b0d55137203daeb57a9b3758e4ced56488cb71b0 -->
<!-- measurement:exectv2_six_model_dev140_clinical_headline_f1:20863c01dfe365fd30bf6cf0b9f8ce4f5da0cd6d081afd9914f918c986641575 -->
<!-- measurement:exectv2_six_model_test60_clinical_headline_f1:e6ca9d6af74532cf57920530579ea446a540e59baac70474f1ac4174ea1ca168 -->
<!-- measurement:gan2026_unknown_gold_active_rate_overread_rate:60e7c73aefa66bf981ce5f4c493d672f272bdd1bb8a84d59f21d7f9f4a1645f8 -->
<!-- measurement:exectv2_sf_unknown_only_active_rate_overread_rate:4873efb59c40600ccd667b3310f965fe264e125a1d3e44098c3f32fced8e1688 -->
<!-- measurement:gan2026_textual_grounding_rate:c12e57a6f552a30c8e9ef0bb5bed66df62afa1472654d005b52a4f57e0396ebc -->
<!-- measurement:gan2026_semantic_support_review:9fdf8100fe09d7042f6c7e5ee5b098bde73f26d8c324cd9767118960874dc920 -->
<!-- measurement:exectv2_final_exact_evidence_rate:ae648bde9c8a0c0cb47e301468d7e738d18700d321adb60101211bef9a8bf84f -->
<!-- measurement:exectv2_semantic_support_review:81eb4323b1b00371192d5e99b47b12e0bb27054b62244cf9bdd48088b2165bdf -->
<!-- measurement:gan2026_external_signal_calibration:9690d1a2a1a9de6f4cae3eb38882d755db226e9ce1350514348e33956c92671a -->
<!-- measurement:gan2026_risk_coverage:86bb99dcb427e71583b1c416a766460ac125f545cc47bd68b9546555e64c832d -->
<!-- measurement:exectv2_internal_scoring_rule_calibration:f6aa9eb6848b29c942c0048acfebe698d00ad71de2a35567ef38c37bdecabc2a -->
<!-- measurement:exectv2_historical_model_reported_confidence_failure_auroc:fa52512fc87fead1e38d5eb640be80ae6f17fe74a293afcba04d6738255496e7 -->
<!-- measurement:gan2026_prompt_version_robustness_index:f4965e5544068a713ba7b8938f06b00fb8724f4806d11240e63a78dc8d1665f6 -->
<!-- measurement:gan2026_repeated_temperature_semantic_entropy:b13ebe5d5851bc224394d3934e8d731272aaeb64a752cdf137ddac0da7a5fe0e -->
<!-- measurement:exectv2_six_model_dev_to_test_f1_change:54aa71b66f375426d76d2f99c59d0ecb4ab2de19554ab2437034d02682743eef -->
<!-- measurement:gan2026_validation750_normalization_component_delta:01234496dcb5d3161f32c963cef3a1da3d83902eab5c8f95a8ada5c39d22e236 -->
<!-- measurement:exectv2_dev140_normalization_component_delta:0399f86b248be1ef232373e33027d1f5e71522d6ae40c5e92f0006229ab819a8 -->
<!-- measurement:exectv2_six_model_score_stage_f1:0adc9b70ded8d26573559eb0b41180a4bf61aa8b481d674f106829ef763ad80f -->
<!-- measurement:exectv2_historical_deterministic_correction_transitions:ab045fb9cca4941198e8f8d05532a9cf3743b2b49c7d7a67f9f7ad03c1e10ce6 -->
<!-- measurement:exectv2_six_model_sf_correction_transitions:bf7fb62013a6ad7480deab8a1028bba363e42cb4690546cc23dc72f146f2cf6e -->
<!-- measurement:gan2026_seizure_band_error_variation:46b981e1b9c30d71f840ceccfeddab1a10a2cfb8a0e5bafc132fdbb4cbc86347 -->
<!-- measurement:gan2026_demographic_fairness:9fdf8100fe09d7042f6c7e5ee5b098bde73f26d8c324cd9767118960874dc920 -->
<!-- measurement:exectv2_six_model_dev140_family_f1:1534f084d8336e01dfdec906aac05c650e939b20e757fbdec06f87fd1dd41b7c -->
<!-- measurement:exectv2_demographic_fairness:9fdf8100fe09d7042f6c7e5ee5b098bde73f26d8c324cd9767118960874dc920 -->
<!-- measurement:gan2026_historical_operational_summary:27374eeaa1efc7973ccdcce8f77635df7d238c604c6765f3ee2b09e2a48c923f -->
<!-- measurement:gan2026_six_model_test450_operational_events:2aeea8d8b180505755e3339cdcb2af69f699b15a9195d221d72015600195cae9 -->
<!-- measurement:exectv2_six_model_test60_operational_events:8d83ed44dcad4a5a677c350f11968fb5ddd5cb26c6d13e9ee376ec7b258ea3a6 -->
