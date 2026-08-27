# ExECT `v0.9.24` non-SF encoding and example prune — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; two-arm **answer**  
Protocol: [leave-one-out family](v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md)  
Parent: [scope-cluster answer](v0924_scope_cluster_luna_dev20_2026-08-16.md)

## Executive result

The non-SF pages of encoding and examples are **low_value**. The
SeizureFrequency bill in those dumps is not sitting in diagnosis
headings, hygiene demos, or Rx/Ix teachers.

| Slice | hybrid | Δ vs control | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `v0.9.24` control | 0.9251 | — | — | 10/20 | — |
| drop all encoding | 0.9115 | −0.0136 | −0.0769 | 9/20 | low_value |
| drop_encoding_non_sf | 0.8996 | −0.0255 | −0.0712 | 9/20 | **low_value** |
| drop all examples | 0.9043 | −0.0208 | −0.0712 | 8/20 | low_value |
| drop_examples_non_sf | 0.9123 | −0.0128 | −0.0385 | 10/20 | **low_value** |

40 fresh Luna calls. 0 parse/schema failures. Default remains
`v0.9.24`. Decision 0050 is unchanged.

Non-SF encoding is 16 rules (~4k). Non-SF examples are 26 items
(~16k, about 28% of the EA0133 payload). Each arm stayed under the
headline, family, and exactness bars. They were not scored together.

## Valid evidence

- Same frozen 20 development letters. `test60` not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved `v0.9.24` through HEAD.
- `drop_encoding_non_sf` keeps the 13 SF encoding rules and all 49
  examples.
- `drop_examples_non_sf` keeps the 13 SF encoding examples and the 10
  SF scope examples.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_non_sf_slice_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| drop_encoding_non_sf | 0.8767 | 0.8519 | 0.9412 | 0.9412 |
| drop_examples_non_sf | 0.8767 | 0.8846 | 0.9706 | 0.9143 |

Diagnosis moves a little on both arms and does not trip the bar.
SeizureFrequency still pays something for non-SF encoding (−0.0712),
almost as much as dropping every encoding rule (−0.0769). That is
not proof the 13 SF encoding rules are free. It is proof the 16
non-SF encoding rules can come out without crossing the stop rule.

## What this is not

Stacking both cheap arms, or stacking either with scaffold, is a new
study. A later split of the kept 23 SF examples is a new study. Do
not start `dev140` from this result.

## Decision

**answer.** Non-SF encoding and non-SF examples are each low_value.
Keep the 13 SF encoding rules and the 23 SF examples until a later
split says otherwise. Keep `v0.9.24` as the default.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
