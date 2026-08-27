# ExECT `v0.9.24` cheap-slice stack — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; one-arm **answer**  
Protocol: [v0924_cheap_stack_luna_dev20_protocol_2026-08-16.md](v0924_cheap_stack_luna_dev20_protocol_2026-08-16.md)  
Parent: [SF-example split](v0924_sf_examples_luna_dev20_2026-08-16.md)

## Executive result

The four cheap cuts do not stay cheap together. Dropping the 16
non-SF encoding rules and all 49 examples trips the SeizureFrequency
stop bar. Scaffold stayed in.

| Slice | hybrid | Δ vs control | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `v0.9.24` control | 0.9251 | — | — | 10/20 | — |
| drop non-SF encoding | 0.8996 | −0.0255 | −0.0712 | 9/20 | low_value |
| drop all examples | 0.9043 | −0.0208 | −0.0712 | 8/20 | low_value |
| drop_encoding_non_sf_all_examples | 0.9083 | −0.0168 | **−0.0929** | 9/20 | **load_bearing** |

20 fresh Luna calls. 0 parse/schema failures. Default remains
`v0.9.24`. Decision 0050 is unchanged.

On EA0133 the stacked payload is **27,564** characters (−30,818,
**−53%**). Headline barely moves. SeizureFrequency does not.

If the two parents were independent, SeizureFrequency would fall by
about 0.14. The stack falls by 0.0929. They interact, and the
interaction is enough to cross 0.08.

## Valid evidence

- Same frozen 20 development letters. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved `v0.9.24` through HEAD.
- Candidate keeps scaffold, the 13 SF encoding rules, and all scope
  rules.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| cheap stack | 0.8889 | **0.8302** | 0.9565 | 0.9714 |

SeizureFrequency letter-exact falls 17 → 13. Prescription and
Investigations rise. Headline (−0.0168) and net exact (−1) stay under
their bars. The family bar is enough.

## What this is not

A smaller stack — non-SF encoding plus only the 26 non-SF examples,
or all examples without the encoding cut — is a new study. Scaffold
plus examples is already load-bearing and was not repeated. Do not
start `dev140` from this result.

## Decision

**answer.** The stack is **load_bearing** on SeizureFrequency, so it
does not replace `v0.9.24`. It is the retained cheap prompt variant
(slot 2). Owner:
[prompt variant slots](prompt_variant_slots_2026-08-16.md).
Do not start `dev140` from this result.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
