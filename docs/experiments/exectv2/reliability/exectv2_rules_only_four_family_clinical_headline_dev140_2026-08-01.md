# ExECTv2 rules-only four-family clinical_headline (dev140)

Date: 2026-08-01
Status: complete; Phase B of the 0046 evidence protocol
Row policy: development (`dev140`)

Protocol: [primary method-comparison surface protocol](exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)

Decision: [0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)

Machine artifact: [JSON](../../../experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json)

## Question

What is rules-only four-family `clinical_headline` F1 on `dev140` under the Sol-matched assembly `headline_target` surface?

## Result

| Overall clinical_headline F1 | 0.8160 |
| Precision | 0.7944 |
| Recall | 0.8389 |

| Family | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.8599 | 0.8715 | 0.8485 |
| SeizureFrequency | 0.8323 | 0.8373 | 0.8274 |
| Prescription | 0.9615 | 0.9524 | 0.9709 |
| Investigations | 0.5325 | 0.4599 | 0.6324 |

## Method

- Pipeline: deterministic all-nine (`run_all9_on_letters`, diagnosis resolution candidate and benchmark residuals off).
- Production rule: restrict-and-rescore to Diagnosis, Seizure Frequency, Prescription, and Investigations.
- Scorer: assembly `headline_target` via `build_scoring_views` (same surface as Sol hybrid cells).
- Mentions: 1186 all-nine → 929 four-family (257 non-key excluded from this peer score only).

## Claim boundary

Development rules-only four-family clinical_headline on ExECT dev140 for decision 0046. Sol-matched assembly headline_target on all-nine deterministic predictions with non-key entities excluded from the peer score only. Not nine-entity published metrics, not clinical_recovery_scorecard overall, not holdout evidence, and not clinical validation.

## Next action

Phase C of the same protocol: aggregate-only rules-only four-family `clinical_headline` on `test60`.
