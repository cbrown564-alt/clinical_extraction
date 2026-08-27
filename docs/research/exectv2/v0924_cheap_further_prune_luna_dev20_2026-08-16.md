# ExECT cheap-stack further prune — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; three independent **low_value** answers  
Protocol: [v0924_cheap_further_prune_luna_dev20_protocol_2026-08-16.md](v0924_cheap_further_prune_luna_dev20_protocol_2026-08-16.md)  
Parent: [cleaned cheap remasure](v0924_cheap_stack_plain_luna_dev20_2026-08-16.md)

## Executive result

Each arm is one further cut of the cleaned cheap stack, scored
against that stack. Default remains `v0.9.24`. Slot 2 remains
`v0.9.40`. Decision 0050 is unchanged.

| Arm | hybrid | Δ vs cheap | SF | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| cleaned cheap | 0.8996 | — | 0.8302 | — | 9/20 | control |
| `v0.9.24` | 0.9251 | — | 0.9231 | — | 10/20 | secondary |
| investigation pending collapse | 0.8947 | −0.0049 | 0.8462 | +0.0160 | 8/20 | **low_value** |
| scaffold reprint drop | 0.9211 | +0.0215 | 0.8846 | +0.0544 | 11/20 | **low_value** |
| refuse chorus collapse | 0.8929 | −0.0067 | 0.8163 | −0.0139 | 9/20 | **low_value** |

60 fresh Luna calls. parse=0 schema=0 on every arm. Primary verdicts
are versus the cleaned cheap stack.

## What moved

The investigation-pending chorus was not carrying Investigations on
this pool. Investigations F1 stayed 0.9143. The only four-family exact
loss versus cheap was EA0008 (SeizureFrequency). Diagnosis F1 dipped
(−0.0274) without crossing a stop bar.

Dropping the four-layer scaffold reprint did not damage the cheap
stack. SeizureFrequency rose +0.0544 and exact went 9/20 → 11/20.
Versus `v0.9.24` this arm is close on headline (−0.0040) and still
short on SeizureFrequency (−0.0385). That is a 20-letter observation,
not a selected-stack change.

Collapsing the ten Diagnosis/SeizureFrequency refuse restatements into
one rule stayed under the bars. Diagnosis was the sore point
(−0.0548, still under 0.08). Exact wins and losses cancelled. Versus
`v0.9.24`, SeizureFrequency is −0.1068; that restates the cheap
stack's existing SF cost, not a new refuse-only failure.

EA0004 and EA0010 remain contamination letters. They were not used to
retune.

## Valid evidence

- Same frozen 20 development letters. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved cleaned cheap stack through HEAD.
- Secondary: saved `v0.9.24` through HEAD.
- Each candidate is one live further cut. The three cuts were not stacked.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_cheap_further_prune_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| cleaned cheap | 0.9041 | 0.8302 | 0.9412 | 0.9143 |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| investigation pending collapse | 0.8767 | 0.8462 | 0.9412 | 0.9143 |
| scaffold reprint drop | 0.9041 | 0.8846 | 0.9565 | 0.9412 |
| refuse chorus collapse | 0.8493 | 0.8163 | 0.9706 | 0.9412 |

## Decision

**investigation pending collapse: low_value** versus cleaned cheap
(headline −0.0049, exact net −1). Versus `v0.9.24`: headline −0.0304,
SF −0.0769, exact net −2.

**scaffold reprint drop: low_value** versus cleaned cheap (headline
+0.0215, exact net +2). Versus `v0.9.24`: headline −0.0040, SF
−0.0385, exact net +1.

**refuse chorus collapse: low_value** versus cleaned cheap (headline
−0.0067, exact net 0). Versus `v0.9.24`: headline −0.0322, SF
−0.1068, exact net −1.

None of these choruses is still required inside the cheap stack on
this pool. That is not permission to fold them into slot 2, stack
them, or start `dev140`. Live default stays `v0.9.24`. Slot 2 stays
`v0.9.40`.

## Claim boundary

ExECTv2 Luna 20-letter development study of one further cheap-stack
cut versus the cleaned cheap stack. Not holdout, not a selected
prompt, not a slot-2 change, and not a Decision 0050 change.
