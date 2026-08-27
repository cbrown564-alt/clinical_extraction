# 06 — Gan 2026 results and test rules

Last updated: 2026-07-27

Gan 2026 asks for one current seizure-frequency label per letter.

- dev750 permits development and replay; retained artifacts use the legacy
  identifier `validation750`;
- test450 is locked and aggregate-only;
- a new test run requires a fixed protocol and explicit authority;
- test450 rows must not be inspected or used for tuning.

A 2026-07-15 documentation command unintentionally printed part of a generated
test450 row table after the hosted runs were complete. No row was analyzed or
used for tuning. The results remain frozen aggregate evidence, but the project
must no longer claim that no test row was ever exposed.

## Development comparison

| Method | Split | Purist result |
| --- | --- | ---: |
| Rules only | dev750 | 697/750 |
| LLM only | dev750 | 581/750 |
| LLM event extraction with deterministic normalization | dev750 | 661/748 rendered |

## Saved test results

| Method | Purist result | Limit |
| --- | ---: | --- |
| Single-pass event extractor | 364/450 | Saved aggregate |
| Multi-model comparison (`V12`) | 379/450 | Saved aggregate; source removed |

## Six-model matched test results

| Model | Prompt | Purist | Pragmatic | Operational result |
| --- | --- | ---: | ---: | --- |
| GPT-4.1-mini | v0.5 | 361/450 (0.8022) | 379/450 (0.8422) | 0 call failures; 4 parse/validation failures; 419/450 exact evidence |
| GPT-5.6 Luna | v0.5 | 362/450 (0.8044) | 375/450 (0.8333) | 0 call failures; 3 parse/validation failures; 444/450 exact evidence |
| GPT-5.6 Sol | v0.5 | 373/450 (0.8289) | 384/450 (0.8533) | 0 call or parse/validation failures; 450/450 exact evidence |
| DeepSeek V4 Flash | v0.5 | 344/450 (0.7644) | 366/450 (0.8133) | 0 call failures; 3 parse/validation failures; 433/450 exact evidence |
| Qwen 3.6:35B | v0.5 | 362/450 (0.8044) | 384/450 (0.8533) | 0 call failures; 2 parse/validation failures; 347/450 exact evidence |
| Gemma 4 26B | v0.5 | 355/450 (0.7889) | 374/450 (0.8311) | 0 call failures; 2 parse/validation failures; 436/450 exact evidence |

Only aggregate results from these locked-test runs may be cited. All six use
the same v0.5 prompt, pipeline family, and scorers. The table above is the
frozen matched panel under the prior `hybrid_full_stack`. As of 2026-07-31 the
Gan **LLM with rules** ruleset is finalized (projection/anti-regression,
dated-count, competing-rate floors, and narrow cross-model guards). Current
LLM-with-rules readouts use no-call replay of the same saved raw outputs;
see [six-model comparison](../research/shared/six_model_comparison_report_2026-07-18.md).
Provider-required transport and temperature differences remain. Report results
as a matched aggregate-only panel, not a pristine one-shot or model-neutral
capability ranking. The local conditions have the same retained claim status as
the hosted conditions; the route and reparse differences are caveats, not a
lower evidence tier. See the
[hosted protocol](../experiments/gan2026/gan2026_matched_v05_test450_protocol_2026-07-16.md)
and [local/replay extension](../experiments/gan2026/gan2026_matched_v05_local_test450_and_qwen_val750_protocol_2026-07-18.md).

## Six-model development coverage

The selected v0.5 six-model `dev750` panel is complete under
[the development protocol](../experiments/gan2026/gan2026_matched_v05_dev750_protocol_2026-07-27.md).
Frozen panel artifacts remain the row-trace/attribution owners under the prior
repair. Final-ruleset development scores are no-call replays of those saved
raw outputs. Do not use the quarantined v0.7 `dev750` panel as the development
half of the primary v0.5 comparison.

## Quarantined prompt-interaction evidence

The complete v0.7 test450 panel remains a historical diagnostic. Relative to
v0.5 it increased Qwen Purist correctness by 5 rows and reduced correctness for
GPT-4.1-mini by 8, Luna by 10, Sol by 15, DeepSeek by 2, and Gemma by 12. It may
be cited only as aggregate evidence that prompt changes can interact with model
family. It must not supply primary scores, rankings, reliability measurements,
or paper conclusions.

## Efficiency result

The [aggregate efficiency audit](../research/gan2026/efficiency/single_vs_multimodel_efficiency_report_2026-07-14.md)
closes the retrospective comparison with a bounded result. V12 gained 15
Purist-correct rows (3.33 percentage points) but requires three model passes per
note in a cold execution, versus one for the single-pass system.

The old runs did not retain matched prompt/completion tokens, cost, wall time,
hardware, retries, or cache telemetry. V12's final test audit reused two
saved upstream traces and made 450 new reasoner calls, so the paper must not
present a measured token, dollar, energy, or latency comparison. No new model
calls or locked-row inspection are warranted to recreate missing telemetry.
