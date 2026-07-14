# 07 — ExECT retained evidence

Last updated: 2026-07-14

ExECT broad phenotyping covers Diagnosis, SeizureFrequency, Prescription, and
Investigations in the primary `clinical_headline` comparison.

## Retained architecture comparison

| Family | Split | Result | Role |
| --- | --- | ---: | --- |
| Deterministic all nine | dev140 | strict item F1 0.3548 | Rules reference |
| GEPA LLM-only | dev140 | headline F1 0.7393 | Negative comparator |
| Holistic assembly v08 | dev140 | headline F1 0.9189 | Current performance control |

The [manifest](../experiments/retained_evidence_manifest.md) owns exact paths,
hashes, source closures, and replay expectations.

## Same-core model evidence

| Model | Full200 headline | Boundary |
| --- | ---: | --- |
| GPT-4.1-mini | 0.8356 | Development-inclusive aggregate |
| DeepSeek chat | 0.8566 | Development-inclusive aggregate |
| Qwen 3.6:35b repair v02 | 0.8197 | Diagnostic aggregate |

This is a three-model result, not the requested six-model comparison. Full200
contains dev140 and held-out test60; it is not an independent holdout estimate.

## Calibration

The retained 2026-07-07 internal scoring-rule result reports full200 aggregate
Brier 0.2225 against base rate 0.2340 and ECE 0.0587. It does not validate
model-reported confidence or a low-burden review policy.

## Remaining work

- reproduce the paper-comparable phrase/CUI/full-attribute surface;
- test model-reported confidence out of sample;
- run the frozen six-model comparison;
- complete the annotation taxonomy and sensitivity analysis.

