# ExECTv2 Prescription rescue-scope candidate protocol

Date: 2026-07-15  
Status: completed; candidate rejected because four comparator-correct rows became wrong  
Result: [Prescription rescue-scope candidate result](exectv2_prescription_rescue_scope_candidate_2026-07-15.md)

## Primary question

Can a local Prescription frequency-repair rule make removal of deterministic
Prescription residual additions safe on the three saved ExECTv2 dev140 model
outputs?

The rejected bundled model-preserving candidate showed that residual additions
partly compensate for an over-broad frequency repair: a rescue cue elsewhere in
shared evidence can turn an ordinary model-owned regimen into an as-required
regimen. This study isolates that dependency before any further Diagnosis work.

## Data and inspection policy

- Dataset: ExECTv2.
- Split: the 140 identifiers in the repository's `dev` manifest.
- Permission: dev140 row inspection was explicitly permitted on 2026-07-15.
- Exclusion: no test60 note, prediction, annotation, identifier, failure, or
  row-level difference may be inspected or retained.
- Inputs: saved historical GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6
  35B repair v02 producer outputs only.
- Replay: no model calls; full200 Git blobs must be filtered to temporary
  dev-only JSONL files before assembly.

## Comparator and candidate

Comparator: the current default decision-0040 model-led policy.

Candidate identifier:
`decision_0040_rx_rescue_scope_no_residual_dev140_v1`.

The candidate is opt-in and changes only Prescription:

1. When the model-owned Prescription text contains a recognized frequency cue,
   use that local cue for frequency repair. A rescue cue elsewhere in a longer
   shared evidence span must not override it.
2. If the model-owned text has no recognized frequency cue, retain the current
   evidence-based fill behavior.
3. An explicit rescue cue in the model-owned text, including `prn`, `as
   required`, `rescue`, or `for seizure clusters`, still sets `As_Required`.
4. Disable all deterministic Prescription residual additions.

Prescription drug, dose, and unit normalization; supported regimen splitting;
future/historical suppression; Diagnosis; Seizure Frequency; Investigations;
evidence validation; gold; and scorers remain fixed. The rejected candidate's
Diagnosis guards and current-versus-future Prescription guard are not enabled.

Both changes are deterministic `clinical_epilepsy` rules. The frequency repair
changes regimen meaning and must not be described as mechanical formatting.

## Required tests

Write failing tests before implementation showing that the opt-in candidate:

- keeps `levetiracetam 1500mg bd` and `lamotrigine 200mg bd` ordinary when one
  shared evidence sentence later identifies clobazam as rescue medication;
- still maps an explicitly local `for seizure clusters`, `prn`, or `as
  required` regimen to `As_Required`;
- keeps the existing evidence-based frequency fill when selected text has no
  frequency cue;
- disables Prescription residual additions only when the candidate is on;
- leaves the default policy unchanged.

## Metrics and gates

Primary scorer: family-local `clinical_headline_unit_keys`.

Promotion requires every gate:

- Prescription correct-to-wrong below the comparator's 23;
- Prescription wrong-to-correct at least 36;
- retain at least 36 of the comparator's 41 Prescription rescues, losing at
  most five by row identity;
- create zero newly wrong Prescription rows from comparator-correct rows;
- Diagnosis, Seizure Frequency, and Investigations final keys remain identical
  to the comparator for every dev140 model/family row;
- every comparator-versus-candidate changed row has exact evidence;
- no new schema, parse, call, abstention, or fallback failure.

Secondary metrics are model-owned and final `clinical_headline` F1 by model and
family, the entity-agnostic compatibility view, changed-row mechanisms, and
first prediction-changing owner. Aggregate improvement cannot override a
failed component gate.

## Artifact

Write one machine-readable row per comparator-versus-candidate changed
model/family decision, with model-owned, comparator, candidate, family-local
gold, and compatibility-gold keys; all correctness states and directions;
selected evidence and validity; deterministic actions; first owner; model and
source revision; split and replay policy.

The top-level artifact must record protocol and code revision, dirty-tree note,
Python version, model/config identities, score ladders, schema/parse/call and
fallback counts, all gate operands, and the final decision.

## Stop rule

- Accept for the next frozen comparison only if every gate passes and changed
  rows follow the two predeclared Prescription mechanisms.
- Revise only for an implementation or instrumentation defect.
- Reject if any gate fails. Do not add a row-, drug-, or model-specific rule
  after viewing candidate rows.

Stop after the dev140 decision. A positive result is a development decision for
three saved outputs, not holdout evidence or permission for a model call.
