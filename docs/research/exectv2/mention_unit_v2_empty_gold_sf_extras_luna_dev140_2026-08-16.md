# ExECT mention-unit v2 empty-gold SF extras — `dev140`

Date: 2026-08-16  
Status: complete; **answer**  
Protocol: [mention_unit_v2_empty_gold_sf_extras_luna_dev140_protocol_2026-08-16.md](mention_unit_v2_empty_gold_sf_extras_luna_dev140_protocol_2026-08-16.md)  
Prior: [mention-unit v2 `dev140`](mention_unit_v2_fork_a_luna_dev140_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)

## Executive result

The extras rise is more frequency statements on letters gold already
left empty, not more empty-gold letters and not seizure-story over-read.
Mention-unit v2 `llm` has **53** extras on **30** letters. Default v4
has **38** extras on **33** letters. Twenty-eight letters are shared.
The result is an **answer**. Decision 0050 is unchanged. Do not retune.
Do not start mention-unit v3 or Fork B.

## Valid evidence

- 140 development letters; `test60` not inspected.
- `model_calls`: 0. Saved v2 and v4 `dev140` rows only.
- 41 letters have zero gold SeizureFrequency units.
- 0 seizure-story extras. 0 unclassified extras.

Artifact: [`extras_catalog.json`](../../../experiments/exectv2_mention_unit_v2_empty_gold_sf_extras_luna_dev140_20260816/extras_catalog.json)

## Letter count versus mention count

| Method | Empty-gold letters with an SF extra | SF extras |
| --- | ---: | ---: |
| v4 `llm` | 33 | 38 |
| v2 `llm` | 30 | 53 |

v2-only letters: EA0014, EA0018. Both are frequency statements
(“continues to get”; “twice a week”).
v4-only letters: EA0052, EA0092, EA0149, EA0166, EA0185.
v2 dropped five v4 extra letters. The mention-count stop fired because
v2 emits more statements per shared empty-gold letter.

## Classes

| Class | Mentions |
| --- | ---: |
| frequency_statement | 46 |
| remote_childhood | 7 |
| seizure_story | 0 |
| other | 0 |

Five mentions are same-evidence copies: EA0109 writes one sentence as
three form readings, and EA0114 writes the couple-of-FIAS / no-FBTCS
clause as two names. Those are not unused-letter units.

Every extra is a count, rate, last-event, change, seizure-free
duration, or a febrile / childhood count. That is the mention-unit job
succeeding on unannotated letters. It remains a scorer extra. It is
not missing gold.

## Decision

**answer.** Mechanism: more frequency statements on shared empty-gold
letters. The predeclared transfer stop still stands. The leftover is
not a reason to teach the model to omit supported frequency
statements. A later study that wants extras down is a gold-policy or
scorer-denominator question, not a clinical-name rewrite.

## Next

Leave this language frozen. Do not retune for EA0009 or empty-gold
extras. The leftover-form remasure is a separate **answer**:
[leftover-form](mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md).

## Claim boundary

Development catalog of mention-unit v2 empty-gold SeizureFrequency
extras. Not clinical validation, holdout evidence, or a Decision 0050
change.
