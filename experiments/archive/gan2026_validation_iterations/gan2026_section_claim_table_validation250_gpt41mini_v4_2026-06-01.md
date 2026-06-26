# Gan 2026 Section Claim Table V4

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a flat section-and-claim table can expose temporal, conflict, and evidence-state failures before the model collapses them into one final label.

Prediction-bearing component: model-produced claim rows plus model final query. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 250 rows.
Escalation reason: v4 passed the 50-row architecture gate; this 250-row diagnostic tests whether the section-claim-table v4 family should be promoted, revised, or rejected before any larger validation run

## Model And Prompt Metadata

- Pipeline: `gan2026_section_claim_table_v4`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-first claim extractor and final query selector
- Prompt/program version: `gan2026_section_claim_table_v4`
- Temperature: `0.0`
- Max tokens: `1400`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `220`
- Reuse source: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_2026-06-01.jsonl, experiments/gan2026_section_claim_table_validation50_gpt41mini_v4_2026-06-01.jsonl`
- Optimizer: none
- Prompt policy taxonomy: `sct_v4.schema.scalar_enum_output`, `sct_v4.schema.strict_json_object`, `sct_v4.evidence.exact_substring`, `sct_v4.gan_label.parser_ready_surface`, `sct_v4.gan_label.interval_preservation`, `sct_v4.gan_label.cluster_dual_axis`, `sct_v4.selection.current_burden_precedence`, `sct_v4.selection.add_same_window_counts`, `sct_v4.boundary.unknown_no_reference_seizure_free`, `sct_v4.exclusion.proxy_or_conditional_frequency`, `sct_v4.gan_label.compact_interval_notation`, `sct_v4.gan_label.maximum_burden`
- Deterministic rule configuration: none before prediction; deterministic code only validates, performs strict/frozen clean scorer-facing repair, and scores.
- Git commit: `691903d`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_2026-06-01.jsonl`

## Summary

- Structured claim-table records: 248 / 250
- Call failures: 0
- Parse/schema/label issues: 2
- Exact claim evidence substrings: 593 / 601
- Exact selected final evidence substrings: 247 / 250
- raw final-query score: Purist 0.9080 (227 / 250), Pragmatic 0.9360 (234 / 250)
- Strict-format score: Purist 0.9160 (229 / 250), Pragmatic 0.9440 (236 / 250)
- Frozen clean scorer-facing score: Purist 0.9200 (230 / 250), Pragmatic 0.9480 (237 / 250)
- Rows changed by downstream repair layers: 33

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 2 |
| claim_extraction | 10 |
| temporality_conflict | 0 |
| final_query | 3 |
| parse_schema | 2 |
| scorer_format | 7 |

## Reviewable Failure Details

| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |
| ---: | --- | --- | --- |
| 182 | claim evidence not exact (c2: No use of rescue medication since the last appointment) |  |  |
| 763 | claim evidence not exact (c4: no clear myoclonic jerks or sustained tonic–clonic movements) |  |  |
| 891 | claim evidence not exact (c4: No witnessed generalised tonic–clonic seizures.) |  |  |
| 1317 |  | unparsable_label: 1 cluster per day (Unparsable cluster label: '1 cluster per day') |  |
| 2678 |  | unparsable_label: 1 per night (Unparsable label (raw: '1 per night' / normalized: '1 per night')) |  |
| 3468 | claim evidence not exact (c1: She observes a clear and consistent catamenial pattern: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free.); selected evidence not exact (She observes a clear and consistent catamenial pattern: Seizures happen when perimenstrual only (days -2 to +2). Outside this window she remains seizure-free.) |  |  |
| 3534 |  | unparsable_label: seizure_free for 6 month (Unparsable label (raw: 'seizure_free for 6 month' / normalized: 'seizure_free for 6 month')) |  |
| 3623 |  | unparsable_label: up to 7 per week (Unparsable label (raw: 'up to 7 per week' / normalized: 'up to 7 per week')) |  |
| 3643 |  | missing_final_label | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple' |
| 4368 | claim evidence not exact (c5: No family history of seizures reported.) |  |  |
| 4574 | claim evidence not exact (c3: No tongue biting or urinary incontinence reported) |  |  |
| 4842 |  | missing_final_label | schema_validation_error: Extra inputs are not permitted |
| 5210 | claim evidence not exact (c2: No episodes suggestive of absence, myoclonus, or nocturnal events) |  |  |
| 5406 | claim evidence not exact (c4: No injuries, no tongue biting, and recovery is rapid when episodes occur, aligning with non-epileptic-like events rather than electroclinical seizures.) |  |  |
| 5551 |  | unparsable_label: several per day (Unparsable label (raw: 'several per day' / normalized: 'several per day')) |  |

