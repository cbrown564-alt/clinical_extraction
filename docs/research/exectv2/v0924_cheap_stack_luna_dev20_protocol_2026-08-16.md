# Protocol: ExECT `v0.9.24` cheap-slice stack

Date: 2026-08-16  
Status: **complete**; stack load_bearing  
Parent: [SF-example split](v0924_sf_examples_luna_dev20_2026-08-16.md)

Non-SF encoding, non-SF examples, SF encoding examples, and SF
scope examples were each cheap alone. This study stacks those four
cuts as one candidate: drop the 16 non-SF encoding rules and all 49
examples. Scaffold and both SF scope rule clusters stay. `v0.9.24`
stays the default. `test60` is sealed.

## Primary question

On the same frozen 20-letter Luna pool, does the stacked cheap cut
stay under the leave-one-out stop bars versus saved `v0.9.24`?

This is not scaffold plus examples. That pair is already
load-bearing.

## Arms

| Arm | Prompt | Drop | Keep |
| --- | --- | --- | --- |
| `v0924_head` | saved `v0.9.24` through HEAD | none | all |
| `drop_encoding_non_sf_all_examples` | `v0.9.40_drop_encoding_non_sf_all_examples` | 16 diagnosis/Rx/Ix encoding rules; all 49 examples | scaffold; 13 SF encoding rules; all scope rules |

## Data and scoring

Same frozen `dev20`, model, scorer, and stop bars. Compare to saved
`v0.9.24`. No `dev140`.

## Stop rule

Same bars. `revise` if parse/schema failures appear. Do not promote.
Do not change the default.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
