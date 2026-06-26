# Gan 2026 Change-Only Verifier LLM-Selector Exact Calibration

Validation-development calibration panel for LLM-selector exact alternatives. Panel positives and controls use validation gold only for development accounting and do not authorize locked-test use.

## Decision

Promote to full validation-family audit; calibration is clean and useful.

## Artifacts

- Panel JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_panel_2026-06-05.jsonl`
- Row JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_reparse_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_reparse_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 88 |
| recoverable positive rows | 13 |
| regression control rows | 75 |
| call ok rows | 88 |
| model call rows | 0 |
| raw output reused rows | 88 |
| parse ok rows | 88 |
| parse error rows | 0 |
| all evidence quotes exact rows | 84 |
| base correct rows | 75 |
| projected correct rows | 82 |
| base purist proxy | 0.8523 |
| projected purist proxy | 0.9318 |
| changed label precision | 1.0000 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 75 |
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
