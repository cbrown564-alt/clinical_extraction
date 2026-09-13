# ExECTv2 bounded Prescription policy candidate protocol

Date: 2026-07-15  
Status: completed; candidate rejected on the zero-regression gate  
Result: [bounded Prescription policy result](exectv2_prescription_bounded_policy_candidate_2026-07-15.md)

## Primary question

Can a Prescription-only decision-0040 policy retain the four demonstrated
missing-regimen rescue rows while reducing deterministic regressions through
three separable changes: local frequency-rescue scope, preservation of an
explicitly current model-owned regimen when later text describes a future
change, and removal of unanchored residual regimen recovery?

The preceding candidate showed that removing all residual additions is unsafe.
This study keeps candidate generation fixed and separates the retained
current-regimen recovery rule from the residual target-list behavior that added
planned, rescue, or contextually incomplete regimens.

## Data and inspection policy

- Dataset: ExECTv2.
- Split: the 140 identifiers in the repository `dev` manifest.
- Permission: dev140 row inspection was explicitly permitted on 2026-07-15.
- Exclusion: no test60 note, prediction, annotation, identifier, failure, or
  row-level difference may be inspected or retained.
- Inputs: saved historical GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6
  35B repair v02 producer outputs only.
- Replay: no model calls; full200 Git blobs must be filtered to temporary
  dev-only JSONL files before assembly.

## Comparator, candidate, and fixed behavior

Comparator: the current default decision-0040 model-led policy.

Fallback reference: the implemented but originally rejected
`decision_0040_model_preserving_dev140_v1` bundle. It reduced Diagnosis and
Prescription correct-to-wrong rows to 3 and 6 and improved all three aggregate
scores, but retained only 143 of 160 comparator rescues. The user has accepted
that disclosed trade-off as the fallback if the bounded Prescription and
separate Diagnosis studies do not produce a better implemented policy.

Candidate identifier: `decision_0040_rx_bounded_policy_dev140_v1`.

The candidate is opt-in and changes only Prescription:

1. Prefer a recognized frequency cue in the model-selected Prescription text
   over a rescue cue elsewhere in shared evidence. When selected text has no
   frequency cue, retain the existing evidence-based fill.
2. Preserve a complete model-owned current regimen when its local evidence or
   immediately governing medication section marks it as current, even when the
   same evidence later describes tapering, stopping, or increasing it.
3. Keep residual recovery only for complete regimens governed by an explicit
   current-medication cue. A plan, conditional start, future-change cue,
   historical cue, or rescue-only cue between that cue and the regimen makes
   the residual unanchored and disables it.
4. Disable the prior unanchored target-list residual group.

The current-regimen group must retain these already demonstrated comparator
rescues by row identity:

- EA0096, historical DeepSeek and GPT-4.1-mini: paired Topiramate 75 mg evening
  regimen;
- EA0127, historical DeepSeek: omitted Lamotrigine 100 mg twice daily regimen;
- EA0150, Qwen: omitted Levetiracetam 1500 mg and Lamotrigine 200 mg twice daily
  regimens.

Prescription drug, dose, and unit normalization; supported regimen splitting;
candidate generation; Diagnosis; Seizure Frequency; Investigations; evidence
validation; gold; and scorers remain fixed. All three changes are deterministic
`clinical_epilepsy` clinical-selection rules, not mechanical formatting.

## Required ablations

Replay the same saved rows under five Prescription variants:

1. default comparator;
2. local frequency scope only;
3. explicit-current model-owned selection guard only;
4. explicit-current residual recovery with the unanchored residual group off;
5. the combined candidate.

For each variant, report family-local directions, Prescription stage scores,
changed-row identities, exact-evidence status, residual additions by rule group,
and first prediction-changing owner. The combined decision must not be inferred
from a mixed union of variant outputs.

## Required tests

Write failing tests before implementation showing that:

- the local-scope variant does not spread a rescue cue across shared evidence
  and still fills frequency from evidence when selected text lacks a cue;
- the explicit-current selection guard preserves a current regimen followed by
  a taper or increase but still drops a planned-only regimen;
- current medication headings and local `is taking` wording classify complete
  residual regimens as `explicit_current_regimen_recovery` across multiline
  medication lists;
- conditional starts, planned titration targets, rescue-only regimens, and
  unanchored target-list matches classify as
  `unanchored_target_regimen_recovery` and are absent from the combined output;
- default and the two completed historical candidate switches retain their
  existing behavior.

## Metrics and gates

Primary scorer: family-local `clinical_headline_unit_keys`.

The combined candidate is accepted for the next frozen comparison only if
every gate passes:

- Prescription correct-to-wrong is below the comparator's 23;
- Prescription wrong-to-correct is at least 39;
- at least 39 of the comparator's 41 Prescription rescues are retained by row
  identity;
- all four demonstrated missing-regimen rescue rows listed above are retained;
- zero comparator-correct Prescription rows become wrong;
- Diagnosis, Seizure Frequency, and Investigations final keys remain identical
  to the comparator for every dev140 model/family row;
- every comparator-versus-candidate changed row has exact evidence;
- no new schema, parse, call, abstention, or fallback failure occurs.

Secondary metrics are model-owned and final `clinical_headline` F1 by model and
family, the entity-agnostic compatibility view, changed-row mechanisms,
residual rule-group counts, and first prediction-changing owner. Aggregate
improvement cannot override a failed row-retention or regression gate.

## Artifact

Write one machine-readable row per comparator-versus-candidate changed
model/family decision. Preserve model-owned, comparator, candidate, family-local
gold, and compatibility-gold keys; all correctness states and directions;
selected evidence and validity; deterministic actions and residual rule group;
first owner; model and source revision; split and replay policy.

The top-level artifact must record the protocol and code revision, dirty-tree
note, Python version, model/config identities, the five ablation score ladders,
schema/parse/call and fallback counts, all gate operands, and the final decision.
It must also compare the combined Prescription component with the Prescription
part of the implemented fallback: 6 correct-to-wrong, 35 wrong-to-correct, and
11 lost comparator Prescription rescues.

## Stop rule and claim boundary

- Accept only if every combined-candidate gate passes and all retained residual
  additions belong to the predeclared explicit-current group.
- Revise only for an implementation or instrumentation defect.
- Reject if a gate fails. Do not add a row-, drug-, dose-, or model-specific
  exception after viewing the replay.
- Run no second Prescription candidate. If this candidate does not improve the
  implemented fallback's disclosed regression/rescue-retention trade-off, stop
  Prescription iteration and carry that fallback into the final policy choice.

Stop after the dev140 decision. A positive result is a development decision for
three saved outputs. It is not holdout evidence, clinical validation, evidence
for the three unrun roster models, or permission for a model call.
