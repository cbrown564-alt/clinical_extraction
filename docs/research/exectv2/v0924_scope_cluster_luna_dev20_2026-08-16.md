# ExECT `v0.9.24` scope-cluster prune — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; four-arm **answer**  
Protocol: [leave-one-out family](v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md)  
Parent: [cumulative answer](v0924_cumulative_prune_luna_dev20_2026-08-16.md)

## Executive result

The scope score is two SeizureFrequency jobs, not one dump. Dropping
either the refuse cluster or the keep cluster trips the family stop
bar. Diagnosis scope and Prescription/Investigations scope do not.

| Slice | hybrid | Δ vs control | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `v0.9.24` control | 0.9251 | — | — | 10/20 | — |
| drop_scope (all 25) | 0.8966 | −0.0285 | −0.1017 | 7/20 | load_bearing |
| drop_scope_sf_refuse | 0.8899 | −0.0352 | **−0.0929** | 8/20 | **load_bearing** |
| drop_scope_sf_keep | 0.9035 | −0.0216 | **−0.0867** | 8/20 | **load_bearing** |
| drop_scope_diagnosis | 0.9163 | −0.0088 | −0.0385 | 10/20 | **low_value** |
| drop_scope_rx_ix | 0.9083 | −0.0168 | −0.0174 | 9/20 | **low_value** |

80 fresh Luna calls. 0 parse/schema failures. Default remains
`v0.9.24`. Decision 0050 is unchanged.

The two SeizureFrequency clusters do not add. If they were
independent, SeizureFrequency would fall by about 0.18. The full
25-rule drop falls by 0.1017. Each cluster is almost the whole scope
cost by itself.

## Valid evidence

- Same frozen 20 development letters as the leave-one-out. `test60`
  not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved `v0.9.24` through HEAD.
- Candidates keep scaffold, examples, encoding, hygiene, and
  `already_code`. One named scope cluster is removed.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_scope_cluster_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| drop_scope_sf_refuse | 0.8767 | **0.8302** | 0.9254 | 0.9412 |
| drop_scope_sf_keep | 0.9041 | **0.8364** | 0.9394 | 0.9412 |
| drop_scope_diagnosis | 0.8919 | 0.8846 | 0.9412 | 0.9697 |
| drop_scope_rx_ix | 0.8767 | 0.9057 | 0.9412 | 0.9143 |

Refuse is “do not list NES, generic events, childhood/family, risk, or
advice as SeizureFrequency.” Keep is “onset-history, last-event, and
bare seizure-free need a type or time frame.” Both are required. The
other families’ scope rules are cheap on this pool.

## What this is not

A later split of the 11 SeizureFrequency scope rules is a new study.
This result does not say which refuse rule or which keep rule is the
payload. It says both jobs stay. Do not start `dev140` from this
result.

## Decision

**answer.** Rank by SeizureFrequency cost: SF refuse ≈ SF keep >
diagnosis scope > Rx/Ix scope. Only the two SeizureFrequency clusters
are load-bearing. Keep `v0.9.24` as the default.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
