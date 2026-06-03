# Gan 2026 RQ1/RQ2 Single-Task Control Panels

Frozen validation-development row panels for the isolated candidate, evidence, projection, and paired-task overload controls. These panels materialize row membership only; they do not run or score fresh model calls.

- Date: `2026-06-04`
- Split manifest: `gan2026_split_v1`
- Panel rows: 125
- Source rows represented: 115
- JSONL artifact: `experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.json`

## Panels

| Panel | Rows | Source rows | Gold kinds |
| --- | ---: | ---: | --- |
| `balanced_validation50` | 50 | 50 | `frequency`=20, `no_reference`=6, `seizure_free`=8, `unknown`=8, `unresolved_multiple`=8 |
| `hidden_family_hard_panel` | 75 | 75 | `frequency`=35, `seizure_free`=3, `unknown`=22, `unresolved_multiple`=15 |

## Hidden Family Coverage

| Panel | Family | Rows |
| --- | --- | ---: |
| `balanced_validation50` | `benchmark_format_convention` | 9 |
| `balanced_validation50` | `cluster_burden` | 24 |
| `balanced_validation50` | `competing_semiologies` | 43 |
| `balanced_validation50` | `current_vs_historical` | 49 |
| `balanced_validation50` | `diary_or_log_aggregation` | 47 |
| `balanced_validation50` | `rate_bucket_or_denominator` | 38 |
| `balanced_validation50` | `seizure_free_duration` | 10 |
| `balanced_validation50` | `uncertainty_or_ambiguity` | 19 |
| `balanced_validation50` | `unknown_boundary` | 7 |
| `hidden_family_hard_panel` | `benchmark_format_convention` | 24 |
| `hidden_family_hard_panel` | `candidate_absent_or_weak` | 4 |
| `hidden_family_hard_panel` | `cluster_burden` | 18 |
| `hidden_family_hard_panel` | `cluster_or_diary` | 12 |
| `hidden_family_hard_panel` | `competing_semiologies` | 37 |
| `hidden_family_hard_panel` | `current_vs_historical` | 39 |
| `hidden_family_hard_panel` | `deterministic_miss` | 4 |
| `hidden_family_hard_panel` | `diary_or_log_aggregation` | 8 |
| `hidden_family_hard_panel` | `rate_bucket_or_denominator` | 32 |
| `hidden_family_hard_panel` | `seizure_free_duration` | 27 |
| `hidden_family_hard_panel` | `seizure_free_overreach` | 11 |
| `hidden_family_hard_panel` | `shorthand_interval_range` | 1 |
| `hidden_family_hard_panel` | `temporal_conflict` | 10 |
| `hidden_family_hard_panel` | `uncertainty_or_ambiguity` | 26 |
| `hidden_family_hard_panel` | `unclassified` | 4 |
| `hidden_family_hard_panel` | `unknown_boundary` | 20 |
| `hidden_family_hard_panel` | `unknown_no_reference_boundary` | 14 |

## Row Manifest

