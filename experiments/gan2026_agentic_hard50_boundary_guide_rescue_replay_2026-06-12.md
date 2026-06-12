# Gan 2026 Agentic Hard50 Boundary-Guide Rescue Replay

Date: 2026-06-12

## Experiment Unit

- Work class: D0 validation hard-slice no-call rescue-gate replay.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- E1 source JSONL: `experiments\gan2026_agentic_hard50_tool_context_ablation_2026-06-12.jsonl`
- E2 source JSONL: `experiments\gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl`
- Hard50 manifest: `experiments\gan2026_agentic_validation_hard50_manifest_2026-06-12.json`
- Scorer: existing Gan-compatible Purist first, Pragmatic side-car.
- Parser candidates: not used as prediction-bearing prompt context.

## Claim Boundary

validation-development D0 no-call replay over saved E1/E2 hard50 boundary-guide traces; no new model calls, no holdout use, no scorer change, and no benchmark claim

## Policy Summary

| Policy | Eligible | Gate | Purist | Pragmatic | Changed | Wrong->Correct | Correct->Wrong | Net | Precision | Fallbacks |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `unanimous_frequency_or_cluster_override` | True | reject | 34/50 | 36/50 | 5 | 2 | 0 | 2 | 0.400 | 23 |
| `guide_and_vote_agree_override` | True | reject | 35/50 | 36/50 | 8 | 4 | 1 | 3 | 0.500 | 20 |
| `cluster_restore_only` | True | reject | 34/50 | 35/50 | 2 | 2 | 0 | 2 | 1.000 | 48 |
| `higher_burden_only` | True | promote | 35/50 | 36/50 | 4 | 3 | 0 | 3 | 0.750 | 46 |
| `boundary_demotion_block` | True | reject | 34/50 | 35/50 | 12 | 4 | 2 | 2 | 0.333 | 3 |

## Interpretation

`higher_burden_only` passes the predeclared D0 no-call gate. Treat it as a validation-development promote signal only; it does not authorize validation250 or holdout escalation.

## Changed Labels

