# ExECT `v0.9.24` leave-one-out prompt prune — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; four-arm **answer**  
Protocol: [v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md](v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md)

## Executive result

The score in `v0.9.24` is not sitting in the architecture block, the
49 worked examples, or the encoding-rule dump. It is sitting in the
**scope** rules: what to list, what to refuse, and how historical
frequency statements stay in.

| Slice | hybrid | Δ vs control | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `v0.9.24` control | 0.9251 | — | — | 10/20 | — |
| drop_scaffold | 0.9138 | −0.0113 | −0.0385 | 10/20 | **low_value** |
| drop_examples | 0.9043 | −0.0208 | −0.0712 | 8/20 | **low_value** |
| drop_encoding | 0.9115 | −0.0136 | −0.0769 | 9/20 | **low_value** |
| drop_scope | 0.8966 | −0.0285 | **−0.1017** | 7/20 | **load_bearing** |

80 fresh Luna calls. 0 parse/schema failures on every arm. Default
remains `v0.9.24`. Decision 0050 is unchanged.

v10 dropped every slice at once and SeizureFrequency collapsed. That
was not evidence that examples or encoding were the payload. Removing
them one at a time costs about two headline points or less. Removing
scope crosses the predeclared family and exactness bars.

## Valid evidence

- Same frozen 20 development letters as v10–v19. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved `v0.9.24` through HEAD.
- Candidates keep the `v0.9.24` schema and hybrid stack. One named
  slice is removed.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_ablation_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| drop_scaffold | 0.9041 | 0.8846 | 0.9296 | 0.9444 |
| drop_examples | 0.9041 | 0.8519 | 0.9412 | 0.9143 |
| drop_encoding | 0.9041 | 0.8462 | 0.9552 | 0.9412 |
| drop_scope | 0.9041 | 0.8214 | 0.9412 | 0.9143 |

Diagnosis does not move. SeizureFrequency is the only family that
pays for each slice. Scope is the only one that pays enough to trip
the stop rule (family drop ≥ 0.08 or net exact losses ≥ 3). Encoding
is next (−0.0769) and stays under the bar.

## What this is not

A low-value leave-one-out does not prove the slice can be dropped
together with another low-value slice. The follow-on
[cumulative prune](v0924_cumulative_prune_luna_dev20_2026-08-16.md)
found scaffold plus examples **load_bearing**. Keep scope in any
later prune.

## Decision

**answer.** Rank by SeizureFrequency cost: scope > encoding >
examples > scaffold. Only scope is load-bearing on this pool.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not clinical validation, not holdout evidence, and not a Decision
0050 change. A small drop here is not proof the slice is worthless on
`dev140`.
