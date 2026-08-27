# ExECT mention-unit v2 leftover-form v2 knobs — `dev140`

Date: 2026-08-16  
Status: complete; four-arm **revise**  
Protocol: [leftover-form v2](mention_unit_v2_leftover_form_v2_luna_dev140_protocol_2026-08-16.md)  
Prior: [leftover-form v1](mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

## Executive result

Each leftover-form v2 knob moves the named leftover class on saved
mention-unit v2 hybrid raws. Inspection revises every arm. Decision
0050 is unchanged. Default encoder stays `landed`. Do not retune the
prompt. Do not stack these knobs. Do not inspect `test60`.

Leftover-form v1 rematerialized as **130** SF-with-count and **2**
Investigations Unknown. `model_calls`: 0.

| Arm | SF-with-count | Δ | Named leftover | Automated bar | Inspected verdict |
| --- | ---: | ---: | --- | --- | --- |
| leftover-form v1 | 130 | — | `count_unparsed` 104 | — | comparator |
| intervening | 172 | +42 | unparsed 104→62 | extras held | **revise** — age, duration, and a date became counts |
| implicit period | 149 | +19 | unparsed 104→86 | extras held | **revise** — `a week ago` and several-times rates became 1 |
| casefold | 142 | +12 | drops 36→21 | extras rose 49→57 | **revise** |
| last-event | 136 | +6 | last-event zero +9 | extras held | **revise** — `clinical_name` plus `Last month` zeroed counted clusters |

Headline context versus leftover-form v1 **0.7316**: intervening
**0.7395**, implicit **0.7374**, casefold **0.7413**, last-event
**0.7321**. Control hybrid remains **0.9020**. `llm` remains **0.7340**.

## Valid evidence

- 140 development letters; `test60` not inspected.
- Saved mention-unit v2 hybrid `raw_output` only.
- One knob per arm. Leftover-form v1 unchanged.
- Prompt `exectv2_mention_unit_v2` unchanged. Landed default unchanged.

Artifact: [`comparison.json`](../../../experiments/exectv2_mention_unit_v2_leftover_form_v2_luna_dev140_20260816/comparison.json)

## Intervening-word counts

True recoveries include `2 febrile seizures`, `four in the last three
weeks`, `a couple of focal impaired awareness seizures`, and `1 since
previous appointment`.

False counts from the same knob:

- EA0016 `22 December` → `NumberOfSeizures=22`
- EA0061 / EA0161 age (`at the age of 3` / `age of 8`) → 3 / 8
- EA0135 `6 months without having seizures` → 6
- EA0137 / EA0141 last-event duration (`2 months ago`, `two weeks ago`)
- EA0163 `hasn't had any seizures now for around three weeks` → 3

The protocol stop is duration tokens becoming counts. That fired.

## Implicit 1 / bare period

True recoveries: EA0043 `every year` → 1/Year; EA0049 `Myoclonic jerks
daily` → 1/Day; EA0161 `absences … every week` → 1/Week (also drops
`suppress_uncoded_sf` 8→7).

False 1/period fills: EA0096 `until about a week ago` matches leftover
`a week` and becomes 1/Week. Several-times rates already parsed by v1
as 3 collapse to 1 when implicit period fills a bare unit (EA0076,
EA0158, EA0121 `2 or 3 times per month` → 1/Month).

## Case-fold gate

Fifteen exact-case drops go away. Ten kept names include real
case-only letter spans (`Focal` vs `focal`). Empty-gold extras rise
49→57 because EA0021, EA0045, and EA0185 are empty-gold letters whose
case-only names now survive. Paraphrases absent from the letter stay
dropped. The gate does what it said. The extras stop fired.

## Last-event cue widening

True zeros: `event last month`, `seizure last month`, `seizures free`,
`seizrue free`, `No events since surgery`.

False zeros: haystack is `clinical_name` plus evidence. A name
`seizures` plus evidence `Last month, Joan had a cluster of 5` becomes
`seizures Last month` and the wide cue fires. EA0151, EA0169, and
EA0181 lose counted clusters to 0.

## Decision

**revise** on all four arms. The leftover classes are real. None of
the knobs as written is safe to keep. Do not promote leftover-form v2.
Do not make leftover-form the default. Do not start mention-unit v3 or
Fork B from this remasure.

The later intervening-counts-only remasure with those three
guards is an **answer**:
[leftover-form v3](mention_unit_v2_leftover_form_v3_luna_dev140_2026-08-16.md).
A later study that wants intervening counts must exclude age,
duration, and calendar dates in the same protocol, not by retuning
these rows. Implicit period must not fill 1 onto `a week ago` or onto
an already-parsed several-times rate. Last-event cues must not see
`clinical_name` glued onto `Last month`. Case-fold, if retried, needs
an empty-gold extras bar in the same study.

## Claim boundary

Development remasure of saved mention-unit v2 hybrid raws. Not
clinical validation, holdout evidence, or a Decision 0050 change.
