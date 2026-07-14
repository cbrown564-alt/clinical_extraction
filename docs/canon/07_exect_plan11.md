# 07 — ExECT results

Last updated: 2026-07-14

The main ExECT comparison covers diagnosis, seizure frequency, prescriptions,
and investigations.

| Method | Split | Result | Role |
| --- | --- | ---: | --- |
| Rules only, all nine entities | dev140 | strict item F1 0.3548 | Rules baseline |
| GEPA LLM only | dev140 | clinical fact F1 0.7393 | Negative comparison |
| LLM with rules (`v08`) | dev140 | clinical fact F1 0.9189 | Current development reference |

## Three-model results using the same main pipeline

| Model | Full200 clinical fact F1 | Limit |
| --- | ---: | --- |
| GPT-4.1-mini | 0.8356 | Development-inclusive aggregate |
| DeepSeek chat | 0.8566 | Development-inclusive aggregate |
| Qwen 3.6:35b, repair v02 | 0.8197 | Diagnostic aggregate |

This is not the planned six-model comparison. Full200 contains dev140 and
held-out test60, so it is not an independent holdout.

The selected internal calibration result reports full200 Brier 0.2225, base-rate
Brier 0.2340, and ECE 0.0587. It does not validate model-reported confidence or
a low-burden review policy.

Remaining work: published-metric reproduction, out-of-sample confidence,
the strict six-model comparison, and annotation sensitivity analysis.
