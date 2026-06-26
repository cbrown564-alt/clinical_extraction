# Gan 2026 Atlas Hard-Slice No-Call Diagnostic

Diagnostic validation-cycle replay over saved artifacts. This does not change the pipeline, scorer, prompts, graph projection policy, or holdout status.

- Split manifest: `gan2026_split_v1`
- Rows: 87 slice memberships
- Unique source rows: 55
- JSONL artifact: `experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.jsonl`
- Summary JSON: `experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.json`

## Slice Summary

| Slice | Rows | Baseline correct | LLM sidecar scorable | LLM sidecar correct | LLM rescues | Graph replay rows | Best projection corrections | Projection regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `candidate_generation_rescue` | 44 | 0 | 8 | 6 | 6 | 44 | 1 | 0 |
| `candidate_generation_unknown_seizure_free_boundary` | 26 | 0 | 8 | 6 | 6 | 26 | 1 | 0 |
| `projection_arbitration` | 11 | 0 | 4 | 1 | 1 | 9 | 9 | 0 |
| `projection_unknown_seizure_free_arbitration` | 6 | 0 | 2 | 1 | 1 | 6 | 6 | 0 |

## Projection Variants

| Variant | Rows | Exact | Corrections vs baseline | Regressions vs baseline |
| --- | ---: | ---: | ---: | ---: |
| `baseline_v0` | 85 | 0 | 0 | 0 |
| `boundary_state_priority` | 85 | 9 | 9 | 0 |
| `competing_frequency_uncertainty` | 85 | 4 | 4 | 0 |
| `lowest_current_frequency` | 85 | 6 | 6 | 0 |
| `oracle_gold_node` | 85 | 15 | 15 | 0 |
| `seizure_free_priority` | 85 | 0 | 0 | 0 |

## Rows That Would Change

These rows are generated from diagnostic sidecars and ablation variants. They describe what would change under a hypothetical gate or projection variant; they are not current production-policy changes.

### LLM Candidate Sidecar Rescues

| Row | Gold | Current final | Deterministic label | LLM sidecar | Families | Why |
| ---: | --- | --- | --- | --- | --- | --- |
| 3356 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM candidate selector raw layer is Purist-correct while deterministic safety-floor final label is Purist-wrong. |
| 6244 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | unknown_boundary;seizure_free_duration;uncertainty_or_ambiguity | LLM candidate selector raw layer is Purist-correct while deterministic safety-floor final label is Purist-wrong. |
| 6321 | `unknown` | `1 per day` | `1 per day` | `unknown` | unknown_boundary;rate_bucket_or_denominator;uncertainty_or_ambiguity | LLM candidate selector raw layer is Purist-correct while deterministic safety-floor final label is Purist-wrong. |
| 10266 | `unknown` | `1 per 5 day` | `1 per 5 day` | `unknown` | unknown_boundary;cluster_burden;diary_or_log_aggregation;uncertainty_or_ambiguity | LLM candidate selector raw layer is Purist-correct while deterministic safety-floor final label is Purist-wrong. |
| 11259 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | LLM candidate selector raw layer is Purist-correct while deterministic safety-floor final label is Purist-wrong. |
| 14076 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | LLM candidate selector raw layer is Purist-correct while deterministic safety-floor final label is Purist-wrong. |
| 15193 | `multiple per 13 month` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | seizure_free_duration;current_vs_historical;competing_semiologies;benchmark_format_convention | LLM candidate selector raw layer is Purist-correct while deterministic safety-floor final label is Purist-wrong. |

### Projection Variant Corrections

| Row | Gold | Current final | Graph baseline | Correct variant output | Variant evidence | Families | Why |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 5921 | `1 per 6 to 8 week` | `1 per day` | `1 per day` | `lowest_current_frequency: 1 per 6 to 8 week` | lowest_current_frequency: once every 6–8 weeks | rate_bucket_or_denominator | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 6368 | `unknown` | `1 per 1 to 2 week` | `1 per 1 to 2 week` | `competing_frequency_uncertainty: unknown` | competing_frequency_uncertainty: once every one to two weeks \| Over the past six weeks he describes three witnessed convulsive episodes | unknown_boundary;uncertainty_or_ambiguity | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 6889 | `multiple per week` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `boundary_state_priority: multiple per week` | boundary_state_priority: brief morning myoclonic jerks several times per week | rate_bucket_or_denominator;benchmark_format_convention | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 10386 | `1 cluster per week, 2 to 3 per cluster` | `1 per day` | `1 per day` | `lowest_current_frequency: 1 cluster per week, 2 to 3 per cluster` | lowest_current_frequency: weekly, 2 - 3 per cluster | cluster_burden;rate_bucket_or_denominator;current_vs_historical | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 11216 | `unknown` | `seizure free for 4 month` | `seizure free for 4 month` | `boundary_state_priority: unknown; competing_frequency_uncertainty: unknown` | boundary_state_priority: Last seizure; competing_frequency_uncertainty: Last seizure on 25 December 2023 \| no absences noted by colleagues or family. Sleep has been more regular since \| No subsequent events reported \| seizure freedom since | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 11254 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `boundary_state_priority: unknown` | boundary_state_priority: Last seizure | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 11259 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `boundary_state_priority: unknown` | boundary_state_priority: Last seizure | unknown_boundary;seizure_free_duration;current_vs_historical;uncertainty_or_ambiguity | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 11272 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `boundary_state_priority: unknown` | boundary_state_priority: last seizure | unknown_boundary;seizure_free_duration;current_vs_historical;competing_semiologies;uncertainty_or_ambiguity | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 13209 | `1 per 8 month` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `lowest_current_frequency: 1 per 8 month` | lowest_current_frequency: seizure-free for 8 months, until a focal impaired-awareness seizure occurred 2 Thursdays ago | seizure_free_duration;competing_semiologies | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |
| 15986 | `11 per 3 month` | `1 per 5 to 7 day` | `1 per 5 to 7 day` | `lowest_current_frequency: 11 per 3 month` | lowest_current_frequency: In Mar she had five seizures during sleep and 5 while awake. In May she had no in sleep and one while awake | unclassified | Saved state graph contains a gold-compatible node; a named non-oracle projection variant selects it. |

## Interpretation

Saved sidecars show 6 LLM-candidate rescues on the candidate-generation rescue slice, while graph projection replay supplies 9 non-oracle projection corrections on the projection-arbitration slice. Treat this as a revise/design signal, not a promotion: the next change should target the sidecar mechanism with an explicit safety-floor gate and regression accounting.

The candidate-generation sidecar signal is useful diagnostically where the saved LLM candidate selector is scorable and correct, but it is not promoted into the final label here. Projection rows are replayed only when the saved artifact contains state-graph nodes; Decision 0007 final-projection misses remain counted as projection-family rows but are not graph-arbitration replays.

## Interpretation Required After Generation

The tables above are generated mechanically from saved artifacts. A human reviewer must add post-hoc interpretation before any candidate change is predeclared or implemented: verify whether each proposed changed row reflects a portable clinical mechanism, a Gan-specific convention, scorer-category equivalence rather than exact label equivalence, or an artifact of saved sidecar/projection diagnostics. Do not promote any row-level change from this report alone.
