# Short reading paths

Use the shortest path that answers the question.

## Continue the project

[README](../README.md) → [status](../PROJECT_STATUS.md) →
[roadmap](plans/ACTIVE_ROADMAP.md)

## Replay current-stack six-model hybrid fills

[runbook](runbooks/current_stack_six_model_replay.md) →
[inventory](../experiments/current_stack/SOURCES.json) →
[living fills](../experiments/current_stack/latest/fills.json) →
[decision 0050](decisions/0050-current-stack-hybrid-primary-fills.md)

## Resume Decision 0048 after the 2026-08-02 pause

[Decision 0048](decisions/0048-comprehension-and-handoff-refactor.md) →
[status current point](../PROJECT_STATUS.md#decision-0048-current-point) →
[active milestone sequence](plans/ACTIVE_ROADMAP.md#active-comprehension-and-handoff-work) →
[regeneration and retention ledger](REGENERATION.md)

## ExECT SeizureFrequency projection (v0.14)

The extra-AR leftover campaign is closed at the practical floor.
Production owner is
[`sf_state_projection`](../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_state_projection.py)
v0.14. Landed ownership passes are the ordered `_OWNERSHIP_PASSES`
table; single last-event duration lives in the state pass. Do not
reopen without a gold-free leftover-only predicate. Cleanup record owns the dated predicate notes (pruned from the
working tree; recover from Git history if needed).
Live over-read guard:
[sf_active_rate_overread_guard](research/exectv2/sf_active_rate_overread_guard_2026-08-11.md).

## Rules-only Investigations result binding

Standalone Investigations now binds List 9 findings instead of emitting
bare modality tokens. Selected fills: `dev140` **0.8982**
(Investigations 0.9579); aggregate-only `test60` **0.7918**
(Investigations 0.8706). Hybrid Investigations is still a no-op.

Owner:
[result-binding report](research/exectv2/rules_only_investigations_result_binding_2026-08-15.md).

## Rules-only parity campaign

Closed 2026-08-15. ExECT E0–E5 and Gan G0–G5 are complete. Selected
ExECT rules fills are `dev140` **0.9042** / `test60` **0.7937**. Gan
rules holdout stays **329/450 (0.7311)**. Not next work.

Owner:
[E5 remasure](research/exectv2/rules_only_campaign_e5_remeasure_2026-08-15.md);
[G5 remasure](research/gan2026/rules_only_campaign_g5_remeasure_2026-08-15.md).

## ExECT structured-prompt v10

The live six-model prompt is `v0.9.24`. Topology-only v10 and the later
structured-prompt zoo are closed and pruned. Successor direction is
Fork A / the three assigned hybrid slots, not a prompt add-back.

Owner:
[Decision 0054](decisions/0054-model-request-order-and-metadata-are-explicit.md);
[prompt variant slots](research/exectv2/prompt_variant_slots_2026-08-16.md).

## ExECT LLM representation (Fork A)

Abandoned semantic-inventory / mention-unit v1 lanes are pruned.
Mention-unit v2 on frozen `dev20` is an answer: gold SF wording
appears as `clinical_name`; empty-gold extras did not rise. The
frozen-language `dev140` transfer is a revise: wording still copies
(131/187); empty-gold extras rose versus earlier Fork A baselines.
The extras catalog is an answer: more frequency statements on shared
empty-gold letters, not more over-read letters. The hybrid encoder
catalog is an answer: names stay; counts and investigation results
do not. The leftover-form remasure is an answer: leftover evidence
words recover form (SF with a count 58→130; Ix Unknown 61→2). The
leftover-form v2 four-arm remasure is a revise: each knob moves the
named leftover and each has a named side effect. Leftover-form v3
intervening-counts-only is an answer: SF-with-count 130→164 and the
three predeclared false-read classes stay out. Leftover-form v4
episodes and implicit period v4 are answers; last-event v4 revises.
Default
encoder stays landed. This prompt is ExECT current-hybrid slot 3.
[Assignment](research/exectv2/prompt_variant_slots_2026-08-16.md).

Owner:
[plan](plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md);
[prompt fundamentals](plans/exect_prompt_fundamentals_2026-08-16.md);
[leftover-form v4](research/exectv2/mention_unit_v2_leftover_form_v4_luna_dev140_2026-08-16.md);
[leftover-form v3](research/exectv2/mention_unit_v2_leftover_form_v3_luna_dev140_2026-08-16.md);
[leftover-form v2](research/exectv2/mention_unit_v2_leftover_form_v2_luna_dev140_2026-08-16.md);
[leftover-form](research/exectv2/mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md);
[hybrid encoder](research/exectv2/mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md);
[extras catalog](research/exectv2/mention_unit_v2_empty_gold_sf_extras_luna_dev140_2026-08-16.md);
[mention-unit v2 `dev140`](research/exectv2/mention_unit_v2_fork_a_luna_dev140_2026-08-16.md);
[mention-unit v2](research/exectv2/mention_unit_v2_fork_a_luna_dev20_2026-08-16.md);
[decision 0055](decisions/0055-exect-semantic-inventory-and-method-contracts.md).

## ExECT current-hybrid prompt variants

Three retained prompts inside the selected one-call hybrid. Live
default stays `v0.9.24`. Cheap stack and mention-unit v2 are named
variants, not selected stacks. Slot 2 is now the stacked further
prune (`v0.9.44`). The three-model `dev140` remasure is in progress.

Owner:
[assignment](research/exectv2/prompt_variant_slots_2026-08-16.md);
[cheap stack](research/exectv2/v0924_cheap_stack_luna_dev20_2026-08-16.md);
[plain remasure](research/exectv2/v0924_cheap_stack_plain_luna_dev20_2026-08-16.md);
[cheap-stack `dev140`](research/exectv2/v0924_cheap_stack_luna_dev140_2026-08-16.md);
[further prune](research/exectv2/v0924_cheap_further_prune_luna_dev20_2026-08-16.md);
[stacked further prune](research/exectv2/v0924_cheap_further_prune_stacked_luna_dev20_2026-08-17.md);
[slot-2 `dev140`](research/exectv2/v0924_cheap_slot2_dev140_protocol_2026-08-17.md);
[mention-unit v2](research/exectv2/mention_unit_v2_fork_a_luna_dev20_2026-08-16.md);
[REGENERATION.md](REGENERATION.md).

## ExECT `v0.9.24` leave-one-out prune

Keep the selected prompt. Leave-one-out: scope is load-bearing;
scaffold, examples, and encoding are each low-value. Cumulative:
scaffold plus examples is load-bearing. Scope-cluster: both
SeizureFrequency jobs are load-bearing; diagnosis and Rx/Ix scope
are not. Non-SF encoding, non-SF examples, and both SF example clusters are
each low-value. Stacking non-SF encoding with all examples is
load-bearing on SF and is the retained cheap prompt variant, not the
default. The authorized Luna `dev140` transfer stays **load_bearing**
on net four-family exact losses (−6). Three further cuts of that
cheap stack on Luna `dev20` are each **low_value** versus the cleaned
cheap payload. Stacking those three cuts stays **low_value** versus
the same cheap stack. Live default stays `v0.9.24`. The three current-hybrid
slots are assigned in
[prompt variant slots](research/exectv2/prompt_variant_slots_2026-08-16.md).

Owner:
[protocol](research/exectv2/v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md);
[report](research/exectv2/v0924_prompt_ablation_luna_dev20_2026-08-16.md);
[cumulative report](research/exectv2/v0924_cumulative_prune_luna_dev20_2026-08-16.md);
[scope-cluster](research/exectv2/v0924_scope_cluster_luna_dev20_2026-08-16.md);
[non-SF](research/exectv2/v0924_non_sf_slice_luna_dev20_2026-08-16.md);
[SF examples](research/exectv2/v0924_sf_examples_luna_dev20_2026-08-16.md);
[cheap stack](research/exectv2/v0924_cheap_stack_luna_dev20_2026-08-16.md);
[plain remasure](research/exectv2/v0924_cheap_stack_plain_luna_dev20_2026-08-16.md);
[cheap-stack `dev140`](research/exectv2/v0924_cheap_stack_luna_dev140_2026-08-16.md);
[further prune](research/exectv2/v0924_cheap_further_prune_luna_dev20_2026-08-16.md);
[stacked further prune](research/exectv2/v0924_cheap_further_prune_stacked_luna_dev20_2026-08-17.md).

## ExECT prompt-convention migration

Closed and pruned. Annotator codebook items moved into attributable
hybrid code; intermediate v11–v27 drafts, campaign notes, and one-off
runners are removed (recover from Git history). Live default stays
`v0.9.24`.

Owner:
[decision 0054](decisions/0054-model-request-order-and-metadata-are-explicit.md);
[prompt variant slots](research/exectv2/prompt_variant_slots_2026-08-16.md).

## Gan structured-prompt lineage

Closed 2026-08-15. Selected `gan2026_hybrid_structured_events_v0.5`
is the original 13-instruction contract, not an ExECT-style pile.
`v0.6` / `v0.7` / `v0.8_*` are named model-specific add-ons already
quarantined by Decision 0043. No Gan `v10`. No holdout inspection.

Owner:
[report](research/gan2026/structured_prompt_lineage_2026-08-15.md).

`final` (`gan2026_hybrid_structured_events_final`) drops the remaining
envelope identity strings. Luna `dev20`: no large drop (19/20 vs
19/20). Luna `dev750`: no large drop (660/750 vs 663/750, −3). Not
selected. Owner:
[decision 0053](decisions/0053-gan-structured-events-final-prompt.md);
[dev20 run](research/gan2026/structured_prompt_final_luna_dev20_2026-08-15.md);
[dev750 run](research/gan2026/structured_prompt_final_luna_dev750_2026-08-15.md).

## Qwen rescue overfiring audit

Closed 2026-08-15. First remasure used July 18 v0.7 by error; code now
requires matched v0.5. The inexact-span family-rewrite split landed
the same day. Holdout aggregate: Qwen 364→361, other selected models 0.

Owner:
[audit](research/gan2026/qwen_rescue_overfiring_2026-08-15.md);
[landing](research/gan2026/inexact_span_family_rewrite_2026-08-15.md).

## Task-shape basics and category-cut competence

[research index](research/README.md) →
[framework](research/shared/task_shape_framework_2026-08-06.md) →
[why the two programmes annotated differently](research/shared/annotation_approach_comparison_2026-08-16.md) →
[Gan gold taxonomy](research/gan2026/gold_task_taxonomy_2026-08-06.md) →
[ExECT gold taxonomy](research/exectv2/gold_task_taxonomy_2026-08-06.md) →
[x/y/z performance by category](research/shared/six_model_category_cut_performance_2026-08-06.md) →
[sealed holdout category aggregates](research/shared/six_model_holdout_category_aggregates_2026-08-06.md)
([unlock protocol](research/shared/six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md);
[restore runbook](runbooks/restore_sealed_holdout_ledgers_for_category_cuts.md) if another machine lacks sealed trees) →
[paper claim-boundary packaging vs C16 / 0046](research/shared/paper_claim_boundary_hybrid_mechanism_c16_0046_2026-08-06.md) →
[Gan category error catalog + ablation](research/gan2026/category_error_catalog_2026-08-06.md) →
[Gan hybrid stage ablation](research/gan2026/hybrid_stage_ablation_2026-08-06.md) →
[Gan rule decomposition and mechanism audit](research/gan2026/rule_decomposition_and_mechanism_audit_2026-08-10.md) →
[ExECT within-family error catalog + ablation](research/exectv2/family_error_catalog_2026-08-06.md) →
[ExECT hybrid stage ablation](research/exectv2/hybrid_stage_ablation_2026-08-06.md) →
[ExECT Diagnosis residual removal study](research/exectv2/diagnosis_residual_additions_compensation_removal_2026-08-11.md) →
[model-compensating rule audit](research/shared/model_compensating_rule_audit_2026-08-11.md) →
[cross-task hybrid mechanism synthesis](research/shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md) →
[Gan unknown_sentinel clinical harm](research/gan2026/unknown_sentinel_clinical_harm_2026-08-06.md) →
[Gan unknown breakthrough LOO](research/gan2026/unknown_breakthrough_loo_2026-08-06.md) →
[ExECT Prescription lens counterfactual](research/exectv2/prescription_lens_counterfactual_2026-08-06.md) →
kept machine artifacts in
`experiments/six_model_category_cut_performance_20260806.json`,
`experiments/six_model_holdout_category_aggregates_20260806.json`,
`experiments/paper_claim_boundary_hybrid_mechanism_c16_0046_20260806.json`,
`experiments/gan2026_hybrid_stage_ablation_20260806.json`,
`experiments/exectv2_family_error_catalog_20260806.json`,
`experiments/exectv2_hybrid_stage_ablation_20260806.json`, and
`experiments/cross_task_hybrid_mechanism_synthesis_20260806.json`
(taxonomy / unknown-sentinel / prescription-lens dump JSONs pruned 2026-08-16; prose owners above remain)

## DeepSeek V4-Flash-0731 provider update (matched comparison)

[protocol](research/shared/deepseek_v4_flash_0731_matched_comparison_protocol_2026-08-03.md) →
[report](research/shared/deepseek_v4_flash_0731_matched_comparison_report_2026-08-03.md) →
[artifact](../experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json)

## DeepSeek unknown collaboration (active; hosted)

[protocol](experiments/gan2026/gan2026_deepseek_unknown_competence_protocol_2026-07-31.md) →
[thread](research/gan2026/deepseek_unknown_competence_thread_2026-07-31.md) →
[A/U run protocol](experiments/gan2026/gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md) →
rejected slice artifact `experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json` →
[roadmap](plans/ACTIVE_ROADMAP.md#deepseek-unknown-competence-open)

## Write from the paper source library

[NAVIGATION paper-source library](NAVIGATION.md#paper-source-library) →
[why hybrid](research/paper/why_hybrid_architecture_2026-08-09.md) and the
[Gan phrase-variant inventory](research/paper/gan_gold_phrase_variants_2026-08-13.md) and
[ExECT phrase-variant inventory](research/paper/exect_gold_phrase_variants_2026-08-13.md) →
[Gan story](research/paper/gan_story_2026-08-10.md) and
[ExECT story](research/paper/exect_story_2026-08-12.md) →
[rescue source exhibit](research/artifacts/rescue_source_provenance_2026-08-13.html) →
[failures and limits](research/paper/failures_and_limits_2026-08-10.md) →
[paper claim status](canon/10_paper_provenance.md)

Do not start from the historical
[generated manuscript](research/paper/manuscript_2026-06-26.md).

## Check a paper claim

[paper claim status](canon/10_paper_provenance.md) →
[retained evidence index](experiments/retained_evidence_manifest.md) →
the selected report or data file

## Understand a score

[scoring rules](canon/04_scoring.md) →
[Gan evidence](canon/06_gan_clinical_policy.md) or
[ExECT evidence](canon/07_exect_plan11.md)

## Change the implementation

[software design](design/architecture.md) →
[data rules](design/data_contract.md) and [Gan split rules](design/gan2026_split_protocol.md) →
[model policy](design/model_strategy.md) →
[component attribution](design/component_evidence_attribution_architecture.md) →
[reliability evaluation framework](design/reliability_evaluation_framework.md) →
the relevant decision record and tests

Durable decision doors for selected methods:

- [decision 0039](decisions/0039-final-exect-six-model-roster.md) — completed six-model roster
- [decision 0051](decisions/0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md) — successor six-model roster (Gemini 3.7 Flash)
- [decision 0052](decisions/0052-gemini-37-flash-holdout-six-model-slot.md) — Gemini holdout six-model slot
- [Gan Gemini LLM-only v0.8](research/gan2026/gemini37flash_llm_only_dev750_test450_2026-08-13.md) — successor `dev750` / `test450` llm cells
- [ExECT Gemini LLM-only raw lane](research/exectv2/gemini37flash_llm_only_raw_lane_2026-08-14.md) — one-call `raw_lane_score` 0.8444 / 0.82; no second live call
- [Qwen 3.8 27B candidate](research/shared/qwen38_27b_candidate_protocol_2026-08-14.md) — reserved local successor; not a Decision 0051 roster swap. Gan `dev750` vs 3.6: [stage comparison](research/gan2026/qwen38_27b_vs_qwen36_35b_dev750_2026-08-16.md)
- [decision 0040](decisions/0040-final-exect-llm-with-rules-family-ownership.md) — ExECT family ownership
- [decision 0041](decisions/0041-single-call-exect-model-comparison.md) — one-call ExECT comparison
- [decision 0043](decisions/0043-gan-hosted-comparison-uses-v05-prompt.md) — hosted Gan prompt (`v0.5` selected identity)
- [decision 0053](decisions/0053-gan-structured-events-final-prompt.md) — Gan `final` envelope hygiene; Luna `dev750` complete, not selected
- [decision 0054](decisions/0054-model-request-order-and-metadata-are-explicit.md) — rendered request order and research-metadata separation; ExECT v17 unmeasured
- [decision 0044](decisions/0044-shared-reliability-criteria-use-task-specific-measures.md) — shared reliability criteria
- [decision 0046](decisions/0046-exect-primary-method-comparison-boundary.md) — ExECT primary method-comparison boundary
- [decision 0048](decisions/0048-comprehension-and-handoff-refactor.md) — comprehension and handoff refactor
- [decision 0049](decisions/0049-pytest-research-validity-firewall.md) — pytest research-validity firewall

Also: [pipeline trace explorer spec](design/pipeline_trace_explorer_spec.md),
[evidence groundedness metric](reference/evidence_groundedness_metric.md),
and [runbooks](runbooks/).

## Run an OpenAI-compatible or vLLM endpoint

[model strategy](design/model_strategy.md) →
[software design](design/architecture.md) →
[ExECT family ownership](decisions/0040-final-exect-llm-with-rules-family-ownership.md) →
[one-call ExECT architecture](decisions/0041-single-call-exect-model-comparison.md) →
[local structured-output repair](decisions/0042-shared-local-model-structured-output-repair.md) →
[local vLLM dev10 runbook](runbooks/local_vllm_dev10_windows_2026-08-10.md)

## Change evidence or split policy

[evidence rules](canon/03_evidence_claims_frozen.md) →
[locked-data procedure](runbooks/gated_blockers_2026-06-18.md) →
[retained evidence checks](experiments/retained_evidence_manifest.md)
