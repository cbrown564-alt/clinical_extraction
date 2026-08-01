# ExECTv2 rules-only four-family clinical_headline (test60)

Date: 2026-08-01
Status: complete; Phase C of the 0046 evidence protocol
Row policy: aggregate-only

Protocol: [primary method-comparison surface protocol](exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)

Decision: [0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)

Machine artifact: [JSON](../../../experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json)

## Question

What is rules-only four-family `clinical_headline` F1 on locked `test60` under the Sol-matched assembly `headline_target` surface?

## Result

Aggregate-only. No letter identifiers, notes, predictions, or row failures are reported. Sealed predictions remain under ignored `scratch/holdout/`.

| Overall clinical_headline F1 | 0.7154 |
| Precision | 0.7270 |
| Recall | 0.7043 |
| Letters scored | 59 |

| Family | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.8550 | 0.8839 | 0.8279 |
| SeizureFrequency | 0.5797 | 0.6250 | 0.5405 |
| Prescription | 0.8395 | 0.8831 | 0.8000 |
| Investigations | 0.4037 | 0.3548 | 0.4681 |

## Method

- Pipeline: deterministic all-nine (`run_all9_on_letters`, diagnosis resolution candidate and benchmark residuals off).
- Production rule: restrict-and-rescore to the four key families.
- Scorer: assembly `headline_target` via `build_scoring_views`.
- Mentions (counts only): 424 all-nine → 340 four-family (84 non-key excluded from this peer score only).

## Claim boundary

Aggregate-only rules-only four-family clinical_headline on ExECT test60 for decision 0046. Sol-matched assembly headline_target on all-nine deterministic predictions with non-key entities excluded from the peer score only. No letter identifiers, notes, predictions, or failure cases are included in this public artifact. Not the published ExECT benchmark or clinical validation.

## Next action

Update canon / manuscript method rows to decision 0046 using the completed A→B→C artifacts.
