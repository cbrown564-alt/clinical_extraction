# 06 — Gan 2026 results and holdout rules

Last updated: 2026-07-14

Gan 2026 asks for one current seizure-frequency label per letter.

- validation750 permits development and replay;
- test450 is locked and aggregate-only;
- a new holdout run requires a fixed protocol and explicit authority;
- test450 rows must not be inspected or used for tuning.

## Development comparison

| Method | Split | Purist result |
| --- | --- | ---: |
| Rules only | validation750 | 697/750 |
| LLM only | validation750 | 581/750 |
| LLM event extraction with deterministic normalization | validation750 | 661/748 rendered |

## Saved holdout results

| Method | Purist result | Limit |
| --- | ---: | --- |
| Single-pass event extractor | 364/450 | Saved aggregate |
| Multi-model comparison (`V12`) | 379/450 | Saved aggregate; source removed |

## Efficiency result

The [aggregate efficiency audit](../research/gan2026/efficiency/gan2026_single_vs_multimodel_efficiency_report_2026-07-14.md)
closes the retrospective comparison with a bounded result. V12 gained 15
Purist-correct rows (3.33 percentage points) but requires three model passes per
note in a cold execution, versus one for the single-pass system.

The old runs did not retain matched prompt/completion tokens, cost, wall time,
hardware, retries, or cache telemetry. V12's final holdout audit reused two
saved upstream traces and made 450 new reasoner calls, so the paper must not
present a measured token, dollar, energy, or latency comparison. No new model
calls or locked-row inspection are warranted to recreate missing telemetry.
