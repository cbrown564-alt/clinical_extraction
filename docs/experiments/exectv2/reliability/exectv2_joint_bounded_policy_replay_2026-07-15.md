# ExECTv2 joint bounded-policy replay result

Date: 2026-07-15  
**Status: archived historical evidence (2026-07-31).** Active comparison uses
`default` / `default` per
[decision 0045](../../../decisions/0045-exect-default-policy-not-joint-combined.md).
Archive index:
[archive/exectv2_joint_policy_archive_README.md](archive/exectv2_joint_policy_archive_README.md).

Decision (historical): select the joint bounded policy over the implemented
model-preserving fallback

## Answer

The frozen joint policy is the better fallback for the fixed model comparison.
It reproduces the separately evaluated Diagnosis and Prescription components
exactly, introduces no cross-family interaction, and passes every predeclared
joint gate.

Across the three saved dev140 model outputs, the joint policy produces 172
wrong-to-correct changes, 3 correct-to-wrong changes, and 108 changed-still-wrong
rows. The previous implemented fallback produced 161, 9, and 108. The joint
policy retains 153 of the current policy's 160 rescues; the previous fallback
retained 143. It improves 17 rows that the old fallback leaves wrong and makes
zero fallback-correct rows wrong.

The selected policy identifier is
`decision_0040_joint_bounded_dev140_v1`. This is a development policy decision,
not holdout validation. No test60 row was assembled or inspected, and no model
was called.

## Fixed comparison

- Dataset and split: ExECTv2 dev140, with permitted row inspection.
- Inputs: saved GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6 35B repair
  v02 outputs.
- Current comparator: default decision-0040 model-led policy.
- Previous fallback: `decision_0040_model_preserving_dev140_v1`.
- Joint candidate: combined Diagnosis guards plus bounded Prescription policy.
- Fixed: model-owned producer outputs, Seizure Frequency, Investigations, gold,
  evidence validation, and scorers.
- Primary scorer: family-local `clinical_headline_unit_keys`.

## Gate result

| Gate | Result |
|---|---:|
| Joint Diagnosis equals separate Diagnosis candidate | pass |
| Joint Prescription equals separate Prescription candidate | pass |
| SF and Investigations equal current policy | pass |
| Component direction counts reproduce separate studies | pass |
| Total wrong-to-correct at least 172 | pass: 172 |
| Total correct-to-wrong at most 3 | pass: 3 |
| Retain at least 150 of 160 current-policy rescues | pass: 153 |
| Lost rescues match the seven predeclared identities | pass: 7/7 |
| Retain all four demonstrated Prescription rescue rows | pass |
| Direction counts dominate previous fallback | pass |
| Rescue retention exceeds previous fallback | pass: 153 versus 143 |
| Every current-versus-joint change has exact evidence | pass: 81/81 |
| Every model's overall, Diagnosis, and Prescription F1 is no worse | pass |
| No new call, parse/schema, or fallback failure | pass |

## Full component comparison

| Family | Policy | Wrong to correct | Correct to wrong | Changed, still wrong | Current rescues retained |
|---|---|---:|---:|---:|---:|
| Diagnosis | Current | 81 | 18 | 82 | 81/81 |
| Diagnosis | Previous fallback | 88 | 3 | 78 | 75/81 |
| Diagnosis | **Joint** | **88** | **3** | **78** | **75/81** |
| Prescription | Current | 41 | 23 | 16 | 41/41 |
| Prescription | Previous fallback | 35 | 6 | 10 | 30/41 |
| Prescription | **Joint** | **46** | **0** | **10** | **40/41** |
| Seizure Frequency | All three policies | 38 | 0 | 20 | 38/38 |
| Investigations | All three policies | 0 | 0 | 0 | not applicable |
| **Total** | Current | **160** | **41** | **118** | **160/160** |
| **Total** | Previous fallback | **161** | **9** | **108** | **143/160** |
| **Total** | **Joint** | **172** | **3** | **108** | **153/160** |

The joint result is the exact composition of the two separate candidates. The
Diagnosis map matches the Diagnosis-only assembly for every prediction-changing
model/family/letter row; the Prescription map matches the Prescription-only
assembly; SF and Investigations match the current policy.

## Per-model scores

| Saved model | Policy | Overall F1 | Diagnosis F1 | Prescription F1 | SF F1 | Investigations F1 |
|---|---|---:|---:|---:|---:|---:|
| Historical DeepSeek | Current | 0.8747 | 0.8892 | 0.9268 | 0.7635 | 0.9091 |
|  | Previous fallback | 0.8819 | 0.9037 | 0.9343 | 0.7635 | 0.9091 |
|  | **Joint** | **0.8889** | **0.9037** | **0.9614** | **0.7635** | **0.9091** |
| GPT-4.1-mini | Current | 0.8378 | 0.8727 | 0.8867 | 0.7018 | 0.8583 |
|  | Previous fallback | 0.8440 | 0.8846 | 0.8949 | 0.7018 | 0.8583 |
|  | **Joint** | **0.8503** | **0.8846** | **0.9193** | **0.7018** | **0.8583** |
| Qwen 3.6 35B repair v02 | Current | 0.8565 | 0.8653 | 0.9481 | 0.7193 | 0.8718 |
|  | Previous fallback | 0.8618 | 0.8793 | 0.9484 | 0.7193 | 0.8718 |
|  | **Joint** | **0.8667** | **0.8793** | **0.9681** | **0.7193** | **0.8718** |

## Row-level comparison with the old fallback

The joint and previous fallback differ on 22 model/family rows:

| Previous fallback correct | Joint correct | Rows |
|---|---|---:|
| No | Yes | 17 |
| No | No | 5 |
| Yes | No | 0 |

The joint policy therefore Pareto-dominates the old fallback at the row-correctness
level on this development distribution: it adds correct rows without losing a
row the fallback got right.

## Remaining failures and ownership

The joint selection does not erase the known component caveats:

- Diagnosis loses six current-policy rescues on EA0082 and EA0126 under all
  three models.
- Prescription loses the EA0141/Qwen current-policy rescue because the bounded
  current guard preserves a future Lamotrigine target.
- The three remaining model-correct regressions are the EA0117 Diagnosis
  synonym residual under all three models. Deterministic residual recovery adds
  `focal seizures with altered awareness` beside the model-owned `focal impaired
  awareness seizures`.

All seven lost current-policy rescues and all 81 current-versus-joint changed
rows have exact evidence. These are deterministic clinical-selection effects;
the final facts remain hybrid and are not credited entirely to the model.

## Decision and next action

Use `decision_0040_joint_bounded_dev140_v1` as the disclosed fallback policy for
the fixed six-model comparison. Retire the previous bundled fallback from that
role, but retain its report as historical development evidence.

Any six-model row produced before this joint decision must record its actual
policy. It cannot be presented as a joint-policy result unless replayed or
rerun through the selected joint assembly. Do not inspect test60 failures or
tune another deterministic exception.

## Artifacts

- Protocol: `docs/experiments/exectv2/reliability/exectv2_joint_bounded_policy_replay_protocol_2026-07-15.md`
- Machine-readable result: `experiments/exectv2_joint_bounded_policy_replay_dev140_20260715.json`
- Replay: `.venv\Scripts\python.exe scripts/check_exectv2_joint_bounded_policy_replay.py`

## Claim boundary

This is an inspected dev140 development decision for three saved outputs. It is
not test60 evidence, clinical validation, or evidence that the same trade-off
holds for the three unrun models in the fixed roster.
