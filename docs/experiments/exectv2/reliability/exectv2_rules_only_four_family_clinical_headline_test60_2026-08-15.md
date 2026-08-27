# ExECTv2 rules-only four-family clinical_headline (test60)

Date: 2026-08-15
Status: complete; 2026-08-15 Investigations result-binding remasure
Row policy: aggregate_only

Protocol: [primary method-comparison surface protocol](exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)

Decision: [0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)

Machine artifact: [JSON](../../../experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260815.json)

Supersedes the 2026-08-01 fill for this split. Historical file kept.

## Result

| Overall clinical_headline F1 | 0.7918 |
| Precision | 0.8385 |
| Recall | 0.7500 |
| Letters scored | 59 |

| Family | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.8550 | 0.8839 | 0.8279 |
| SeizureFrequency | 0.5797 | 0.6250 | 0.5405 |
| Prescription | 0.8395 | 0.8831 | 0.8000 |
| Investigations | 0.8706 | 0.9737 | 0.7872 |

## Claim boundary

Aggregate-only rules-only four-family clinical_headline on ExECT test60 after the 2026-08-15 Investigations result-binding rewrite. Sol-matched assembly headline_target. No letter identifiers, notes, predictions, or failure cases are included in this public artifact. Not the published ExECT benchmark or clinical validation.
