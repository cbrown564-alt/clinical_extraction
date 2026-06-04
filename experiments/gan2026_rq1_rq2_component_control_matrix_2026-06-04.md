# Gan 2026 RQ1/RQ2 Component-Control Matrix Analysis

Full validation-development analysis of the RQ1/RQ2 component-control matrix.
The `balanced_validation50` panel, paired-task overload conditions, and
`hidden_family_hard_panel` now contain fresh parsed outputs.

- Date: `2026-06-04`
- JSONL artifact: `experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl`
- Total matrix rows: 875
- Source rows represented: 115
- Completed output rows: 875/875
- Claim boundary: validation-development component analysis only; no locked-test or benchmark-comparable claim.

## Executive Findings

1. All 875 matrix rows now have parsed outputs. This includes all paired-task overload conditions and all 525 hidden-family hard-panel rows.
2. Single-task evidence selection remains the strongest surface: `candidate_conditioned_evidence_only` is 47/50 exact on balanced and 73/75 exact on hard rows; `gold_query_evidence_only` is 47/50 and 69/75.
3. Paired-task overload reduces exact-evidence quality, especially when projection is bundled with candidate/evidence generation: `candidate_plus_evidence_plus_projection` is 35/50 exact on balanced and 52/75 on hard rows.
4. Projection remains the weak link. Balanced projection-only parsed 50/50 but only 4/50 outputs exactly match canonical Gan labels; hard-panel projection needs the same deterministic rendering and policy-layer caution.
5. The completed hard panel confirms the mechanism pattern: text location is generally stronger than benchmark-state projection, especially for ambiguity, unknown-boundary, and benchmark-convention rows.

## Artifact Coverage

| Panel | Matrix rows | Source rows | Completed rows | Status |
| --- | ---: | ---: | ---: | --- |
| `balanced_validation50` | 350 | 50 | 350 | completed controls |
| `hidden_family_hard_panel` | 525 | 75 | 525 | completed controls |

## Condition Status

| Condition | Task | Panel | Rows | Parsed | Exact evidence | Output status |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `candidate_conditioned_evidence_only` | `evidence_selection` | `balanced_validation50` | 50 | 50/50 | 47/50 | fresh outputs present |
| `candidate_only` | `candidate_generation` | `balanced_validation50` | 50 | 50/50 | 47/50 | fresh outputs present |
| `candidate_plus_evidence` | `candidate_generation+evidence_selection` | `balanced_validation50` | 50 | 50/50 | 40/50 | fresh outputs present |
| `candidate_plus_evidence_plus_projection` | `candidate_generation+evidence_selection+projection` | `balanced_validation50` | 50 | 50/50 | 35/50 | fresh outputs present |
| `evidence_plus_projection` | `evidence_selection+projection` | `balanced_validation50` | 50 | 50/50 | 50/50 | fresh outputs present |
| `gold_query_evidence_only` | `evidence_selection` | `balanced_validation50` | 50 | 50/50 | 47/50 | fresh outputs present |
| `projection_only` | `projection` | `balanced_validation50` | 50 | 50/50 | 0/50 | fresh outputs present |
| `candidate_conditioned_evidence_only` | `evidence_selection` | `hidden_family_hard_panel` | 75 | 75/75 | 73/75 | fresh outputs present |
| `candidate_only` | `candidate_generation` | `hidden_family_hard_panel` | 75 | 75/75 | 67/75 | fresh outputs present |
| `candidate_plus_evidence` | `candidate_generation+evidence_selection` | `hidden_family_hard_panel` | 75 | 75/75 | 63/75 | fresh outputs present |
| `candidate_plus_evidence_plus_projection` | `candidate_generation+evidence_selection+projection` | `hidden_family_hard_panel` | 75 | 75/75 | 52/75 | fresh outputs present |
| `evidence_plus_projection` | `evidence_selection+projection` | `hidden_family_hard_panel` | 75 | 75/75 | 74/75 | fresh outputs present |
| `gold_query_evidence_only` | `evidence_selection` | `hidden_family_hard_panel` | 75 | 75/75 | 69/75 | fresh outputs present |
| `projection_only` | `projection` | `hidden_family_hard_panel` | 75 | 75/75 | 0/75 | fresh outputs present |

## RQ1 Candidate-Only Readout

