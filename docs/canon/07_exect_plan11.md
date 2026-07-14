# 07 — ExECT results

Last updated: 2026-07-14

The main ExECT comparison covers diagnosis, seizure frequency, prescriptions,
and investigations.

| Method | Split | Result | Role |
| --- | --- | ---: | --- |
| Rules only, all nine entities | dev140 | strict item F1 0.3548 | Rules baseline |
| Rules only, all nine entities | dev140 | all-features macro item F1 0.6020 | Paper-derived metric development result |
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

## Published metric development replay

The no-call rules-only replay over all nine dev140 entity types produced macro
per-item F1 of 0.5687 for normalized phrase, 0.7144 for CUI, and 0.6020 for all
features. Macro per-letter F1 was 0.7518, 0.8534, and 0.7922 respectively. The
scorer follows the paper's entity-specific attribute policy: certainty for
Diagnosis and PatientHistory, and negation only for PatientHistory. The result verifies the
metric implementation on permitted development data; it does not reproduce the
paper's original system, annotation process, or 0.87/0.90 scores.

## Diagnosis review and development candidates

The completed 246-row dev140 Diagnosis review found 173
representation/evaluation issues, 72 extraction errors, and one uncertain row.
Keeping gold and the fixed scorer unchanged, the conservative sensitivity view
raises fixed Diagnosis F1 to 0.9344 for rules only, 0.8499 for LLM only, and
0.9789 for LLM with rules. Shared deterministic boundary fixes improve the
fixed rules-only score from 0.8599 to 0.8926, while the hybrid candidate moves
from 0.8984 to 0.9034. A fixed LLM-only prompt candidate regresses from 0.6861
to 0.6210 and is rejected. These are inspected dev140 development results; none
is promoted and test60 was not inspected. See the
[component comparison](../experiments/exectv2/diagnosis/exectv2_diagnosis_component_comparison_2026-07-14.md).

Remaining work: out-of-sample model-reported confidence and the strict
six-model comparison. Independent clinical review is still required for
clinical-validity claims about the Diagnosis interpretation decisions.
