# Protocol: Living source-near rules find on `test450`

Date: 2026-08-31
Status: complete
Owner: this file
Report: [result](gan_rules_source_near_find_test450_2026-08-31.md)
Parent: [find dialects](gan_rules_find_llm_dialects_protocol_2026-08-31.md)
Frozen candidate: `phase_c_candidate_config()`
Guardrail: `gan2026-scoring-guardrail`;
[holdout is aggregate-only](../../paper/decisions/holdout-is-aggregate-only.md)

## Primary question

What is the Purist find-stop count for the promoted three-stage
rules program when `find_label` is the living source-near dialect?

## Why this matters

Phase D published find/encode **292 / 292** because those stops
were fused codebook strings. Living find is now source-near
(`gan_llm_extract_raw` dialect). The five-cell rules find ablation
and the FES stage table still print 0.65 from that fused stop.
Select must not move.

## Frozen candidate

`run_record_three_stage(phase_c_candidate_config())`. Zero model
calls. Scorer: `score_label` Purist. No scorer, prompt, or keep
change.

| Stop | Public field | Expected |
| --- | --- | --- |
| Find | source-near `find_label` | new measured count |
| Encode | codebook of the same pick | **292/450** (Phase D) |
| Select | submitted label | **325/450** |

If select is not 325, stop and do not rewrite the five-cell JSON.
If encode is not 292, record the measured encode and do not invent
292.

## Data and inspection

| Item | Value |
| --- | --- |
| Split | `test450` |
| Row policy | `aggregate_only` |
| Public output | stop counts and rates only |

Do not inspect, quote, or tune on holdout identifiers, notes,
predictions, evidence, errors, or class slices. The public artifact
must not contain those keys.

## Claim boundary

Aggregate-only remasure of the living find dialect. Select stays
the cited 0.72. Not a new rules program. Not clinical validation.
