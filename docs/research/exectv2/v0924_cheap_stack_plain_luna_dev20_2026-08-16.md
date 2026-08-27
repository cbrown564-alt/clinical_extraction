# ExECT cheap-stack plain-language remasure — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; one-arm **load_bearing**  
Protocol: [v0924_cheap_stack_plain_luna_dev20_protocol_2026-08-16.md](v0924_cheap_stack_plain_luna_dev20_protocol_2026-08-16.md)  
Parent: [cheap-stack structural cut](v0924_cheap_stack_luna_dev20_2026-08-16.md)

## Executive result

Cleaning the leftover research language did not recover the cheap
stack's SeizureFrequency cost. Versus saved `v0.9.24`, hybrid
headline is −0.0255 and SeizureFrequency is **−0.0929**. That is the
same family-bar trip as the structural cut. Default remains
`v0.9.24`. Decision 0050 is unchanged.

| Arm | hybrid | Δ vs `v0.9.24` | SF | SF Δ | exact |
| --- | ---: | ---: | ---: | ---: | ---: |
| `v0.9.24` control | 0.9251 | — | 0.9231 | — | 10/20 |
| previous cheap | 0.9083 | — | 0.8302 | — | 9/20 |
| plain cheap | 0.8996 | −0.0255 | **0.8302** | **−0.0929** | 9/20 |

20 fresh Luna calls. parse=0 schema=0. Verdict versus `v0.9.24`:
**load_bearing**.

Versus the pre-cleanup cheap stack: headline −0.0087;
SeizureFrequency **+0.0000**; exact net 0. The language pass moved
Diagnosis, Prescription, and Investigations a little. It did not
move SeizureFrequency F1.

## Valid evidence

- Same frozen 20 development letters. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved `v0.9.24` through HEAD.
- Previous cheap: saved pre-cleanup cheap raws through HEAD.
- Candidate: live cleaned cheap stack. Dirty tree at
  `47ca4f88`.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| previous cheap | 0.8889 | 0.8302 | 0.9565 | 0.9714 |
| plain cheap | 0.9041 | **0.8302** | 0.9412 | 0.9143 |

Versus `v0.9.24`, SeizureFrequency letter-exact loses 4 and wins 0
(EA0009, EA0010, EA0133, EA0158). Four-family exact is 1 win
(EA0005) and 2 losses (EA0010, EA0120). Headline and net exact stay
under their bars. The family bar is enough.

Versus the previous cheap wording, SeizureFrequency letter-exact is
2 wins and 2 losses. Investigations F1 falls 0.0571. That is under
the 0.08 family bar and is not a reason to put the jargon back.

EA0004 and EA0010 are the contamination letters. EA0010 is one of
the four SeizureFrequency exact losses versus `v0.9.24`. EA0004 does
not flip.

## Decision

**load_bearing.** The cleaned cheap stack stays the retained cheap
variant. Live default stays `v0.9.24`. Do not start `dev140` from
this result. The earlier
[cheap-stack `dev140`](v0924_cheap_stack_luna_dev140_protocol_2026-08-16.md)
authorization was for the pre-cleanup wording and is not this study.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
