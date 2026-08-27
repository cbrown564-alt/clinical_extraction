# ExECT `v0.9.24` cumulative prune — GPT-5.6 Luna `dev20`

Date: 2026-08-16  
Status: complete; first-arm **answer**; encoding add-on not run  
Protocol: [leave-one-out family](v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md)  
Parent: [leave-one-out answer](v0924_prompt_ablation_luna_dev20_2026-08-16.md)

## Executive result

Scaffold and examples are cheap **one at a time**. They are not cheap
**together**. Dropping both trips the SeizureFrequency stop bar. The
encoding add-on did not run.

| Slice | hybrid | Δ vs control | SF Δ | exact | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `v0.9.24` control | 0.9251 | — | — | 10/20 | — |
| drop_scaffold (leave-one-out) | 0.9138 | −0.0113 | −0.0385 | 10/20 | low_value |
| drop_examples (leave-one-out) | 0.9043 | −0.0208 | −0.0712 | 8/20 | low_value |
| drop_scaffold_examples | 0.8978 | −0.0273 | **−0.1314** | 9/20 | **load_bearing** |
| drop_scaffold_examples_encoding | — | — | — | — | not run |

20 fresh Luna calls. 0 parse/schema failures. Default remains
`v0.9.24`. Decision 0050 is unchanged.

Leave-one-out said the cheap slices could be stripped later. This
study says they cannot be stripped as a pair. The interaction is on
SeizureFrequency: each parent stayed under the 0.08 family bar;
together they go to **0.7917** (−0.1314). Headline (−0.0273) and net
exact (−1) stay under their bars. The family bar is enough.

If the two cheap drops were independent, SeizureFrequency would land
near 0.8134 (control 0.9231 minus 0.0385 minus 0.0712). The observed
value is 0.7917, about two extra points of interaction.

## Valid evidence

- Same frozen 20 development letters as the leave-one-out. `test60`
  not inspected.
- Model `openai/gpt-5.6-luna`. Temperature 1.0. Cache off.
- Control: saved `v0.9.24` through HEAD.
- Candidate: `v0.9.30_drop_scaffold_examples`. Architecture, decision
  procedure, candidate ledger, lane guide, junk rules 01–04, and the
  49 worked examples are gone. Scope, encoding, hygiene,
  `already_code`, family guidance, schema, and vocabulary stay.

Artifact: [`comparison.json`](../../../experiments/exectv2_v0924_cumulative_prune_luna_dev20_20260816/comparison.json)

## Family context

| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | --- |
| `v0.9.24` | 0.9041 | 0.9231 | 0.9412 | 0.9412 |
| drop_scaffold | 0.9041 | 0.8846 | 0.9296 | 0.9444 |
| drop_examples | 0.9041 | 0.8519 | 0.9412 | 0.9143 |
| drop_scaffold_examples | 0.8767 | **0.7917** | 0.9706 | 0.9444 |

SeizureFrequency letter-exact falls 17 → 13 (five losses, one win).
Raw SeizureFrequency drops further (−0.1591) and raw Diagnosis also
drops (−0.1096). Hybrid repairs some Diagnosis; it does not repair
SeizureFrequency.

## What this is not

A later pairwise of scaffold+encoding or examples+encoding is a new
study. This result does not say which of the two slices is the
interaction partner. It says the pair cannot be dropped. Scope stays.
Do not start `dev140` from this result.

## Decision

**answer.** Stop. Do not add encoding. The cheap slices interact.
Keep `v0.9.24` as the default. The follow-on
[scope-cluster prune](v0924_scope_cluster_luna_dev20_2026-08-16.md)
found both SeizureFrequency scope jobs load-bearing.

## Claim boundary

GPT-5.6 Luna ExECT development result on the named `dev20` sample. It
is not a selected prompt, not holdout evidence, and not a Decision
0050 change.
