# ExECT mention-unit v2 leftover-form encoder — `dev140`

Date: 2026-08-16  
Status: complete; **answer**  
Protocol: [mention_unit_v2_leftover_form_encoder_luna_dev140_protocol_2026-08-16.md](mention_unit_v2_leftover_form_encoder_luna_dev140_protocol_2026-08-16.md)  
Prior: [hybrid encoder damage catalog](mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

## Executive result

Parsing leftover evidence words recovers the hybrid form the landed
encoder left behind. SF mentions with a count rise **58 → 130**
versus `llm` **224**. Investigations Unknown fall **61 → 2** versus
`llm` **1**. Names stay. Empty-gold extras do not rise. The result
is an **answer**. Decision 0050 is unchanged. Default encoder stays
`landed`. Do not retune the prompt. Do not inspect `test60`.

## Valid evidence

- 140 development letters; `test60` not inspected.
- `model_calls`: 0. Saved mention-unit v2 hybrid `raw_output` only.
- Landed rematerialization reproduced the saved hybrid form census
  (SF with a count **58**; Investigations Unknown **61**).
- Prompt `exectv2_mention_unit_v2` unchanged. Landed encoder
  unchanged. Candidate encoder `exectv2_mention_unit_leftover_form_v1`.

Artifact: [`comparison.json`](../../../experiments/exectv2_mention_unit_v2_leftover_form_encoder_luna_dev140_20260816/comparison.json)

## Form versus name

| Check | `llm` | landed | leftover-form |
| --- | ---: | ---: | ---: |
| SF mentions | 267 | 232 | 234 |
| SF mentions with a count | 224 | 58 | 130 |
| Investigations Normal/Abnormal | 120 | 62 | 121 |
| Investigations Unknown | 1 | 61 | 2 |
| SF `clinical_name` kept | — | 231 | 233 |
| SF `clinical_name` rewritten | — | 1 | 1 |
| Empty-gold SF extras | 53 | 49 | 49 |

Headline context: leftover-form **0.7316** versus landed **0.6255**
and `llm` **0.7340**. SF **0.4599** versus landed **0.3167** and
`llm` **0.6225**. Investigations **0.9112** versus landed **0.4788**
and `llm` **0.9027**. Diagnosis and Prescription do not move.
Control hybrid remains **0.9020**.

## Remaining leftover

| Class | Landed | Leftover-form | Owner |
| --- | ---: | ---: | --- |
| `count_unparsed` | 174 | 104 | Leftover words that are not a digit/word count plus day/week/month/year. Common leftovers: `events`/`episodes`, `fortnight`, qualitative frequency, and `every week` without a number |
| `result_unknown` | 61 | 2 | EEG spans with no List 9 finding |
| `text_not_substring_drop` | 36 | 36 | Unchanged. Pre-encoder drop |
| `suppress_uncoded_sf` | 10 | 8 | Qualitative or unnumbered absence/drop language |
| `name_rewritten` | 1 | 1 | Unchanged |

Two SF mentions that landed suppressed now survive because leftover
count or period filled before the empty-attribute gate. Last-event
zero still fires. No ECG. No letter-text growth.

## Decision

**answer.** Mechanism: `leftover_form_recovered`. List 9 closes the
Investigations Unknown gap. Leftover count and period recover part of
the SF form gap. The remaining SF leftover is a different parse
question (`events`/`episodes`, `fortnight`, qualitative rate), not a
reason to rewrite the prompt or start Fork B.

Leftover-form stays a research-lane encoder. It is not the default
and not a selected-stack change.

## Next

Leave the mention-unit v2 language frozen. Leave default
`materialize_mention_unit` on `landed`. A later study that wants the
remaining 104 unparsed counts needs its own protocol. The `v0.9.24`
scope-split decision remains the other live track.

## Claim boundary

Development remasure of saved mention-unit v2 hybrid raws. Not
clinical validation, holdout evidence, or a Decision 0050 change.