| Panel | Row | Gold | Kind | Families | Selection |
| --- | ---: | --- | --- | --- | --- |
| `balanced_validation50` | 10 | `4 per day` | `frequency` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 40 | `4 per week` | `frequency` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 79 | `6 to 7 per year` | `frequency` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 103 | `2 to 4 per year` | `frequency` | `diary_or_log_aggregation;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 128 | `17 per month` | `frequency` | `seizure_free_duration;cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 156 | `1 per 6 day` | `frequency` | `rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 180 | `1 per 7 day` | `frequency` | `diary_or_log_aggregation;current_vs_historical` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 182 | `1 per 2 day` | `frequency` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 187 | `1 per 7 to 9 day` | `frequency` | `cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 190 | `1 per 4 week` | `frequency` | `cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 198 | `1 per 4 week` | `frequency` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;uncertainty_or_ambiguity` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 212 | `1 per 3 to 4 week` | `frequency` | `cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 218 | `1 per 3 week` | `frequency` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 243 | `1 per 4 month` | `frequency` | `diary_or_log_aggregation;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 278 | `multiple per week` | `unresolved_multiple` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 280 | `multiple per day` | `unresolved_multiple` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 338 | `multiple per month` | `unresolved_multiple` | `cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 409 | `1 per month` | `frequency` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 419 | `2 per year` | `frequency` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 446 | `2 per week` | `frequency` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 466 | `21 to 28 per month` | `frequency` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 467 | `9 per month` | `frequency` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 531 | `12 to 30 per 3 month` | `frequency` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:frequency` |
| `balanced_validation50` | 743 | `multiple per week` | `unresolved_multiple` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 744 | `multiple per week` | `unresolved_multiple` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 869 | `multiple per month` | `unresolved_multiple` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 1317 | `unknown, multiple per cluster` | `unknown` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 1687 | `multiple per week` | `unresolved_multiple` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 1695 | `multiple per month` | `unresolved_multiple` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` | `gold_kind_quota:unresolved_multiple` |
| `balanced_validation50` | 2149 | `unknown` | `unknown` | `unknown_boundary;cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 2166 | `unknown` | `unknown` | `unknown_boundary;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 2907 | `seizure free for 6 month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 2932 | `seizure free for 9 month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;current_vs_historical;competing_semiologies` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 2938 | `seizure free for 8 month` | `seizure_free` | `seizure_free_duration;cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 2965 | `seizure free for 16 month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 2992 | `seizure free for 7 month` | `seizure_free` | `seizure_free_duration;cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 3015 | `seizure free for 12 month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 3048 | `seizure free for 16 month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 3058 | `seizure free for 12 month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical` | `gold_kind_quota:seizure_free` |
| `balanced_validation50` | 3356 | `unknown` | `unknown` | `unknown_boundary;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 3371 | `unknown` | `unknown` | `unknown_boundary;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 3436 | `unknown` | `unknown` | `unknown_boundary;cluster_burden;rate_bucket_or_denominator;current_vs_historical;uncertainty_or_ambiguity` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 3468 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 3469 | `unknown` | `unknown` | `unknown_boundary;cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `gold_kind_quota:unknown` |
| `balanced_validation50` | 11400 | `no seizure frequency reference` | `no_reference` | `diary_or_log_aggregation;rate_bucket_or_denominator;competing_semiologies` | `gold_kind_quota:no_reference` |
| `balanced_validation50` | 11405 | `no seizure frequency reference` | `no_reference` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `gold_kind_quota:no_reference` |
| `balanced_validation50` | 11408 | `no seizure frequency reference` | `no_reference` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;uncertainty_or_ambiguity` | `gold_kind_quota:no_reference` |
| `balanced_validation50` | 11409 | `no seizure frequency reference` | `no_reference` | `cluster_burden;diary_or_log_aggregation;current_vs_historical` | `gold_kind_quota:no_reference` |
| `balanced_validation50` | 11411 | `no seizure frequency reference` | `no_reference` | `diary_or_log_aggregation;current_vs_historical;competing_semiologies` | `gold_kind_quota:no_reference` |
| `balanced_validation50` | 11434 | `no seizure frequency reference` | `no_reference` | `diary_or_log_aggregation;current_vs_historical;competing_semiologies` | `gold_kind_quota:no_reference` |
| `hidden_family_hard_panel` | 190 | `1 per 4 week` | `frequency` | `cluster_burden;competing_semiologies` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 278 | `multiple per week` | `unresolved_multiple` | `rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention;cluster_or_diary;temporal_conflict;unknown_no_reference_boundary` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 338 | `multiple per month` | `unresolved_multiple` | `current_vs_historical;competing_semiologies;benchmark_format_convention;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 743 | `multiple per week` | `unresolved_multiple` | `rate_bucket_or_denominator;benchmark_format_convention;cluster_or_diary;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 744 | `multiple per week` | `unresolved_multiple` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention;cluster_or_diary;unknown_no_reference_boundary` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 816 | `1 per month` | `frequency` | `rate_bucket_or_denominator;current_vs_historical;competing_semiologies` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 869 | `multiple per month` | `unresolved_multiple` | `cluster_or_diary;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary;diary_or_log_aggregation;rate_bucket_or_denominator;benchmark_format_convention` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 959 | `1 per 2 month` | `frequency` | `rate_bucket_or_denominator;benchmark_format_convention` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 960 | `1 per 2 month` | `frequency` | `rate_bucket_or_denominator;benchmark_format_convention` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 987 | `1 per 2 month` | `frequency` | `rate_bucket_or_denominator;benchmark_format_convention` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1046 | `3 to 5 per month` | `frequency` | `cluster_burden;current_vs_historical;uncertainty_or_ambiguity` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1317 | `unknown, multiple per cluster` | `unknown` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical;uncertainty_or_ambiguity;benchmark_format_convention;diary_or_log_aggregation;cluster_or_diary;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1363 | `3 per day` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1687 | `multiple per week` | `unresolved_multiple` | `rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention;shorthand_interval_range;temporal_conflict;unknown_no_reference_boundary` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1694 | `1 cluster per 2 week, 3 per cluster` | `frequency` | `cluster_burden;current_vs_historical;competing_semiologies` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1695 | `multiple per month` | `unresolved_multiple` | `diary_or_log_aggregation;current_vs_historical;competing_semiologies;benchmark_format_convention;cluster_or_diary;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1706 | `multiple cluster per month, multiple per cluster` | `frequency` | `cluster_burden;current_vs_historical;competing_semiologies;benchmark_format_convention` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1707 | `multiple per week` | `unresolved_multiple` | `cluster_or_diary;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary;cluster_burden;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention;diary_or_log_aggregation` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 1923 | `7 per 6 month` | `frequency` | `current_vs_historical` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 2080 | `multiple per month` | `unresolved_multiple` | `cluster_or_diary;seizure_free_overreach;unknown_no_reference_boundary;current_vs_historical;benchmark_format_convention` | `component_projection_followup_panel` |
| `hidden_family_hard_panel` | 2748 | `1 per month` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `atlas_hard_slice_manifest` |
| `hidden_family_hard_panel` | 3356 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity;current_vs_historical;competing_semiologies;candidate_absent_or_weak;cluster_or_diary;deterministic_miss;seizure_free_overreach;unknown_no_reference_boundary` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 3528 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;candidate_absent_or_weak;cluster_or_diary;deterministic_miss;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 4368 | `5 per 2 month` | `frequency` | `diary_or_log_aggregation;unclassified` | `atlas_hard_slice_manifest` |
| `hidden_family_hard_panel` | 4690 | `multiple per day` | `unresolved_multiple` | `seizure_free_duration;rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention;candidate_absent_or_weak;cluster_or_diary;deterministic_miss;seizure_free_overreach;unknown_no_reference_boundary` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 5534 | `1 per multiple month` | `unresolved_multiple` | `seizure_free_duration;current_vs_historical;competing_semiologies;unclassified;candidate_absent_or_weak;cluster_or_diary;deterministic_miss;seizure_free_overreach;temporal_conflict;unknown_no_reference_boundary` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 5921 | `1 per 6 to 8 week` | `frequency` | `rate_bucket_or_denominator` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 5974 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6077 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6094 | `3 per month` | `frequency` | `rate_bucket_or_denominator` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6131 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6153 | `9 per month` | `frequency` | `unclassified` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6209 | `multiple per day` | `unresolved_multiple` | `rate_bucket_or_denominator;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6244 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6321 | `unknown` | `unknown` | `unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6368 | `unknown` | `unknown` | `unknown_boundary;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6501 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;cluster_burden;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6571 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6889 | `multiple per week` | `unresolved_multiple` | `rate_bucket_or_denominator;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 6987 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 7168 | `unknown` | `unknown` | `unknown_boundary;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 7615 | `3 to 7 per month` | `frequency` | `competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 9496 | `6 per 12 month` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 9888 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 9937 | `1 cluster per month, multiple per cluster` | `frequency` | `cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `frequency` | `cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 9955 | `1 cluster per month, multiple per cluster` | `frequency` | `cluster_burden;rate_bucket_or_denominator;uncertainty_or_ambiguity;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 10266 | `unknown` | `unknown` | `unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 10386 | `1 cluster per week, 2 to 3 per cluster` | `frequency` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 10618 | `unknown, 4 to 6 per cluster` | `unknown` | `seizure_free_duration;cluster_burden;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 10677 | `1 cluster per month, multiple per cluster` | `frequency` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 10996 | `1 to 2 cluster per month, 4 per cluster` | `frequency` | `cluster_burden;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 11216 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 11254 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 11259 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 11272 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 12422 | `1 per day` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 12438 | `1 per day` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 12456 | `1 per day` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 12460 | `1 per day` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 12468 | `1 per day` | `frequency` | `rate_bucket_or_denominator;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 13209 | `1 per 8 month` | `frequency` | `seizure_free_duration;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 13843 | `seizure free for multiple month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;current_vs_historical` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 13858 | `seizure free for multiple month` | `seizure_free` | `seizure_free_duration;diary_or_log_aggregation;current_vs_historical` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 13889 | `seizure free for multiple month` | `seizure_free` | `seizure_free_duration;current_vs_historical` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 14025 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 14076 | `unknown` | `unknown` | `unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 14810 | `1 per month` | `frequency` | `seizure_free_duration;current_vs_historical;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 14821 | `1 per month` | `frequency` | `seizure_free_duration;current_vs_historical;competing_semiologies` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 15168 | `multiple per 15 month` | `unresolved_multiple` | `seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 15193 | `multiple per 13 month` | `unresolved_multiple` | `seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `frequency` | `cluster_burden;current_vs_historical` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 15672 | `1 per day` | `frequency` | `cluster_burden;rate_bucket_or_denominator;current_vs_historical` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 15834 | `5 per week` | `frequency` | `rate_bucket_or_denominator;current_vs_historical` | `atlas_hard_slice_manifest;component_projection_followup_panel` |
| `hidden_family_hard_panel` | 15986 | `11 per 3 month` | `frequency` | `unclassified` | `atlas_hard_slice_manifest;component_projection_followup_panel` |

## Claim Boundary

Frozen validation-development panels for RQ1/RQ2 single-task controls; no locked-test row-level use and no model-performance claim.
