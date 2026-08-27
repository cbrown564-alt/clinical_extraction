# ExECTv2 model-reported confidence out-of-sample result

Date: 2026-07-15

Status: completed aggregate-only negative-result study

## Answer

The saved model-reported confidence labels did not satisfy the frozen test60
informativeness rule for any of the three historical models. No confidence-based
review policy is adopted.

## Aggregate test60 result

| Model | Usable coverage | Failure AUROC | Low/medium burden | Low/medium catch | Missing-inclusive burden | Missing-inclusive catch | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| DeepSeek chat | 0.8292 | 0.5503 | 0.0792 | 0.1507 | 0.2500 | 0.2192 | negative_result_do_not_adopt_confidence_review_policy |
| GPT-4.1-mini | 0.8250 | 0.5394 | 0.1583 | 0.2289 | 0.3333 | 0.2771 | negative_result_do_not_adopt_confidence_review_policy |
| Qwen 3.6 35B repair v02 | 0.8417 | 0.4895 | 0.0625 | 0.0617 | 0.2208 | 0.0617 | negative_result_do_not_adopt_confidence_review_policy |

The unit is one letter-family cell across Diagnosis, Seizure Frequency,
Prescription, and Investigations. Confidence is the least-confident usable
label among the model's source mentions. Missing labels remain a separate
category. The primary outcome is exact final `clinical_headline` cell
correctness after the fixed decision-0040 pipeline.

## Family behavior

| Model | Family | Coverage | AUROC | Errors |
| --- | --- | ---: | ---: | ---: |
| DeepSeek chat | Diagnosis | 1.0000 | 0.5933 | 22 |
| DeepSeek chat | SeizureFrequency | 0.9000 | 0.509 | 31 |
| DeepSeek chat | Prescription | 0.9333 | 0.5 | 13 |
| DeepSeek chat | Investigations | 0.4833 | 0.5 | 7 |
| GPT-4.1-mini | Diagnosis | 1.0000 | 0.5139 | 24 |
| GPT-4.1-mini | SeizureFrequency | 0.8333 | 0.4928 | 30 |
| GPT-4.1-mini | Prescription | 0.9500 | 0.5971 | 17 |
| GPT-4.1-mini | Investigations | 0.5167 | 0.5 | 12 |
| Qwen 3.6 35B repair v02 | Diagnosis | 1.0000 | 0.4857 | 25 |
| Qwen 3.6 35B repair v02 | SeizureFrequency | 0.9167 | 0.4565 | 32 |
| Qwen 3.6 35B repair v02 | Prescription | 0.9333 | 0.5 | 11 |
| Qwen 3.6 35B repair v02 | Investigations | 0.5167 | 0.5 | 13 |

## Interpretation and boundary

This is a no-call replay of saved historical outputs. Dev140 and test60 are
reported separately, and no test60 row identifier, text, prediction, or failure
was emitted. The result concerns these saved outputs only. The historical
DeepSeek runtime metadata is incomplete. This is not deployment calibration,
independent clinical validation, a six-model conclusion, or evidence for the
final DeepSeek V4 Flash runtime.

Protocol: `docs/experiments/exectv2/reliability/exectv2_model_reported_confidence_protocol_2026-07-15.md`

Machine-readable result:
`experiments/exectv2_model_reported_confidence_out_of_sample_20260715.json`
