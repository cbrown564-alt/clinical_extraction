# Qwen Dev140 Model-Preserving Replay Summary

Date: 2026-06-23

This note summarizes no-call finding-assembly replays for Qwen dev140 variants
using the current assembly runner's materialized
`protocol_model_preserving_canonical` surface. The replay is structural over
frozen JSONL source artifacts and introduces no live model calls.

Important scoring note: this replay surface is stricter than the hand-written
`model_preserving_canonical` attribution table in
`qwen_protocol_clean_attribution_2026-06-23.md`. In particular,
`v0924_qwencompact_schemaoperand` is `0.6688` on the runner-materialized
`protocol_model_preserving_canonical` surface, while the attribution readout
listed `0.7821` after additional allowed schema/operand accounting. Treat the
numbers below as the current no-call replay surface, not the earlier attribution
table dialect.

## Results

| Candidate | Class | protocol_model_preserving_canonical F1 | P | R | TP | FP | FN | Diagnosis | SeizureFrequency | Prescription | Investigations | Headline F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140` | candidate-backed relaxed selector | 0.8872 | 0.8750 | 0.8997 | 718 | 102 | 80 | 0.9090 | 0.7814 | 0.9357 | 0.9132 | 0.9091 |
| `exectv2_holistic_finding_assembly_v05_qwen_strict_actions_dev140` | candidate-backed strict selector | 0.8684 | 0.8708 | 0.8659 | 691 | 101 | 107 | 0.8795 | 0.7781 | 0.9247 | 0.8880 | 0.9020 |
| `exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140` | direct compact/schemaoperand | 0.6688 | 0.6564 | 0.6817 | 544 | 279 | 254 | 0.6533 | 0.4306 | 0.8405 | 0.7630 | 0.8483 |
| `exectv2_holistic_finding_assembly_v0910_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0911_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0912_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0913_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0914_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0915_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0916_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0917_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0918_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0919_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0920_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0921_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | direct compact residual-repair replay | 0.6406 | 0.6433 | 0.6378 | 509 | 265 | 289 | 0.6109 | 0.3733 | 0.8786 | 0.7176 | 0.8973 |

## Interpretation

- The best replay-generated model-preserving Qwen dev140 score is the
  candidate-backed relaxed action replay at `0.8872`, but it is a hybrid
  selector diagnostic rather than direct Qwen extraction.
- The best direct compact Qwen dev140 replay is
  `v0924_qwencompact_schemaoperand` at `0.6688`.
- The `v0910` through `v0922` residual-repair manifests all collapse to the
  same model-preserving replay value, because they point to the same frozen
  `v0910_qwencompact` source JSONL and the current replay surface preserves the
  source-scored fact inventory before deterministic residual additions.
- The high historical headline values for the residual-repair line are not
  model-preserving direct extraction scores; they are full/clinical headline
  surfaces that include deterministic rescue behavior.

## Replay Artifacts

Each candidate has fresh no-call replay artifacts under:

`experiments/<candidate>_modelpreserving_replay_20260623.{json,jsonl,md}`

