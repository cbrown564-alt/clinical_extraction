# ExECT mention-unit v2 hybrid encoder damage — `dev140`

Date: 2026-08-16  
Status: complete; **answer**  
Protocol: [mention_unit_v2_hybrid_encoder_damage_luna_dev140_protocol_2026-08-16.md](mention_unit_v2_hybrid_encoder_damage_luna_dev140_protocol_2026-08-16.md)  
Prior: [mention-unit v2 `dev140`](mention_unit_v2_fork_a_luna_dev140_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

## Executive result

The landed encoder keeps the emitted SeizureFrequency name and loses
the form. Hybrid SF mentions with a count are **58/232** versus `llm`
**224/267**. Investigations results go Unknown: hybrid **61** versus
`llm` **1**. Names are not the leftover: **231** hybrid SF names are
kept; **1** is rewritten. The result is an **answer**. Decision 0050
is unchanged. Do not retune the prompt. Do not retune the encoder
from this catalog.

## Valid evidence

- 140 development letters; `test60` not inspected.
- `model_calls`: 0. Saved mention-unit v2 `dev140` rows only.
- Matched independent `llm` and `llm_with_rules` calls. Not one raw
  through two projectors.

Artifact: [`damage_catalog.json`](../../../experiments/exectv2_mention_unit_v2_hybrid_encoder_damage_luna_dev140_20260816/damage_catalog.json)

## Form versus name

| Check | `llm` | hybrid |
| --- | ---: | ---: |
| SF mentions | 267 | 232 |
| SF mentions with a count | 224 | 58 |
| Investigations Normal/Abnormal | 120 | 62 |
| Investigations Unknown | 1 | 61 |
| SF `clinical_name` kept | — | 231 |
| SF `clinical_name` rewritten | — | 1 |

Headline context from the transfer study: hybrid SF **0.3167** versus
`llm` **0.6225**; Investigations **0.4788** versus **0.9027**.

## Named leftover classes

| Class | Count | Owner |
| --- | ---: | --- |
| `count_unparsed` | 174 | Landed SF encoder does not recover count or period from leftover evidence words |
| `result_unknown` | 61 | Investigation result stays Unknown unless the evidence uses the words `normal` or `abnormal` |
| `text_not_substring_drop` | 36 | Item dropped because `clinical_name` is not a letter substring |
| `suppress_uncoded_sf` | 10 | `suppress_uncoded_or_noise_sf` runs on empty attributes **before** encoding. `absences` is not in the phrase list, so “2–3 per day” never gets a count |
| `name_rewritten` | 1 | EA0161 `seizure frequency` → `seizure` |

Seven of the ten suppressions match a gold SeizureFrequency unit
(mostly `absences`). `last_event_zero` fired 43 times. That overlay
is last-event language becoming `NumberOfSeizures=0`, not name loss.

## Decision

**answer.** Mechanism: `count_and_result_unparsed`. The frozen
clinical-name language did its job. The hybrid lane does not yet
parse leftover evidence words into the scored form fields. That is
an encoder leftover, not a reason to rewrite the prompt or start
Fork B.

A later encoder study is a new protocol. It must not inspect
`test60` and must not treat this catalog as permission to retune
against these rows during implementation.

## Next

The leftover-form remasure is an **answer**:
[leftover-form](mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md).
Leave the mention-unit v2 language frozen. Default encoder stays
`landed`. The `v0.9.24` scope-split decision remains the other live
track.

## Claim boundary

Development catalog of mention-unit v2 hybrid encoder leftover. Not
clinical validation, holdout evidence, or a Decision 0050 change.
