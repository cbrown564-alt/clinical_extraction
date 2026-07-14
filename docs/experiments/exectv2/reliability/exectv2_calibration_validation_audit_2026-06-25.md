# ExECTv2 Calibration Validation Audit

Date: 2026-07-07

Status: aggregate-only calibration validation and stop-rule readout.

## Preflight

- Evaluation set: rich-schema holistic assembly reliability scorecard
- Scorer: `headline_target family-cell correctness`
- Split: `full-200 aggregate-only validation requested`
- Code hash: `76d26fae+dirty`
- Row-inspection boundary: Aggregate calibration metrics and artifact inventory only; no row identifiers, note text, gold labels, predictions, evidence spans, rationales, or selected failure examples are emitted.

## Frozen Calibration Candidate

- Model type: `grouped_logistic_scoring_rule`
- Training set: dev140 rich-schema holistic assembly reliability scorecard
- Development cells: 1719
- Dev cross-validated ECE: 0.0229
- Dev cross-validated Brier: 0.1761
- Protocol ECE baseline for promotion: 0.1456
- Feature set: `family:Diagnosis, family:SeizureFrequency, family:Prescription, family:Investigations, evidence_invalid, low_confidence, source_final_delta, active_rate, plan_language, result_state, deterministic_action_count, prediction_count`

## Validation Artifact Inventory

| Artifact | Rows | Evaluation set | Eligibility | Reason |
| --- | ---: | --- | --- | --- |
| `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl` | 200 | current-code v08-shape rich-schema holistic assembly | eligible | Accepted for aggregate-only validation of the fixed dev140 grouped calibration scoring rule on the current-code v08-shaped rich-schema holistic assembly evaluation set. |

## Aggregate Validation Readout

- Artifact: `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl`
- Rows: 200
- Eligible family cells: 622
- Overall accuracy: 0.6576
- Mean calibrated confidence: 0.6878
- ECE: 0.0587
- Brier: 0.2225
- Constant base-rate Brier: 0.2340
- Brier improvement vs constant base rate: 0.0115
- Maximum adjacent-bin reversal: 0.0784

### Reliability Bins

| Bin | Cells | Confidence range | Mean confidence | Accuracy | Gap | ECE contribution | Mean cell F1 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| q1 | 124 | 0.5918-0.6165 | 0.6112 | 0.5403 | -0.0708 | 0.0141 | 0.8401 |
| q2 | 124 | 0.6165-0.6923 | 0.6470 | 0.5565 | -0.0905 | 0.0180 | 0.7707 |
| q3 | 125 | 0.6923-0.7145 | 0.7035 | 0.6720 | -0.0315 | 0.0063 | 0.8326 |
| q4 | 124 | 0.7145-0.7412 | 0.7269 | 0.7984 | 0.0715 | 0.0143 | 0.9065 |
| q5 | 125 | 0.7412-0.8026 | 0.7499 | 0.7200 | -0.0299 | 0.0060 | 0.7933 |

### Per-Family Calibration

| Family | Cells | Accuracy | Mean confidence | ECE | Brier | Constant Brier | Bins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 189 | 0.5608 | 0.6183 | 0.1527 | 0.2501 | 0.2827 | 4 |
| SeizureFrequency | 153 | 0.5490 | 0.6875 | 0.1384 | 0.2689 | 0.2886 | 4 |
| Prescription | 170 | 0.7647 | 0.7465 | 0.0868 | 0.1875 | 0.1801 | 4 |
| Investigations | 110 | 0.8091 | 0.7171 | 0.0963 | 0.1649 | 0.1578 | 4 |

## Stop-Rule Outcome

- Status: `completed_current_code_surface_validation`
- Validation run executed: `True`
- Promotion decision: `promoted`
- Reason: The frozen dev140 calibration scoring rule passes all predeclared aggregate validation gates on the accepted current-code v08-shaped full-200 artifact.

## Promotion Gates

| Gate | Outcome | Note |
| --- | --- | --- |
| ECE improves over protocol dev-only proxy baseline | pass | Validation ECE 0.0587; baseline 0.1456. |
| Brier improves over constant base-rate comparator | pass | Validation Brier 0.2225; constant base-rate 0.2340. |
| At least four populated reliability bins | pass | Populated bins: 5. |
| No adjacent-bin reversal larger than 0.10 | pass | Maximum adjacent-bin reversal is 0.0784. |
| Per-family ECE reported for all four families | pass | Families reported: Diagnosis, Investigations, Prescription, SeizureFrequency. |

## Result

The fixed dev140 calibration scoring rule is promoted as aggregate full-200 validation evidence. The claim is limited to improved calibration evidence on this evaluation set: ECE 0.0587, Brier 0.2225, five populated bins, and per-family ECE reported for every scored family.

Next action: Upgrade scorecard calibration coverage above dev-only status while keeping the claim limited to aggregate full-200 validation, not deployment-ready probability or holdout calibration.