## Diagnostic Review

Decision: revise before any larger validation run. This is a completed 250-row validation diagnostic, not a promotion signal.

Interpretation: v4 stays above the 0.9000 Purist development threshold, but the architecture gate is not clean enough for scale-up. This artifact has 248/250 structured records, 0 call failures, 2 parse/schema failures, 247/250 exact selected final evidence substrings, and 230/250 clean Purist. Raw-to-clean repair changes 33 rows and improves Purist from 227/250 to 230/250, so the score remains a mixed LLM-plus-format/clean-policy development result.

Resume/retry note: a parallel resume artifact, `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_resume_2026-06-01.md`, completed with 229/250 clean Purist and 236/250 clean Pragmatic. Treat the one-row difference as retry variance in the live tail, not as a prompt or policy change.

Main failure families: interval or denominator mismatch, cluster-axis handling, seizure-free versus unknown/no-reference boundary errors, two schema/parse failures, and a small number of evidence-exactness misses. The 50-row watch item persists: row 1046 collapses an uncertain count range to a point estimate. New misses add cluster count/per-cluster confusion, seizure-free boundary errors, and cadence denominator errors.

Next action: do row-level family review and targeted v5 prompt/schema revision on validation only. Do not run beyond this 250-row slice or inspect holdout rows until the failure-family review produces a written change hypothesis.

## Rows

| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes |  |
| 40 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 79 | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes |  |
| 103 | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per year | yes | yes |  |
| 128 | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes |  |
| 180 | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes |  |
| 182 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes | claim_extraction |
| 187 | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes |  |
| 190 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 198 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes |  |
| 212 | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes |  |
| 218 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 243 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 278 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 409 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 419 | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes |  |
| 598 | 1 per 8 month | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes |  |
| 659 | 2 per 4 day | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes |  |
| 665 | 2 per 2 week | 2 per 2 week | 2 per 2 week | 2 per 2 week | yes | yes |  |
| 678 | 2 per 4 month | 2 per 4 month | 2 per 4 month | 2 per 4 month | yes | yes |  |
| 694 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | 2 per month | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 725 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 744 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 763 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes | claim_extraction |
| 790 | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | 1 per 7 to 10 day | yes | yes |  |
| 816 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | 1 per 12 month | 1 per 12 month | 1 per 12 month | 1 per year | yes | yes |  |
| 854 | 1 per year | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 891 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes | claim_extraction |
| 899 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 959 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 960 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 978 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 987 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 1030 | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | 5 per month | 5 per month | 5 per month | 3 to 5 per month | no | no |  |
| 1070 | 3 to 4 per 1 week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | 3 to 5 per 1 week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes |  |
| 1171 | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | 7 to 9 per 3 week | yes | yes |  |
| 1207 | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | 21 to 28 per 3 month | yes | yes |  |
| 1223 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1249 | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | 2 to 4 per week | yes | yes |  |
| 1281 | 5 to 7 per 1 year | 5 to 7 per year | 5 to 7 per year | 5 to 7 per year | yes | yes |  |
| 1317 | 1 cluster per day | 1 cluster per day | 1 per day | unknown, multiple per cluster |  | no | scorer_format |
| 1357 | 1 per 1 day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 1363 | 3 per 1 day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 1413 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 1454 | 7 per 1 week | 7 per week | 7 per week | 7 per week | yes | yes |  |
| 1486 | 3 per month | 3 per month | 3 per month | 3 per month | yes | yes |  |
| 1573 | 11 per 1 week | 11 per week | 11 per week | 11 per week | yes | yes |  |
| 1591 | 11 per 1 month | 11 per month | 11 per month | 11 per month | yes | yes |  |
| 1596 | 12 per 1 week | 12 per week | 12 per week | 12 per week | yes | yes |  |
| 1597 | 12 per 1 month | 12 per month | 12 per month | 12 per month | yes | yes |  |
| 1636 | 5 per 1 month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 1640 | 5 per 1 week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 1687 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 1694 | 3 per 2 week | 3 per 2 week | 3 per 2 week | 1 cluster per 2 week, 3 per cluster | yes | yes |  |
| 1695 | unknown | unknown | unknown | multiple per month | yes | yes |  |
| 1706 | unknown | unknown | unknown | multiple cluster per month, multiple per cluster | no | no |  |
| 1707 | unknown | unknown | unknown | multiple per week | yes | yes |  |
| 1772 | 11 per 6 month | 11 per 6 month | 11 per 6 month | 11 per 6 month | yes | yes |  |
| 1773 | 11 per 3 month | 11 per 3 month | 11 per 3 month | 11 per 3 month | yes | yes |  |
| 1790 | 8 per 4 month | 8 per 4 month | 8 per 4 month | 8 per 4 month | yes | yes |  |
| 1794 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1866 | 8 per 2 month | 8 per 2 month | 8 per 2 month | 8 per 2 month | yes | yes |  |
| 1880 | 7 per 2 month | 7 per 2 month | 7 per 2 month | 8 per 2 month | no | no |  |
| 1887 | 4 per 3 month | 4 per 3 month | 4 per 3 month | 4 per 3 month | yes | yes |  |
| 1914 | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1922 | 7 per 3 month | 7 per 3 month | 7 per 3 month | 7 per 3 month | yes | yes |  |
| 1923 | 7 per 6 month | 7 per 6 month | 7 per 6 month | 7 per 6 month | yes | yes |  |
| 1979 | 6 per 2 month | 6 per 2 month | 6 per 2 month | 6 per 2 month | yes | yes |  |
| 1980 | 6 per 3 month | 6 per 3 month | 6 per 3 month | 6 per 3 month | yes | yes |  |
| 2023 | 5 per month | 5 per month | 5 per month | 5 per month | yes | yes |  |
| 2080 | unknown | unknown | unknown | multiple per month | yes | yes |  |
| 2094 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2114 | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 2149 | unknown | unknown | unknown | unknown | yes | yes |  |
| 2166 | unknown | unknown | unknown | unknown | yes | yes |  |
| 2228 | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | 3 to 5 per 2 week | yes | yes |  |
| 2233 | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | 6 to 7 per 2 month | yes | yes |  |
| 2245 | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | 7 to 8 per 3 week | yes | yes |  |
| 2259 | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | 6 to 8 per 3 month | yes | yes |  |
| 2354 | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | 6 to 7 per week | yes | yes |  |
| 2366 | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per 12 month | 2 to 4 per year | yes | yes |  |
| 2369 | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | 3 to 4 per month | yes | yes |  |
| 2374 | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | 7 to 9 per month | yes | yes |  |
| 2425 | 6 to 8 per 1 month | 6 to 8 per month | 6 to 8 per month | 6 to 8 per month | yes | yes |  |
| 2427 | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 2435 | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | 5 to 7 per 2 week | yes | yes |  |
| 2437 | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | 2 to 3 per 2 month | yes | yes |  |
| 2440 | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | 5 to 7 per 2 month | yes | yes |  |
| 2456 | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | 6 to 7 per 2 week | yes | yes |  |
| 2459 | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | 7 to 9 per 2 week | yes | yes |  |
| 2487 | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | 2 to 3 per 3 month | yes | yes |  |
| 2513 | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | 2 to 3 per 2 week | yes | yes |  |
| 2541 | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | 8 to 9 per 2 week | yes | yes |  |
| 2548 | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | 5 to 6 per 2 month | yes | yes |  |
| 2554 | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | 1 to 10 per 2 month | yes | yes |  |
| 2558 | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | 3 to 4 per 2 month | yes | yes |  |
| 2609 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2622 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2628 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2678 | 1 per night | 1 per day | 1 per day | 1 per day |  | yes | scorer_format |
| 2681 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2698 | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes |  |
| 2731 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 2740 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2748 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2759 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2762 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2765 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 2776 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2789 | 1 per week | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 2812 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2822 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2824 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 2877 | 2 per 1 year | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 2887 | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 2907 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 2932 | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | seizure free for 9 month | yes | yes |  |
| 2938 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 8 month | yes | yes |  |
| 2965 | seizure free for 1 year 4 month | seizure free for 1 year | seizure free for 1 year | seizure free for 16 month | yes | yes |  |
| 2992 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for 7 month | yes | yes |  |
| 3015 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 12 month | yes | yes |  |
| 3048 | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | seizure free for 16 month | yes | yes |  |
| 3058 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3082 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | yes | yes |  |
| 3095 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 3113 | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | seizure free for 14 month | yes | yes |  |
| 3118 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 3137 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 3224 | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | 1 cluster per month, 6 to 7 per cluster | yes | yes |  |
| 3242 | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 1 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3261 | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 1 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster | no | no |  |
| 3262 | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | 2 cluster per month, 5 per cluster | yes | yes |  |
| 3281 | 8 per 30 day | 8 per 30 day | 8 per 30 day | 8 per month | yes | yes |  |
| 3297 | 6 per 30 day | 6 per 30 day | 6 per 30 day | 6 per month | yes | yes |  |
| 3325 | 3 per week | 3 per week | 3 per week | 3 per week | yes | yes |  |
| 3356 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3371 | seizure free for 8 week | seizure free for multiple year | seizure free for multiple year | unknown | no | no |  |
| 3436 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3468 | unknown | unknown | unknown | unknown | yes | yes | claim_extraction,final_query |
| 3469 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | unknown | no | no |  |
| 3482 | 1 per 7 day | 1 per 7 day | 1 per 7 day | unknown | no | no |  |
| 3493 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3507 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3512 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3528 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3532 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3534 | seizure_free for 6 month | seizure_free for 6 month | seizure_free for 6 month | unknown |  |  | scorer_format |
| 3600 | unknown | unknown | unknown | unknown | yes | yes |  |
| 3623 | up to 7 per week | 7 per week | 7 per week | 7 per week |  | yes | scorer_format |
| 3643 | None | None | None | 7 per week |  |  | schema_validation_error: Input should be 'frequency', 'seizure_free', 'unknown', 'no_reference' or 'unresolved_multiple'; claim_extraction,final_query,parse_schema,scorer_format |
| 3681 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3682 | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3710 | 5 per week | 5 per week | 5 per week | 5 per week | yes | yes |  |
| 3753 | 1 per day | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 3766 | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3774 | 9 per 1 year | 9 per year | 9 per year | 9 per year | yes | yes |  |
| 3791 | 10 per 12 month | 10 per 12 month | 10 per 12 month | 10 per year | yes | yes |  |
| 3801 | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 3806 | 6 per month | 6 per month | 6 per month | 6 per month | yes | yes |  |
| 3827 | 7 per month | 7 per month | 7 per month | 7 per month | yes | yes |  |
| 3846 | 2 per day | 2 per day | 2 per day | 2 per day | yes | yes |  |
| 3849 | 3 per day | 3 per day | 3 per day | 3 per day | yes | yes |  |
| 3889 | 8 per year | 8 per year | 8 per year | 8 per year | yes | yes |  |
| 3892 | 3 per year | 3 per year | 3 per year | 3 per year | yes | yes |  |
| 3940 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3949 | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes |  |
| 3988 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 3995 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 3999 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4022 | 8 per 3 month | 8 per 3 month | 8 per 3 month | 8 per month | no | no |  |
| 4026 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 4092 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4100 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4110 | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | 1 per 1 to 2 day | yes | yes |  |
| 4116 | 1 to 2 per day | 1 to 2 per day | 1 to 2 per day | 1 per 1 to 2 day | no | no |  |
| 4173 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per 2 week | yes | yes |  |
| 4243 | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | 1 per 2 to 3 week | yes | yes |  |
| 4258 | 4 per 7 day | 4 per 7 day | 4 per 7 day | 4 per week | yes | yes |  |
| 4337 | 3 per 3 month | 3 per 3 month | 3 per 3 month | 3 per 3 month | yes | yes |  |
| 4345 | 4 per 2 week | 4 per 2 week | 4 per 2 week | 4 per month | no | no |  |
| 4368 | 5 per 2 month | 5 per 2 month | 5 per 2 month | 5 per 2 month | yes | yes | claim_extraction |
| 4402 | 1 per month | 1 per month | 1 per month | 7 per 7 month | yes | yes |  |
| 4410 | 1 per 2 to 3 month | 1 per 2 to 3 month | 1 per 2 to 3 month | 4 per 7 month | yes | yes |  |
| 4478 | 19 per 1 week | 19 per week | 19 per week | 19 per week | yes | yes |  |
| 4480 | 3 to 5 per 1 week | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 4496 | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | 7 to 8 per 3 month | yes | yes |  |
| 4562 | 1 per 6 week | 1 per 6 week | 1 per 6 week | 1 per 6 week | yes | yes |  |
| 4563 | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes |  |
| 4574 | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes | claim_extraction |
| 4592 | 1 per 2 month | 1 per 2 month | 1 per 2 month | 1 per 2 month | yes | yes |  |
| 4597 | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes |  |
| 4624 | 2 per 1 month | 2 per month | 2 per month | 1 per 3 to 4 day | no | no |  |
| 4631 | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | 1 per 14 to 21 day | yes | yes |  |
| 4690 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4694 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4700 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4709 | unknown | unknown | unknown | multiple per day | yes | yes |  |
| 4731 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4732 | unknown | unknown | unknown | unknown | yes | yes |  |
| 4771 | 2 per 6 week | 2 per 6 week | 2 per 6 week | unknown | no | no |  |
| 4839 | seizure free for 4 month | seizure free for 4 month | seizure free for 4 month | seizure free for multiple month | yes | yes |  |
| 4842 | None | None | None | seizure free for multiple month |  |  | schema_validation_error: Extra inputs are not permitted; claim_extraction,final_query,parse_schema,scorer_format |
| 4910 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes | segmentation_sectioning |
| 4919 | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | seizure free for 2 year | yes | yes |  |
| 4926 | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | seizure free for 1 year | yes | yes |  |
| 4951 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 4956 | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | seizure free for 7 month | yes | yes |  |
| 4992 | seizure free for 10 month | seizure free for 10 month | seizure free for 10 month | seizure free for 11 month | yes | yes |  |
| 4994 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | yes | yes |  |
| 5040 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for 6 months | yes | yes |  |
| 5082 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5092 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5110 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 5121 | no seizure frequency reference | no seizure frequency reference | no seizure frequency reference | seizure free for multiple month | no | no |  |
| 5136 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5141 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5197 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes |  |
| 5210 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple month | yes | yes | claim_extraction |
| 5221 | seizure free for 1 year 9 month | seizure free for 1 year | seizure free for 1 year | seizure free for multiple month | yes | yes |  |
| 5248 | seizure free | seizure free for multiple year | seizure free for multiple year | seizure free for multiple year | yes | yes |  |
| 5331 | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | seizure free for 12 month | yes | yes |  |
| 5345 | seizure free for 6 month | seizure free for 6 month | seizure free for 6 month | seizure free for multiple month | yes | yes |  |
| 5351 | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | seizure free for 18 month | yes | yes |  |
| 5379 | seizure free for 3 month | seizure free for 3 month | seizure free for 3 month | seizure free for multiple month | yes | yes |  |
| 5406 | seizure free for 2 month | seizure free for 2 month | seizure free for 2 month | seizure free for multiple month | yes | yes | claim_extraction |
| 5476 | 1 per 1 month | 1 per month | 1 per month | unknown | no | no |  |
| 5490 | unknown | unknown | unknown | unknown | yes | yes | segmentation_sectioning |
| 5491 | 2 per 6 week | 2 per 6 week | 2 per 6 week | unknown | no | no |  |
| 5504 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5507 | unknown | unknown | unknown | unknown | yes | yes |  |
| 5528 | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 5534 | 1 per 2 week | 1 per 2 week | 1 per 2 week | 1 per multiple month | no | no |  |
| 5551 | several per day | several per day | multiple per day | multiple per day |  | yes | scorer_format |
| 5567 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 5584 | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes |  |
