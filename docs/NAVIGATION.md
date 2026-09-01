# Documentation navigation

Paper source library and current owners. Campaign reports and the
numbered decision series are not listed here. Recover them from git.
The dense pointer log is [decision history](history/decisions.md).

## Current owners

| Need | Read |
| --- | --- |
| Public front door | [README](../README.md) |
| What is present, missing, and allowed to run | [project status](../PROJECT_STATUS.md) |
| Paper methods, claims, cells | [paper keep-set](paper/README.md) |
| Dissertation scope | [Gan is the dissertation paper](paper/decisions/gan-is-the-dissertation-paper.md) |
| Gan inventory feasibility | [100-letter descriptive study](research/gan2026/gan_inventory_feasibility_dev750_n100_2026-08-28.md) |
| Cited Gemini five-cell grids | [Gan grid](research/gan2026/gan_five_cell_grid_2026-08-22.md), [paired `test450` tests](research/gan2026/gan_paired_significance_test450_2026-08-29.md), [Gan rules three-stage Phase D](research/gan2026/gan_rules_only_three_stage_phase_d_2026-08-29.md), [source-near rules find](research/gan2026/gan_rules_source_near_find_test450_2026-08-31.md), [ExECT inventory grid](research/exectv2/exect_both_extract_on_inventory_protocol_2026-08-23.md) (4-family micro F1; [`paper_experiments/exect/five_cell_grid/`](../paper_experiments/exect/five_cell_grid/)), [ExECT cell 4](research/exectv2/exect_rule_select_after_llm_encode_2026-08-22.md) |
| Gan test450 class report | [Purist/Pragmatic class report](research/gan2026/gan_test450_classification_report_2026-08-28.md), [pragmatic rate → unknown](research/gan2026/gan_pragmatic_infrequent_error_mode_2026-08-29.md), [pragmatic gold → unknown](research/gan2026/gan_pragmatic_unknown_error_mode_2026-08-29.md), [last-event well-since](research/gan2026/gan_last_event_well_since_protocol_2026-08-29.md) |
| Gan find prompt-component ablations | [protocol](research/gan2026/gan_extract_prompt_component_ablation_protocol_2026-08-30.md), [test450 report](research/gan2026/gan_extract_prompt_component_ablation_2026-08-30.md), [round-2 protocol](research/gan2026/gan_extract_prompt_component_ablation_round2_protocol_2026-08-30.md), [round-2 report](research/gan2026/gan_extract_prompt_component_ablation_round2_2026-08-30.md), [Holgate-like `dev250`](research/gan2026/gan_holgate_like_dev250_2026-08-30.md) |
| Gemini vs Qwen COT synthetic | [synthetic-to-synthetic compare](research/gan2026/gan_gemini_vs_qwen25_14b_cot_synthetic_2026-08-28.md) |
| Six-model cell-3 roster | [roster decision](paper/decisions/six-model-roster.md), [codebook rung replay](research/gan2026/gan_cell3_codebook_roster_replay_2026-08-28.md), [find vs selected-evidence volume](research/gan2026/gan_cell3_candidate_volume_dev750_2026-08-29.md), [`paper_experiments/roster.json`](../paper_experiments/roster.json) |
| Live runner mapped onto a cell | [cells and runners](paper/cells_and_runners.md) |
| Gan rules find dialect | [source-near is living find](research/gan2026/gan_rules_find_llm_dialects_2026-08-31.md); `gan_llm_extract` is bundled find-and-encode |
| Stage story | [architecture](paper/architecture.md) |
| Replayable cells | [paper experiments](../paper_experiments/README.md) |
| Live runner | `python -m clinical_extraction.paper` |

Implemented-runner atlas (not the headline table): [architecture/README](architecture/README.md).

## Paper source library

Write from these files. Do not write from the June manuscript, the
neuro-symbolic `paper/draft/` tex, or the 9–10 Aug HTML pack.

1. [Why narrative epilepsy letters are a research problem](research/paper/why_narrative_letters_are_a_research_problem_2026-08-17.md)
2. [What the two golds already decided](research/paper/what_the_two_golds_already_decided_2026-08-17.md)
3. [What the two extraction tasks ask](research/shared/task_shape_framework_2026-08-06.md)
4. [Literature review draft](paper/literature_review_draft.md)
5. [Method × stage](paper/method_x_stage.md) — five cells; Gan row 10 and ExECT `EA0007`
6. [Rule catalogue](paper/rule_catalogue.md) — named rules by authority, then stage
7. [Rules and models across stages (Gan, Gemini)](research/paper/gan_rules_and_llms_across_stages_2026-08-21.md)
8. [Three variables: stages, model, thinking](research/paper/three_variables_rules_model_thinking_2026-08-23.md) — draft results; [paired `test450` tests](research/gan2026/gan_paired_significance_test450_2026-08-29.md)
9. [Source-near find vs bundled encode](research/paper/gan_source_near_vs_bundled_encode_2026-08-23.md) — Gan ablation
10. [Find then Select vs find-and-select](research/paper/exect_extract_vs_extract_and_select_2026-08-25.md) — ExECT ablation
11. [How the two tasks are scored](research/paper/score_definitions_2026-08-17.md)
12. [ExECT paper scoring is not our comparison](research/paper/exect_published_metric_is_not_the_comparison_2026-08-24.md)
13. [Dataset description](research/paper/dataset_description_2026-08-26.md) — letter n, words, gold density
14. [Dataset gold support](research/paper/dataset_gold_support_2026-08-22.md) — denominators, occupancy, bands
15. [Failures and limits](research/paper/failures_and_limits_2026-08-10.md)
16. [Two reviewable cases](research/paper/reviewable_case_pair_2026-08-09.md) — development letters only
17. [Flagship 3-letter suite](research/paper/flagship_3_letter_suite_2026-08-11.md) — development letters, not holdout
18. [Gemini cell 3 encode→select on Gan `dev750`](research/paper/gan_gemini_cell3_encode_to_select_dev750_2026-08-29.md) — changed-row select increment

The source library explains the evidence. It does not replace
[claims](paper/claims.md) or `paper_experiments/`.
