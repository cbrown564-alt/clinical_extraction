# Gan 2026 Change-Only Verifier LLM-Selector Exact Calibration

Validation-development calibration panel for LLM-selector exact alternatives. Panel positives and controls use validation gold only for development accounting and do not authorize locked-test use.

## Decision

Diagnostic positive but not promotable; inspect validation C->W regressions.

## Artifacts

- Panel JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_panel_2026-06-05.jsonl`
- Row JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_reparse_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_reparse_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 281 |
| recoverable positive rows | 0 |
| regression control rows | 0 |
| call ok rows | 281 |
| model call rows | 4 |
| raw output reused rows | 277 |
| parse ok rows | 281 |
| parse error rows | 0 |
| all evidence quotes exact rows | 269 |
| base correct rows | 260 |
| projected correct rows | 266 |
| base purist proxy | 0.9253 |
| projected purist proxy | 0.9466 |
| changed label precision | 0.8750 |
| whole validation base correct rows | 697 |
| whole validation projected correct rows | 703 |
| whole validation base purist proxy | 0.9293 |
| whole validation projected purist proxy | 0.9373 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 259 |
| `C_to_W` | 1 |
| `W_to_C` | 7 |
| `W_to_W` | 14 |

## Changed Validation Rows

| Row | Role | Kind | Transition | Current | Proposed |
| ---: | --- | --- | --- | --- | --- |
| 4690 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 6244 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 6321 | `full_family` | `frequency_rate` | `W_to_C` | `1 per day` | `unknown` |
| 6987 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 10266 | `full_family` | `unknown_frequency` | `W_to_C` | `1 per 5 day` | `unknown` |
| 10618 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 14250 | `full_family` | `frequency_rate` | `C_to_W` | `2 per month` | `2 seizures in last week then seizure free` |
| 15193 | `full_family` | `frequency_rate` | `W_to_C` | `seizure free for multiple year` | `unknown` |
