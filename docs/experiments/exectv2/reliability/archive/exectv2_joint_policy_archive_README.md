# Archived: ExECT joint (`combined`/`combined`) Diagnosis/Prescription policy

Date archived: 2026-07-31  
Governing decision: [0045](../../../decisions/0045-exect-default-policy-not-joint-combined.md)

## Status

**Not for active comparison use.** The live ExECT assembly policy is
`default` / `default`.

Joint bounded (`combined` / `combined`) was selected on 2026-07-15 as a
disclosed fallback over an earlier model-preserving bundle, then demoted on
2026-07-31 because six-model matched gains were marginal for the added
complexity, and the retained panel was already scored under default.

## Find these materials

| Artifact | Path |
| --- | --- |
| Original joint selection result | [`../exectv2_joint_bounded_policy_replay_2026-07-15.md`](../exectv2_joint_bounded_policy_replay_2026-07-15.md) |
| Original joint selection protocol | [`../exectv2_joint_bounded_policy_replay_protocol_2026-07-15.md`](../exectv2_joint_bounded_policy_replay_protocol_2026-07-15.md) |
| Six-model default-vs-joint no-call replay | [`../exectv2_six_model_joint_policy_replay_2026-07-31.md`](../exectv2_six_model_joint_policy_replay_2026-07-31.md) |
| Machine panel | [`../../../../experiments/exectv2_six_model_joint_policy_replay_20260731/panel_summary.json`](../../../../experiments/exectv2_six_model_joint_policy_replay_20260731/panel_summary.json) |
| Historical check script | `scripts/check_exectv2_joint_bounded_policy_replay.py` |
| Opt-in six-model replay | `scripts/run_exectv2_six_model_joint_policy_replay.py --allow-archived-joint-policy` |

## How to replay (explicit opt-in only)

```powershell
.venv\Scripts\python.exe scripts/run_exectv2_six_model_joint_policy_replay.py --allow-archived-joint-policy
```

Do not wire `combined` into new Luna, six-model, or paper configs.
