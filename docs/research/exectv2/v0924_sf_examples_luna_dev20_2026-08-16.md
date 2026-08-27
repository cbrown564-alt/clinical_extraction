# ExECT `v0.9.24` SeizureFrequency example split — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; two-arm **answer**  
Protocol: [leave-one-out family](v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md)  
Parent: [non-SF answer](v0924_non_sf_slice_luna_dev20_2026-08-16.md)

## Executive result

Both remaining SeizureFrequency example jobs are **low_value**. The
13 encoding teachers and the 10 scope-refuse demos can each come out
without tripping the stop bars.

| Slice | hybrid | Δ vs control | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `v0.9.24` control | 0.9251 | — | — | 10/20 | — |
| drop all 49 examples | 0.9043 | −0.0208 | −0.0712 | 8/20 | low_value |
| drop 26 non-SF examples | 0.9123 | −0.0128 | −0.0385 | 10/20 | low_value |
| drop_examples_sf_encoding | 0.9163 | −0.0088 | −0.0552 | 8/20 | **low_value** |
| drop_examples_sf_scope | 0.9123 | −0.0128 | −0.0342 | 8/20 | **low_value** |

40 fresh Luna calls. 0 parse/schema failures. Default remains
`v0.9.24`. Decision 0050 is unchanged.

Every named example cluster is now cheap alone, and dropping all 49
examples was already cheap. Scaffold plus examples is still
load-bearing. The examples dump is not the score until it is paired
with the architecture block.

## Valid evidence

- Same frozen 20 development letters. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved `v0.9.24` through HEAD.
- Each arm drops one SF example cluster. Rules and the other examples
  stay.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_sf_examples_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| drop_examples_sf_encoding | 0.9189 | 0.8679 | 0.9394 | 0.9412 |
| drop_examples_sf_scope | 0.9041 | 0.8889 | 0.9254 | 0.9412 |

If the two SF example clusters were independent they would sum past
the 0.08 family bar. The full 49-example drop does not. They do not
add.

## What this is not

Stacking example clusters with scaffold is already answered:
load_bearing. A later split of the 13 encoding examples is not
needed to decide a cut. Do not start `dev140` from this result.

## Decision

**answer.** Both SF example clusters are low_value. Keep `v0.9.24`
as the default. The remaining example question is only whether to
drop them in a named shorter candidate that still keeps scaffold.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