| Metric | Value |
| --- | ---: |
| Parsed rows | 50/50 |
| Exact-evidence rows | 47/50 |
| Candidate facts emitted | 60 |
| Mean candidates per row | 1.20 |
| Median candidates per row | 1 |
| P90 candidates per row | 2 |
| Rows with no candidates | 8 |

| Candidate kind | Count |
| --- | ---: |
| `frequency_rate` | 35 |
| `cluster_frequency` | 10 |
| `seizure_free` | 8 |
| `last_event_only` | 5 |
| `unknown_frequency` | 2 |

| Temporality | Count |
| --- | ---: |
| `current` | 37 |
| `recent` | 16 |
| `historical` | 7 |

| Confidence | Count |
| --- | ---: |
| `high` | 51 |
| `medium` | 9 |

Interpretation: candidate-only is useful as an RQ1 recall surface, not as a final answer selector. It emits a small candidate burden, mostly one or two facts per note, and preserves ambiguity on many rows. The eight zero-candidate rows are expected to include `unknown` or `no_reference` cases rather than automatic failures.

Non-exact or unchecked candidate rows:

| Row | Gold | Status | Mechanism note |
| ---: | --- | --- | --- |
| 79 | `6 to 7 per year` | `not_exact` | seizure frequency currently reported as ≤ 6 to 7 per year |
| 744 | `multiple per week` | `not_checked` | raw output retained; exact-evidence checker did not validate the parsed packet |
| 2932 | `seizure free for 9 month` | `not_checked` | raw output retained; exact-evidence checker did not validate the parsed packet |

## RQ2 Gold-Query Evidence Only Readout

| Metric | Value |
| --- | ---: |
| Parsed rows | 50/50 |
| Exact-evidence rows | 47/50 |
| Evidence spans emitted | 126 |
| Mean spans per row | 2.52 |
| Median spans per row | 3 |
| P90 spans per row | 3 |
| Rows with insufficient-evidence reason | 6 |

| Evidence role | Count |
| --- | ---: |
| `supporting_context` | 58 |
| `decisive` | 52 |
| `historical` | 8 |
| `future_planned` | 8 |

| Support status | Count |
| --- | ---: |
| `supports_candidate` | 89 |
| `not_applicable` | 37 |

| Most frequent missing component | Count |
| --- | ---: |
| `rate_time_basis` | 69 |
| `count` | 57 |
| `timeframe` | 48 |
| `unit` | 40 |
| `per_cluster_burden` | 25 |
| `seizure_free_duration` | 23 |
| `cluster_cadence` | 18 |

Interpretation: this is a strong evidence-location surface but not a full clinical decision surface. Missing operands remain common by design because the prompt is allowed to say that selected evidence is decisive, contextual, or incomplete without rendering a Gan label.

Non-exact evidence rows:

| Row | Gold | Status | Mechanism note |
| ---: | --- | --- | --- |
| 40 | `4 per week` | `not_exact` | Since my last assessment he reports a variable pattern of episodes but overall a frequency of ≤ four seizures per week |
| 180 | `1 per 7 day` | `not_exact` | The patient keeps a diary and describes a pattern of seizures every seven days |
| 182 | `1 per 2 day` | `not_exact` | The carer reports that seizures are occurring every 2 days on average, based on a written diary and a smartphone log tha |

## RQ2 Candidate-Conditioned Evidence Only Readout

| Metric | Value |
| --- | ---: |
| Parsed rows | 50/50 |
| Exact-evidence rows | 47/50 |
| Evidence spans emitted | 51 |
| Mean spans per row | 1.02 |
| Median spans per row | 1 |
| P90 spans per row | 1 |
| Rows with insufficient-evidence reason | 5 |

| Evidence role | Count |
| --- | ---: |
| `decisive` | 39 |
| `supporting_context` | 9 |
| `non_seizure_or_indirect_context` | 3 |

| Support status | Count |
| --- | ---: |
| `supports_candidate` | 43 |
| `incompletely_supports_candidate` | 5 |
| `not_applicable` | 3 |

| Most frequent missing component | Count |
| --- | ---: |
| `unit` | 41 |
| `timeframe` | 36 |
| `rate_time_basis` | 35 |
| `count` | 35 |
| `per_cluster_burden` | 26 |
| `cluster_cadence` | 22 |
| `seizure_free_duration` | 21 |

Interpretation: this is a strong evidence-location surface but not a full clinical decision surface. Missing operands remain common by design because the prompt is allowed to say that selected evidence is decisive, contextual, or incomplete without rendering a Gan label.

Non-exact evidence rows:

