# Gan 2026 H9 Action-Policy Gap v0

H9 no-call validation plus aggregate-only locked-test readout. Validation action rows may be inspected, but locked-test output is limited to predeclared aggregate action/family summaries and writes no test row ids, note text, raw model outputs, or row-level failures.

## Decision

h9_partially_supported_action_policy_shift_not_primary_gap_explanation

## Interpretation

Validation action policy is not neutral: nonprediction/review rows are safety-floor-owned and frequently block deterministic-correct labels. The locked-test aggregate selector surface has much lower nonprediction burden, while the test accuracy gap remains large, so H9 is supported as an action-policy shift but not as the primary explanation for the validation-test generalisation gap.

## Overall Action Pressure

| Split | Rows | Nonprediction rows | Nonprediction rate | Abstain | Review | Blocked baseline-correct | Blocked baseline-wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| validation750 | 750 | 34 | 0.0453 | 26 | 8 | 19 | 15 |
| locked_test450 | 450 | 1 | 0.0022 | 1 | 0 |  |  |

## Validation By Action Reason

| Reason | Rows | Abstain | Review | Rate | Blocked C | Blocked W |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `last_event_boundary` | 750 | 0 | 8 | 0.0107 | 2 | 6 |
| `missing_denominator_anchor` | 750 | 2 | 0 | 0.0027 | 2 | 0 |
| `trigger_conditioned_frequency` | 750 | 24 | 0 | 0.0320 | 15 | 9 |

## Validation By Hidden Family

| Family | Rows | Nonprediction rows | Nonprediction rate | Blocked C | Blocked W |
| --- | ---: | ---: | ---: | ---: | ---: |
| `benchmark_format_convention` | 10 | 0 | 0.0000 | 0 | 0 |
| `cluster_burden` | 11 | 0 | 0.0000 | 0 | 0 |
| `competing_semiologies` | 26 | 7 | 0.2692 | 0 | 7 |
| `current_vs_historical` | 25 | 8 | 0.3200 | 0 | 8 |
| `diary_or_log_aggregation` | 4 | 0 | 0.0000 | 0 | 0 |
| `rate_bucket_or_denominator` | 20 | 2 | 0.1000 | 0 | 2 |
| `seizure_free_duration` | 27 | 10 | 0.3704 | 0 | 10 |
| `uncertainty_or_ambiguity` | 24 | 11 | 0.4583 | 0 | 11 |
| `unclassified` | 697 | 20 | 0.0287 | 19 | 1 |
| `unknown_boundary` | 20 | 11 | 0.5500 | 0 | 11 |

## Test Aggregate Family Context

| Family | Test rows | Test proxy | Test changed rate | Validation-test proxy gap |
| --- | ---: | ---: | ---: | ---: |
| `unknown_boundary` | 57 | 0.7368 | 0.1053 | 0.1368 |
| `benchmark_format_convention` | 48 | 0.6667 | 0.0833 | 0.2369 |
| `seizure_free_duration` | 121 | 0.6529 | 0.0413 | 0.2431 |
| `uncertainty_or_ambiguity` | 178 | 0.7247 | 0.0393 | 0.2008 |
| `cluster_burden` | 264 | 0.7765 | 0.0379 | 0.1568 |
| `rate_bucket_or_denominator` | 347 | 0.7752 | 0.0317 | 0.1643 |
| `current_vs_historical` | 444 | 0.7770 | 0.0315 | 0.1661 |
| `competing_semiologies` | 386 | 0.7720 | 0.0259 | 0.1686 |
| `diary_or_log_aggregation` | 436 | 0.7775 | 0.0252 | 0.1702 |
| `unclassified` | 1 | 1.0000 | 0.0000 | 0.0000 |

## Inspection Boundary

Locked-test family rows above are aggregate-only and come from predeclared H1/frozen selector summaries. This artifact does not resolve test row-level owner/failure mechanisms.
