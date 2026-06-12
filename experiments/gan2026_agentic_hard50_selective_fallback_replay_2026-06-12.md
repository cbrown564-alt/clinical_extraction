# Gan 2026 Agentic Hard50 Selective Fallback Replay

Date: 2026-06-12

## Experiment Unit

- Work class: validation hard-slice no-call selective-action replay.
- Rows: 50
- Fallback comparator: `single_self_consistency_temperature`
- Source JSONL: `experiments\gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.jsonl`
- Hard50 manifest: `experiments\gan2026_agentic_validation_hard50_manifest_2026-06-12.json`
- Scorer: existing Gan-compatible Purist first, Pragmatic side-car.

## Claim Boundary

validation-development no-call replay over saved hard50 traces; no new model calls, no holdout use, no scorer change, and no benchmark claim

## Policy Summary

| Policy | Eligible | Gate | Purist | Pragmatic | Changed | Wrong->Correct | Correct->Wrong | Net | Precision | Fallbacks |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `all_agree_tool_accept` | True | reject | 20/50 | 22/50 | 26 | 0 | 12 | -12 | 0.000 | 0 |
| `all_agree_multi_accept` | True | reject | 26/50 | 27/50 | 14 | 0 | 6 | -6 | 0.000 | 15 |
| `boundary_coordinator_agree` | True | reject | 29/50 | 30/50 | 11 | 0 | 3 | -3 | 0.000 | 17 |
| `no_seizure_free_introduction` | True | reject | 26/50 | 28/50 | 17 | 0 | 6 | -6 | 0.000 | 6 |
| `raw_repair_disagreement_fallback` | True | reject | 26/50 | 27/50 | 15 | 0 | 6 | -6 | 0.000 | 21 |
| `manifest_family_oracle` | False | diagnostic_only | 31/50 | 33/50 | 3 | 0 | 1 | -1 | 0.000 | 41 |

## Interpretation

No promotable selective fallback policy passed the predeclared gate. Use this as a revise/reject signal and move to tool-context ablation before any new live multi-agent calls.

## Row-Level Changed Labels