| Row | Gold | Status | Mechanism note |
| ---: | --- | --- | --- |
| 79 | `6 to 7 per year` | `not_exact` | seizure frequency currently reported as ≤ 6 to 7 per year |
| 2938 | `seizure free for 8 month` | `not_exact` | he reports that he has been Seizure-free since 13-Nov-2015 |
| 11411 | `no seizure frequency reference` | `not_exact` | No explicit seizure frequency information is present in the note to fully support or contradict the candidate. |

## Projection-Only Readout

| Metric | Value |
| --- | ---: |
| Parsed rows | 50/50 |
| Exact canonical label matches | 4/50 |
| Broad decision-kind matches | 33/50 |
| Null or abstained labels | 22/50 |

| Gold kind | Rows | Exact label | Broad kind match | Null label |
| --- | ---: | ---: | ---: | ---: |
| `frequency` | 20 | 4 | 18 | 2 |
| `no_reference` | 6 | 0 | 6 | 6 |
| `seizure_free` | 8 | 0 | 8 | 2 |
| `unknown` | 8 | 0 | 0 | 6 |
| `unresolved_multiple` | 8 | 0 | 1 | 6 |

| Gold kind -> decision kind | Rows |
| --- | ---: |
| `frequency` -> `frequency` | 18 |
| `seizure_free` -> `seizure_free` | 8 |
| `no_reference` -> `no_reference` | 6 |
| `unknown` -> `no_reference` | 5 |
| `unresolved_multiple` -> `no_reference` | 4 |
| `unknown` -> `seizure_free` | 3 |
| `unresolved_multiple` -> `frequency` | 2 |
| `frequency` -> `unknown` | 1 |
| `unresolved_multiple` -> `seizure_free` | 1 |
| `unresolved_multiple` -> `unknown` | 1 |
| `frequency` -> `seizure_free` | 1 |

Interpretation: projection-only separates semantic selection from benchmark rendering. The model often recognizes ordinary frequency and seizure-free states, but it does not reliably emit canonical Gan labels and it mishandles `unknown` and `unresolved_multiple` policy states. This supports a deterministic compiler or policy layer after any LLM-selected state, plus an explicit ambiguity/review routing policy rather than direct model rendering.

Projection-kind mismatches:

| Row | Gold | Gold kind | Predicted label | Decision kind | Families |
| ---: | --- | --- | --- | --- | --- |
| 187 | `1 per 7 to 9 day` | `frequency` | `None` | `unknown` | `cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies` |
| 278 | `multiple per week` | `unresolved_multiple` | `seizure free` | `seizure_free` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| 280 | `multiple per day` | `unresolved_multiple` | `None` | `unknown` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| 338 | `multiple per month` | `unresolved_multiple` | `None` | `no_reference` | `cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| 466 | `21 to 28 per month` | `frequency` | `None` | `seizure_free` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies` |
| 743 | `multiple per week` | `unresolved_multiple` | `None` | `no_reference` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` |
| 869 | `multiple per month` | `unresolved_multiple` | `None` | `no_reference` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` |
| 1317 | `unknown, multiple per cluster` | `unknown` | `None` | `no_reference` | `cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` |
| 1687 | `multiple per week` | `unresolved_multiple` | `None` | `frequency` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;benchmark_format_convention` |
| 1695 | `multiple per month` | `unresolved_multiple` | `None` | `no_reference` | `diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity;benchmark_format_convention` |
| 2149 | `unknown` | `unknown` | `None` | `no_reference` | `unknown_boundary;cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| 2166 | `unknown` | `unknown` | `None` | `no_reference` | `unknown_boundary;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| 3356 | `unknown` | `unknown` | `seizure free` | `seizure_free` | `unknown_boundary;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| 3371 | `unknown` | `unknown` | `None` | `seizure_free` | `unknown_boundary;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| 3436 | `unknown` | `unknown` | `None` | `no_reference` | `unknown_boundary;cluster_burden;rate_bucket_or_denominator;current_vs_historical;uncertainty_or_ambiguity` |
| 3468 | `unknown` | `unknown` | `None` | `no_reference` | `unknown_boundary;seizure_free_duration;cluster_burden;diary_or_log_aggregation;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |
| 3469 | `unknown` | `unknown` | `seizure free for 6 months` | `seizure_free` | `unknown_boundary;cluster_burden;diary_or_log_aggregation;rate_bucket_or_denominator;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity` |

