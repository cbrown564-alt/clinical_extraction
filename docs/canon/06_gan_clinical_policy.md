# 06 — Gan 2026 results and holdout rules

Last updated: 2026-07-18

Gan 2026 asks for one current seizure-frequency label per letter.

- validation750 permits development and replay;
- test450 is locked and aggregate-only;
- a new holdout run requires a fixed protocol and explicit authority;
- test450 rows must not be inspected or used for tuning.

A 2026-07-15 documentation command unintentionally printed part of a generated
test450 row table after the hosted runs were complete. No row was analyzed or
used for tuning. The results remain frozen aggregate evidence, but the project
must no longer claim that no test row was ever exposed.

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

## Six-model matched holdout results

| Model | Prompt | Purist | Pragmatic | Operational result |
| --- | --- | ---: | ---: | --- |
| GPT-4.1-mini | v0.7 | 353/450 (0.7844) | 371/450 (0.8244) | 0 call failures; 2 parse/schema/label issues; 419/450 exact evidence |
| GPT-5.6 Luna | v0.7 | 352/450 (0.7822) | 365/450 (0.8111) | 0 call failures; 3 parse/schema/label issues |
| GPT-5.6 Sol | v0.7 | 358/450 (0.7956) | 376/450 (0.8356) | 0 call or parse/schema failures |
| DeepSeek V4 Flash, thinking enabled | v0.7 | 342/450 (0.7600) | 362/450 (0.8044) | 0 call failures; 4 parse/schema/label issues; 434/450 exact evidence |
| Qwen 3.6:35B | v0.7 | 367/450 (0.8156) | 380/450 (0.8444) | 0 final call/parse/schema/label issues; 363/450 exact evidence |
| Gemma 4 26B | v0.7 | 343/450 (0.7622) | 367/450 (0.8156) | 0 final call/parse/schema/label issues; 437/450 exact evidence |

Only aggregate results from these locked-test runs may be cited. All six use
the same current v0.7 prompt, pipeline, repair policy, and scorer. The panel is
matched on those fields, but provider-required transport and temperature
differences remain. Qwen and Gemma were retained through aggregate-only no-call
reparse of their sealed local outputs, while the hosted conditions retain their
recorded hosted execution paths. Prompt v0.7 was developed from validation
failures, and test450 has supported sequential aggregate evaluations. Report
the result as a matched aggregate-only panel, not a pristine one-shot or
model-neutral capability ranking. The local conditions have the same retained
claim status as the hosted conditions; the route and reparse differences are
caveats, not a lower evidence tier. See the
[matched protocol and result](../experiments/gan2026/gan2026_matched_v07_test450_protocol_2026-07-15.md).

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