| Row | Policy | Action | Transition | Fallback | Selected | Families |
| ---: | --- | --- | --- | --- | --- | --- |
| 3356 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_correct | `multiple per month` | `unknown` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 3356 | `all_agree_multi_accept` | accept_multi_agent_matched | correct_to_wrong | `multiple per month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 3356 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | correct_to_wrong | `multiple per month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 3528 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_correct | `multiple per day` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 3528 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_correct | `multiple per day` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 4690 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `multiple per day` | `seizure free for multiple year` | seizure_free_duration, rate_bucket_or_denominator, current_vs_historical, benchmark_format_convention |
| 4690 | `all_agree_multi_accept` | accept_multi_agent_matched | correct_to_wrong | `multiple per day` | `seizure free for multiple year` | seizure_free_duration, rate_bucket_or_denominator, current_vs_historical, benchmark_format_convention |
| 4690 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | correct_to_wrong | `multiple per day` | `seizure free for multiple year` | seizure_free_duration, rate_bucket_or_denominator, current_vs_historical, benchmark_format_convention |
| 5534 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_correct | `1 per multiple month` | `unknown` | seizure_free_duration, current_vs_historical, competing_semiologies |
| 5534 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_correct | `1 per multiple month` | `multiple per year` | seizure_free_duration, current_vs_historical, competing_semiologies |
| 5534 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_correct | `1 per multiple month` | `multiple per year` | seizure_free_duration, current_vs_historical, competing_semiologies |
| 5534 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_correct | `1 per multiple month` | `multiple per year` | seizure_free_duration, current_vs_historical, competing_semiologies |
| 6077 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_wrong | `1 per year` | `seizure free for 8 month` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6077 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_wrong | `1 per year` | `seizure free for 8 month` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6077 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_wrong | `1 per year` | `seizure free for 8 month` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6094 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_wrong | `5 per month` | `unknown` | rate_bucket_or_denominator |
| 6094 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_wrong | `5 per month` | `unknown` | rate_bucket_or_denominator |
| 6094 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_wrong | `5 per month` | `unknown` | rate_bucket_or_denominator |
| 6094 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_wrong | `5 per month` | `unknown` | rate_bucket_or_denominator |
| 6094 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_wrong | `5 per month` | `unknown` | rate_bucket_or_denominator |
| 6094 | `manifest_family_oracle` | accept_multi_manifest_family_oracle | changed_both_wrong | `5 per month` | `unknown` | rate_bucket_or_denominator |
| 6131 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `no seizure frequency reference` | `seizure free for 12 month` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 6153 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `9 per 4 week` | `3 per 4 week` | unclassified |
| 6153 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | correct_to_wrong | `9 per 4 week` | `3 per 4 week` | unclassified |
| 6153 | `manifest_family_oracle` | accept_multi_manifest_family_oracle | correct_to_wrong | `9 per 4 week` | `3 per 4 week` | unclassified |
| 6244 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_correct | `multiple per week` | `unknown` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6244 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_correct | `multiple per week` | `unknown` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6244 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_correct | `multiple per week` | `unknown` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6244 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_correct | `multiple per week` | `unknown` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6244 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_correct | `multiple per week` | `unknown` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6368 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_wrong | `3 per 6 week` | `1 per 1 to 2 week` | unknown_boundary, uncertainty_or_ambiguity |
| 6368 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_wrong | `3 per 6 week` | `1 per 1 to 2 week` | unknown_boundary, uncertainty_or_ambiguity |
| 6368 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_wrong | `3 per 6 week` | `1 per 1 to 2 week` | unknown_boundary, uncertainty_or_ambiguity |
| 6368 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_wrong | `3 per 6 week` | `1 per 1 to 2 week` | unknown_boundary, uncertainty_or_ambiguity |
| 6368 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_wrong | `3 per 6 week` | `1 per 1 to 2 week` | unknown_boundary, uncertainty_or_ambiguity |
| 6368 | `manifest_family_oracle` | accept_multi_manifest_family_oracle | changed_both_wrong | `3 per 6 week` | `1 per 1 to 2 week` | unknown_boundary, uncertainty_or_ambiguity |
| 6571 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6571 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6571 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6571 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6571 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, uncertainty_or_ambiguity |
| 6987 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_correct | `no seizure frequency reference` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 6987 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_correct | `no seizure frequency reference` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 6987 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_correct | `no seizure frequency reference` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 6987 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_correct | `no seizure frequency reference` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 6987 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_correct | `no seizure frequency reference` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 9888 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_correct | `no seizure frequency reference` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 9888 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_correct | `no seizure frequency reference` | `unknown` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 9943 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_wrong | `unknown` | `1 per 4 to 5 week` | cluster_burden, rate_bucket_or_denominator, uncertainty_or_ambiguity, benchmark_format_convention |
| 9943 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_wrong | `unknown` | `1 per 4 to 5 week` | cluster_burden, rate_bucket_or_denominator, uncertainty_or_ambiguity, benchmark_format_convention |
| 9943 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_wrong | `unknown` | `1 per 4 to 5 week` | cluster_burden, rate_bucket_or_denominator, uncertainty_or_ambiguity, benchmark_format_convention |
| 9955 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `1 cluster per month, multiple per cluster` | `1 per month` | cluster_burden, rate_bucket_or_denominator, uncertainty_or_ambiguity, benchmark_format_convention |
| 9955 | `all_agree_multi_accept` | accept_multi_agent_matched | correct_to_wrong | `1 cluster per month, multiple per cluster` | `1 per month` | cluster_burden, rate_bucket_or_denominator, uncertainty_or_ambiguity, benchmark_format_convention |
| 9955 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | correct_to_wrong | `1 cluster per month, multiple per cluster` | `1 per month` | cluster_burden, rate_bucket_or_denominator, uncertainty_or_ambiguity, benchmark_format_convention |
| 9955 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | correct_to_wrong | `1 cluster per month, multiple per cluster` | `1 per month` | cluster_burden, rate_bucket_or_denominator, uncertainty_or_ambiguity, benchmark_format_convention |
| 12422 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `1 per day` | `4 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12422 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | correct_to_wrong | `1 per day` | `4 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12438 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `1 per day` | `2 to 3 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12456 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `1 per day` | `3 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12460 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `1 per day` | `2 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12460 | `all_agree_multi_accept` | accept_multi_agent_matched | correct_to_wrong | `1 per day` | `2 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12460 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | correct_to_wrong | `1 per day` | `2 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12460 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | correct_to_wrong | `1 per day` | `2 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12460 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | correct_to_wrong | `1 per day` | `2 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12468 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `1 per day` | `4 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12468 | `all_agree_multi_accept` | accept_multi_agent_matched | correct_to_wrong | `1 per day` | `4 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12468 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | correct_to_wrong | `1 per day` | `4 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12468 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | correct_to_wrong | `1 per day` | `4 per year` | rate_bucket_or_denominator, competing_semiologies |
| 12468 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | correct_to_wrong | `1 per day` | `4 per year` | rate_bucket_or_denominator, competing_semiologies |
| 14025 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_wrong | `2 per year` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 14025 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_wrong | `2 per year` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 14025 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_wrong | `2 per year` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 15168 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `no seizure frequency reference` | `seizure free for 1 year` | seizure_free_duration, current_vs_historical, competing_semiologies, benchmark_format_convention |
| 15168 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | correct_to_wrong | `no seizure frequency reference` | `seizure free for 1 year` | seizure_free_duration, current_vs_historical, competing_semiologies, benchmark_format_convention |
| 15193 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `no seizure frequency reference` | `seizure free for 1 year` | seizure_free_duration, current_vs_historical, competing_semiologies, benchmark_format_convention |
| 15193 | `all_agree_multi_accept` | accept_multi_agent_matched | correct_to_wrong | `no seizure frequency reference` | `seizure free for 1 year` | seizure_free_duration, current_vs_historical, competing_semiologies, benchmark_format_convention |
| 15193 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | correct_to_wrong | `no seizure frequency reference` | `seizure free for 1 year` | seizure_free_duration, current_vs_historical, competing_semiologies, benchmark_format_convention |
| 15593 | `all_agree_tool_accept` | accept_single_agent_tools | correct_to_wrong | `1 cluster per 5 day, 2 to 4 per cluster` | `2 per 6 month` | cluster_burden, current_vs_historical |
| 15593 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | correct_to_wrong | `1 cluster per 5 day, 2 to 4 per cluster` | `2 per 6 month` | cluster_burden, current_vs_historical |
| 10386 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_correct | `1 cluster per week, 2 to 3 per cluster` | `1 per week` | cluster_burden, rate_bucket_or_denominator, current_vs_historical |
| 10386 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_correct | `1 cluster per week, 2 to 3 per cluster` | `2 to 3 per week` | cluster_burden, rate_bucket_or_denominator, current_vs_historical |
| 11216 | `all_agree_tool_accept` | accept_single_agent_tools | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 11216 | `all_agree_multi_accept` | accept_multi_agent_matched | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 11216 | `boundary_coordinator_agree` | accept_boundary_coordinator_agree | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 11216 | `no_seizure_free_introduction` | accept_multi_unless_seizure_free_introduction | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
| 11216 | `raw_repair_disagreement_fallback` | accept_multi_no_raw_repair_kind_disagreement | changed_both_wrong | `seizure free for 4 month` | `seizure free for multiple year` | unknown_boundary, seizure_free_duration, current_vs_historical, competing_semiologies, uncertainty_or_ambiguity |