| Row | Policy | Action | Transition | Fallback | Selected | Kind transition |
| ---: | --- | --- | --- | --- | --- | --- |
| 5534 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | correct_to_wrong | `1 per multiple month` | `1 per 2 month` | unresolved_multiple->frequency |
| 5534 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | correct_to_wrong | `1 per multiple month` | `1 per 2 month` | unresolved_multiple->frequency |
| 5974 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | changed_both_wrong | `seizure free for multiple year` | `seizure free for 1 year` | seizure_free->seizure_free |
| 6077 | `unanimous_frequency_or_cluster_override` | accept_unanimous_frequency_or_cluster_e2 | changed_both_wrong | `1 per year` | `1 per 8 month` | frequency->frequency |
| 6077 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | changed_both_wrong | `1 per year` | `1 per 8 month` | frequency->frequency |
| 6077 | `higher_burden_only` | accept_higher_numeric_burden_only | changed_both_wrong | `1 per year` | `1 per 8 month` | frequency->frequency |
| 6077 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | changed_both_wrong | `1 per year` | `1 per 8 month` | frequency->frequency |
| 6131 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | correct_to_wrong | `no seizure frequency reference` | `seizure free for 12 month` | no_reference->seizure_free |
| 6153 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | changed_both_correct | `9 per 4 week` | `9 per 2 month` | frequency->frequency |
| 6368 | `unanimous_frequency_or_cluster_override` | accept_unanimous_frequency_or_cluster_e2 | wrong_to_correct | `3 per 6 week` | `multiple per day` | frequency->unresolved_multiple |
| 6368 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | wrong_to_correct | `3 per 6 week` | `multiple per day` | frequency->unresolved_multiple |
| 6368 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | wrong_to_correct | `3 per 6 week` | `multiple per day` | frequency->unresolved_multiple |
| 7615 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | wrong_to_correct | `2 per year` | `3 to 6 per 5 day` | frequency->frequency |
| 7615 | `higher_burden_only` | accept_higher_numeric_burden_only | wrong_to_correct | `2 per year` | `3 to 6 per 5 day` | frequency->frequency |
| 7615 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | wrong_to_correct | `2 per year` | `3 to 6 per 5 day` | frequency->frequency |
| 9943 | `unanimous_frequency_or_cluster_override` | accept_unanimous_frequency_or_cluster_e2 | changed_both_wrong | `unknown` | `1 per 4 to 5 week` | unknown->frequency |
| 9943 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | changed_both_wrong | `unknown` | `1 per 4 to 5 week` | unknown->frequency |
| 9943 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | changed_both_wrong | `unknown` | `1 per 4 to 5 week` | unknown->frequency |
| 10677 | `unanimous_frequency_or_cluster_override` | accept_unanimous_frequency_or_cluster_e2 | wrong_to_correct | `1 per month` | `1 cluster per month, multiple per cluster` | frequency->frequency |
| 10677 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | wrong_to_correct | `1 per month` | `1 cluster per month, multiple per cluster` | frequency->frequency |
| 10677 | `cluster_restore_only` | accept_cluster_restore_only | wrong_to_correct | `1 per month` | `1 cluster per month, multiple per cluster` | frequency->frequency |
| 10677 | `higher_burden_only` | accept_higher_numeric_burden_only | wrong_to_correct | `1 per month` | `1 cluster per month, multiple per cluster` | frequency->frequency |
| 10677 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | wrong_to_correct | `1 per month` | `1 cluster per month, multiple per cluster` | frequency->frequency |
| 10996 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | wrong_to_correct | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | frequency->frequency |
| 10996 | `cluster_restore_only` | accept_cluster_restore_only | wrong_to_correct | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | frequency->frequency |
| 10996 | `higher_burden_only` | accept_higher_numeric_burden_only | wrong_to_correct | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | frequency->frequency |
| 10996 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | wrong_to_correct | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | frequency->frequency |
| 15168 | `unanimous_frequency_or_cluster_override` | accept_unanimous_frequency_or_cluster_e2 | changed_both_correct | `no seizure frequency reference` | `multiple per day` | no_reference->unresolved_multiple |
| 15168 | `guide_and_vote_agree_override` | accept_e1_boundary_and_e2_vote_agree | changed_both_correct | `no seizure frequency reference` | `multiple per day` | no_reference->unresolved_multiple |
| 15168 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | changed_both_correct | `no seizure frequency reference` | `multiple per day` | no_reference->unresolved_multiple |
| 15193 | `boundary_demotion_block` | accept_e2_unless_boundary_demotion | changed_both_correct | `no seizure frequency reference` | `multiple per year` | no_reference->unresolved_multiple |

## Diagnostic Hidden-Family Summary

This section uses predeclared hard50 family tags from the validation manifest. It is non-runtime diagnostic context only and is not an eligible gate feature.

