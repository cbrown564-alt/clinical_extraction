# ExECT `v0.9.24` cheap-slice stack — GPT-5.6 Luna `dev140`

Date: 2026-08-16  
Status: complete; one-arm **answer**  
Protocol: [v0924_cheap_stack_luna_dev140_protocol_2026-08-16.md](v0924_cheap_stack_luna_dev140_protocol_2026-08-16.md)  
Parent: [cheap-stack `dev20`](v0924_cheap_stack_luna_dev20_2026-08-16.md)

## Executive result

The cheap stack stays **load_bearing** on the 140 development
letters. Headline and SeizureFrequency stay under their bars. Net
four-family exact losses do not.

| Slice | hybrid | Δ vs control | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `v0.9.24` control | 0.8974 | — | — | 55/140 | — |
| drop_encoding_non_sf_all_examples | 0.8856 | −0.0118 | −0.0465 | 49/140 | **load_bearing** |

140 fresh Luna calls. 0 parse/schema failures. Default remains
`v0.9.24`. Decision 0050 is unchanged.

The family bar that failed on the frozen 20 letters (−0.0929)
shrinks to −0.0465 on the rest of development. The exact bar does
not. Four-family exact is 5 wins and 11 losses (net −6).

The live candidate is the retained slot-2 identity: 67 rules, 0
examples, scaffold kept. That payload is the current cleaned cheap
wording, not a new prompt version.

## Valid evidence

- All 140 loadable ExECT development letters. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off. 16000 tokens.
- Control: saved Luna `v0.9.24` through HEAD. Zero new `v0.9.24` calls.
- Candidate keeps scaffold, the 13 SF encoding rules, and all scope
  rules.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_cheap_stack_luna_dev140_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| `v0.9.24` | 0.8873 | 0.8291 | 0.9505 | 0.9202 |
| cheap stack | 0.8821 | 0.7826 | 0.9507 | 0.9195 |

SeizureFrequency letter-exact falls 99 → 89 (17 losses, 7 wins).
Diagnosis 98 → 95. Prescription 126 → 127. Investigations 125 → 125.
Headline (−0.0118) and every family F1 stay under their bars. The
exact bar is enough.

## Frozen `dev20` overlap

Not the 140-letter result. New live draw of the current cheap
payload on the same 20 letters.

| Slice | hybrid | SF | exact |
| --- | ---: | ---: | ---: |
| `v0.9.24` HEAD replay | 0.9251 | 0.9231 | 10/20 |
| this transfer | 0.8957 | 0.7925 | 9/20 |
| saved cheap-stack `dev20` | 0.9083 | 0.8302 | 9/20 |

Control matches the saved HEAD replay. The overlap still trips the
SeizureFrequency family bar (−0.1306). That is a new draw, not a
replay of the saved cheap-stack raws.

## What this is not

A smaller stack, a new prompt, or a selected-stack change. The
`dev20` SeizureFrequency drop shrinking on `dev140` is still not a
reason to replace `v0.9.24`. Do not start another cheap cut from
this result.

## Decision

**answer.** The stack is **load_bearing** on net four-family exact
losses, so it does not replace `v0.9.24`. It stays the retained
cheap prompt variant (slot 2). Owner:
[prompt variant slots](prompt_variant_slots_2026-08-16.md).

## Claim boundary

GPT-5.6 Luna ExECT development-transfer result on the named `dev140`
letters. It is not a selected prompt, not holdout evidence, and not
a Decision 0050 change.
