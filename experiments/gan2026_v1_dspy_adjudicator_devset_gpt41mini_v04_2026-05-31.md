# Gan 2026 DSPy Final-Selection Adjudicator Dev-Set Run

Date: 2026-05-31

This is a validation-only prompt/adjudicator development run over the 16-example dev set mined from validation ablations. It is not a benchmark result and does not inspect locked test-row failures.

## Experiment Unit

Hypothesis: a DSPy final-selection adjudicator can use deterministic V1 candidate diagnostics to reject unsupported high-priority candidates while preserving necessary deterministic evidence.

Minimal change: add the adjudicator program and run harness only. Deterministic candidate extraction, normalization, scoring, split policy, and repair rules are unchanged.

Data surface: `validation` split, `gan2026_split_v1`, 16 examples from `experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl`.
Scorer policy: compare final labels to carried gold labels with Gan-compatible Purist categories first, Pragmatic categories as a side-car.

## Model And Prompt Metadata

- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: final-selection adjudicator
- Prompt/program version: `gan2026_final_selection_adjudicator_v0.4`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- Optimizer: none
- Deterministic rule configuration: frozen V1 diagnostics from the dev-set JSONL
- Git commit: `1c55aa5`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_v04_2026-05-31.jsonl`

## Summary

- Decision records: 16 / 16
- Call failures: 0
- Parse/schema/label issues: 0
- Purist dev-set accuracy: 0.5625 (9 / 16)
- Pragmatic dev-set accuracy: 0.7500 (12 / 16)

## Rows

| Row | Lesson | Condition | Final | Gold | Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 6209 | deterministic_overreach | disable_portable_rate_expressions | 1 per day | multiple per day | no |  |
| 5921 | deterministic_overreach | disable_portable_rate_expressions | 1 per 6 to 8 week | 1 per 6 to 8 week | yes |  |
| 10386 | deterministic_overreach | disable_portable_rate_expressions | 1 per day | 1 cluster per week, 2 to 3 per cluster | no |  |
| 3356 | deterministic_overreach | disable_seizure_free_no_event_assertions | seizure free for multiple year | unknown | no |  |
| 6131 | deterministic_overreach | disable_seizure_free_no_event_assertions | seizure free for 6 month | unknown | no |  |
| 6889 | deterministic_overreach | disable_temporal_selection | 1 per 2 to 3 week | multiple per week | no |  |
| 13209 | deterministic_overreach | disable_temporal_selection | 1 per 4 to 5 week | 1 per 8 month | no |  |
| 15986 | deterministic_overreach | disable_temporal_selection | 1 per 5 to 7 day | 11 per 3 month | no |  |
| 5921 | deterministic_overreach | disable_temporal_selection | 1 per 6 to 8 week | 1 per 6 to 8 week | yes |  |
| 10386 | deterministic_overreach | disable_temporal_selection | 1 cluster per week, 2 to 3 per cluster | 1 cluster per week, 2 to 3 per cluster | yes |  |
| 15242 | deterministic_support_control | disable_cluster_arithmetic | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster | yes |  |
| 10807 | deterministic_support_control | disable_cluster_arithmetic | 2 cluster per month, multiple per cluster | 2 cluster per month, multiple per cluster | yes |  |
| 10517 | deterministic_support_control | disable_cluster_arithmetic | 3 to 4 cluster per week, multiple per cluster | 3 to 4 cluster per week, multiple per cluster | yes |  |
| 15497 | deterministic_support_control | disable_cluster_arithmetic | 1 cluster per 4 to 5 day, 5 per cluster | 1 cluster per 4 to 5 day, 5 per cluster | yes |  |
| 7401 | deterministic_support_control | disable_cluster_arithmetic | 2 cluster per 6 week, 1 to 2 per cluster | 2 cluster per 6 week, 1 to 2 per cluster | yes |  |
| 4337 | deterministic_support_control | disable_diary_log_aggregation | 3 per 3 month | 3 per 3 month | yes |  |

## Interpretation

The dev-set behavior is interpretable enough to inspect row-level successes and failures before deciding whether to revise the prompt or run a broader validation pass.
