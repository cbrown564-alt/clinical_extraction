# ExECT mention-unit v2 leftover-form v4 leftover-word contracts — `dev140`

Date: 2026-08-16  
Status: complete; episodes **answer**, implicit period v4 **answer**, last-event v4 **revise**  
Protocol: [leftover-form v4](mention_unit_v2_leftover_form_v4_luna_dev140_protocol_2026-08-16.md)  
Prior: [leftover-form v3](mention_unit_v2_leftover_form_v3_luna_dev140_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

## Executive result

Three remaining leftover-word contracts were tested independently on
top of leftover-form v3. Decision 0050 is unchanged. Default encoder
stays `landed`. Do not retune the prompt. Do not inspect `test60`.
Do not stack these arms. Do not promote leftover-form from this
remasure.

Leftover-form v3 rematerialized as **164** SF-with-count and **2**
Investigations Unknown. `model_calls`: 0. Empty-gold extras stayed
49 mentions on 27 letters. Names rewritten stayed 1. ECG stayed out.

| Arm | SF-with-count | Δ vs v3 | `count_unparsed` | Automated | Inspected |
| --- | ---: | ---: | ---: | --- | --- |
| intervening v3 | 164 | — | 70 | comparator | comparator |
| episodes | 165 | +1 | 69 | answer | **answer** |
| implicit period v4 | 171 | +7 | 64 | answer | **answer** |
| last-event v4 | 169 | +5 | 65 | answer | **revise** |

Headline versus leftover-form v3 **0.7390**: episodes **0.7390**,
implicit **0.7428** (+0.0038), last-event **0.7386** (−0.0004).
`llm` remains **0.7340**.

## Valid evidence

- 140 development letters; `test60` not inspected.
- Saved mention-unit v2 hybrid `raw_output` only.
- One contract per arm, each starting from leftover-form v3.
- Guards were written in the protocol before code.
- Prompt `exectv2_mention_unit_v2` unchanged. Landed default unchanged.

Artifact: [`comparison.json`](../../../experiments/exectv2_mention_unit_v2_leftover_form_v4_luna_dev140_20260816/comparison.json)

## Episodes

The one recovered leftover is the named true range: EA0040 `three or
four further episodes` → 3–4. Collapse, `stopped the episodes`, and
`22 December` stay unparsed. Automated guard-failure census: 0.

Most of the remaining `events` / `episodes` mentions are not missing
counts. They are last-event language, a collapse, a date, or
`stopped the episodes`. The leftover-word contract is real and small
on this split.

## Implicit period v4

Seven bare-period mentions become 1 plus period: `every year`,
`daily`, `every month`, `on a weekly basis` (two), `happening
weekly`, and `absences … every week`. `until about a week ago` does
not become 1. `2 or 3 times per month` stays 3. One previously
suppressed uncoded absence mention survives because it now has a
count.

## Last-event v4

The intended zeros land: `event last month`, `seizures free`,
`seizrue free`, `seizure last month`, and `No events since surgery`.
The glued cluster (`Last month` plus `cluster of 5`) is not zeroed.

Inspection revises the arm. Skipping the leftover-form early zero so
that intervening can run first also lets a number in a true-zero
sentence become a count. EA0075 `Once commenced on sodium valproate
… she has had no further seizures` becomes 1. `Once` is not a
seizure count. Two other last-event sentences that also contain a
historical count move from 0 to that count (EA0010 `3 or 4`; EA0061
`2 events in total`). The named glue failure did not fire. A new
false-read class did.

## Decision

Episodes and implicit period v4 are **answers**. Last-event v4 is a
**revise**. Do not stack the arms. Do not make leftover-form the
default encoder. Do not start mention-unit v3 or Fork B.

The remaining `count_unparsed` after the two answers is still mostly
qualitative rate or change, a number that is the wrong object, or an
unnumbered cluster. Those are not leftover counts waiting for a
wider net.

## Claim boundary

Development remasure of saved mention-unit v2 hybrid raws. Not
clinical validation, holdout evidence, or a Decision 0050 change.
