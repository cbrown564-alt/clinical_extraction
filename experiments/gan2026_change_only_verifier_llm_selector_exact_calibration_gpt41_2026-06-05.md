# Gan 2026 Change-Only Verifier LLM-Selector Exact Calibration

Validation-development calibration panel for LLM-selector exact alternatives. Panel positives and controls use validation gold only for development accounting and do not authorize locked-test use.

## Decision

Reject or revise; calibration does not show high-precision switching.

## Artifacts

- Panel JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_panel_2026-06-05.jsonl`
- Row JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 88 |
| recoverable positive rows | 13 |
| regression control rows | 75 |
| call ok rows | 88 |
| model call rows | 54 |
| raw output reused rows | 34 |
| parse ok rows | 88 |
| parse error rows | 0 |
| all evidence quotes exact rows | 84 |
| base correct rows | 75 |
| projected correct rows | 73 |
| base purist proxy | 0.8523 |
| projected purist proxy | 0.8295 |
| changed label precision | 0.4375 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 66 |
| `C_to_W` | 9 |
| `W_to_C` | 7 |
| `W_to_W` | 6 |

## Changed Validation Rows

| Row | Role | Kind | Transition | Current | Proposed |
| ---: | --- | --- | --- | --- | --- |
| 4690 | `recoverable_positive` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 6244 | `recoverable_positive` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 6321 | `recoverable_positive` | `frequency_rate` | `W_to_C` | `1 per day` | `unknown` |
| 6987 | `recoverable_positive` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 10266 | `recoverable_positive` | `unknown_frequency` | `W_to_C` | `1 per 5 day` | `unknown` |
| 10618 | `recoverable_positive` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 15193 | `recoverable_positive` | `frequency_rate` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 14530 | `regression_control` | `cluster_frequency` | `C_to_W` | `2 per 2 month` | `unknown` |
| 14635 | `regression_control` | `cluster_frequency` | `C_to_W` | `5 per 4 month` | `unknown` |
| 15029 | `regression_control` | `cluster_frequency` | `C_to_W` | `1 per 3 month` | `unknown` |
| 16324 | `regression_control` | `cluster_frequency` | `C_to_W` | `10 per 3 month` | `3-5 per month` |
| 4624 | `regression_control` | `frequency_rate` | `C_to_W` | `1 per 3 to 4 day` | `2 per month` |
| 5763 | `regression_control` | `frequency_rate` | `C_to_W` | `6 per 3 month` | `2 per 3 months` |
| 5767 | `regression_control` | `frequency_rate` | `C_to_W` | `1 per 1 to 2 week` | `1-2 per week` |
| 9449 | `regression_control` | `frequency_rate` | `C_to_W` | `4 per 6 month` | `1-2 per month` |
| 14672 | `regression_control` | `last_event_only` | `C_to_W` | `3 per 8 month` | `unknown` |