## Paired-Task And Hard-Panel Summary

| Panel | Condition | Rows | Parsed | Exact evidence | Valid source ids |
| --- | --- | ---: | ---: | ---: | ---: |
| `balanced_validation50` | `candidate_only` | 50 | 50/50 | 47/50 | 0/50 |
| `balanced_validation50` | `gold_query_evidence_only` | 50 | 50/50 | 47/50 | 0/50 |
| `balanced_validation50` | `candidate_conditioned_evidence_only` | 50 | 50/50 | 47/50 | 0/50 |
| `balanced_validation50` | `projection_only` | 50 | 50/50 | 0/50 | 0/50 |
| `balanced_validation50` | `candidate_plus_evidence` | 50 | 50/50 | 40/50 | 41/50 |
| `balanced_validation50` | `evidence_plus_projection` | 50 | 50/50 | 50/50 | 50/50 |
| `balanced_validation50` | `candidate_plus_evidence_plus_projection` | 50 | 50/50 | 35/50 | 36/50 |
| `hidden_family_hard_panel` | `candidate_only` | 75 | 75/75 | 67/75 | 69/75 |
| `hidden_family_hard_panel` | `gold_query_evidence_only` | 75 | 75/75 | 69/75 | 75/75 |
| `hidden_family_hard_panel` | `candidate_conditioned_evidence_only` | 75 | 75/75 | 73/75 | 75/75 |
| `hidden_family_hard_panel` | `projection_only` | 75 | 75/75 | 0/75 | 0/75 |
| `hidden_family_hard_panel` | `candidate_plus_evidence` | 75 | 75/75 | 63/75 | 69/75 |
| `hidden_family_hard_panel` | `evidence_plus_projection` | 75 | 75/75 | 74/75 | 75/75 |
| `hidden_family_hard_panel` | `candidate_plus_evidence_plus_projection` | 75 | 75/75 | 52/75 | 57/75 |

Overload interpretation: paired prompts parse reliably, but exact-evidence quality drops when candidate discovery, evidence selection, and projection are bundled. The `evidence_plus_projection` condition is the exception: because it conditions on a fixed candidate, it preserves exact evidence on 50/50 balanced rows and 74/75 hard rows. The full bundled condition should therefore be treated as a stress surface, not a preferred architecture.

## Balanced Panel Hidden-Family Readout

| Family | Rows | Candidate exact | Gold-query evidence exact | Candidate-conditioned evidence exact | Projection kind match |
| --- | ---: | ---: | ---: | ---: | ---: |
| `benchmark_format_convention` | 9 | 8/9 | 9/9 | 9/9 | 1/9 |
| `cluster_burden` | 24 | 22/24 | 23/24 | 22/24 | 14/24 |
| `competing_semiologies` | 43 | 40/43 | 41/43 | 40/43 | 27/43 |
| `current_vs_historical` | 49 | 46/49 | 46/49 | 46/49 | 32/49 |
| `diary_or_log_aggregation` | 47 | 44/47 | 44/47 | 44/47 | 31/47 |
| `rate_bucket_or_denominator` | 38 | 36/38 | 36/38 | 36/38 | 24/38 |
| `seizure_free_duration` | 10 | 9/10 | 10/10 | 9/10 | 9/10 |
| `uncertainty_or_ambiguity` | 19 | 19/19 | 19/19 | 19/19 | 8/19 |
| `unknown_boundary` | 7 | 7/7 | 7/7 | 7/7 | 0/7 |

Family interpretation: exact evidence stays high even in dense overlapping families, but projection degrades on benchmark conventions, unknown boundaries, unresolved multiple states, and ambiguity-heavy rows. That pattern points to representation and policy failures rather than a simple inability to locate text.

## Instrumentation Gaps And Next Analysis

- Paired-task overload rows with outputs: 375/375.
- Hidden-family hard-panel rows with outputs: 525/525.
- Completed rows missing `source_id_status`: 200/875.
- Completed rows missing `model_id`: 0/875.
- `projection_only` exact-evidence status is `not_checked` by design because the input is fixed candidate/evidence state rather than newly selected spans.

## Decision

The completed matrix supports a development-control answer across the fixed validation surfaces: candidate generation and evidence selection are worth carrying forward as component surfaces, while projection should not be trusted as direct final-label rendering. Use paired prompts as overload diagnostics rather than preferred final architecture, and keep deterministic rendering/policy gates after LLM-selected facts.

