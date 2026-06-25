# ExECTv2 Calibration Validation Audit

Date: 2026-06-25

Status: aggregate-only calibration validation and stop-rule readout.

## Preflight

- Surface: rich-schema holistic assembly reliability scorecard
- Scorer: `headline_target family-cell correctness`
- Split: `full-200 aggregate-only validation requested`
- Code hash: `207bcaf+dirty`
- Row-inspection boundary: Aggregate calibration metrics and artifact inventory only; no row identifiers, note text, gold labels, predictions, evidence spans, rationales, or selected failure examples are emitted.

## Frozen Calibration Candidate

- Model type: `grouped_logistic_scoring_rule`
- Training surface: dev140 rich-schema holistic assembly reliability scorecard
- Development cells: 1706
- Dev cross-validated ECE: 0.0277
- Dev cross-validated Brier: 0.1774
- Protocol ECE baseline for promotion: 0.1456
- Feature set: `family:Diagnosis, family:SeizureFrequency, family:Prescription, family:Investigations, evidence_invalid, low_confidence, source_final_delta, active_rate, plan_language, result_state, deterministic_action_count, prediction_count`

## Validation Artifact Inventory

| Artifact | Rows | Surface | Eligibility | Reason |
| --- | ---: | --- | --- | --- |
| `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl` | 200 | current-code v08-shape rich-schema holistic assembly | eligible | Accepted for aggregate-only validation of the frozen dev140 grouped calibration scoring rule on the current-code v08-shaped rich-schema holistic assembly surface. |

## Aggregate Validation Readout

- Artifact: `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl`
- Rows: 200
- Eligible family cells: 619
- Overall accuracy: 0.6478
- Mean calibrated confidence: 0.6802
- ECE: 0.0432
- Brier: 0.2245
- Constant base-rate Brier: 0.2387
- Brier improvement vs constant base rate: 0.0142
- Maximum adjacent-bin reversal: 0.0000

### Reliability Bins

| Bin | Cells | Confidence range | Mean confidence | Accuracy | Gap | ECE contribution | Mean cell F1 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| q1 | 123 | 0.5179-0.6102 | 0.5967 | 0.5285 | -0.0682 | 0.0136 | 0.8381 |
| q2 | 124 | 0.6102-0.6614 | 0.6330 | 0.5726 | -0.0605 | 0.0121 | 0.7725 |
| q3 | 124 | 0.6685-0.7221 | 0.6893 | 0.6290 | -0.0603 | 0.0121 | 0.7890 |
| q4 | 124 | 0.7221-0.7452 | 0.7274 | 0.7419 | 0.0145 | 0.0029 | 0.8651 |
| q5 | 124 | 0.7452-0.8197 | 0.7536 | 0.7661 | 0.0125 | 0.0025 | 0.8185 |

### Per-Family Calibration

| Family | Cells | Accuracy | Mean confidence | ECE | Brier | Constant Brier | Bins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 189 | 0.5608 | 0.6044 | 0.1424 | 0.2463 | 0.2822 | 4 |
| SeizureFrequency | 153 | 0.5425 | 0.6716 | 0.1292 | 0.2669 | 0.2914 | 4 |
| Prescription | 167 | 0.7365 | 0.7453 | 0.1214 | 0.2009 | 0.1942 | 4 |
| Investigations | 110 | 0.8091 | 0.7234 | 0.0925 | 0.1636 | 0.1579 | 4 |

## Stop-Rule Outcome

- Status: `completed_current_code_surface_validation`
- Validation run executed: `True`
- Promotion decision: `promoted`
- Reason: The frozen dev140 calibration scoring rule passes all predeclared aggregate validation gates on the accepted current-code v08-shaped full-200 artifact.

## Promotion Gates

| Gate | Outcome | Note |
| --- | --- | --- |
| ECE improves over protocol dev-only proxy baseline | pass | Validation ECE 0.0432; baseline 0.1456. |
| Brier improves over constant base-rate comparator | pass | Validation Brier 0.2245; constant base-rate 0.2387. |
| At least four populated reliability bins | pass | Populated bins: 5. |
| No adjacent-bin reversal larger than 0.10 | pass | Maximum adjacent-bin reversal is 0.0000. |
| Per-family ECE reported for all four families | pass | Families reported: Diagnosis, Investigations, Prescription, SeizureFrequency. |

## Result

The frozen dev140 calibration scoring rule is promoted as aggregate full-200 validation evidence. The claim is limited to improved calibration evidence on this surface: ECE 0.0432, Brier 0.2245, five populated bins, and per-family ECE reported for every scored family.

Next action: Upgrade scorecard calibration coverage above dev-only status while keeping the claim limited to aggregate full-200 validation, not deployment-ready probability or holdout calibration.
