# 10 — Paper claims and provenance

Last updated: 2026-07-14

This document owns claim strength. The
[retained evidence manifest](../experiments/retained_evidence_manifest.md) owns
selected files and hashes. The [manuscript](../research/paper_manuscript_2026-06-26.md)
must not exceed either boundary.

## Required paper story

| ID | Required statement | Current evidence | State |
| --- | --- | --- | --- |
| S1 | One modular system is evaluated on Gan and ExECT | Six reference cells replay from retained code and outputs | Partial |
| S2 | Rules-only, LLM-only, and hybrid forms have attributable results on both tasks | Two-task by three-family manifest | Partial |
| S3 | Gan V12 adds modest quality at higher operational cost | Quality is retained; matched cost and latency are missing | Partial |
| S4 | Six exact models run on one frozen ExECT architecture | GPT-4.1-mini, DeepSeek, and Qwen are retained | 3/6 |
| S5 | Unknown-versus-rate overconfidence generalizes across models and tasks | Gan evidence retained; ExECT transfer proof is not retained | Open |
| S6 | Extraction, normalization, projection, schema, and evidence stages are explicit and tested | Stage closures and cross-task ablation retained | Partial |
| S7 | ExECT reproduces the published phrase/CUI/full-attribute surface | Current deterministic strict score remains below the paper | Open |
| S8 | Both tasks have bounded reliability evidence | Gan package and ExECT internal calibration retained | Partial |
| S9 | Annotation flaws and conventions have complete transparent handling | Four family ledgers and selected row analyses retained | Partial |

## Current capability claims

| ID | Claim | Strength | Retained proof | Boundary |
| --- | --- | --- | --- | --- |
| C1 | Some ExECT Diagnosis and SF disagreements are annotation multiplicity or representation issues | Soft | Canonical row analyses, blind replication, family ledgers | Internal dev140 adjudication |
| C2 | Normalization improves both tasks while the evidence check is score-inert on representative replays | Strong | Cross-task ablation package | Development replay only |
| C3 | Gan unknown-versus-rate behavior transfers to ExECT | Open | No selected ExECT transfer artifact | Do not claim yet |
| C4 | The same ExECT core runs across GPT-4.1-mini, DeepSeek, and Qwen | Strong but asymmetric | Three-model package | Full200 development-inclusive aggregate |
| C5 | Split and evaluation discipline is enforced | Strong for retained paths | Split manifests, CLI barriers, registry, replay tests | Not external validation |

## Retained headline results

### Gan

| Subject | Result |
| --- | ---: |
| Operational frozen test450 | 364/450 Purist |
| V12 frozen ceiling | 379/450 Purist |

### ExECT

| Subject | Result |
| --- | ---: |
| Deterministic dev140 strict item F1 | 0.3548 |
| GEPA LLM-only dev140 headline F1 | 0.7393 |
| Hybrid v08 dev140 headline F1 | 0.9189 |
| Same-core full200 GPT / DeepSeek / Qwen | 0.8356 / 0.8566 / 0.8197 |

## Prohibited wording

- Do not describe ExECT full200 as an independent holdout.
- Do not describe `clinical_headline` as the published strict benchmark.
- Do not present internal annotation adjudication as independent clinical validation.
- Do not claim ExECT Wall transfer without adding selected evidence.
- Do not present the GEPA cell as a production control.
- Do not state a six-model conclusion from the current three-model package.

## Open work

1. Add the matched Gan quality, calls, tokens, cost, and latency table.
2. Implement the deterministic phrase/CUI/full-attribute benchmark surface.
3. Evaluate model-reported confidence out of sample.
4. Consolidate the annotation taxonomy and sensitivity analysis.
5. Run the remaining three frozen model comparisons.
6. Regenerate manuscript tables and sync the IEEE source.

