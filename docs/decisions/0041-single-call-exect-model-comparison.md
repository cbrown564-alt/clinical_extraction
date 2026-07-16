# 0041: Use one structured model call for the ExECT comparison

Date: 2026-07-15  
Status: accepted; rerun configured, final model rows pending

## Decision

The final six-model ExECT comparison will use one structured four-family
event-ledger call per letter. Diagnosis, Seizure Frequency, Prescription, and
Investigations all begin from that named model output. The separate Diagnosis
decomposer call is removed from the comparison graph.

The deterministic work allowed by decision 0040 remains unchanged and
separately attributable. In particular, the selected joint bounded Diagnosis
and Prescription policy, Seizure Frequency projection and suppression,
Investigations normalization, evidence validation, finding assembly, and
scorer remain fixed.

## Evidence and trade-off

The predeclared GPT-4.1-mini dev140 ablation did not meet its original
non-inferiority gate. Final Diagnosis F1 changed from `0.8727` with the
decomposer to `0.8542` with the structured producer, a difference of `-0.0185`.
The one-call condition produced 3 letter-level rescues, 11 regressions, and an
overall four-family F1 difference of `-0.0072`. Exact-evidence validity remained
`1.0`.

The user accepts this measured development trade-off because the difference
does not justify a second API call for every letter. This is an architecture
and resource-policy decision, not retroactive passage of the ablation's
predeclared score gate. The regression mechanisms remain part of the disclosed
evidence.

The supported efficiency statement is limited to model passes: the architecture
uses one instead of two model calls per letter. Cost, token, latency, energy,
and hardware savings require matched telemetry from the rerun.

## Rerun boundary

- Dataset and split: manifest-defined ExECTv2 dev140.
- Conditions: the six exact decision-0039 model/runtime conditions.
- Calls: one structured event-ledger call per letter and condition.
- Prompt: the same committed `full` structured prompt profile.
- Output ownership: Diagnosis uses `structured_key_family_event_ledger`.
- Checkpoint rule: start from clean single-call output paths. Never resume the
  contaminated first-140 artifacts.
- Inspection: dev140 row review is permitted; test60 is not called or inspected.
- Reporting: retain exact model route, prompt version, source IDs, evidence,
  parse/schema failures, deterministic actions, score layers, latency, and
  token or usage metadata when the provider exposes them.

## Contaminated run record

The first attempted six-model run used `load_letters()[:140]` rather than the
manifest dev140 split. Only 94 IDs overlapped. Active GPT-5.6 Luna, GPT-5.6 Sol,
and DeepSeek V4 Flash processes were stopped when the defect was found. The
GPT-4.1-mini output and all partial affected model artifacts are excluded from
development evidence and must not be resumed or merged into the clean rerun.

The corrected runner selects manifest rows and rejects an existing checkpoint
containing any identifier outside the frozen set before a model call begins.

## Consequences

- Decision 0040 continues to govern model ownership and deterministic
  attribution; this decision selects the structured producer for Diagnosis.
- The two-call GPT-4.1-mini ablation comparator remains development evidence,
  not the selected operational graph.
- The next and only active ExECT evidence task is the clean six-model single-call
  dev140 rerun.
- No final model ranking or paper-facing six-model result exists until all six
  clean conditions complete and the component report is reproducible.

Evidence owner:

- [GPT-4.1-mini single-call Diagnosis ablation](../experiments/exectv2/diagnosis/exectv2_gpt41mini_single_call_diagnosis_ablation_2026-07-15.md)
