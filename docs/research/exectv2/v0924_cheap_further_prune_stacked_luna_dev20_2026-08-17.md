# ExECT cheap-stack stacked further prune — GPT-5.6 Luna `dev20`

Date: 2026-08-17  
Status: complete; stacked arm **low_value**  
Protocol: [v0924_cheap_further_prune_stacked_luna_dev20_protocol_2026-08-17.md](v0924_cheap_further_prune_stacked_luna_dev20_protocol_2026-08-17.md)  
Parent: [one-at-a-time further prune](v0924_cheap_further_prune_luna_dev20_2026-08-16.md)

## Executive result

The three low_value cheap-stack choruses are applied together.
Default remains `v0.9.24`. Slot 2 remains `v0.9.40`.
Decision 0050 is unchanged.

| Arm | hybrid | Δ vs cheap | SF | SF Δ | exact |
| --- | ---: | ---: | ---: | ---: | ---: |
| cleaned cheap | 0.8996 | — | 0.8302 | — | 9/20 |
| `v0.9.24` | 0.9251 | — | 0.9231 | — | 10/20 |
| investigation pending collapse | 0.8947 | — | 0.8462 | — | 8/20 |
| scaffold reprint drop | 0.9211 | — | 0.8846 | — | 11/20 |
| refuse chorus collapse | 0.8929 | — | 0.8163 | — | 9/20 |
| stacked further prune | 0.9043 | +0.0047 | 0.8148 | -0.0154 | 11/20 |

20 fresh Luna calls. parse=0 schema=0. Verdict versus cleaned cheap: **low_value**.

Versus `v0.9.24`: headline −0.0208, SeizureFrequency −0.1083, exact net +1.

Versus scaffold-reprint one-cut: headline −0.0168, SeizureFrequency −0.0698, exact net 0.

The stack stays under the cheap-stack bars and matches the scaffold
one-cut on exact (11/20). It does not keep that one-cut's
SeizureFrequency bump (0.8846 → 0.8148). Diagnosis lands between the
refuse one-cut and the cleaned cheap stack. That is a 20-letter
observation, not a slot-2 change.

## Valid evidence

- Same frozen 20 development letters. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved cleaned cheap stack through HEAD.
- One-cut arms: saved further-prune raws through HEAD.
- Secondary: saved `v0.9.24` through HEAD.
- Candidate: live stacked further prune.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_cheap_further_prune_stacked_luna_dev20_20260817/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| cleaned cheap | 0.9041 | 0.8302 | 0.9412 | 0.9143 |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| investigation pending collapse | 0.8767 | 0.8462 | 0.9412 | 0.9143 |
| scaffold reprint drop | 0.9041 | 0.8846 | 0.9565 | 0.9412 |
| refuse chorus collapse | 0.8493 | 0.8163 | 0.9706 | 0.9412 |
| stacked further prune | 0.8919 | 0.8148 | 0.9706 | 0.9412 |

## Decision

**low_value** versus cleaned cheap (headline +0.0047, exact net +2). Live default stays `v0.9.24`. Slot 2 stays `v0.9.40`. Do not start `dev140` from this result.

## Claim boundary

ExECTv2 Luna 20-letter development study of the stacked further cheap-stack cuts versus the cleaned cheap stack. Not holdout, not a selected prompt, not a slot-2 change, and not a Decision 0050 change.
