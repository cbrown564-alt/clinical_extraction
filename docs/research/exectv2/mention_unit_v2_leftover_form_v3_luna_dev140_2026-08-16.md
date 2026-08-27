# ExECT mention-unit v2 leftover-form v3 intervening counts — `dev140`

Date: 2026-08-16  
Status: complete; **answer**  
Protocol: [leftover-form v3](mention_unit_v2_leftover_form_v3_luna_dev140_protocol_2026-08-16.md)  
Prior: [leftover-form v2](mention_unit_v2_leftover_form_v2_luna_dev140_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

## Executive result

Guarded intervening leftover counts recover SeizureFrequency form on
saved mention-unit v2 hybrid raws without taking a count from age,
duration / last-event span, or a calendar date. Decision 0050 is
unchanged. Default encoder stays `landed`. Do not retune the prompt.
Do not inspect `test60`. Do not promote leftover-form from this
remasure alone.

Leftover-form v1 rematerialized as **130** SF-with-count and **2**
Investigations Unknown. Unsafe intervening v2 stayed **172**.
`model_calls`: 0.

| Arm | SF-with-count | Δ vs v1 | `count_unparsed` | Inspected verdict |
| --- | ---: | ---: | ---: | --- |
| leftover-form v1 | 130 | — | 104 | comparator |
| intervening v2 | 172 | +42 | 62 | recorded unsafe baseline |
| intervening v3 | 164 | +34 | 70 | **answer** |

Headline context versus leftover-form v1 **0.7316**: intervening v3
**0.7390** (+0.0074). Unsafe v2 remains **0.7395**. `llm` remains
**0.7340**. Empty-gold extras stayed 49 mentions on 27 letters.
Names rewritten stayed 1. ECG stayed out. Guard-failure census: 0.

## Valid evidence

- 140 development letters; `test60` not inspected.
- Saved mention-unit v2 hybrid `raw_output` only.
- Intervening counts only. Implicit period, case-fold, and last-event
  were not retried.
- The three false-read guards were written in the protocol before
  code. They are span predicates, not letter patches.
- Prompt `exectv2_mention_unit_v2` unchanged. Landed default unchanged.
- Unsafe `leftover_form_intervening` unchanged.

Artifact: [`comparison.json`](../../../experiments/exectv2_mention_unit_v2_leftover_form_v3_luna_dev140_20260816/comparison.json)

## True recoveries

The four leftover-word recoveries named in the protocol still land:

- `2 febrile seizures` (including when age follows in the same
  sentence)
- `four in the last three weeks`
- `a couple of focal impaired awareness seizures`
- `1 since previous appointment`

The +34 versus leftover-form v1 are a subset of the v2 intervening
recoveries. v3 did not invent a new count class.

## False-read guards

v3 blocked the eight v2 intervening counts that leftover-form v1
did not have:

- EA0016 `22 December` → 22
- EA0061 `at the age of 3` → 3
- EA0161 `age of 8` → 8
- EA0110 `For the last six month` → 6
- EA0135 `6 months without having seizures` → 6
- EA0137 `2 months ago` → 2
- EA0141 `two weeks ago` → 2
- EA0163 `for around three weeks` → 3

EA0110 is the duration-window class already named in the protocol:
a matched number immediately followed by a time unit is a time
quantity. Same-letter true counts still recovered where they
existed (`2 secondary generalised seizures per year` on EA0137;
`3 febrile seizures` on EA0141).

## Decision

**answer**. Intervening leftover counts rise, extras do not rise,
names are not rewritten more, ECG stays out, and the three
false-read classes do not become counts.

Do not make leftover-form the default encoder from this remasure.
Do not start mention-unit v3 or Fork B. Do not stack implicit
period, case-fold, or last-event onto this arm. Remaining
`count_unparsed` 70 is a different leftover class, not a warrant
to widen these guards against the catalog.

The later leftover-word remasure is
[leftover-form v4](mention_unit_v2_leftover_form_v4_luna_dev140_2026-08-16.md):
episodes and implicit period v4 are answers; last-event v4 revises.

## Claim boundary

Development remasure of saved mention-unit v2 hybrid raws. Not
clinical validation, holdout evidence, or a Decision 0050 change.
