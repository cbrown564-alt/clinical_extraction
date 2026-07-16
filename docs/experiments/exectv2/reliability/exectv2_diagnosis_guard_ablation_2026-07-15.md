# ExECTv2 Diagnosis guard ablation result

Date: 2026-07-15  
Decision: do not independently promote; retain the bundled fallback only under the accepted trade-off

## Answer

The two Diagnosis guards reproduce the Diagnosis part of the implemented
model-preserving fallback when evaluated without Prescription changes. They
reduce correct-to-wrong changes from 18 to 3, increase wrong-to-correct changes
from 81 to 88, preserve the model-owned absence phenotype on EA0156, and retain
75 of 81 comparator rescues. The six lost rescues are exactly the predeclared
EA0082 and EA0126 rows under all three saved models.

The combined guards nevertheless fail the frozen mechanism gate because all
three remaining regressions are the same unresolved broad-concept addition on
EA0117. The residual-subsumption check treats token containment as subsumption;
it does not recognize `focal impaired awareness seizures` and `focal seizures
with altered awareness` as equivalent concepts. The deterministic residual
therefore adds the second surface and changes a model-correct row to wrong for
all three models.

No second Diagnosis candidate will be tuned. The guards are not independently
promoted. The already implemented bundled fallback remains available only
because the user explicitly accepts its disclosed rescue-retention and
regression trade-off.

No test60 row was assembled or inspected, and no model was called.

## Fixed comparison

- Dataset and split: ExECTv2 dev140, with permitted row inspection.
- Inputs: saved GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6 35B repair
  v02 outputs.
- Comparator: current default decision-0040 model-led policy.
- Variants: residual subsumption only, absence preservation only, and both
  guards combined.
- Fixed: Prescription, Seizure Frequency, Investigations, candidate generation,
  other Diagnosis repair, gold, evidence checks, and scorers.
- Primary scorer: family-local `clinical_headline_unit_keys`.

## Gate result

| Gate | Result |
|---|---:|
| Diagnosis correct-to-wrong at most 3 | pass: 3 |
| Diagnosis wrong-to-correct at least 88 | pass: 88 |
| Retain at least 75 of 81 comparator rescues | pass: 75 |
| Lost rescues confined to EA0082/EA0126 under each model | pass: 6/6 |
| Preserve the EA0156 absence phenotype | pass: 2 changed model rows correct |
| Do not reintroduce the named broad-concept regression family | **fail: EA0117 under 3/3 models** |
| Other families unchanged | pass: 0 changed rows |
| Exact evidence on every comparator-candidate change | pass: 47/47 |
| No new call, parse/schema, or fallback failure | pass |

## Component ablations

| Variant | Wrong to correct | Correct to wrong | Changed, still wrong | Comparator-changed rows |
|---|---:|---:|---:|---:|
| Default comparator | 81 | 18 | 82 | 0 |
| Residual subsumption only | 91 | 5 | 75 | 42 |
| Absence preservation only | 78 | 16 | 85 | 5 |
| Combined guards | 88 | 3 | 78 | 47 |

The subsumption guard does most of the work. The absence guard correctly
restores the two model-owned EA0156 facts, but by itself loses three rescues and
does not address most residual-addition regressions. In combination it changes
which Diagnosis rows are rescued: 75 old rescues remain, six are lost, and 13
new rescues appear.

## Mechanism and ownership

- EA0156 is a model-preservation success. DeepSeek and Qwen supplied affirmed
  `absence seizures` with exact evidence alongside `juvenile absence epilepsy`.
  The default drop rule removed the seizure phenotype; the guard leaves the
  model-owned fact intact.
- The repeated literal broad residuals on EA0008, EA0016, EA0067, EA0137, and
  EA0178 are suppressed by the subsumption guard.
- EA0117 remains harmful. The model supplies `focal impaired awareness
  seizures`; deterministic benchmark-format residual recovery adds `focal
  seizures with altered awareness`. That addition is the first harmful owner.

The guard successes and failures are deterministic clinical-selection effects.
They are not credited to the model merely because they operate on model output.

## Scores

| Saved model | Comparator overall F1 | Combined overall F1 | Comparator Diagnosis F1 | Combined Diagnosis F1 |
|---|---:|---:|---:|---:|
| Historical DeepSeek chat | 0.8747 | 0.8800 | 0.8892 | 0.9037 |
| GPT-4.1-mini | 0.8378 | 0.8419 | 0.8727 | 0.8846 |
| Qwen 3.6 35B repair v02 | 0.8565 | 0.8616 | 0.8653 | 0.8793 |

All aggregates improve, but the predeclared mechanism gate controls the
independent promotion decision.

## Stop and fallback decision

Do not iterate on a synonym exception for EA0117. The implemented
`decision_0040_model_preserving_dev140_v1` bundle remains the operational
fallback named by the user. Its development evidence must continue to state:

- Diagnosis: 88 rescues, 3 correct-to-wrong changes, and six lost comparator
  rescues;
- Prescription: 35 rescues, 6 correct-to-wrong changes, and 11 lost comparator
  rescues;
- total comparator rescue retention: 143/160;
- all candidate changes have exact evidence; test60 was not inspected.

This is a conscious fallback choice, not retroactive passage of either rejected
protocol.

## Artifacts

- Protocol: `docs/experiments/exectv2/reliability/exectv2_diagnosis_guard_ablation_protocol_2026-07-15.md`
- Machine-readable result: `experiments/exectv2_diagnosis_guard_ablation_dev140_20260715.json`
- Replay: `.venv\Scripts\python.exe scripts/check_exectv2_diagnosis_guard_ablation.py`

## Claim boundary

This is inspected development evidence for three saved outputs. It is not
holdout evidence, cross-model validation for the unrun roster models, clinical
validation, or permission to inspect test60.
