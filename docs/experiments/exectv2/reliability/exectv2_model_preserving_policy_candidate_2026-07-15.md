# ExECTv2 model-preserving deterministic-policy candidate result

Date: 2026-07-15  
Decision: reject; do not use this bundled policy in the next frozen comparison

## Answer

The opt-in `decision_0040_model_preserving_dev140_v1` candidate is not the
correct replacement for the current decision-0040 deterministic policy.

It substantially reduced rules that changed a correct model answer into a
wrong answer, and all three saved models improved on aggregate dev140 F1. But
the aggregate result hid replacement of old rescues with new rescues. The
candidate retained only 143 of the comparator's 160 wrong-to-correct rows and
lost 17. The protocol allowed at most 10 losses, so the candidate fails and is
rejected.

No test60 row was assembled or inspected. No model was called. The current
policy remains the default; the rejected candidate is available only through
an explicit replay flag.

## Fixed comparison

- Dataset and split: ExECTv2 dev140, whose row inspection was explicitly
  permitted.
- Models: saved GPT-4.1-mini, saved DeepSeek chat, and saved Qwen 3.6 35B repair
  v02 outputs.
- Comparator: current decision-0040 model-led policy.
- Candidate: four predeclared model-preserving changes only.
- Scorer: family-local `clinical_headline_unit_keys` for the primary decision;
  the existing entity-agnostic compatibility view remained secondary.
- Replay: historical Git blobs filtered to dev identifiers before assembly.
- Evidence: all 88 comparator-versus-candidate changed model/family rows had
  exact evidence.

## Gate result

| Gate | Result |
|---|---:|
| Diagnosis correct-to-wrong below 18 | pass: 3 |
| Prescription correct-to-wrong below 23 | pass: 6 |
| Seizure Frequency correct-to-wrong remains zero | pass: 0 |
| Total wrong-to-correct at least 150 | pass: 161 |
| Lose at most 10 of the comparator's 160 rescues | **fail: 17 lost** |
| Exact evidence on every changed candidate row | pass |
| No schema, parse, call, or fallback failure | pass |

The rescue-retention check is intentionally row-based. A first implementation
of the report checked only the candidate's total 161 rescues. Required row
review showed that this net count combined 143 retained rescues with 18 new
rescues and therefore hid 17 lost comparator rescues. Correcting this missing
instrumentation changed the decision from pass to reject; no clinical rule was
changed after viewing the candidate rows.

## Component result

| Family | Comparator correct-to-wrong | Candidate correct-to-wrong | Comparator wrong-to-correct | Candidate wrong-to-correct |
|---|---:|---:|---:|---:|
| Diagnosis | 18 | 3 | 81 | 88 |
| Prescription | 23 | 6 | 41 | 35 |
| Seizure Frequency | 0 | 0 | 38 | 38 |
| Investigations | 0 | 0 | 0 | 0 |
| **Total** | **41** | **9** | **160** | **161** |

The 17 lost rescues were six Diagnosis rows that became changed-still-wrong and
11 Prescription rows that returned to the wrong model-owned answer. The 18 new
rescues were 13 Diagnosis rows and five Prescription rows. There were 47
Diagnosis and 41 Prescription comparator-versus-candidate changed rows; the
candidate did not alter Seizure Frequency or Investigations.

## Aggregate scores are supportive, not decisive

| Saved model | Comparator overall F1 | Candidate overall F1 | Comparator Diagnosis F1 | Candidate Diagnosis F1 | Comparator Prescription F1 | Candidate Prescription F1 |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek chat | 0.8747 | 0.8819 | 0.8892 | 0.9037 | 0.9268 | 0.9343 |
| GPT-4.1-mini | 0.8378 | 0.8440 | 0.8727 | 0.8846 | 0.8867 | 0.8949 |
| Qwen 3.6 35B repair v02 | 0.8565 | 0.8618 | 0.8653 | 0.8793 | 0.9481 | 0.9484 |

Every aggregate score improved, but promotion was defined by component safety
and rescue retention as well as aggregate performance. The failed retention
gate therefore controls the decision.

## Mechanism finding

The Prescription residual additions are not independent of the existing
Prescription attribute repair. In dev row EA0150, for example, one shared
evidence sentence contains two ordinary current regimens and an as-required
drug. The existing repair applies the rescue cue across the shared evidence,
turning the ordinary model-owned regimens into rescue regimens. Comparator
residual additions partly reconstruct the ordinary regimens. Disabling all
residual additions removes that compensation without fixing the over-broad
attribute scope.

This does not justify retaining residual additions as the final architecture.
It shows that residual removal must follow, or be evaluated jointly with, a
general repair of rescue-cue scope. Adding a letter-specific exception to this
candidate would violate the protocol.

The Diagnosis guards are directionally useful: they removed most
correct-to-wrong changes and produced more new rescues than losses. They still
lost six prior Diagnosis rescues, so they also require a separate bounded
ablation rather than promotion as part of this rejected bundle.

## Next work

1. Predeclare and test a Prescription rescue-scope repair on shared evidence,
   then reevaluate residual removal as a separate component ablation.
2. Evaluate Diagnosis residual subsumption and absence-phenotype preservation
   separately, with explicit rescue-retention accounting.
3. Freeze a replacement policy only after one of those bounded candidates
   passes every dev140 gate. Then run the planned same-core multi-model
   comparison. Test60 remains locked until that architecture and its analysis
   plan are frozen.

## Artifacts

- Protocol: `docs/experiments/exectv2/reliability/exectv2_model_preserving_policy_candidate_protocol_2026-07-15.md`
- Machine-readable result: `experiments/exectv2_model_preserving_policy_candidate_dev140_20260715.json`
- Replay command: `.venv\Scripts\python.exe scripts/check_exectv2_model_preserving_policy_candidate.py`

## Claim boundary

This is inspected development evidence for three saved outputs. It is not
holdout evidence, cross-model validation for the unrun roster models, clinical
validation, or permission to inspect test60.
