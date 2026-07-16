# ExECTv2 Diagnosis guard ablation protocol

Date: 2026-07-15  
Status: completed; combined guards failed the predeclared regression-family gate  
Result: [Diagnosis guard ablation result](exectv2_diagnosis_guard_ablation_2026-07-15.md)

## Primary question

When evaluated independently of Prescription changes, do the implemented
Diagnosis residual-subsumption and absence-phenotype guards improve the current
decision-0040 Diagnosis policy enough to retain as the Diagnosis part of the
implemented model-preserving fallback?

The bundled fallback reduced Diagnosis correct-to-wrong changes from 18 to 3
and increased rescues from 81 to 88, but it also lost six comparator rescues.
This study attributes those effects to each Diagnosis guard without changing
Prescription or tuning another rule.

## Data and inspection policy

- Dataset: ExECTv2 dev140, using the repository `dev` manifest.
- Row inspection: permitted on 2026-07-15.
- Test60: no note, prediction, annotation, identifier, failure, or row-level
  difference may be assembled, inspected, or retained.
- Inputs: saved historical GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6
  35B repair v02 outputs.
- Replay: saved Git blobs only, filtered to dev identifiers before assembly;
  zero model calls.

## Comparator and variants

Comparator: the current default decision-0040 model-led policy.

Candidate identifier: `decision_0040_diagnosis_guards_dev140_v1`.

Replay four Diagnosis-only variants:

1. default comparator;
2. residual-subsumption guard only: do not add a broader residual seizure
   concept when an evidence-backed model concept already contains it;
3. absence-phenotype guard only: preserve a model-owned affirmed `absence
   seizures` phenotype when the model also supplies an affirmed absence-epilepsy
   syndrome;
4. both guards combined.

The guards are deterministic `clinical_epilepsy` clinical-selection rules.
Prescription, Seizure Frequency, Investigations, candidate generation, heading
recovery, other Diagnosis rewrites and drops, gold, evidence checks, and scorers
remain fixed. The existing bundled `model_preserving_policy_candidate` switch
must retain its behavior.

## Required tests

Write failing tests before implementation showing that:

- the subsumption-only variant suppresses a broader focal-seizure residual but
  does not activate absence preservation;
- the absence-only variant preserves the model-owned absence phenotype but does
  not activate residual subsumption;
- the combined variant does both;
- an epilepsy syndrome and its seizure phenotype remain distinct;
- an unknown variant is rejected; and
- the default and bundled fallback switches remain unchanged.

## Metrics and gates

Primary scorer: family-local `clinical_headline_unit_keys`.

Accept the combined guards as the Diagnosis part of the fallback only if every
gate passes:

- Diagnosis correct-to-wrong is at most 3;
- Diagnosis wrong-to-correct is at least 88;
- at least 75 of the comparator's 81 Diagnosis rescues are retained by row
  identity;
- any lost comparator Diagnosis rescue is confined to the six already observed
  fallback rows: EA0082 and EA0126 under each saved model;
- the absence-seizure preservation mechanism is active on EA0156 where present;
- the repeated broad-concept regression family on EA0008, EA0016, EA0067,
  EA0117, EA0137, and EA0178 is not reintroduced;
- Prescription, Seizure Frequency, and Investigations final keys are identical
  to the comparator for every dev140 model/family row;
- every comparator-candidate changed row has exact evidence;
- no new schema, parse, call, abstention, or fallback failure occurs.

Report each guard's model-to-final directions, row identities, changed-row
mechanisms, evidence status, first prediction-changing owner, and model/family
score ladder. Aggregate F1 cannot replace rescue-identity accounting.

## Artifact and stop rule

Write one machine-readable row per comparator-versus-combined-candidate changed
model/family decision, plus compact changed-row identities for each single-guard
ablation. Record split, scorer, repair policy, model and source revision,
environment, dirty-tree note, failure counts, all gate operands, and the
implemented fallback reference.

Run no second Diagnosis candidate. Revise only for an implementation or
instrumentation defect. If the combined guards fail a gate, retain the bundled
implemented fallback only by the user's explicitly accepted trade-off; do not
tune a new exception.

A positive result is an inspected dev140 development decision for three saved
outputs. It is not test60 evidence, cross-model validation for the unrun roster
models, clinical validation, or permission for a model call.
