# ExECTv2 joint bounded-policy replay protocol

Date: 2026-07-15  
Status: completed; joint policy selected as the disclosed fallback  
Result: [joint bounded-policy result](exectv2_joint_bounded_policy_replay_2026-07-15.md)

## Primary question

When the already implemented bounded Prescription candidate and combined
Diagnosis guards run together, does the joint policy improve on the previously
implemented model-preserving fallback without introducing a cross-family
interaction or losing more than ten of the current policy's 160 rescues?

The two components were evaluated separately on identical saved outputs. This
replay is required before treating their separate gains as one policy result.
Neither component will be changed after the joint output is observed.

## Data and inspection policy

- Dataset: ExECTv2.
- Split: the 140 identifiers in the repository `dev` manifest.
- Permission: dev140 row inspection was explicitly permitted on 2026-07-15.
- Exclusion: no test60 note, prediction, annotation, identifier, failure, or
  row-level difference may be assembled, inspected, or retained.
- Inputs: saved historical GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6
  35B repair v02 producer outputs only.
- Replay: no model calls; full200 Git blobs must be filtered to temporary
  dev-only JSONL files before assembly.

## Policies compared

1. **Current comparator:** default decision-0040 model-led policy.
2. **Implemented fallback:** `decision_0040_model_preserving_dev140_v1`, using
   the existing `model_preserving_policy_candidate=True` switch.
3. **Joint candidate:** `decision_0040_joint_bounded_dev140_v1`, using
   `diagnosis_policy_variant="combined"` and
   `prescription_policy_variant="combined"` together.

The joint candidate makes no new clinical rule. It composes the frozen
Diagnosis subsumption and absence-preservation guards with the frozen local
Prescription frequency scope, bounded current-selection guard, and
explicit-current residual recovery. Seizure Frequency, Investigations,
candidate generation, gold, evidence validation, and scorers remain fixed.

All prediction-changing Diagnosis and Prescription decisions remain
deterministic-owned `clinical_epilepsy` or recorded benchmark-format rules. A
joint result is LLM with rules, not LLM-only or model-owned.

## Expected component identity checks

The joint replay must reproduce the separately measured component results:

- Diagnosis: 88 wrong-to-correct, 3 correct-to-wrong, 78 changed-still-wrong,
  and 75/81 current-policy rescue retention;
- Prescription: 46 wrong-to-correct, 0 correct-to-wrong, 10
  changed-still-wrong, and 40/41 rescue retention;
- Seizure Frequency: unchanged from the current policy at 38
  wrong-to-correct, 0 correct-to-wrong, and 20 changed-still-wrong;
- Investigations: no prediction-changing row.

Any disagreement is an implementation or instrumentation defect and permits
revision of the replay only, not the clinical components.

## Metrics and decision gates

Primary scorer: family-local `clinical_headline_unit_keys`.

Select the joint candidate over the implemented fallback for the next fixed
comparison only if every gate passes:

- the component identity checks above pass exactly;
- total wrong-to-correct is at least 172;
- total correct-to-wrong is at most 3;
- at least 150 of the current policy's 160 rescues are retained by model,
  family, and row identity;
- the seven expected lost rescues are confined to the six Diagnosis rows on
  EA0082/EA0126 and the one Prescription row on EA0141/Qwen;
- all four demonstrated missing-regimen Prescription rescue rows remain
  retained;
- the joint policy has strictly more rescues, fewer regressions, and greater
  current-policy rescue retention than the implemented fallback;
- final family keys equal the corresponding separate-study candidate keys for
  every model/family/letter row;
- every comparator-versus-joint changed row has exact evidence;
- no new schema, parse, call, abstention, or fallback failure occurs; and
- each saved model's overall and Diagnosis/Prescription family F1 is no worse
  than the implemented fallback.

The known EA0117 Diagnosis synonym residual and EA0141/Qwen future-target error
remain explicit caveats. This protocol asks whether the joint policy is the
better fallback, not whether those previously failed component gates now pass.

Secondary outputs are the model-owned, current, implemented-fallback, and joint
score ladders; family-local and compatibility directions; first
prediction-changing owner; changed-row evidence; residual rule groups; and
per-model aggregate scores.

## Artifact and stop rule

Write one machine-readable row per current-versus-joint changed model/family
decision and a second compact row-identity comparison against the implemented
fallback. Record model-owned, current, fallback, joint, family-local gold, and
compatibility-gold keys; correctness states; evidence; deterministic actions;
first owner; model and source revision; split; environment; dirty-tree note;
and all gate operands.

- Accept the joint candidate as the disclosed fallback only if every gate
  passes.
- Revise only for an implementation or instrumentation defect.
- Reject otherwise and retain the implemented fallback.
- Run no second joint candidate and do not add a row-, model-, drug-, dose-, or
  concept-specific exception.

A positive result is an inspected dev140 development policy decision for three
saved outputs. It is not test60 evidence, clinical validation, evidence for the
three unrun roster models, or permission for a model call.
