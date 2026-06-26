# Gan 2026 Test450 Nonprediction Selector Aggregate Audit

Frozen aggregate-only locked-test audit of validation-selected selector policies. No test row-level failures were inspected and no scorer/gold/split policy was changed.

## Summary

Base full-row Purist proxy: 0.7600 (342 / 450).
Router actions: {'abstain': 1, 'predict': 449}

| Selector | Selected | W->C | C->W | Projected proxy | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `deterministic_window_parseable_v0` | 70 | 5 | 45 | 0.6711 | `reject` |
| `deterministic_non_seizure_free_parseable_v0` | 93 | 11 | 57 | 0.6578 | `reject` |
| `llm_unknown_current_v0` | 62 | 3 | 28 | 0.7044 | `reject` |
| `llm_unknown_any_v0` | 107 | 5 | 50 | 0.6600 | `reject` |
| `nonprediction_llm_unknown_current_v0` | 0 | 0 | 0 | 0.7600 | `reject` |
| `nonprediction_llm_unknown_any_v0` | 0 | 0 | 0 | 0.7600 | `reject` |

## Interpretation

The validation-positive nonprediction selector has too little holdout surface because the frozen router predicts on nearly every test row. It cannot move the test result toward 0.9.
