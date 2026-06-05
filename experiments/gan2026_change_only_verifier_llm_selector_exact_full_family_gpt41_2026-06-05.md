# Gan 2026 Change-Only Verifier LLM-Selector Exact Calibration

Validation-development calibration panel for LLM-selector exact alternatives. Panel positives and controls use validation gold only for development accounting and do not authorize locked-test use.

## Decision

Reject or revise; calibration does not show high-precision switching.

## Artifacts

- Panel JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_panel_2026-06-05.jsonl`
- Row JSONL: `experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 281 |
| recoverable positive rows | 0 |
| regression control rows | 0 |
| call ok rows | 277 |
| model call rows | 179 |
| raw output reused rows | 102 |
| parse ok rows | 281 |
| parse error rows | 0 |
| all evidence quotes exact rows | 266 |
| base correct rows | 260 |
| projected correct rows | 260 |
| base purist proxy | 0.9253 |
| projected purist proxy | 0.9253 |
| changed label precision | 0.5000 |
| whole validation base correct rows | 697 |
| whole validation projected correct rows | 697 |
| whole validation base purist proxy | 0.9293 |
| whole validation projected purist proxy | 0.9293 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 253 |
| `C_to_W` | 7 |
| `W_to_C` | 7 |
| `W_to_W` | 14 |

## Changed Validation Rows

| Row | Role | Kind | Transition | Current | Proposed |
| ---: | --- | --- | --- | --- | --- |
| 4690 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 6244 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 6321 | `full_family` | `frequency_rate` | `W_to_C` | `1 per day` | `unknown` |
| 6987 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 10237 | `full_family` | `unknown_frequency` | `C_to_W` | `4 cluster per month, multiple per cluster` | `unknown` |
| 10266 | `full_family` | `unknown_frequency` | `W_to_C` | `1 per 5 day` | `unknown` |
| 10618 | `full_family` | `unknown_frequency` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 12827 | `full_family` | `frequency_rate` | `C_to_W` | `5 per 5 month` | `5 per year` |
| 13711 | `full_family` | `frequency_rate` | `C_to_W` | `76 per 12 month` | `unknown` |
| 13732 | `full_family` | `unknown_frequency` | `C_to_W` | `52 per 8 month` | `unknown` |
| 14250 | `full_family` | `frequency_rate` | `C_to_W` | `2 per month` | `2 seizures in last week then seizure free` |
| 14284 | `full_family` | `unknown_frequency` | `C_to_W` | `2 to 3 per month` | `unknown` |
| 15193 | `full_family` | `frequency_rate` | `W_to_C` | `seizure free for multiple year` | `unknown` |
| 15964 | `full_family` | `frequency_rate` | `C_to_W` | `11 per 3 month` | `3-6 per month` |
