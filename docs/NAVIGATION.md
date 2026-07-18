# Documentation navigation

## Current work

| Need | Read |
| --- | --- |
| Current outcome and checks | [project status](../PROJECT_STATUS.md) |
| Ordered next work | [active roadmap](plans/ACTIVE_ROADMAP.md) |
| Cleanup history and measurements | [repository cleanup record](research/maintenance/repository_surgery_assessment_2026-07-14.md) |

## Evidence and claims

| Need | Read |
| --- | --- |
| Selected files, hashes, and replay requirements | [retained evidence index](experiments/retained_evidence_manifest.md) |
| Strength of paper claims | [paper claim status](canon/10_paper_provenance.md) |
| Gan evidence and holdout rules | [Gan evidence summary](canon/06_gan_clinical_policy.md) |
| Gan hosted test450 protocol and result | [hosted Gan result](experiments/gan2026/gan2026_hosted_test450_protocol_2026-07-15.md) |
| Gan matched v0.5 test450 protocol and aggregate | [v0.5 protocol](experiments/gan2026/gan2026_matched_v05_test450_protocol_2026-07-16.md) and [aggregate artifact](../experiments/gan2026_matched_v05_test450_aggregate_20260716.json) |
| Gan quality and model-pass comparison | [Gan efficiency result](research/gan2026/efficiency/gan2026_single_vs_multimodel_efficiency_report_2026-07-14.md) |
| ExECT evidence | [ExECT evidence summary](canon/07_exect_plan11.md) |
| ExECT hosted test60 protocol and result | [hosted ExECT result](experiments/exectv2/reliability/exectv2_hosted_test60_protocol_2026-07-15.md) |
| Six-model cross-task comparison | [comparison report](research/six_model_comparison_report_2026-07-18.md) |
| ExECT six-model SF over-inference | [protocol](experiments/exectv2/reliability/exectv2_six_model_sf_overinference_protocol_2026-07-18.md) and [result](experiments/exectv2/reliability/exectv2_six_model_sf_overinference_2026-07-18.md) |
| ExECT paper-derived metric result | [published-metric replay](experiments/exectv2/reliability/exectv2_published_metric_reproduction_results_2026-07-14.md) |
| ExECT Diagnosis review and component result | [Diagnosis component comparison](experiments/exectv2/diagnosis/exectv2_diagnosis_component_comparison_2026-07-14.md) |
| Guide to the different ExECT Diagnosis F1 scores | [Diagnosis score guide](experiments/exectv2/diagnosis/exectv2_diagnosis_score_guide_2026-07-14.md) |
| Three-model LLM-with-rules ownership and corrected aggregate | [LLM-with-rules component audit](experiments/exectv2/reliability/exectv2_llm_with_rules_component_audit_2026-07-14.md) |
| Dev140 deterministic benefit and regression mechanisms | [model-led regression analysis](experiments/exectv2/reliability/exectv2_model_led_dev140_regression_analysis_2026-07-15.md) |
| Bounded Prescription policy and residual rule groups | [Prescription candidate result](experiments/exectv2/reliability/exectv2_prescription_bounded_policy_candidate_2026-07-15.md) |
| Separate Diagnosis guard effects | [Diagnosis guard ablation](experiments/exectv2/reliability/exectv2_diagnosis_guard_ablation_2026-07-15.md) |
| Joint bounded policy versus the previous fallback | [Joint policy replay](experiments/exectv2/reliability/exectv2_joint_bounded_policy_replay_2026-07-15.md) |
| GPT-4.1-mini one-call versus two-call Diagnosis | [single-call Diagnosis ablation](experiments/exectv2/diagnosis/exectv2_gpt41mini_single_call_diagnosis_ablation_2026-07-15.md) |
| Scoring and annotation limits | [scoring rules](canon/04_scoring.md) |
| Combined annotation defects, conventions, ambiguity, scoring, sensitivity, and review status | [annotation-evidence synthesis](experiments/exectv2/reliability/exectv2_annotation_evidence_synthesis_2026-07-15.md) |
| Reliability across tasks | [cross-task reliability](canon/09_cross_task_reliability.md) |
| Detailed eight-criterion reliability result | [shared reliability scorecard](research/shared_reliability_scorecard_2026-07-18.md) |
| Pending ExECT semantic-support review sample | [review protocol](experiments/exectv2/reliability/exectv2_semantic_support_review_substrate_protocol_2026-07-18.md) |

## Implementation

| Need | Read |
| --- | --- |
| Package boundaries | [software design](design/architecture.md) |
| Data and split rules | [data rules](design/data_contract.md) and [Gan split rules](design/gan2026_split_protocol.md) |
| Component attribution | [component attribution](design/component_evidence_attribution_architecture.md) |
| Proposed pipeline trace explorer | [frontend and backend specification](design/pipeline_trace_explorer_spec.md) |
| Final ExECT family ownership | [decision 0040](decisions/0040-final-exect-llm-with-rules-family-ownership.md) |
| Single-call final comparison architecture | [decision 0041](decisions/0041-single-call-exect-model-comparison.md) |
| Model policy and final six-model roster | [model policy](design/model_strategy.md) and [decision 0039](decisions/0039-final-exect-six-model-roster.md) |
| Shared hosted Gan prompt | [decision 0043](decisions/0043-gan-hosted-comparison-uses-v05-prompt.md) |
| Evidence metric | [evidence groundedness](reference/evidence_groundedness_metric.md) |
| Shared reliability definitions | [reliability evaluation framework](design/reliability_evaluation_framework.md) and [decision 0044](decisions/0044-shared-reliability-criteria-use-task-specific-measures.md) |
| Procedures | [runbooks](runbooks/) |

Detailed experiment history is intentionally absent from the active tree. Use
Git history when the selected evidence is not enough.
