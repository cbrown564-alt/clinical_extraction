# 10 — Paper claims and supporting evidence

Last updated: 2026-07-15

This file states how strongly the paper may make each claim. The
[retained evidence index](../experiments/retained_evidence_manifest.md) records
the exact files and hashes. The [manuscript](../research/paper_manuscript_2026-06-26.md)
must not make a stronger claim than either source supports.

## Required paper statements

| ID | Statement | Current evidence | State |
| --- | --- | --- | --- |
| S1 | One modular package is evaluated on Gan and ExECT | Six selected runs replay from retained code and outputs | Partial |
| S2 | Rules-only, LLM-only, and LLM-with-rules methods have attributable results on both tasks | One selected run per task and method; ExECT `v08` is a historical hybrid control whose deterministic Prescription producer and SF union do not meet the final decision-0040 contract | Partial |
| S3 | The Gan multi-model method adds modest quality with three model passes rather than one | Saved holdout quality, run metadata, and aggregate input availability | Bounded |
| S4 | Six exact models run on one fixed ExECT pipeline | Roster fixed by decision 0039; GPT-4.1-mini and Qwen have directly named retained evidence; DeepSeek V4 Flash maps to `deepseek/deepseek-chat`, but the retained run does not record whether thinking was enabled | 2/6 confirmed |
| S5 | Unknown-versus-rate overconfidence appears across models and tasks | Gan evidence exists; no selected ExECT transfer study exists | Open |
| S6 | Extraction, normalization, final formatting, schema, and evidence steps are explicit and tested | Step-specific tests and cross-task replay exist | Partial |
| S7 | ExECT reports paper-derived normalized-phrase, CUI, and full-attribute metrics | No-call rules-only dev140 replay covers all nine entities; original 0.87/0.90 scores are not reproduced | Development answer |
| S8 | Both tasks have reliability evidence with stated limits | Gan package and ExECT internal calibration are selected | Partial |
| S9 | Annotation flaws and conventions have transparent handling | Four entity ledgers and selected row analyses exist | Partial |

## Current claims

| ID | Claim | Strength | Evidence limit |
| --- | --- | --- | --- |
| C1 | Some ExECT diagnosis and seizure-frequency disagreements concern annotation multiplicity or representation | Limited | Diagnosis evidence is historical pre-D1 internal review; the current three-method union is not yet adjudicated |
| C2 | Normalization improves both tasks; the exact-evidence check is score-neutral on selected replays | Strong for the named replays | Development data only |
| C3 | Gan unknown-versus-rate behavior transfers to ExECT | Unsupported | Do not claim |
| C4 | The historical ExECT component graph ran with GPT-4.1-mini, DeepSeek, and Qwen | Strong for execution of that graph, not for a consistent model-led comparison | Full200 development-inclusive aggregate; Prescription was deterministic-only and SF included an independent extractor union |
| C5 | Split and evaluation rules are enforced | Strong for selected paths | Engineering verification, not external validation |
| C6 | Gan V12 gains 15/450 Purist-correct rows while requiring a three-pass cold architecture rather than one pass | Strong for saved quality and architecture structure | Tokens, cost, latency, and hardware were not measured in a matched run |
| C7 | The ExECT rules-only system scores 0.5687 phrase, 0.7144 CUI, and 0.6020 all-features macro item F1 | Strong for the named no-call dev140 replay | Paper-derived metric implementation on development data; not reproduction of the original system or reported scores |
| C8 | The recorded ExECT model rows do not implement one consistent model-led method across all four families | Strong for the saved-output ownership audit | Full200 aggregate-only audit; corrected scores are unpromoted candidates |

## Selected headline results

| Task and method | Result |
| --- | ---: |
| Gan single-pass system, test450 | 364/450 Purist |
| Gan multi-model comparison, test450 | 379/450 Purist |
| ExECT rules only, dev140 | paper-derived macro item F1: phrase 0.5687, CUI 0.7144, all features 0.6020; strict micro item F1 0.3548 |
| ExECT GEPA LLM only, dev140 | clinical fact F1 0.7393 |
| ExECT historical LLM with rules (`v08`), dev140 | clinical fact F1 0.9189; reproducible development control, not the final decision-0040 architecture |
| ExECT GPT / Qwen historical full200 rows | 0.8356 / 0.8197 clinical fact F1 |

The historical DeepSeek full200 aggregate is `0.8566`, but its thinking state
was not recorded. It is retained for audit only and is excluded from the
paper-facing model table unless thinking-enabled execution can be proved.

## Wording the paper must avoid

- Do not describe ExECT full200 as an independent holdout.
- Do not describe `clinical_headline` as the published strict benchmark.
- Do not describe the paper-derived development replay as reproduction of the
  original ExECT system or its 0.87/0.90 validation scores.
- Do not present internal annotation review as independent clinical validation.
- Do not claim cross-task transfer without a selected ExECT study.
- Do not present the GEPA run as a production reference.
- Do not state a six-model conclusion from three models.
- Do not describe the historical ExECT Prescription or Seizure Frequency
  columns as model-to-model results.
- Do not describe `v08` as satisfying the final model-led family contract.
- Do not promote the corrected aggregate candidates before durable
  configurations, `state_profile`, attribution, regression, and retained-
  evidence checks exist.
- Do not turn Gan model-pass counts into measured token, dollar, energy, or
  latency savings.

## Open work

1. Materialize decision 0040 with durable model-swap configurations, reproduce
   the corrected aggregate, add Seizure Frequency `state_profile`, and pass the
   attribution, regression, and retained-evidence checks.
2. Evaluate model-reported confidence out of sample.
3. Run the decision-0039 roster with the same corrected model-led pipeline:
   GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, hosted DeepSeek V4 Flash, local Qwen
   3.6:35B, and local Gemma 4 26B. For DeepSeek, use
   `deepseek/deepseek-chat` with thinking enabled, report the display name
   **DeepSeek V4 Flash**, and retain the thinking-setting metadata.
