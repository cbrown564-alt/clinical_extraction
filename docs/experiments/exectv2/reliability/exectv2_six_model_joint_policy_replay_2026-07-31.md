# ExECTv2 six-model joint-policy no-call replay result

Date: 2026-07-31  
Status: answered; **archived readout** — active ExECT policy is `default` /
`default` ([decision 0045](../../../decisions/0045-exect-default-policy-not-joint-combined.md));
see [archive index](archive/exectv2_joint_policy_archive_README.md)  
Protocol:
[exectv2_six_model_joint_policy_replay_protocol_2026-07-31.md](exectv2_six_model_joint_policy_replay_protocol_2026-07-31.md)  
Machine panel:
[`experiments/exectv2_six_model_joint_policy_replay_20260731/panel_summary.json`](../../../../experiments/exectv2_six_model_joint_policy_replay_20260731/panel_summary.json)

## Answer

Under the fixed decision-0041 one-call producers, reassembly with the selected
joint bounded Diagnosis/Prescription policy (`combined` / `combined`) raises
overall `clinical_headline` F1 for every model on both `dev140` and aggregate-only
`test60`. Seizure Frequency and Investigations F1 are unchanged (policy does not
touch those families). The six-model rank order is unchanged on both splits.
Default reassembly reproduced every retained panel cell within the predeclared
tolerance (`0.0005`).

The historical six-model table remains the **default-policy** panel. Joint
figures below are a matched no-call reassembly, not a replacement of those
artifact hashes.

## Fixed conditions

- Models: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, DeepSeek V4 Flash,
  Qwen 3.6:35B, Gemma 4 26B.
- Architecture: decision 0040/0041 single-call.
- Producers: saved structured + SF unknown-suppression artifacts only.
- Call mode: **zero new model calls**.
- Policies: `default`/`default` versus joint `combined`/`combined`.
- Scorer: `clinical_headline`.
- Sol `test60`: canonical credit-restart producers under
  `scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol/` (not the incomplete
  first-attempt Sol root).
- `test60`: aggregate-only; no sealed rows inspected.

## Gate result

| Gate | Result |
| --- | --- |
| Default reassembly matches retained panel (all 6 × 2) | pass |
| New model calls | 0 |
| Rank order change under joint | none on either split |

## Overall F1

### Development (`dev140`)

| Model | Default | Joint | Δ |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol | 0.8920 | 0.9033 | +0.0113 |
| GPT-5.6 Luna | 0.8832 | 0.9006 | +0.0174 |
| DeepSeek V4 Flash | 0.8767 | 0.8899 | +0.0132 |
| Qwen 3.6:35B | 0.8571 | 0.8682 | +0.0111 |
| GPT-4.1-mini | 0.8202 | 0.8337 | +0.0135 |
| Gemma 4 26B | 0.8016 | 0.8100 | +0.0084 |

### Locked test (`test60`, aggregate-only)

| Model | Default | Joint | Δ |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol | 0.8047 | 0.8198 | +0.0151 |
| GPT-5.6 Luna | 0.7950 | 0.8141 | +0.0191 |
| DeepSeek V4 Flash | 0.7881 | 0.8052 | +0.0171 |
| Qwen 3.6:35B | 0.7872 | 0.8030 | +0.0158 |
| GPT-4.1-mini | 0.7572 | 0.7697 | +0.0125 |
| Gemma 4 26B | 0.7169 | 0.7384 | +0.0215 |

Joint lifts are driven by Diagnosis and Prescription. SF and Investigations
deltas are `0.0000` for every model on both splits.

## Mechanism (development only)

On `dev140`, family deltas are Diagnosis `+0.011` to `+0.018` and Prescription
`+0.015` to `+0.043`. That matches the earlier three-model joint-policy selection
and the Luna residual map: joint helps Dx/Rx assembly; SF remains model-owned.

## Claim boundary

No-call ExECTv2 policy-reassembly evidence for the named saved producers under
default versus joint bounded Diagnosis/Prescription. Not a prompt change, not
clinical validation, and not automatic erasure of the historical default-panel
provenance. `test60` remains aggregate-only.

## Relation to Luna A/B/C

Luna variant A under joint (`0.9006` / `0.8141`) matches this six-model joint
cell for Luna. Those figures must not be pasted into the historical default
panel without this matched six-model disclosure.
