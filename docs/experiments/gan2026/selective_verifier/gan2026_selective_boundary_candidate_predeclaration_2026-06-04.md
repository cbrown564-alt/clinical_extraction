# Gan 2026 Selective Boundary-Candidate Predeclaration

This is a pre-run validation-development contract for selective LLM boundary-candidate proposal. It fixes the exact hard slice, prompt, schema, gates, and post-run accounting before any new live model calls.

## Decision

New selective boundary-candidate calls are authorized for the saved hard-panel recall-rescue slice: 22 validation rows where deterministic candidates did not cover the gold state but the saved LLM boundary proposal did.

## Stop/Go Evidence

Decision: `go`.

| Metric | Observed | Threshold |
| --- | ---: | ---: |
| exact evidence rate | 1.000 | 0.990 |
| valid source id rate | 1.000 | 0.990 |
| deterministic recall lost rows | 0 | 0 |
| p90 union candidate count | 3.000 | 4.000 |
| unsupported candidate rate | 0.011 | 0.050 |
| llm recall rescue rows | 22 | 1 |

## Exact Hard Slice

- Split: `validation` from `gan2026_split_v1`.
- Include only saved hard-panel rows with deterministic candidate recall false, saved LLM boundary-proposal recall true, union recall true, exact retained LLM proposal evidence, and at least one eligible hard-family tag.
- Exclude locked test rows, broad validation rows outside the saved hard panel, rows with non-exact saved proposal evidence, and rows where deterministic candidate recall already covers the gold state.

## Prompt Contract

Extract only seizure-frequency candidate facts that are easy to miss. Use exact words from the note for every evidence quote. Return candidates for uncertainty, no frequency reference, seizure-free claims with blockers, conditional-only events, competing seizure types, cluster patterns, diary or log summaries, and vague rates with a clear time basis. Do not choose a seizure-frequency answer. Do not rewrite ordinary rate facts unless they are needed to explain one of these hard cases. Use one string value, not a list, for each choice field such as candidate_kind, currentness, assertion_status, time_unit, and duration_unit. Use asserted, not no_reference, as assertion_status when candidate_kind is no_reference. For cluster statements, put the number of clusters and cluster timing in rate, and put seizures per cluster in cluster. Do not put seizures per cluster in rate count fields. If the note gives exact seizures per cluster, fill the numeric low/high fields and leave seizures_per_cluster_is_multiple false. If the note gives only seizures per cluster without timing, still return that cluster burden. For cluster timing, keep the stated unit: four to five weeks means time_count_low 4, time_count_high 5, and time_unit week. one to two times per month means count_low 1, count_high 2, time_count_low 1, and time_unit month. five days without seizures followed by a cluster means one cluster per five days, not one cluster per day.

The output must be JSON with one top-level `candidates` list. Each candidate must include `candidate_kind`, `evidence_quote`, `currentness`, `assertion_status`, `seizure_type`, `rate`, `cluster`, `seizure_free`, `conditionality_note`, `competing_state_summary`, `ambiguity_flags`, and `reason`.

## Claim Boundary

Validation-development selective boundary-candidate proposer predeclaration only. No live model calls, locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim are authorized.

## Artifacts

- Protocol: ``
- Boundary-candidate input JSONL: `experiments/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.json`
- Source candidate-union JSONL: `experiments/gan2026_candidate_union_saved_artifact_2026-06-04.jsonl`
- Source rich-state replay: `experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| predeclared rows | 22 |
| candidate union rows reviewed | 75 |
| saved recall rescue rows available | 22 |
| rows with note text | 22 |
| saved rescue proposal count | 22 |

## Hard Families

| Family | Rows |
| --- | ---: |
| `candidate_absent_or_weak` | 1 |
| `cluster_burden` | 8 |
| `cluster_or_diary` | 2 |
| `competing_semiologies` | 11 |
| `current_vs_historical` | 10 |
| `deterministic_miss` | 1 |
| `diary_or_log_aggregation` | 2 |
| `rate_bucket_or_denominator` | 6 |
| `seizure_free_duration` | 12 |
| `seizure_free_overreach` | 3 |
| `temporal_conflict` | 2 |
| `uncertainty_or_ambiguity` | 16 |
| `unknown_boundary` | 13 |
| `unknown_no_reference_boundary` | 3 |

## Post-Run Accounting

After outputs are collected, apply the existing candidate-union gates before any selected-state replay. Report retained, merged, and rejected candidates; candidate-recall rescue; evidence exactness; source-id validity; burden; and metadata completeness. Do not use proposer outputs as final labels.
