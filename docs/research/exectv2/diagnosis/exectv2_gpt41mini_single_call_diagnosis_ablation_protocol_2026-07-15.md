# ExECTv2 GPT-4.1-mini single-call Diagnosis ablation protocol

Date: 2026-07-15  
Status: predeclared before candidate assembly or scoring; source-row amendment
recorded before scoring after the six-model runner failed the split check

## Question

Can the Diagnosis facts already produced by the GPT-4.1-mini structured
four-family event-ledger call replace the separate Diagnosis decomposer without
a material loss after the same accepted deterministic Diagnosis policy is
applied?

This matters because the completed dev140 review classified 173 of 246
Diagnosis disagreements as representation or evaluation issues rather than
extraction errors. The retained structured call and Diagnosis decomposer also
have similar raw Diagnosis concept F1. If their final outputs are comparable,
the fixed model comparison may not need a second model pass per letter.

## Data and inspection policy

- Dataset: ExECTv2.
- Split: `dev140`, 140 development letters under the retained loader and split
  definition.
- Row inspection: permitted for dev140.
- Prohibited: test60 and full200 row-level outputs, annotations, errors, or
  differences.
- Calls: no model calls. Read the retained GPT-4.1-mini full200 structured and
  Diagnosis-decomposer Git blobs, filter them by source identifier to the
  manifest-defined dev140 IDs before assembly, and never assemble, score,
  serialize, or inspect excluded rows.

The initially named working-tree six-model artifacts cannot be used: the live
runner selected `load_letters()[:140]`, and the pre-score assembly check found
that only 94 of those IDs belong to the manifest-defined dev140 split. The
active affected runs were stopped. This amendment switches to retained full200
Git blobs from revision `8d808656ce99c029272aaa996b8f6be36043a0c6^`, whose
prompt versions match the candidate (`event_ledger_v0.9.24` and Diagnosis
decomposer `v0.1`). Filtering occurs before row deserialization for analysis;
only manifest dev140 rows may enter the study.

## Candidate and comparator

- Comparator: retained GPT-4.1-mini two-call decision-0040 output, with
  `diagnosis_decomposer` as the Diagnosis producer.
- Candidate: the same retained GPT-4.1-mini structured event-ledger output, with
  `structured_key_family_event_ledger` also used as the Diagnosis producer.
- Model condition: `openai/gpt-4.1-mini`, retained `full` prompt output,
  temperature `0`, cache disabled in the original live run.
- Fixed downstream work: the selected joint bounded Diagnosis policy,
  evidence validation, finding assembly, and the existing score views.
- Changed component: Diagnosis producer only. Seizure Frequency, Prescription,
  Investigations, gold, scorer, and deterministic policies remain fixed.

The candidate remains model-led under decision 0040 because GPT-4.1-mini
produced the Diagnosis concepts, assertions, and evidence. Deterministic
prediction-changing work remains attributed separately.

## Scores and evidence

- Primary component score: final Diagnosis `clinical_headline` concept/assertion
  precision, recall, and F1.
- Primary architecture score: overall four-family `clinical_headline` F1.
- Secondary scores: raw-candidate and evidence-valid Diagnosis scores,
  normalized phrase, CUI, and fidelity-companion views.
- Evidence checks: exact-evidence rate, invalid or missing evidence, call state,
  and parse/schema state inherited from each retained producer.
- Changed-row analysis: wrong-to-correct, correct-to-wrong, changed-still-wrong,
  unchanged-correct, first prediction-changing owner, deterministic action,
  and available Diagnosis issue or mechanism tags.

The machine-readable artifact will retain one record per letter and Diagnosis
comparison, including source identifier, split, model, replay mode, producer,
prompt/program identity, raw and final clinical keys, gold keys, evidence
status, deterministic actions, comparator/candidate correctness, change
direction, and first failure owner. Aggregate sections will retain scorer,
repair policy, source hashes, score layers, counts, and claim boundary.

## Decision rule

- **Select for a frozen follow-up:** candidate Diagnosis F1 is at least the
  comparator F1, exact-evidence validity does not regress, and changed-row
  analysis exposes no new severe clinical failure pattern.
- **Trade-off candidate:** Diagnosis F1 is no more than `0.0100` below the
  comparator, evidence validity is preserved, and regressions are bounded and
  explained. Report the one-versus-two-model-pass trade-off without promoting
  it automatically.
- **Reject:** Diagnosis F1 falls by more than `0.0100`, evidence validity
  regresses, or correct-to-wrong rows expose a material clinical failure mode.
- **Revise separately:** a narrow, identifiable structured-prompt omission
  explains a near miss. Any prompt revision requires a new predeclared live-call
  condition; it is not part of this replay.
- **Blocked:** retained artifacts cannot reconstruct comparable final outputs
  with valid source identifiers and attribution.

## Claim boundary

A positive result is a development answer for the retained GPT-4.1-mini
ExECTv2 dev140 output under the fixed scorer and selected deterministic policy.
It is not test60 evidence, clinical validation, a published-benchmark result,
or evidence that every model can use one call. It supports only a measured
reduction from two retained model passes to one; cost and latency claims require
separate telemetry.
