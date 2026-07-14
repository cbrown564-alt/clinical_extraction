# 10 — Paper claims and supporting evidence

Last updated: 2026-07-14

This file states how strongly the paper may make each claim. The
[retained evidence index](../experiments/retained_evidence_manifest.md) records
the exact files and hashes. The [manuscript](../research/paper_manuscript_2026-06-26.md)
must not make a stronger claim than either source supports.

## Required paper statements

| ID | Statement | Current evidence | State |
| --- | --- | --- | --- |
| S1 | One modular package is evaluated on Gan and ExECT | Six selected runs replay from retained code and outputs | Partial |
| S2 | Rules-only, LLM-only, and LLM-with-rules methods have attributable results on both tasks | One selected run per task and method | Partial |
| S3 | The Gan multi-model method adds modest quality at higher cost | Quality is saved; matched cost and latency are missing | Partial |
| S4 | Six exact models run on one fixed ExECT pipeline | GPT-4.1-mini, DeepSeek, and Qwen are selected | 3/6 |
| S5 | Unknown-versus-rate overconfidence appears across models and tasks | Gan evidence exists; no selected ExECT transfer study exists | Open |
| S6 | Extraction, normalization, final formatting, schema, and evidence steps are explicit and tested | Step-specific tests and cross-task replay exist | Partial |
| S7 | ExECT reproduces published phrase, CUI, and full-attribute metrics | Current deterministic strict score remains below the paper | Open |
| S8 | Both tasks have reliability evidence with stated limits | Gan package and ExECT internal calibration are selected | Partial |
| S9 | Annotation flaws and conventions have transparent handling | Four entity ledgers and selected row analyses exist | Partial |

## Current claims

| ID | Claim | Strength | Evidence limit |
| --- | --- | --- | --- |
| C1 | Some ExECT diagnosis and seizure-frequency disagreements concern annotation multiplicity or representation | Limited | Internal dev140 review by the same team |
| C2 | Normalization improves both tasks; the exact-evidence check is score-neutral on selected replays | Strong for the named replays | Development data only |
| C3 | Gan unknown-versus-rate behavior transfers to ExECT | Unsupported | Do not claim |
| C4 | The same main ExECT pipeline runs with GPT-4.1-mini, DeepSeek, and Qwen | Strong but runtime conditions differ | Full200 development-inclusive aggregate |
| C5 | Split and evaluation rules are enforced | Strong for selected paths | Engineering verification, not external validation |

## Selected headline results

| Task and method | Result |
| --- | ---: |
| Gan single-pass system, test450 | 364/450 Purist |
| Gan multi-model comparison, test450 | 379/450 Purist |
| ExECT rules only, dev140 | strict item F1 0.3548 |
| ExECT GEPA LLM only, dev140 | clinical fact F1 0.7393 |
| ExECT LLM with rules, dev140 | clinical fact F1 0.9189 |
| ExECT GPT / DeepSeek / Qwen, full200 | 0.8356 / 0.8566 / 0.8197 clinical fact F1 |

## Wording the paper must avoid

- Do not describe ExECT full200 as an independent holdout.
- Do not describe `clinical_headline` as the published strict benchmark.
- Do not present internal annotation review as independent clinical validation.
- Do not claim cross-task transfer without a selected ExECT study.
- Do not present the GEPA run as a production reference.
- Do not state a six-model conclusion from three models.

## Open work

1. Add a matched Gan quality, calls, tokens, cost, and latency table.
2. Implement the published ExECT phrase, CUI, and full-attribute metrics.
3. Evaluate model-reported confidence out of sample.
4. Combine annotation issues with sensitivity results.
5. Specify the remaining model runtimes, then run all six with the same pipeline.
6. Regenerate manuscript tables and synchronize the IEEE source.