| Policy | Hidden family | Changed | Wrong->Correct | Correct->Wrong | Net |
| --- | --- | ---: | ---: | ---: | ---: |
| `unanimous_frequency_or_cluster_override` | `benchmark_format_convention` | 3 | 1 | 0 | 1 |
| `unanimous_frequency_or_cluster_override` | `cluster_burden` | 2 | 1 | 0 | 1 |
| `unanimous_frequency_or_cluster_override` | `competing_semiologies` | 1 | 0 | 0 | 0 |
| `unanimous_frequency_or_cluster_override` | `current_vs_historical` | 2 | 1 | 0 | 1 |
| `unanimous_frequency_or_cluster_override` | `diary_or_log_aggregation` | 0 | 0 | 0 | 0 |
| `unanimous_frequency_or_cluster_override` | `rate_bucket_or_denominator` | 2 | 1 | 0 | 1 |
| `unanimous_frequency_or_cluster_override` | `seizure_free_duration` | 2 | 0 | 0 | 0 |
| `unanimous_frequency_or_cluster_override` | `uncertainty_or_ambiguity` | 3 | 1 | 0 | 1 |
| `unanimous_frequency_or_cluster_override` | `unclassified` | 0 | 0 | 0 | 0 |
| `unanimous_frequency_or_cluster_override` | `unknown_boundary` | 2 | 1 | 0 | 1 |
| `guide_and_vote_agree_override` | `benchmark_format_convention` | 4 | 2 | 0 | 2 |
| `guide_and_vote_agree_override` | `cluster_burden` | 3 | 2 | 0 | 2 |
| `guide_and_vote_agree_override` | `competing_semiologies` | 3 | 1 | 1 | 0 |
| `guide_and_vote_agree_override` | `current_vs_historical` | 3 | 1 | 1 | 0 |
| `guide_and_vote_agree_override` | `diary_or_log_aggregation` | 0 | 0 | 0 | 0 |
| `guide_and_vote_agree_override` | `rate_bucket_or_denominator` | 2 | 1 | 0 | 1 |
| `guide_and_vote_agree_override` | `seizure_free_duration` | 3 | 0 | 1 | -1 |
| `guide_and_vote_agree_override` | `uncertainty_or_ambiguity` | 3 | 1 | 0 | 1 |
| `guide_and_vote_agree_override` | `unclassified` | 0 | 0 | 0 | 0 |
| `guide_and_vote_agree_override` | `unknown_boundary` | 2 | 1 | 0 | 1 |
| `cluster_restore_only` | `benchmark_format_convention` | 2 | 2 | 0 | 2 |
| `cluster_restore_only` | `cluster_burden` | 2 | 2 | 0 | 2 |
| `cluster_restore_only` | `competing_semiologies` | 0 | 0 | 0 | 0 |
| `cluster_restore_only` | `current_vs_historical` | 1 | 1 | 0 | 1 |
| `cluster_restore_only` | `diary_or_log_aggregation` | 0 | 0 | 0 | 0 |
| `cluster_restore_only` | `rate_bucket_or_denominator` | 1 | 1 | 0 | 1 |
| `cluster_restore_only` | `seizure_free_duration` | 0 | 0 | 0 | 0 |
| `cluster_restore_only` | `uncertainty_or_ambiguity` | 0 | 0 | 0 | 0 |
| `cluster_restore_only` | `unclassified` | 0 | 0 | 0 | 0 |
| `cluster_restore_only` | `unknown_boundary` | 0 | 0 | 0 | 0 |
| `higher_burden_only` | `benchmark_format_convention` | 2 | 2 | 0 | 2 |
| `higher_burden_only` | `cluster_burden` | 2 | 2 | 0 | 2 |
| `higher_burden_only` | `competing_semiologies` | 1 | 1 | 0 | 1 |
| `higher_burden_only` | `current_vs_historical` | 1 | 1 | 0 | 1 |
| `higher_burden_only` | `diary_or_log_aggregation` | 0 | 0 | 0 | 0 |
| `higher_burden_only` | `rate_bucket_or_denominator` | 1 | 1 | 0 | 1 |
| `higher_burden_only` | `seizure_free_duration` | 1 | 0 | 0 | 0 |
| `higher_burden_only` | `uncertainty_or_ambiguity` | 1 | 0 | 0 | 0 |
| `higher_burden_only` | `unclassified` | 0 | 0 | 0 | 0 |
| `higher_burden_only` | `unknown_boundary` | 1 | 0 | 0 | 0 |
| `boundary_demotion_block` | `benchmark_format_convention` | 5 | 2 | 0 | 2 |
| `boundary_demotion_block` | `cluster_burden` | 3 | 2 | 0 | 2 |
| `boundary_demotion_block` | `competing_semiologies` | 5 | 1 | 2 | -1 |
| `boundary_demotion_block` | `current_vs_historical` | 5 | 1 | 2 | -1 |
| `boundary_demotion_block` | `diary_or_log_aggregation` | 0 | 0 | 0 | 0 |
| `boundary_demotion_block` | `rate_bucket_or_denominator` | 2 | 1 | 0 | 1 |
| `boundary_demotion_block` | `seizure_free_duration` | 6 | 0 | 2 | -2 |
| `boundary_demotion_block` | `uncertainty_or_ambiguity` | 5 | 1 | 1 | 0 |
| `boundary_demotion_block` | `unclassified` | 1 | 0 | 0 | 0 |
| `boundary_demotion_block` | `unknown_boundary` | 4 | 1 | 1 | 0 |
