# ExECTv2 rules-only four-family clinical_headline (dev140)

Date: 2026-08-15
Status: complete; 2026-08-15 Investigations result-binding remasure
Row policy: dev140_rows_permitted_test60_forbidden

Protocol: [primary method-comparison surface protocol](exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)

Decision: [0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)

Machine artifact: [JSON](../../../experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260815.json)

Supersedes the 2026-08-01 fill for this split. Historical file kept.

## Result

| Overall clinical_headline F1 | 0.8982 |
| Precision | 0.9061 |
| Recall | 0.8904 |
| Letters scored | 140 |

| Family | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.8633 | 0.8737 | 0.8532 |
| SeizureFrequency | 0.8333 | 0.8333 | 0.8333 |
| Prescription | 0.9615 | 0.9524 | 0.9709 |
| Investigations | 0.9579 | 1.0000 | 0.9191 |

## Claim boundary

Development rules-only four-family clinical_headline on ExECT dev140 after the 2026-08-15 Investigations result-binding rewrite. Sol-matched assembly headline_target. Not nine-entity published metrics, not holdout evidence, and not clinical validation.
